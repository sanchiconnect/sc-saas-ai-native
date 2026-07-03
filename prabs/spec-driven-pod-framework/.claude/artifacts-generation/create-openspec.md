**name:** create-openspec

**description:** Sprint Artifact Generator — detects missing `artifacts/openspec.yaml` and/or `artifacts/sprint-capacity.yaml` and generates them through a targeted elicitation with the POD Lead. Invoke when Conductor, SpecFlow, or any downstream skill reports either file absent, or directly via phrases like "generate openspec", "create sprint spec", "initialize sprint", "generate sprint capacity". Reads `specs/program.md`, `specs/tasks.md`, and `specs/design.md` first to pre-fill what it can — only asks for what cannot be inferred.


# SKILL: CreateOpenspec
**SpecPod Framework v2.1.0 · Planning · 00**
**Model:** claude-sonnet-4-6 · **Context Budget:** ~80K tokens
**Role:** Sprint artifact bootstrapper — generates `openspec.yaml` and `sprint-capacity.yaml` when either is absent

---

## Purpose

CreateOpenspec is the prerequisite guardian for sprint planning. Any skill that requires `artifacts/openspec.yaml` or `artifacts/sprint-capacity.yaml` (Conductor, SpecFlow, PolicyCatalog, TraceGraph, Guardian, PerformanceOptimizer) may invoke this skill to bootstrap the missing files. It reads all available spec context first, pre-fills what it can infer, then runs a focused interview to cover only the remaining gaps.

---

## Trigger

**Invoked by other skills** when they detect a missing input file.

**Invoked directly** by the POD Lead with any of:
- `generate openspec` / `create openspec.yaml`
- `generate sprint capacity` / `create sprint-capacity.yaml`
- `initialize sprint` / `set up sprint artifacts`
- `run CreateOpenspec`

---

## Step 0 — Detection

Before asking any questions, check file presence and available context:

```
artifacts/openspec.yaml:         EXISTS | MISSING
artifacts/sprint-capacity.yaml:  EXISTS | MISSING

Context sources (read if present):
  specs/program.md   → program_id, program_name, pod_lead, phases, NFRs
  specs/tasks.md     → module names, task estimates
  specs/design.md    → tech stack, architecture, compliance rules
  specs/knowledge.md → business rules, domain entities
```

Print a detection report and halt if both files already exist:

```
## CreateOpenspec — Detection Report

artifacts/openspec.yaml:         [EXISTS | MISSING]
artifacts/sprint-capacity.yaml:  [EXISTS | MISSING]

Pre-fill context:
  specs/program.md:   [FOUND — will pre-fill program_id, program_name, pod_lead | NOT FOUND]
  specs/tasks.md:     [FOUND — will suggest modules and estimates | NOT FOUND]
  specs/design.md:    [FOUND — will inform NFRs and policy rails | NOT FOUND]

Action: [GENERATING openspec.yaml | GENERATING sprint-capacity.yaml | GENERATING BOTH | NOTHING TO DO — both files present]
```

---

## Part A — `openspec.yaml`

Skip if `artifacts/openspec.yaml` already exists.

### A0 — Pre-fill and Confirm

Extract from available specs and present for confirmation before asking anything:

```
Pre-filled from specs — confirm or correct before we continue:
  program_id:   [value | not found — please provide]
  program_name: [value | not found — please provide]
  pod_lead:     [value | not found — please provide]
  Modules from tasks.md: [list | none detected]
  NFRs from design.md:   [list | none detected]

Type CONFIRM to proceed, or correct any field inline.
```

### A1 — Sprint Identity

Ask as one grouped block:

```
SPRINT IDENTITY
  1. Sprint ID          (e.g. SPRINT-002)
  2. Sprint name        (short descriptive title)
  3. Phase              (e.g. "Phase 2 (Weeks 5–8)")
  4. Sprint start date  (YYYY-MM-DD)
  5. Sprint end date    (YYYY-MM-DD)
  6. Planning day       (the Monday reserved for planning — no build dispatch)
  7. Pod Lead           (confirm or override pre-filled value)
```

### A2 — Sprint Goals

Collect 1–4 goals, one at a time:

```
SPRINT GOAL [n]
  Goal statement:      What must the system do by end of sprint?
  Success indicator:   How will you verify this is achieved? (concrete, observable)

(Type DONE when all goals are entered.)
```

### A3 — In-Scope Modules

Pre-populate from `specs/tasks.md` if available. For each module:

```
MODULE [n]: [pre-filled name or "new module"]
  Module ID:          (e.g. MOD-ING)
  Module name:        [pre-filled or enter]
  Source domain:      Code path prefix (e.g. src/pipeline/ingestion/)
  Description:        What does this module deliver this sprint?
  Acceptance criteria: One per line — type DONE when complete
  Dependencies:       Prerequisites (modules, credentials, systems) — DONE when complete
  NFR references:     Performance/availability/security NFRs — SKIP if none
  Out-of-scope note:  What is explicitly excluded from this module — SKIP if none

(Type NEXT MODULE to add another, DONE WITH MODULES when finished.)
```

### A4 — Out of Scope

```
OUT OF SCOPE — this sprint
  List items explicitly excluded (one per line). Type DONE when complete.
```

### A5 — Open Decisions

```
OPEN DECISIONS (SKIP if none)
  For each unresolved question affecting this sprint:
    Decision ID:       (e.g. OD-004)
    Description:       What is unresolved?
    Impact:            How does it affect sprint work?
    Resolution owner:  Who must resolve it?
    Required before:   Which milestone needs this resolved?
    Sprint impact:     LOW / MEDIUM / HIGH

  Type NEXT for another, SKIP or DONE if none.
```

### A6 — Policy Rails

```
POLICY RAILS (pre-populated from design.md if available — SKIP if none)
  For each compliance or audit constraint builders must inject into code:
    Policy ID:    (e.g. POL-AUDIT-001)
    Applies to:   Module IDs (comma-separated)
    Description:  The constraint to enforce

  Type NEXT for another, SKIP or DONE if none.
```

### A7 — Confirm and Write

```
## openspec.yaml — Ready to Generate
  Sprint:    [sprint_id] — [sprint_name]
  Goals:     [n]
  Modules:   [n] in scope
  OOS items: [n]
  Decisions: [n] open
  Policies:  [n] rails

Type GENERATE to write artifacts/openspec.yaml,
or EDIT [section] to revise before generating.
```

---

## Part B — `sprint-capacity.yaml`

Skip if `artifacts/sprint-capacity.yaml` already exists. If `openspec.yaml` now exists, pre-fill `sprint_id`, `sprint_name`, `program_id`, `sprint_start`, `sprint_end`, and `planning_day` from it automatically.

### B1 — Builder Roster

```
BUILDER ROSTER
  How many AI Builders are active this sprint? (default: 2)

  For each builder:
    Builder ID:           (e.g. BUILDER-1)
    Role:                 (e.g. Primary Builder)
    Skill affinity:       Comma-separated skills (e.g. spec-flow, spec-database)
    Preferred task types: (e.g. Code generation, Database schema, API endpoints)
    Hours per day:        (default: 6.0)
    Available days:       Build days only — exclude planning day (e.g. Tue, Wed, Thu)
    Notes:                SKIP if none

  Type NEXT BUILDER to add another, DONE when roster is complete.
```

### B2 — Capacity and Human Spikes

Auto-calculate totals and confirm:

```
CAPACITY SUMMARY (auto-calculated — confirm or override)
  Total raw builder hours:  [builders × hours/day × build days]
  Overhead buffer %:        15 — override? (enter % or KEEP)
  Overhead hours:           [calculated]
  Net available hours:      [calculated]

Any human-led work tracked separately (e.g. spikes, investigations)?
  Owner:              Name
  Type:               e.g. Human-led investigation
  Hours:              (not deducted from builder capacity)
  Deadline:           YYYY-MM-DD
  Mid-point check-in: YYYY-MM-DD (SKIP if none)
  Output artifact:    e.g. artifacts/spike-findings.md (SKIP if none)

  Type NEXT to add another, SKIP or DONE if none.
```

### B3 — Wave Allocation

If modules exist from `openspec.yaml`, suggest a dependency-aware wave plan for confirmation. Otherwise elicit manually:

```
WAVE [n]
  Dispatch day:   (e.g. Tuesday AM)
  Description:    What does this wave accomplish?

  For each task:
    Task ref:         (e.g. T-001)
    Description:      Brief task description
    Builder:          BUILDER-1 / BUILDER-2 / ...
    Estimated hours:
    Skill:            SpecPod skill that drives this task
    Depends on:       Task refs (NONE for wave 0)

  Type NEXT TASK / NEXT WAVE / DONE WITH WAVES.
```

### B4 — Load Balancing and Risk Flags

```
LOAD BALANCING (defaults shown — type KEEP ALL or override individually)
  max_high_complexity_per_builder_per_wave: 1
  traceability_gate_before_wave_advance:    true
  decision_logging_mode:                    side-channel
  compliance_injection_mode:                cluster-prompt

RISK FLAGS (SKIP if none)
  Risk ID:     (e.g. RISK-CAP-001)
  Description: What is the risk?
  Severity:    LOW / MEDIUM / HIGH
  Mitigation:  How is it managed?

  Type NEXT for another, SKIP or DONE if none.
```

### B5 — Confirm and Write

```
## sprint-capacity.yaml — Ready to Generate
  Builders:   [n]
  Net hours:  [n]
  Waves:      [n]
  Tasks:      [n]
  Risk flags: [n]

Type GENERATE to write artifacts/sprint-capacity.yaml,
or EDIT [section] to revise before generating.
```

---

## Output: `artifacts/openspec.yaml`

```yaml
# openspec.yaml — Locked Sprint Specification
# SpecPod Framework v2.1.0 · Gate-0 Pending
# DO NOT MODIFY after lock. Any changes require a new spec version and re-run of SpecImpactAnalyzer.
# Generated by: CreateOpenspec
# Source: specs/program.md, specs/tasks.md, specs/design.md (where available)
# Generated: [YYYY-MM-DD]

meta:
  spec_version: "1.0"
  sprint_id: [sprint_id]
  sprint_name: "[sprint_name]"
  program_id: [program_id]
  program_name: "[program_name]"
  phase: "[phase]"
  sprint_start: "[YYYY-MM-DD]"
  sprint_end: "[YYYY-MM-DD]"
  pod_lead: "[pod_lead]"
  locked: false
  locked_by: null
  locked_at: null
  gate_status: "GATE-0 PENDING"

sprint_goals:
  - id: SG-001
    goal: >
      [goal]
    success_indicator: >
      [success_indicator]

in_scope:
  - module_id: [MOD-XXX]
    module_name: "[name]"
    source_domain: "[src/path/]"
    description: >
      [description]
    acceptance_criteria:
      - "[criterion]"
    dependencies:
      - "[dependency]"
    nfr_refs:
      - "[NFR-XXX: description]"
    out_of_scope_notes: >
      [note — omit this key if SKIP]

out_of_scope:
  - "[item]"

open_decisions:
  - id: [OD-XXX]
    description: "[description]"
    impact: >
      [impact]
    resolution_owner: "[owner]"
    required_before: "[milestone]"
    sprint_impact: [LOW|MEDIUM|HIGH]

policy_rails:
  - policy_id: [POL-XXX]
    applies_to: [[MOD-XXX, MOD-YYY]]
    description: "[constraint]"

hitl_gates:
  gate_0:
    name: "Spec Lock"
    status: PENDING
    cleared_by: null
    cleared_at: null
  gate_0_5:
    name: "Assumption Clearance"
    status: PENDING
  gate_1:
    name: "Plan Sign-off"
    status: PENDING
```

> **Lock note:** `locked: false` on generation. POD Lead sets `locked: true`, `locked_by`, and `locked_at` manually after review. Never auto-lock.

---

## Output: `artifacts/sprint-capacity.yaml`

```yaml
# sprint-capacity.yaml — Sprint Capacity Plan
# SpecPod Framework v2.1.0 · Conductor Input
# Generated by: CreateOpenspec
# Source: POD Lead elicitation + artifacts/openspec.yaml (where available)
# Generated: [YYYY-MM-DD]

meta:
  sprint_id: [sprint_id]
  sprint_name: "[sprint_name]"
  program_id: [program_id]
  sprint_start: "[YYYY-MM-DD]"
  sprint_end: "[YYYY-MM-DD]"
  working_days: [n]
  planning_day: "[YYYY-MM-DD]"

builders:
  - builder_id: [BUILDER-1]
    role: "[role]"
    skill_affinity: [[skill, skill]]
    preferred_task_types:
      - "[type]"
    hours_per_day: [n]
    available_days: [[Tue, Wed, Thu]]
    total_hours: [hours_per_day × len(available_days)]
    notes: >
      [notes — omit key if SKIP]

capacity_summary:
  total_raw_builder_hours: [sum of builder total_hours]
  overhead_buffer_pct: [pct]
  overhead_hours: [calculated]
  net_available_builder_hours: [calculated]
  net_build_hours: [net_available_builder_hours]

wave_allocation:
  wave_0:
    dispatch_day: "[e.g. Tuesday AM]"
    description: "[what this wave delivers]"
    planned_hours: [sum of task hours]
    tasks:
      - task_ref: [T-001]
        description: "[description]"
        builder: [BUILDER-1]
        estimated_hours: [n]
        skill: [skill-name]
        depends_on: []

# [wave_1, wave_2 … repeat as needed]

# [human spike block — include only if declared in B2]
erp_spike:
  owner: "[owner]"
  type: "[type]"
  note: >
    [note]
  deadline: "[YYYY-MM-DD]"
  milestone_check: "[YYYY-MM-DD]"
  output: "[artifacts/path.md]"

load_balancing:
  max_high_complexity_per_builder_per_wave: [n]
  traceability_gate_before_wave_advance: [true|false]
  decision_logging_mode: "[side-channel|inline]"
  compliance_injection_mode: "[cluster-prompt|separate-task]"

risk_flags:
  - id: [RISK-CAP-001]
    description: >
      [description]
    severity: [LOW|MEDIUM|HIGH]
    mitigation: >
      [mitigation]

forecast_inputs:
  total_tasks: [n]
  average_task_duration_hours: [calculated average]
  net_builder_hours_available: [net_available_builder_hours]
  estimated_completion_day: "[e.g. Thursday EOD]"
  confidence: [LOW|MEDIUM|HIGH]
```

---

## Post-Generation Summary

```
## CreateOpenspec — Complete

Files written:
  artifacts/openspec.yaml        [WRITTEN | SKIPPED — already existed]
  artifacts/sprint-capacity.yaml [WRITTEN | SKIPPED — already existed]

openspec status:
  Sprint:  [sprint_id] — [sprint_name]
  Goals:   [n] | Modules: [n] in scope | Lock: PENDING (POD Lead action required)

sprint-capacity status:
  Builders: [n] | Net hours: [n] | Waves: [n] | Tasks: [n]

Recommended next steps:
  1. Review both artifacts and correct any inferred values
  2. Set locked: true in openspec.yaml when satisfied (POD Lead)
  3. Run AssumptionTracker → PolicyCatalog → PortfolioPrioritizer
  4. Run SpecFlow once openspec is locked
  5. Run Conductor after Gate-1 (Plan Sign-off) is cleared
```

---

## Limitations

- Does not auto-lock `openspec.yaml` — locking is always a deliberate POD Lead action.
- Wave plan suggestions are dependency-aware but not load-optimal — verify wave hours against net capacity.
- Without `specs/program.md`, all program-level fields require manual entry.
- Does not produce `task-breakdown.yaml` — that is SpecFlow's output after the spec is locked.

---

## References

- `references/artifacts/openspec.yaml` — canonical completed example
- `references/artifacts/sprint-capacity.yaml` — canonical completed example
- `.claude/conductor/SKILL.md` — full artifact checklist Conductor requires
- `.claude/spec-flow/SKILL.md` — how openspec.yaml is consumed for decomposition
- `.claude/performance-optimizer/SKILL.md` — how sprint-capacity.yaml drives budget enforcement
