# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


import csv
import io
import json as _json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from classquiz.auth import get_current_user
from classquiz.db.models import User, GameResults
router = APIRouter()


@router.get("/list")
async def list_game_results(
    user: User = Depends(get_current_user),
) -> list[GameResults]:
    results = (
        await GameResults.objects.select_related(GameResults.quiz)
        .order_by(GameResults.timestamp.desc())
        .all(user=user.id)
    )
    return results


@router.get("/list/{quiz_id}")
async def get_results_by_quiz(quiz_id: UUID, user: User = Depends(get_current_user)) -> list[GameResults]:
    res = await GameResults.objects.all(user=user.id, quiz=quiz_id)
    if res is None:
        raise HTTPException(status_code=404, detail="Game Result not found")
    else:
        return res


@router.get("/{game_id}")
async def get_game_result(game_id: UUID, user: User = Depends(get_current_user)) -> GameResults:
    res = await GameResults.objects.select_related(GameResults.quiz).get_or_none(user=user.id, id=game_id)
    if res is None:
        raise HTTPException(status_code=404, detail="Game Result not found")
    else:
        return res


class _SetNoteInput(BaseModel):
    note: str


@router.post("/set_note")
async def set_note(id: UUID, data: _SetNoteInput, user: User = Depends(get_current_user)) -> GameResults:
    res = await GameResults.objects.get_or_none(user=user.id, id=id)
    if res is None:
        raise HTTPException(status_code=404, detail="Game Result not found")
    res.note = data.note
    return await res.update()


def _compute_badges(player_scores: dict, answers: list) -> dict[str, list[str]]:
    """Compute achievement badges for each player based on their game performance."""
    badges: dict[str, list[str]] = {}

    if not player_scores:
        return badges

    scores = {k: int(v) for k, v in player_scores.items() if v is not None}
    if not scores:
        return badges

    # Perfect Score: player scored in top 10% or ≥900
    max_score = max(scores.values()) if scores else 0
    for player, score in scores.items():
        player_badges = []
        if score >= 900 or (max_score > 0 and score >= max_score * 0.95):
            player_badges.append("Perfect Score")
        if player_badges:
            badges[player] = player_badges

    # Top Player badge for #1
    if scores:
        top_player = max(scores, key=lambda p: scores[p])
        badges.setdefault(top_player, [])
        if "Top Player" not in badges[top_player]:
            badges[top_player].append("Top Player")

    # Most Improved: fastest answer (computed from answer records if available)
    if answers:
        fastest_time = None
        fastest_player = None
        for q_answers in answers:
            if not isinstance(q_answers, list):
                continue
            for a in q_answers:
                if not isinstance(a, dict):
                    continue
                if a.get("right") and a.get("time_taken") is not None:
                    t = float(a["time_taken"])
                    if fastest_time is None or t < fastest_time:
                        fastest_time = t
                        fastest_player = a.get("username")
        if fastest_player:
            badges.setdefault(fastest_player, [])
            if "Fastest Answer" not in badges[fastest_player]:
                badges[fastest_player].append("Fastest Answer")

    return badges


def _detect_anomalies(answers: list, player_scores: dict) -> list[dict]:
    """Detect score anomalies in game answer data.

    Flags:
    - "outlier": Player's per-question score > mean + 2.5σ across all players
    - "confidence_mismatch": confidence=3 (high) but score=0 on 3+ consecutive questions
    """
    import math
    flags: list[dict] = []

    # Per-question outlier detection
    for q_index, q_answers in enumerate(answers):
        if not isinstance(q_answers, list):
            continue
        scores_this_q = [float(a.get("score", 0)) for a in q_answers if isinstance(a, dict) and "score" in a]
        if len(scores_this_q) < 3:
            continue
        mean = sum(scores_this_q) / len(scores_this_q)
        variance = sum((s - mean) ** 2 for s in scores_this_q) / len(scores_this_q)
        sigma = math.sqrt(variance)
        threshold = mean + 2.5 * sigma
        for a in q_answers:
            if not isinstance(a, dict):
                continue
            score = float(a.get("score", 0))
            if sigma > 0 and score > threshold:
                flags.append({
                    "player": a.get("username", "unknown"),
                    "question_index": q_index,
                    "type": "outlier",
                    "detail": f"Score {score:.0f} vs mean {mean:.0f} (+{(score - mean) / sigma:.1f}σ)",
                })

    # Confidence mismatch: high confidence but wrong, on 3+ consecutive questions
    # Build per-player answer timeline
    player_timeline: dict[str, list[dict]] = {}
    for q_index, q_answers in enumerate(answers):
        if not isinstance(q_answers, list):
            continue
        for a in q_answers:
            if not isinstance(a, dict):
                continue
            username = a.get("username", "unknown")
            player_timeline.setdefault(username, []).append({
                "q": q_index,
                "confidence": a.get("confidence", None),
                "score": float(a.get("score", 0)),
                "correct": a.get("right", False),
            })

    for player, timeline in player_timeline.items():
        sorted_tl = sorted(timeline, key=lambda x: x["q"])
        run = 0
        for entry in sorted_tl:
            if entry.get("confidence") == 3 and not entry.get("correct") and entry.get("score", 1) == 0:
                run += 1
                if run == 3:
                    flags.append({
                        "player": player,
                        "question_index": entry["q"],
                        "type": "confidence_mismatch",
                        "detail": "High confidence declared but scored 0 on 3+ consecutive questions",
                    })
            else:
                run = 0

    return flags


@router.get("/aar/{game_id}")
async def get_after_action_report(game_id: UUID, user: User = Depends(get_current_user)) -> dict:
    """Return a structured After-Action Report for a completed tabletop game."""
    res = await GameResults.objects.get_or_none(user=user.id, id=game_id)
    if res is None:
        raise HTTPException(status_code=404, detail="Game Result not found")

    import json as _json

    def _safe_parse(val):
        if val is None:
            return None
        if isinstance(val, (dict, list)):
            return val
        try:
            return _json.loads(val)
        except (ValueError, TypeError):
            return val

    player_scores = _safe_parse(res.player_scores) or {}
    answers = _safe_parse(res.answers) or []
    badges = _compute_badges(player_scores, answers)

    facilitator_overrides = _safe_parse(res.facilitator_overrides) or []
    decision_log = None
    for entry in facilitator_overrides:
        if isinstance(entry, dict) and entry.get("type") == "decision_log":
            decision_log = entry.get("entries")
            break

    aar = {
        "metadata": {
            "game_id": str(res.id),
            "title": res.title,
            "description": res.description,
            "timestamp": res.timestamp.isoformat(),
            "player_count": res.player_count,
            "scenario_type": res.scenario_type,
            "note": res.note,
        },
        "scores": {
            "players": player_scores,
            "company_score": res.company_score,
            "company_score_timeline": _safe_parse(res.company_score_timeline),
            "score_visibility_policy": res.score_visibility_policy,
        },
        "achievements": badges,
        "anomaly_flags": _detect_anomalies(answers, player_scores),
        "branch_path": _safe_parse(res.branch_path),
        "player_roles": _safe_parse(res.player_roles),
        "injects_log": _safe_parse(res.injects_log),
        "situation_log": _safe_parse(res.situation_log),
        "decision_log": decision_log,
        "file_downloads_log": _safe_parse(res.file_downloads_log),
        "questions": _safe_parse(res.questions),
        "answers": answers,
    }
    return aar


@router.get("/export-csv/{result_id}")
async def export_result_csv(result_id: UUID, user: User = Depends(get_current_user)):
    """Export game results as a CSV file — one row per player-answer."""
    res = await GameResults.objects.get_or_none(user=user.id, id=result_id)
    if res is None:
        raise HTTPException(status_code=404, detail="Game Result not found")

    def _safe(val):
        if val is None:
            return None
        if isinstance(val, (dict, list)):
            return val
        try:
            return _json.loads(val)
        except (ValueError, TypeError):
            return val

    questions = _safe(res.questions) or []
    answers = _safe(res.answers) or []
    player_roles = _safe(res.player_roles) or {}

    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            "username", "role", "question_index", "question",
            "answer", "correct", "score", "confidence", "objective", "time_taken",
        ],
        extrasaction="ignore",
    )
    writer.writeheader()

    for q_idx, q_answers in enumerate(answers):
        if not isinstance(q_answers, list):
            continue
        q_text = ""
        q_objective = ""
        if q_idx < len(questions):
            q = questions[q_idx]
            q_text = q.get("question", "").replace("<[^>]*>", "") if isinstance(q, dict) else ""
            q_objective = q.get("objective", "") if isinstance(q, dict) else ""
        for a in q_answers:
            if not isinstance(a, dict):
                continue
            username = a.get("username", "")
            writer.writerow({
                "username": username,
                "role": player_roles.get(username, ""),
                "question_index": q_idx + 1,
                "question": q_text,
                "answer": a.get("answer", ""),
                "correct": "yes" if a.get("right") else "no",
                "score": a.get("score", ""),
                "confidence": a.get("confidence", ""),
                "objective": q_objective,
                "time_taken": a.get("time_taken", ""),
            })

    csv_bytes = output.getvalue().encode("utf-8-sig")  # BOM for Excel compat

    import urllib.parse
    safe_title = urllib.parse.quote(res.title or "results")
    return StreamingResponse(
        iter([csv_bytes]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=ClassQuiz-{safe_title}.csv"},
    )


# skipcq: PYL-W0105
"""
@router.get("/export/{result_id}", response_class=StreamingResponse)
async def export_result(result_id: UUID, user: User = Depends(get_current_user)):
    res = await GameResults.objects.get_or_none(user=user.id, id=result_id)
    if res is None:
        raise HTTPException(status_code=404, detail="Game Result not found")
    quiz = Quiz(title=res.title, questions=res.questions)
    spreadsheet = await generate_spreadsheet(
        quiz=quiz, quiz_results=data, player_fields=player_fields, player_scores=score_data
    )

    def iter_file():
        yield from spreadsheet

    return StreamingResponse(
        iter_file(),
        media_type="application/vnd.ms-excel",
        headers={
            "Content-Disposition": f"attachment;filename=ClassQuiz-{urllib.parse.quote(quiz.title)}-{datetime.strftime('%m-%d-%Y')}.xlsx"
            # noqa: E501
        },
    )

"""
