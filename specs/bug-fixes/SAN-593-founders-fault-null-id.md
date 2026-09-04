---
id: SAN-593
title: foundersFault( Cannot read properties of null (reading 'id') ) — unguarded fault.error.message + unconfirmed upstream origin
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-593
sentry:
  - SC-SAAS-FRONTEND-BN
repos: [frontend]
commit: sc-saas-frontend@e83ac158 (branch ai_native_setup_vishali, pushed)
created: 2026-09-04
updated: 2026-09-04
---

# SAN-593 — foundersFault null id

## Root cause
No stacktrace was attached to this Sentry event (level `warning`, logger `console` — a plain `console.warn` capture, not a caught exception object), so the message text is the only lead. It's the literal value of `fault.error.message` from `FoundersService.getFounders()`'s `catchError` (`founders.service.ts:32-35`, before fix). Because the string reads like a raw JS `TypeError` message rather than a normal API validation message, the backend's error response body may itself contain a leaked, unhandled server-side exception (a `sc-saas-backend` issue, not confirmed).

Checked the full backend founders path (`sc-saas-backend/src/modules/startup/founder/startup-founder.service.ts` and `repositories/startup-founder.repository.ts`) for an unguarded `.id` read — both are fully null-guarded. Exact origin **not conclusively identified**.

## Fix applied (confirmed-safe hardening, not a root-cause fix)
`founders.service.ts:33` and its exact copy-pasted sibling `advisoryBoard.service.ts:33` both read `fault.error.message` with no optional chaining, inconsistent with every other `catchError` in the same two files. Fixed both to `fault?.error?.message` to match the established sibling-method convention.

## Blast radius
None — purely defensive; only changes behavior when `fault.error` is null, which previously crashed.

## Verification
`npx tsc -p tsconfig.json --noEmit` clean on both changed files. No automated test suite exists for this repo.

## Open item
Backend root cause not confirmed. If this recurs, check `sc-saas-backend` application/error logs around the event dates (2026-08-30/31) for a raw exception leaking into the founders-list response body.
