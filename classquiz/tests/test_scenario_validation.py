from classquiz.scenario_validation import validate_scenario


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
