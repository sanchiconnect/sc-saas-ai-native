---
id: SAN-785
title: Corporate profile completion shows 100% while Company Logo / Engagement fields are still missing
type: bug-fix
status: in-review
linear: https://linear.app/sanchiconnect/issue/SAN-785
repos: [backend]
commit:
created: 2026-09-15
updated: 2026-09-15
---

# SAN-785 — corporate profile-completeness percentage ignores companyLogo / connectionRequirements

## Problem
On the corporate "Edit profile" page (`/corporates/edit/corporate-intro`), the top "Profile completion" bar read 100% even though Company Logo (Basic Information tab) and "Why do you want to connect with startups?" (Engagement tab, `connectionRequirements`) were both empty — both tabs showed a red "!" and the page's own "field(s) are not complete yet" banner was visible at the same time as the 100% bar.

## Root cause (CODE_ERROR)
`sc-saas-backend/src/modules/corporate/repositories/corporate.repository.ts`, `getCorporateProfileCompleteness()`:
1. The `criteria.corporate` array that drives `completenessReport.percentage` had `companyLogo` and `connectionRequirements` commented out, so neither was ever counted toward total/completed — even though the frontend (`corporate-intro.component.ts` and `corporate-engagement.component.ts`, both `countInvalidFields` getters) independently treats both as mandatory for their own tab-level red "!" indicators.
2. The query builder's `.select([...])` list didn't fetch `corporates.companyLogo` or `corporates.connectionRequirements` at all, so even once uncommented, `calculateCompleteness()` would have seen both as permanently `undefined` regardless of actual DB value.

## Fix
- Added `companyLogo` back into the base `criteria.corporate` list (unconditionally required, matches Basic Information tab).
- Added `connectionRequirements` into the existing `saasFeatures[Feature.CORPORATE_ENGAGEMENT_FORM]`-gated block instead of the base list — the Engagement tab (`navlinks.ts`: `featureKey: 'corporates_enagement_form'`) is entirely hidden for tenants with that flag off, so making the field unconditionally required would have permanently blocked those tenants at <100%.
- Added `corporates.companyLogo` and `corporates.connectionRequirements` to the query builder's `.select([...])` list.

Scope: `sc-saas-backend` only, corporate stakeholder only — no other stakeholder type touched, no API contract shape change, no flag change, no frontend change (the frontend's nav-links component was already anticipating this exact fix — see `ENGAGEMENT_MISSING_FIELD_MESSAGES` / `isEngagementDataComplete()` in `corporate-edit-page-nav-links.component.ts`).

## Verification
- `npx tsc --noEmit` — clean.
- `npx eslint` on both touched files — no new warnings/errors (only pre-existing unrelated warnings on the repository file).
- Added `sc-saas-backend/src/modules/corporate/repositories/corporate.repository.spec.ts` (4 Jest tests, all passing): Company Logo missing → percentage < 100; Connection requirements NOT required when Engagement flag is off; Connection requirements required when Engagement flag is on; both filled → 100% / `canRequestApproval` true.
- Not manually verified in the running app (no dev environment exercised this session) — Jest coverage plus the type-check are the verification for this fix.
