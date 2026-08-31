from classquiz.live_health import calculate_exercise_health


def test_healthy_live_exercise_snapshot():
    health = calculate_exercise_health(
        players=[{"username": "alice"}], assigned_roles={"alice": "CISO"},
        expected_responses=1, received_responses=1,
        timer={"running": True, "duration": 120}, current_question=2, question_count=5,
    )
    assert health["overall"] == "healthy"
    assert health["phase"] == "live"


def test_degraded_snapshot_identifies_actionable_risks():
    health = calculate_exercise_health(
        players=[{"username": "alice"}, {"username": "bob"}], assigned_roles={"alice": "CISO"},
        expected_responses=3, received_responses=1,
        timer={"running": True}, current_question=0, question_count=4,
        reference_documents=[{"title": "Broken policy"}], failed_events=2, validation_errors=1,
    )
    assert health["overall"] == "error"
    assert {check["code"] for check in health["checks"] if check["severity"] in {"warning", "error"}} >= {"unassigned_roles", "responses", "timer", "content", "socket_events"}
