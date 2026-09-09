---
id: SAN-465
title: getNews/getCategories external service failures flooding Sentry (3 issues)
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-465
sentry: []
repos: [backend]
commit: sc-saas-backend@2e01d244 (branch ai_native_setup_aman)
created: 2026-08-20
updated: 2026-08-21
---

# SAN-465 — news service catch blocks flooding Sentry

## Root cause
`getNews()` and `getCategories()` in `news.service.ts` already had graceful degradation (try/catch, return empty results). Sentry noise came from `logger.error()` in the catch blocks — `CaptureConsole({ levels: ['warn', 'error'] })` in `instrument.ts` forwards these to Sentry on every transient news server hiccup.

Both functions are called via `Promise.all` alongside report downloads and webinars in `DashboardService.getDashboardContent()` — a news timeout previously also cascaded and was caught here, then logged as error.

## Fix
Downgraded `logger.error` → `logger.debug` in both catch blocks (`news.service.ts:100` and `:143`). Graceful degradation behavior (return empty results) unchanged.

## Blast radius
None — logging change only; empty-result fallback behavior unchanged.

## Verification
`tsc --noEmit --skipLibCheck` clean. Committed `2e01d244`.
