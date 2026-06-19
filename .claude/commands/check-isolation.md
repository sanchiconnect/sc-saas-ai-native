---
description: Scan the tenant-scoped repos for data access that doesn't enforce the tenant/workspace scoping rule
argument-hint: "[optional: repo name or changed files to scope the scan]"
---

Scan for tenant-isolation risks across SanchiSaaS. Scope: $ARGUMENTS (if empty, sweep repositories/services).

Delegate to the `tenant-isolation-reviewer` subagent. Remind it of the per-repo rule: `tenants` filters every tenant-owned query by `domain`; `admin` must use the per-request tenant DB (`$database`), not the main DB, for tenant data; `sc-saas-backend` is one-deployment-per-tenant so it should NOT have per-query scoping — flag hardcoded hosts / cross-tenant config / tenant data in process-globals instead. Ask for a findings table (likely-leak / needs-verification / OK) with file:line and fix. Report verbatim, then one line: isolation holds or N risks.
