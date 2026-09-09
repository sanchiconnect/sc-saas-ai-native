---
id: SAN-597
title: s.replace is not a function (sanitizeInput) — already fixed in code, still firing 15 days later
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-597
sentry:
  - SC-SAAS-FRONTEND-C9
  - SC-SAAS-FRONTEND-CA
repos: [frontend]
commit: none — no code defect found, see Investigation
created: 2026-09-04
updated: 2026-09-04
---

# SAN-597 — sanitizeInput already fixed, deploy/cache check needed

## Investigation — code is already correct
`FormFieldComponent.sanitizeInput()` / `.sanitizeScriptTagsInput()` (`form-field.component.ts:214-232`) already have the fix for this exact bug class (`typeof value === 'string' &&` guard before `.replace()`), landed in commit `c0638d20` (2026-08-19, "fix: resolve 16 Sentry production errors", SAN-364/365/367/370/377) — verified present in the current working tree via direct file read and `git show c0638d20`. Searched the entire `dynamic-forms` module tree for any other unguarded `.replace()` call on a form-control value — none found.

C9/CA's first-seen (2026-09-03) is 15 days after that fix landed. This is the **third** instance found this session of a Sentry issue still showing recent events well after its code fix landed (also SC-SAAS-FRONTEND-2A, fixed 2026-08-20 by SAN-471, and SC-SAAS-FRONTEND-3S, fixed 2026-08-25 by SAN-512/513) — a recurring pattern, not a one-off.

## Likely cause — not a code fix
This repo's own CLAUDE.md documents exactly this gotcha: "a service-worker cache can hide deploys — hard-refresh / bump SW to verify (`ngsw-config.json`)." Recommend checking:
1. Whether `sc-saas-frontend` prod is actually running a build that includes `c0638d20` (and SAN-471/SAN-512/513).
2. Whether affected users' browsers are serving a stale cached bundle via the Angular service worker.

## Fix
None applied — no code defect exists to fix. Ticket exists to record the investigation and flag the deploy/cache question, per explicit request to track every checked issue rather than silently closing it as untracked.

## Related
SC-SAAS-FRONTEND-2A (SAN-471), SC-SAAS-FRONTEND-3S (SAN-512/513) — same "already fixed, still firing" pattern.
