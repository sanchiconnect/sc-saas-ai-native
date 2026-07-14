# Spec-Authoring Practices — Lessons from the SpecPod Trial

**Status:** Reference guide, not a process to follow step-by-step.
**Origin:** Distilled from a live trial of `prabs/spec-driven-pod-framework` ("SpecPod"), run against the Bulk Email Attachments feature (`sc-saas-admin/specs/features/bulk-email-attachments/`) in July 2026.

---

## Verdict

Do **not** adopt `prabs/spec-driven-pod-framework` as the working process for this workspace. It is built for a from-scratch, sprint-based "AI-native" build (single fixed stack, AI Builder fleet, HITL sprint gates, production cost/drift/experiment infrastructure) that does not match any of this workspace's seven repos or its incremental, poly-repo delivery model. Use the existing `/spec-new` → `/spec-implement` pipeline for all bug fixes, enhancements, and new feature work, gated by `/audit-contract`, `/trace-flag`, `/check-isolation`, and `/cross-repo-review` as already defined in the workspace `CLAUDE.md`.

The four practices below, however, are worth carrying into that existing pipeline — they were the genuinely good ideas the trial surfaced, independent of the framework itself.

---

## Practice 1 — Check the real code before proposing new entities

**What went wrong in the trial:** left to run unassisted, the framework invented three new database tables (`bulk_emails`, `bulk_email_attachments`, `bulk_email_recipient_logs`) to model a feature whose functionality already existed as `broadcast_messages` and `ses_email_queue` in `sc-saas-admin`. It only produced the correct design after being explicitly redirected to read the real handler (`bulkEmailRoundApplications` in `submission-application-management.php`).

**Practice to adopt:** before `spec-author` (or any spec-generation step) proposes a new table, entity, endpoint, or mechanism, it must first search the target repo for an existing equivalent — by feature name, by the nearest existing controller/handler, and by grep for related terms — and cite what it found (or confirm nothing exists) before proposing anything new. This is not optional for live, mature repos; assume prior art exists until proven otherwise.

---

## Practice 2 — Ask before guessing, don't guess and flag later

**What worked in the trial:** two of SpecPod's skills (`spec-design`, `spec-uiux`) have a mandatory first step — ask the user whether a reference document exists (design preferences, UX reference) *before* generating anything, rather than silently inferring and hoping.

**Practice to adopt:** any spec step that would otherwise have to guess at a design/UX/architecture preference should ask first, once, with a direct yes/no question, before generating content. If the answer is no, proceed with full inference — but only after asking.

---

## Practice 3 — Tag every claim by evidence strength

**What worked in the trial:** every non-trivial statement in a generated spec was tagged as one of:
- Evidenced (cited directly to a source document or a `file:line` in the real codebase)
- `[INFERRED — requires validation]` (a reasonable extrapolation, not directly stated)
- `[NOT SPECIFIED IN SOURCE]` (a real gap — no source states this either way)
- `[DESIGN DECISION PENDING]` (a genuinely new decision with no precedent to ground it in)

**Practice to adopt:** carry this tagging convention into specs produced by `spec-author` for any bug fix, enhancement, or new feature. It makes it immediately obvious to a reviewer which parts of a spec are safe to build from and which need a human decision first — this was the single most useful stylistic habit the trial produced, and it costs nothing to keep.

---

## Practice 4 — Name the cross-repo contract impact explicitly

**What worked in the trial:** when the Bulk Email Attachments feature turned out to require a change to `sc-saas-backend`'s `v1/admin-actions/broadcast-ceo-message` endpoint (not just `sc-saas-admin`), the spec called this out in its own named section — showing the current contract, the exact requested change, and which gate (`/audit-contract`) must run before implementation.

**Practice to adopt:** this workspace's `CLAUDE.md` already requires this (invariant #2 and the `/audit-contract` command exist for exactly this reason) — the trial simply confirmed that naming the affected contract *inside the spec itself*, not just as a follow-up step, makes it much harder for a cross-repo change to get missed during implementation. Any spec produced by `/spec-new` that touches more than one repo should include an explicit "Cross-Repo Contract Impact" section, not leave it implicit in the `repos:` frontmatter field alone.

---

## What was deliberately not adopted

- The 15-prompt NEXT/CONFIRM ceremony per Phase 1 skill — too slow for routine work; reasonable only for a large, novel, high-stakes build where the extra rigor is worth the time cost.
- All of Phases 2–5 (52 of the framework's 67 prompts) — sprint-board orchestration, AI Builder fleet code generation, HITL gate machinery, production cost/drift/experiment tooling. None of it matches this workspace's stack (legacy PHP, NestJS, Angular, FastAPI-for-AI-only) or delivery model (independently-deployed, continuously-evolving repos, not sprint-boxed greenfield builds).
- The framework's own skill catalog and skill-generation machinery (`SkillFlow`, `skill-generator`) — meta-tooling for extending the framework itself, not applicable here.

---

## Linear Tracking — standing practice

Every bug fix, requirement implementation, and enhancement should have a corresponding Linear record so work state (Backlog / Todo / In Progress / In Review / Done / Canceled) is always visible — not just tracked in local spec files.

**Team:** Sanchiconnect (id `9e9df5bf-10ce-452a-ae21-aea4ab9f8adf`) — the only team in this Linear workspace.

**Structure:**
- **Feature/initiative-scale work** (anything that would get its own `/spec-new` spec — a new capability, a multi-repo change, anything with real design surface) → create a **Linear Project** for it, with one issue per meaningful piece of work under that project.
- **Bug fixes and small, self-contained enhancements** → a flat issue in the Sanchiconnect team backlog, no project. Still gets created and moved through states — just without a project wrapper.

**States (Sanchiconnect team's real workflow, confirmed via `list_issue_statuses`):** `Backlog` → `Todo` → `In Progress` → `In Review` → `Done` (plus `Canceled` / `Duplicate` as needed). Move the issue as work actually progresses — don't create it and leave it stale in `Todo` while work is really `In Progress`.

**When to create the issue:** at the point work is confirmed to start (not necessarily at the first mention of an idea) — mirrors the existing `/from-linear` command's direction (pulling work *from* Linear into a spec); this is the reverse flow, pushing tracked work *back into* Linear as it happens.

---

## Worked example

`sc-saas-admin/specs/features/bulk-email-attachments/` (`program.md`, `knowledge.md`, `design.md`, `ui-ux.md`, `database.md`, `api.md`) is a complete, kept example of all four practices applied to a real feature — including the correction trail where Practice 1 caught and fixed an invented-table mistake mid-spec. Worth reading as a reference the next time a spec needs this level of rigor.
