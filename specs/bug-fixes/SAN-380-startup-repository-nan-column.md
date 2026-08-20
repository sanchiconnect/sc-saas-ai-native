---
id: SAN-380
title: "Unknown column 'NaN' — unvalidated industryDomainPrimaryIds interpolated unquoted into raw SQL"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-380
sentry:
  - SC-SAAS-BACKEND-B
repos: [backend]
commit: sc-saas-backend@1e2a23ea (branch ai_native_setup_aman)
created: 2026-08-19
updated: 2026-08-19
---

# SAN-380 — Unknown column 'NaN' in searchStartupOrLiveDeal

## Root cause
`industryDomainPrimaryIds` is an unvalidated query-string param (`StartupOrLiveDealSearchDto`, only `@IsOptional()`), split on `,` and mapped through `Number()` with no NaN check, then interpolated **unquoted** directly into a raw SQL fragment in `startup.repository.ts` (`searchStartupOrLiveDeal`): `` `startups.startupIndustryPrimaryId =${technologyDomainId}` ``. A request like `?industryDomainPrimaryIds=abc` produces `...=NaN` — MySQL has no NaN literal, parses it as a bareword column → `Unknown column 'NaN'`. Confirmed via workspace-wide grep this is the one unquoted numeric interpolation in the whole search path (sibling filters use quoted `JSON_CONTAINS`, so bad input there silently mismatches instead of crashing). This is also a SQL-injection-shaped pattern (unvalidated input concatenated into raw SQL), currently only exploitable as a DoS since the field is numeric-only.

## Fix
Filtered out non-finite values before use, and switched from raw string interpolation to a parameterized query (`:industryDomainPrimaryId{index}` named params).

## Blast radius
None — confirmed no param-name collisions with the other named params used in the same query-builder method (`:name`, `:productStageIds`, `:fundingStageIds`, `:revenueStage`, `:cityId`, `:stateId`, `:countryId`). Verified the empty-Brackets edge case (all input filtered out as non-finite) produces TypeORM's own `1=1` literal, not invalid SQL — confirmed by reading the installed TypeORM `QueryBuilder.js` source. Query-shape bug only, doesn't read/write cross-tenant data.

Flagged separately (not fixed here): sibling unquoted interpolations nearby (`partnerId`/`StakeholderApprovalType`, lines ~1086-1104) aren't user-controlled today but share the same pattern — worth the same audit later.

## Verification
`tsc --noEmit` clean; `npm run build` clean; lint on this file shows only pre-existing unused-import warnings, 0 errors.
