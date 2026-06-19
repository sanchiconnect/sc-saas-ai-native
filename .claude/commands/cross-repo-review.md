---
description: Review the current diff across all affected repos against the 5 cross-repo invariants before opening PRs
argument-hint: "[optional: repo name or git-ref to scope the diff]"
---

Review the pending changes across the SanchiSaaS poly-repo for cross-repo correctness **before PRs are opened**. Scope: $ARGUMENTS

Delegate to the `cross-repo-reviewer` subagent so the diff-reading happens in a separate context. Tell it to:

1. Collect the diff in each repo (`git -C <repo> --no-pager diff` and `--cached`; if `$ARGUMENTS` is a ref, diff against it). If `$ARGUMENTS` names one repo, still check the OTHER repos for consumers that the diff affects.
2. Check the changes against the 6 invariants in the workspace `CLAUDE.md`:
   - (1) flag names owned by `tenants` — any added/renamed/removed flag must propagate to backend `Feature` enum, frontend `IFeatures`, admin `config.php`.
   - (2) API contract owned by `sc-saas-backend` — any controller/DTO change must be reflected in frontend `core/service/*` and admin cURL callers.
   - (3) tenant-verification shape owned by `tenants` (`verify_tenant`/`tenant-settings`, incl. `apiUrl`).
   - (4) auth (JWT) — token attachment/session changes ripple to all clients.
   - (5) tenant scoping — every new query/endpoint enforces the per-repo scoping rule.
   - (6) cross-workspace PowerPitch contract — any change to `sc-saas-backend/src/core/services/power-pitch-external.service.ts` or to `power-pitch-sanchiconnect-api/src/modules/external/` must be coordinated across both workspaces.
3. Return findings as a table: severity (BLOCKER / WARN / NIT), repo, file:line, the invariant at risk, and the concrete fix. End with a go / no-go for opening PRs.

Report the subagent's findings verbatim, then add a one-line recommendation.
