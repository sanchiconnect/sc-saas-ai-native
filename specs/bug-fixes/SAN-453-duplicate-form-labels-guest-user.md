---
id: SAN-453
title: Duplicate form labels in getProfileDataByEmailOfGuestUser — 14 Sentry issues (~1000+ events)
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-453
sentry: []
repos: [backend]
commit: already in codebase (user.service.ts:1361-1368 — first-non-empty-wins)
created: 2026-08-20
updated: 2026-08-21
---

# SAN-453 — Duplicate form label data loss in guest user profile

## Root cause
Old production code used "last value wins" — a later duplicate label silently overwrote an earlier value (data loss). 14 Sentry issues all showed the OLD message `duplicate label "X" — later value overwrites earlier`, confirming the old JS build was in production.

## Fix
Already in the TypeScript source at `user.service.ts:1361-1368`: "first non-empty value wins" — duplicate labels are detected, a warning is logged, and the first non-empty value is preserved. Current code emits `duplicate label "X" has conflicting values — keeping first`.

## Blast radius
None — internal user-service helper, no API contract change.

## Verification
No code change required. Fix rides with next production deploy of `ai_native_setup`. All 14 related Sentry issues resolved.
