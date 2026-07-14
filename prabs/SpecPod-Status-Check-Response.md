# SpecPod Adoption, Initial Status Check — Response

**Response due:** 16th July

---

## Q1. Is the framework installed and verified in the SanchiSaaS repository?

> Hint: `.claude/`, `CLAUDE.md`, `AGENTS.md` committed; orchestrator check from the README passing (41 tests, example sprint completes). Has `AGENTS.md` been rewritten for SanchiSaaS, or is it still the accounts-payable example?

**Response:**

Not as delivered. `CLAUDE.md` and `AGENTS.md` are committed in the workspace root and all 7 product repos (`sc-saas-admin`, `sanchiconnect-saas-tenants`, `sc-saas-backend`, `sc-saas-frontend`, `ai-startups-analyzer`, `sc-saas-3rdparty-webservices`, `sanchiconnect-saas-tenants-admin`), completed as of today. All `AGENTS.md` files have been fully rewritten and grounded in real code for this codebase — none are the generic accounts-payable placeholder.

However, this is a **separate, custom-built `.claude/` system**, not the SpecPod framework itself. The workspace root's `.claude/` contains its own agents and commands (`spec-new`, `spec-implement`, `trace-flag`, `flag-impact`, `check-isolation`, `cross-repo-review`, `audit-contract`, `from-linear`, `onboard`, `catchup`) built specifically around SanchiSaaS's cross-repo invariants. The SpecPod framework as delivered (`axiom-test-gen`, `budget-governor`, `eval-checkpoint`, `skill-orchestrator`, `performance-optimizer`, `value-tracker`, etc.) exists **only as reference material** under `prabs/spec-driven-pod-framework/` — it has not been installed into any of the 7 repos, and its orchestrator check (41 tests, example sprint) has never been run against this codebase.

**Status: Not done.** Expected date: _______________

---

## Q2. Which coding agent and model configuration is the team using?

> Hint: The agent (Claude Code or Cursor) and version, the model provider and plan, and whether the pinned model IDs shipped in the skills were updated, centrally or per-skill.

**Response:**

Claude Code. This session ran on Sonnet 5 (`claude-sonnet-5`).

- Plan/provider tier (Pro / Team / Enterprise) and whether it's standardized across the team or per-engineer: **to be filled in by the team** — not visible from this session.
- No hardcoded model ID was found in the actually-installed `.claude/commands/` or `.claude/agents/` — none of them pin a model. SpecPod's own reference skills under `prabs/` do reference specific model IDs, but since that framework isn't installed, "updated centrally or per-skill" doesn't yet apply in practice.

**Status: Partially answered — needs team input.** Expected date: _______________

---

## Q3. What does CI run on every pull request, and which security controls are in place?

> Hint: Name the CI system and confirm each of: test suite, lint, secret scan (which tool, and whether it also runs pre-commit). Note any repository not yet covered.

**Response:**

No CI system exists in any of the 7 repos — confirmed directly (searched for GitHub Actions, GitLab CI, CircleCI, and Jenkinsfile configs across every repo; none found anywhere). No automated test suite, lint, or secret scan runs on any pull request today.

The one safeguard currently in place is a Claude Code session-level hook (`guard-sensitive-files.sh`) that blocks the AI agent itself from reading or writing `.env`/key files during a session. This is not a repository-wide secret scanner, does not run pre-commit for human contributors, and does not cover git history.

**Repositories covered by CI: none (0 of 7).**

**Status: Not done.** Expected date: _______________

---

## Q4. Which test frameworks and issue tracker are in use?

> Hint: Unit and end-to-end frameworks matched to the stack, the generated tests have to land somewhere the team actually runs, plus the tracker and whether it is agent-driven or manual.

**Response:**

| Repo | Test framework | Status |
|---|---|---|
| `sc-saas-backend` | Jest (unit + e2e) | Configured, real tests exist |
| `sanchiconnect-saas-tenants` | Jest | Configured, **no test specs written yet** |
| `sc-saas-frontend` | Karma + Jasmine | Configured; **no lint configured** |
| `sc-saas-admin` | None (`php -l` syntax check only) | No test suite |
| `sanchiconnect-saas-tenants-admin` | None (`php -l` only) | No test suite |
| `ai-startups-analyzer` | None | No test suite, by explicit design note in its own CLAUDE.md |
| `sc-saas-3rdparty-webservices` | Jest | Configured; the one e2e test present is stale and would fail if run |

**Issue tracker:** Linear — confirmed by the installed `/from-linear` command, which pulls a Linear issue into a spec. Whether day-to-day issue creation is agent-driven or manual is a workflow question for the team to confirm; this session can only confirm the tooling exists, not usage patterns.

**Status: Partially done — needs team input on tracker usage pattern.** Expected date: _______________

---

## Q5. How do requirements become issues and a backlog, and where does that backlog live?

> Hint: Walk the path end to end. What is the source of a requirement (BRD, meeting, ticket), which skill or step turns it into specs and then into tasks, and who creates the issues in the tracker, a person or the agent? Name the tool and the board or project the backlog sits in, and say how a task in `task-breakdown.yaml` maps to an issue, one to one or otherwise.

**Response:**

Current, working path: a requirement (from a Linear issue or a rough idea) becomes a spec via `/from-linear <id>` or `/spec-new feature <id>` — feature specs land at `specs/features/<id>-<slug>.spec.md`, module specs at `<repo>/src/<module>/module.spec.md`. Once approved, `/spec-implement <id>` builds directly from the spec, running cross-repo gates (`/audit-contract`, `/trace-flag`, `/check-isolation`) before moving a spec to `in-review`.

There is **no step today that explodes a spec into a `task-breakdown.yaml` or auto-generates a batch of tracker issues.** The only `task-breakdown.yaml` anywhere in the workspace is a sample input file inside the uninstalled SpecPod reference copy (`prabs/spec-driven-pod-framework/.claude/axiom-test-gen/sample_input/task-breakdown.yaml`) — it is not a live artifact and has no mapping to real Linear issues.

So: spec → implementation is direct today; there isn't yet a formal spec → generated-backlog → Linear-issues pipeline as SpecPod describes it. **Team should confirm this matches actual day-to-day practice**, including any manual workarounds not visible in the tooling itself.

**Status: Not done as described in the framework.** Expected date: _______________

---

## Q6. What are your top blockers, and what do you need from Prabhakar or the business?

> Hint: Rank up to three. For each, name who owns the resolution.

**Response:**

_This is a team/business call, not a technical one — the three below are candidates surfaced by the technical review above. Rank, edit, and assign owners before sending:_

1. **SpecPod itself was received but never installed/integrated** — only sitting as reference material in `prabs/spec-driven-pod-framework/`. Needs a decision: adopt it wholesale, cherry-pick pieces into the existing custom `.claude/` setup, or formally decline. Owner: _______________
2. **Zero CI / secret-scanning across all 7 repos.** Owner: _______________
3. **Inconsistent test coverage** — 2 of 7 repos have no test suite by design, `sc-saas-frontend` has no lint configured at all. Owner: _______________

---

Completed by: ______________ · Date: ______________
Reviewed by POD Lead: ______________
