# SPDX-FileCopyrightText: 2025
#
# SPDX-License-Identifier: MPL-2.0

from __future__ import annotations

import json
from collections import Counter

from classquiz.config import redis
from classquiz.db.models import (
    PlayGame,
    QuizQuestion,
    ABCDQuizAnswer,
    AnswerDataList,
    Inject,
)


def find_question_by_id(questions: list[QuizQuestion], question_id: str) -> tuple[int, QuizQuestion] | None:
    """Return (index, question) for the given question ID, or None."""
    for idx, q in enumerate(questions):
        if q.id == question_id:
            return idx, q
    return None


def find_question_index_by_id(questions: list[QuizQuestion], question_id: str) -> int | None:
    """Return the list index for the given question ID, or None."""
    result = find_question_by_id(questions, question_id)
    return result[0] if result is not None else None


def is_tabletop(game_data: PlayGame) -> bool:
    return game_data.scenario_type == "tabletop"


def get_allowed_roles(question: QuizQuestion) -> list[str] | None:
    """Return the allowed roles for a question, or None if all may answer."""
    return question.allowed_roles if question.allowed_roles else None


async def get_player_role(game_pin: str, username: str) -> str | None:
    """Look up a player's assigned role from Redis."""
    role = await redis.hget(f"game_session:{game_pin}:player_roles", username)
    return role


async def get_all_player_roles(game_pin: str) -> dict[str, str]:
    """Return {username: role} mapping for all assigned players."""
    return await redis.hgetall(f"game_session:{game_pin}:player_roles") or {}


async def set_player_role(game_pin: str, username: str, role: str) -> None:
    """Assign a role to a player in Redis."""
    await redis.hset(f"game_session:{game_pin}:player_roles", username, role)


async def get_eligible_player_count(game_pin: str, allowed_roles: list[str] | None) -> int:
    """Count players whose role is in allowed_roles. If None, count all players."""
    if allowed_roles is None:
        return await redis.scard(f"game_session:{game_pin}:players")
    roles = await get_all_player_roles(game_pin)
    return sum(1 for role in roles.values() if role in allowed_roles)


def check_player_role_allowed(player_role: str | None, allowed_roles: list[str] | None) -> bool:
    """Check if a player with the given role may answer this question."""
    if allowed_roles is None:
        return True
    if player_role is None:
        return False
    return player_role in allowed_roles


def tally_votes(answers: AnswerDataList) -> Counter:
    """Count votes per answer text from the answer list."""
    return Counter(a.answer for a in answers)


def resolve_next_question_id(
    question: QuizQuestion,
    winning_answer_text: str | None,
) -> str | None:
    """Given the winning answer text, find the next_question_id from the branch mapping.

    Falls back to default_next_question_id, then None (= scenario complete).
    """
    if winning_answer_text is not None and isinstance(question.answers, list):
        for ans in question.answers:
            if isinstance(ans, ABCDQuizAnswer) and ans.answer == winning_answer_text:
                if ans.next_question_id:
                    return ans.next_question_id
                break

    return question.default_next_question_id


def determine_winning_answer(vote_tally: Counter) -> tuple[str | None, bool]:
    """Return (winning_answer_text, is_tie).

    If there's a clear majority, return that answer with is_tie=False.
    If there's a tie among the top answers, return None with is_tie=True.
    If no votes, return (None, False).
    """
    if not vote_tally:
        return None, False

    most_common = vote_tally.most_common()
    top_count = most_common[0][1]
    tied = [answer for answer, count in most_common if count == top_count]

    if len(tied) == 1:
        return tied[0], False
    else:
        return None, True


async def append_branch_path(game_pin: str, question_id: str) -> None:
    """Record a visited question ID in the branch path."""
    await redis.rpush(f"game_session:{game_pin}:branch_path", question_id)
    await redis.expire(f"game_session:{game_pin}:branch_path", 7200)


async def get_branch_path(game_pin: str) -> list[str]:
    """Get the list of question IDs visited so far."""
    path = await redis.lrange(f"game_session:{game_pin}:branch_path", 0, -1)
    return path or []


async def log_facilitator_override(game_pin: str, from_question_id: str | None, forced_next_id: str) -> None:
    """Log a facilitator override action."""
    entry = json.dumps({
        "from_question": from_question_id,
        "forced_next": forced_next_id,
        "type": "facilitator_override",
    })
    await redis.rpush(f"game_session:{game_pin}:overrides", entry)
    await redis.expire(f"game_session:{game_pin}:overrides", 7200)


async def get_facilitator_overrides(game_pin: str) -> list[dict]:
    """Get all facilitator override entries."""
    raw = await redis.lrange(f"game_session:{game_pin}:overrides", 0, -1)
    return [json.loads(r) for r in (raw or [])]


# ============================================================
# Inject helpers
# ============================================================

def ensure_inject_ids(injects: list[Inject] | None) -> list[Inject]:
    """Assign UUIDs to injects that are missing an ID."""
    import uuid as _uuid
    if not injects:
        return injects or []
    for inj in injects:
        if not inj.id:
            inj.id = str(_uuid.uuid4())
    return injects


def get_auto_injects_for_question(injects: list[Inject] | None, question_id: str) -> list[Inject]:
    """Return injects that should auto-fire after the given question."""
    if not injects:
        return []
    return [inj for inj in injects if inj.trigger_after_question_id == question_id]


async def log_inject(game_pin: str, inject: Inject, triggered_by: str = "auto") -> None:
    """Record an inject that was pushed during the session."""
    from datetime import datetime as _dt
    entry = json.dumps({
        "inject_id": inject.id,
        "title": inject.title,
        "severity": inject.severity,
        "triggered_by": triggered_by,
        "timestamp": _dt.now().isoformat(),
    })
    await redis.rpush(f"game_session:{game_pin}:injects_log", entry)
    await redis.expire(f"game_session:{game_pin}:injects_log", 7200)


async def get_injects_log(game_pin: str) -> list[dict]:
    """Get all inject events that were pushed during the session."""
    raw = await redis.lrange(f"game_session:{game_pin}:injects_log", 0, -1)
    return [json.loads(r) for r in (raw or [])]


# ============================================================
# Situation Room helpers
# ============================================================

async def set_situation_status(game_pin: str, status: dict) -> None:
    """Store the current situation room status in Redis."""
    await redis.set(f"game_session:{game_pin}:situation_status", json.dumps(status), ex=7200)


async def get_situation_status(game_pin: str) -> dict | None:
    """Retrieve the current situation room status."""
    raw = await redis.get(f"game_session:{game_pin}:situation_status")
    return json.loads(raw) if raw else None


async def log_situation_change(game_pin: str, status: dict) -> None:
    """Append a situation status change to the log."""
    from datetime import datetime as _dt
    entry = json.dumps({**status, "timestamp": _dt.now().isoformat()})
    await redis.rpush(f"game_session:{game_pin}:situation_log", entry)
    await redis.expire(f"game_session:{game_pin}:situation_log", 7200)


async def get_situation_log(game_pin: str) -> list[dict]:
    """Get the full history of situation status changes."""
    raw = await redis.lrange(f"game_session:{game_pin}:situation_log", 0, -1)
    return [json.loads(r) for r in (raw or [])]


def ensure_question_ids(questions: list[QuizQuestion]) -> list[QuizQuestion]:
    """Ensure every question has an ID. Assigns UUIDs to any question missing one."""
    import uuid
    for q in questions:
        if not q.id:
            q.id = str(uuid.uuid4())
    return questions


TABLETOP_FLAT_SCORE = 100
