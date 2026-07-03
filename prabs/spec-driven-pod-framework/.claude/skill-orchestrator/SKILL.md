---
name: skill-orchestrator
description: "Execute a multi-skill workflow whose tasks are organized into ordered planning, build, and validate phases with human-in-the-loop gates. Use this skill whenever work decomposes into many individual skill invocations that share a file/artifact dependency graph, run in parallel where independent, pass through approval gates (e.g. spec lock,"
---

**name:** skill-orchestrator

**description:** Execute a multi-skill workflow whose tasks are organized into ordered planning, build, and validate phases with human-in-the-loop gates. Use this skill whenever work decomposes into many individual skill invocations that share a file/artifact dependency graph, run in parallel where independent, pass through approval gates (e.g. spec lock, design sign-off, release sign-off), and need rework loops plus governance (tokens, first-time-right, gate outcomes, makespan). It also offers a plan mode (think first, act later) that analyzes requirements, lays out the execution plan, estimates token cost, asks clarifying questions, recommends which skills to include or exclude, and persists a finalized run config. Trigger it for phrasing like "run the planning/build/validate phases", "orchestrate these skills", "execute the sprint workflow", "plan this run first", "estimate the cost before running", "what skills do we actually need", "dry-run the workflow", "dispatch tasks in waves", "gate the release", or any pipeline of named skills with gates and artifacts. In plan mode the engine analyzes and recommends; in run mode it decides the next wave of skills/gates and you (Claude Code) execute each via subagents (and route each gate to a human) and feed results back.


# Skill Orchestrator (phase + gate model)

A deterministic **dispatch-mode** engine that schedules and governs a workflow of
other skills. The engine owns the *decisions* (what to run next, in what order, in
parallel or alone, when to rework, when a gate blocks progress); you own the
*execution* (running each skill as a subagent, and routing each gate to its human
reviewer), then feed results back.

This is modeled on the **SpecPod Framework**: a sprint runs three ordered **phases** —
`planning → build → validate` — and each phase is a set of **tasks**. A task is either:

- a **skill task** — one AI-native skill invocation that *consumes* and *produces*
  named artifact files, and may be **reworked** if its result is rejected; or
- a **gate task** — a human-in-the-loop (HITL) checkpoint (SpecPod Gate 0/0.5/1/2/3)
  that must be **approved** before the tasks behind it run, and that can send specific
  upstream tasks **back for rework** when rejected.

Governance carries the original three dimensions — **tokens**, **first-time-right**
(FTR), **lifecycle/timing** — now rolled up per phase, plus gate outcomes and makespan.

## Plan mode (think first, act later)

Before committing to a run, use **plan mode** to analyze a spec against the user's
requirements without invoking any skill:

```bash
python -m skill_orchestrator.cli plan --spec examples/SpecPod/SpecPod-sprint.workflow.json \
  --requirements "Build a CRUD expense service; 1000 concurrent users, p95 < 300ms." \
  --report plan-report.md --config run-config.json
```

It (1) explores the artifact graph (required input specs vs. produced deliverables) and
the skill/gate inventory; (2) dry-runs the real scheduler to lay out the wave-by-wave
execution plan and an estimated makespan; (3) estimates tokens and cost (base and a
worst-case-with-rework ceiling) from each task's `token_budget` and a configurable
price book; (4) raises **clarifying questions** (scope, AI features, NFR targets,
golden references); and (5) **recommends skills to include/exclude** (e.g. drop
`spec-impact-analyzer` with no spec diff, `prompt-bench` with no AI features).

The flow is two-pass:
- **First pass** (no/some answers): status is `needs_input`; the report lists the open
  questions and recommendations. The run config is **not** persisted yet. Surface the
  questions to the user (ideally via the interactive picker) and collect answers.
- **Second pass** (`--answers answers.json`, where the JSON maps each question `id` to
  an answer): answers prune or keep skills; once none are open, status is `ready` and
  the finalized **run config** is written — a pruned spec with a `plan` provenance block
  (requirements, answers, exclusions, cost estimate, price book) that
  `orchestrator init` consumes directly.

`--exclude a,b` / `--include c` force scope decisions; `--pricebook prices.json`
overrides the default per-model rates; `--markdown` prints the report instead of JSON.

The cost figures are estimates, not a quote — token budgets and the default price book
are both approximate. Set your contracted rates in a price book file. Keyword detection
for questions is heuristic (it cannot read negation like "no AI"), which is exactly why
plan mode asks the user to confirm rather than deciding silently.

## The control loop

```
init ─▶ next ─▶ [run the wave: skills as subagents, gates to humans] ─▶ record ─▶ … ─▶ report
```

1. **init** a workflow spec → state file.
2. **next** → the next *wave*: a batch of actions plus a `mode` (`parallel`, or
   `sequential` for a gate or an exclusive task) and the `phase` it belongs to.
3. **Run the wave.** For each **skill** action, spawn a subagent that performs `skill`
   for `task_id`, passing the artifacts it `consumes`. For a **gate** action
   (`requires_approval: true`), present the artifacts it consumes to the named
   `reviewer` and collect an approve/reject decision — do **not** auto-approve.
4. **record** one result per action. The engine applies transitions (accept / retry /
   approve / reject / fail), routes rework, and advances the clock.
5. Loop until `next` reports `complete` (or no actions).
6. **report**.

State persists after every `record`, so the run is **resumable across turns**.

## Spec format

A spec is JSON: a `config` block plus a flat `tasks` list spanning all phases.

```json
{
  "name": "SpecPod-sprint",
  "config": {
    "time_budget_seconds": 0,
    "max_parallelism": 5,
    "default_rework_budget": 1,
    "default_accept_threshold": 0.8,
    "enforce_phase_order": true
  },
  "tasks": [
    {"id": "gate-0", "name": "Gate 0 — openspec lock", "phase": "planning",
     "kind": "gate", "reviewer": "POD Lead", "produces": ["openspec.yaml"]},

    {"id": "spec-flow", "name": "SpecFlow", "phase": "planning", "kind": "skill",
     "skill": "spec-flow", "model": "claude-opus-4", "token_budget": 120000,
     "consumes": ["openspec.yaml", "context.yaml", "policy-catalogue.yaml"],
     "produces": ["task-breakdown.yaml", "ai-manifest.json"],
     "depends_on": ["gate-0_5"]},

    {"id": "gate-1", "name": "Gate 1 — Plan sign-off", "phase": "planning",
     "kind": "gate", "reviewer": "POD Lead + Business Lead",
     "consumes": ["sprint-board.md", "scenario-matrix.md"]}
  ]
}
```

Task fields:
- `phase` — `planning` | `build` | `validate` (the sprint stage; runs in that order).
- `kind` — `skill` (needs `skill`) or `gate` (needs `reviewer`).
- `consumes` / `produces` — artifact filenames. **Dependencies are derived from these**:
  a task that consumes file X automatically depends on whichever task produces X. A
  consumed file with no in-workflow producer is treated as an external precondition
  (e.g. `specs/*.md` from a prior phase) and ignored.
- `depends_on` — explicit dependencies in addition to artifact-derived ones.
- `exclusive` — must run alone in its wave (gates are implicitly exclusive).
- `optional` — may be dropped under time pressure.
- `rework_budget` — max rework cycles before a skill task fails (default from config).
- `accept_threshold` — minimum skill `score` (0–1) to accept.
- `token_budget`, `model`, `estimated_seconds` — metadata + scheduling estimate.

Authoring from a spec document (like the SpecPod readmes): create one skill task per
skill, set `consumes`/`produces` from its artifact contract, add a gate task per HITL
gate, and let the engine wire the rest. See `examples/SpecPod/generate_specs.py`, which
encodes all three readmes into `planning`, `build`, `validate`, and a combined
`SpecPod-sprint` spec.

## Running it (CLI = what Claude Code drives)

```bash
python -m skill_orchestrator.cli init   --spec examples/SpecPod/SpecPod-sprint.workflow.json --state state.json
python -m skill_orchestrator.cli next   --state state.json                 # -> wave JSON
# ... run the wave, write results.json ...
python -m skill_orchestrator.cli record --state state.json --results results.json --governor-db gov.db
python -m skill_orchestrator.cli report --state state.json                 # add --json for machine-readable
python -m skill_orchestrator.cli status --state state.json
```

A `next` wave looks like:

```json
{"wave_index": 19, "mode": "parallel", "phase": "validate", "complete": false,
 "actions": [
   {"task_id": "red-team-x", "kind": "skill", "skill": "red-team-x", "attempt_number": 1,
    "consumes": ["eval-rubric.yaml", "ai-manifest.json"], "requires_approval": false},
   {"task_id": "sim-lab", "kind": "skill", "skill": "sim-lab", "attempt_number": 1,
    "consumes": ["openspec.yaml", "task-breakdown.yaml", "deploy-manifest.yaml"]}
 ]}
```

## Reporting results

Write one result object per action under `{"results": [...]}`.

**Skill result** — drives accept / retry / fail:
```json
{"task_id": "red-team-x", "success": true, "score": 0.91, "issues": [],
 "token_usage": {"input_tokens": 40000, "output_tokens": 8000}, "duration_seconds": 30,
 "suggested_skill": null}
```
- `score < accept_threshold` (or `success:false`) → the engine **retries** within
  `rework_budget`, else fails the task.
- `suggested_skill` → the retry is **redirected** to that remediation skill (e.g.
  Guardian routes a fix to a focused fixer).

**Gate result** — drives approve / reject:
```json
{"task_id": "gate-3", "approved": false, "rework_targets": ["red-team-x"],
 "note": "VULNERABLE finding; remediate before release"}
```
- `approved: true` → gate clears; downstream proceeds.
- `approved: false` with `rework_targets` → those upstream tasks reopen for rework, and
  **everything downstream of them that had already completed re-runs too** (so the gate
  re-fires against fresh artifacts), then the gate is re-presented.
- `approved: false` with no targets → the gate fails and its downstream is skipped.

Capture each subagent's real tokens/duration from its completion notification.

## How the engine schedules and decides

- **Order**: ready tasks are sorted by phase (earlier phases first), then by critical
  path (longest downstream estimate first), then required-before-optional.
- **Concurrency**: independent skill tasks pack into one parallel wave up to
  `max_parallelism`; a **gate** or an **exclusive** task gets a solo sequential wave.
  Phases legitimately **overlap** when artifacts allow (validation rubric/feature
  generation can begin once the plan is signed off, concurrently with build).
- **Phase order** (`enforce_phase_order`): a task may not depend on a later-phase task;
  violations are rejected at build time, along with dependency cycles, unknown
  dependencies, and duplicate artifact producers.
- **Rework under time pressure**: with a finite `time_budget_seconds`, once remaining
  time drops below `tight_time_fraction` the effective rework budget is curbed (→1, then
  0) and optional tasks are dropped — completing the list beats perfecting it.
- **first-time-right**: a skill task is FTR only if it reaches `done` on its first
  attempt with no rework. Gates are never counted as FTR.

## Unified governance telemetry

Pass `--governor-db gov.db` to `record` to persist each skill task into the vendored
`skill_governor`, giving a queryable per-skill report (FTR, reruns, tokens) alongside
the orchestrator's per-phase report.

## Tests & demo

```bash
python -m pytest tests/ -q                                    # engine + scheduler + gates + integration
cd examples/SpecPod && PYTHONPATH=../../src python generate_specs.py   # regenerate specs from the readmes
cd examples/SpecPod && PYTHONPATH=../../src python run_sprint.py       # simulate the full sprint end-to-end
```

`run_sprint.py` stands in for the subagents and the reviewer: it drives the combined
29-skill / 6-gate sprint, exercises a skill rework (DevCopilot), and a gate-driven
remediation loop (Gate 3 rejects → RedTeamX re-runs → InsightOps re-synthesizes →
Gate 3 approves).
