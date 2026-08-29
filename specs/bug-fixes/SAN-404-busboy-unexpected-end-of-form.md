---
id: SAN-404
title: "\"Unexpected end of form\" (busboy) still reaching Sentry despite prior fix"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-404
sentry:
  - SC-SAAS-BACKEND-Q
repos: [backend]
commit: sc-saas-backend@d9ec7f0a (branch ai_native_setup_aman)
created: 2026-08-20
updated: 2026-08-20
---

# SAN-404 — busboy client-abort events bypassing the exception filter

## Root cause
`global-exception.filter.ts` already reclassifies `'Unexpected end of form'` / `'Unexpected end of multipart data'` to HTTP 400 and skips `Sentry.captureException` — a prior fix explicitly referencing this same Sentry issue (SC-SAAS-BACKEND-Q). Since it kept recurring (134 occurrences over 16 days), the exception isn't reaching that filter: busboy emits this as a raw stream `'error'` event, which under some busboy/multer version combinations surfaces as a **Node-level uncaught exception**, caught instead by `@sentry/node`'s default `OnUncaughtException`/`OnUnhandledRejection` integrations (`instrument.ts` never disables default integrations) — bypassing the filter's reclassification entirely.

## Fix
`instrument.ts` — extended the existing `scrubEvent`/`beforeSend` hook to drop any Sentry event whose exception message matches these two known client-mid-upload-abort strings, regardless of capture path.

## Blast radius
None — only these two exact, previously-confirmed-benign messages are filtered.

## Verification
`tsc --noEmit` clean; `npm run build` clean; lint shows only pre-existing unrelated warnings. Could not reproduce a live busboy mid-upload abort in this session to confirm the uncaught-exception theory end-to-end — recommend watching the Sentry issue post-deploy; if it recurs, the busboy/multer version mismatch noted in the exception filter's own comment needs a direct dependency-alignment follow-up.
