# DevCopilot

The primary implementation assistant for AI Builders during build days. Generates spec-anchored code for a React/Python FastAPI/PostgreSQL stack with provenance headers, spec traceability IDs, and coding convention compliance injected automatically. Delivers code only after a conformance loop confirms Spec Conformance Score ≥ 90%.

---

## When to Use

Invoke when an AI Builder is implementing a task from `task-breakdown.yaml`, needs implementation guidance for a specific requirement, or needs a spec conformance re-validation.

**Trigger phrases:** `implement TASK-042`, `generate code for REQ-API-003`, `DevCopilot: [task description]`

---

## Inputs

| Input | Required |
|---|---|
| `artifacts/task-breakdown.yaml` | Mandatory |
| `artifacts/openspec.yaml` | Mandatory |
| `artifacts/ai-manifest.json` | Mandatory |
| `specs/design.md` | Mandatory |
| `specs/api.md` | Mandatory |
| `specs/database.md` | Mandatory |
| `artifacts/policy-catalogue.yaml` | Mandatory |
| `.cursorrules` | Mandatory |
| `AGENTS.md` | Mandatory |
| KnowledgeMesh retrieval | Mandatory |
| TrustFabric flags | Mandatory |

## Outputs

- Generated source code files with provenance headers (`@spec:`, `@task:`, `@generated:`)
- Updated `artifacts/ai-manifest.json` entries

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| Conductor dispatch | ReviewPilot |
| KnowledgeMesh (context retrieval) | TrustFabric (data contract validation) |
| TrustFabric (constraint check) | NexusDeploy |
