# SPDX-FileCopyrightText: 2026 CyberAsk
# SPDX-License-Identifier: MPL-2.0

from __future__ import annotations

import secrets
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from classquiz.auth import get_current_user, get_admin_user
from classquiz.db.models import (
    DataRetentionPolicy,
    ExerciseAuditLog,
    ExerciseCompletion,
    ExerciseEvidence,
    ExerciseFacilitator,
    ExerciseNote,
    GameResults,
    Quiz,
    StorageItem,
    User,
)

router = APIRouter()


class FacilitatorInput(BaseModel):
    email: str
    permission: str = Field(default="facilitator", pattern="^(facilitator|observer)$")


class NoteInput(BaseModel):
    body: str = Field(min_length=1, max_length=10000)


class EvidenceInput(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    storage_item_id: uuid.UUID
    question_index: int | None = Field(default=None, ge=0)


class RetentionInput(BaseModel):
    results_days: int = Field(ge=1, le=3650)
    evidence_days: int = Field(ge=1, le=3650)
    audit_days: int = Field(ge=1, le=3650)


class CompletionInput(BaseModel):
    participant_name: str = Field(min_length=1, max_length=100)


async def _owned_game_result(game_id: uuid.UUID, user: User) -> GameResults:
    result = await GameResults.objects.get_or_none(id=game_id, user=user.id)
    if result is None:
        raise HTTPException(status_code=404, detail="Exercise result not found")
    return result


async def _accessible_game_result(game_id: uuid.UUID, user: User) -> GameResults:
    result = await GameResults.objects.get_or_none(id=game_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Exercise result not found")
    if result.user and result.user.id == user.id:
        return result
    facilitator = await ExerciseFacilitator.objects.get_or_none(game_id=str(game_id), user=user.id)
    if facilitator is None:
        raise HTTPException(status_code=403, detail="You are not assigned to this exercise")
    return result


async def _log(game_id: str | None, actor: User, action: str, details: dict | None = None) -> None:
    await ExerciseAuditLog.objects.create(game_id=game_id, actor=actor.id, action=action, details=details or {})


@router.get("/{game_id}/facilitators")
async def list_facilitators(game_id: uuid.UUID, user: User = Depends(get_admin_user)):
    await _owned_game_result(game_id, user)
    rows = await ExerciseFacilitator.objects.filter(game_id=str(game_id)).select_related("user").all()
    return [{"id": str(row.id), "email": row.user.email if row.user else None, "username": row.user.username if row.user else None, "permission": row.permission} for row in rows]


@router.post("/{game_id}/facilitators")
async def add_facilitator(game_id: uuid.UUID, payload: FacilitatorInput, user: User = Depends(get_admin_user)):
    await _owned_game_result(game_id, user)
    invited = await User.objects.get_or_none(email=payload.email)
    if invited is None:
        raise HTTPException(status_code=404, detail="User not found")
    row = await ExerciseFacilitator.objects.get_or_none(game_id=str(game_id), user=invited.id)
    if row is None:
        row = await ExerciseFacilitator.objects.create(game_id=str(game_id), user=invited.id, permission=payload.permission)
    else:
        row.permission = payload.permission
        await row.update()
    await _log(str(game_id), user, "facilitator_added", {"user_id": str(invited.id), "permission": payload.permission})
    return {"id": str(row.id), "email": invited.email, "permission": row.permission}


@router.delete("/{game_id}/facilitators/{facilitator_id}")
async def remove_facilitator(game_id: uuid.UUID, facilitator_id: uuid.UUID, user: User = Depends(get_admin_user)):
    await _owned_game_result(game_id, user)
    row = await ExerciseFacilitator.objects.get_or_none(id=facilitator_id, game_id=str(game_id))
    if row is None:
        raise HTTPException(status_code=404, detail="Facilitator not found")
    await row.delete()
    await _log(str(game_id), user, "facilitator_removed", {"facilitator_id": str(facilitator_id)})
    return {"deleted": True}


@router.get("/{game_id}/notes")
async def list_notes(game_id: uuid.UUID, user: User = Depends(get_current_user)):
    await _accessible_game_result(game_id, user)
    notes = await ExerciseNote.objects.filter(game_id=str(game_id)).select_related("author").order_by(ExerciseNote.created_at.asc()).all()
    return [{"id": str(note.id), "body": note.body, "author": note.author.username if note.author else None, "created_at": note.created_at.isoformat()} for note in notes]


@router.post("/{game_id}/notes")
async def create_note(game_id: uuid.UUID, payload: NoteInput, user: User = Depends(get_current_user)):
    await _accessible_game_result(game_id, user)
    note = await ExerciseNote.objects.create(game_id=str(game_id), author=user.id, body=payload.body)
    await _log(str(game_id), user, "note_created", {"note_id": str(note.id)})
    return {"id": str(note.id), "body": note.body, "author": user.username, "created_at": note.created_at.isoformat()}


@router.post("/{game_id}/evidence")
async def attach_evidence(game_id: uuid.UUID, payload: EvidenceInput, user: User = Depends(get_current_user)):
    await _accessible_game_result(game_id, user)
    item = await StorageItem.objects.get_or_none(id=payload.storage_item_id, user=user, deleted_at=None)
    if item is None:
        raise HTTPException(status_code=404, detail="Evidence file not found")
    evidence = await ExerciseEvidence.objects.create(game_id=str(game_id), uploaded_by=user.id, storage_item_id=item.id, title=payload.title, question_index=payload.question_index)
    await _log(str(game_id), user, "evidence_attached", {"evidence_id": str(evidence.id), "storage_item_id": str(item.id)})
    return {"id": str(evidence.id), "title": evidence.title, "storage_item_id": str(item.id), "question_index": evidence.question_index}


@router.get("/{game_id}/audit")
async def list_audit(game_id: uuid.UUID, user: User = Depends(get_admin_user)):
    await _owned_game_result(game_id, user)
    rows = await ExerciseAuditLog.objects.filter(game_id=str(game_id)).order_by(ExerciseAuditLog.created_at.desc()).all()
    return [{"id": str(row.id), "action": row.action, "details": row.details, "created_at": row.created_at.isoformat()} for row in rows]


@router.get("/retention")
async def get_retention(user: User = Depends(get_admin_user)):
    policy = await DataRetentionPolicy.objects.get_or_none(user=user.id)
    if policy is None:
        return {"results_days": 365, "evidence_days": 180, "audit_days": 730}
    return {"results_days": policy.results_days, "evidence_days": policy.evidence_days, "audit_days": policy.audit_days}


@router.put("/retention")
async def update_retention(payload: RetentionInput, user: User = Depends(get_admin_user)):
    policy = await DataRetentionPolicy.objects.get_or_none(user=user.id)
    if policy is None:
        policy = await DataRetentionPolicy.objects.create(user=user.id, **payload.model_dump())
    else:
        for key, value in payload.model_dump().items():
            setattr(policy, key, value)
        policy.updated_at = datetime.now()
        await policy.update()
    await _log(None, user, "retention_policy_updated", payload.model_dump())
    return await get_retention(user)


@router.post("/{game_id}/completion")
async def issue_completion(game_id: uuid.UUID, payload: CompletionInput, user: User = Depends(get_admin_user)):
    result = await _owned_game_result(game_id, user)
    completion = await ExerciseCompletion.objects.create(result=result.id, user=user.id, participant_name=payload.participant_name, completion_code=secrets.token_urlsafe(12).upper(), certificate_status="issued")
    await _log(str(game_id), user, "completion_issued", {"participant_name": payload.participant_name, "completion_id": str(completion.id)})
    return {"id": str(completion.id), "participant_name": completion.participant_name, "completion_code": completion.completion_code, "certificate_status": completion.certificate_status, "completed_at": completion.completed_at.isoformat()}


@router.get("/completion/{completion_code}")
async def verify_completion(completion_code: str):
    completion = await ExerciseCompletion.objects.get_or_none(completion_code=completion_code)
    if completion is None:
        raise HTTPException(status_code=404, detail="Completion record not found")
    return {"participant_name": completion.participant_name, "completion_code": completion.completion_code, "certificate_status": completion.certificate_status, "completed_at": completion.completed_at.isoformat()}
