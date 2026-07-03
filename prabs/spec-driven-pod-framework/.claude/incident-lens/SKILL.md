---
name: incident-lens
description: "IncidentLens converts repeated production incidents from a cost centre into a product improvement signal. It ingests incident logs, RuntimeIQ SLA metrics at the time of incidents, resolution steps, and historical incident data to classify every incident as one-off, pattern, or systemic."
---

# SKILL.md — IncidentLens

```yaml
skill_id:      incident-lens
display_name:  IncidentLens
phase:         Operate
agent_ref:     O-05
version:       1.0.0
model:         claude-sonnet-4-20250514
token_budget:  ~60K
status:        core
```

---

## Skill Purpose

IncidentLens converts repeated production incidents from a cost centre into a product improvement signal. It ingests incident logs, RuntimeIQ SLA metrics at the time of incidents, resolution steps, and historical incident data to classify every incident as one-off, pattern, or systemic. For pattern and systemic incidents it traces root causes — spec gaps, missing edge case tests, infrastructure limits, dependency failures — and produces actionable sprint backlog items. Crucially, it distinguishes between incidents that require a hotfix and those that require a spec change, routing them correctly. Over 4–6 sprints it builds a failure intelligence base that makes the planning session measurably more informed.

---

## Trigger Phrases

```
"run IncidentLens"
"analyse incidents"
"log a new incident"
"classify incidents"
"find incident patterns"
"post-incident analysis"
"identify systemic failures"
"generate incident report"
"what incidents recur"
```

---

## Input Contract

### Read-Only Source Files (from manifest)

| File | Phase Origin | What the skill reads |
|---|---|---|
| `artifacts/openspec.yaml` | Phase 3 — Planning | Spec baseline — used to classify if an incident is caused by a spec gap |
| `artifacts/deploy-manifest.yaml` | Build/Deploy | Deployment version at time of incident; dependency versions |
| `operate/runtime-iq/sla-breach-log.md` | Operate — RuntimeIQ | SLA metrics at time of incidents |
| `operate/runtime-iq/thresholds.yaml` | Operate — RuntimeIQ | NFR baselines for context |
| `operate/control-plane/security-event-log.md` | Operate — ControlPlane | Security events to cross-reference with incidents |

### Runtime Inputs (live data / user-elicited)

| Input | Source | Required? | Notes |
|---|---|---|---|
| New incident details | Elicitation Q1–Q6 | Yes | Structured intake for each new incident |
| Pattern lookback window | Elicitation Q7 | Yes | How many sprints of history to analyse |
| Classification thresholds | Elicitation Q8 | Yes | At what recurrence count to escalate classification |

---

## Elicitation Protocol

> IncidentLens operates in two modes:
> **Mode A — Log New Incident**: User has a new incident to record and analyse.
> **Mode B — Analyse Existing Log**: User wants pattern analysis on accumulated history.
> The skill asks which mode first.

### Q&A Sequence

```yaml
questions:
  - id: Q0
    required: true
    prompt: |
      IncidentLens operates in two modes:
        A) Log and analyse a NEW incident
        B) Analyse patterns in EXISTING incident history
      Which mode?
    type: single_select
    options: ["A) Log new incident", "B) Analyse existing history"]
    depends_on: null

  # ── MODE A: New Incident Intake ────────────────────────────────────────────

  - id: Q1
    required: true
    prompt: |
      [Mode A] Incident timestamp — when did the incident start? (ISO format: YYYY-MM-DDTHH:MM:SSZ)
    type: free_text
    validation: "Valid ISO-8601 datetime"
    depends_on: "Q0 == 'A) Log new incident'"

  - id: Q2
    required: true
    prompt: |
      Which feature(s) / service(s) were affected? (comma-separated if multiple)
    type: free_text
    validation: "Non-empty string"
    depends_on: "Q0 == 'A) Log new incident'"

  - id: Q3
    required: true
    prompt: |
      Describe the incident symptom — what was observable from a user or system perspective:
    type: free_text
    validation: "Non-empty string, minimum 10 characters"
    depends_on: "Q0 == 'A) Log new incident'"

  - id: Q4
    required: true
    prompt: |
      What was the error type / category? Select closest match:
    type: single_select
    options:
      - Latency spike (SLA breach)
      - Error rate spike (5xx)
      - Incorrect AI output (semantic failure)
      - Complete service outage
      - Data loss / corruption
      - Security event
      - Dependency failure (upstream service)
      - Cost overrun / throttling
      - Other (describe in Q3)
    depends_on: "Q0 == 'A) Log new incident'"

  - id: Q5
    required: true
    prompt: |
      What resolution steps were taken? (describe chronologically)
    type: free_text
    validation: "Non-empty string"
    depends_on: "Q0 == 'A) Log new incident'"

  - id: Q6
    required: true
    prompt: |
      What was the root cause, if known? (or enter "unknown"):
    type: free_text
    depends_on: "Q0 == 'A) Log new incident'"

  - id: Q6b
    required: true
    prompt: |
      Was the incident resolved? If yes, what is the verified fix?
    type: single_select
    options:
      - "Yes — hotfix deployed"
      - "Yes — config change applied"
      - "Yes — rolled back to previous version"
      - "Yes — resolved without code change (transient)"
      - "No — still open"
    depends_on: "Q0 == 'A) Log new incident'"

  # ── MODE B: Pattern Analysis ───────────────────────────────────────────────

  - id: Q7
    required: true
    prompt: |
      [Mode B] How many sprints of incident history should be included in the analysis?
      (Enter integer; uses all available history if fewer sprints exist):
    type: numeric
    validation: "Integer between 1 and 52"
    default: "6"
    depends_on: "Q0 == 'B) Analyse existing history'"

  - id: Q8
    required: true
    prompt: |
      Set classification escalation thresholds:
      - At what recurrence count should an incident be classified as a PATTERN?
      - At what count should it be classified as SYSTEMIC?
      Enter as: pattern_count,systemic_count (e.g. 2,4):
    type: free_text
    validation: "Format: integer,integer where pattern_count < systemic_count"
    default: "2,4"
    depends_on: "Q0 == 'B) Analyse existing history'"

  - id: Q9
    required: true
    prompt: |
      Should backlog items for systemic issues be generated in a specific format?
    type: single_select
    options:
      - Plain Markdown (operate/incident-lens/backlog-items.md)
      - YAML task format (compatible with Conductor sprint-board)
      - Both
    depends_on: "Q0 == 'B) Analyse existing history'"
```

### Confirmation Gate

**Mode A:**
```
New Incident Summary
─────────────────────────────────────────────
Timestamp     : [Q1]
Affected      : [Q2]
Symptom       : [Q3]
Error type    : [Q4]
Resolution    : [Q5]
Root cause    : [Q6]
Status        : [Q6b]
─────────────────────────────────────────────
Type CONFIRM to log this incident and run pattern analysis, or EDIT <Q-number> to change.
```

**Mode B:**
```
Pattern Analysis Configuration
─────────────────────────────────────────────
Lookback window    : [Q7] sprints
Pattern threshold  : [Q8 parsed]
Backlog format     : [Q9]
─────────────────────────────────────────────
Type CONFIRM to run pattern analysis, or EDIT <Q-number> to change.
```

---

## Processing Logic

### Mode A — Log New Incident

1. **Append to incident log** — Write structured incident entry to `operate/incident-lens/incident-log.md` in the standard incident table format.

2. **Cross-reference SLA data** — Read `operate/runtime-iq/sla-breach-log.md` and extract SLA metrics within ±30 minutes of the incident timestamp. Append to incident record.

3. **Classify incident** — Use Claude Sonnet to:
   - Check if this incident has a matching pattern in the existing log
   - Classify as: `one-off | pattern | systemic`
   - Identify if root cause maps to a spec gap in `openspec.yaml`

4. **Enrich RunbookSynth** — If root cause and verified fix are known, write enrichment data to `operate/incident-lens/runbook-enrichments.yaml` for RunbookSynth to consume.

5. **Trigger feedback loop update**.

### Mode B — Pattern Analysis

1. **Load full incident history** — Read all entries from `operate/incident-lens/incident-log.md`.

2. **Cluster by error type and affected feature** — Group incidents into clusters. Apply Q8 thresholds to classify each cluster.

3. **Root cause analysis** — For each pattern/systemic cluster, use Claude Sonnet to:
   - Identify the common thread across incidents
   - Trace to spec, infrastructure, or dependency root cause
   - Classify root cause type: spec_gap | missing_test | infrastructure_limit | dependency_failure | data_quality

4. **Generate backlog items** — For each systemic cluster, produce a sprint backlog item in Q9 format with: problem statement, affected features, root cause, recommended sprint action.

5. **Generate incident report** — Produce/update `operate/incident-lens/incident-pattern-report.md`.

6. **Write feedback loop contribution**.

---

## Output Contract

| Output File | Location | Format | Description |
|---|---|---|---|
| `incident-log.md` | `operate/incident-lens/` | Markdown | Classified incident history with pattern flags |
| `incident-pattern-report.md` | `operate/incident-lens/` | Markdown | Pattern analysis: clusters, root causes, systemic issues |
| `backlog-items.md` | `operate/incident-lens/` | Markdown | Sprint backlog recommendations for systemic issues |
| `backlog-items.yaml` | `operate/incident-lens/` | YAML | Machine-readable backlog for Conductor consumption |
| `runbook-enrichments.yaml` | `operate/incident-lens/` | YAML | Known issue + verified fix data for RunbookSynth |

### Feedback Loop Contribution

```yaml
incident_lens:
  generated_at: "ISO-8601"
  summary: "N incidents logged. X patterns identified. Y systemic issues requiring sprint action."
  triggers:
    - cluster_id: string
      classification: one-off | pattern | systemic
      affected_features: list
      root_cause_type: spec_gap | missing_test | infrastructure_limit | dependency_failure
      recurrence_count: integer
      recommended_action: string
      severity: info | warning | critical
  severity: info | warning | critical
```

---

## Downstream Consumers

| Output File | Consumed By | How |
|---|---|---|
| `incident-log.md` | RunbookSynth | Known issues and verified fixes populate runbooks |
| `incident-log.md` | RuntimeIQ | SLA context for new incidents |
| `backlog-items.yaml` | Conductor (next sprint) | Systemic issues injected into sprint board |
| `runbook-enrichments.yaml` | RunbookSynth | Enriches runbooks with incident-derived playbooks |
| `feedback-loop-triggers.yaml` | Planning session | Incident patterns inform next sprint scope |

---

## Error Handling

| Condition | Behaviour |
|---|---|
| `incident-log.md` absent (Mode B) | Warn: `"No incident history yet. Run Mode A after each incident for 4–6 sprints."` |
| Fewer sprints than Q7 lookback | Analyse all available; note in report: `"Analysed N sprints (fewer than requested)"` |
| Root cause unknown | Log incident without root cause; flag as `root_cause_status: pending_investigation` |
| SLA log absent for cross-reference | Skip SLA enrichment; note in incident record |

---

## HITL Gates

| Gate | Condition | Reviewer | Blocks |
|---|---|---|---|
| Pre-run | CONFIRM received | POD Lead | Incident logging and analysis |
| Systemic backlog item | Any systemic classification | POD Lead | Backlog item written to sprint board |
| Security incident | Error type = Security event | POD Lead | ControlPlane notification sent immediately |

---

## Metadata

```yaml
author:        SpecPod Framework
framework_ref: 02e_SpecPod-sprint-specs-operate.html (O-05)
manifest_ref:  061-generated-files-manifest.txt
created:       2025-01
```
