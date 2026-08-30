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
            "industries": list(t.industries),
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

    alignment = {
        "cloud_identity": {"tags": ["cloud", "identity", "mfa", "oauth"], "framework_mappings": {"NIST CSF 2.0": ["Govern", "Identify", "Protect", "Detect", "Respond", "Recover"], "CAF 4.0": ["A2 Risk Management", "B2 Identity and Access Control", "C1 Security Monitoring", "D1 Response and Recovery Planning"], "MITRE ATT&CK Enterprise": ["Initial Access", "Persistence", "Credential Access", "Lateral Movement"]}},
        "ransomware": {"tags": ["ransomware", "extortion", "recovery"], "framework_mappings": {"NIST CSF 2.0": ["Protect", "Detect", "Respond", "Recover"], "CAF 4.0": ["B4 System Security", "C1 Security Monitoring", "D1 Response and Recovery Planning", "D2 Lessons Learned"], "CIS Controls v8.1": ["8 Audit Log Management", "11 Data Recovery", "17 Incident Response Management"]}},
        "data_leak": {"tags": ["apt", "data-loss", "exfiltration", "privacy"], "framework_mappings": {"NIST CSF 2.0": ["Identify", "Detect", "Respond", "Recover"], "CAF 4.0": ["A3 Asset Management", "B3 Data Security", "C2 Threat Hunting", "D2 Lessons Learned"], "MITRE ATT&CK Enterprise": ["Discovery", "Collection", "Exfiltration", "Impact"]}},
        "insider_threat": {"tags": ["insider", "hr", "data-loss", "investigation"], "framework_mappings": {"NIST CSF 2.0": ["Govern", "Identify", "Detect", "Respond"], "CAF 4.0": ["A1 Governance", "B3 Data Security", "B6 Staff Awareness and Training", "D1 Response and Recovery Planning"]}},
        "disaster_recovery": {"tags": ["resilience", "business-continuity", "disaster-recovery", "supplier"], "framework_mappings": {"NIST CSF 2.0": ["Identify", "Protect", "Respond", "Recover"], "CAF 4.0": ["A4 Supply Chain", "B5 Resilient Networks and Systems", "D1 Response and Recovery Planning", "D2 Lessons Learned"], "CIS Controls v8.1": ["11 Data Recovery", "12 Network Infrastructure Management", "17 Incident Response Management"]}},
    }.get(template_id, {})
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
        tags=alignment.get("tags", []),
        difficulty=next((template.difficulty for template in list_templates() if template.id == template_id), None),
        framework_mappings=alignment.get("framework_mappings", {}),
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
