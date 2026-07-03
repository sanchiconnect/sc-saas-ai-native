# The Adoption Handbook

*How to start using this framework — what to have ready, how to run your first sprint in a small pod, and how to bring it to software that already exists.*

This handbook assumes you've read *Understanding Skills & Spec-Driven Development*. Names like `openspec.yaml`, "gate", and "spec conformance" are explained there.

---

# Part A — Prerequisites

Before a team starts, five things need to be in place. Skipping any of them turns the first sprint into a scramble.

## A.1 People and roles

The framework is built for a **pod of three to four**: one **POD Lead** and two or three **AI Builders**. The mapping to responsibilities is the important part, not the headcount:

- **POD Lead** — owns direction and *owns every gate*. This is the human-in-the-loop: the person who approves or rejects at each checkpoint, resolves ambiguity, and is accountable for what ships. On a solo project, one person plays POD Lead and delegates the building to the AI.
- **AI Builders** — the people who drive the building agent (Cursor, Claude Code, or similar): they run the skills, feed inputs, and bring back evidence. Each Builder typically owns one wave of tasks per sprint.

One person must be clearly accountable for gates. A pod where "everyone" approves is a pod where no one does.

## A.2 Tools and accounts

| Need | Purpose | Note |
|---|---|---|
| A coding agent | Cursor or Claude Code — where the building happens | The framework ships `.cursorrules` and `AGENTS.md` for exactly this |
| A model API key | Powers the skills and the coding agent | Budget awareness matters; skills declare token budgets |
| Git + a host (GitHub etc.) | Version control and pull requests | The whole method assumes PR-based review |
| CI (e.g. GitHub Actions) | Runs tests, lint, and secret scans on every PR | This is where gates get *enforced* rather than hoped for |
| A test framework | Executes the tests skills generate | Match your stack (e.g. Vitest/Playwright, or pytest) |
| A secret scanner (e.g. gitleaks) | Blocks credentials from being committed | A pre-commit hook plus a CI step |
| An issue tracker (optional) | Roadmap and task visibility | Linear works well and can be driven by the agent |
| An LLM-eval tool (if you ship AI features) | Golden references and injection tests | e.g. promptfoo, wired into CI |

## A.3 Repository readiness

- A git repository the team can push to and open PRs against.
- A **chosen stack** — the framework is stack-agnostic in principle but every prompt is sharper when the stack is decided. Write it down.
- The ability to **run the test suite locally and in CI**. If tests can't run, the verification half of the framework can't work.

## A.4 Inputs

- **Greenfield:** a requirements source — a PRD, a brief, meeting notes, whatever states what you're building. The framework's knowledge-capture skills turn these into specs.
- **Brownfield:** the **existing codebase** (see Part C). The framework extracts specs *from the code*.

## A.5 Disposition

Two cultural prerequisites matter as much as the technical ones:

- **Comfort with the basics** — git, reading and reviewing PRs, reading a spec. Nobody needs to be an expert, but the loop assumes these.
- **The discipline not to bypass gates.** The framework's guarantees evaporate the moment someone hotfixes past the ledger and the checks. Agree, as a team, that the gates are real before you start.

---

# Part B — Your first sprint, step by step (3–4 person pod)

This is a concrete walkthrough. Do it once end-to-end on a small, real slice of work — not the whole product — so the pod learns the rhythm cheaply.

## Week 0 — Install the framework into the repo

1. **Drop the package into the repo.** The `.claude/` skills, and the reference files (`CLAUDE.md`, `AGENTS.md`, `.cursorrules`) that tell the coding agent the rules of this repo. Commit them, so the method lives in the repo rather than in anyone's head.
2. **Write down conventions once.** Confirm the stack, the coding standards, and — importantly — the escalation rule: *when the agent is unsure, it stops and asks; it does not invent.* The shipped `AGENTS.md` already encodes this posture; adapt it.
3. **Wire the CI spine.** A pipeline that, on every pull request, runs the test suite, the linters, and a secret scan. This is what makes a "gate" more than a promise. If you ship AI features, add an eval step (golden references + an injection suite).
4. **Decide who owns gates** (the POD Lead) and how approvals are recorded (a ledger entry, a PR approval, or both).

## The weekly rhythm

The pod runs one sprint a week. Here's what each day produces and who does what.

### Monday — Plan (and lock)

| Step | Skill(s) | Who | Output |
|---|---|---|---|
| Capture knowledge | meeting- / doc- / code-extraction | Builder | Updated `specs/` with new rules, entities, decisions |
| Generate specs | spec-generation | Builder | Epics → stories → **tasks, each under ~3 days** |
| Lock the sprint | CreateOpenspec | POD Lead + Builder | `openspec.yaml` — the frozen scope with acceptance criteria |
| Decompose | SpecFlow | Builder | `task-breakdown.yaml` — clusters, waves, builder assignments |
| **Gate 0** | — | **POD Lead** | Scope approved; the sprint is now real |

The point of Monday is that by end of day, **the whole sprint is written down and agreed** — every task, every acceptance criterion, every dependency — and locked. Nothing after this works against a vague instruction.

### Tuesday–Thursday — Build

For each task cluster, a Builder runs the loop:

1. **Tests first.** Guardian turns the cluster's acceptance criteria into executable tests *before* the code is written.
2. **Build.** DevCopilot generates spec-anchored code — carrying the acceptance-criteria IDs in comments and a provenance header — against the shared knowledge plane, with secrets automatically redacted.
3. **Conformance gate.** Code is "done" only at a Spec Conformance Score ≥ 0.90 **and** zero critical failures, checked by a *separate* verifier pass. Three iterations without reaching the bar escalates to the POD Lead rather than shipping.
4. **Record the decision.** Anything that changed scope or a spec gets an append-only entry in the decision ledger.
5. **Gates 1–2** (POD Lead) approve clusters as they land; a rejection ripples rework forward into anything built on top.

Each Builder owns a wave; independent waves proceed in parallel. (The deterministic orchestrator can schedule this and dry-run cost and time in "plan mode" first, if you want the coordination automated — optional for a small pod.)

### Friday — Validate and release

| Step | Skill(s) | Who | Output |
|---|---|---|---|
| Adversarial + scenario testing | RedTeamX, SimLab | Builder | Vulnerability and edge-case findings |
| Policy gate | PolicyEnforcer | Builder | Pass/fail against compliance rails (a **zero-critical hard gate**) |
| Synthesise failures | InsightOps | Builder | Cross-cutting failure report; recurring failures flagged as spec gaps |
| **Gate 3** | — | **POD Lead** | Release approved |
| Ship + watch | rollout / runbook / DriftGuard | Builder | Deploy; then drift-guard samples production output against the locked spec |

## How to run any single skill

The mechanics are the same every time: **point the agent at the skill's `SKILL.md`, give it the inputs the skill names, let it produce the outputs, collect them.** Read the skill's limitations section — every skill has one, and it tells you where its output needs a human's eye.

## The gate mechanic, concretely

At a gate the POD Lead is answering one question per acceptance criterion: *can I point at a result and say yes?* The evidence the Builder brings back is the worked happy path plus live checks (a query, a request, a log). Approve → the work advances. Reject → the framework re-opens the rejected piece *and everything downstream of it*, so nothing built on a rejected foundation slips through.

## Common pitfalls (and the fix)

- **Bypassing a gate under time pressure.** The fix is cultural: agree up front the gates are real, and let CI catch what discipline misses.
- **Spec drift.** When you change behaviour, change the spec first. A recurring test failure is a signal the spec is wrong, not just the code.
- **Over-scoping a task.** If a task can't be verified on its own, it's too big — split it. The "under three days" rule exists for this.
- **Applying the full ceremony to a trivial change.** Use a lightweight path for micro-changes: keep the goal, the acceptance criteria, and the evidence, drop the rest.

---

# Part C — Bringing the framework to existing software

The framework is often *most* valuable on software that already exists and keeps being worked on — because that's where "why was this built this way?" and "who reviews the AI's change?" bite hardest. But you adopt it differently than on a greenfield project: **you do not rewrite, and you do not spec everything at once.**

## C.1 The retrofit path

The starting move is a skill called **code-extraction**. Instead of writing specs by hand, you point it at the existing codebase and it generates the `knowledge.md`, `api.md`, and `database.md` specs *from what is actually built* — the real entities, the real endpoints, the real schema. A human review pass then validates and corrects them. Within a week or two you have specs that describe your system as it truly is, not as someone hoped it was two years ago.

## C.2 Strangler adoption

From there, adopt incrementally — the "strangler" pattern:

- **Only new work goes through the full loop.** New features are specced, locked in `openspec.yaml`, built to conformance, and gated.
- **Legacy code gets specced when you touch it,** never wholesale. The first time you modify an old module, you bring it under a spec; until then it stays as-is.
- Over time the specced surface grows around the legacy core, and the parts that change most — which are the parts that matter most — end up governed first.

## C.3 What you gain, specifically

- **Traceability where there was none.** New behaviour carries acceptance-criteria IDs; six months later the change is legible.
- **Onboarding for free.** The extracted specs *are* the document a new teammate — or a second AI agent — reads to understand the system.
- **A safety net for AI features.** If the existing product has (or is adding) an LLM feature, the eval, red-team, and drift skills are the half of the workflow most teams are missing.
- **Regression coverage from worked examples.** Skills ship with sample input/output pairs; these seed a regression suite that guards the behaviour you extracted.

## C.4 What to watch

- **Extraction is approximate.** It reads what the code does, which is not always what the code *should* do. The human review pass is not optional.
- **Maintained specs only.** On a moving product, a spec you stop updating becomes a confident lie. Budget for keeping the specced surface honest.
- **Resist the big-bang.** The failure mode is trying to spec the whole legacy system in one heroic sprint. Spec what changes; leave the rest.

## C.5 A concrete first two weeks on a brownfield codebase

1. **Days 1–3:** Install the framework and CI spine. Run code-extraction to draft `knowledge.md`, `api.md`, `database.md`. 
2. **Days 4–5:** Review and correct the extracted specs with someone who knows the system. This is the highest-leverage review you'll do.
3. **Week 2:** Take one *small, real* upcoming change. Run it through the full loop — lock a mini-`openspec.yaml`, generate tests from its criteria, build to conformance, gate it. 
4. **End of week 2:** The pod has proven the rhythm on real work, has honest specs for the parts that matter, and a template for every change after. Expand from there, one touched module at a time.

---

## A note on names

Throughout this package, **"SpecPod"** (the framework) and **"Acme Corp"** (the example organisation) are neutral placeholders. Replace them with your own names when you adopt it. The worked example project under the orchestrator is a demonstration of an accounts-payable automation sprint; treat it as a reference, not a fixture to keep.

---

*Start small, prove the loop once, then widen it. The framework rewards a pod that runs one honest sprint end-to-end far more than one that adopts every skill on day one.*
