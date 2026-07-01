# SPDX-FileCopyrightText: 2025 CyberAsk
#
# SPDX-License-Identifier: MPL-2.0

from classquiz.seed.builders import abcd_q, base_quiz, file_q, info_q, voting_q


def build() -> dict:
    injects = [
        {
            "id": "dr-inj-1",
            "title": "Datacenter power failure",
            "content": "**Facilities:** Primary datacenter lost utility power. Generators failed after 40 minutes. Temperature rising in server halls.",
            "severity": "critical",
            "trigger_after_question_id": "dr-incident",
        },
        {
            "id": "dr-inj-2",
            "title": "Cloud provider regional outage",
            "content": "**Ops:** Secondary cloud region reports API degradation. Failover automation partially succeeded.",
            "severity": "warning",
            "trigger_after_question_id": "dr-d2-activate",
        },
        {
            "id": "dr-inj-3",
            "title": "Customer SLA breach warnings",
            "content": "**Comms:** Top 10 enterprise customers threaten contract penalties if {{primary_system}} is unavailable beyond 4 hours.",
            "severity": "warning",
            "trigger_after_question_id": "dr-d4-comms",
        },
    ]

    questions = [
        info_q(
            "dr-brief",
            "Exercise Briefing — Full Disaster Recovery",
            "<p><strong>{{company_name}}</strong> business continuity and disaster recovery tabletop.</p>"
            "<p><strong>Date:</strong> {{exercise_date}} · <strong>Location:</strong> {{location}}</p>",
            next_id="dr-context",
            discussion=180,
        ),
        info_q(
            "dr-context",
            "BCP & Infrastructure Overview",
            "<p>Critical service: <strong>{{primary_system}}</strong> serving {{employee_count}} internal users and external customers.</p>"
            "<p>RTO target: 4 hours. RPO target: 15 minutes. Alternate site: warm standby in secondary region.</p>",
            next_id="dr-incident",
        ),
        info_q(
            "dr-incident",
            "Incident — Cascading Infrastructure Failure",
            "<p>06:30: UPS failure at primary datacenter. 07:10: Generator fault. 07:45: Controlled shutdown of production cluster initiated.</p>"
            "<p>{{primary_system}} is offline. Payment processing queue growing.</p>",
            next_id="dr-evidence",
            discussion=150,
        ),
        file_q(
            "dr-evidence",
            "Evidence Review — RTO/RPO Matrix & Runbooks",
            "<p>Review the BCP matrix and failover runbooks. Identify dependencies and recovery order constraints.</p>",
            filename="bcp-rto-rpo-matrix.txt",
            description="Synthetic BCP document: system tiers, RTO/RPO, and dependency map.",
            next_id="dr-d1-assess",
            roles=["Business Continuity Manager", "IT Operations"],
            discussion=240,
        ),
        abcd_q(
            "dr-d1-assess",
            "Decision 1 — Declare disaster?",
            "Do you invoke the disaster recovery plan?",
            [
                ("Declare disaster; activate crisis management team", "dr-d2-activate"),
                ("Wait 2 hours for utility restoration", "dr-d3-priority"),
                ("Fail over single critical service only", "dr-d2-activate"),
                ("Escalate to {{ceo_name}} before any declaration", "dr-d2-activate"),
            ],
            roles=["Incident Commander", "Business Continuity Manager"],
            objective="Detection",
        ),
        abcd_q(
            "dr-d2-activate",
            "Decision 2 — Recovery site strategy",
            "Which recovery strategy do you execute?",
            [
                ("Full failover to warm standby site", "dr-d3-priority"),
                ("Partial failover — customer portal only", "dr-d3-priority"),
                ("Cold site rebuild from backups (accept longer RTO)", "dr-d3-priority"),
                ("Hybrid: SaaS substitute for customer portal", "dr-d3-priority"),
            ],
            roles=["IT Operations", "Business Continuity Manager"],
            objective="Recovery",
        ),
        abcd_q(
            "dr-d3-priority",
            "Decision 3 — System recovery order",
            "What do you restore first?",
            [
                ("{{primary_system}} customer-facing tier", "dr-d4-comms"),
                ("Identity and authentication services", "dr-d4-comms"),
                ("Payment processing and ledger", "dr-d4-comms"),
                ("Internal ERP and payroll", "dr-d5-vendors"),
            ],
            roles=["IT Operations", "Incident Commander"],
            objective="Recovery",
        ),
        abcd_q(
            "dr-d4-comms",
            "Decision 4 — Customer communication",
            "How do you notify customers of the outage?",
            [
                ("Status page update within 30 minutes", "dr-d5-vendors"),
                ("Direct outreach to top 50 accounts", "dr-d5-vendors"),
                ("Wait until failover completes before any notice", "dr-d6-staff"),
                ("Social media statement from {{ceo_name}}", "dr-d5-vendors"),
            ],
            roles=["Communications Lead", "Business Continuity Manager"],
            objective="Communication",
        ),
        abcd_q(
            "dr-d5-vendors",
            "Decision 5 — Vendor escalation",
            "Critical vendor SLA breach on managed database. Action?",
            [
                ("Invoke contractual disaster recovery clause", "dr-d6-staff"),
                ("Switch to secondary vendor contract", "dr-d6-staff"),
                ("Accept manual processing workaround", "dr-vote"),
                ("Delay vendor escalation until internal recovery fails", "dr-d6-staff"),
            ],
            roles=["IT Operations", "Legal & Compliance"],
        ),
        abcd_q(
            "dr-d6-staff",
            "Decision 6 — Staff & workplace continuity",
            "Primary office inaccessible. Staff continuity plan?",
            [
                ("Mandatory remote work; redirect call centre", "dr-vote"),
                ("Activate alternate office site", "dr-vote"),
                ("Skeleton crew on-site with safety overrides", "dr-vote"),
                ("Pause non-critical functions for 24 hours", "dr-vote"),
            ],
            roles=["HR Director", "Business Continuity Manager"],
            objective="Communication",
        ),
        voting_q(
            "dr-vote",
            "Resource allocation during recovery",
            "Allocate limited engineering capacity first to:",
            [
                "Customer-facing restoration",
                "Data integrity validation",
                "Security monitoring of failover environment",
                "Regulatory reporting obligations",
            ],
            next_id="dr-d7-test",
        ),
        abcd_q(
            "dr-d7-test",
            "Decision 7 — Failover validation",
            "Warm site is online. How do you validate before cutover?",
            [
                ("Full regression test suite on warm site", "dr-lessons"),
                ("Canary release to 5% of customers", "dr-lessons"),
                ("Immediate full cutover; fix issues live", "dr-lessons"),
                ("Parallel run for 24 hours before switch", "dr-lessons"),
            ],
            default_next="dr-lessons",
            roles=["IT Operations", "SOC Lead"],
            objective="Recovery",
        ),
        info_q(
            "dr-lessons",
            "Lessons Learned — DR Hot Wash",
            "<p>Evaluate generator maintenance, runbook accuracy, and crisis comms latency.</p>"
            "<p>Schedule full failover test within 90 days.</p>",
            next_id="dr-close",
            discussion=300,
        ),
        info_q(
            "dr-close",
            "Exercise Close",
            "<p>{{company_name}} disaster recovery tabletop complete.</p>",
            notes="Document RTO/RPO actuals vs targets.",
        ),
    ]

    return base_quiz(
        title="{{company_name}} — Disaster Recovery Tabletop",
        description="Full DR/BCP exercise with cascading failures, failover decisions, vendor escalation, and recovery validation.",
        questions=questions,
        injects=injects,
    )