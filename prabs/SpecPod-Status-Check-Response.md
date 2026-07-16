# SpecPod Adoption, Initial Status Check — Response

**Response due:** 16th July

---

## Q1. Is the framework installed and verified?

**No.** We use our own `.claude/` setup (agents + commands), not the SpecPod framework itself.

- `CLAUDE.md` and `AGENTS.md` are committed in all 7 repos, fully rewritten for SanchiSaaS.
- SpecPod's actual skills (`axiom-test-gen`, `skill-orchestrator`, etc.) are untouched — sitting only as reference material in `prabs/spec-driven-pod-framework/`. Never installed, orchestrator check never run.
- We took 4 ideas from it (Linear automation, test generation, rollout gating, secrets scan) and built them into our own setup instead.

**Status:** Not done — deliberate choice, pending sign-off (see Q6). Expected date: ______________

---

## Q2. Which coding agent and model?

- **Claude Code**, running **Sonnet 5**.
- No model IDs are hardcoded anywhere in our commands/agents — nothing to update per-skill.
- Plan/tier (Pro/Team/Enterprise) — team to confirm.

**Status:** Mostly answered, needs plan/tier confirmation. Expected date: ______________

---

## Q3. CI and security controls?

**None.** Zero CI across all 7 repos — no GitHub Actions, no test/lint/secret-scan gate on any PR.

- Only safeguard: a local Claude Code hook that stops the AI agent itself from touching `.env`/key files during a session. Not a real scanner, doesn't run pre-commit, doesn't cover git history.

**Repos covered by CI: 0 of 7.**

**Status:** Not done. Expected date: ______________

---

## Q4. Test frameworks and issue tracker?

| Repo | Tests |
|---|---|
| `sc-saas-backend` | Jest — real tests exist |
| `sanchiconnect-saas-tenants` | Jest — configured, no tests written |
| `sc-saas-3rdparty-webservices` | Jest — configured, no tests written |
| `sc-saas-frontend` | Karma/Jasmine — default boilerplate only, no lint |
| `sc-saas-admin`, `sanchiconnect-saas-tenants-admin`, `ai-startups-analyzer` | None |

**Tracker: Linear**, and it's agent-driven — our agents create and move issues themselves as work happens (proven this week, see Q5). Test auto-generation is built but hasn't produced a committed test yet.

**Status:** Tracker working. Test generation not yet exercised. Expected date: ______________

---

## Q5. How do requirements become tracked work?

1. Requirement → spec (`/spec-new` or `/from-linear`).
2. Agent drafts the spec **and** creates a Linear Project + one issue per repo automatically.
3. Once approved, implementation moves each issue Todo → In Progress → In Review → Done as work happens.
4. Small bug fixes skip the spec/project — just one flat issue (`/bug-fix`).

**Proven this week:** Bulk Email Attachments — issues SAN-5 to SAN-15 on Linear, tracked start to finish this way.

No `task-breakdown.yaml` step exists — one Linear issue per repo, not per task.

**Status:** Done and working.

---

## Q6. Top blockers?

1. **Decision needed:** keep cherry-picking SpecPod ideas into our own setup, or adopt the framework wholesale? Owner: ______________
2. **No CI or secret-scanning anywhere** — root cause behind most of the gaps above. Owner: ______________
3. **Uneven test coverage** — 3 of 7 repos have no test framework at all. Owner: ______________

---

Completed by: ______________ · Date: ______________
Reviewed by POD Lead: ______________
