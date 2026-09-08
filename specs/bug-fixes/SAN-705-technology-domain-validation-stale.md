---
id: SAN-705
title: "Technology domain required — no client-side validation before submit (Sentry noise)"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-705
sentry:
  - SC-SAAS-FRONTEND-CN
repos: [frontend]
commit: none — already fixed, see Investigation
created: 2026-09-08
updated: 2026-09-08
---

# SAN-705 — technology domain required, already client-side guarded

## Investigation
`industry-technology.component.ts` already has `isTechSelected`/`isIndustrySelected` getters feeding a `saveButtonDisabled` getter, and both the Save button and the "Next" step button in the template are `[disabled]="saveButtonDisabled"` (`industry-technology.component.html:196-197, 213-214`) — the form cannot be submitted with zero technology domains selected through the UI today. This validation predates the Sentry event by a long margin (added in commit `6f0a125a`, April 2025).

Sentry event carried `environment: local`, `release: sc-saas-frontend@unknown` — consistent with a stale/local test session, not a current-code gap.

No code change made.

## Blast radius
None.

## Verification
Read `industry-technology.component.ts` + template; confirmed `saveButtonDisabled` gating on both the Save and Next buttons; confirmed via `git show` that the gating commit (`6f0a125a`) long predates this event.

## Related
[[SAN-704]] (same class, elevator pitch form).

## Confidence note
Medium-high confidence, same caveat as SAN-704 — no live repro available.
