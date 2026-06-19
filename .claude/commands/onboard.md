---
description: Summarize the SanchiSaaS platform for a new contributor (reads the constitution + all 4 per-repo CLAUDE.md)
---

You are onboarding a new contributor to the **SanchiSaaS** poly-repo.

Read, in this order:
1. The workspace constitution: `CLAUDE.md` (this directory's parent).
2. Each per-repo memory: `sanchiconnect-saas-tenants/CLAUDE.md`, `sc-saas-backend/CLAUDE.md`, `sc-saas-frontend/CLAUDE.md`, `sc-saas-admin/CLAUDE.md`.

Then produce a concise onboarding brief, no more than ~40 lines:
- **What the platform is** and the role of each of the four repos (one line each).
- **The blast-radius / dependency direction** (tenants → backend → {frontend, admin}) in plain words.
- **The 5 cross-repo invariants** as a numbered list, each one line.
- **Run commands** per repo (dev / build / test / lint) as a compact table.
- **The cross-repo commands available** (`/trace-flag`, `/audit-contract`, `/check-isolation`, `/cross-repo-review`, `/plan-feature`) and when to reach for each.
- **Top 3 gotchas** a newcomer will hit first.

Do not invent anything not in the memory files. If something important is missing from them, say so explicitly as a gap.
