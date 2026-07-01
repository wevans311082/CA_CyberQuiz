# SPDX-FileCopyrightText: 2025 CyberAsk
#
# SPDX-License-Identifier: MPL-2.0

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from classquiz.seed.templates import data_leak, disaster_recovery, insider_threat, ransomware


@dataclass(frozen=True)
class SeedTemplateMeta:
    id: str
    name: str
    summary: str
    topic: str
    slide_count: int
    branch_count: int
    inject_count: int
    difficulty: str
    builder: Callable[[], dict]


TEMPLATES: dict[str, SeedTemplateMeta] = {
    "ransomware": SeedTemplateMeta(
        id="ransomware",
        name="Ransomware Response",
        summary="Detection through containment, extortion response, regulatory notification, and recovery.",
        topic="Ransomware",
        slide_count=15,
        branch_count=8,
        inject_count=4,
        difficulty="Advanced",
        builder=ransomware.build,
    ),
    "data_leak": SeedTemplateMeta(
        id="data_leak",
        name="State-Sponsored Data Leak",
        summary="APT exfiltration, legal preservation, dark web exposure, and long-term remediation.",
        topic="Data Breach / APT",
        slide_count=14,
        branch_count=7,
        inject_count=3,
        difficulty="Advanced",
        builder=data_leak.build,
    ),
    "insider_threat": SeedTemplateMeta(
        id="insider_threat",
        name="Insider Threat",
        summary="HR-security coordination, evidence preservation, investigation, and IP recovery.",
        topic="Insider Threat",
        slide_count=14,
        branch_count=7,
        inject_count=3,
        difficulty="Intermediate",
        builder=insider_threat.build,
    ),
    "disaster_recovery": SeedTemplateMeta(
        id="disaster_recovery",
        name="Full Disaster Recovery",
        summary="Datacenter failure, BCP activation, failover, vendor escalation, and validation.",
        topic="Business Continuity / DR",
        slide_count=14,
        branch_count=7,
        inject_count=3,
        difficulty="Intermediate",
        builder=disaster_recovery.build,
    ),
}


def list_templates() -> list[SeedTemplateMeta]:
    return list(TEMPLATES.values())


def get_template(template_id: str) -> SeedTemplateMeta:
    if template_id not in TEMPLATES:
        known = ", ".join(sorted(TEMPLATES))
        raise KeyError(f"Unknown template '{template_id}'. Available: {known}")
    return TEMPLATES[template_id]