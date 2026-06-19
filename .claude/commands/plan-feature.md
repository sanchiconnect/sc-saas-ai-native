---
description: Produce a per-repo change plan for a feature (which repos, modules, contract/flag impacts, migrations, tests) — no code
argument-hint: "<feature description>"
---

Plan the feature below across the SanchiSaaS poly-repo. **Do not write any code** — produce a plan only.

Feature: $ARGUMENTS

First read the workspace `CLAUDE.md` and any per-repo `CLAUDE.md` you'll touch. Then explore (read-only) the relevant modules to ground the plan in real files.

Produce:
1. **Summary** — one paragraph: what the feature does and which of the four repos it touches, in blast-radius order (tenants → backend → frontend → admin).
2. **Per-repo plan** — for each affected repo: the modules/files to change, new endpoints/DTOs or flag columns, and the specific functions/components involved (cite real paths).
3. **Contract & flag impact** — does it add/rename a flag? (→ which repos must mirror it.) Does it change the API contract? (→ which consumers update.) Reference invariants 1–5.
4. **Migrations / data** — schema changes (tenants `tenant_users` columns, backend entities, admin tenant DB), and whether they are backward-compatible across independently-deployed repos.
5. **Sequencing** — because repos deploy independently, the safe order to ship (e.g., add flag default-off in tenants first, then backend gate, then frontend UI, then enable).
6. **Test plan** — per repo, what to test (jest / karma / manual), plus the cross-repo smoke check.
7. **Open questions** — anything ambiguous to confirm before coding.

Keep it tight and decision-ready.
