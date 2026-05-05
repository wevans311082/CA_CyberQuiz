# Phase 4 End-to-End Manual Test Walkthrough

**Document Version:** 1.0  
**Date:** May 5, 2026  
**Scope:** Tabletop Slide System Expansion (Phases 1–4)

---

## Overview

This document outlines a manual end-to-end test walkthrough covering all tabletop features implemented in Phases 1–4:

- **Phase 1:** Branching, roles, and tabletop decision-making
- **Phase 2:** Injects, facilitator notes, and discussion timer
- **Phase 3:** INFORMATION/FILE slide types and per-slide timer controls
- **Phase 4:** Master theme system, theme overrides, file upload, file download audit logging

---

## Pre-Test Setup

### Environment
- Backend running on `http://localhost:8000`
- Frontend running on `http://localhost:5173` (Vite dev server)
- Redis cache available
- Database migrations applied (including migration `c3d4e5f6a7b8`)
- Storage backend configured (local or S3)

### Test Scenario: Cyber Incident Response Drill

**Quiz Title:** Incident Response Playbook  
**Type:** Tabletop Exercise  
**Duration:** ~30 minutes  
**Participants:** 1 facilitator + 2–3 players in assigned roles (SOC Manager, Incident Commander, Communications Lead)

---

## Test Walkthrough Steps

### 1. Quiz Authoring (Master Theme + Question Types)

**Goal:** Verify theme system, slide types, and file upload in editor

#### 1.1 Create Quiz with Master Theme
- [ ] Open editor, create new tabletop quiz
- [ ] In **Settings → Master Slide Theme**, set:
  - Background Color: `#0f172a` (dark blue)
  - Text Color: `#ffffff` (white)
  - Accent Color: `#f97316` (orange)
  - Font Family: `Inter, sans-serif`
  - Background Image: (optional, leave blank or choose image)
- [ ] Verify theme values are persisted in localStorage

#### 1.2 Add Question Types
Create 5 questions:

1. **Q1: ABCD (Introduction)**
   - Type: ABCD (multiple choice)
   - Title: "Initial Incident Report"
   - Question: "What type of alert triggered the incident?"
   - Answers:
     - A: Web application error (correct)
     - B: Database connection loss
     - C: Network outage
     - D: Hardware failure
   - Discussion Time: 60 seconds
   - Facilitator Notes: "Discuss the alert source; this determines escalation path"
   - Decision Mode: Majority Vote
   - Default Next: Q2

2. **Q2: INFORMATION (Briefing)**
   - Type: INFORMATION
   - Title: "Incident Timeline"
   - Content: "Timeline of events:\n- 09:00 UTC: Alert fired\n- 09:05 UTC: Incident created\n- 09:10 UTC: SOC assigned ticket"
   - Facilitator Notes: "Present timeline to team; no voting needed"
   - Optional: Add a background image/diagram
   - Default Next: Q3

3. **Q3: ABCD with Branch (Decision Point)**
   - Type: ABCD
   - Title: "Containment Strategy"
   - Question: "Which systems should be isolated first?"
   - Allowed Roles: SOC Manager, Incident Commander
   - Decision Mode: Consensus
   - Answers:
     - A: Web servers (Branch to Q4)
     - B: Database servers (Branch to Q5)
     - C: All systems (Branch to Q5)
     - D: None (Branch to Q2, escalation fallback)
   - Discussion Time: 120 seconds
   - Timer Enabled: Yes (default 90 seconds)

4. **Q4: FILE (Evidence Review)**
   - Type: FILE
   - Title: "Server Logs Review"
   - Description: "Review access logs from affected servers"
   - Add File Attachments:
     - Upload `incident_logs.pdf` (or create dummy file)
     - Filename: "Server Access Logs"
     - MIME Type: `application/pdf`
     - Description: "Filtered access logs from web servers"
   - Facilitator Notes: "Participants can download and review logs; check for suspicious access patterns"
   - Default Next: Q5

5. **Q5: INFORMATION (Conclusion)**
   - Type: INFORMATION
   - Title: "Next Steps"
   - Content: "Actions:\n1. Document findings\n2. Create remediation plan\n3. Schedule follow-up review"
   - Facilitator Notes: "Wrap-up and thank participants"

#### 1.3 Apply Per-Slide Theme Overrides
- [ ] On Q2 (INFORMATION):
  - Advanced Options → Override Master Theme
  - Override Accent Color: `#06b6d4` (cyan)
  - Verify override persists
- [ ] On Q4 (FILE):
  - Advanced Options → Override Master Theme
  - Override Background Color: `#1e293b` (slightly lighter)
  - Verify override persists

#### 1.4 Add Injects (Phase 2)
- [ ] Settings → Injects:
  - Inject 1 (trigger after Q3):
    - Title: "Network Alert"
    - Severity: `warning`
    - Content: "⚠️ Network latency spike detected on backbone. Impact: 5% packet loss."
    - Image: (optional)
  - Inject 2 (trigger after Q4):
    - Title: "Executive Escalation"
    - Severity: `critical`
    - Content: "🚨 CTO requesting real-time update. ETA for containment decision needed."
    - Image: (optional)

#### 1.5 Save Quiz
- [ ] Save quiz; verify in quiz list
- [ ] Verify all fields persisted:
  - Master theme in payload
  - Question types (ABCD, INFORMATION, FILE)
  - File attachments with URLs
  - Injects list
  - Branching metadata

---

### 2. Game Start & Admin/Player Lobby (Roles Setup)

**Goal:** Verify role assignment and scenario startup

#### 2.1 Facilitator Starts Game
- [ ] Admin opens quiz in live mode
- [ ] Click "Start Game" → generates PIN (e.g., `1234`)
- [ ] Admin sees lobby with master theme applied to background
- [ ] Verify theme colors and fonts are visible

#### 2.2 Players Join & Get Assigned Roles
- [ ] Player 1 joins with PIN `1234`, username `alice`
- [ ] Player 2 joins, username `bob`
- [ ] Player 3 joins, username `carol`
- [ ] Admin assigns roles:
  - alice → SOC Manager
  - bob → Incident Commander
  - carol → Communications Lead
- [ ] Players see "Your Role: [Role Name]" chip in lobby
- [ ] Players see other players' roles (badges in player list)

#### 2.3 Verify Master Theme Applied to Players
- [ ] All players see quiz title with master theme background/text colors
- [ ] All players see master theme fonts applied
- [ ] Admin sees same theme

---

### 3. Q1: ABCD Question (Phase 1 Branching + Phase 2 Discussion Timer)

**Goal:** Verify role-based voting, discussion timer, injects

#### 3.1 Question Emit & Display
- [ ] Admin moves to Q1
- [ ] All players see Q1: "Initial Incident Report"
- [ ] Theme applied: background, text color, accent color for answer buttons
- [ ] Facilitator notes visible to admin only (blue card, top-left): "Discuss the alert source…"
- [ ] Discussion timer: Admin sees input field "Discussion: __ s" with "▶ Start" button
- [ ] Players see all 4 answer options with timer visible if admin starts

#### 3.2 Submit Answers
- [ ] alice submits: A (Web application error)
- [ ] bob submits: A
- [ ] carol submits: B
- [ ] Server-side: Verify role check passed (all roles allowed to answer)
- [ ] Admin sees answer summary: A (2), B (1) — waiting for 100% submission

#### 3.3 Discussion Timer
- [ ] Admin clicks "▶ Start" discussion timer (default 60s)
- [ ] Players see countdown badge (top-right): "01:00" → "00:59" → ...
- [ ] Timer color: green (>60s) → yellow (≤60s) → red (≤15s)
- [ ] Admin can click ⏸ (pause), ▶ (resume), ■ (stop)
- [ ] After 60s timeout, timer stops and admin sees "Discussion: __ s" again
- [ ] Verify timer state persisted in Redis and synced to all clients

---

### 4. Branching Decision (Phase 1)

**Goal:** Verify majority vote leads to correct branch

#### 4.1 Move to Q3: Decision Point
- [ ] Admin manually advances from Q1 → Q3 (skip Q2 for now)
- [ ] Q3 shown: "Which systems should be isolated first?"
- [ ] Theme applied (with cyan accent override on answers)
- [ ] Allowed Roles: SOC Manager, Incident Commander → Communications Lead is blocked

#### 4.2 Answer Submission with Role Check
- [ ] Communications Lead (carol) tries to submit answer → blocked
  - Server emits `role_not_allowed` event
  - carol sees message: "Waiting for SOC Manager and Incident Commander to decide"
- [ ] alice (SOC Manager) submits: A (Web servers)
- [ ] bob (Incident Commander) submits: B (Database servers)
- [ ] carol (Communications Lead) still blocked, sees "Waiting for…" message

#### 4.3 Tie Detection
- [ ] Server detects tie: A (1) vs B (1)
- [ ] All clients receive `tie_detected` event
- [ ] Admin sees tie-break UI with buttons for each option:
  - "Resolve → A" (Web servers)
  - "Resolve → B" (Database servers)
- [ ] Admin clicks "Resolve → A"
- [ ] Server emits `branch_resolved` with next_question_id = Q4
- [ ] All clients advance to Q4

---

### 5. Q2: INFORMATION Screen (Phase 3)

**Goal:** Verify INFORMATION slide render and theme override

#### 5.1 Return to Q2 (Manual Branch)
- [ ] Admin manually sets current question to Q2
- [ ] Players see Q2: "Incident Timeline" (INFORMATION type)
- [ ] Content displayed (multiline text with timeline):
  - "Timeline of events:\n- 09:00 UTC: Alert fired\n- 09:05 UTC…"
- [ ] Theme override applied: accent color is cyan (#06b6d4)
- [ ] **No answer buttons** (INFORMATION type never has choices)
- [ ] Admin sees facilitator notes: "Present timeline to team…"
- [ ] Optional: Background image/diagram displayed if set

#### 5.2 Transition Timer (Phase 3)
- [ ] If Q2 has `timer.enabled = true`:
  - Admin sees "Answer: ___ s" (question timer, not discussion timer)
  - Admin can start/pause/resume/stop question timer
  - Players see countdown badge
- [ ] Admin manually advances after reviewing (no voting needed)

---

### 6. Q4: FILE Screen (Phase 3 + Phase 4)

**Goal:** Verify FILE slide, file upload/download, audit logging

#### 6.1 Display FILE Slide
- [ ] Admin moves to Q4: "Server Logs Review" (FILE type)
- [ ] Players see:
  - Title: "Server Logs Review"
  - Description: "Review access logs from affected servers"
  - File attachment box with:
    - Filename: "Server Access Logs"
    - MIME Type: `application/pdf`
    - "Open" link (or download button)
- [ ] Theme applied (background override from author)

#### 6.2 File Download & Audit Logging
- [ ] alice clicks "Open" (or download link) → browser downloads `incident_logs.pdf`
- [ ] Client emits socket event: `file_downloaded` with `{ file_id: "...", filename: "incident_logs.pdf" }`
- [ ] Server receives event, calls `log_file_download(game_pin, "alice", file_id, "incident_logs.pdf")`
- [ ] Entry added to in-memory file download log (Redis or game session cache)
- [ ] bob also clicks "Open" → another log entry recorded
- [ ] carol clicks "Open" → third log entry recorded

#### 6.3 Verify Audit Log Payload
- [ ] After game ends, export results
- [ ] In exported JSON, find `file_downloads_log`:
  ```json
  "file_downloads_log": [
    {
      "username": "alice",
      "file_id": "file-uuid-xxx",
      "filename": "incident_logs.pdf",
      "timestamp": "2026-05-05T10:30:00Z"
    },
    {
      "username": "bob",
      "file_id": "file-uuid-xxx",
      "filename": "incident_logs.pdf",
      "timestamp": "2026-05-05T10:32:00Z"
    },
    ...
  ]
  ```
- [ ] Verify order and timestamps are chronological

#### 6.4 FILE with Multiple Attachments
- [ ] (Advanced test) If Q4 had multiple file attachments, verify:
  - Each file appears as separate clickable link
  - Each download is logged separately
  - Audit log captures unique file_id per attachment

---

### 7. Per-Slide Answer Timer (Phase 3 + Phase 4)

**Goal:** Verify question timer controls and synchronization

#### 7.1 Question with Timer Enabled
- [ ] Admin moves to a question with `timer.enabled = true` (e.g., Q3)
- [ ] Admin sees "Answer:" control bar next to Discussion timer
- [ ] Input field for custom duration (e.g., "120" seconds)
- [ ] "▶ Start" button
- [ ] Admin clicks "▶ Start" → timer starts
- [ ] Players see countdown overlay badge (top-right): "02:00" → "01:59" → ...
- [ ] Admin can pause (⏸), resume (▶), or stop (■)

#### 7.2 Timer Color Coding
- [ ] Verify timer colors:
  - Green: > 30s
  - Yellow: 10–30s
  - Red: ≤ 10s
  - Gray: paused/stopped
- [ ] Admin adjusts visible-only timer controls (pause/resume/stop)

#### 7.3 Timer State Synchronization
- [ ] Open browser DevTools → Network tab
- [ ] Observe socket events emitted/received:
  - `question_timer_started` (contains total seconds)
  - `question_timer_paused` (contains remaining seconds)
  - `question_timer_resumed`
  - `question_timer_stopped`
- [ ] Verify all players receive same events
- [ ] Verify Redis key `game:{pin}:question_timer` contains timer state

#### 7.4 Transition Between Questions
- [ ] Admin moves to next question
- [ ] Old timer stops automatically
- [ ] If new question has `timer.enabled = true`, admin sees new timer UI ready to start

---

### 8. Facilitator Notes & Injects (Phase 2)

**Goal:** Verify facilitator-only information and triggered injects

#### 8.1 Facilitator Notes Display
- [ ] Admin sees blue card in top-left corner with:
  - **Facilitator Notes** (bold header)
  - Current question's `facilitator_notes` text
- [ ] Notes update as admin changes questions
- [ ] Players never see facilitator notes (only on server → admin)

#### 8.2 Auto-Triggered Injects
- [ ] After Q3 answered (first inject trigger):
  - All players receive `inject_received` event
  - Inject notification appears (orange card, severity: `warning`):
    - Title: "Network Alert"
    - Content: "⚠️ Network latency spike…"
  - Players can click "Dismiss" to close
- [ ] After Q4 completed (second inject trigger):
  - Critical inject appears (red card):
    - Title: "Executive Escalation"
    - Content: "🚨 CTO requesting real-time update…"
  - Players can dismiss

#### 8.3 Manual Inject Push (Admin)
- [ ] Admin opens Injects panel (button in controls bar)
- [ ] Admin can:
  - Select from pre-defined injects dropdown and push
  - Enter ad-hoc inject text and push immediately
- [ ] Notification appears on all players with new severity/content

---

### 9. Situation Room (Phase 2)

**Goal:** Verify situation tracking and status UI

#### 9.1 Admin Situation Update
- [ ] Admin opens Situation Room panel
- [ ] Admin sets:
  - Severity: `critical`
  - Phase: `containment`
  - Affected Systems: `web, database`
  - Summary: "Active incident in production; containment in progress"
- [ ] Admin clicks "Update"

#### 9.2 Players See Situation Status
- [ ] All players see bottom status bar update:
  - Color: red (critical)
  - Text: "CRITICAL: Containment - web, database"
- [ ] Players can click to expand and see full summary

#### 9.3 Status Persistence
- [ ] Move to next question and back
- [ ] Situation status bar remains (or can be re-fetched)

---

### 10. Game Export & Results (Phase 4)

**Goal:** Verify all audit logs and metadata in final export

#### 10.1 Complete the Quiz
- [ ] Advance through remaining questions (Q5: INFORMATION conclusion)
- [ ] Admin ends game

#### 10.2 Export Results
- [ ] Access results/export view
- [ ] Download/view exported JSON or CSV

#### 10.3 Verify Exported Data
Check that exported results contain:
- [ ] `scenario_type: "tabletop"`
- [ ] `player_roles: { alice: "SOC Manager", bob: "Incident Commander", carol: "Communications Lead" }`
- [ ] `branch_path: [Q1_id, Q3_id, Q4_id, Q5_id]` (actual branches taken)
- [ ] `injects_log`: List of all injects pushed with timestamps
- [ ] `situation_log`: List of all situation updates with timestamps
- [ ] `file_downloads_log`: All file downloads with username, file_id, filename, timestamp
- [ ] Per-question: `answers`, `discussion_time_used`, `timer_data` (if applicable)
- [ ] `master_theme`: Full theme configuration used during game
- [ ] Per-slide: `theme_override` applied (if any)

#### 10.4 Verify Data Integrity
- [ ] All timestamps are valid ISO 8601 format
- [ ] All UUIDs for questions/files are valid
- [ ] All usernames match player list
- [ ] All branch_path IDs exist in quiz
- [ ] No null/undefined fields in critical structures

---

## Edge Cases & Regression Tests

### 11.1 Legacy Quiz Compatibility
- [ ] Load a **pre-Phase 4 quiz** (without master_theme, file_attachments):
  - Game starts without errors
  - No theme applied (or default theme)
  - Questions render normally
  - No file download auditing (field is null)

### 11.2 Mixed Question Types
- [ ] Quiz with ABCD, INFORMATION, FILE, ABCD questions in sequence:
  - All render correctly
  - Branching works across types
  - Timers work only for ABCD/INFORMATION (if enabled)

### 11.3 Role-Based FILE Access
- [ ] (If implemented) FILE slide with allowed_roles restriction:
  - Only assigned roles see download link
  - Other roles see "Waiting for…" message
  - Download logs only capture downloads from authorized roles

### 11.4 Storage Backend Fallback
- [ ] Test with **local storage** backend:
  - File upload stores to local disk
  - Download retrieves from local disk
  - Audit log records correctly
- [ ] Test with **S3 storage** backend (if configured):
  - File upload stores to S3
  - Download retrieves from S3
  - Audit log records correctly

### 11.5 Timer Synchronization Under Load
- [ ] Start timer, then manually send multiple timer control events in rapid succession
- [ ] Verify final state is consistent across all clients
- [ ] No duplicate timer entries in Redis

---

## Success Criteria

✅ **All tests pass** if:

1. **Master Theme System:**
   - Quiz-level theme set in editor persists to database
   - Per-slide overrides persist to database
   - Runtime: theme colors applied to all question types (ABCD, INFORMATION, FILE)
   - Theme values appear in exported results

2. **Question Types:**
   - INFORMATION slides render text/content without answer buttons
   - FILE slides display attachments with download links
   - All types inherit master theme + override

3. **Per-Slide Timers:**
   - Admin can start/pause/resume/stop timer per question
   - Players see live countdown (MM:SS format)
   - Timer colors change based on remaining time
   - Timer state syncs via socket events
   - No timer appears for questions with `timer.enabled = false`

4. **File Upload & Audit:**
   - Files upload via POST `/api/v1/storage/` 
   - Storage ID returned and saved in attachment
   - File downloads recorded in audit log with username/filename/timestamp
   - Audit log exported in final game results

5. **Branching & Roles:**
   - Questions with allowed_roles block ineligible players
   - Tie detection and admin resolution works
   - Branch paths followed as expected
   - All branch history exported

6. **Injects & Situation:**
   - Auto-triggered injects appear at specified times
   - Admin can manually push injects
   - Situation room updates propagate to all players
   - All events logged and exported

7. **Backward Compatibility:**
   - Pre-Phase 4 quizzes load and run without errors
   - New fields optional and default to null/empty

---

## Notes

- **Performance:** Monitor network traffic and server logs during multi-player scenario to check for excessive socket event volume or memory leaks in Redis.
- **Browser Compatibility:** Test on Chrome, Firefox, and Safari (if applicable).
- **Accessibility:** Verify timer countdown and inject notifications are readable and accessible (color contrast, screen reader).
- **Mobile:** Verify admin controls and player UI work on tablet/mobile viewports.

---

**Document End**
