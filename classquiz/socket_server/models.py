# SPDX-FileCopyrightText: 2025 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0

from pydantic import BaseModel, field_validator, ValidationInfo
from classquiz.db.models import QuizQuestion, QuizQuestionType, VotingQuizAnswer
from datetime import datetime


class AvatarParams(BaseModel):
    """Avatar customization parameters for game session players."""
    skin_color: int = 0
    hair_color: int = 0
    facial_hair_type: int = 0
    facial_hair_color: int = 0
    top_type: int = 0
    hat_color: int = 0
    mouth_type: int = 0
    eyebrow_type: int = 0
    nose_type: int = 0
    accessories_type: int = 0
    clothe_type: int = 0
    clothe_color: int = 0
    clothe_graphic_type: int = 0


class PlayerData(BaseModel):
    """Enriched player data emitted in lobby_state, joined_game, and player_joined events."""
    username: str
    avatar_params: AvatarParams | None = None
    sid: str | None = None


class ChatMessage(BaseModel):
    """Chat message structure for lobby community chat."""
    sender: str  # username
    content: str
    timestamp: datetime
    blocked: bool = False  # True if message was filtered by profanity check


class SendChatMessageData(BaseModel):
    content: str


class JoinGameData(BaseModel):
    username: str
    game_pin: str
    captcha: str | None = None
    custom_field: str | None = None
    avatar_params: AvatarParams | None = None


class RejoinGameData(BaseModel):
    old_sid: str
    game_pin: str
    username: str
    avatar_params: AvatarParams | None = None


class RegisterAsAdminData(BaseModel):
    game_pin: str
    game_id: str


class ABCDQuizAnswerWithoutSolution(BaseModel):
    answer: str
    color: str | None = None


class RangeQuizAnswerWithoutSolution(BaseModel):
    min: int
    max: int


class ReturnQuestion(QuizQuestion):
    answers: list[ABCDQuizAnswerWithoutSolution] | RangeQuizAnswerWithoutSolution | list[VotingQuizAnswer] | str
    type: QuizQuestionType = QuizQuestionType.ABCD

    @field_validator("answers")
    def answers_not_none_if_abcd_type(cls, v, info: ValidationInfo):
        if info.data["type"] == QuizQuestionType.ABCD and type(v[0]) is not ABCDQuizAnswerWithoutSolution:
            raise ValueError("Answers can't be none if type is ABCD")
        if info.data["type"] == QuizQuestionType.RANGE and type(v) is not RangeQuizAnswerWithoutSolution:
            raise ValueError("Answer must be from type RangeQuizAnswer if type is RANGE")
        # skipcq: PTC-W0047
        if info.data["type"] == QuizQuestionType.VOTING and type(v[0]) is not VotingQuizAnswer:
            pass
        if info.data["type"] == QuizQuestionType.SLIDE and type(v) is not str:
            raise ValueError("Answer must be from type str if type is SLIDE")
        if info.data["type"] == QuizQuestionType.INFORMATION and type(v) is not str:
            raise ValueError("Answer must be from type str if type is INFORMATION")
        if info.data["type"] == QuizQuestionType.FILE and type(v) is not str:
            raise ValueError("Answer must be from type str if type is FILE")
        return v


class SubmitAnswerDataOrderType(BaseModel):
    answer: str


class SubmitAnswerData(BaseModel):
    question_index: int
    answer: str | int
    complex_answer: list[SubmitAnswerDataOrderType] | None = None


class KickPlayerInput(BaseModel):
    username: str


class ConnectSessionIdEvent(BaseModel):
    session_id: str
