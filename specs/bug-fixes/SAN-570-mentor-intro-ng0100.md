---
id: SAN-570
title: NG0100 ExpressionChangedAfterItHasBeenCheckedError in MentorIntroComponent
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-570
sentry:
  - SC-SAAS-FRONTEND-A8
repos: [frontend]
commit: 0b862bb0 (branch ai_native_setup_vishali) — pre-existing (SAN-527), verified only
created: 2026-09-03
updated: 2026-09-03
---

# SAN-570 — NG0100 in MentorIntroComponent

## Root cause
Template binding reading a value flipping from `null` to `true` right after initial render — same class as the Quill `editorContent` getter bug fixed under SAN-527.

## Finding — already fixed
Commit `0b862bb0` ("SAN-527: NG0100 ExpressionChangedAfterItHasBeenCheckedError from live Quill editorContent getter") explicitly lists Sentry ID `SC-SAAS-FRONTEND-A8` and `MentorIntroComponent` as one of three components it fixed — replaced the live `editorContent` getter with a plain field, set from `onAboutChange()` and after the initial `patchValue()`. Verified no other getter/null→true binding remains in the component (see `specs/bug-fixes/` doc for SAN-527 if present, and `0b862bb0`'s diff).

No new change made in this session — verified only.

## Blast radius
None — no new change.

## Verification
Confirmed via `git log`/diff that the fix is present and unmodified since.
