---
name: runtime-iq
description: "RuntimeIQ is the continuous SLA sentinel for the production environment. It ingests live telemetry (latency percentiles, error rates, token consumption, agent health) and compares them against NFR targets locked in openspec.yaml."
---

# SKILL.md — RuntimeIQ

```yaml
skill_id:      runtime-iq
display_name:  RuntimeIQ
phase:         Operate
agent_ref:     O-01
version:       1.0.0
model:         claude-haiku-4-5-20251001
token_budget:  ~20K
status:        core
```

---

## Skill Purpose

RuntimeIQ is the continuous SLA sentinel for the production environment. It ingests live telemetry (latency percentiles, error rates, token consumption, agent health) and compares them against NFR targets locked in `openspec.yaml`. When any threshold is breached it alerts the POD Lead with severity, affected feature, and breach delta. It also enforces auto-scaling within the cost ceiling approved by ControlPlane — it requests scale-up but never provisions beyond the authorised budget. Every monitoring cycle contributes a structured performance summary to `feedback-loop-triggers.yaml` so the next sprint planning session starts from production evidence, not assumptions.

---

## Trigger Phrases

```
"run RuntimeIQ"
"start SLA monitoring"
"set up production monitoring"
"check SLA status"
"configure auto-scaling"
"monitor latency and errors"
"production health check"
"generate SLA dashboard"
```

---

## Input Contract

### Read-Only Source Files (from manifest)

| File | Phase Origin | What the skill reads |
|---|---|---|
| `artifacts/openspec.yaml` | Phase 3 — Planning | NFR SLA targets: latency budgets, error rate thresholds, availability targets per feature |
| `artifacts/deploy-manifest.yaml` | Build/Deploy | Deployed services, endpoints, agent identifiers, replica counts |
| `specs/design.md` | Phase 2 — Knowledge | Architecture topology: services, dependencies, expected traffic patterns |
| `operate/control-plane/cost-config.yaml` | Operate — ControlPlane | Hard cost ceiling and approved scaling bounds per agent/service |

### Runtime Inputs (live data / user-elicited)

| Input | Source | Required? | Notes |
|---|---|---|---|
| Observability stack type | Elicitation Q2 | Yes | Determines which scraper/exporter to generate |
| Metrics endpoint / connection string | Elicitation Q3 | Yes | Where to pull live telemetry from |
| Alert notification channel | Elicitation Q4 | Yes | Slack webhook, email, PagerDuty, or webhook URL |
| Monitoring interval (seconds) | Elicitation Q5 | Yes | Default: 60s |
| Scaling bounds (min/max replicas or compute units) | Elicitation Q6 | Conditional | Required if deploy.md is absent or does not specify bounds |

---

## Elicitation Protocol

### Q&A Sequence

```yaml
questions:
  - id: Q1
    required: true
    prompt: |
      I need to read your runtime environment configuration.
      Does the file `artifacts/deploy-manifest.yaml` exist in the project root?
      (yes / no)
    type: single_select
    options: [yes, no]
    depends_on: null

  - id: Q1b
    required: true
    prompt: |
      deploy-manifest.yaml was not found. I need to collect runtime details manually.
      What is the deployment target?
    type: single_select
    options:
      - Kubernetes (on-prem)
      - Kubernetes (cloud — AWS EKS / Azure AKS / GCP GKE)
      - Docker Compose
      - Serverless (AWS Lambda / Azure Functions)
      - Bare metal / VM
      - Other (describe below)
    depends_on: "Q1 == no"

  - id: Q2
    required: true
    prompt: |
      What observability stack is in use? Select one:
    type: single_select
    options:
      - Prometheus + Grafana
      - Datadog
      - OpenTelemetry (with Jaeger / Tempo / custom backend)
      - AWS CloudWatch
      - Azure Monitor
      - Google Cloud Monitoring
      - ELK Stack (Elasticsearch + Logstash + Kibana)
      - Custom / None — generate generic polling scripts
    validation: "Must select one option"
    depends_on: null

  - id: Q3
    required: true
    prompt: |
      Provide the metrics endpoint or connection string for your observability stack.
      Examples:
        Prometheus: http://prometheus:9090
        Datadog:    https://api.datadoghq.com (API key will be prompted separately)
        CloudWatch: arn:aws:cloudwatch:us-east-1:123456789012
      Enter value:
    type: free_text
    validation: "Must be a non-empty string; URL format validated if http/https"
    depends_on: null

  - id: Q4
    required: true
    prompt: |
      Where should SLA breach alerts be sent?
    type: single_select
    options:
      - Slack (provide webhook URL)
      - Email (provide address)
      - PagerDuty (provide integration key)
      - Microsoft Teams (provide webhook URL)
      - Generic webhook (provide URL)
      - Console / log only (no external alerting)
    depends_on: null

  - id: Q4b
    required: true
    prompt: |
      Provide the alert destination value (webhook URL / email address / integration key):
    type: free_text
    validation: "Non-empty string"
    depends_on: "Q4 != 'Console / log only'"

  - id: Q5
    required: true
    prompt: |
      What monitoring polling interval should RuntimeIQ use?
      Recommended: 60 seconds for standard production, 15 seconds for high-criticality.
      Enter value in seconds (integer, 10–300):
    type: numeric
    validation: "Integer between 10 and 300"
    default: "60"
    depends_on: null

  - id: Q6
    required: true
    prompt: |
      Define auto-scaling bounds. If ControlPlane cost-config.yaml is present these will be
      cross-validated. Enter as: min_replicas,max_replicas (e.g. 2,10)
      Or enter "none" to disable auto-scaling (alerts only):
    type: free_text
    validation: "Format: integer,integer where min < max, or the word 'none'"
    default: "2,10"
    depends_on: null

  - id: Q7
    required: true
    prompt: |
      Which SLA dimensions should be monitored? Select all that apply:
    type: multi_select
    options:
      - p50 latency
      - p95 latency
      - p99 latency
      - Error rate (5xx)
      - Error rate (4xx)
      - Token consumption per request
      - Availability / uptime %
      - Agent response quality score (from DriftGuard feed)
    depends_on: null
```

### Confirmation Gate

```
RuntimeIQ Configuration Summary
─────────────────────────────────────────────
Deployment target     : [Q1b value or from deploy-manifest.yaml]
Observability stack   : [Q2]
Metrics endpoint      : [Q3]
Alert channel         : [Q4] → [Q4b]
Polling interval      : [Q5]s
Auto-scaling bounds   : min=[Q6.min] max=[Q6.max]
SLA dimensions        : [Q7 selections]
NFR targets from      : artifacts/openspec.yaml
─────────────────────────────────────────────
Type CONFIRM to generate all RuntimeIQ artifacts, or EDIT <Q-number> to change a value.
```

---

## Processing Logic

1. **Parse NFR targets** — Read `artifacts/openspec.yaml`, extract all `nfr:` blocks. Build an internal map of `{feature_id → {metric → threshold}}`. If openspec.yaml is absent, abort with message: `"openspec.yaml is required. Run SpecFlow (Planning) to generate it first."`

2. **Read deploy manifest** — Read `artifacts/deploy-manifest.yaml` to enumerate all deployed services and agent endpoints. Cross-reference with openspec.yaml feature IDs to ensure full coverage.

3. **Generate monitoring configuration** — Based on Q2 (observability stack), generate the appropriate monitoring config file:
   - Prometheus: `prometheus-rules.yaml` (alerting rules) + `scrape-config.yaml`
   - Datadog: `datadog-monitors.json` (monitor definitions via API)
   - OpenTelemetry: `otel-collector-config.yaml` + alert rules
   - CloudWatch: `cloudwatch-alarms.json`
   - Generic: `polling-script.py` + `thresholds.yaml`

4. **Generate auto-scaling policy** — Using Q6 bounds and ControlPlane's `cost-config.yaml` (if present), generate scaling policy files appropriate to the deployment target. For Kubernetes: `hpa.yaml`. For cloud: provider-specific autoscaling configs.

5. **Generate alert routing** — Based on Q4, generate the alert notification config. For Slack: webhook payload template. For PagerDuty: integration config. For email: SMTP config block.

6. **Generate SLA dashboard** — Produce a Grafana dashboard JSON (generic format) or provider-equivalent that visualises all Q7-selected SLA dimensions per feature with NFR target lines overlaid.

7. **Generate the monitoring agent script** — Produce `runtime-iq-monitor.py` — a self-contained Python script that polls the metrics endpoint, evaluates thresholds, triggers alerts, requests scaling, and writes to `feedback-loop-triggers.yaml` on each cycle.

8. **Write feedback loop contribution** — Append a structured entry to `operate/feedback-loop-triggers.yaml` with current performance status.

---

## Output Contract

| Output File | Location | Format | Description |
|---|---|---|---|
| `sla-dashboard.json` | `operate/runtime-iq/` | JSON (Grafana/generic) | Live SLA dashboard: per-feature latency and error rate vs. NFR targets |
| `prometheus-rules.yaml` OR `datadog-monitors.json` OR `cloudwatch-alarms.json` OR `otel-collector-config.yaml` | `operate/runtime-iq/` | YAML / JSON | Stack-specific monitoring rules (only one generated based on Q2) |
| `polling-script.py` | `operate/runtime-iq/` | Python | Generic telemetry poller (generated if stack = Custom/None) |
| `hpa.yaml` OR `autoscaling-policy.json` | `operate/runtime-iq/` | YAML / JSON | Auto-scaling policy for deployment target |
| `alert-config.yaml` | `operate/runtime-iq/` | YAML | Alert routing: channel, thresholds, escalation |
| `runtime-iq-monitor.py` | `operate/runtime-iq/` | Python | Master monitoring agent — polls, evaluates, alerts, scales |
| `thresholds.yaml` | `operate/runtime-iq/` | YAML | NFR threshold registry derived from openspec.yaml |
| `sla-breach-log.md` | `operate/runtime-iq/` | Markdown | Running log of SLA breaches with timestamp, feature, severity, delta |

### Feedback Loop Contribution

```yaml
runtime_iq:
  generated_at: "ISO-8601"
  summary: "SLA status across N features. X breaches in last cycle."
  triggers:
    - feature_id: string
      metric: string
      current_value: float
      threshold: float
      breach_delta: float
      severity: warning | critical
  severity: info | warning | critical
```

---

## Downstream Consumers

| Output File | Consumed By | How |
|---|---|---|
| `thresholds.yaml` | ControlPlane | Cross-validates scaling bounds against cost ceiling |
| `sla-breach-log.md` | IncidentLens | Provides SLA metrics at time of incident |
| `feedback-loop-triggers.yaml` (contribution) | Next sprint planning session | Performance evidence for Monday planning |

---

## Error Handling

| Condition | Behaviour |
|---|---|
| `openspec.yaml` missing | Abort — emit: `"openspec.yaml required. Generate via SpecFlow before running RuntimeIQ."` |
| `deploy-manifest.yaml` missing | Trigger Q1b elicitation to collect runtime details inline |
| Observability endpoint unreachable | Log error in `sla-breach-log.md`, set severity=critical, alert POD Lead |
| Cost ceiling exceeded before scaling | Alert POD Lead, log to `sla-breach-log.md`, do not scale beyond ceiling |
| `control-plane/cost-config.yaml` absent | Warn user: "ControlPlane not configured. Run ControlPlane skill first to set cost ceilings." |

---

## HITL Gates

| Gate | Condition | Reviewer | Blocks |
|---|---|---|---|
| Pre-run | Confirmation gate CONFIRM received | POD Lead | All artifact generation |
| Scaling request | Requested replicas exceed 80% of max bound | POD Lead | Scale-up execution |
| Critical SLA breach | p99 latency > 3× threshold | POD Lead | No auto-resolution; human action required |

---

## Metadata

```yaml
author:        SpecPod Framework
framework_ref: 02e_SpecPod-sprint-specs-operate.html (O-01)
manifest_ref:  061-generated-files-manifest.txt
created:       2025-01
```
