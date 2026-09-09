---
id: SAN-480
title: Duplicate label "later value overwrites earlier" — 9 Sentry issues, old JS in production
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-480
sentry:
  - SC-SAAS-BACKEND-M
  - SC-SAAS-BACKEND-J
  - SC-SAAS-BACKEND-H
  - SC-SAAS-BACKEND-S
  - SC-SAAS-BACKEND-W
  - SC-SAAS-BACKEND-R
  - SC-SAAS-BACKEND-T
  - SC-SAAS-BACKEND-V
  - SC-SAAS-BACKEND-1E
repos: [backend]
commit: covered by SAN-453 @ sc-saas-backend (already in ai_native_setup_aman)
created: 2026-08-21
updated: 2026-08-21
---

# SAN-480 — 9 "duplicate label" Sentry issues are old JS in production

## Root cause
All 9 Sentry issues show the OLD log message format:
```
duplicate label "X" — later value overwrites earlier
```
SAN-453 changed this message to:
```
duplicate label "X" has conflicting values — keeping first
```
The different message pattern is conclusive: the old compiled JS bundle is still running in production. No new TS source fix is needed — the code is already correct.

## Resolution
**No code change required.** Deploy the `ai_native_setup` branch to production. The SAN-453 fix in `user.service.ts:1361-1368` is already committed. After deploy, all 9 Sentry issues (SC-SAAS-BACKEND-M/J/H/S/W/R/T/V/1E) will stop firing with the old message.

## Action for Aman
Trigger a production deploy of `ai_native_setup`. After deploy, manually resolve the 9 Sentry issues above.

## Blast radius
None — code already fixed; this is a deploy-only resolution.
