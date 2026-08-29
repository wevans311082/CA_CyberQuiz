"""Validation helpers for authored branching scenarios.

The editor uses the same graph rules client-side; this module is the final
server-side guard so malformed routes cannot be published by another client.
"""

from collections import deque
from typing import Any


def _get(value: Any, key: str, default=None):
    if isinstance(value, dict):
        return value.get(key, default)
    return getattr(value, key, default)


def validate_scenario(questions: list[Any], roles: list[str] | None = None, injects: list[Any] | None = None) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    if not questions:
        return [{"level": "error", "code": "empty_scenario", "message": "Add at least one question or information slide."}]

    id_to_index: dict[str, int] = {}
    for index, question in enumerate(questions):
        question_id = _get(question, "id")
        if not question_id:
            issues.append({"level": "error", "code": "missing_id", "question_index": index, "message": f"Step {index + 1} is missing a stable ID."})
        elif question_id in id_to_index:
            issues.append({"level": "error", "code": "duplicate_id", "question_index": index, "question_id": question_id, "message": f"Step {index + 1} reuses the ID '{question_id}'."})
        else:
            id_to_index[question_id] = index

    edges: list[tuple[int, int]] = []
    for index, question in enumerate(questions):
        explicit = False
        answers = _get(question, "answers", [])
        if isinstance(answers, list):
            for answer in answers:
                target = _get(answer, "next_question_id")
                if not target:
                    continue
                explicit = True
                if target not in id_to_index:
                    issues.append({"level": "error", "code": "missing_target", "question_index": index, "message": f"A route from step {index + 1} points to '{target}', which does not exist."})
                else:
                    edges.append((index, id_to_index[target]))
        default_target = _get(question, "default_next_question_id")
        if default_target:
            explicit = True
            if default_target not in id_to_index:
                issues.append({"level": "error", "code": "missing_target", "question_index": index, "message": f"The default route from step {index + 1} points to '{default_target}', which does not exist."})
            else:
                edges.append((index, id_to_index[default_target]))
        elif not explicit and index < len(questions) - 1:
            edges.append((index, index + 1))

        allowed_roles = _get(question, "allowed_roles") or []
        for role in allowed_roles:
            if roles and role not in roles:
                issues.append({"level": "warning", "code": "unknown_role", "question_index": index, "message": f"Step {index + 1} references the role '{role}', which is not in the role list."})

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
            issues.append({"level": "warning", "code": "unreachable", "question_index": index, "message": f"Step {index + 1} cannot be reached from the start."})

    if not any(source not in {edge[0] for edge in edges} for source in range(len(questions))):
        issues.append({"level": "warning", "code": "no_terminal", "message": "No route ends the exercise; participants may be trapped in a loop."})

    question_ids = set(id_to_index)
    for index, inject in enumerate(injects or []):
        target = _get(inject, "trigger_after_question_id")
        if target and target not in question_ids:
            issues.append({"level": "error", "code": "missing_inject_target", "message": f"Inject {index + 1} triggers after a step that does not exist."})
    return issues
