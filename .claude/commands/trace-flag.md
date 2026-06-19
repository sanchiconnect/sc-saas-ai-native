---
description: Trace a feature flag from its definition in tenants to every consumer in backend, frontend, and admin (+ orphans)
argument-hint: "<flag-name (snake_case)>"
---

Trace the feature flag `$ARGUMENTS` across all four SanchiSaaS repos.

Delegate to the `feature-flag-mapper` subagent. Pass it the flag name `$ARGUMENTS` and ask for: the definition site + default in `sanchiconnect-saas-tenants`, every read site in `sc-saas-backend` / `sc-saas-frontend` / `sc-saas-admin`, and any orphans (defined-but-unused, used-but-undefined). Report its findings verbatim, then one line: is this flag fully wired across the platform?
