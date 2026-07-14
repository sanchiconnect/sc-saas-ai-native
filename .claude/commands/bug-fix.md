---
description: Fix a bug (or ship a small, self-contained enhancement) with lightweight Linear tracking — no spec ceremony.
argument-hint: <short description of the bug/enhancement>
---
$ARGUMENTS

1. Create a Linear issue in the Sanchiconnect team backlog (no project — this is flat, single-issue tracking) titled from the description, state Todo. Move it to In Progress before starting work.
2. Investigate and fix directly in the affected repo(s) — no spec file required for a narrowly-scoped, single-repo change. If it turns out to span multiple repos, touch a feature flag, change an API contract, or need real design/acceptance-criteria work, stop and suggest `/spec-new` instead — don't keep going as a bug fix.
3. Run the affected repo's own lint/check (`php -l`, `npm run lint`, `tsc --noEmit`, etc.) on every touched file.
4. Once the fix is ready, add a short comment to the Linear issue summarizing the root cause and the fix, and move it to In Review (or Done, only if the user has you commit/merge directly). Use the Sanchiconnect team's real states only (Backlog/Todo/In Progress/In Review/Done/Canceled/Duplicate).
