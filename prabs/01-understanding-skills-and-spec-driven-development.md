# Understanding Skills & Spec-Driven Development

*A plain-language guide to what this framework is and why it is built the way it is.*

---

## 1. The problem this solves

Most people build software with an AI assistant the same way they'd chat: they describe what they want, the model writes code, they eyeball it, they ask for changes. This works beautifully for an afternoon and falls apart over a quarter. The reason is simple — **the project's real state lives in the conversation**. What was decided, why a table has the shape it has, which rule the checkout logic is enforcing: all of it sits in chat history that gets compacted, lost when a new session starts, and is invisible to a second person or a second agent. Six weeks in, nobody can say why a thing was built the way it was, and the only reviewer is the person who is also the author.

This framework is a disciplined answer to that failure. Its single move is to **take the project's truth out of the chat and put it into files in the repository** — and then manufacture the AI's instructions *from* those files and check the AI's output *against* them. Everything else is machinery in service of that one idea.

Two concepts do the work: **skills** and **spec-driven development**. They are separate ideas that combine here into one system.

---

## 2. What a "skill" is

A skill is a folder containing a `SKILL.md` file plus any supporting scripts, templates, and worked examples. `SKILL.md` is a procedure written for an AI agent — the accumulated, hard-won *right way* to do one job, encoded once so it doesn't have to be re-derived every time.

Think of it as the difference between telling a new hire "figure out how we write test suites" versus handing them a one-page playbook that says exactly which files to read, what format to produce, what counts as done, and where the usual mistakes are. The playbook is the skill.

A well-formed `SKILL.md` has two parts:

- **Frontmatter** — a short YAML header with a `name` and a `description`. This is not decoration; it is the *trigger*. In tools like Claude Code, the agent scans the descriptions of all available skills and pulls in the one whose description matches the task at hand. A vague or missing description means the skill never fires when it should. (Repairing exactly this — 69 skills that shipped without frontmatter — was part of preparing this package; see `CHANGES.md`.)
- **Body** — the actual procedure: purpose, the inputs it needs, numbered steps, the outputs it produces, and an honest section on its limitations.

Two design principles make skills powerful rather than just tidy:

1. **Progressive disclosure.** The `SKILL.md` stays short and points to heavier reference material only when needed. The agent reads the one-page procedure first and loads the 40-page reference only if the task requires it. This keeps the agent's limited context window full of *relevant* material instead of everything-just-in-case.
2. **Composability.** Skills are small and single-purpose, so they chain. One extracts knowledge from a meeting; the next turns that knowledge into a spec; the next turns the spec into tasks. Each is independently useful and independently improvable.

In this framework there are 69 of them, each written as a named "agent" with a version, an assigned model, a token budget, required input files, output files, and numbered steps. Together they cover the entire lifecycle of building software.

---

## 3. What "spec-driven development" is

Ordinary development treats code as the source of truth: the spec (if one exists) describes intent, but the code is what's real, and the two drift apart within weeks. Spec-driven development **inverts that**. The specification is the source of truth; code is a *conforming artifact* generated from it. If the code is wrong, you fix the code. **If the spec is wrong, you fix the spec first, then the code.** The spec is never allowed to fall behind.

Concretely, the framework keeps the truth in six small domain files under `specs/`:

| File | What it governs |
|---|---|
| `program.md` | The charter — goals, scope, KPIs, open decisions |
| `knowledge.md` | Business entities, rules, state machines, glossary |
| `design.md` | Stack, architecture, coding standards, security posture |
| `ui-ux.md` | Design tokens, components, accessibility standards |
| `database.md` | Schema, indexes, migration policy |
| `api.md` | Endpoints, request/response schemas, the auth contract |

Why six small files instead of one big document? Because an AI agent building a checkout endpoint needs the API contract and the schema — not the design system or the KPI targets. Small domain files mean **less context per task**, which means cheaper, sharper, more accurate agent runs.

The specs are deliberately fine-grained down to **acceptance criteria with stable IDs** (for example `F5-AC1`). Every unit of behaviour has an ID, and the code that implements it carries that ID in a comment. That single convention is what makes the whole thing traceable months later: you can walk from a line of code to the criterion it satisfies, and from a criterion to the code that satisfies it.

---

## 4. How skills and specs combine here

The two ideas lock together like this:

- **The specs are the law.** They say what is true about the product.
- **The skills are the procedures** that read the specs, do a job, and write artifacts back — always conforming to the specs, never contradicting them.
- **Each sprint locks a scope.** A skill called CreateOpenspec elicits the sprint's scope and freezes it into `openspec.yaml` — the contract for *this* sprint, with every task, its acceptance criteria, and its dependencies. Nothing in the sprint is allowed to exceed what's locked without going back and re-locking.

So the flow of a piece of work is: the specs define what's true → a sprint locks a slice of it into `openspec.yaml` → skills decompose that into small tasks → an agent builds each task to conform → other skills verify it against the very criteria that were locked. The AI never freelances against a vague prompt; it always works against a written, checkable contract.

---

## 5. The lifecycle

The framework organises its skills into a weekly rhythm with five stages. A small pod runs one sprint a week: plan on Monday, build Tuesday to Thursday, validate and release on Friday.

```
  KNOWLEDGE          SPEC              PLAN              BUILD             VALIDATE          OPERATE
  CAPTURE      →     GENERATION   →    (lock + decompose) →  (generate) →  (test + gate)  →  (watch prod)
  meetings,          epics →           openspec.yaml,     spec-anchored    Gherkin from ACs, drift vs spec,
  docs, code         stories →         task clusters,     code, shared     red-team, policy  incidents,
  → specs            tasks (<3 days)   waves, gates       RAG, secrets      gate (0 critical) parity
```

Between the stages sit **human gates** (Gate 0 through Gate 3) — checkpoints where a person reviews and either approves or sends work back. This is the "human-in-the-loop": the AI does the labour, the human owns the decisions. When a gate rejects work, the rework *ripples forward* — anything already built on top of the rejected piece is re-opened too, so the specs and the code never quietly diverge.

---

## 6. The mechanisms worth understanding

A few ideas inside the framework are the difference between a serious system and a pile of prompts. These are worth internalising because they are the reusable lessons, whatever tool you use.

**Oracles come from the spec, not the implementation.** A skill called Guardian turns acceptance criteria into executable tests (in Gherkin) *before* the build begins. This matters enormously: if you write tests by looking at the code, you only prove the code does what it does. Writing them from the spec proves the code does what it was *supposed* to.

**The generator and the verifier are separate.** Code is delivered only when a Spec Conformance Score of at least 0.90 is reached *and* zero critical failures remain, scored across weighted dimensions against external ground truth. Crucially, the verifier runs as a *separate* invocation that is told it did not write the code, improvement must be monotonic each iteration, and after three iterations it escalates to a human instead of shipping. This is the correct answer to the well-known failure of models grading their own homework.

**Every failure is classified.** No test failure is absorbed silently; each is triaged into a category. A failure that recurs is treated not as a bug in the code but as a **gap in the spec** — the sign that the specification was ambiguous or wrong. This is how the specs get better over time instead of rotting.

**Orchestration is deterministic.** There is a real scheduling engine (plain Python, with a passing test suite) that derives the task dependency graph from what each task consumes and produces, schedules independent tasks in parallel, blocks on the human gates, ripples rework forward, and tracks token spend. It **never calls a model** — it's ordinary, predictable software doing the coordination, which is exactly what you want coordination to be. It also has a "plan mode" that dry-runs cost and time and asks clarifying questions before anything executes.

**Context and cost are engineered, not hoped for.** A cluster of skills routes each task to an appropriately-sized model, slims prompts, compacts context, caches semantically similar calls, and audits the tool surface. Running powerful models is expensive; this discipline is what keeps a portfolio affordable.

**The framework extends itself.** A planning skill (SkillFlow) reads the catalog plus the specs and decides — *with evidence citations and confidence scores, and explicit rules against treating best-practice assumptions as evidence* — which skills to run, skip, or enhance for a given project. Another skill materialises new skills; another mines session transcripts for repeated behaviour worth promoting into a skill. The system is designed to grow.

---

## 7. Why this beats chat-first building

Put plainly, against the "describe it and eyeball the output" approach, spec-driven building with skills gives you:

- **Durability.** State lives in files, so a new session, a switched tool, or a fortnight away costs nothing. The plan rehydrates from the repo in one read.
- **A reviewer you otherwise don't have.** Tests written from the criteria, plus a fresh, separate verifier pass, simulate the second pair of eyes a solo builder or a small pod lacks. "Done" becomes something you can point at, not something you feel.
- **Month-three debuggability.** Every behaviour traces to an ID and every decision has a ledger entry, so when something misbehaves later you read a line instead of doing archaeology through old chats.
- **A safety net for AI features.** Golden references, injection red-teaming, and drift checks are things ordinary workflows have no answer for — and any product that ships an LLM feature needs them.
- **Cheaper, sharper runs.** Small domain specs plus scoped rules beat pasting an entire requirements document into every prompt.

---

## 8. What it is *not*, and where it costs you

This is not a silver bullet, and using it where it doesn't fit is its own mistake.

- **It taxes speed.** Nothing builds until the sprint locks, which is friction when you just want to try something. (The escape valve is a "spike" — an explicit exploration task whose deliverable is a findings report rather than production code.)
- **Small changes get heavier.** A two-line copy tweak now travels through the proper files and checks; a column rename touches the schema spec first.
- **Specs rot if unmaintained** — and a stale spec is *worse* than none, because it lies with confidence. The discipline of fixing the spec first is not optional.
- **It's weakest where the value is taste.** For editorial or heavily aesthetic work, spec-first has less to offer than it does for systems with money, state machines, and data integrity on the line.
- **It only works if the bypass never happens.** At 11pm the temptation to hotfix and skip the ledger is real. CI catches some of it; discipline carries the rest.

The rule of thumb: **the payoff scales with three things** — how many hard invariants a product has, whether it runs an AI feature in production, and how many sessions, people, or agents will touch the code over time. Score high on those and this framework earns its keep. Score low and a lighter approach may serve you better.

---

## 9. Glossary of the artifacts

| Artifact | What it is |
|---|---|
| `specs/*.md` | The six domain files — the source of truth for the whole product |
| `openspec.yaml` | The locked scope for a single sprint: tasks, acceptance criteria, dependencies |
| `task-breakdown.yaml` | The sprint's work decomposed into small, bounded clusters and waves |
| `decision-ledger.md` | An append-only log of every decision that changed scope, a spec, or an invariant |
| Acceptance criterion ID (e.g. `F5-AC1`) | A stable handle for one unit of behaviour, cited in code comments |
| Provenance header | A comment block on generated files: which agent made it, from which spec sections and criteria, when |
| `SKILL.md` | One reusable procedure, with frontmatter that triggers it and a body that performs it |
| Gate (0–3) | A human checkpoint that approves work or sends it back, rippling rework forward |

---

*Next: the **Adoption Handbook** covers what a team needs ready before starting, a step-by-step first sprint for a 3–4 person pod, and how to bring the framework to an existing codebase.*
