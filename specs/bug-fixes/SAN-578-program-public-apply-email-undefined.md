---
id: SAN-578
title: "Uncaught: Cannot read 'email' of undefined — program-public-apply"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-578
sentry:
  - SC-SAAS-FRONTEND-9T
repos: [frontend]
commit: sc-saas-frontend@2ee07c21 (branch ai_native_setup_vishali, not pushed)
created: 2026-09-03
updated: 2026-09-03
---

# SAN-578 — email undefined on program-public-apply

## Root cause
`program-public-apply.component.html` line 102 interpolated `{{applicationMeta.name}} ({{applicationMeta.email}})` without `?.`. `applicationMeta` is a getter reading applicant info from localStorage and is referenced with `?.` at 7 other spots in the same file — line 102 was the sole exception.

The sibling SAN-482 fix (commit `f0484689`, same file, `checkAndAutoApply()`) added `if (!this.profileDetails) { return }`, guarding the whole object for that method's reads (including `.mobileNumber` and later `.email` at lines 225/226) — but that guard doesn't reach the template interpolation at line 102, which reads a different property path (`applicationMeta`, not `profileDetails`).

## Fix
Added `?.` at line 102, matching the other 7 occurrences of `applicationMeta` in this file.

## Blast radius
None — template-only guard; once `applicationMeta` resolves, output is identical.

## Verification
`npx tsc -p tsconfig.json --noEmit` clean.

## Related
SAN-482 (sibling fix, same file, `profileDetails` object rather than `applicationMeta`).
