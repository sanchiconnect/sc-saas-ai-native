# SpecFlow

Converts a locked `openspec.yaml` into a parallel-ready build plan. Decomposes every functional and non-functional requirement into bounded generation clusters — each cluster is a self-contained unit of code that one AI Builder can generate independently. The primary input to Conductor for task dispatch.

---

## When to Use

Invoke after `context.yaml` (ContextFabric) and `policy-catalogue.yaml` (PolicyCatalog) are available.

**Trigger phrases:** `Run SpecFlow`, `Decompose sprint spec`

---

## Inputs

| Input | Required |
|---|---|
| `artifacts/openspec.yaml` | Mandatory |
| `artifacts/context.yaml` | Mandatory |
| `artifacts/policy-catalogue.yaml` | Mandatory |
| `specs/spec.md` | Mandatory |
| `specs/tasks.md` | Mandatory |
| `specs/design.md` | Mandatory |
| `specs/api.md` | Mandatory |
| `specs/database.md` | Mandatory |
| `specs/ui-ux.md` | Mandatory |
| `artifacts/ai-manifest.json` | If iterating |

## Outputs

- `artifacts/task-breakdown.yaml` — bounded generation clusters with requirement IDs and acceptance criteria
- `artifacts/ai-manifest.json` — component registry with builder assignments

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| ContextFabric, PolicyCatalog | TraceGraph |
| | Conductor |
| | ValueModeler |
