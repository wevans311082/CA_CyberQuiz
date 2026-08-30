# SPDX-FileCopyrightText: 2026 CA Tabletop
# SPDX-License-Identifier: MPL-2.0

from types import SimpleNamespace

from classquiz.socket_server import _decision_quality


def test_decision_quality_matches_configured_evidence_keywords():
    question = SimpleNamespace(time="120", decision_rubric=[
        {"id": "containment", "label": "Containment", "keywords": ["isolate", "quarantine"], "max_points": 20},
        {"id": "comms", "label": "Communication", "keywords": ["regulator"], "max_points": 10},
    ])

    result = _decision_quality(question, "We will isolate the affected server and notify the regulator.", 30_000, 3)

    assert result["rubric_score"] == 100
    assert result["confidence_score"] == 100
    assert result["time_score"] == 75
    assert all(criterion["matched"] for criterion in result["criteria"])


def test_decision_quality_is_partial_and_time_is_bounded():
    question = SimpleNamespace(time="60", decision_rubric=[
        {"label": "Recovery", "keywords": ["backup"], "max_points": 10},
        {"label": "Lessons learned", "keywords": ["review"], "max_points": 10},
    ])

    result = _decision_quality(question, "Restore from backup.", 90_000, 1)

    assert result["rubric_score"] == 50
    assert result["confidence_score"] == 33
    assert result["time_score"] == 0
    assert 0 <= result["time_score"] <= 100


def test_decision_quality_without_rubric_preserves_legacy_signal_only():
    question = SimpleNamespace(time="0", decision_rubric=None)

    result = _decision_quality(question, "A response", 500_000, None)

    assert result["rubric_score"] is None
    assert result["criteria"] == []
    assert result["time_score"] == 100
    assert result["confidence_score"] == 0
