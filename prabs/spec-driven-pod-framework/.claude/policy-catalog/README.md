# PolicyCatalog

Maps every requirement in `openspec.yaml` to its applicable compliance policies before build starts. Generates per-task compliance guard prompts injected into SpecFlow cluster definitions and Conductor task dispatches — ensuring compliance is baked in at generation time, not audited after the fact.

---

## When to Use

Invoke in parallel with ContextFabric and ResearchCopilot at Step 1 of Monday planning.

**Trigger phrases:** `Run PolicyCatalog`, `Generate compliance rails`

---

## Inputs

| Input | Required |
|---|---|
| `artifacts/openspec.yaml` | Mandatory |
| `specs/database.md` | Mandatory |
| `specs/api.md` | Mandatory |
| `specs/features.md` | Mandatory |
| `references/policy-library.md` | Mandatory |

## Outputs

- `artifacts/policy-catalogue.yaml` — per-task compliance guard prompts consumed by SpecFlow and Conductor

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| Phase 01 spec completion | SpecFlow (injects compliance rails) |
| `references/policy-library.md` available | Conductor (compliance-gated dispatch) |
| (parallel with ContextFabric, ResearchCopilot, TransformIQ) | PolicyEnforcer (validates enforcement) |
