# ExperimentOps

Enables a small team to run statistically rigorous A/B and multi-armed experiments in production without dedicated data science infrastructure. Generates complete experiment configurations — traffic routing rules, variant definitions, guardrail monitors, statistical significance calculators, and auto-stop logic. Automatically stops experiments and routes traffic back to control if a guardrail metric degrades.

> ⬡ **Proposed** — statistical significance requirements and guardrail thresholds must be defined before production experiments run. POD Lead sign-off mandatory.

---

## When to Use

Run during the Operate phase when the team wants to A/B test a feature or model variant in production.

**Trigger phrases:** `run ExperimentOps`, `set up A/B test`, `create experiment`, `configure production experiment`

---

## Inputs

| Input | Required |
|---|---|
| `artifacts/openspec.yaml` | Mandatory |
| `artifacts/deploy-manifest.yaml` | Mandatory |
| `operate/runtime-iq/thresholds.yaml` | Mandatory |
| `operate/value-tracker/value-tracker-config.yaml` | Mandatory |
| Experiment hypothesis (elicited) | Mandatory |
| Variants definition (elicited) | Mandatory |
| Traffic allocation (elicited) | Mandatory |

## Outputs

- `operate/experiment-ops/experiment-config.yaml` — full experiment configuration
- `operate/experiment-ops/guardrail-monitor.yaml` — auto-stop rules per guardrail metric

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| RuntimeIQ and ValueTracker configured | — |
| Deployment established | |
