---
id: SAN-760
title: "calenderAvilablity read before async load resolves — crashes in accept-connection-modal & isDisabledDateForMeeting"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-760
sentry:
  - SC-SAAS-FRONTEND-DD
  - SC-SAAS-FRONTEND-DB
repos: [frontend]
commit: sc-saas-frontend@6b3db5d1 (ai_native_setup_vishali)
created: 2026-09-14
updated: 2026-09-14
---

# SAN-760 — calenderAvilablity undefined-read guards

## Investigation

`accept-connection-modal.component.ts:95` declares `calenderAvilablity: IMeetingAvailability` with no
initializer; it's populated only once an async calendar-availability fetch resolves (line 178). But
`setMeetingForm()` wires up `date`/`duration` valueChanges listeners synchronously, so a user interacting with
those fields (or the datepicker calling `isDisabledDateForMeeting`) before that fetch resolves hits `undefined`:

- `accept-connection-modal.component.ts:266` (`recalculateSlots`) — `this.calenderAvilablity.availabilityHours`,
  no guard on `calenderAvilablity` itself.
- `common-methods.ts:108` (`isDisabledDateForMeeting`) — `calenderAvilablity.dates?.length`; the `?.` only
  guarded `.dates`, not the parent object.

Confirmed both still present/unguarded in current source — not a stale/already-fixed Sentry capture.

## Fix

Optional-chained both reads (`calenderAvilablity?.availabilityHours`, `calenderAvilablity?.dates?.length`).
Pure defensive guard — no change to meeting-availability logic once the data has loaded.

## Blast radius

None — same-file, same-behavior-when-loaded change. No API/flag/tenant-isolation contract touched.

## Verification

`npx tsc -p tsconfig.json --noEmit` clean for both touched files (only pre-existing, unrelated Jasmine/Karma
`.spec.ts` type errors elsewhere in the run — same known gap as [[SAN-753]]). No `.spec.ts` exists for either
file. Tests-first is blocked workspace-wide (no `guardian` skill yet); this is the substitute verification.

## Rollout

Committed and pushed as `sc-saas-frontend@6b3db5d1` ("SAN-760: guard calenderAvilablity reads before async
load resolves") on `ai_native_setup_vishali`, after Vishali's review and explicit go-ahead. Still subject to
the workspace's known frontend deploy lag.

## Open questions

None blocking.
