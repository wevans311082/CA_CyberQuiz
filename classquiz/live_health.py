"""Pure health calculations for the live facilitator workspace."""

from typing import Any


def calculate_exercise_health(
    *,
    players: list[dict[str, Any]],
    assigned_roles: dict[str, str] | None = None,
    expected_responses: int = 0,
    received_responses: int = 0,
    timer: dict[str, Any] | None = None,
    current_question: int = -1,
    question_count: int = 0,
    reference_documents: list[dict[str, Any]] | None = None,
    failed_events: int = 0,
    validation_errors: int = 0,
) -> dict[str, Any]:
    """Return an actionable, privacy-light health snapshot.

    The function accepts snapshots from Redis/socket state so it is easy to
    test without services and safe to reuse for admin and projector views.
    """
    assigned_roles = assigned_roles or {}
    reference_documents = reference_documents or []
    checks: list[dict[str, Any]] = []

    unassigned = [p.get("username") for p in players if p.get("username") and not assigned_roles.get(p["username"])]
    checks.append({"code": "participant_connections", "severity": "ok" if players else "info", "label": "Participant connections", "detail": f"{len(players)} active participant(s)."})
    checks.append({"code": "unassigned_roles", "severity": "warning" if unassigned else "ok", "label": "Role assignments", "detail": f"{len(unassigned)} participant(s) need a role.", "count": len(unassigned), "participants": unassigned})

    outstanding = max(0, expected_responses - received_responses)
    checks.append({"code": "responses", "severity": "warning" if outstanding else "ok", "label": "Response completion", "detail": f"{received_responses} of {expected_responses} expected response(s) received.", "outstanding": outstanding})

    timer_running = bool(timer and timer.get("running"))
    timer_duration = timer.get("duration") if timer else None
    checks.append({"code": "timer", "severity": "warning" if timer_running and not timer_duration else "ok", "label": "Timer synchronisation", "detail": "Timer state is available to all clients." if not timer_running or timer_duration else "Timer is running without a shared duration."})

    content_issue_count = max(0, validation_errors)
    checks.append({"code": "content", "severity": "error" if content_issue_count else "ok", "label": "Scenario content", "detail": f"{content_issue_count} blocking content issue(s)."})
    missing_references = sum(1 for document in reference_documents if not document.get("id") or not document.get("title"))
    checks.append({"code": "references", "severity": "warning" if missing_references else "ok", "label": "Reference shelf", "detail": f"{missing_references} unavailable reference document(s)."})
    checks.append({"code": "socket_events", "severity": "error" if failed_events else "ok", "label": "Live event delivery", "detail": f"{failed_events} failed event(s) need retry."})

    if current_question < 0:
        phase = "lobby"
    elif question_count and current_question >= question_count:
        phase = "complete"
    else:
        phase = "live"
    severities = [check["severity"] for check in checks]
    overall = "error" if "error" in severities else "warning" if "warning" in severities else "healthy"
    return {"overall": overall, "phase": phase, "current_question": current_question, "checks": checks}
