# ScenarioPlanner

Runs a 3-scenario (best / expected / worst) analysis per major scope choice, identifies which assumptions most heavily influence ROI outcomes, calculates minimum viable scope, and flags items with high variance between best and worst case. Gives the POD Lead a 5-minute stress-test of scope choices.

> ⬡ **Proposed** — scenario parameters and sensitivity ranges require definition from the business before meaningful outputs can be generated.

---

## When to Use

Invoke after PortfolioPrioritizer produces `sprint-scope-ranked.md` (Step 5 of Monday planning).

**Trigger phrases:** `Run ScenarioPlanner`, `Stress-test sprint scope`

---

## Inputs

| Input | Required |
|---|---|
| `artifacts/roi-brief.md` | Mandatory |
| `artifacts/sprint-scope-ranked.md` | Mandatory |
| `artifacts/assumption-log.md` | Mandatory |
| `artifacts/task-breakdown.yaml` | Mandatory |
| `specs/program.md` | Mandatory |

## Outputs

- `artifacts/scenario-matrix.md` — 3-scenario analysis per scope item with sensitivity rankings and minimum viable scope

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| PortfolioPrioritizer | Conductor |
| | ReleaseIntel (consumes scenario-matrix) |
