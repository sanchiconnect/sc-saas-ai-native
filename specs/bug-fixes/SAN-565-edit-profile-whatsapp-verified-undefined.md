---
id: SAN-565
title: Cannot read 'isWhatsappNumberVerified' of undefined — EditProfileComponent
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-565
sentry:
  - SC-SAAS-FRONTEND-B6
repos: [frontend]
commit: sc-saas-frontend@1280df96 (branch ai_native_setup_vishali, not pushed)
created: 2026-09-03
updated: 2026-09-03
---

# SAN-565 — isWhatsappNumberVerified undefined read

## Root cause
`edit-profile.component.html` reads `profileDetails.isWhatsappNumberVerified` at two spots (lines 241, 299) without optional chaining. `profileDetails` only becomes defined once the `getProfileData` NgRx selector emits asynchronously in `ngOnInit`. A third occurrence of this exact read (line 340) already used `?.` — the other two were the inconsistent gap.

## Fix
Added `?.` at both remaining sites, making all three occurrences consistent.

## Blast radius
None — template-only guard; once `profileDetails` loads, rendering is identical to before.

## Verification
`npx tsc -p tsconfig.json --noEmit` clean.
