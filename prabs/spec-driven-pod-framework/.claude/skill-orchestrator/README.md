# skill-orchestrator

A deterministic, **dispatch-mode** workflow engine that executes a graph of AI-native
skills organized into ordered **planning → build → validate** phases with
human-in-the-loop **gates**. It is modeled on the **SpecPod Framework**: a sprint is a
set of single-skill tasks plus gates, wired by a file/artifact dependency contract, and
the engine schedules them in waves, runs rework loops, enforces gates, and reports
governance (tokens, first-time-right, gate outcomes, makespan).

The vendored `skill_governor` SDK provides the telemetry primitives, so the original
governance dimensions carry over and roll up per phase.

## Engine decides, agent executes

The engine is **deterministic Python**; it never calls a model. It computes *what to
run next*. **Claude Code executes** each skill action via a subagent and routes each
**gate** action to its human reviewer, then feeds results back.

```
init ─▶ next ─▶ [skills→subagents, gates→humans] ─▶ record ─▶ … ─▶ report
          ▲                                            │
          └────────────────────────────────────────────┘  loop until complete
```

State persists as JSON after every `record`, so a run survives across turns.

## Plan mode (think first, act later)

Before running, **plan mode** analyzes a spec against a free-text requirements
statement — without invoking any skill — and answers "what will this do, what will it
cost, and what do we actually need?":

```bash
python -m skill_orchestrator.cli plan --spec examples/SpecPod/SpecPod-sprint.workflow.json \
  --requirements "Internal CRUD expense service; 1000 concurrent users, p95 < 300ms." \
  --answers answers.json --report plan-report.md --config run-config.json
```

It explores the artifact graph (required input specs vs. produced deliverables),
dry-runs the real scheduler to lay out the wave-by-wave plan and estimated makespan,
estimates **tokens and cost** (base and worst-case-with-rework) from each task's budget
and a configurable price book, raises **clarifying questions**, and **recommends skills
to include/exclude**. It is two-pass: the first pass reports `needs_input` with open
questions; once answers resolve them it reports `ready` and persists a finalized
**run config** (a pruned spec plus a `plan` provenance block) that `init` consumes
directly. See `examples/SpecPod/plan_demo.py`.

## The model

| Concept | Meaning |
|---------|---------|
| **Phase** | A sprint stage: `planning`, `build`, `validate`, run in order (and allowed to overlap where artifacts permit). |
| **Skill task** | One skill invocation that consumes/produces artifact files; reworked if its result is rejected. |
| **Gate task** | A HITL checkpoint (SpecPod Gate 0/0.5/1/2/3); must be approved before downstream runs; can route rework upstream when rejected. |
| **Wave** | A batch of actions to run concurrently — or a single gate/exclusive action run alone. |
| **TaskResult** | What the agent reports: skill `success`/`score`/`issues`/`suggested_skill`, or gate `approved`/`rework_targets`. |

### Dependencies are mostly inferred

You rarely write `depends_on` by hand. Every task declares the artifact files it
`consumes` and `produces`; the engine adds a dependency from each consumer to the
producer of that file. Files with no in-workflow producer are external preconditions
(e.g. `specs/*.md` from a prior phase) and are ignored. The build step also rejects
dependency cycles, unknown dependencies, duplicate producers, and (when
`enforce_phase_order`) any dependency on a later phase.

### Gates and the remediation loop

A gate blocks the tasks behind it until approved. On rejection with `rework_targets`,
the engine reopens those tasks **and ripples the rework forward** through any already
-completed dependents, so the gate re-fires against freshly regenerated artifacts —
faithful to "RedTeamX VULNERABLE → builder remediates → re-synthesize → re-gate".

### Scheduling and least-rework-within-budget

Ready tasks are ordered by phase, then critical path, then required-before-optional;
independent skills pack into parallel waves up to `max_parallelism`; gates/exclusive
tasks run solo. With a finite time budget, rework is curbed and optional tasks dropped
as time runs short.

## Architecture

```
src/skill_orchestrator/
├── models.py       # Phase, TaskKind, TaskSpec, TaskRuntime, TaskResult, Action, WaveDispatch, WorkflowState
├── scheduler.py    # critical paths, dependency/blocking, parallel/gate/exclusive wave selection, time gating
├── analysis.py     # skill accept/retry/fail; gate approve/reject(+rework targets); time-aware rework curbing
├── engine.py       # build_state (+artifact wiring, cycle/phase checks), record_wave, transitions, rework ripple
├── planner.py      # plan mode: dry-run schedule, cost estimate, clarifying questions, scope recs, run-config persistence
├── state_store.py  # atomic JSON save/load (resumability)
├── reporting.py    # per-phase rollups: FTR, rework, tokens, gates approved/total, makespan vs budget
└── cli.py          # plan / init / next / record / status / report
src/skill_governor/ # vendored telemetry SDK (TokenUsage + per-skill governance report)
examples/SpecPod/
├── generate_specs.py  # encodes the 3 readmes -> planning/build/validate + combined sprint specs
├── *.workflow.json    # the generated specs
├── plan_demo.py       # plan-mode walkthrough (clarify -> finalize -> persist run config)
└── run_sprint.py      # end-to-end simulation of the combined sprint
```

## Quick start

```bash
pip install -e .            # or PYTHONPATH=src
python -m pytest -q         # 41 tests: deps, gates, rework, ripple, time budget, plan mode, integration

cd examples/SpecPod
PYTHONPATH=../../src python generate_specs.py   # (re)build specs from the readmes
PYTHONPATH=../../src python run_sprint.py        # simulate the full sprint
```

Sample combined-sprint report:

```
skill tasks      : 29  (done=29, failed=0, skipped=0, completion=100.0%)
first-time-right : 26/29  (rate=89.7%)
rework           : 2 cycle(s)
HITL gates       : 6/6 approved
schedule         : makespan=159.8s; waves=24; avg parallelism=1.62

BY PHASE
  planning  tasks=13 done=13 ftr=13 rework=0 gates=3/3
  build     tasks=9  done=9  ftr=8  rework=1 gates=1/1
  validate  tasks=7  done=7  ftr=5  rework=1 gates=2/2
```

## SpecPod mapping

| Phase | Skills (tasks) | Gates |
|-------|----------------|-------|
| **Planning** | ContextFabric, PolicyCatalog, ResearchCopilot, TransformIQ, AssumptionTracker, SpecFlow (Opus), TraceGraph, SpecImpactAnalyzer, ValueModeler, PortfolioPrioritizer, ScenarioPlanner, DecisionLedger, Conductor | Gate 0 (openspec lock), Gate 0.5 (assumption sign-off), Gate 1 (plan sign-off) |
| **Build** | SecretShield, PerformanceOptimizer, ExperienceStudio, TrustFabric, KnowledgeMesh, DevCopilot, ReviewPilot, PromptBench, NexusDeploy | Gate 2 (design sign-off) |
| **Validate** | EvalHarness, Guardian (generation + execution), RedTeamX, SimLab, PolicyEnforcer, InsightOps | Gate 2 (feature sign-off), Gate 3 (release) |

The combined `SpecPod-sprint` spec chains them: build and validate entry tasks depend on
Gate 1, and validate's later agents stagger behind the build artifacts they consume
(`ai-manifest.json`, `task-breakdown.yaml`, `deploy-manifest.yaml`).

## Relationship to skill-governor

Pass `--governor-db` to `record` to persist each skill task into `skill_governor`,
yielding a unified per-skill telemetry report (FTR, reruns, tokens) alongside the
orchestrator's per-phase governance report.

## License

© 2026 Acme Corp. All rights reserved.

This software and its documentation are the confidential and proprietary property of
Acme Corp. Use, reproduction, modification, or distribution is permitted only
under the terms of a license agreement with Acme Corp. The SpecPod Framework and
associated skill definitions are trademarks of Acme Corp.
