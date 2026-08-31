# SPDX-FileCopyrightText: 2026 CyberAsk
# SPDX-License-Identifier: MPL-2.0

from __future__ import annotations

import copy
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from classquiz.auth import get_admin_user
from classquiz.db.models import Quiz, ScenarioVersion, StorageItem, User
from classquiz.scenario_validation import validate_scenario

router = APIRouter()


class ScenarioMetadataInput(BaseModel):
    tags: list[str] = Field(default_factory=list)
    difficulty: str | None = None
    duration_minutes: int | None = Field(default=None, ge=1, le=1440)
    framework_mappings: dict[str, list[str]] = Field(default_factory=dict)
    reusable_roles: list[dict] = Field(default_factory=list)
    reusable_injects: list[dict] = Field(default_factory=list)
    evidence_packs: list[dict] = Field(default_factory=list)
    reference_documents: list[dict] = Field(default_factory=list)


class VersionInput(BaseModel):
    label: str = "Draft"
    change_summary: str | None = None
    content: dict


def _content(quiz: Quiz) -> dict:
    return {
        "title": quiz.title,
        "description": quiz.description,
        "questions": quiz.questions,
        "cover_image": quiz.cover_image,
        "background_color": quiz.background_color,
        "background_image": quiz.background_image,
        "scenario_type": quiz.scenario_type,
        "roles": quiz.roles or [],
        "role_descriptions": quiz.role_descriptions or {},
        "teams": quiz.teams or {},
        "injects": quiz.injects or [],
        "master_theme": quiz.master_theme or {},
        "tags": quiz.tags or [],
        "difficulty": quiz.difficulty,
        "duration_minutes": quiz.duration_minutes,
        "framework_mappings": quiz.framework_mappings or {},
        "reusable_roles": quiz.reusable_roles or [],
        "reusable_injects": quiz.reusable_injects or [],
        "evidence_packs": quiz.evidence_packs or [],
        "reference_documents": quiz.reference_documents or [],
    }


async def _owned_quiz(quiz_id: uuid.UUID, user: User) -> Quiz:
    quiz = await Quiz.objects.get_or_none(id=quiz_id, user_id=user.id)
    if quiz is None:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return quiz


async def _next_version(quiz: Quiz) -> int:
    versions = await ScenarioVersion.objects.filter(quiz=quiz.id).all()
    return max((version.version_number for version in versions), default=0) + 1


async def _owned_reference_documents(documents: list[dict], user: User) -> list[dict]:
    """Keep only safe, owned storage references in scenario metadata."""
    if len(documents) > 50:
        raise HTTPException(status_code=422, detail="A scenario can have at most 50 reference documents")
    normalised: list[dict] = []
    seen: set[str] = set()
    for document in documents:
        if not isinstance(document, dict):
            raise HTTPException(status_code=422, detail="Invalid reference document")
        try:
            document_id = uuid.UUID(str(document.get("id")))
        except (TypeError, ValueError, AttributeError):
            raise HTTPException(status_code=422, detail="Invalid reference document id")
        key = str(document_id)
        if key in seen:
            continue
        item = await StorageItem.objects.get_or_none(id=document_id, user=user.id, deleted_at=None)
        if item is None:
            raise HTTPException(status_code=404, detail="Reference document not found")
        seen.add(key)
        normalised.append({
            "id": key,
            "title": str(document.get("title") or item.filename or "Company reference")[:200],
            "category": str(document.get("category") or "Company policy")[:80],
            "filename": item.filename,
            "mime_type": item.mime_type,
            "description": str(document.get("description") or "")[:500],
        })
    return normalised


@router.get("/{quiz_id}/metadata")
async def get_metadata(quiz_id: uuid.UUID, user: User = Depends(get_admin_user)):
    quiz = await _owned_quiz(quiz_id, user)
    return {key: getattr(quiz, key) for key in ("tags", "difficulty", "duration_minutes", "framework_mappings", "reusable_roles", "reusable_injects", "evidence_packs", "reference_documents")}


@router.put("/{quiz_id}/metadata")
async def update_metadata(quiz_id: uuid.UUID, payload: ScenarioMetadataInput, user: User = Depends(get_admin_user)):
    quiz = await _owned_quiz(quiz_id, user)
    values = payload.model_dump()
    values["reference_documents"] = await _owned_reference_documents(values["reference_documents"], user)
    for key, value in values.items():
        setattr(quiz, key, value)
    quiz.updated_at = datetime.now()
    await quiz.update()
    return await get_metadata(quiz_id, user)


@router.get("/{quiz_id}/versions")
async def list_versions(quiz_id: uuid.UUID, user: User = Depends(get_admin_user)):
    quiz = await _owned_quiz(quiz_id, user)
    versions = await ScenarioVersion.objects.filter(quiz=quiz.id).order_by(ScenarioVersion.version_number.desc()).all()
    return [{"id": str(v.id), "version_number": v.version_number, "status": v.status, "label": v.label, "change_summary": v.change_summary, "created_at": v.created_at.isoformat()} for v in versions]


@router.get("/{quiz_id}/versions/{version_id}")
async def get_version(quiz_id: uuid.UUID, version_id: uuid.UUID, user: User = Depends(get_admin_user)):
	quiz = await _owned_quiz(quiz_id, user)
	version = await ScenarioVersion.objects.get_or_none(id=version_id, quiz=quiz.id)
	if version is None:
		raise HTTPException(status_code=404, detail="Version not found")
	return {"id": str(version.id), "version_number": version.version_number, "status": version.status, "label": version.label, "change_summary": version.change_summary, "created_at": version.created_at.isoformat(), "content": version.content}


@router.get("/{quiz_id}/versions/compare/{left_id}/{right_id}")
async def compare_versions(quiz_id: uuid.UUID, left_id: uuid.UUID, right_id: uuid.UUID, user: User = Depends(get_admin_user)):
    quiz = await _owned_quiz(quiz_id, user)
    left = await ScenarioVersion.objects.get_or_none(id=left_id, quiz=quiz.id)
    right = await ScenarioVersion.objects.get_or_none(id=right_id, quiz=quiz.id)
    if left is None or right is None:
        raise HTTPException(status_code=404, detail="Version not found")
    keys = sorted(set((left.content or {}).keys()) | set((right.content or {}).keys()))
    changed = [key for key in keys if (left.content or {}).get(key) != (right.content or {}).get(key)]
    return {"left": left.version_number, "right": right.version_number, "changed": changed, "left_content": left.content, "right_content": right.content}


@router.post("/{quiz_id}/versions")
async def create_version(quiz_id: uuid.UUID, payload: VersionInput, user: User = Depends(get_admin_user)):
    quiz = await _owned_quiz(quiz_id, user)
    version = await ScenarioVersion.objects.create(
        quiz=quiz.id, created_by=user.id, version_number=await _next_version(quiz), status="draft",
        label=payload.label, change_summary=payload.change_summary, content=payload.content,
    )
    return {"id": str(version.id), "version_number": version.version_number, "status": version.status}


@router.post("/{quiz_id}/versions/{version_id}/publish")
async def publish_version(quiz_id: uuid.UUID, version_id: uuid.UUID, user: User = Depends(get_admin_user)):
    quiz = await _owned_quiz(quiz_id, user)
    version = await ScenarioVersion.objects.get_or_none(id=version_id, quiz=quiz.id)
    if version is None:
        raise HTTPException(status_code=404, detail="Version not found")
    content = version.content or {}
    issues = validate_scenario(
        content.get("questions", []),
        content.get("roles"),
        content.get("injects"),
        {"framework_mappings": content.get("framework_mappings", {})},
    )
    blocking_issues = [issue for issue in issues if issue["level"] == "error"]
    if blocking_issues:
        raise HTTPException(status_code=422, detail={"message": "Version cannot be published until blocking issues are fixed", "issues": blocking_issues})
    published = await ScenarioVersion.objects.filter(quiz=quiz.id, status="published").all()
    for previous in published:
        if previous.id != version.id:
            previous.status = "archived"
            await previous.update()
    version.status = "published"
    await version.update()
    return {"id": str(version.id), "status": version.status}


@router.post("/{quiz_id}/versions/{version_id}/rollback")
async def rollback_version(quiz_id: uuid.UUID, version_id: uuid.UUID, user: User = Depends(get_admin_user)):
    quiz = await _owned_quiz(quiz_id, user)
    version = await ScenarioVersion.objects.get_or_none(id=version_id, quiz=quiz.id)
    if version is None:
        raise HTTPException(status_code=404, detail="Version not found")
    for key, value in copy.deepcopy(version.content).items():
        if hasattr(quiz, key) and key not in {"id", "user_id"}:
            setattr(quiz, key, value)
    quiz.updated_at = datetime.now()
    await quiz.update()
    restored = await ScenarioVersion.objects.create(
        quiz=quiz.id, created_by=user.id, version_number=await _next_version(quiz), status="draft",
        label=f"Rollback to v{version.version_number}", change_summary=f"Restored scenario content from version {version.version_number}",
        parent_version_id=version.id, content=_content(quiz),
    )
    return {"restored_version": version.version_number, "scenario_id": str(quiz.id), "new_version_id": str(restored.id)}


@router.post("/{quiz_id}/duplicate")
async def duplicate_scenario(quiz_id: uuid.UUID, user: User = Depends(get_admin_user)):
    source = await _owned_quiz(quiz_id, user)
    data = _content(source)
    clone = await Quiz.objects.create(**{**data, "title": f"{source.title} (Copy)", "user_id": user.id, "public": False})
    await ScenarioVersion.objects.create(quiz=clone.id, created_by=user.id, version_number=1, status="draft", label="Initial copy", content=_content(clone))
    return {"id": str(clone.id), "title": clone.title}


@router.post("/{quiz_id}/fork")
async def fork_scenario(quiz_id: uuid.UUID, user: User = Depends(get_admin_user)):
    return await duplicate_scenario(quiz_id, user)
