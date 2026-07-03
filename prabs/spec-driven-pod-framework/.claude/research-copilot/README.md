# ResearchCopilot

Validates each draft requirement against available discovery evidence — interviews, user feedback, analytics, support tickets, and prior sprint reports. Classifies evidence strength per requirement, surfaces contradictions between stated requirements and observed user behaviour, and flags weak-evidence requirements as AssumptionTracker candidates.

---

## When to Use

Invoke in parallel with PolicyCatalog, ContextFabric, and TransformIQ at Step 1 of Monday planning.

**Trigger phrases:** `Run ResearchCopilot`, `Synthesise discovery evidence`

---

## Inputs

| Input | Required |
|---|---|
| `artifacts/openspec.yaml` | Mandatory |
| `specs/knowledge.md` | Mandatory |
| `specs/features.md` | Mandatory |
| Interview transcripts / meeting notes | Optional |
| Analytics exports / usage telemetry | Optional |
| Prior sprint validation reports | Optional |
| Support ticket exports | Optional |

## Outputs

- `artifacts/evidence-map.md` — per-requirement evidence classification (CONFIRMED / PARTIAL / WEAK / NO-EVIDENCE / CONTRADICTED)

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| Phase 01 spec completion | AssumptionTracker (consumes evidence-map) |
| (parallel with PolicyCatalog, ContextFabric, TransformIQ) | SpecFlow |
