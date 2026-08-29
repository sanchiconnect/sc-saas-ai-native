---
id: SAN-478
title: QueryFailedError Unknown column 'NaN' — unguarded numeric params across 6 modules (238 events, regressed)
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-478
sentry:
  - SC-SAAS-BACKEND-B
repos: [backend]
commit: pending (branch ai_native_setup_aman)
created: 2026-08-21
updated: 2026-08-21
---

# SAN-478 — QueryFailedError NaN across multiple modules

## Root cause
`mysql2` treats JavaScript `NaN` or `Infinity` as `typeof === 'number'` and renders them as bare unquoted SQL identifiers (`WHERE id = NaN`, `programs.partnerId = Infinity`). MySQL parses these as column references and rejects with `Unknown column 'NaN' in 'field list'`.

SAN-405 fixed this in the `meetings` module. Sentry shows "regressed" because the same class of bug exists in other endpoints. Two sub-patterns found:

**Pattern A — Raw SQL template interpolation (highest risk):** `programs.partnerId = ${partnerId}` in `application-programs.repository.ts`. If `Number(partnerId)` yields `Infinity` (e.g. `?partnerId=Infinity`), the value is truthy, bypasses the `if (partnerId)` guard, and lands directly in unquoted SQL → `Unknown column 'Infinity' in 'field list'`.

**Pattern B — `JSON_CONTAINS` with `.map(Number)` and no `isNaN` guard (5 modules):** `sectoralInterestIds.split(',').map(v => Number(v))` then embedded in `JSON_CONTAINS(col,'${id}')`. If any CSV token is not a valid integer, `Number(token)` yields NaN or Infinity. NaN inside single-quoted JSON produces MySQL error `3140 Invalid JSON value for CAST`. Affects: challenges, mentors, investor (5 filter arrays), startup (technologyDomainIds, industryDomainIds), corporate.

## Files changed

| File | Change |
|------|--------|
| `src/modules/application-management/repositories/application-programs.repository.ts` | Pattern A fix: replaced raw `${partnerId}` with `:partnerId` parameterized binding; added `Number.isFinite(partnerId)` guard |
| `src/modules/challenges/repositories/challenges.repository.ts` | Pattern B: added `.filter(Number.isFinite)` to sectoralInterestIds and challengeCollections arrays |
| `src/modules/mentors/repositories/mentor.repository.ts` | Pattern B: added `.filter(Number.isFinite)` to sectoralInterestIds, domainAreas, technologyDomainIds |
| `src/modules/investor/repositories/investor.repository.ts` | Pattern B: added `.filter(Number.isFinite)` to investmentMechanismIds, investmentPreferenceIds, sectoralInterestIds, investmentStageIds, investAbilityMetricIds |
| `src/modules/startup/repositories/startup.repository.ts` | Pattern B: added `.filter(Number.isFinite)` to technologyDomainIds and industryDomainIds (industryDomainPrimaryIds already had it — the correct pattern) |
| `src/modules/corporate/repositories/corporate.repository.ts` | Pattern B: added `.filter(Number.isFinite)` to sectoralInterestIds |

## Correct pattern (from startup.repository.ts:1143 — already used there)
```ts
param.split(',').map(v => Number(v)).filter(Number.isFinite)
```

## Blast radius
- All filter endpoints (search/listing) for programs, challenges, mentors, investors, startups, corporates: invalid numeric filter tokens are now silently dropped instead of crashing with a 500. This is correct and safe — a non-integer filter token was always meaningless.
- Programs endpoint: `partnerId=Infinity` now returns programs with `partnerId IS NULL` (else branch) instead of a 500.

## Verification
`tsc --noEmit --skipLibCheck` clean. No commit/push until Aman confirms.
