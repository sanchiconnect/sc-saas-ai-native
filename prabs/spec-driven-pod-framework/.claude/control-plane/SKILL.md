---
name: control-plane
description: "ControlPlane is the financial and security governor of the production AI system. It enforces hard monthly cost ceilings per agent and per feature, right-sizes compute allocations based on observed usage patterns, and monitors access patterns for security anomalies."
---

# SKILL.md — ControlPlane

```yaml
skill_id:      control-plane
display_name:  ControlPlane
phase:         Operate
agent_ref:     O-03
version:       1.0.0
model:         claude-haiku-4-5-20251001
token_budget:  ~25K
status:        core
```

---

## Skill Purpose

ControlPlane is the financial and security governor of the production AI system. It enforces hard monthly cost ceilings per agent and per feature, right-sizes compute allocations based on observed usage patterns, and monitors access patterns for security anomalies. When consumption reaches 70% of a monthly ceiling it alerts the POD Lead with a projected overrun date. At 100% it blocks further consumption — protecting the organisation from unbounded AI billing events that are a unique risk of AI-native systems. It also produces and maintains the `cost-config.yaml` file that RuntimeIQ must respect when making scaling decisions. Security posture monitoring detects access pattern anomalies (unusual call volumes, off-hours access, new IP/principal patterns) and alerts the POD Lead for investigation.

---

## Trigger Phrases

```
"run ControlPlane"
"set up cost governance"
"configure cost ceilings"
"monitor AI costs"
"set budget limits"
"cost and security posture setup"
"FitOps configuration"
"production cost management"
"security anomaly monitoring"
```

---

## Input Contract

### Read-Only Source Files (from manifest)

| File | Phase Origin | What the skill reads |
|---|---|---|
| `artifacts/openspec.yaml` | Phase 3 — Planning | Per-feature resource requirements, token budgets declared in spec |
| `artifacts/deploy-manifest.yaml` | Build/Deploy | All deployed agents and services — used to enumerate what needs cost ceilings |
| `artifacts/roi-brief.md` | Phase 3 — ValueModeler | Sprint budget context: approved spend per feature cluster |
| `specs/design.md` | Phase 2 — Knowledge | Architecture decisions affecting resource footprint |

### Runtime Inputs (live data / user-elicited)

| Input | Source | Required? | Notes |
|---|---|---|---|
| Monthly cost ceiling per agent | Elicitation Q2 | Yes | Hard limit in USD or chosen currency |
| Alert threshold % | Elicitation Q3 | Yes | Default 70% |
| Observability/billing data source | Elicitation Q4 | Yes | Where to pull cost data from |
| Security monitoring: anomaly sensitivity | Elicitation Q5 | Yes | Low / medium / high |
| Alert notification channel | Elicitation Q6 | Yes | Same or different from RuntimeIQ |
| Currency | Elicitation Q1 | Yes | Default: USD |

---

## Elicitation Protocol

### Q&A Sequence

```yaml
questions:
  - id: Q1
    required: true
    prompt: |
      What currency should ControlPlane use for cost tracking?
    type: single_select
    options: [USD, GBP, EUR, AUD, INR, Other (specify)]
    default: USD
    depends_on: null

  - id: Q2
    required: true
    prompt: |
      I will now collect monthly cost ceilings per deployed agent/service.
      First: does `artifacts/deploy-manifest.yaml` exist so I can enumerate agents automatically?
      (yes / no)
    type: single_select
    options: [yes, no]
    depends_on: null

  - id: Q2b
    required: true
    prompt: |
      deploy-manifest.yaml not found. List the agent/service names to govern costs for,
      comma-separated (e.g. summarisation-api, classification-api, recommendation-api):
    type: free_text
    validation: "Non-empty comma-separated list"
    depends_on: "Q2 == no"

  - id: Q3
    required: true
    prompt: |
      For each agent, set the monthly cost ceiling in [Q1 currency].
      Format: agent_name=amount, one per line. Example:
        summarisation-api=500
        classification-api=200
        recommendation-api=800
      Enter values (or type "all=<amount>" to apply one ceiling to all agents):
    type: free_text
    validation: "Each line must be: string=positive_number"
    depends_on: null

  - id: Q4
    required: true
    prompt: |
      At what percentage of the monthly ceiling should ControlPlane send a WARNING alert?
      (Recommended: 70. Range: 50–90):
    type: numeric
    validation: "Integer between 50 and 90"
    default: "70"
    depends_on: null

  - id: Q5
    required: true
    prompt: |
      Where does billing / cost data come from? Select one:
    type: single_select
    options:
      - Anthropic API usage dashboard (via API key)
      - AWS Cost Explorer
      - Azure Cost Management
      - GCP Billing API
      - Custom cost tracking endpoint (provide URL)
      - Manual input / no automated billing feed
    depends_on: null

  - id: Q5b
    required: true
    prompt: "Provide the billing endpoint URL or API key reference (env var name):"
    type: free_text
    depends_on: "Q5 in ['Anthropic API usage dashboard (via API key)', 'Custom cost tracking endpoint (provide URL)']"

  - id: Q6
    required: true
    prompt: |
      Set security anomaly detection sensitivity:
    type: single_select
    options:
      - Low (alert on severe anomalies: >5× normal call volume, unknown principals)
      - Medium (alert on >2× normal call volume, off-hours spikes, new IPs) — RECOMMENDED
      - High (alert on any deviation from baseline access pattern)
    default: "Medium"
    depends_on: null

  - id: Q7
    required: true
    prompt: |
      Where should ControlPlane send cost and security alerts?
    type: single_select
    options:
      - Same channel as RuntimeIQ (reuse config)
      - Slack (provide webhook URL)
      - Email (provide address)
      - PagerDuty (provide integration key)
      - Console / log only
    depends_on: null

  - id: Q7b
    required: true
    prompt: "Provide the alert destination value:"
    type: free_text
    depends_on: "Q7 not in ['Same channel as RuntimeIQ (reuse config)', 'Console / log only']"
```

### Confirmation Gate

```
ControlPlane Configuration Summary
─────────────────────────────────────────────
Currency              : [Q1]
Agents governed       : [list from manifest or Q2b]
Cost ceilings         : [Q3 parsed values]
Warning alert at      : [Q4]% of ceiling
Billing data source   : [Q5]
Security sensitivity  : [Q6]
Alert channel         : [Q7] → [Q7b]
─────────────────────────────────────────────
Type CONFIRM to generate all ControlPlane artifacts, or EDIT <Q-number> to change a value.
```

---

## Processing Logic

1. **Build agent registry** — From `deploy-manifest.yaml` (or Q2b), create a complete list of agents/services to govern. Cross-reference with `openspec.yaml` to pull any declared token budgets.

2. **Generate cost-config.yaml** — Write the master cost governance config at `operate/control-plane/cost-config.yaml`. This is the file read by RuntimeIQ for scaling bounds.

3. **Generate cost monitor script** — Produce `control-plane-monitor.py` that:
   - Polls the billing API/endpoint on a configured schedule (daily default)
   - Computes month-to-date spend per agent
   - Projects end-of-month spend based on daily burn rate
   - Sends WARNING alert at Q4% threshold with projected overrun date
   - Sends CRITICAL alert and triggers consumption block at 100%

4. **Generate consumption block** — Based on deployment target, generate the enforcement mechanism:
   - Kubernetes: `cost-limit-networkpolicy.yaml` (blocks outbound API calls when ceiling hit)
   - API gateway: request throttling rule config
   - Generic: `cost-gate.py` middleware wrapper

5. **Generate security monitor** — Produce `security-monitor.py` that:
   - Reads access logs from the observability stack
   - Establishes a rolling baseline of normal access patterns
   - Flags anomalies per the Q6 sensitivity setting
   - Writes to `operate/control-plane/security-event-log.md`

6. **Generate cost dashboard** — Produce `cost-dashboard.json` showing per-agent spend vs. ceiling with projected burn rate curves.

7. **Write feedback loop contribution**.

---

## Output Contract

| Output File | Location | Format | Description |
|---|---|---|---|
| `cost-config.yaml` | `operate/control-plane/` | YAML | Master cost governance: ceilings, thresholds, scaling bounds |
| `control-plane-monitor.py` | `operate/control-plane/` | Python | Billing poller, threshold evaluator, alert sender |
| `cost-gate.py` | `operate/control-plane/` | Python | Consumption enforcement middleware |
| `cost-limit-networkpolicy.yaml` | `operate/control-plane/` | YAML | Kubernetes NetworkPolicy for cost enforcement (if K8s target) |
| `security-monitor.py` | `operate/control-plane/` | Python | Access pattern anomaly detector |
| `cost-dashboard.json` | `operate/control-plane/` | JSON | Per-agent spend vs. ceiling dashboard |
| `cost-event-log.md` | `operate/control-plane/` | Markdown | Running log of cost alerts and ceiling hits |
| `security-event-log.md` | `operate/control-plane/` | Markdown | Security anomaly log for POD Lead investigation |

### Feedback Loop Contribution

```yaml
control_plane:
  generated_at: "ISO-8601"
  summary: "Cost status: N agents tracked. X at warning level. Security: Y anomalies."
  triggers:
    - agent_id: string
      month_to_date_spend: float
      ceiling: float
      utilisation_pct: float
      projected_overrun_date: string | null
      severity: info | warning | critical
  severity: info | warning | critical
```

---

## Downstream Consumers

| Output File | Consumed By | How |
|---|---|---|
| `cost-config.yaml` | RuntimeIQ | Scaling bounds and cost ceiling enforcement |
| `security-event-log.md` | IncidentLens | Security events fed into incident pattern analysis |
| `feedback-loop-triggers.yaml` | Next sprint planning | Cost overrun trends inform next sprint budget planning |

---

## Error Handling

| Condition | Behaviour |
|---|---|
| Billing API unreachable | Log warning; use last known spend + conservative daily estimate; alert POD Lead |
| `deploy-manifest.yaml` missing | Trigger Q2b to enumerate agents manually |
| Ceiling already exceeded at first run | Immediately generate CRITICAL alert; do not block until POD Lead confirms |
| Security baseline not established | Run for 7 days in observation-only mode before alerting |

---

## HITL Gates

| Gate | Condition | Reviewer | Blocks |
|---|---|---|---|
| Pre-run | CONFIRM received | POD Lead | All generation |
| Ceiling enforcement activation | First time consumption block would fire | POD Lead | Block activation |
| Security alert | Any security anomaly flagged | POD Lead | Investigation required before clearing |

---

## Metadata

```yaml
author:        SpecPod Framework
framework_ref: 02e_SpecPod-sprint-specs-operate.html (O-03)
manifest_ref:  061-generated-files-manifest.txt
created:       2025-01
```
