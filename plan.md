# CyberAsk Platform Improvement Plan

## Purpose

This is the implementation tracker for the next major product-quality phase. The order below is intentional and follows the requested sequence. Each milestone must meet its acceptance criteria and testing gate before the next milestone is considered complete.

## Status legend

- `Planned` — defined but not started
- `In progress` — actively being implemented
- `Blocked` — cannot proceed without an external decision or dependency
- `Complete` — implemented and verified against the acceptance criteria

## Delivery principles

1. Preserve the existing live exercise, scoring, scenario editor, reference shelf, and framework guide capabilities.
2. Prefer server-authoritative state for live exercises, timers, scores, branches, and audit events.
3. Every facilitator action should be observable, recoverable, and safe to repeat.
4. Every player-facing flow must have loading, empty, error, retry, and reconnect states.
5. New features must work with light SaaS styling, slide-out panels, responsive layouts, keyboard navigation, and the existing white-label direction.
6. Do not call a feature complete until it has unit coverage plus a browser-level acceptance path where applicable.

## Roadmap

### 1. Decision-quality scoring — Planned

Replace simple correctness-only assessment with a richer model for tabletop decisions.

Scope:

- Time-to-decision.
- Evidence used.
- Stakeholders consulted.
- Risk awareness.
- Communication quality.
- Containment and recovery thinking.
- Alignment to selected framework outcomes.
- Facilitator-adjustable scoring rubric.
- Transparent player/team feedback.

Acceptance criteria:

- Facilitators can configure decision-quality dimensions per scenario.
- A response can receive partial scores with an explanation.
- Score calculations are idempotent and server-authoritative.
- Player, team, facilitator, and executive results show consistent totals.
- Reports explain why points were awarded or withheld.
- Existing quizzes without the new rubric continue to work unchanged.

Testing gate:

- Unit tests for rubric calculation, partial scoring, duplicate submissions, and bonus interaction.
- Multi-user test for player submission, facilitator review, and final results consistency.

### 2. Facilitator rehearsal, playback, and reset mode — Planned

Give facilitators a safe way to test and demonstrate a scenario before or during a live exercise.

Scope:

- Private rehearsal mode.
- Simulated player responses.
- Adjustable clock speed.
- Inject preview without broadcasting.
- Branch simulation.
- Save and restore exercise state.
- Restart from any node.
- Reset one team or the whole exercise.
- Replay a previous branch.

Acceptance criteria:

- Rehearsal sessions cannot alter production results or participant records.
- A facilitator can reset a session deterministically.
- Restoring a saved state restores node, branch, timer, role, score, inject, and note state.
- Rehearsal mode visibly identifies itself on every operator screen.
- A scenario can be tested from start to completion without a second account.

Testing gate:

- State snapshot/restore tests.
- Branch replay tests.
- Browser acceptance test proving rehearsal data is isolated from live reporting.

### 3. Facilitator preview as player — Planned

Allow facilitators to inspect the exact player experience before broadcasting decisions or content.

Scope:

- Open a player-view preview from the facilitator console.
- Preview current slide, timer, score, role, situation status, injects, notifications, and reference shelf.
- Toggle between player/team viewpoints.
- Highlight content that differs between facilitator and player views.
- Preview policy spotlight events.

Acceptance criteria:

- Preview uses the same rendering components as the real player screen.
- Preview cannot submit live answers or alter live state unless explicitly switched to rehearsal mode.
- Facilitators can identify hidden, unavailable, or broken media before launch.
- Preview works at desktop, tablet, and mobile widths.

Testing gate:

- Component tests for player/facilitator rendering parity.
- Browser test covering a scenario with branches, timer, inject, score, and policy spotlight.

### 4. Multi-browser reliability testing — Planned

Create a repeatable reliability harness for facilitator, player, projector, and reference workflows.

Scope:

- Playwright or equivalent browser test setup.
- One facilitator plus at least two players.
- Live Redis/Postgres test environment.
- Reconnect and rejoin testing.
- Timer synchronisation.
- Role assignment and acceptance.
- Branch decisions.
- Scoring and bonus points.
- Projector and presentation views.
- Policy spotlight and document access.
- Failure injection for disconnected sockets and delayed API responses.

Acceptance criteria:

- A complete end-to-end tabletop scenario runs automatically.
- Tests fail when facilitator and player state diverge.
- Tests cover refresh, reconnect, duplicate events, and late join/rejoin.
- CI can run the suite against disposable services.
- Test output includes screenshots, traces, console errors, and network failures.

Testing gate:

- Full browser suite passes against real Redis/Postgres services.
- No uncategorised console errors or unhandled promise rejections.

### 5. Scenario quality validator — Planned

Prevent broken scenarios from reaching preview or live use.

Scope:

- Orphaned slides.
- Dead-end and invalid branch targets.
- Duplicate or missing question IDs.
- Missing required answer data.
- Invalid role references.
- Unused injects.
- Missing recovery or debrief phase.
- Broken or unavailable media and policy references.
- Missing framework mappings.
- Excessively long, empty, or inaccessible content.
- Severity and timer consistency checks.
- Fix links into the relevant editor panel.

Acceptance criteria:

- Validation runs before preview, publish, and live start.
- Errors block unsafe operations; warnings remain reviewable.
- Each issue identifies the affected slide, inject, role, or document.
- Facilitators can export or copy a validation report.
- Existing valid templates pass with no blocking errors.

Testing gate:

- Validator unit tests for every issue type.
- Regression tests for all five built-in scenario templates.
- Browser test proving invalid scenarios cannot be launched accidentally.

### 6. Persistent live event timeline — Planned

Create an authoritative timeline for live operations, debugging, and reporting.

Scope:

- Injects delivered.
- Policies opened or spotlighted.
- Decisions and branch changes.
- Score awards and adjustments.
- Timer changes.
- Facilitator notes.
- Participant joins, leaves, reconnects, and role changes.
- System errors and retries.
- Search, filter, and export.
- Timeline links to the affected player, node, decision, or document.

Acceptance criteria:

- Events are persisted server-side with timestamp, actor, session, type, and payload metadata.
- Duplicate client events do not create duplicate timeline records.
- Timeline survives page refresh and reconnect.
- Sensitive content is permission-aware and excluded from unauthorised views.
- Timeline data is available to executive reporting and audit logs.

Testing gate:

- Persistence and idempotency tests.
- Permission tests.
- Multi-client ordering and reconnect tests.

### 7. Exercise health dashboard — Planned

Give facilitators an immediate view of operational and content risks.

Scope:

- Participant connection health.
- Players without roles.
- Required responses outstanding.
- Timer synchronisation warnings.
- Failed socket events.
- Missing branches or media.
- Unavailable reference documents.
- Unpublished scenario changes.
- Score consistency warnings.
- One-click remediation links.

Acceptance criteria:

- Health state is calculated from live server state and recent events.
- Warnings are categorised by severity and actionable.
- Facilitator can retry or resolve supported issues from the dashboard.
- Health status does not expose private player data unnecessarily.
- Dashboard remains usable on small screens.

Testing gate:

- Health calculation tests with healthy, degraded, and failed states.
- Browser test with deliberate disconnect, missing role, and failed reference document.

### 8. Framework coverage map — Planned

Make scenario alignment visible and useful rather than storing mappings as metadata only.

Scope:

- Scenario-to-framework coverage matrix.
- NIST CSF 2.0 Functions and outcomes.
- NCSC CAF 4.0 objectives and principles.
- CIS Controls v8.1 Controls.
- MITRE ATT&CK tactics and techniques.
- ISO/IEC 27001:2022 themes.
- Coverage by slide, decision, inject, and debrief action.
- Uncovered outcome warnings.
- Framework-linked reporting filters.
- Exportable coverage summary.

Acceptance criteria:

- Facilitator can see which scenario elements support each selected framework.
- Mappings link to the framework reference guide.
- Coverage distinguishes planned alignment from evidence observed during play.
- Reports never imply certification or compliance solely from scenario coverage.
- Framework catalog versions are explicit and updateable.

Testing gate:

- Mapping validation tests.
- Coverage aggregation tests.
- Browser test for editing, saving, filtering, and exporting coverage.

## Cross-cutting reliability backlog

These items should be addressed alongside the milestones when touched by implementation:

- Finish the remaining AAR reactive-state warning.
- Protect company policy downloads with exercise-scoped access or signed URLs.
- Replace remaining public or ambiguous browser storage access patterns.
- Preserve idempotency for scoring, bonus, branch, timer, and spotlight events.
- Add structured server error responses for socket actions.
- Add loading, empty, retry, and failure states to all new panels.
- Maintain keyboard and screen-reader accessibility.
- Keep the light SaaS visual system consistent across legacy facilitator consoles.
- Avoid adding another large client bundle without code splitting.

## Release checkpoints

### Checkpoint A — Scoring confidence

Complete milestones 1–3. Facilitators can assess decisions, rehearse scenarios, and inspect the player experience safely.

### Checkpoint B — Live reliability

Complete milestone 4. The full facilitator/player/projector workflow passes automated multi-browser testing against real services.

### Checkpoint C — Content safety

Complete milestone 5. Broken scenarios are caught before preview, publish, or launch.

### Checkpoint D — Operational control

Complete milestones 6–7. Facilitators have an authoritative timeline and health view during exercises.

### Checkpoint E — Enterprise reporting

Complete milestone 8. Scenario coverage and observed evidence can be explained clearly in debriefs and executive reports.

## Current status

Milestone 2 implementation note: isolated Redis rehearsal state, server acknowledgements, snapshots, restore/reset, clock speed, simulated player-response controls, and branch-following playback are implemented. Browser-level acceptance coverage against disposable services remains part of milestone 4.

| Milestone | Feature | Status |
|---:|---|---|
| 1 | Decision-quality scoring | Complete |
| 2 | Facilitator rehearsal, playback, and reset mode | Complete |
| 3 | Facilitator preview as player | Planned |
| 4 | Multi-browser reliability testing | Planned |
| 5 | Scenario quality validator | Planned |
| 6 | Persistent live event timeline | Planned |
| 7 | Exercise health dashboard | Planned |
| 8 | Framework coverage map | Planned |
