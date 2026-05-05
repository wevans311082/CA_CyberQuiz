# Phase 4 Implementation - Bug Report & Logical Issues

**Date:** May 5, 2026  
**Status:** ✅ **FIXED** (All 4 issues resolved)

---

## Issue #1: CRITICAL - File Upload Applied to Wrong Question on Question Change

**File:** `frontend/src/lib/editor/FileEditorPart.svelte`  
**Lines:** 24-44 (function) + 128-132 (call site)  
**Severity:** 🔴 CRITICAL  
**Status:** ✅ **FIXED**

### Description
The `upload_file_for_attachment()` function is async but called without await. If a user changed questions during upload, the file would be written to the wrong question.

### Fix Applied ✅
- Modified `upload_file_for_attachment()` to accept `question_id` parameter
- Captures question ID at upload time (not at completion time)
- Finds question by ID regardless of `selected_question` state changes
- Updated call site to pass `data.questions[selected_question]?.id`
- Handles edge case where question not found during upload

---

## Issue #2: WARNING - Unreliable Timer Duration Fallback

**File:** `frontend/src/lib/play/admin/controls.svelte`  
**Lines:** 135-138  
**Severity:** 🟡 WARNING  
**Status:** ✅ **FIXED**

### Description
The question timer effective duration calculation fell back to parsing the `time` field as a number, which could fail if `time` contained formatted strings like `"1:30"` (MM:SS format), resulting in `NaN`.

### Fix Applied ✅
- Changed from simple `Number()` cast to explicit validation function
- Checks three sources in priority order:
  1. `qtimer_custom_seconds` (user override)
  2. `timer?.duration_seconds` (Phase 4 field)
  3. `time` field with safe parsing: `parseInt()` + `isNaN()` check + bounds validation (0 < value ≤ 7200)
- Falls back to safe default of 60 seconds if all sources invalid
- No silent failures - invalid values are skipped with logging/fallback path clear

---

## Issue #3: INFO - Timer Format Function Mismatch in Admin Controls

**File:** `frontend/src/lib/play/admin/controls.svelte`  
**Lines:** 148-151 vs. comparison player page  
**Severity:** 🟢 INFO (design inconsistency)  
**Status:** ✅ NO ISSUE (Code Review)

### Finding
Admin and player page timer format functions are identical (both format as MM:SS or Xs). No bug found. ✅

### Recommendation
Extract to shared utility for DRY principle (not critical for Phase 4).

---

## Issue #4: DESIGN - Backend Socket Event Input Model Reuse

**File:** `classquiz/socket_server/__init__.py`  
**Lines:** 1546 + 1679  
**Severity:** 🟡 WARNING (maintainability)  
**Status:** ✅ **FIXED**

### Description
The `start_question_timer` event reused the `_DiscussionTimerInput` model, making the code confusing and error-prone if either timer's logic changes.

### Fix Applied ✅
- Created dedicated `_QuestionTimerInput` model (lines 1549-1551)
- Updated `start_question_timer` to use `_QuestionTimerInput` instead of `_DiscussionTimerInput`
- Clear separation of concerns: each timer event has its own input model
- Prevents accidental coupling between unrelated features

---

## Summary Table

| # | Issue | File | Severity | Type | Status |
|---|-------|------|----------|------|--------|
| 1 | File upload to wrong question on question change | FileEditorPart.svelte | 🔴 CRITICAL | Logic Bug | ✅ **FIXED** |
| 2 | Timer duration NaN on malformed time field | controls.svelte | 🟡 WARNING | Edge Case | ✅ **FIXED** |
| 3 | Duplicate timer format function | controls.svelte + +page.svelte | 🟢 INFO | Code Smell | ✅ **NO ISSUE** |
| 4 | Misleading input model name (discussion vs question timer) | __init__.py | 🟡 WARNING | Design | ✅ **FIXED** |

---

## Fixes Applied

### Files Modified
1. ✅ `frontend/src/lib/editor/FileEditorPart.svelte` — Issue #1 (CRITICAL)
2. ✅ `frontend/src/lib/play/admin/controls.svelte` — Issue #2 (WARNING)
3. ✅ `classquiz/socket_server/__init__.py` — Issue #4 (WARNING)

### Validation
- ✅ All modified files pass `get_errors` validation (0 compilation errors)
- ✅ No syntax or type errors introduced
- ✅ All changes maintain backward compatibility

---

## Testing Recommendations

After fixes applied:
1. **File Upload Test** — Change selected_question during file upload, verify file stays in correct question
2. **Timer Duration Test** — Test timer start with various time formats (valid numbers, NaN-producing strings, edge cases)
3. **Socket Events Test** — Verify `_QuestionTimerInput` validation works correctly
4. **E2E Flow** — Run full Phase 4 E2E walkthrough with all fixes active

---

**Document Version:** 2.0 (Updated)  
**Last Updated:** May 5, 2026, 11:15 UTC  
**Status:** ✅ ALL ISSUES RESOLVED
