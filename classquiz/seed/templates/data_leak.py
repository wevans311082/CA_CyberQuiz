# SPDX-FileCopyrightText: 2025 CyberAsk
#
# SPDX-License-Identifier: MPL-2.0

from classquiz.seed.builders import abcd_q, base_quiz, file_q, info_q, voting_q


def build() -> dict:
    injects = [
        {
            "id": "dl-inj-1",
            "title": "Threat intel — APT41 TTP match",
            "content": "**Intel:** Industry ISAC published an advisory matching TTPs observed in your environment: long-dwell exfiltration via DNS tunneling.",
            "severity": "warning",
            "trigger_after_question_id": "dl-discovery",
        },
        {
            "id": "dl-inj-2",
            "title": "Dark web sample posted",
            "content": "**SOC:** External monitoring found a 2 GB sample labelled '{{company_name}} customer DB' on a criminal forum.",
            "severity": "critical",
            "trigger_after_question_id": "dl-d1-scope",
        },
        {
            "id": "dl-inj-3",
            "title": "Government agency inquiry",
            "content": "**Legal:** National cyber security agency requests urgent call regarding state-sponsored activity targeting {{industry}} firms in {{region}}.",
            "severity": "warning",
            "trigger_after_question_id": "dl-d3-notify",
        },
    ]

    questions = [
        info_q(
            "dl-brief",
            "Exercise Briefing — State-Sponsored Data Exfiltration",
            "<p><strong>Scenario:</strong> {{company_name}} suspects a long-running advanced persistent threat exfiltrating sensitive data.</p>"
            "<p><strong>Date:</strong> {{exercise_date}}</p>",
            next_id="dl-context",
            notes="Emphasise intelligence-sharing and legal constraints.",
            discussion=180,
        ),
        info_q(
            "dl-context",
            "Threat Actor & Data Landscape",
            "<p>{{company_name}} stores {{data_classification}} across hybrid cloud and on-prem systems.</p>"
            "<p>Recent intelligence suggests nation-state interest in {{industry}} targets in {{location}}.</p>"
            "<p>{{ciso_name}} has elevated threat level to <strong>high</strong>.</p>",
            next_id="dl-discovery",
        ),
        info_q(
            "dl-discovery",
            "Discovery — DLP & UEBA Alerts",
            "<p>DLP flagged repeated large transfers from a database admin account to an unknown S3-compatible bucket.</p>"
            "<p>UEBA shows the account active at 03:00 local time for 14 consecutive nights.</p>",
            next_id="dl-evidence",
            discussion=150,
        ),
        file_q(
            "dl-evidence",
            "Evidence Review — Exfiltration Timeline",
            "<p>Analyse the attached exfiltration log summary. Determine dwell time and data categories affected.</p>",
            filename="exfil-timeline-summary.txt",
            description="Synthetic log: database queries, compressed archives, and egress volumes by night.",
            next_id="dl-d1-scope",
            discussion=240,
        ),
        abcd_q(
            "dl-d1-scope",
            "Decision 1 — Confirm breach scope",
            "How do you validate the scope of exfiltration?",
            [
                ("Full forensic imaging of database and app servers", "dl-d2a-legal"),
                ("Query audit logs only; avoid tipping off the attacker", "dl-d2b-forensics"),
                ("Engage external IR with threat-hunting retainer", "dl-d2a-legal"),
                ("Assume worst case and begin notification planning", "dl-d3-notify"),
            ],
            roles=["CISO", "SOC Lead"],
            objective="Detection",
        ),
        abcd_q(
            "dl-d2a-legal",
            "Branch — Legal hold & preservation",
            "Forensics confirms 800 GB exported. Legal requests preservation strategy.",
            [
                ("Issue litigation hold and snapshot all relevant systems", "dl-d3-notify"),
                ("Preserve logs only; keep production systems running", "dl-d2b-forensics"),
                ("Isolate suspect admin account and rotate all DB credentials", "dl-d3-notify"),
                ("Delay preservation until board approval", "dl-d2b-forensics"),
            ],
            default_next="dl-d3-notify",
            roles=["Legal & Compliance", "IT Operations"],
        ),
        abcd_q(
            "dl-d2b-forensics",
            "Branch — Covert investigation",
            "You are conducting a covert investigation. Attacker changes C2 domain.",
            [
                ("Continue covert monitoring with law enforcement liaison", "dl-d3-notify"),
                ("Cut external access immediately", "dl-d4-contain"),
                ("Confront the suspected insider administrator", "dl-d6-remediation"),
                ("Publicly disclose to force attacker retreat", "dl-d5-pr"),
            ],
            default_next="dl-d3-notify",
            roles=["SOC Lead", "CISO"],
        ),
        abcd_q(
            "dl-d3-notify",
            "Decision 2 — Notification sequencing",
            "Who do you notify first?",
            [
                ("{{regulator}} and national cyber agency", "dl-d4-contain"),
                ("Affected customers with preliminary facts", "dl-d5-pr"),
                ("Board and executive leadership only", "dl-d4-contain"),
                ("Law enforcement before any external party", "dl-d4-contain"),
            ],
            roles=["Legal & Compliance", "Communications Lead"],
            objective="Communication",
        ),
        abcd_q(
            "dl-d4-contain",
            "Decision 3 — Containment & access cutover",
            "How do you contain the threat?",
            [
                ("Block all outbound non-corporate traffic at the perimeter", "dl-d5-pr"),
                ("Revoke all privileged access; enforce PAM checkout", "dl-d5-pr"),
                ("Rebuild identity provider from known-good backup", "dl-d6-remediation"),
                ("Maintain access to observe attacker for attribution", "dl-d5-pr"),
            ],
            roles=["Incident Commander", "IT Operations"],
            objective="Containment",
        ),
        abcd_q(
            "dl-d5-pr",
            "Decision 4 — Public & media strategy",
            "A journalist publishes a story citing the dark web sample. Response?",
            [
                ("Issue holding statement acknowledging investigation", "dl-vote"),
                ("No comment until forensic scope is confirmed", "dl-vote"),
                ("Proactive customer email with credit monitoring offer", "dl-vote"),
                ("CEO video message within 4 hours", "dl-vote"),
            ],
            roles=["Communications Lead", "CEO liaison via Incident Commander"],
            objective="Communication",
        ),
        voting_q(
            "dl-vote",
            "Data recovery & notification priority",
            "Which data category requires the fastest customer notification?",
            [
                "Authentication credentials",
                "Financial transaction history",
                "Personal identity documents",
                "Internal employee records",
            ],
            next_id="dl-d6-remediation",
        ),
        abcd_q(
            "dl-d6-remediation",
            "Decision 5 — Long-term remediation",
            "Select the primary 90-day remediation investment:",
            [
                ("Zero-trust network segmentation programme", "dl-lessons"),
                ("Database activity monitoring and query analytics", "dl-lessons"),
                ("Supply chain security review of managed service providers", "dl-lessons"),
                ("Enhanced insider threat programme with HR integration", "dl-lessons"),
            ],
            default_next="dl-lessons",
            roles=["CISO", "Business Continuity Manager"],
            objective="Recovery",
        ),
        info_q(
            "dl-lessons",
            "Lessons Learned",
            "<p>Review dwell time, detection gaps, and cross-border notification obligations.</p>",
            next_id="dl-close",
            discussion=300,
        ),
        info_q(
            "dl-close",
            "Exercise Close",
            "<p>{{company_name}} data exfiltration tabletop complete.</p>",
            notes="Summarise branch decisions and regulatory timeline.",
        ),
    ]

    return base_quiz(
        title="{{company_name}} — State-Sponsored Data Leak Tabletop",
        description="Advanced persistent threat and data exfiltration exercise with legal, forensic, and communications branches.",
        questions=questions,
        injects=injects,
    )