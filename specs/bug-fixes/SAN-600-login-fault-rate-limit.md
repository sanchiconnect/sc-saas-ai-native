---
id: SAN-600
title: "loginFault(rate limit reached) re-thrown to Sentry — 23 users, 28 events"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-600
sentry:
  - SC-SAAS-FRONTEND-4K
repos: [frontend]
commit: sc-saas-frontend@4e4bd3cb (branch ai_native_setup_vishali, pushed)
created: 2026-09-04
updated: 2026-09-04
---

# SAN-600 — loginFault(rate limit reached) re-thrown to Sentry

## Investigation — not a code defect
`AuthService.login()`'s `catchError` block `console.warn`s this fault; it doesn't toast itself, but `login.component.ts`'s own error subscription does — the error is fully handled end-to-end by the caller. The `console.warn` was the source of the duplicate Sentry report, same pattern as SAN-599/601/608 and the earlier SAN-504 fix.

## Fix
Same `main.ts:109` `HANDLED_HTTP_FAULT` regex extension as SAN-599/601/608 — added this fault's exact message text so it's dropped by `beforeSend` instead of double-reported.

## Blast radius
None. Login error handling and the rate-limit itself are untouched — only Sentry noise is reduced. No evidence found that the rate limit is being mistriggered by app-side retry/polling behavior (checked `login.component.ts` for retry loops — none present).

## Verification
`npx tsc --noEmit` clean.

## Related
SC-SAAS-FRONTEND-2Q (SAN-599), SC-SAAS-FRONTEND-3H (SAN-601), SC-SAAS-FRONTEND-34 (SAN-608) — same fix, same commit.
