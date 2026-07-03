---
name: runbook-synth
description: "RunbookSynth eliminates stale operational documentation — the primary cause of extended incident resolution in rapid-iteration teams. It reads the deploy manifest, system architecture, and all available incident history to generate complete, step-by-step operational runbooks per deployed feature and integration."
---

# SKILL.md — RunbookSynth

```yaml
skill_id:      runbook-synth
display_name:  RunbookSynth
phase:         Operate
agent_ref:     O-04
version:       1.0.0
model:         claude-sonnet-4-20250514
token_budget:  ~40K
status:        core
```

---

## Skill Purpose

RunbookSynth eliminates stale operational documentation — the primary cause of extended incident resolution in rapid-iteration teams. It reads the deploy manifest, system architecture, and all available incident history to generate complete, step-by-step operational runbooks per deployed feature and integration. On each new deployment, it automatically diffs the previous runbook against the new system state and updates only the sections that changed, preserving version history. As IncidentLens surfaces root causes and verified fixes, RunbookSynth enriches the relevant runbooks with "Known Issue" and "Verified Fix" sections, so the next operator encountering the same issue has a documented resolution path rather than a blank page.

---

## Trigger Phrases

```
"run RunbookSynth"
"generate runbooks"
"create operational runbooks"
"update runbooks after deployment"
"synthesise runbooks"
"build operational playbooks"
"generate incident playbooks"
"update runbook for new deployment"
```

---

## Input Contract

### Read-Only Source Files (from manifest)

| File | Phase Origin | What the skill reads |
|---|---|---|
| `artifacts/deploy-manifest.yaml` | Build/Deploy | All deployed services, versions, configurations, dependencies, rollback plan |
| `artifacts/openspec.yaml` | Phase 3 — Planning | Feature specs, integration contracts, expected behaviours |
| `specs/design.md` | Phase 2 — Knowledge | System architecture, dependency map, infrastructure topology |
| `specs/api.md` | Phase 2 — Knowledge | API contracts, authentication, error response codes |
| `artifacts/decision-ledger.md` | Phase 3 — DecisionLedger | Architectural decisions relevant to operations |
| `operate/incident-lens/incident-log.md` | Operate — IncidentLens | Resolved incidents with root causes and verified fixes |
| `operate/drift-guard/drift-report.md` | Operate — DriftGuard | Known drift patterns to document in runbooks |

### Runtime Inputs (live data / user-elicited)

| Input | Source | Required? | Notes |
|---|---|---|---|
| Runbook audience level | Elicitation Q1 | Yes | Ops engineer / senior developer / POD Lead |
| Runbook sections to include | Elicitation Q2 | Yes | Multi-select from standard sections |
| Auto-update trigger | Elicitation Q3 | Yes | What events trigger a runbook update |
| Runbook format | Elicitation Q4 | Yes | Markdown / Confluence wiki / Notion / plain text |
| Rollback runbook required? | Elicitation Q5 | Yes | Whether to generate rollback-specific runbook |

---

## Elicitation Protocol

### Q&A Sequence

```yaml
questions:
  - id: Q1
    required: true
    prompt: |
      Who is the primary audience for these runbooks?
      This determines the assumed knowledge level and verbosity.
    type: single_select
    options:
      - POD Lead (experienced; terse, decision-focused)
      - Operations Engineer (procedural; step-by-step with commands)
      - On-call Developer (moderate; commands with brief explanations)
      - Mixed / All of the above (generates multiple verbosity sections)
    depends_on: null

  - id: Q2
    required: true
    prompt: |
      Which standard runbook sections should be generated? Select all that apply:
    type: multi_select
    options:
      - System Overview (architecture diagram reference, component map)
      - Deployment Procedures (how to deploy, rollout steps)
      - Health Check Procedures (how to verify system is healthy)
      - Scaling Procedures (how to scale up/down manually)
      - Rollback Procedures (how to revert to previous version)
      - Alert Response Playbooks (per-alert investigation and resolution steps)
      - Known Issues & Verified Fixes (populated from IncidentLens)
      - Dependency Management (how to handle upstream/downstream failures)
      - Security Incident Response (access anomalies, breach response)
      - Contact & Escalation Matrix (who to call and when)
    depends_on: null

  - id: Q3
    required: true
    prompt: |
      What events should trigger an automatic runbook update? Select all that apply:
    type: multi_select
    options:
      - New deployment (deploy-manifest.yaml changes)
      - Resolved incident added to incident-log.md
      - Drift threshold breach logged by DriftGuard
      - Manual trigger only (POD Lead explicitly re-runs RunbookSynth)
    depends_on: null

  - id: Q4
    required: true
    prompt: |
      What output format should runbooks be generated in?
    type: single_select
    options:
      - Markdown (files in operate/runbook-synth/)
      - Confluence wiki markup (for upload to Confluence)
      - Notion markdown
      - Plain text
    default: "Markdown (files in operate/runbook-synth/)"
    depends_on: null

  - id: Q5
    required: true
    prompt: |
      Should RunbookSynth generate a dedicated Rollback Runbook from the
      RolloutAdvisor rollback plan in the deploy manifest?
      (yes / no)
    type: single_select
    options: [yes, no]
    depends_on: null

  - id: Q6
    required: true
    prompt: |
      What is the current sprint/deployment version identifier?
      This is used for runbook versioning. Example: sprint-12, v2.3.1, 2025-01-deploy
    type: free_text
    validation: "Non-empty string, no spaces"
    depends_on: null
```

### Confirmation Gate

```
RunbookSynth Configuration Summary
─────────────────────────────────────────────
Target audience       : [Q1]
Sections to generate  : [Q2 selections]
Auto-update triggers  : [Q3 selections]
Output format         : [Q4]
Rollback runbook      : [Q5]
Version identifier    : [Q6]
Sources               : deploy-manifest.yaml, openspec.yaml, design.md, incident-log.md
─────────────────────────────────────────────
Type CONFIRM to generate all RunbookSynth artifacts, or EDIT <Q-number> to change a value.
```

---

## Processing Logic

1. **Parse deploy manifest** — Read `artifacts/deploy-manifest.yaml` to enumerate all deployed features, services, configs, versions, dependencies, and the rollback plan. Extract integration endpoints and health check paths.

2. **Build system context** — Read `specs/design.md` and `specs/api.md` to construct the operational context: service dependencies, failure modes, API error codes, authentication flows.

3. **Load incident history** — Read `operate/incident-lens/incident-log.md` if it exists. Extract all `RESOLVED` incidents with their root causes and verified fixes. Group by affected feature.

4. **Generate master runbook** — For each deployed feature/service, produce a `runbook-[feature-id]-[version].md` file containing only the Q2-selected sections. Use Claude Sonnet to generate prose that is appropriate for the Q1 audience.

5. **Generate alert response playbooks** — If "Alert Response Playbooks" selected in Q2, for each alert defined in RuntimeIQ's `alert-config.yaml` and `thresholds.yaml`, generate a step-by-step investigation and resolution procedure.

6. **Generate rollback runbook** — If Q5 = yes, extract the rollback plan from the deploy manifest and generate `runbook-rollback-[version].md` with ordered rollback steps, verification commands, and go/no-go criteria.

7. **Generate runbook index** — Produce `runbook-index.md` — a master index of all runbooks with their version, last-updated timestamp, and the deployment version they correspond to.

8. **Generate update trigger script** — Produce `runbook-update-trigger.sh` that watches the Q3-selected trigger files and re-invokes RunbookSynth when any changes.

9. **Version previous runbooks** — Move any existing runbooks to `operate/runbook-synth/history/` before writing new versions.

---

## Output Contract

| Output File | Location | Format | Description |
|---|---|---|---|
| `runbook-[feature-id]-[version].md` | `operate/runbook-synth/` | Markdown | Per-feature operational runbook |
| `runbook-rollback-[version].md` | `operate/runbook-synth/` | Markdown | Rollback-specific runbook (if Q5=yes) |
| `runbook-index.md` | `operate/runbook-synth/` | Markdown | Master index of all runbooks with version history |
| `runbook-update-trigger.sh` | `operate/runbook-synth/` | Shell | Watch script that triggers runbook regeneration on deploy events |
| `runbook-config.yaml` | `operate/runbook-synth/` | YAML | RunbookSynth configuration: triggers, format, audience, version |
| `history/runbook-[feature]-[prev-version].md` | `operate/runbook-synth/history/` | Markdown | Versioned history of previous runbooks |

### Feedback Loop Contribution

```yaml
runbook_synth:
  generated_at: "ISO-8601"
  summary: "Generated N runbooks for version [version]. X known issues documented."
  triggers:
    - runbook_id: string
      feature_id: string
      version: string
      sections_generated: list
      known_issues_count: integer
  severity: info
```

---

## Downstream Consumers

| Output File | Consumed By | How |
|---|---|---|
| `runbook-[feature].md` | POD Lead / On-call | Primary incident response reference |
| `runbook-rollback.md` | POD Lead | Executed during rollback decision gate |
| `runbook-index.md` | IncidentLens | Cross-references runbook version at time of incident |

---

## Error Handling

| Condition | Behaviour |
|---|---|
| `deploy-manifest.yaml` missing | Abort: `"deploy-manifest.yaml is required. Run the Deploy phase first."` |
| `incident-log.md` absent | Generate runbooks without Known Issues section; note: `"No incident history available yet"` |
| Feature in openspec not in manifest | Log warning: `"Feature [id] in spec not found in deployment. Runbook generated from spec only."` |
| Runbook generation produces empty section | Omit section silently; note in `runbook-config.yaml` as `skipped_sections: []` |

---

## HITL Gates

| Gate | Condition | Reviewer | Blocks |
|---|---|---|---|
| Pre-run | CONFIRM received | POD Lead | All generation |
| Rollback runbook review | Rollback runbook generated | POD Lead | Runbook published to index |

---

## Metadata

```yaml
author:        SpecPod Framework
framework_ref: 02e_SpecPod-sprint-specs-operate.html (O-04)
manifest_ref:  061-generated-files-manifest.txt
created:       2025-01
```
