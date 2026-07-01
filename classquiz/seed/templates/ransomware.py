# SPDX-FileCopyrightText: 2025 CyberAsk
#
# SPDX-License-Identifier: MPL-2.0

from classquiz.seed.builders import abcd_q, base_quiz, file_q, info_q, voting_q


def build() -> dict:
    injects = [
        {
            "id": "rw-inj-1",
            "title": "EDR alert — Cobalt Strike beacon",
            "content": "**SOC:** EDR flagged a Cobalt Strike beacon on `fin-app-07.{{domain}}`. Process tree shows `powershell.exe` spawning from an Excel macro.",
            "severity": "warning",
            "trigger_after_question_id": "rw-detection",
        },
        {
            "id": "rw-inj-2",
            "title": "Ransom note on file servers",
            "content": "**Operations:** Multiple file servers display `README-RECOVER.txt`. Threat actor claims 1.2 TB exfiltrated and demands payment within 24 hours.",
            "severity": "critical",
            "trigger_after_question_id": "rw-d1-contain",
        },
        {
            "id": "rw-inj-3",
            "title": "Media inquiry",
            "content": "**Comms:** A national journalist emailed {{ceo_name}} asking whether {{company_name}} is experiencing a ransomware incident. Response requested within 60 minutes.",
            "severity": "warning",
            "trigger_after_question_id": "rw-comms",
        },
        {
            "id": "rw-inj-4",
            "title": "{{regulator}} notification deadline",
            "content": "**Legal:** {{regulator}} guidance requires initial breach notification within 72 hours if personal data is affected. Clock started at first awareness.",
            "severity": "warning",
            "trigger_after_question_id": "rw-regulatory",
        },
    ]

    questions = [
        info_q(
            "rw-brief",
            "Exercise Briefing — Ransomware Response",
            "<p><strong>Facilitator:</strong> Welcome to the {{company_name}} ransomware tabletop.</p>"
            "<p><strong>Date:</strong> {{exercise_date}} · <strong>Industry:</strong> {{industry}}</p>"
            "<p>Players will move through detection, containment, ransom decision, regulatory response, and recovery.</p>",
            next_id="rw-context",
            notes="Assign roles. Confirm speaking order. Remind players decisions branch the scenario.",
            discussion=180,
        ),
        info_q(
            "rw-context",
            "Organisation & Threat Context",
            "<p><strong>{{company_name}}</strong> employs {{employee_count}} staff in {{location}}.</p>"
            "<p>Critical system: <strong>{{primary_system}}</strong>. Data handled includes {{data_classification}}.</p>"
            "<p>Threat intelligence indicates active ransomware campaigns targeting {{industry}} firms in {{region}}.</p>",
            next_id="rw-detection",
            objective="Detection",
        ),
        info_q(
            "rw-detection",
            "Initial Detection — 06:14",
            "<p>SOC Lead reports anomalous outbound traffic from a finance workstation to an unknown VPS.</p>"
            "<p>Simultaneously, helpdesk receives three user reports of encrypted files on shared drives.</p>"
            "<p><em>Facilitator: push inject after this slide if desired.</em></p>",
            next_id="rw-evidence",
            notes="Pause for role introductions. Ask SOC Lead to summarise indicators.",
            discussion=150,
        ),
        file_q(
            "rw-evidence",
            "Evidence Review — SIEM & Email Headers",
            "<p>Review the attached artefacts. Identify likely initial access and lateral movement paths.</p>",
            filename="siem-ransomware-indicators.txt",
            description="Synthetic SIEM export: macro execution, SMB lateral movement, and C2 callbacks.",
            next_id="rw-d1-contain",
            notes="SOC Lead and IT Operations lead discussion. Cite specific log lines.",
            discussion=240,
        ),
        abcd_q(
            "rw-d1-contain",
            "Decision 1 — Immediate containment strategy",
            "What is your first containment action?",
            [
                ("Isolate affected endpoints and block known C2 at the perimeter", "rw-d2-isolate"),
                ("Segment finance VLAN only; keep other business units online", "rw-d2-segment"),
                ("Continue monitoring to preserve forensic evidence", "rw-d2-monitor"),
                ("Maintain business operations; investigate after market close", "rw-d2-crisis"),
            ],
            roles=["Incident Commander", "CISO", "IT Operations"],
            notes="Majority vote determines branch. No option is fully 'correct' — discuss trade-offs.",
            objective="Containment",
            sla=[
                {
                    "deadline_seconds": 300,
                    "bonus_points": 40,
                    "penalty_points": 20,
                    "description": "Containment decision within 5 minutes",
                }
            ],
        ),
        abcd_q(
            "rw-d2-isolate",
            "Branch — Aggressive isolation path",
            "Endpoints are isolated. Several production batch jobs have stopped. Next step?",
            [
                ("Expand isolation to all finance subnets pending scope confirmation", "rw-comms"),
                ("Restore critical batch jobs on isolated hosts to meet SLA", "rw-d2-crisis"),
                ("Deploy emergency read-only mode for customer portal", "rw-comms"),
                ("Begin ransom negotiation preparation in parallel", "rw-comms"),
            ],
            default_next="rw-comms",
            roles=["Incident Commander", "IT Operations"],
            objective="Containment",
        ),
        abcd_q(
            "rw-d2-segment",
            "Branch — Surgical segmentation path",
            "Finance VLAN is segmented. Monitoring shows spread attempts to HR file shares.",
            [
                ("Extend segmentation to HR and block east-west SMB", "rw-comms"),
                ("Rollback segmentation to restore payroll processing", "rw-d2-crisis"),
                ("Request threat-hunting team before further network changes", "rw-comms"),
                ("Issue company-wide password reset immediately", "rw-comms"),
            ],
            default_next="rw-comms",
            roles=["SOC Lead", "IT Operations"],
        ),
        abcd_q(
            "rw-d2-monitor",
            "Branch — Monitor-first path",
            "Threat actor activity continues. DLP flags 400 GB archive upload to external storage.",
            [
                ("Escalate to full isolation immediately", "rw-d2-isolate"),
                ("Block egress to the external storage provider only", "rw-comms"),
                ("Engage external IR firm before taking action", "rw-comms"),
                ("Continue monitoring until encryption events confirm scope", "rw-d2-crisis"),
            ],
            default_next="rw-comms",
            roles=["SOC Lead", "CISO"],
        ),
        abcd_q(
            "rw-d2-crisis",
            "Branch — Business continuity pressure",
            "{{ceo_name}} demands minimal disruption. Encryption is spreading.",
            [
                ("Declare major incident and invoke crisis management team", "rw-comms"),
                ("Pay ransom to restore operations quickly", "rw-comms"),
                ("Fail over to offline backups and accept 48h outage", "rw-comms"),
                ("Defer decision until legal review completes", "rw-comms"),
            ],
            default_next="rw-comms",
            roles=["Incident Commander", "CISO", "Business Continuity Manager"],
            objective="Communication",
        ),
        abcd_q(
            "rw-comms",
            "Decision 2 — Ransom payment & extortion response",
            "Threat actor provides proof-of-steal sample and payment wallet. How do you respond?",
            [
                ("Refuse payment; rebuild from backups and notify stakeholders", "rw-regulatory"),
                ("Pay ransom via insurance broker; pursue decryption key", "rw-regulatory"),
                ("Engage law enforcement and withhold public comment", "rw-regulatory"),
                ("Negotiate for time while accelerating recovery", "rw-regulatory"),
            ],
            roles=["Incident Commander", "CISO", "Legal & Compliance"],
            notes="Push media inject. Discuss OFAC, insurance, and moral hazard.",
            objective="Communication",
        ),
        abcd_q(
            "rw-regulatory",
            "Decision 3 — Regulatory & customer notification",
            "Legal confirms personal data likely affected. What is your notification sequence?",
            [
                ("Notify {{regulator}} within 72 hours; customer notice after scope validation", "rw-recovery"),
                ("Issue customer notice immediately; file regulator report next business day", "rw-recovery"),
                ("Notify {{regulator}} and customers simultaneously within 24 hours", "rw-recovery"),
                ("Delay all external notices until forensic report is final", "rw-recovery"),
            ],
            roles=["Legal & Compliance", "Communications Lead"],
            objective="Communication",
        ),
        abcd_q(
            "rw-recovery",
            "Decision 4 — Recovery prioritisation",
            "Which system cluster do you restore first?",
            [
                ("{{primary_system}} — customer-facing services", "rw-vote"),
                ("Core banking back-office and payment switches", "rw-vote"),
                ("Email and collaboration (restore internal comms)", "rw-vote"),
                ("Forensic evidence preservation environment", "rw-vote"),
            ],
            default_next="rw-vote",
            roles=["IT Operations", "Business Continuity Manager"],
            objective="Recovery",
        ),
        voting_q(
            "rw-vote",
            "Stakeholder communications priority",
            "Rank your immediate external communication channels by priority:",
            [
                "Customers via status page",
                "Regulators and authorities",
                "Media holding statement",
                "Staff all-hands briefing",
            ],
            next_id="rw-lessons",
            notes="Use vote results to drive comms lead actions.",
        ),
        info_q(
            "rw-lessons",
            "Lessons Learned — Hot Wash",
            "<p>Capture: what worked, gaps in detection, backup integrity, and decision latency.</p>"
            "<p>Assign owners for 30/60/90-day remediation actions.</p>",
            next_id="rw-close",
            objective="Recovery",
            discussion=300,
        ),
        info_q(
            "rw-close",
            "Exercise Debrief",
            "<p>Thank you for participating in the {{company_name}} ransomware exercise.</p>"
            "<p>Facilitator: summarise branch path taken and key decisions.</p>",
            notes="End exercise. Offer to export timeline and scores.",
            discussion=120,
        ),
    ]

    return base_quiz(
        title="{{company_name}} — Ransomware Response Tabletop",
        description="Branching ransomware exercise for {{industry}} organisations. Covers detection, containment, extortion, regulatory notification, and recovery.",
        questions=questions,
        injects=injects,
    )