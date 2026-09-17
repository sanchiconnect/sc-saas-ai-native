---
id: SAN-596
title: "Uncaught (in promise): TypeError: Ne.forEach is not a function — calculateSlots() assumes dateAvailability is always an array"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-596
sentry:
  - SC-SAAS-FRONTEND-7A
repos: [frontend]
commit: sc-saas-frontend@5b6385cc (branch ai_native_setup_vishali, pushed)
created: 2026-09-04
updated: 2026-09-04
---

# SAN-596 — calculateSlots dateAvailability non-array

## Root cause
No stacktrace with resolvable source-mapped frames was available (culprit is a fully minified/generic `Array.forEach(<anonymous>)` label), so this couldn't be pinned with full certainty. `"X.forEach is not a function"` (as opposed to `"Cannot read properties of null/undefined (reading 'forEach')"`) means `X` is a defined, non-null value that simply lacks a `.forEach` method — e.g. a plain object, not an array.

The strongest candidate is `calculateSlots()` in `common-methods.ts:300` (before fix): `dateAvailability.forEach(...)`, where `dateAvailability` comes straight from `MeetingService.getUsersAvailabilityByDate()`'s raw API response with no shape validation. `calculateSlots` is called from 5 places (`add-meeting-modal`, `accept-connection-modal`, `edit-meeting-event`, `book-facility`, `book-facilitys`). This exact line is also the confirmed site for the separate SC-SAAS-FRONTEND-7P — same root cause, possibly the same underlying event under a different minified variable name/chunk hash. Not certain, but the best-supported fix given the evidence.

## Fix
```ts
const dateAvailabilityList = Array.isArray(dateAvailability) ? dateAvailability : [];
dateAvailabilityList.forEach((d) => { ... })
```
No behavior change when the API returns a proper array; only prevents the crash when it returns something else.

## Blast radius
None on the correct-input path. If the API genuinely sometimes returns a non-array, that date's booked-slot exclusions are simply skipped rather than crashing the whole slot-calculation flow.

## Confidence note
**Best-effort.** Mechanism confidence is high; confidence that this is literally the same event as SC-SAAS-FRONTEND-7A is moderate, given the fully-minified culprit. Flag for extra scrutiny if this doesn't fully resolve the Sentry group.

## Verification
`npx tsc -p tsconfig.json --noEmit` clean on the changed file. No automated test suite exists for this repo.

## Related
SC-SAAS-FRONTEND-7P (`dateAvailability.forEach is not a function`) — same site, not part of this batch, effectively fixed by the same change.
