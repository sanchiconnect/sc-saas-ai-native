# KnowledgeMesh

The centralised RAG context backbone for all build-phase agents. Every build agent retrieves context through KnowledgeMesh rather than independently reading spec files — creating a single, versioned, deduplicated knowledge plane across the entire sprint. Prevents context divergence between AI Builders.

---

## When to Use

Invoked by any build agent requesting context retrieval. Also triggered when a source document changes mid-sprint or when a context coverage audit is requested.

**Trigger phrases:** `run KnowledgeMesh`, `build context index`, `retrieve context for [task]`

---

## Inputs

| Input | Required |
|---|---|
| `specs/knowledge.md` | Mandatory |
| `specs/design.md` | Mandatory |
| `specs/api.md` | Mandatory |
| `specs/database.md` | Mandatory |
| `specs/features.md` | Mandatory |
| `specs/impl.md` | Mandatory |
| `artifacts/openspec.yaml` | Mandatory |
| `artifacts/task-breakdown.yaml` | Mandatory |
| `artifacts/ai-manifest.json` | Optional |
| `artifacts/decision-ledger.md` | Optional |

## Outputs

- `artifacts/knowledge-mesh-index.md` — sprint context index log
- Retrieval responses to downstream agents

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| All Phase 01 specs and Phase 03 planning artifacts available | DevCopilot (context retrieval) |
| | ExperienceStudio, ReviewPilot, TrustFabric |
