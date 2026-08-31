"""Server-side validation for authored branching scenarios."""

from collections import deque
from typing import Any

KNOWN_FRAMEWORKS = {"NIST CSF 2.0", "CAF 4.0", "NCSC CAF 4.0", "CIS Controls v8.1", "MITRE ATT&CK Enterprise", "ISO/IEC 27001:2022"}
KNOWN_TYPES = {"ABCD", "RANGE", "VOTING", "SLIDE", "INFORMATION", "FILE", "TEXT", "ORDER", "CHECK", "SCOREBOARD"}
CONTENT_TYPES = {"SLIDE", "INFORMATION", "FILE", "SCOREBOARD"}


def _get(value: Any, key: str, default=None):
    if isinstance(value, dict):
        return value.get(key, default)
    return getattr(value, key, default)


def _text(value: Any) -> str:
    return str(value or "").strip()


def _number(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _issue(issues: list[dict[str, Any]], level: str, code: str, message: str, path: str | None = None, **extra: Any) -> None:
    issue = {"level": level, "code": code, "message": message}
    if path is not None:
        issue["path"] = path
    issue.update(extra)
    issues.append(issue)


def validate_scenario(
    questions: list[Any],
    roles: list[str] | None = None,
    injects: list[Any] | None = None,
    metadata: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Return stable, deep-linkable blocking errors and author warnings."""
    issues: list[dict[str, Any]] = []
    metadata = metadata or {}
    if not questions:
        _issue(issues, "error", "empty_scenario", "Add at least one question or information slide.", "questions")
        return issues

    role_names = [str(role).strip() for role in (roles or [])]
    seen_roles: set[str] = set()
    for index, role in enumerate(role_names):
        if not role:
            _issue(issues, "error", "empty_role", "A role cannot be blank.", f"roles[{index}]")
        elif role in seen_roles:
            _issue(issues, "error", "duplicate_role", f"The role '{role}' is listed more than once.", f"roles[{index}]")
        seen_roles.add(role)

    id_to_index: dict[str, int] = {}
    for index, question in enumerate(questions):
        path = f"questions[{index}]"
        question_id = _text(_get(question, "id"))
        if not question_id:
            _issue(issues, "error", "missing_id", f"Step {index + 1} is missing a stable ID.", f"{path}.id", question_index=index)
        elif question_id in id_to_index:
            _issue(issues, "error", "duplicate_id", f"Step {index + 1} reuses the ID '{question_id}'.", f"{path}.id", question_index=index, question_id=question_id)
        else:
            id_to_index[question_id] = index

        if not _text(_get(question, "question")) and not _text(_get(question, "information_body")):
            _issue(issues, "error", "empty_content", f"Step {index + 1} has no visible content.", f"{path}.question", question_index=index)
        question_type = _get(question, "type")
        question_type = getattr(question_type, "value", question_type) or "ABCD"
        if question_type not in KNOWN_TYPES:
            _issue(issues, "error", "unknown_type", f"Step {index + 1} uses unsupported type '{question_type}'.", f"{path}.type", question_index=index)

        timer = _get(question, "timer")
        duration = _get(timer, "duration_seconds") if timer and _get(timer, "enabled") else _get(question, "time")
        if duration is not None and (_number(duration) is None or _number(duration) < 0):
            _issue(issues, "error", "invalid_timer", f"Step {index + 1} has an invalid timer value.", f"{path}.time", question_index=index)
        if timer and _get(timer, "enabled") and (_number(_get(timer, "duration_seconds")) or 0) == 0:
            _issue(issues, "warning", "zero_timer", f"Step {index + 1} has an enabled timer with no duration.", f"{path}.timer.duration_seconds", question_index=index)

        answers = _get(question, "answers", [])
        if question_type not in CONTENT_TYPES and question_type != "RANGE" and not isinstance(answers, list):
            _issue(issues, "error", "invalid_answers", f"Step {index + 1} needs a list of answer options.", f"{path}.answers", question_index=index)
        if isinstance(answers, list):
            answer_labels: set[str] = set()
            for answer_index, answer in enumerate(answers):
                label = _text(_get(answer, "answer"))
                if question_type not in CONTENT_TYPES and not label:
                    _issue(issues, "error", "empty_answer", f"Step {index + 1} contains a blank answer option.", f"{path}.answers[{answer_index}].answer", question_index=index)
                if label and label.casefold() in answer_labels:
                    _issue(issues, "warning", "duplicate_answer", f"Step {index + 1} repeats an answer option.", f"{path}.answers[{answer_index}].answer", question_index=index)
                answer_labels.add(label.casefold())
        allowed_roles = _get(question, "allowed_roles") or []
        for role_index, role in enumerate(allowed_roles):
            if role_names and role not in role_names:
                _issue(issues, "warning", "unknown_role", f"Step {index + 1} references the role '{role}', which is not in the role list.", f"{path}.allowed_roles[{role_index}]", question_index=index)
        for attachment_index, attachment in enumerate(_get(question, "file_attachments") or []):
            if not _text(_get(attachment, "url")):
                _issue(issues, "error", "missing_attachment_url", f"Attachment {attachment_index + 1} on step {index + 1} has no file URL.", f"{path}.file_attachments[{attachment_index}].url", question_index=index)

    # Resolve routes after every ID has been collected so forward references work.
    edges: list[tuple[int, int]] = []
    for index, question in enumerate(questions):
        path = f"questions[{index}]"
        answers = _get(question, "answers", [])
        targets = [_get(answer, "next_question_id") for answer in answers] if isinstance(answers, list) else []
        targets.append(_get(question, "default_next_question_id"))
        valid_targets: list[int] = []
        for answer_index, target in enumerate(targets):
            if not target:
                continue
            if target not in id_to_index:
                field = f"{path}.default_next_question_id" if answer_index == len(targets) - 1 else f"{path}.answers[{answer_index}].next_question_id"
                _issue(issues, "error", "missing_target", f"A route from step {index + 1} points to '{target}', which does not exist.", field, question_index=index, target=target)
            else:
                valid_targets.append(id_to_index[target])
        if valid_targets:
            edges.extend((index, target) for target in valid_targets)
        elif not any(targets) and index < len(questions) - 1:
            edges.append((index, index + 1))

    reachable = {0}
    queue = deque([0])
    while queue:
        current = queue.popleft()
        for source, target in edges:
            if source == current and target not in reachable:
                reachable.add(target)
                queue.append(target)
    for index in range(len(questions)):
        if index not in reachable:
            _issue(issues, "warning", "unreachable", f"Step {index + 1} cannot be reached from the start.", f"questions[{index}]", question_index=index)

    terminal_nodes = {index for index in range(len(questions)) if not any(source == index for source, _ in edges)}
    if not terminal_nodes:
        _issue(issues, "warning", "no_terminal", "No route ends the exercise; participants may be trapped in a loop.", "questions")
    else:
        reverse: dict[int, set[int]] = {index: set() for index in range(len(questions))}
        for source, target in edges:
            reverse[target].add(source)
        can_finish = set(terminal_nodes)
        queue = deque(terminal_nodes)
        while queue:
            current = queue.popleft()
            for source in reverse[current]:
                if source not in can_finish:
                    can_finish.add(source)
                    queue.append(source)
        if 0 not in can_finish:
            _issue(issues, "warning", "no_completion_path", "The starting step cannot reach a terminal step.", "questions[0]")

    seen_injects: set[str] = set()
    for index, inject in enumerate(injects or []):
        path = f"injects[{index}]"
        inject_id = _text(_get(inject, "id"))
        if inject_id and inject_id in seen_injects:
            _issue(issues, "error", "duplicate_inject_id", f"Inject {index + 1} reuses the ID '{inject_id}'.", f"{path}.id")
        seen_injects.add(inject_id)
        if not _text(_get(inject, "title")) or not _text(_get(inject, "content")):
            _issue(issues, "error", "empty_inject", f"Inject {index + 1} needs a title and content.", path)
        if _get(inject, "severity", "info") not in {"info", "warning", "critical"}:
            _issue(issues, "error", "invalid_inject_severity", f"Inject {index + 1} has an invalid severity.", f"{path}.severity")
        target = _get(inject, "trigger_after_question_id")
        if target and target not in id_to_index:
            _issue(issues, "error", "missing_inject_target", f"Inject {index + 1} triggers after a step that does not exist.", f"{path}.trigger_after_question_id", target=target)

    mappings = metadata.get("framework_mappings") or {}
    if not mappings:
        _issue(issues, "warning", "missing_framework_mapping", "Add at least one framework mapping so the exercise can be reported against an outcome.", "framework_mappings")
    for framework, outcomes in mappings.items():
        if framework not in KNOWN_FRAMEWORKS:
            _issue(issues, "warning", "unknown_framework", f"'{framework}' is not in the built-in framework catalogue.", f"framework_mappings.{framework}")
        if not outcomes:
            _issue(issues, "warning", "empty_framework_mapping", f"Framework '{framework}' has no mapped outcomes.", f"framework_mappings.{framework}")
    return issues


def validate_quiz_payload(payload: Any) -> list[dict[str, Any]]:
    """Validate a QuizInput-like object, including title and metadata."""
    metadata = {key: _get(payload, key) for key in ("framework_mappings", "tags", "duration_minutes")}
    issues = validate_scenario(_get(payload, "questions", []) or [], _get(payload, "roles"), _get(payload, "injects"), metadata)
    if not _text(_get(payload, "title")):
        _issue(issues, "error", "missing_title", "Give the scenario a title.", "title")
    duration = _number(_get(payload, "duration_minutes"))
    if duration is not None and duration <= 0:
        _issue(issues, "error", "invalid_duration", "Scenario duration must be greater than zero.", "duration_minutes")
    return issues
