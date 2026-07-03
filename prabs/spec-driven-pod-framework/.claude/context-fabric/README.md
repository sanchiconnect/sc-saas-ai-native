# ContextFabric

Refreshes the enterprise context snapshot each sprint, mapping new requirements to existing system capabilities (gap vs. existing). Publishes a versioned `context.yaml` that SpecFlow uses as the authoritative system capability reference — preventing AI Builders from re-implementing capabilities that already exist.

> ⬡ **Proposed** — context refresh cadence and scope boundary rules need further definition.

---

## When to Use

Invoke in parallel with PolicyCatalog, ResearchCopilot, and TransformIQ at Step 1 of Monday planning.

---

## Inputs

| Input | Required |
|---|---|
| `artifacts/openspec.yaml` | Mandatory |
| `specs/knowledge.md` | Mandatory |
| `specs/design.md` | Mandatory |
| `specs/database.md` | Mandatory |
| `specs/api.md` | Mandatory |
| `artifacts/ai-manifest.json` | Optional |
| Enterprise API docs / schema files | Optional |

## Outputs

- `artifacts/context.yaml` — versioned enterprise capability map consumed by SpecFlow

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| Phase 01 spec completion | SpecFlow |
| (parallel with PolicyCatalog, ResearchCopilot, TransformIQ) | |
