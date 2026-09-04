---
id: SAN-606
title: "startupinfoFault(Startup not found) on supernova.gdai.in — 6 users, 27 events"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-606
sentry:
  - SC-SAAS-FRONTEND-3V
repos: [backend]
commit: sc-saas-backend@93d6359e (branch ai_native_setup_vishali, pushed)
created: 2026-09-04
updated: 2026-09-04
---

# SAN-606 — startupinfoFault(Startup not found) on supernova.gdai.in

## Root cause
`StartupService.getStartupInformation()` looks up a startup by `session.startupId` (from the caller's own JWT — never a user-typed name), and previously threw `NotFoundException(ApiErrors.STARTUP_NOT_FOUND)` when no row was found. That message ("...ensure you have entered the correct startup name") only makes sense for a name/search-based lookup, not a parameterless self-lookup — it's misleading copy for this case, not a query bug. `ApiErrors.STARTUP_PROFILE_NOT_ATTACHED` already exists in `api-error-message.ts` for exactly this "your account has no linked startup profile" condition and is already used by `AuthService.generateAccessToken()` for the same scenario.

Also found (and fixed as a defensive cleanup, not the primary bug): the `if (!startup)` check was ordered *after* the `startup.pitchDeck` access below it — dead code today since the repository call (`getStartupInformationByStartupId()`) already throws `NotFoundException` itself before ever returning a falsy value, but left fragile against a future contract change to that repository method.

## Fix
`startup.service.ts`: swapped `ApiErrors.STARTUP_NOT_FOUND` → `ApiErrors.STARTUP_PROFILE_NOT_ATTACHED` for this self-lookup path, and reordered the null check above the `pitchDeck` access. `ApiErrors.STARTUP_NOT_FOUND` itself was left untouched — it's shared by ~70 other call sites across the codebase, most of which are genuine ID/name lookups where the existing copy still applies.

## Blast radius
Message-text-only change on an already-erroring path; no successful-response shape changed. Grepped `sc-saas-frontend` for hardcoded matches on the old `STARTUP_NOT_FOUND` text — no UI logic branches on the specific wording.

## Verification
Ran the actual backend `startup` module test suite: 20/20 pass.

## Related
SC-SAAS-FRONTEND-3T (SAN-607) — same tenant, same fault class, same commit (`getDashboard()`'s equivalent self-lookup).
