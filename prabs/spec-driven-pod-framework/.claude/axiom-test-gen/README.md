# AxiomTestGen — SpecPod Skill Package

Deterministic software test-case generation for a single epic or task, invoked
**after DevCopilot** finishes implementation. Part of the SpecPod Framework v2.1.0
Build→Validate handoff (Acme Corp).

## What it produces
For one epic/task, AxiomTestGen generates:
1. `tests/<epic-id>/…` — runnable test files (unit / integration / contract / acceptance)
2. `test-plan.<epic-id>.yaml` — machine-readable case manifest (handoff to Guardian/CI)
3. `test-traceability.md` — acceptance-criterion → test-case matrix
4. `coverage-gap-report.md` — uncovered/ambiguous ACs with HITL flags

Tests are **traceable to acceptance criteria**, target **>90% line + branch coverage**,
carry mandatory edge cases, and derive expected outcomes from the **spec, never the
implementation**.

## Package contents
```
axiom-test-gen/
├── SKILL.md                       # The skill definition (10-section canonical)
├── references/
│   ├── test-design-techniques.md  # EP, BVA, decision tables, state-transition, pairwise, property
│   ├── coverage-policy.md         # >90% target, edge taxonomy, assertion-strength rubric
│   ├── output-schema.md           # Schemas for the 4 output artifacts
│   └── framework-adapters.md      # Framework/language detection + per-framework idioms
├── sample_input/                  # Worked example: chat rate-limiter (EP-03 / TASK-03.2)
│   ├── spec.md                    # Oracle source (acceptance criteria)
│   ├── tasks.md                   # Task catalogue
│   ├── task-breakdown.yaml        # Target task + scope boundary
│   ├── ai-manifest.json           # DevCopilot provenance: task → source files
│   └── src/ratelimit/limiter.py   # The implemented code under test
└── sample_output/                 # Verified green (13 tests, 100% line coverage)
    ├── tests/test_limiter.py
    ├── test-plan.EP-03.yaml
    ├── test-traceability.md
    └── coverage-gap-report.md
```

## Installation
Copy the `axiom-test-gen/` folder into your project's skill directory:
```
project-root/.claude/axiom-test-gen/
```
It registers automatically via the `name:` / `description:` frontmatter in `SKILL.md`.

## How to use

### Interactively (Claude.ai / Claude Code chat)
1. Ensure the **required inputs** exist (see `SKILL.md > Required Inputs`):
   `spec.md`, `tasks.md`, `task-breakdown.yaml`, `ai-manifest.json`, and the
   implemented `src/`.
2. Invoke with a trigger phrase, naming the target, e.g.
   *"Generate test cases for TASK-03.2"* or *"AxiomTestGen on EP-03"*.
3. The skill will:
   - resolve scope, **detect the test framework** from the repo (asks only if ambiguous),
   - ask for criticality tier if absent, and offer to add extra edge cases,
   - generate the four artifacts to `/mnt/user-data/outputs/`.

### What the skill will ask you
- **Scope** — which epic/task, if more than one is in play.
- **Framework** — only if detection is ambiguous (e.g. "Python detected, no framework — use pytest?").
- **Criticality** — `standard` vs `critical` (drives model + negative-case depth) if not in `task-breakdown.yaml`.
- **Extra cases** — any scenarios beyond the acceptance criteria you want covered.

## Run the sample yourself
```bash
cd axiom-test-gen/sample_input
pip install pytest pytest-cov
PYTHONPATH=src python -m pytest ../sample_output/tests/test_limiter.py \
  --cov=ratelimit --cov-report=term-missing -q
# Expected: 13 passed, 100% line coverage
```

## Design guarantees & boundaries
- **Oracle from spec only** — prevents tautological tests that assert the code does
  what the code does.
- **Generation only** — does not execute/gate; that is Guardian/CI. Adversarial &
  security cases belong to **RedTeamX**.
- **Coverage % is a floor** — a mutation run is recommended for `critical` tasks; the
  sample shows 100% line coverage with one acceptance criterion still uncovered.
- **Deterministic tests** — injected clocks, mocked I/O, seeded randomness, no order
  dependence.

## Phase & dependencies
- **Phase:** Validate / Solution (Platform Enablement) — Build→Validate boundary.
- **Upstream:** DevCopilot, SpecFlow/SpecGenerator.
- **Downstream:** Guardian, ReviewPilot, EvalHarness, CI/NexusDeploy.
- **HITL gate:** any uncovered *critical* AC in the gap report → POD Lead review.

---
SpecPod Framework v2.1.0 · Acme Corp · Confidential
