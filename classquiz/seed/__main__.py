# SPDX-FileCopyrightText: 2025 CyberAsk
#
# SPDX-License-Identifier: MPL-2.0

from __future__ import annotations

import argparse
import asyncio
import sys

from classquiz.db import database
from classquiz.db.models import User
from classquiz.seed.context import WizardContext
from classquiz.seed.registry import list_templates
from classquiz.seed.service import create_seed_quiz, seed_all_templates


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Seed CyberAsk with premade tabletop exercise templates."
    )
    parser.add_argument("--list", action="store_true", help="List available templates and exit")
    parser.add_argument("--template", "-t", help="Template id (ransomware, data_leak, insider_threat, disaster_recovery)")
    parser.add_argument("--all", action="store_true", help="Create all templates")
    parser.add_argument("--user-email", required=False, help="Admin user email to own created quizzes")
    parser.add_argument("--company", default=None, help="Company name")
    parser.add_argument("--industry", default=None, help="Industry")
    parser.add_argument("--location", default=None, help="HQ location")
    parser.add_argument("--ceo", default=None, help="CEO name")
    parser.add_argument("--ciso", default=None, help="CISO name")
    parser.add_argument("--regulator", default=None, help="Regulator name")
    parser.add_argument("--domain", default=None, help="Company domain")
    return parser


def _context_from_args(args: argparse.Namespace) -> WizardContext:
    data = {}
    if args.company:
        data["company_name"] = args.company
    if args.industry:
        data["industry"] = args.industry
    if args.location:
        data["location"] = args.location
    if args.ceo:
        data["ceo_name"] = args.ceo
    if args.ciso:
        data["ciso_name"] = args.ciso
    if args.regulator:
        data["regulator"] = args.regulator
    if args.domain:
        data["domain"] = args.domain
    return WizardContext.from_dict(data)


async def _main_async(args: argparse.Namespace) -> int:
    if args.list:
        for template in list_templates():
            print(
                f"{template.id:20} {template.slide_count:2} slides  "
                f"{template.branch_count} branches  {template.inject_count} injects  — {template.name}"
            )
        return 0

    if not args.user_email:
        print("error: --user-email is required unless using --list", file=sys.stderr)
        return 2

    if not args.all and not args.template:
        print("error: specify --template <id> or --all (or use --list)", file=sys.stderr)
        return 2

    if not database.is_connected:
        await database.connect()

    user = await User.objects.get_or_none(email=args.user_email)
    if user is None:
        print(f"error: user not found: {args.user_email}", file=sys.stderr)
        return 1

    ctx = _context_from_args(args)

    if args.all:
        quizzes = await seed_all_templates(ctx, user)
        for quiz in quizzes:
            print(f"created {quiz.id}  {quiz.title}")
        print(f"done — {len(quizzes)} exercises created for {user.email}")
        return 0

    quiz = await create_seed_quiz(args.template, ctx, user)
    print(f"created {quiz.id}")
    print(f"title: {quiz.title}")
    print(f"questions: {len(quiz.questions)}")
    print(f"edit: /edit?quiz_id={quiz.id}")
    return 0


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    raise SystemExit(asyncio.run(_main_async(args)))


if __name__ == "__main__":
    main()