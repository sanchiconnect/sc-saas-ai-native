---
id: SAN-666
title: "TypeError: Cannot read properties of undefined (reading 'features') in mentor-forms — missing optional chaining"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-666
sentry:
  - SC-SAAS-FRONTEND-B0
repos: [frontend]
commit: sc-saas-frontend@b1fd84ad (branch ai_native_setup_vishali)
created: 2026-09-07
updated: 2026-09-07
---

# SAN-666 — mentor-forms templates read brandDetails.features unguarded

## Root cause
Two templates in the `mentor-forms` chunk read `.features` off `brandDetails` without optional chaining, unlike every other read in the same files/module: `mentor-technology-industry.component.html` (`brandDetails.features.mentorship_areas_new_layout`) and `mentor-public-profile.component.html` (`brandDetails.features.events_exhibitors_menu_enabled`). If `brandDetails` hadn't emitted from the global NgRx store yet when these render, this threw.

## Fix
Added `?.` to both: `brandDetails?.features?.mentorship_areas_new_layout` and `brandDetails?.features?.events_exhibitors_menu_enabled`.

## Blast radius
None — before `brandDetails` loads, these expressions now evaluate to `undefined`/falsy (hiding the gated UI) instead of crashing; once it loads, behavior is identical to before.

## Verification
`npx tsc --noEmit -p tsconfig.app.json` clean. No test suite change — no automated regression coverage added.
