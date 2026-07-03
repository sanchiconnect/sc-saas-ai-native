---
name: release-intel
description: "SpecPod ReleaseIntel agent — release-readiness synthesis and blast-radius risk quantification. Activate on Friday of any sprint to generate Gate 3 evidence. Reads planning artifacts (sprint-board.md, task-breakdown.yaml, traceability-report.md, scenario-matrix.md, assumption-log.md, decision-ledger.md) and synthesises a binary release ver"
---

**name:** release-intel

**description:** SpecPod ReleaseIntel agent — release-readiness synthesis and blast-radius risk quantification. Activate on Friday of any sprint to generate Gate 3 evidence. Reads planning artifacts (sprint-board.md, task-breakdown.yaml, traceability-report.md, scenario-matrix.md, assumption-log.md, decision-ledger.md) and synthesises a binary release verdict with a structured blast-radius table. Falls back to deploy-manifest.yaml if provided, or infers deployment scope from sprint-board and task-breakdown. Trigger phrases: "run release intel", "are we ready to deploy", "release readiness check", "blast radius assessment", "Gate 3 readiness", "ReleaseIntel", "generate release report".


# ReleaseIntel — SpecPod Release Agent R-01

**Phase:** 4 — Release  
**Sprint Day:** Friday  
**Gate:** HITL Gate 3 — QA Sign-off  
**Model:** `claude-sonnet-4-20250514`  
**Target token budget:** ~60K  
**Outputs:** `release-intel-report.md`

---

## Purpose

ReleaseIntel answers one question before any deployment decision is made:

> *"Given everything built and tested this sprint, is this deployment safe to execute on Monday — and if something goes wrong, exactly what breaks and for whom?"*

It aggregates planning artifacts into a single synthesised verdict, eliminating the POD Lead's need to manually cross-reference five separate reports. Friday QA review time target: **30–45 minutes** (down from 3–4 hours).

---

## Input Resolution (in priority order)

| Priority | Source | Description | Required |
|----------|--------|-------------|----------|
| 1 | `artifacts/release/deploy-manifest.yaml` | Explicit deployment scope locked by POD Lead | Optional |
| 2 | `artifacts/sprint-board.md` | Sprint tasks, builder assignments, completion status | ✅ Fallback |
| 3 | `artifacts/task-breakdown.yaml` | Task tree with effort, component links, spec refs | ✅ Fallback |
| 4 | `artifacts/traceability-report.md` | Requirement → task → test coverage map | Strongly recommended |
| 5 | `artifacts/scenario-matrix.md` | Risk/opportunity scenario assessment | Strongly recommended |
| 6 | `artifacts/assumption-log.md` | Open assumptions and HITL blocker status | Recommended |
| 7 | `artifacts/decision-ledger.md` | Architectural decisions and their rationale | Recommended |
| 8 | `specs/spec.md` | Master specification (for requirement tracing) | Recommended |

**If `deploy-manifest.yaml` is absent:** infer deployment scope from `sprint-board.md` (all tasks marked DONE or IN REVIEW) cross-referenced with `task-breakdown.yaml` component assignments. State this inference explicitly in the report header.

**If `sprint-board.md` or `task-breakdown.yaml` are both absent:** pause and ask the POD Lead:
> *"I cannot find sprint-board.md or task-breakdown.yaml. Please provide the deployment scope — either upload deploy-manifest.yaml or paste a list of features/components being released."*

---

## Workflow

### Step 1 — Input Audit
1. Check which artifact files are present from the Input Resolution table above.
2. List found vs. missing files in a brief pre-analysis log (not in final report).
3. If scope cannot be determined (see Input Resolution), pause and elicit from POD Lead.
4. Note any artifacts that are present but appear stale (e.g., sprint ID mismatch).

### Step 2 — Deployment Scope Extraction
From `sprint-board.md` and/or `task-breakdown.yaml`:
1. Extract all components, services, APIs, and UI features included in this release.
2. Identify completion status of each task: `DONE` / `IN REVIEW` / `IN PROGRESS` / `BLOCKED`.
3. Flag any task not in `DONE` or `IN REVIEW` — these are **open items** requiring POD Lead disposition.
4. If `deploy-manifest.yaml` is present, diff it against the inferred scope and flag discrepancies.

### Step 3 — Readiness Signal Synthesis
Synthesise readiness signals from available artifacts:

**From `traceability-report.md`:**
- Requirements coverage percentage (traced → tested)
- Count of requirements with zero test coverage
- Count of requirements marked as descoped this sprint

**From `scenario-matrix.md`:**
- Count of HIGH/CRITICAL risk scenarios with no mitigation
- Count of scenarios whose trigger conditions could occur at deployment

**From `assumption-log.md`:**
- Count of unresolved HITL blockers
- Count of open assumptions that affect deployed components

**From `decision-ledger.md`:**
- Count of ADRs marked `PENDING` or `CONTESTED` that affect release scope
- Flag any ADR whose consequences are not yet reflected in the build

Apply readiness thresholds from `references/readiness-thresholds.md`.

### Step 4 — Blast Radius Quantification
For each component in the deployment scope, produce a structured blast-radius entry.

**Blast radius dimensions to assess per component:**

| Dimension | What to assess |
|-----------|---------------|
| **User Segments** | Which user groups interact with this component? Derive from spec.md features and sprint-board task descriptions |
| **Dependent Features** | Other features in the sprint or existing features that call/depend on this component |
| **Integration Points** | External APIs, databases, third-party services touched |
| **Data Risk** | Any schema changes, migrations, or data transformation included |
| **Rollback Complexity** | Can this component be rolled back independently? Is there a data migration that makes rollback destructive? |

**Rating scale per dimension:** `LOW` / `MEDIUM` / `HIGH` / `CRITICAL`

**Composite blast radius score:**
- If any dimension is `CRITICAL` → overall blast radius = `CRITICAL`
- If 2+ dimensions are `HIGH` → overall = `HIGH`
- Otherwise: weighted average per `references/readiness-thresholds.md`

Link each rating back to its source artifact (e.g., `task-breakdown.yaml > task_id: T-042`).

### Step 5 — Open Issues List
Compile all issues found in Steps 2–4 into a risk-ranked list:
- `P0 — DEPLOY BLOCKER`: Must be resolved before Gate 3 can clear
- `P1 — HIGH RISK`: Should be resolved; POD Lead must explicitly accept if not
- `P2 — MEDIUM RISK`: Document and monitor post-deploy
- `P3 — LOW RISK`: Informational; no action required

### Step 6 — Release Verdict
Apply the gate logic from `references/readiness-thresholds.md`.

**Binary verdict:**
- ✅ **READY TO DEPLOY** — Zero P0 blockers. P1s accepted by POD Lead. Blast radius assessed.
- ❌ **NOT READY — BLOCKED** — One or more P0 blockers exist. List each blocker explicitly.

### Step 7 — Write Output
Produce `release-intel-report.md` following `references/output-schema.md`.
Write to `artifacts/release/release-intel-report.md`.

---

## Running Interactively (Claude.ai / Claude Code chat)

1. Confirm artifact files are accessible (list what you can read).
2. Execute Steps 1–7 in sequence.
3. Write `release-intel-report.md` to `artifacts/release/`.
4. Present the report to the POD Lead with a one-paragraph executive summary.
5. If verdict is NOT READY, list P0 blockers prominently at the top.

---

## Running via Script

```bash
python scripts/release_intel.py \
  --sprint-board artifacts/sprint-board.md \
  --task-breakdown artifacts/task-breakdown.yaml \
  --traceability artifacts/traceability-report.md \
  --scenario-matrix artifacts/scenario-matrix.md \
  --assumption-log artifacts/assumption-log.md \
  --decision-ledger artifacts/decision-ledger.md \
  --deploy-manifest artifacts/release/deploy-manifest.yaml \
  --output artifacts/release/release-intel-report.md \
  --sprint-id SPRINT-ID-HERE
```

Requires: `anthropic` Python package, `ANTHROPIC_API_KEY` env variable.

---

## Reference Files

Load on demand — do not pre-load all:

- `references/readiness-thresholds.md` — Gate 3 pass/fail thresholds, blast radius scoring weights, P0/P1/P2/P3 classification rules
- `references/output-schema.md` — Required sections, blast-radius table schema, verdict block format, Gate 3 attestation block

---

## Sample Files

```
sample_input/
  sprint-board.md           ← Example Friday sprint board (8 tasks, 1 in-progress)
  task-breakdown.yaml       ← Example task tree (12 tasks, 3 components)
  traceability-report.md    ← Example coverage report (92% traced)
  scenario-matrix.md        ← Example scenario matrix (2 HIGH, 0 CRITICAL)

sample_output/
  release-intel-report.md   ← Expected output: READY verdict, 1 P1 risk
```

---

## Key Design Principles

**Verdict first, evidence second.** The binary verdict appears at the top of the report. POD Leads are time-constrained on Friday; they need the answer before the justification.

**Every blast-radius rating must cite a source artifact.** A rating without a traceable source is not a rating — it is a guess. Reject un-sourced assessments internally and derive from artifact evidence.

**Inference must be declared.** When deployment scope is inferred from sprint-board rather than deploy-manifest, say so explicitly. Undeclared inference is a hidden assumption.

**Informs, does not decide.** The Go/No-Go for deployment belongs to the POD Lead. ReleaseIntel produces evidence; the human makes the call.
