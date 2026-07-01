# SPDX-FileCopyrightText: 2025 CyberAsk
#
# SPDX-License-Identifier: MPL-2.0

from __future__ import annotations

import uuid
from datetime import datetime

from classquiz.db.models import Quiz, QuizQuestion, User
from classquiz.seed.context import WizardContext
from classquiz.seed.personalize import personalize_quiz
from classquiz.seed.registry import SeedTemplateMeta, get_template, list_templates
from classquiz.socket_server.branching import ensure_question_ids


def template_catalog() -> list[dict]:
    return [
        {
            "id": t.id,
            "name": t.name,
            "summary": t.summary,
            "topic": t.topic,
            "slide_count": t.slide_count,
            "branch_count": t.branch_count,
            "inject_count": t.inject_count,
            "difficulty": t.difficulty,
        }
        for t in list_templates()
    ]


def build_quiz_payload(template_id: str, context: WizardContext | None = None) -> dict:
    template: SeedTemplateMeta = get_template(template_id)
    ctx = context or WizardContext()
    raw = template.builder()
    return personalize_quiz(raw, ctx)


async def create_seed_quiz(template_id: str, context: WizardContext, user: User) -> Quiz:
    payload = build_quiz_payload(template_id, context)
    questions = [QuizQuestion.model_validate(q) for q in payload["questions"]]
    questions = ensure_question_ids(questions)

    quiz = Quiz(
        id=uuid.uuid4(),
        public=payload.get("public", False),
        title=payload["title"],
        description=payload.get("description", ""),
        user_id=user.id,
        questions=[q.model_dump() for q in questions],
        cover_image=payload.get("cover_image"),
        background_color=payload.get("background_color"),
        background_image=payload.get("background_image"),
        scenario_type=payload.get("scenario_type", "tabletop"),
        roles=payload.get("roles"),
        injects=payload.get("injects"),
        master_theme=payload.get("master_theme"),
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    await quiz.save()
    return quiz


async def seed_all_templates(context: WizardContext, user: User) -> list[Quiz]:
    created: list[Quiz] = []
    for template in list_templates():
        created.append(await create_seed_quiz(template.id, context, user))
    return created