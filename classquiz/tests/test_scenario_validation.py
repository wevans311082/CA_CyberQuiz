from classquiz.scenario_validation import validate_scenario
from classquiz.socket_server import branching


def question(question_id, target=None):
    return {"id": question_id, "question": question_id, "answers": [{"answer": "Continue", "next_question_id": target}] if target else []}


def test_linear_scenario_is_valid():
    issues = validate_scenario([question("a"), question("b")])
    assert not [issue for issue in issues if issue["level"] == "error"]


def test_missing_branch_target_is_blocking():
    issues = validate_scenario([question("a", "missing")])
    assert any(issue["code"] == "missing_target" and issue["level"] == "error" for issue in issues)


def test_unreachable_step_is_reported_without_blocking_save():
    issues = validate_scenario([question("a", "a"), question("orphan")])
    assert any(issue["code"] == "unreachable" for issue in issues)
    assert not [issue for issue in issues if issue["level"] == "error"]


def test_inject_must_reference_existing_question():
    issues = validate_scenario([question("a")], injects=[{"trigger_after_question_id": "missing"}])
    assert any(issue["code"] == "missing_inject_target" for issue in issues)


def test_invalid_content_has_editor_paths_and_stable_codes():
    issues = validate_scenario(
        [
            {"id": "start", "question": "Choose", "time": "not-a-number", "answers": [{"answer": "", "next_question_id": "missing"}]},
            {"id": "start", "question": "Duplicate", "time": "30", "answers": []},
        ],
        roles=["Incident Lead", "Incident Lead"],
        injects=[{"id": "i1", "title": "", "content": "", "severity": "urgent"}],
    )
    assert {issue["code"] for issue in issues} >= {
        "invalid_timer", "empty_answer", "missing_target", "duplicate_id", "duplicate_role", "empty_inject", "invalid_inject_severity"
    }
    assert all("path" in issue for issue in issues)


def test_framework_mapping_is_advisory_and_unknown_framework_is_reported():
    issues = validate_scenario(
        [question("a")],
        metadata={"framework_mappings": {"Custom Framework": []}},
    )
    assert any(issue["code"] == "unknown_framework" and issue["level"] == "warning" for issue in issues)
    assert any(issue["code"] == "empty_framework_mapping" for issue in issues)


def test_live_timeline_event_is_idempotent(monkeypatch):
    class FakeRedis:
        def __init__(self):
            self.keys = set()
            self.events = []

        async def set(self, key, value, nx=False, ex=None):
            if nx and key in self.keys:
                return False
            self.keys.add(key)
            return True

        async def rpush(self, key, value):
            self.events.append(value)

        async def expire(self, key, seconds):
            return True

        async def lrange(self, key, start, end):
            return self.events

    fake = FakeRedis()
    monkeypatch.setattr(branching, "redis", fake)
    import asyncio

    assert asyncio.run(branching.append_timeline_event("123456", "bonus_awarded", {"points": 10}, event_id="retry-1"))
    assert not asyncio.run(branching.append_timeline_event("123456", "bonus_awarded", {"points": 10}, event_id="retry-1"))
    events = asyncio.run(branching.get_timeline_events("123456"))
    assert len(events) == 1
    assert events[0]["type"] == "bonus_awarded"
