# SPDX-FileCopyrightText: 2025 CyberAsk
#
# SPDX-License-Identifier: MPL-2.0

from __future__ import annotations

from typing import Any

DEFAULT_COLORS = ["#D6EDC9", "#B07156", "#7F7057", "#4E6E58"]

STANDARD_ROLES = [
    "Incident Commander",
    "CISO",
    "SOC Lead",
    "IT Operations",
    "Legal & Compliance",
    "Communications Lead",
    "HR Director",
    "Business Continuity Manager",
]

MASTER_THEME = {
    "background_color": "#0f172a",
    "text_color": "#f8fafc",
    "accent_color": "#b07156",
    "background_image": None,
    "font_family": "Inter",
}


def base_quiz(
    *,
    title: str,
    description: str,
    questions: list[dict],
    injects: list[dict] | None = None,
    roles: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "public": False,
        "title": title,
        "description": description,
        "cover_image": None,
        "background_color": "#0f172a",
        "background_image": None,
        "scenario_type": "tabletop",
        "roles": roles or STANDARD_ROLES,
        "injects": injects or [],
        "master_theme": MASTER_THEME,
        "questions": questions,
    }


def info_q(
    id: str,
    title: str,
    body: str,
    *,
    next_id: str | None = None,
    notes: str | None = None,
    discussion: int = 120,
    objective: str = "Detection",
    time: str = "90",
) -> dict:
    return {
        "id": id,
        "question": title,
        "time": time,
        "type": "INFORMATION",
        "answers": "",
        "information_body": body,
        "image": None,
        "hide_results": True,
        "allowed_roles": None,
        "default_next_question_id": next_id,
        "decision_mode": "facilitator_only",
        "facilitator_notes": notes,
        "discussion_time": discussion,
        "category": "CONTENT",
        "file_attachments": None,
        "timer": {"enabled": False, "duration_seconds": None},
        "theme_override": None,
        "objective": objective,
        "sla_checkpoints": None,
    }


def file_q(
    id: str,
    title: str,
    body: str,
    filename: str,
    description: str,
    *,
    next_id: str | None = None,
    roles: list[str] | None = None,
    notes: str | None = None,
    discussion: int = 180,
) -> dict:
    return {
        "id": id,
        "question": title,
        "time": "120",
        "type": "FILE",
        "answers": "",
        "information_body": body,
        "image": None,
        "hide_results": True,
        "allowed_roles": roles or ["SOC Lead", "IT Operations"],
        "default_next_question_id": next_id,
        "decision_mode": "facilitator_only",
        "facilitator_notes": notes,
        "discussion_time": discussion,
        "category": "EVIDENCE",
        "file_attachments": [
            {
                "id": None,
                "filename": filename,
                "mime_type": "text/plain",
                "url": "https://raw.githubusercontent.com/github/gitignore/main/Global/GPG.gitignore",
                "description": description,
            }
        ],
        "timer": {"enabled": False, "duration_seconds": None},
        "theme_override": None,
        "objective": "Detection",
        "sla_checkpoints": None,
    }


def abcd_q(
    id: str,
    question: str,
    options: list[tuple[str, str | None]],
    *,
    default_next: str | None = None,
    roles: list[str] | None = None,
    notes: str | None = None,
    discussion: int = 240,
    objective: str = "Containment",
    time: str = "120",
    sla: list[dict] | None = None,
) -> dict:
    answers = []
    for i, (text, next_id) in enumerate(options):
        answers.append(
            {
                "right": i == 0,
                "answer": text,
                "color": DEFAULT_COLORS[i % len(DEFAULT_COLORS)],
                "next_question_id": next_id,
            }
        )
    return {
        "id": id,
        "question": question,
        "time": time,
        "type": "ABCD",
        "answers": answers,
        "image": None,
        "hide_results": False,
        "allowed_roles": roles,
        "default_next_question_id": default_next,
        "decision_mode": "majority_vote",
        "facilitator_notes": notes,
        "discussion_time": discussion,
        "category": "INTERACTIVE",
        "information_body": None,
        "file_attachments": None,
        "timer": {"enabled": True, "duration_seconds": 90},
        "theme_override": None,
        "objective": objective,
        "sla_checkpoints": sla,
    }


def voting_q(
    id: str,
    question: str,
    options: list[str],
    *,
    next_id: str | None = None,
    notes: str | None = None,
    discussion: int = 180,
) -> dict:
    answers = [
        {"answer": text, "image": None, "color": DEFAULT_COLORS[i % len(DEFAULT_COLORS)]}
        for i, text in enumerate(options)
    ]
    return {
        "id": id,
        "question": question,
        "time": "90",
        "type": "VOTING",
        "answers": answers,
        "image": None,
        "hide_results": True,
        "allowed_roles": None,
        "default_next_question_id": next_id,
        "decision_mode": "majority_vote",
        "facilitator_notes": notes,
        "discussion_time": discussion,
        "category": "INTERACTIVE",
        "information_body": None,
        "file_attachments": None,
        "timer": {"enabled": False, "duration_seconds": None},
        "theme_override": None,
        "objective": "Communication",
        "sla_checkpoints": None,
    }