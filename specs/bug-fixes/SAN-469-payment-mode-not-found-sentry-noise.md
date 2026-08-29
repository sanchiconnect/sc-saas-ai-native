---
id: SAN-469
title: Setting "payments_mode" not found in admin settings — Sentry noise (1 event)
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-469
sentry:
  - SC-SAAS-BACKEND-1J
repos: [backend]
commit: sc-saas-backend@2e01d244 (branch ai_native_setup_aman)
created: 2026-08-20
updated: 2026-08-21
---

# SAN-469 — payments_mode not found flooding Sentry

## Root cause
`getPaymentMode()` in `payment-management.service.ts:183` used `logger.error()` when `payments_mode` is missing from admin settings. `CaptureConsole` forwards `error` level to Sentry. The `NotFoundException` itself is correct behavior — it prevents accidental live-mode payments on mis-provisioned tenants.

## Fix
Downgraded `logger.error` → `logger.debug` at line 183. The `NotFoundException` is kept — no unsafe default, no live-mode fallback without explicit configuration.

## Data fix (separate action)
Seed `payments_mode` (`live` or `test`) in admin settings for the affected tenant via the admin panel.

## Blast radius
None — logging change only; NotFoundException still thrown, payment flow behavior unchanged.

## Verification
`tsc --noEmit --skipLibCheck` clean. Committed `2e01d244`.
