---
id: SAN-382
title: edit-meeting-event handleDurationChange crashes on null timeFrom
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-382
sentry:
  - SC-SAAS-FRONTEND-8W
repos: [frontend]
commit: sc-saas-frontend@c0638d20 (branch ai_native_setup_aman)
created: 2026-08-19
updated: 2026-08-19
---

# SAN-382 — edit-meeting-event handleDurationChange TypeError

## Root cause
`handleDurationChange()` calls `fromTime.split(':')` where `fromTime = this.meetingForm.value.timeFrom`. The `timeFrom` control initializes as `null`; selecting a duration chip before picking a time slot runs this method with `fromTime` still null.

## Fix
Added an early `return` guard when `fromTime` is falsy, before either `.split()` call.

## Blast radius
None — `timeForm`/`timeTo` both carry `Validators.required`, so the submit button is already disabled whenever `timeFrom` is empty regardless of whether `handleDurationChange` recalculates `timeTo`; no caller depends on the recalculation as an unconditional side effect.

## Verification
`tsc --noEmit` clean.
