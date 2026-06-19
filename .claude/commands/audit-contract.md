---
description: Audit the backend API contract for drift against the frontend and admin consumers (stale calls, shape drift)
argument-hint: "[optional: module/controller or changed files to scope the audit]"
---

Audit the SanchiSaaS API contract. Scope: $ARGUMENTS (if empty, sample the most-used controllers).

Delegate to the `api-contract-auditor` subagent. Tell it to treat `sc-saas-backend` controllers/DTOs as the source of truth and detect drift in `sc-saas-frontend` (`core/service/*` + `api-endpoint.service.ts`) and `sc-saas-admin` (cURL in `includes/*`). Ask for a drift table (stale call / shape drift / unconsumed) with backend + consumer file:line and the fix. Report verbatim, then one line: contract healthy or N drifts.
