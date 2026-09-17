---
id: SAN-562
title: Uncaught HTTP failure (status 0) on application-programs-management code lookup
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-562
sentry:
  - SC-SAAS-FRONTEND-2M
repos: [frontend]
commit: sc-saas-frontend@61777951 (branch ai_native_setup_vishali, not pushed)
created: 2026-09-03
updated: 2026-09-03
---

# SAN-562 — uncaught HTTP failure on application-programs-management/code

## Root cause
`application-program-management-dynamic-form.component.ts`'s `checkProgramStatus()` called `PublicApiService.fetchApplicationProgramsManagement()` via a bare `await ... .toPromise()` with no try/catch — the same anti-pattern already fixed once in this same file's `initiateParticipation()` under SAN-510. A network failure (status 0) surfaced as an uncaught promise rejection instead of a handled error.

## Fix
Wrapped the `await .toPromise()` in try/catch (mirroring the SAN-510 pattern/comment), logging via `console.error` on failure and leaving `programClosed` unchanged instead of throwing.

## Blast radius
None — additive error handling only; happy path unchanged.

## Verification
`npx tsc -p tsconfig.json --noEmit` clean.

## Related
Same file/anti-pattern as SAN-510 ("initiateParticipation() unguarded await .toPromise() — 64 users").
