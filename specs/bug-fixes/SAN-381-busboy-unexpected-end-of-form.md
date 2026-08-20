---
id: SAN-381
title: busboy client-abort classified as unhandled 500 instead of 400
type: bug-fix
status: superseded
linear: https://linear.app/sanchiconnect/issue/SAN-381
sentry:
  - SC-SAAS-BACKEND-Q
repos: [backend]
commit: sc-saas-backend@1e2a23ea (branch ai_native_setup_aman)
created: 2026-08-19
updated: 2026-08-20
---

# SAN-381 — busboy "Unexpected end of form" reclassification

## Root cause
Busboy throws a plain `Error` (no `.status` property) whenever a client aborts/disconnects mid-multipart-upload — a normal client-side event, not a server defect. `GlobalExceptionFilter` is a catch-all that defaults anything without a recognized `.status` to 500 and unconditionally sends it to Sentry.

Verified against the raw production Sentry event, which captured the exact deployed source line: `/app/node_modules/busboy/lib/types/multipart.js:588:17 (Multipart._final): return cb(new Error('Unexpected end of form'));`. This also revealed that this repo's own `package-lock.json` pins `busboy@0.2.14` (via multer's `^0.2.11` range), whose actual abort message is the different string `'Unexpected end of multipart data'` — **production runs a materially newer busboy than what this repo's lockfile resolves to**, a separate dependency-drift issue.

## Fix
Added a check in `global-exception.filter.ts` reclassifying both `'Unexpected end of form'` (confirmed production string) and `'Unexpected end of multipart data'` (this repo's locked version's string) as HTTP 400 before the `statusCode >= 500` Sentry-capture branch.

## Superseded — 2026-08-20 (SAN-404)
This fix did not fully resolve the issue in production: busboy's abort error can surface as a **raw Node-level uncaught exception** under some busboy/multer version combinations, which bypasses `GlobalExceptionFilter` entirely (that filter only catches exceptions flowing through NestJS's own request pipeline) and is captured directly by `@sentry/node`'s default uncaught-exception/unhandled-rejection integrations instead. SAN-404 fixed this properly at the Sentry SDK level (`instrument.ts`'s `beforeSend` hook), which catches the error regardless of capture path. See `specs/bug-fixes/SAN-404-busboy-unexpected-end-of-form.md`.

## Blast radius
None — auth/guard model unaffected; the reclassification only changes Sentry-reporting behavior and the HTTP status code for this exact error message.

## Verification
`tsc --noEmit` clean; `npm run build` clean; lint on this file shows only pre-existing unused-import warnings, 0 errors.
