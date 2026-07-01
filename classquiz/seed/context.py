# SPDX-FileCopyrightText: 2025 CyberAsk
#
# SPDX-License-Identifier: MPL-2.0

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date


@dataclass
class WizardContext:
    company_name: str = "Acme Financial Services"
    industry: str = "Financial Services"
    location: str = "London, United Kingdom"
    exercise_date: str = field(default_factory=lambda: date.today().strftime("%d %B %Y"))
    ceo_name: str = "Jane Morgan"
    ciso_name: str = "David Chen"
    employee_count: str = "2,400"
    primary_system: str = "customer banking portal"
    regulator: str = "ICO"
    region: str = "UK"
    domain: str = "acmefinancial.example"
    data_classification: str = "PCI and personal financial data"

    def as_dict(self) -> dict[str, str]:
        return {k: str(v) for k, v in asdict(self).items()}

    @classmethod
    def from_dict(cls, data: dict) -> WizardContext:
        known = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        return cls(**known)