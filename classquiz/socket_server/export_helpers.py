# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


import json
from datetime import datetime

from pydantic import ValidationError

from classquiz.config import redis
from classquiz.db.models import PlayGame, GameResults
from classquiz.socket_server.branching import (
    is_tabletop,
    get_all_player_roles,
    get_branch_path,
    get_facilitator_overrides,
    get_injects_log,
    get_situation_log,
    get_file_downloads_log,
)


async def save_quiz_to_storage(game_pin: str):
    game = PlayGame.model_validate_json(await redis.get(f"game:{game_pin}"))
    player_count = await redis.scard(f"game_session:{game_pin}:players")
    answers = []
    for i in range(len(game.questions)):
        redis_res = await redis.get(f"game_session:{game_pin}:{i}")
        try:
            answers.append(json.loads(redis_res))
        except (ValidationError, TypeError):
            answers.append([])
    player_scores = await redis.hgetall(f"game_session:{game_pin}:player_scores")
    custom_field_data = await redis.hgetall(f"game:{game_pin}:players:custom_fields")
    q_return = []
    for q in game.questions:
        q_return.append(q.model_dump())

    # Tabletop exercise metadata
    player_roles = None
    branch_path = None
    facilitator_overrides_data = None
    injects_log_data = None
    situation_log_data = None
    file_downloads_log_data = None
    scenario_type = game.scenario_type

    if is_tabletop(game):
        player_roles = await get_all_player_roles(game_pin)
        branch_path = await get_branch_path(game_pin)
        facilitator_overrides_data = await get_facilitator_overrides(game_pin)
        injects_log_data = await get_injects_log(game_pin)
        situation_log_data = await get_situation_log(game_pin)
        file_downloads_log_data = await get_file_downloads_log(game_pin)

    data = GameResults(
        id=game.game_id,
        quiz=game.quiz_id,
        user=game.user_id,
        timestamp=datetime.now(),
        player_count=player_count,
        answers=json.dumps(answers),
        player_scores=json.dumps(player_scores),
        custom_field_data=json.dumps(custom_field_data),
        title=game.title,
        description=game.description,
        questions=json.dumps(q_return),
        player_roles=json.dumps(player_roles) if player_roles else None,
        branch_path=json.dumps(branch_path) if branch_path else None,
        facilitator_overrides=json.dumps(facilitator_overrides_data) if facilitator_overrides_data else None,
        scenario_type=scenario_type,
        injects_log=json.dumps(injects_log_data) if injects_log_data else None,
        situation_log=json.dumps(situation_log_data) if situation_log_data else None,
        file_downloads_log=json.dumps(file_downloads_log_data) if file_downloads_log_data else None,
    )
    await data.save()
