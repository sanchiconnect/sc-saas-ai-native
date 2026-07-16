---
description: Fix a bug (or ship a small, self-contained enhancement) with lightweight Linear tracking — no spec ceremony.
argument-hint: <short description of the bug/enhancement>
---
$ARGUMENTS

1. Create a Linear issue in the Sanchiconnect team backlog (no project — this is flat, single-issue tracking) titled from the description, state Todo. Move it to In Progress before starting work.
2. Investigate and fix directly in the affected repo(s) — no spec file required for a narrowly-scoped, single-repo change. If it turns out to span multiple repos, touch a feature flag, change an API contract, or need real design/acceptance-criteria work, stop and suggest `/spec-new` instead — don't keep going as a bug fix.
2a. Before writing a fix, classify the failure as one of: **CODE_ERROR** (the code doesn't do what it's supposed to — the common case), **SPEC_ERROR** (the code does what was asked, but the requirement/expectation itself was wrong or ambiguous — flag this back to the user rather than silently "fixing" intended behavior), or **ENV_ERROR** (config, environment, or a third-party dependency, not the code). Only proceed straight to a code fix for CODE_ERROR; for the other two, say so explicitly before touching anything.
3. If the fix was a CODE_ERROR and lands in a repo with a working test framework (`sanchiconnect-saas-tenants`, `sc-saas-backend`, `sc-saas-3rdparty-webservices` — NestJS/Jest; `sc-saas-frontend` — Angular), propose a regression test covering this specific bug — say what it will assert and which file it goes in — and **wait for the user's go-ahead before writing it**. Do not write the test until confirmed. Skip this step (and say so) for `sc-saas-admin` and `sanchiconnect-saas-tenants-admin` (no test framework exists) and `ai-startups-analyzer` (no test suite set up yet) — note the gap rather than bootstrapping test infrastructure as a side effect of a bug fix.
4. Run the affected repo's own lint/check (`php -l`, `npm run lint`, `tsc --noEmit`, etc.) on every touched file, including any new test file.
5. Once the fix is ready, add a short comment to the Linear issue summarizing the root cause and the fix, and move it to In Review (or Done, only if the user has you commit/merge directly). Use the Sanchiconnect team's real states only (Backlog/Todo/In Progress/In Review/Done/Canceled/Duplicate).
