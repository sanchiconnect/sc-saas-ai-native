# Conductor

The central sprint orchestrator. Reads all Monday planning artifacts, maps every task to the correct AI Builder and accelerator skill, sequences dispatch respecting inter-agent dependencies, and holds dispatch until HITL gates are cleared. Never bypasses a gate — it queues and waits.

---

## When to Use

Invoke after all Step 1–6 planning artifacts are produced and Gate 1 (Plan Sign-off) is cleared by the POD Lead.

---

## Inputs

| Input | Required |
|---|---|
| `artifacts/openspec.yaml` | Mandatory |
| `artifacts/task-breakdown.yaml` | Mandatory |
| `artifacts/ai-manifest.json` | Mandatory |
| `artifacts/policy-catalogue.yaml` | Mandatory |
| `artifacts/traceability-report.md` | Mandatory |
| `artifacts/sprint-scope-ranked.md` | Mandatory |
| `artifacts/assumption-log.md` | Mandatory |
| `artifacts/decision-ledger.md` | Mandatory |
| `specs/tasks.md` | Mandatory |
| `specs/program.md` | Mandatory |
| `artifacts/context.yaml` | Optional |
| `artifacts/impact-analysis.md` | If spec changed |

## Outputs

- `artifacts/sprint-board.md` — live sprint board with task assignments and status
- `artifacts/dispatch-log.md` — full dispatch record with gate attestations

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| All Step 1–6 planning skills | DevCopilot, ExperienceStudio, ReviewPilot (dispatches them) |
| Gate 1 clearance | |
