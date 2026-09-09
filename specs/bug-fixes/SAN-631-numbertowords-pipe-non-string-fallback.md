---
id: SAN-631
title: "NG02100: numberToWords|titlecase pipe chain throws on non-string fallback"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-631
sentry:
  - SC-SAAS-FRONTEND-45
  - SC-SAAS-FRONTEND-AV
repos: [frontend]
commit: sc-saas-frontend@0af48a0f (branch ai_native_setup_vishali)
created: 2026-09-07
updated: 2026-09-07
---

# SAN-631 — NumberToWordsPipe returns non-string, breaks chained titlecase

## Root cause
`investments-details.component.html` pipes a value through `numberToWords | titlecase`. `NumberToWordsPipe.transform()` only returns a word-string for a truthy integer; for any falsy/NaN/non-integer input it returned the raw value unchanged, which then hit `titlecase`. Angular's `TitleCasePipe` throws NG02100 for any non-string, non-null value, unconditionally (not dev-mode-gated). SC-SAAS-FRONTEND-45 (`ticketSizeMin`) and SC-SAAS-FRONTEND-AV (`ticketSizeMax`, `NaN` input) are the same pipe chain, same root cause.

## Fix
`NumberToWordsPipe.transform()`'s fallback branch now returns `typeof value === 'string' ? value : ''` instead of the raw value, so `titlecase` downstream never receives a non-string.

## Blast radius
None — every other call site either already passes a valid integer (unaffected) or now gets an empty string instead of a bare `NaN`/object rendered inline.

## Verification
`npx tsc --noEmit -p tsconfig.app.json` clean. No test suite change — no automated regression coverage added.
