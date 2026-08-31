# SPDX-FileCopyrightText: 2026 CyberAsk
# SPDX-License-Identifier: MPL-2.0

from classquiz.auth import get_current_user
from classquiz.db.models import QuizQuestion
from classquiz.routers.seed import create_seed, get_templates, preview_seed
from classquiz.seed.context import WizardContext
from classquiz.seed.registry import list_templates
from classquiz.scenario_validation import validate_scenario
from classquiz.seed.service import build_quiz_payload


def test_all_seed_templates_build_valid_questions():
    for template in list_templates():
        payload = build_quiz_payload(template.id, WizardContext())
        questions = [QuizQuestion.model_validate(question) for question in payload["questions"]]

        assert questions
        assert payload["scenario_type"] == "tabletop"
        assert payload["roles"]
        assert payload["injects"]


def test_all_seed_templates_have_no_blocking_scenario_issues():
    for template in list_templates():
        payload = build_quiz_payload(template.id, WizardContext())
        issues = validate_scenario(payload["questions"], payload.get("roles"), payload.get("injects"))
        assert not [issue for issue in issues if issue["level"] == "error"], template.id


def test_seed_wizard_is_available_to_any_authenticated_user():
    # The wizard is a normal user feature. Keep these routes separate from
    # administrative seed maintenance endpoints if those are added later.
    assert get_templates.__globals__["get_current_user"] is get_current_user
    assert preview_seed.__globals__["get_current_user"] is get_current_user
    assert create_seed.__globals__["get_current_user"] is get_current_user
