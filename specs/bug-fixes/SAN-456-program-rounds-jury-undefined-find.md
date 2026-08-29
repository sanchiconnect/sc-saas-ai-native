---
id: SAN-456
title: TypeError — undefined.find in ProgramStartupRoundsRepository.archiveProgramRoundsJury (13 events)
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-456
sentry:
  - SC-SAAS-BACKEND-1S
repos: [backend]
commit: already in codebase (program-startup-rounds.repository.ts — TypeORM find + null guard)
created: 2026-08-20
updated: 2026-08-21
---

# SAN-456 — undefined.find in archiveProgramRoundsJury

## Root cause
Old production JS called `Array.prototype.find` on a possibly-undefined value in `archiveProgramRoundsJury`. Was a known prior incident (SAN-349/SAN-253).

## Fix
Already in the TypeScript source: uses TypeORM `juryRepo.find({ where: ... })` (not Array.prototype.find), plus a null/empty guard at line 397 (`if (!records || records.length === 0) return`). Runs inside a DB transaction so a crash rolls back cleanly.

## Blast radius
None — program-management internal, no API contract change.

## Verification
No code change required. Fix rides with next production deploy of `ai_native_setup`. Sentry issue SC-SAAS-BACKEND-1S resolved.
