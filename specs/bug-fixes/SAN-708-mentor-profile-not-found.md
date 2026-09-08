---
id: SAN-708
title: "Mentor profile completeness check: Mentor profile not found — needs investigation"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-708
sentry:
  - SC-SAAS-FRONTEND-C4
repos: [frontend]
commit: none — investigation inconclusive, no fix applied
created: 2026-09-08
updated: 2026-09-08
---

# SAN-708 — mentor profile completeness check, investigation inconclusive

## Investigation
Backend-issued business message (`getIndividualInvestorCompleteness( Mentor profile not found... )`) reaching the client via the completeness-check service call. Could be **ENV/DATA** (this user's mentor record genuinely doesn't match — expected behavior) or **CODE_ERROR** (a lookup doing exact/case-sensitive name matching that should be more lenient, or a race where the completeness check fires before the mentor record is created). Single occurrence, insufficient signal to classify confidently within this session.

No code change made.

## Recommendation
Trace the `getIndividualInvestorCompleteness` call site (likely `mentors.service.ts` / `individual-profile.service.ts`) and the backend mentor-lookup it hits in a follow-up session, ideally with the affected account's data available to check for a genuine mismatch vs. a lookup defect.

## Blast radius
None — no change made.

## Confidence note
Low confidence; documented as an open question.
