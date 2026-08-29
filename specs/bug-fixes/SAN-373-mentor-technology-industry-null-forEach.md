---
id: SAN-373
title: mentor-technology-industry forEach on null API arrays
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-373
sentry:
  - SC-SAAS-FRONTEND-3N
repos: [frontend]
commit: sc-saas-frontend@c0638d20 (branch ai_native_setup_aman)
created: 2026-08-19
updated: 2026-08-19
---

# SAN-373 — mentor-technology-industry forEach TypeError

## Root cause
`mentor-technology-industry.component.ts` calls `.forEach()` on `sectoralInterestIds`/`technologies` destructured from the mentor-info API response with no null guard, while every sibling field in the same destructure (`domainAreasPrimary`, `domainAreas`, `sectoralInterestOthers`) already uses `?.`. The backend evidently returns `null` (not `[]`) for a mentor who hasn't picked interests yet — matches the 26 affected users (new mentor profiles).

## Fix
Added `?.` before both `.forEach()` calls, matching the sibling fields' existing convention.

## Blast radius
None — if the forEach is skipped, `industriesForm`/`technologiesForm` simply keep their default `false`-valued controls; `saveButtonDisabled` already gates on an unpopulated form, so Save stays disabled rather than crashing.

Flagged separately (not fixed here): the inconsistent null-vs-array API response is a real upstream shape gap worth a backend DTO fix so the array always defaults to `[]`.

## Verification
`tsc --noEmit` clean.
