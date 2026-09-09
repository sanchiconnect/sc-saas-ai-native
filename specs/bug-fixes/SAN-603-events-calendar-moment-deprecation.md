---
id: SAN-603
title: "moment.js non-ISO date deprecation warning on calendar/events — 38 users, 44 events"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-603
sentry:
  - SC-SAAS-FRONTEND-14
repos: [frontend]
commit: sc-saas-frontend@6960ac6a (branch ai_native_setup_vishali, pushed)
created: 2026-09-04
updated: 2026-09-04
---

# SAN-603 — moment.js non-ISO date deprecation warning on calendar/events

## Root cause
`EventsCalenderComponent.expandMultiDayEvents()` pre-converted each multi-day date entry's raw 24-hour `time_from`/`time_to` into an AM/PM string via a local `formatTime()` helper before handing the expanded event off to `helpers.ts`'s `formatMeetingData()`. That function parses `` `${date} ${timeFrom}` `` with `moment.utc()` and **no explicit format string** — an AM/PM string there is neither ISO 8601 nor RFC 2822, so moment falls back to the unreliable native `Date()` parser and logs its deprecation warning, forwarded to Sentry via `captureConsoleIntegration`. Single-day events never hit this because their top-level `timeFrom`/`timeTo` are already in the raw 24-hour format `formatMeetingData()` expects.

## Fix
Removed the `formatTime()` AM/PM pre-conversion in `events-calender.component.ts:184-201`; multi-day date entries now pass their raw `dateEntry.time_from`/`time_to` straight through, matching single-day events' format. `formatMeetingData()` still does the AM/PM re-formatting itself downstream (`helpers.ts:46-47`) for display — end-user-visible output is unchanged, only the double-formatting that broke parsing is removed.

## Blast radius
None on display output — traced `expandMultiDayEvents()`'s result directly into both call sites of `formatMeetingData(response, 'eventTitle', false, true)` (`events-calender.component.ts:228, 299`) to confirm the re-format step still runs correctly on the raw input.

## Verification
`npx tsc --noEmit` clean. Added 4 unit tests covering the multi-day conversion, the `dates.length < 2` passthrough boundary, missing-`dates` passthrough, and an empty-array input.
