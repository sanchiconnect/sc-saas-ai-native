---
id: SAN-653
title: "TypeError: Cannot read properties of null (reading 'find') in corporate-intro.component"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-653
sentry:
  - SC-SAAS-FRONTEND-B8
repos: [frontend]
commit: sc-saas-frontend@143fb70e (branch ai_native_setup_vishali)
created: 2026-09-07
updated: 2026-09-07
---

# SAN-653 — corporate-intro subCategoriesList getter unguarded against unloaded industries

## Root cause
The `subCategoriesList` getter calls `this.industries.find((p) => p.id === +e)`, guarded only by the `enable_sub_industries` feature flag — not by whether `this.industries` (populated later, async, by `getInvesmentTypes()`) has loaded yet. Being a template-bound getter, it can run before that data arrives. A second, adjacent latent crash was also found: `found.industrySubCategoryDomains?.length` would throw if `.find()` returned no match (`found` undefined).

## Fix
Added `!this.industries` to the getter's early-return check, and guarded `found?.industrySubCategoryDomains?.length`.

## Blast radius
None — before data loads, the getter now returns `[]` (empty sub-categories list) instead of crashing; identical to the flag-disabled case already handled.

## Verification
`npx tsc --noEmit -p tsconfig.app.json` clean. No test suite change — no automated regression coverage added.

## Related
SC-SAAS-FRONTEND-B9 (SAN-652) is the same module chunk, different line — no shared root cause, just proximity.
