# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


import base64
import hashlib
import json
import os
import random
import re
import asyncio

import socketio
from cryptography.fernet import Fernet
try:
    from better_profanity import profanity
except ImportError:
    profanity = None

from classquiz.config import redis, settings
from classquiz.db.models import (
    PlayGame,
    QuizQuestionType,
    GameSession,
    GamePlayer,
    VotingQuizAnswer,
    AnswerDataList,
    AnswerData,
    Inject,
)
from pydantic import BaseModel, ValidationError
from datetime import datetime

from classquiz.socket_server.helpers import (
    check_answer,
    check_captcha,
    has_already_answered,
)
from .models import (
    RejoinGameData,
    JoinGameData,
    ReturnQuestion,
    SubmitAnswerData,
    RegisterAsAdminData,
    KickPlayerInput,
    ConnectSessionIdEvent,
    ChatMessage,
    SendChatMessageData,
)
from classquiz.socket_server.branching import (
    is_tabletop,
    get_allowed_roles,
    get_player_role,
    get_all_player_roles,
    set_player_role,
    get_eligible_player_count,
    check_player_role_allowed,
    tally_votes,
    resolve_next_question_id,
    determine_winning_answer,
    append_branch_path,
    get_branch_path,
    log_facilitator_override,
    get_facilitator_overrides,
    find_question_by_id,
    find_question_index_by_id,
    ensure_question_ids,
    ensure_inject_ids,
    get_auto_injects_for_question,
    log_inject,
    get_injects_log,
    set_situation_status,
    get_situation_status,
    log_situation_change,
    get_situation_log,
    TABLETOP_FLAT_SCORE,
)

from classquiz.socket_server.export_helpers import save_quiz_to_storage
from classquiz.socket_server.session import get_session, save_session

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=[])
settings = settings()


def get_fernet_key() -> bytes:
    hlib = hashlib.sha256()
    hlib.update(settings.secret_key.encode("utf-8"))
    return base64.urlsafe_b64encode(hlib.hexdigest().encode("latin-1")[:32])


fernet = Fernet(get_fernet_key())
if profanity is not None:
    profanity.load_censor_words()

CHAT_HISTORY_LIMIT = 40
CHAT_MESSAGE_MAX_LEN = 280
COUNTDOWN_DURATION_SECONDS = 5
CHAT_COOLDOWN_SECONDS = 0.8
CHAT_BURST_WINDOW_SECONDS = 10
CHAT_BURST_LIMIT = 12
SOCKET_DIAGNOSTICS_DEFAULT_ENABLED = False
_PROFANITY_EXTRA_TERMS = {
    "rape",
    "rapist",
    "porn",
    "sexual",
    "sex",
    "nude",
    "naked",
    "cum",
    "dick",
    "penis",
    "vagina",
    "cock",
    "bitch",
    "bastard",
    "asshole",
    "faggot",
    "nigger",
    "retard",
}


def _normalize_text(input_text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", input_text.lower())


def contains_blocked_language(input_text: str) -> bool:
    if not input_text:
        return False
    text_lower = input_text.lower()
    if profanity is not None and profanity.contains_profanity(text_lower):
        return True
    normalized = _normalize_text(text_lower)
    if any(term in normalized for term in _PROFANITY_EXTRA_TERMS):
        return True
    return False


async def get_chat_history(game_pin: str) -> list[dict]:
    key = f"game_session:{game_pin}:chat_history"
    messages = await redis.lrange(key, 0, CHAT_HISTORY_LIMIT - 1)
    result: list[dict] = []
    for message_raw in reversed(messages):
        try:
            message = ChatMessage.model_validate_json(message_raw)
            result.append(message.model_dump(mode="json"))
        except ValidationError:
            continue
    return result


async def get_socket_diagnostics_enabled(game_pin: str) -> bool:
    value = await redis.get(f"game:{game_pin}:socket_diagnostics_enabled")
    if value is None:
        return SOCKET_DIAGNOSTICS_DEFAULT_ENABLED
    return str(value).lower() in {"1", "true", "yes", "on"}


async def emit_socket_diagnostics_visibility(game_pin: str, room: str | None = None):
    enabled = await get_socket_diagnostics_enabled(game_pin)
    await sio.emit(
        "socket_diagnostics_visibility",
        {"enabled": enabled},
        room=game_pin if room is None else room,
    )


async def append_chat_message(game_pin: str, message: ChatMessage):
    key = f"game_session:{game_pin}:chat_history"
    await redis.lpush(key, message.model_dump_json())
    await redis.ltrim(key, 0, CHAT_HISTORY_LIMIT - 1)
    await redis.expire(key, 7200)


async def get_countdown_state(game_pin: str) -> dict | None:
    countdown_start = await redis.get(f"game:{game_pin}:countdown_start")
    countdown_duration = await redis.get(f"game:{game_pin}:countdown_duration")
    if countdown_start is None or countdown_duration is None:
        return None
    try:
        start_dt = datetime.fromisoformat(countdown_start)
        duration = int(countdown_duration)
    except ValueError:
        return None

    elapsed = (datetime.now() - start_dt).total_seconds()
    remaining = max(0, duration - elapsed)
    return {
        "server_timestamp": countdown_start,
        "duration_seconds": duration,
        "remaining_seconds": remaining,
    }


async def enforce_chat_rate_limit(game_pin: str, username: str) -> str | None:
    cooldown_key = f"game_session:{game_pin}:chat:last_message_at:{username}"
    burst_key = f"game_session:{game_pin}:chat:burst:{username}"
    now_ts = datetime.now().timestamp()

    last_message_at = await redis.get(cooldown_key)
    if last_message_at is not None:
        try:
            if now_ts - float(last_message_at) < CHAT_COOLDOWN_SECONDS:
                return "rate_limited"
        except ValueError:
            pass

    await redis.set(cooldown_key, str(now_ts), ex=7200)
    burst_count = await redis.incr(burst_key)
    if burst_count == 1:
        await redis.expire(burst_key, CHAT_BURST_WINDOW_SECONDS)
    if burst_count > CHAT_BURST_LIMIT:
        return "too_many_messages"
    return None


async def get_lobby_players(game_pin: str) -> list[dict]:
    """Return enriched player data (username, avatar_params) sorted by username."""
    players_raw = await redis.smembers(f"game_session:{game_pin}:players")
    players: list[dict] = []
    for player_raw in players_raw:
        try:
            player = GamePlayer.model_validate_json(player_raw)
            players.append({
                "username": player.username,
                "avatar_params": player.avatar_params,
            })
        except ValidationError:
            continue
    return sorted(players, key=lambda p: p["username"].lower())


async def get_avatar_map(game_pin: str) -> dict:
    players = await get_lobby_players(game_pin)
    return {player["username"]: player.get("avatar_params") for player in players}


async def get_player_record(game_pin: str, username: str) -> GamePlayer | None:
    players_raw = await redis.smembers(f"game_session:{game_pin}:players")
    for player_raw in players_raw:
        try:
            player = GamePlayer.model_validate_json(player_raw)
        except ValidationError:
            continue
        if player.username == username:
            return player
    return None


async def remove_player_record(game_pin: str, username: str):
    player = await get_player_record(game_pin, username)
    if player is None:
        return
    await redis.srem(f"game_session:{game_pin}:players", player.model_dump_json())


async def emit_lobby_state(game_pin: str, room: str | None = None):
    players = await get_lobby_players(game_pin)
    await sio.emit(
        "lobby_state",
        {"players": players, "player_count": len(players)},
        room=game_pin if room is None else room,
    )


async def emit_current_question(room: str, game_data: PlayGame):
    if game_data.current_question < 0:
        return
    current_q = game_data.questions[game_data.current_question]
    temp_return = game_data.model_dump(include={"questions"})["questions"][game_data.current_question]
    game_pin = game_data.game_pin

    if current_q.type == QuizQuestionType.SLIDE:
        payload = {
            "question_index": game_data.current_question,
            "question": {
                **temp_return,
                "type": current_q.type,
            },
        }
        if is_tabletop(game_data):
            payload["allowed_roles"] = current_q.allowed_roles
            payload["decision_mode"] = current_q.decision_mode
            payload["discussion_time"] = current_q.discussion_time
        await sio.emit("set_question_number", payload, room=room)
    else:
        if current_q.type == QuizQuestionType.VOTING:
            for i in range(len(temp_return["answers"])):
                temp_return["answers"][i] = VotingQuizAnswer(**temp_return["answers"][i])
        temp_return["type"] = current_q.type
        payload = {
            "question_index": game_data.current_question,
            "question": ReturnQuestion(**temp_return).model_dump(),
        }
        if is_tabletop(game_data):
            payload["allowed_roles"] = current_q.allowed_roles
            payload["decision_mode"] = current_q.decision_mode
            payload["discussion_time"] = current_q.discussion_time
        await sio.emit("set_question_number", payload, room=room)

    # Send facilitator notes to admin only
    if is_tabletop(game_data) and current_q.facilitator_notes:
        await sio.emit(
            "facilitator_notes",
            {"question_index": game_data.current_question, "notes": current_q.facilitator_notes},
            room=f"admin:{game_pin}",
        )

    # Auto-fire injects triggered by this question
    if is_tabletop(game_data) and game_data.injects and current_q.id:
        auto_injects = get_auto_injects_for_question(game_data.injects, current_q.id)
        for inj in auto_injects:
            await log_inject(game_pin, inj, triggered_by="auto")
            await sio.emit("inject_received", inj.model_dump(), room=game_pin)


async def generate_final_results(game_data: PlayGame, game_pin: str) -> dict:
    results = {}
    for i in range(len(game_data.questions)):
        redis_res = await redis.get(f"game_session:{game_pin}:{i}")
        if redis_res is None:
            continue
        else:
            results[str(i)] = json.loads(redis_res)
    return results


def calculate_score(z: float, t: int) -> int:
    t = t * 1000
    res = (t - z) / t
    return int(res * 1000)


async def set_answer(answers, game_pin: str, q_index: int, data: AnswerData) -> AnswerDataList:
    if answers is None:
        answers = AnswerDataList([data])
    else:
        answers = AnswerDataList.model_validate_json(answers)
        answers.append(data)
    await redis.set(
        f"game_session:{game_pin}:{q_index}",
        answers.model_dump_json(),
        ex=7200,
    )
    return answers


@sio.event
async def rejoin_game(sid: str, data: dict):
    redis_res = await redis.get(f"game:{data['game_pin']}")
    if redis_res is None:
        await sio.emit("game_not_found", room=sid)
        return
    try:
        data = RejoinGameData(**data)
    except ValidationError as e:
        await sio.emit("error", room=sid)
        print(e)
    redis_sid_key = f"game_session:{data.game_pin}:players:{data.username}"
    old_sid = await redis.get(redis_sid_key)
    if old_sid != data.old_sid:
        return
    encrypted_datetime = fernet.encrypt(datetime.now().isoformat().encode("utf-8")).decode("utf-8")
    await sio.emit("time_sync", encrypted_datetime, room=sid)
    await redis.set(redis_sid_key, sid)
    existing_player = await get_player_record(data.game_pin, data.username)
    existing_avatar_params = existing_player.avatar_params if existing_player is not None else None
    await remove_player_record(data.game_pin, data.username)
    avatar_params = data.avatar_params.model_dump() if data.avatar_params else existing_avatar_params
    await redis.sadd(
        f"game_session:{data.game_pin}:players",
        GamePlayer(username=data.username, sid=sid, avatar_params=avatar_params).model_dump_json(),
    )
    game_data = PlayGame.model_validate_json(redis_res)
    session = {
        "game_pin": data.game_pin,
        "username": data.username,
        "sid_custom": sid,
        "admin": False,
    }
    await save_session(sid, sio, session)
    await sio.enter_room(sid, data.game_pin)
    payload = game_data.to_player_data()
    payload["players"] = await get_lobby_players(data.game_pin)
    await sio.emit(
        "rejoined_game",
        payload,
        room=sid,
    )
    await emit_socket_diagnostics_visibility(data.game_pin, room=sid)
    await sio.emit("chat_history", {"messages": await get_chat_history(data.game_pin)}, room=sid)
    await emit_lobby_state(data.game_pin)
    countdown_state = await get_countdown_state(data.game_pin)
    if countdown_state is not None and countdown_state["remaining_seconds"] > 0:
        await sio.emit("countdown_start", countdown_state, room=sid)
    if game_data.started and game_data.question_show:
        await emit_current_question(sid, game_data)


@sio.event
async def join_game(sid: str, data: dict):
    redis_res = await redis.get(f"game:{data['game_pin']}")
    if redis_res is None:
        await sio.emit("game_not_found", room=sid)
        return
    try:
        data = JoinGameData(**data)
    except ValidationError as e:
        await sio.emit("error", room=sid)
        print(e)
        return
    game_data = PlayGame.model_validate_json(redis_res)
    if contains_blocked_language(data.username):
        await sio.emit("username_blocked", {"reason": "username_blocked_by_moderation"}, room=sid)
        return
    if game_data.started:
        await sio.emit("game_already_started", room=sid)
        return
    # +++ START checking captcha +++
    if game_data.captcha_enabled:
        captcha_res = await check_captcha(data.captcha)
        if not captcha_res:
            return
    # --- END checking captcha ---
    if await redis.get(f"game_session:{data.game_pin}:players:{data.username}") is not None:
        await sio.emit("username_already_exists", room=sid)
        return

    session = {
        "game_pin": data.game_pin,
        "username": data.username,
        "sid_custom": sid,
        "admin": False,
    }
    await save_session(sid, sio, session)
    await redis.set(f"game_session:{data.game_pin}:players:{data.username}", sid, ex=7200)
    await GamePlayer(
        username=data.username,
        sid=sid,
        avatar_params=data.avatar_params.model_dump() if data.avatar_params else None
    ).to_player_stack(data.game_pin)
    await sio.enter_room(sid, data.game_pin)

    lobby_players = await get_lobby_players(data.game_pin)
    payload = game_data.to_player_data()
    payload["players"] = lobby_players
    payload["player_count"] = len(lobby_players)
    await sio.emit(
        "joined_game",
        payload,
        room=sid,
    )
    await emit_socket_diagnostics_visibility(data.game_pin, room=sid)
    await sio.emit("chat_history", {"messages": await get_chat_history(data.game_pin)}, room=sid)
    countdown_state = await get_countdown_state(data.game_pin)
    if countdown_state is not None and countdown_state["remaining_seconds"] > 0:
        await sio.emit("countdown_start", countdown_state, room=sid)

    if data.custom_field == "":
        data.custom_field = None
    if data.custom_field is not None:
        await redis.hset(
            f"game:{data.game_pin}:players:custom_fields",
            data.username,
            data.custom_field,
        )

    await sio.emit(
        "player_joined",
        {
            "username": data.username,
            "sid": sid,
            "avatar_params": data.avatar_params.model_dump() if data.avatar_params else None,
        },
        room=f"admin:{data.game_pin}",
    )
    await emit_lobby_state(data.game_pin)
    # +++ Time-Sync +++
    encrypted_datetime = fernet.encrypt(datetime.now().isoformat().encode("utf-8")).decode("utf-8")
    await sio.emit("time_sync", encrypted_datetime, room=sid)
    # --- Time-Sync ---


@sio.event
async def start_game(sid: str, _data: dict):
    session = await get_session(sid, sio)
    if not session["admin"]:
        return
    game_data = await PlayGame.get_from_redis(session["game_pin"])
    if len(game_data.questions) == 0:
        return

    # Ensure all questions have IDs for tabletop branching
    if is_tabletop(game_data):
        game_data.questions = ensure_question_ids(game_data.questions)
        game_data.injects = ensure_inject_ids(game_data.injects)

    game_data.started = True
    game_data.current_question = 0
    game_data.question_show = False

    # Track current question ID for tabletop branching
    if is_tabletop(game_data) and game_data.questions[0].id:
        game_data.current_question_id = game_data.questions[0].id
        await append_branch_path(session["game_pin"], game_data.questions[0].id)

    await game_data.save(session["game_pin"])
    await redis.delete(f"game_in_lobby:{game_data.user_id.hex}")

    # Emit roles to all players for tabletop mode
    if is_tabletop(game_data):
        roles = await get_all_player_roles(session["game_pin"])
        await sio.emit("roles_updated", {"player_roles": roles}, room=session["game_pin"])

    await sio.emit("start_game", room=session["game_pin"])

    countdown_start = datetime.now().isoformat()
    await redis.set(f"game:{session['game_pin']}:countdown_start", countdown_start, ex=7200)
    await redis.set(
        f"game:{session['game_pin']}:countdown_duration",
        COUNTDOWN_DURATION_SECONDS,
        ex=7200,
    )
    await sio.emit(
        "countdown_start",
        {
            "server_timestamp": countdown_start,
            "duration_seconds": COUNTDOWN_DURATION_SECONDS,
            "remaining_seconds": COUNTDOWN_DURATION_SECONDS,
        },
        room=session["game_pin"],
    )
    await asyncio.sleep(COUNTDOWN_DURATION_SECONDS)

    game_data = await PlayGame.get_from_redis(session["game_pin"])
    game_data.question_show = True
    await game_data.save(session["game_pin"])
    await redis.set(f"game:{session['game_pin']}:current_time", datetime.now().isoformat(), ex=7200)
    await redis.delete(f"game:{session['game_pin']}:countdown_start")
    await redis.delete(f"game:{session['game_pin']}:countdown_duration")
    await emit_current_question(session["game_pin"], game_data)


@sio.event
async def register_as_admin(sid: str, data: dict):
    try:
        data = RegisterAsAdminData(**data)
    except ValidationError as e:
        await sio.emit("error", room=sid)
        print(e)
        return
    game_pin = data.game_pin
    game_id = data.game_id
    if await redis.get(f"game_session:{game_pin}") is not None:
        await sio.emit("already_registered_as_admin", room=sid)
        return
    await GameSession(admin=sid, game_id=game_id, answers=[]).save(game_pin)
    session = {"game_pin": game_pin, "admin": True, "remote": False}
    await save_session(sid, sio, session)
    await sio.enter_room(sid, game_pin)
    await sio.enter_room(sid, f"admin:{data.game_pin}")
    await sio.emit(
        "registered_as_admin",
        {"game_id": game_id, "game": await redis.get(f"game:{game_pin}")},
        room=sid,
    )
    await emit_socket_diagnostics_visibility(game_pin, room=sid)
    await sio.emit("chat_history", {"messages": await get_chat_history(game_pin)}, room=sid)
    countdown_state = await get_countdown_state(game_pin)
    if countdown_state is not None and countdown_state["remaining_seconds"] > 0:
        await sio.emit("countdown_start", countdown_state, room=sid)
    await debug_status(sid)


@sio.event
async def send_chat_message(sid: str, data: dict):
    try:
        data = SendChatMessageData(**data)
    except ValidationError as e:
        await sio.emit("error", room=sid)
        print(e)
        return

    session = await get_session(sid, sio)
    game_pin = session.get("game_pin")
    username = session.get("username", "Admin")
    if game_pin is None:
        await sio.emit("chat_blocked", {"reason": "not_in_game"}, room=sid)
        return

    game_data = await PlayGame.get_from_redis(game_pin)
    if game_data.started:
        await sio.emit("chat_blocked", {"reason": "game_already_started"}, room=sid)
        return

    content = data.content.strip()
    if content == "":
        await sio.emit("chat_blocked", {"reason": "empty_message"}, room=sid)
        return
    if len(content) > CHAT_MESSAGE_MAX_LEN:
        await sio.emit("chat_blocked", {"reason": "message_too_long"}, room=sid)
        return
    rate_limit_reason = await enforce_chat_rate_limit(game_pin, username)
    if rate_limit_reason is not None:
        await sio.emit("chat_blocked", {"reason": rate_limit_reason}, room=sid)
        return
    if contains_blocked_language(content):
        await sio.emit("chat_blocked", {"reason": "message_blocked_by_moderation"}, room=sid)
        return

    player = None
    if not session.get("admin", False):
        player = await get_player_record(game_pin, username)

    message = ChatMessage(
        sender=username,
        content=content,
        timestamp=datetime.now(),
        blocked=False,
    )
    await append_chat_message(game_pin, message)
    await sio.emit(
        "chat_message_received",
        {
            **message.model_dump(mode="json"),
            "sender_avatar_params": player.avatar_params if player is not None else None,
            "sender_is_admin": session.get("admin", False),
        },
        room=game_pin,
    )


@sio.event
async def get_question_results(sid: str, data: dict):
    session = await get_session(sid, sio)
    if not session["admin"]:
        return
    game_pin = session["game_pin"]
    answer_data_list = await AnswerDataList.get_redis_or_empty(game_pin, data["question_number"])
    game_data = await PlayGame.get_from_redis(game_pin)
    game_data.question_show = False
    await game_data.save(game_pin)
    await sio.emit("question_results", answer_data_list.model_dump(), room=game_pin)
    # Also emit anonymous answer summary for all players
    from collections import Counter
    answer_counts = Counter(ad.answer for ad in answer_data_list)
    total = len(answer_data_list)
    await sio.emit("answer_summary", {
        "total": total,
        "answers": {a: c for a, c in answer_counts.most_common()},
    }, room=game_pin)


@sio.event
async def set_question_number(sid: str, data: str):
    # data is just a number (as a str) of the question
    session = await get_session(sid, sio)
    if not session["admin"]:
        return
    game_pin = session["game_pin"]
    game_data = await PlayGame.get_from_redis(session["game_pin"])
    game_data.current_question = int(float(data))
    game_data.question_show = True
    await game_data.save(session["game_pin"])
    await redis.set(f"game:{session['game_pin']}:current_time", datetime.now().isoformat(), ex=7200)
    temp_return = game_data.model_dump(include={"questions"})["questions"][int(float(data))]
    if game_data.questions[int(float(data))].type == QuizQuestionType.SLIDE:
        await sio.emit(
            "set_question_number",
            {
                "question_index": int(float(data)),
                "question": {
                    **temp_return,
                    "type": game_data.questions[int(float(data))].type,
                },
            },
            room=game_pin,
        )
        return
    if game_data.questions[int(float(data))].type == QuizQuestionType.VOTING:
        for i in range(len(temp_return["answers"])):
            temp_return["answers"][i] = VotingQuizAnswer(**temp_return["answers"][i])
    temp_return["type"] = game_data.questions[int(float(data))].type
    if temp_return["type"] == QuizQuestionType.ORDER:
        random.shuffle(temp_return["answers"])
    await sio.emit(
        "set_question_number",
        {
            "question_index": int(float(data)),
            "question": ReturnQuestion(**temp_return).model_dump(),
        },
        room=game_pin,
    )


@sio.event
async def submit_answer(sid: str, data: dict):
    now = datetime.now()
    try:
        data = SubmitAnswerData(**data)
    except ValidationError as e:
        await sio.emit("error", room=sid)
        print(e)
        return
    data.answer = str(data.answer)
    session = await get_session(sid, sio)
    question_index = int(float(data.question_index))
    game_data = await PlayGame.get_from_redis(session["game_pin"])

    # --- Role-gated answering for tabletop mode ---
    if is_tabletop(game_data):
        current_q = game_data.questions[question_index]
        allowed_roles = get_allowed_roles(current_q)
        if allowed_roles is not None:
            player_role = await get_player_role(session["game_pin"], session["username"])
            if not check_player_role_allowed(player_role, allowed_roles):
                await sio.emit("role_not_allowed", {"allowed_roles": allowed_roles}, room=sid)
                return

    already_answered = await has_already_answered(session["game_pin"], question_index, session["username"])
    if already_answered:
        await sio.emit("already_replied", room=sid)
        return
    answer_right, answer = check_answer(game_data, data)
    latency = int(float(session.get("ping", 0)))
    time_q_started = datetime.fromisoformat(await redis.get(f"game:{session['game_pin']}:current_time"))
    diff = (time_q_started - now).total_seconds() * 1000  # - timedelta(milliseconds=latency)

    # --- Tabletop flat scoring vs speed-based ---
    if is_tabletop(game_data):
        score = TABLETOP_FLAT_SCORE if answer_right else 0
    else:
        score = 0
        if answer_right:
            score = calculate_score(
                abs(diff) - latency,
                int(float(game_data.questions[question_index].time)),
            )
            if score > 1000:
                score = 1000

    await redis.hincrby(f"game_session:{session['game_pin']}:player_scores", session["username"], score)
    answer_data = AnswerData(
        username=session["username"],
        answer=answer,
        right=answer_right,
        time_taken=abs(diff) - latency,
        score=score,
    )
    answers = await redis.get(f"game_session:{session['game_pin']}:{data.question_index}")
    answers = await set_answer(
        answers,
        game_pin=session["game_pin"],
        data=answer_data,
        q_index=int(float(data.question_index)),
    )

    # --- Eligible player count (role-aware for tabletop) ---
    if is_tabletop(game_data):
        current_q = game_data.questions[question_index]
        allowed_roles = get_allowed_roles(current_q)
        eligible_count = await get_eligible_player_count(session["game_pin"], allowed_roles)
    else:
        eligible_count = await redis.scard(f"game_session:{session['game_pin']}:players")

    await sio.emit("player_answer", {})
    if len(answers) >= eligible_count:
        game_data = await PlayGame.get_from_redis(session["game_pin"])
        game_data.question_show = False
        await game_data.save(session["game_pin"])
        await sio.emit("everyone_answered", {})


@sio.event
async def get_final_results(sid: str, _data: dict):
    session: dict = await get_session(sid, sio)
    if not session["admin"]:
        return
    game_data = await PlayGame.get_from_redis(session["game_pin"])
    results = await generate_final_results(game_data, session["game_pin"])
    avatar_map = await get_avatar_map(session["game_pin"])
    await sio.emit(
        "final_results",
        {
            "results": results,
            "avatar_map": avatar_map,
        },
        room=session["game_pin"],
    )


@sio.event
async def get_export_token(sid: str):
    session = await get_session(sid, sio)
    if not session["admin"]:
        return
    game_data = await PlayGame.get_from_redis(session["game_pin"])
    results = await generate_final_results(game_data, session["game_pin"])
    token = os.urandom(32).hex()
    await redis.set(f"export_token:{token}", json.dumps(results), ex=7200)
    await sio.emit("export_token", token, room=sid)


@sio.event
async def show_solutions(sid: str, _data: dict):
    session: dict = await get_session(sid, sio)
    game_data = await PlayGame.get_from_redis(session["game_pin"])
    if not session["admin"]:
        return
    await sio.emit(
        "solutions",
        game_data.questions[game_data.current_question].model_dump(),
        room=session["game_pin"],
    )


@sio.event
async def echo_time_sync(sid: str, data: str):
    then_dec = fernet.decrypt(data).decode("utf-8")
    then = datetime.fromisoformat(then_dec)
    now = datetime.now()
    delta = now - then
    session = await get_session(sid, sio)
    session["ping"] = delta.microseconds / 1000
    await save_session(sid, sio, session)


@sio.event
async def kick_player(sid: str, data: dict):
    try:
        data = KickPlayerInput(**data)
    except ValidationError as e:
        await sio.emit("error", room=sid)
        print(e)
        return

    session: dict = await get_session(sid, sio)
    if not session["admin"]:
        return

    player_sid = await redis.get(f"game_session:{session['game_pin']}:players:{data.username}")
    await remove_player_record(session["game_pin"], data.username)
    await redis.delete(f"game_session:{session['game_pin']}:players:{data.username}")
    await sio.leave_room(player_sid, session["game_pin"])
    await sio.emit("kick", room=player_sid)
    await emit_lobby_state(session["game_pin"])


class _RegisterAsRemoteInput(BaseModel):
    game_pin: str
    game_id: str


@sio.event
async def register_as_remote(sid: str, data: dict):
    try:
        data = _RegisterAsRemoteInput(**data)
    except ValidationError as e:
        await sio.emit("error", room=sid)
        print(e)
        return
    await sio.emit(
        "registered_as_admin",
        {"game_id": data.game_id, "game": await redis.get(f"game:{data.game_pin}")},
        room=sid,
    )
    await emit_socket_diagnostics_visibility(data.game_pin, room=sid)
    await sio.emit("control_visibility", {"visible": False}, room=f"admin:{data.game_pin}")
    session = await get_session(sid, sio)
    session["game_pin"] = data.game_pin
    session["admin"] = True
    session["remote"] = True
    await save_session(sid, sio, session)
    await sio.enter_room(sid, data.game_pin)
    await sio.enter_room(sid, f"admin:{data.game_pin}")


class _SetControlVisibilityInput(BaseModel):
    visible: bool


class _SetSocketDiagnosticsVisibilityInput(BaseModel):
    enabled: bool


@sio.event
async def set_control_visibility(sid: str, data: dict):
    try:
        data = _SetControlVisibilityInput(**data)
    except ValidationError as e:
        await sio.emit("error", room=sid)
        print(e)
        return
    session: dict = await get_session(sid, sio)
    await sio.emit(
        "control_visibility",
        {"visible": data.visible},
        room=f"admin:{session['game_pin']}",
    )


@sio.event
async def set_socket_diagnostics_visibility(sid: str, data: dict):
    try:
        data = _SetSocketDiagnosticsVisibilityInput(**data)
    except ValidationError as e:
        await sio.emit("error", room=sid)
        print(e)
        return
    session: dict = await get_session(sid, sio)
    if not session.get("admin", False):
        return
    game_pin = session["game_pin"]
    await redis.set(
        f"game:{game_pin}:socket_diagnostics_enabled",
        "1" if data.enabled else "0",
        ex=7200,
    )
    await emit_socket_diagnostics_visibility(game_pin)


@sio.event
async def save_quiz(sid: str):
    session: dict = await get_session(sid, sio)
    if not session["admin"]:
        return
    await save_quiz_to_storage(session["game_pin"])
    await sio.emit("results_saved_successfully")


@sio.event
async def connect(sid: str, _environ, _auth):
    session_id = os.urandom(16).hex()
    print("Connection opened with handler")
    sio_session = {"session_id": session_id}
    await sio.save_session(sid, sio_session)
    await sio.emit("session_id", ConnectSessionIdEvent(session_id=session_id).dict(), room=sid)


@sio.event
async def debug_status(sid: str):
    server_session = await sio.get_session(sid)
    custom_session = None
    game_summary = None
    players = []
    redis_session_key = None
    if server_session.get("session_id") is not None:
        redis_session_key = f"socket_io_session:{server_session['session_id']}"
        redis_session_data = await redis.get(redis_session_key)
        if redis_session_data is not None:
            custom_session = json.loads(redis_session_data)
    if custom_session and custom_session.get("game_pin"):
        game_pin = custom_session["game_pin"]
        players = await get_lobby_players(game_pin)
        game_data_raw = await redis.get(f"game:{game_pin}")
        if game_data_raw is not None:
            game_data = PlayGame.model_validate_json(game_data_raw)
            game_summary = {
                "game_pin": game_pin,
                "started": game_data.started,
                "current_question": game_data.current_question,
                "question_show": game_data.question_show,
                "question_count": len(game_data.questions),
            }
    await sio.emit(
        "debug_status",
        {
            "sid": sid,
            "time": datetime.now().isoformat(),
            "server_session": server_session,
            "redis_session_key": redis_session_key,
            "custom_session": custom_session,
            "game_summary": game_summary,
            "players": players,
        },
        room=sid,
    )


@sio.event
async def debug_echo(sid: str, data: dict | None = None):
    await sio.emit(
        "debug_echo",
        {
            "sid": sid,
            "time": datetime.now().isoformat(),
            "payload": data or {},
        },
        room=sid,
    )


# ============================================================
# Tabletop exercise events: role assignment, branching, overrides
# ============================================================


class _AssignRoleInput(BaseModel):
    username: str
    role: str


@sio.event
async def assign_role(sid: str, data: dict):
    """Admin assigns a role to a player. Works in lobby or during game."""
    try:
        data = _AssignRoleInput(**data)
    except ValidationError as e:
        await sio.emit("error", room=sid)
        print(e)
        return

    session = await get_session(sid, sio)
    if not session.get("admin", False):
        return

    game_pin = session["game_pin"]
    # Verify the player exists
    player = await get_player_record(game_pin, data.username)
    if player is None:
        await sio.emit("error", {"message": "player_not_found"}, room=sid)
        return

    await set_player_role(game_pin, data.username, data.role)
    roles = await get_all_player_roles(game_pin)
    await sio.emit("roles_updated", {"player_roles": roles}, room=game_pin)


class _BulkAssignRolesInput(BaseModel):
    assignments: dict[str, str]  # {username: role}


@sio.event
async def bulk_assign_roles(sid: str, data: dict):
    """Admin assigns roles to multiple players at once."""
    try:
        data = _BulkAssignRolesInput(**data)
    except ValidationError as e:
        await sio.emit("error", room=sid)
        print(e)
        return

    session = await get_session(sid, sio)
    if not session.get("admin", False):
        return

    game_pin = session["game_pin"]
    for username, role in data.assignments.items():
        await set_player_role(game_pin, username, role)

    roles = await get_all_player_roles(game_pin)
    await sio.emit("roles_updated", {"player_roles": roles}, room=game_pin)


class _RoleProposalInput(BaseModel):
    username: str
    role: str


@sio.event
async def propose_role(sid: str, data: dict):
    """Admin proposes a role to a player; they must accept before it's assigned."""
    try:
        data = _RoleProposalInput(**data)
    except ValidationError as e:
        await sio.emit("error", room=sid)
        print(e)
        return

    session = await get_session(sid, sio)
    if not session.get("admin", False):
        return

    game_pin = session["game_pin"]
    player = await get_player_record(game_pin, data.username)
    if player is None:
        await sio.emit("error", {"message": "player_not_found"}, room=sid)
        return

    # Find the player's SID by scanning session keys
    player_sid = await redis.get(f"game_session:{game_pin}:players:{data.username}")
    if not player_sid:
        # Fallback: broadcast to whole room (player handles if it's them)
        await sio.emit(
            "role_proposed",
            {"username": data.username, "role": data.role, "from_admin": True},
            room=game_pin,
        )
    else:
        await sio.emit(
            "role_proposed",
            {"username": data.username, "role": data.role, "from_admin": True},
            room=player_sid.decode() if isinstance(player_sid, bytes) else player_sid,
        )
    # Notify admin the proposal was sent
    await sio.emit("role_proposal_sent", {"username": data.username, "role": data.role}, room=sid)


class _RoleResponseInput(BaseModel):
    role: str
    accepted: bool


@sio.event
async def respond_to_role(sid: str, data: dict):
    """Player accepts or declines a proposed role."""
    try:
        data = _RoleResponseInput(**data)
    except ValidationError as e:
        await sio.emit("error", room=sid)
        print(e)
        return

    session = await get_session(sid, sio)
    username = session.get("username")
    game_pin = session.get("game_pin")
    if not username or not game_pin:
        return

    if data.accepted:
        await set_player_role(game_pin, username, data.role)
        roles = await get_all_player_roles(game_pin)
        await sio.emit("roles_updated", {"player_roles": roles}, room=game_pin)
        await sio.emit("role_accepted_ack", {"username": username, "role": data.role}, room=game_pin)
    else:
        await sio.emit("role_declined", {"username": username, "role": data.role}, room=game_pin)


class _ForceNextQuestionInput(BaseModel):
    question_id: str


@sio.event
async def force_next_question(sid: str, data: dict):
    """Admin overrides branching and forces a specific next question."""
    try:
        data = _ForceNextQuestionInput(**data)
    except ValidationError as e:
        await sio.emit("error", room=sid)
        print(e)
        return

    session = await get_session(sid, sio)
    if not session.get("admin", False):
        return

    game_pin = session["game_pin"]
    game_data = await PlayGame.get_from_redis(game_pin)

    result = find_question_by_id(game_data.questions, data.question_id)
    if result is None:
        await sio.emit("error", {"message": "question_not_found"}, room=sid)
        return

    target_index, _target_question = result

    # Log the override
    await log_facilitator_override(
        game_pin,
        game_data.current_question_id,
        data.question_id,
    )

    # Advance to the forced question
    game_data.current_question = target_index
    game_data.current_question_id = data.question_id
    game_data.question_show = True
    await game_data.save(game_pin)
    await redis.set(f"game:{game_pin}:current_time", datetime.now().isoformat(), ex=7200)

    await append_branch_path(game_pin, data.question_id)
    await emit_current_question(game_pin, game_data)


class _ResolveTieInput(BaseModel):
    answer_text: str


@sio.event
async def resolve_tie(sid: str, data: dict):
    """Admin breaks a tie by selecting the winning answer, then resolves branching."""
    try:
        data = _ResolveTieInput(**data)
    except ValidationError as e:
        await sio.emit("error", room=sid)
        print(e)
        return

    session = await get_session(sid, sio)
    if not session.get("admin", False):
        return

    game_pin = session["game_pin"]
    game_data = await PlayGame.get_from_redis(game_pin)
    current_q = game_data.questions[game_data.current_question]

    # Resolve the next question based on the admin-chosen answer
    next_q_id = resolve_next_question_id(current_q, data.answer_text)

    if next_q_id is None:
        # Scenario complete — no further questions
        branch_path = await get_branch_path(game_pin)
        await sio.emit(
            "scenario_complete",
            {"branch_path": branch_path, "winning_answer": data.answer_text},
            room=game_pin,
        )
        return

    result = find_question_by_id(game_data.questions, next_q_id)
    if result is None:
        await sio.emit("error", {"message": "branch_target_not_found"}, room=sid)
        return

    target_index, _target_question = result
    game_data.current_question = target_index
    game_data.current_question_id = next_q_id
    game_data.question_show = True
    await game_data.save(game_pin)
    await redis.set(f"game:{game_pin}:current_time", datetime.now().isoformat(), ex=7200)

    await append_branch_path(game_pin, next_q_id)
    await sio.emit(
        "branch_resolved",
        {"winning_answer": data.answer_text, "next_question_id": next_q_id},
        room=game_pin,
    )
    await emit_current_question(game_pin, game_data)


@sio.event
async def advance_tabletop(sid: str, _data: dict):
    """Admin advances to the next question using branching logic (majority vote).

    Called after everyone has answered or after showing solutions.
    Resolves the winning answer, determines the next question, and emits it.
    """
    session = await get_session(sid, sio)
    if not session.get("admin", False):
        return

    game_pin = session["game_pin"]
    game_data = await PlayGame.get_from_redis(game_pin)

    if not is_tabletop(game_data):
        return

    current_q = game_data.questions[game_data.current_question]
    q_index = game_data.current_question

    # Tally the votes for the current question
    answer_data_list = await AnswerDataList.get_redis_or_empty(game_pin, str(q_index))
    vote_tally = tally_votes(answer_data_list)

    winning_answer, is_tie = determine_winning_answer(vote_tally)

    if is_tie:
        # Notify admin of tie — they must call resolve_tie
        tied_answers = [
            answer for answer, count in vote_tally.most_common()
            if count == vote_tally.most_common()[0][1]
        ]
        await sio.emit(
            "tie_detected",
            {"tied_answers": tied_answers, "votes": dict(vote_tally)},
            room=f"admin:{game_pin}",
        )
        return

    # Resolve next question
    next_q_id = resolve_next_question_id(current_q, winning_answer)

    if next_q_id is None:
        # Scenario complete
        branch_path = await get_branch_path(game_pin)
        await sio.emit(
            "scenario_complete",
            {"branch_path": branch_path, "winning_answer": winning_answer},
            room=game_pin,
        )
        return

    result = find_question_by_id(game_data.questions, next_q_id)
    if result is None:
        # Branch target missing — treat as scenario complete
        branch_path = await get_branch_path(game_pin)
        await sio.emit(
            "scenario_complete",
            {"branch_path": branch_path, "winning_answer": winning_answer, "error": "branch_target_not_found"},
            room=game_pin,
        )
        return

    target_index, _target_question = result
    game_data.current_question = target_index
    game_data.current_question_id = next_q_id
    game_data.question_show = True
    await game_data.save(game_pin)
    await redis.set(f"game:{game_pin}:current_time", datetime.now().isoformat(), ex=7200)

    await append_branch_path(game_pin, next_q_id)
    await sio.emit(
        "branch_resolved",
        {"winning_answer": winning_answer, "next_question_id": next_q_id},
        room=game_pin,
    )
    await emit_current_question(game_pin, game_data)


@sio.event
async def get_tabletop_state(sid: str, _data: dict):
    """Admin requests current tabletop state (roles, branch path, etc.)."""
    session = await get_session(sid, sio)
    if not session.get("admin", False):
        return

    game_pin = session["game_pin"]
    roles = await get_all_player_roles(game_pin)
    branch_path = await get_branch_path(game_pin)
    overrides = await get_facilitator_overrides(game_pin)

    await sio.emit(
        "tabletop_state",
        {
            "roles": roles,
            "branch_path": branch_path,
            "facilitator_overrides": overrides,
        },
        room=sid,
    )


# ============================================================
# Inject system: push injects to players
# ============================================================


class _PushInjectInput(BaseModel):
    inject_id: str | None = None  # ID of a pre-defined inject
    title: str | None = None  # For ad-hoc injects
    content: str | None = None
    image: str | None = None
    severity: str = "info"


@sio.event
async def push_inject(sid: str, data: dict):
    """Admin pushes an inject to all players (pre-defined by ID or ad-hoc)."""
    try:
        data = _PushInjectInput(**data)
    except ValidationError as e:
        await sio.emit("error", room=sid)
        print(e)
        return

    session = await get_session(sid, sio)
    if not session.get("admin", False):
        return

    game_pin = session["game_pin"]
    game_data = await PlayGame.get_from_redis(game_pin)

    inject = None
    if data.inject_id and game_data.injects:
        # Find pre-defined inject by ID
        for inj in game_data.injects:
            if inj.id == data.inject_id:
                inject = inj
                break
    if inject is None:
        # Ad-hoc inject
        import uuid as _uuid
        inject = Inject(
            id=data.inject_id or str(_uuid.uuid4()),
            title=data.title or "Inject",
            content=data.content or "",
            image=data.image,
            severity=data.severity,
        )

    await log_inject(game_pin, inject, triggered_by="facilitator")
    await sio.emit("inject_received", inject.model_dump(), room=game_pin)


class _DismissInjectInput(BaseModel):
    inject_id: str


@sio.event
async def dismiss_inject(sid: str, data: dict):
    """Player acknowledges/dismisses an inject."""
    # No-op on server — purely client-side state management
    pass


# ============================================================
# Situation Room: shared incident status board
# ============================================================


class _UpdateSituationInput(BaseModel):
    severity: str | None = None  # green | amber | red | critical
    phase: str | None = None  # e.g. "Detection", "Containment", "Eradication", "Recovery"
    affected_systems: list[str] | None = None
    summary: str | None = None
    context_notes: str | None = None


@sio.event
async def update_situation(sid: str, data: dict):
    """Admin updates the situation room status board."""
    try:
        data = _UpdateSituationInput(**data)
    except ValidationError as e:
        await sio.emit("error", room=sid)
        print(e)
        return

    session = await get_session(sid, sio)
    if not session.get("admin", False):
        return

    game_pin = session["game_pin"]

    status = {
        "severity": data.severity,
        "phase": data.phase,
        "affected_systems": data.affected_systems,
        "summary": data.summary,
        "context_notes": data.context_notes,
    }
    await set_situation_status(game_pin, status)
    await log_situation_change(game_pin, status)
    await sio.emit("situation_updated", status, room=game_pin)


@sio.event
async def get_situation(sid: str, _data: dict):
    """Any participant requests the current situation status + inject history."""
    session = await get_session(sid, sio)
    game_pin = session.get("game_pin")
    if not game_pin:
        return

    status = await get_situation_status(game_pin)
    injects_log = await get_injects_log(game_pin)
    await sio.emit("situation_room_data", {
        "status": status or {},
        "injects_log": injects_log or [],
    }, room=sid)
