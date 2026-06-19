---
description: Summarize what's in flight across all 4 repos' current branches (uncommitted + recent changes)
argument-hint: "[optional: since=<git-ref> or a repo name to focus]"
---

Summarize the work currently in flight across the four SanchiSaaS repos. Focus: $ARGUMENTS

For EACH repo (`sanchiconnect-saas-tenants`, `sc-saas-backend`, `sc-saas-frontend`, `sc-saas-admin`), run (read-only) inside that repo:
- `git -C <repo> rev-parse --abbrev-ref HEAD` (current branch)
- `git -C <repo> status --short` (uncommitted/staged)
- `git -C <repo> --no-pager log --oneline -10` (recent commits)
- `git -C <repo> --no-pager diff --stat` and `git -C <repo> --no-pager diff --stat --cached`

If `$ARGUMENTS` names a repo, only do that one. If it contains `since=<ref>`, also show `git -C <repo> --no-pager log --oneline <ref>..HEAD`.

Then produce, per repo: branch, a 2–4 line summary of what's changing, and the files touched (grouped by module). 

Finally, a **cross-repo flag**: if changes in one repo touch a flag name, a controller/DTO, or auth, call out which other repos likely need a matching change (cite invariants 1–4 from the constitution) and recommend `/trace-flag`, `/audit-contract`, or `/cross-repo-review`. Keep the whole thing scannable.
