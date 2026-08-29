# SPDX-FileCopyrightText: 2025 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0

from pydantic import BaseModel, Field, field_validator, ValidationInfo
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
    username: str = Field(min_length=1, max_length=64)
    game_pin: str = Field(min_length=4, max_length=12)
    captcha: str | None = None
    custom_field: str | None = Field(default=None, max_length=256)
    avatar_params: AvatarParams | None = None


class RejoinGameData(BaseModel):
    old_sid: str = Field(min_length=1, max_length=256)
    game_pin: str = Field(min_length=4, max_length=12)
    username: str = Field(min_length=1, max_length=64)
    avatar_params: AvatarParams | None = None


class RegisterAsAdminData(BaseModel):
    game_pin: str
    game_id: str
    host_token: str


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
        question_type = info.data.get("type")
        if question_type == QuizQuestionType.ABCD and (
            not isinstance(v, list) or not v or not all(isinstance(item, ABCDQuizAnswerWithoutSolution) for item in v)
        ):
            raise ValueError("Answers must contain ABCD answers")
        if question_type == QuizQuestionType.RANGE and not isinstance(v, RangeQuizAnswerWithoutSolution):
            raise ValueError("Answer must be from type RangeQuizAnswer if type is RANGE")
        if question_type == QuizQuestionType.VOTING and (
            not isinstance(v, list) or not v or not all(isinstance(item, VotingQuizAnswer) for item in v)
        ):
            raise ValueError("Answers must contain voting answers")
        if question_type in {QuizQuestionType.SLIDE, QuizQuestionType.INFORMATION, QuizQuestionType.FILE} and not isinstance(v, str):
            raise ValueError("Answer must be from type str if type is SLIDE")
        return v


class SubmitAnswerDataOrderType(BaseModel):
    answer: str = Field(min_length=1, max_length=512)


class SubmitAnswerData(BaseModel):
    question_index: int = Field(ge=0)
    answer: str | int = Field(max_length=4096)
    complex_answer: list[SubmitAnswerDataOrderType] | None = Field(default=None, max_length=100)
    confidence: int | None = None  # 1 (low) | 2 (medium) | 3 (high) — tabletop only


class KickPlayerInput(BaseModel):
    username: str


class ConnectSessionIdEvent(BaseModel):
    session_id: str
