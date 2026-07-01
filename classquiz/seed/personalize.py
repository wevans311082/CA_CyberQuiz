# SPDX-FileCopyrightText: 2025 CyberAsk
#
# SPDX-License-Identifier: MPL-2.0

from __future__ import annotations

import re
from typing import Any

from classquiz.seed.context import WizardContext

_PLACEHOLDER = re.compile(r"\{\{(\w+)\}\}")


def render_text(text: str, ctx: WizardContext) -> str:
    values = ctx.as_dict()

    def repl(match: re.Match[str]) -> str:
        key = match.group(1)
        return values.get(key, match.group(0))

    return _PLACEHOLDER.sub(repl, text)


def personalize_value(value: Any, ctx: WizardContext) -> Any:
    if isinstance(value, str):
        return render_text(value, ctx)
    if isinstance(value, list):
        return [personalize_value(item, ctx) for item in value]
    if isinstance(value, dict):
        return {k: personalize_value(v, ctx) for k, v in value.items()}
    return value


def personalize_quiz(quiz_data: dict, ctx: WizardContext) -> dict:
    return personalize_value(quiz_data, ctx)