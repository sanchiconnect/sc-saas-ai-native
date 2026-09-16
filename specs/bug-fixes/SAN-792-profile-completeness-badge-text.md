# SAN-792 — Frontend: Standardize profile-completeness badge text to "Under Review"

**Repo:** sc-saas-frontend
**Linear:** https://linear.app/sanchiconnect/issue/SAN-792/frontend-standardize-profile-completeness-badge-text-to-under-review

## Problem

After submitting a profile for approval, the completeness badge showed inconsistent text across stakeholder types for the exact same underlying state — some said "Submitted", others said "Under Review".

## Evidence

All `*-profile-completeness` components compute the identical guard:

```
isUnderApproval = isApprovalRequested && !canToggleStatus && !isApproved
```

driven by the same reducer flag (`isApprovalRequested: true`, set identically in every `*.dashboard.reducer.ts` on submit — Corporate, Individual, Investor, Mentor, Partner, Program Office, Service Provider, Startup). Only the hardcoded badge text in each template differed:

- "Under Review" (already correct) — Corporate, Mentor, Partner, Program Office, Service Provider
- "Submitted" (needed to change) — Individual, Startup, Investor

## Root cause

**CODE_ERROR** — copy-paste UI text inconsistency across near-identical components. No tenant/feature flag (`IFeatures` in `brand.model.ts`) or backend status difference drives this — purely hardcoded template strings, confirmed via `/trace-flag`-style grep across `brand.model.ts` (nothing like `requires_review`/`auto_approve`/`profile_review` exists).

## Fix

Changed badge text to "Under Review" in the two components that said "Submitted":

1. `src/app/shared/common-components/individual-profile-completeness/individual-profile-completeness.component.html:68`
2. `src/app/shared/common-components/startup-investor-dashboard-profile/startup-investor-dashboard-profile.component.html:18` (shared by both Startup and Investor)

No changes needed to Corporate/Mentor/Partner/Program Office/Service Provider — already correct.

## Verification

Text-only template change, no logic touched. No lint configured for this repo (per repo CLAUDE.md). User confirmed skipping an automated regression test — pure hardcoded string with no conditional branch to protect.

## Commit

_pending — added once committed_
