# SPDX-FileCopyrightText: 2025 CyberAsk
#
# SPDX-License-Identifier: MPL-2.0

from __future__ import annotations

from pydantic import BaseModel, Field

from fastapi import APIRouter, Depends, HTTPException

from classquiz.auth import get_admin_user
from classquiz.db.models import User
from classquiz.seed.context import WizardContext
from classquiz.seed.service import build_quiz_payload, create_seed_quiz, seed_all_templates, template_catalog

router = APIRouter()


class WizardContextInput(BaseModel):
    company_name: str = "Acme Financial Services"
    industry: str = "Financial Services"
    location: str = "London, United Kingdom"
    exercise_date: str | None = None
    ceo_name: str = "Jane Morgan"
    ciso_name: str = "David Chen"
    employee_count: str = "2,400"
    primary_system: str = "customer banking portal"
    regulator: str = "ICO"
    region: str = "UK"
    domain: str = "acmefinancial.example"
    data_classification: str = "PCI and personal financial data"

    def to_context(self) -> WizardContext:
        return WizardContext.from_dict(self.model_dump(exclude_none=True))


class CreateSeedRequest(BaseModel):
    template_id: str | None = Field(
        default=None,
        description="ransomware | data_leak | insider_threat | disaster_recovery",
    )
    context: WizardContextInput = Field(default_factory=WizardContextInput)
    create_all: bool = False


class CreateSeedResponse(BaseModel):
    quiz_ids: list[str]
    titles: list[str]


class PreviewSeedResponse(BaseModel):
    title: str
    description: str
    slide_count: int
    branch_count: int
    inject_count: int
    roles: list[str]
    question_titles: list[str]


@router.get("/templates")
async def get_templates(_: User = Depends(get_admin_user)):
    return {"templates": template_catalog()}


@router.post("/preview", response_model=PreviewSeedResponse)
async def preview_seed(payload: CreateSeedRequest, _: User = Depends(get_admin_user)):
    if payload.create_all:
        raise HTTPException(status_code=400, detail="Preview does not support create_all")
    if not payload.template_id:
        raise HTTPException(status_code=422, detail="template_id is required for preview")

    try:
        quiz_data = build_quiz_payload(payload.template_id, payload.context.to_context())
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    questions = quiz_data.get("questions", [])
    branch_count = sum(
        1
        for q in questions
        if q.get("type") == "ABCD"
        and any(a.get("next_question_id") for a in (q.get("answers") or []) if isinstance(a, dict))
    )

    from classquiz.seed.registry import get_template

    meta = get_template(payload.template_id)

    return PreviewSeedResponse(
        title=quiz_data.get("title", ""),
        description=quiz_data.get("description", ""),
        slide_count=len(questions),
        branch_count=branch_count,
        inject_count=len(quiz_data.get("injects") or []),
        roles=quiz_data.get("roles") or [],
        question_titles=[q.get("question", "") for q in questions],
    )


@router.post("/create", response_model=CreateSeedResponse)
async def create_seed(payload: CreateSeedRequest, user: User = Depends(get_admin_user)):
    ctx = payload.context.to_context()

    if not payload.create_all and not payload.template_id:
        raise HTTPException(status_code=422, detail="template_id is required unless create_all is true")

    try:
        if payload.create_all:
            quizzes = await seed_all_templates(ctx, user)
        else:
            quizzes = [await create_seed_quiz(payload.template_id, ctx, user)]
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return CreateSeedResponse(
        quiz_ids=[str(q.id) for q in quizzes],
        titles=[q.title for q in quizzes],
    )