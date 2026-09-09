---
id: SAN-460
title: ECOSYSTEM_PUSH_FAILED_ON_APPROVE — tenants API returning 500 for batch with bad record (30 events)
type: bug-fix
status: in-progress
linear: https://linear.app/sanchiconnect/issue/SAN-460
sentry: []
repos: [backend, tenants]
commit: already in codebase for sc-saas-backend (warn→debug). Tenants-side root 500 pending investigation.
created: 2026-08-20
updated: 2026-08-21
---

# SAN-460 — Ecosystem push 500 / Sentry noise

## Root cause — two parts

**1. Sentry noise (sc-saas-backend):** All 8 `ECOSYSTEM_PUSH_FAILED_ON_APPROVE` log calls in `admin-actions.service.ts` used `logger.warn` → forwarded to Sentry by `CaptureConsole`. Already fixed in TypeScript source (warn→debug). Stops Sentry noise after next deploy.

**2. Root 500 (sanchiconnect-saas-tenants):** `ecosystem.service.ts:169` POSTs ALL approved startups in one batch to the tenants API. Startup ID 257 (or investor 14 / individual 4) causes the tenants API to return 500. The batch is all-or-none — one bad record blocks ecosystem sync for every approval. The backend approval itself still succeeds (best-effort try/catch).

## Action required (Aman)
Investigate `sanchiconnect-saas-tenants/src/modules/ecosystem/` — check what data from startup ID 257, investor ID 14, or individual ID 4 causes the tenants API to return 500. May be a malformed field that fails tenants-side validation.

## Blast radius
Ecosystem directory is not updated on every approval until root 500 is fixed.

## Verification
sc-saas-backend code fix: already in TS source, no new commit. Tenants investigation: pending.
