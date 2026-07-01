# SPDX-FileCopyrightText: 2025 CyberAsk
#
# SPDX-License-Identifier: MPL-2.0

from classquiz.seed.builders import abcd_q, base_quiz, file_q, info_q, voting_q


def build() -> dict:
    injects = [
        {
            "id": "it-inj-1",
            "title": "HR flag — departing employee",
            "content": "**HR:** Senior developer submitted resignation effective Friday. DLP shows 12 GB upload to personal cloud storage.",
            "severity": "warning",
            "trigger_after_question_id": "it-discovery",
        },
        {
            "id": "it-inj-2",
            "title": "Source code repository access",
            "content": "**SOC:** User cloned three proprietary repositories after hours. Commits include obfuscated data exfiltration script.",
            "severity": "critical",
            "trigger_after_question_id": "it-d1-response",
        },
        {
            "id": "it-inj-3",
            "title": "Legal counsel advice",
            "content": "**Legal:** Employment solicitor advises caution on interview timing until evidence preservation is complete.",
            "severity": "info",
            "trigger_after_question_id": "it-d4-investigate",
        },
    ]

    questions = [
        info_q(
            "it-brief",
            "Exercise Briefing — Insider Threat",
            "<p><strong>{{company_name}}</strong> insider threat tabletop — {{exercise_date}}.</p>"
            "<p>Balance employee rights, evidence preservation, and business continuity.</p>",
            next_id="it-context",
            discussion=180,
        ),
        info_q(
            "it-context",
            "Insider Risk Context",
            "<p>{{employee_count}} employees across {{location}}. IP assets include {{primary_system}} source code and {{data_classification}}.</p>"
            "<p>{{ciso_name}} reports elevated insider risk score for engineering teams post-restructuring.</p>",
            next_id="it-discovery",
        ),
        info_q(
            "it-discovery",
            "Discovery — HR & DLP Correlation",
            "<p>HR Director flags a senior engineer resigning to join a competitor.</p>"
            "<p>DLP alerts correlate with large uploads and USB device insertion on their workstation.</p>",
            next_id="it-evidence",
        ),
        file_q(
            "it-evidence",
            "Evidence Review — User Activity Report",
            "<p>Review the user activity summary. Identify policy violations and data categories accessed.</p>",
            filename="insider-activity-report.txt",
            description="Synthetic UEBA export: after-hours access, USB events, and cloud uploads.",
            next_id="it-d1-response",
            roles=["SOC Lead", "HR Director"],
            discussion=240,
        ),
        abcd_q(
            "it-d1-response",
            "Decision 1 — Initial response lead",
            "Who leads the first 60 minutes?",
            [
                ("Security team with HR observer", "it-d2-preserve"),
                ("HR with security advisor", "it-d2-preserve"),
                ("Legal-led with joint security/HR", "it-d2-preserve"),
                ("Line manager confronts employee directly", "it-d4-investigate"),
            ],
            roles=["Incident Commander", "HR Director", "CISO"],
            objective="Detection",
        ),
        abcd_q(
            "it-d2-preserve",
            "Decision 2 — Evidence preservation",
            "How do you preserve evidence on the suspect device?",
            [
                ("Forensic image laptop; replace with clean device", "it-d3-access"),
                ("Remote wipe to prevent further exfiltration", "it-d6-comms"),
                ("Collect logs only; leave device in place", "it-d4-investigate"),
                ("Seize device; suspend employee immediately", "it-d3-access"),
            ],
            roles=["SOC Lead", "IT Operations", "Legal & Compliance"],
            objective="Containment",
        ),
        abcd_q(
            "it-d3-access",
            "Decision 3 — Access revocation scope",
            "What access do you revoke?",
            [
                ("All accounts, badges, and VPN immediately", "it-d4-investigate"),
                ("Application access only; keep email for monitoring", "it-d4-investigate"),
                ("Staged revocation after legal review", "it-d5-legal"),
                ("Revoke production access; retain dev environment", "it-d4-investigate"),
            ],
            roles=["IT Operations", "HR Director"],
            objective="Containment",
        ),
        abcd_q(
            "it-d4-investigate",
            "Decision 4 — Investigation approach",
            "How do you proceed with the employee?",
            [
                ("Formal HR interview with legal present", "it-d5-legal"),
                ("Silent monitoring while gathering evidence", "it-d5-legal"),
                ("Immediate suspension pending investigation", "it-d6-comms"),
                ("Allow employee to work notice period with enhanced monitoring", "it-d6-comms"),
            ],
            roles=["HR Director", "Legal & Compliance"],
            objective="Detection",
        ),
        abcd_q(
            "it-d5-legal",
            "Decision 5 — Law enforcement engagement",
            "Forensics confirms trade secret theft. Next step?",
            [
                ("Report to law enforcement and preserve chain of custody", "it-d6-comms"),
                ("Handle internally with civil litigation threat", "it-d6-comms"),
                ("Negotiate settlement with employee", "it-vote"),
                ("Delay report until competitor link is proven", "it-d6-comms"),
            ],
            roles=["Legal & Compliance", "CISO"],
        ),
        abcd_q(
            "it-d6-comms",
            "Decision 6 — Internal communications",
            "Rumours spread on internal chat. What do you communicate?",
            [
                ("All-staff note: security investigation underway, no speculation", "it-vote"),
                ("Targeted message to engineering team only", "it-v7-recovery"),
                ("No communication until investigation concludes", "it-vote"),
                ("Transparent town hall with {{ceo_name}}", "it-vote"),
            ],
            roles=["Communications Lead", "HR Director"],
            objective="Communication",
        ),
        voting_q(
            "it-vote",
            "Disciplinary & employment outcome",
            "What is the most appropriate initial employment action?",
            [
                "Immediate termination for gross misconduct",
                "Suspension on full pay pending investigation",
                "Garden leave until notice period ends",
                "Remain in role with enhanced monitoring",
            ],
            next_id="it-d7-recovery",
            notes="HR Director facilitates. Legal advises on local employment law.",
        ),
        abcd_q(
            "it-d7-recovery",
            "Decision 7 — Data & IP recovery",
            "How do you assess data integrity and IP loss?",
            [
                ("Full code repo diff and secret rotation programme", "it-lessons"),
                ("Customer impact assessment for {{primary_system}}", "it-lessons"),
                ("Third-party IP audit of competitor hiring", "it-lessons"),
                ("Defer recovery until legal case filed", "it-lessons"),
            ],
            default_next="it-lessons",
            roles=["IT Operations", "CISO"],
            objective="Recovery",
        ),
        info_q(
            "it-lessons",
            "Lessons Learned",
            "<p>Review insider threat controls: offboarding, DLP tuning, and HR-security liaison.</p>",
            next_id="it-close",
            discussion=300,
        ),
        info_q(
            "it-close",
            "Exercise Close",
            "<p>{{company_name}} insider threat tabletop complete.</p>",
        ),
    ]

    return base_quiz(
        title="{{company_name}} — Insider Threat Tabletop",
        description="Insider threat exercise covering HR-security coordination, evidence preservation, legal response, and recovery.",
        questions=questions,
        injects=injects,
    )