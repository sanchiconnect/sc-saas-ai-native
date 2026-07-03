# TraceGraph

Builds and maintains a directed traceability graph linking every requirement in `openspec.yaml` to its implementation artifacts, test scenarios, and deployment entries. Surfaces broken links, orphaned artifacts, and untraced requirements. The authoritative chain-of-custody record for every HITL gate attestation.

---

## When to Use

Invoke after SpecFlow produces `ai-manifest.json`. Re-run after every spec change or artifact update.

**Trigger phrases:** `Run TraceGraph`, `Verify traceability`

---

## Inputs

| Input | Required |
|---|---|
| `artifacts/openspec.yaml` | Mandatory |
| `artifacts/ai-manifest.json` | Mandatory |
| `specs/spec.md` | Mandatory |
| `specs/tasks.md` | Mandatory |
| `tests/*.feature` | Optional |
| `artifacts/deploy-manifest.yaml` | Optional |

## Outputs

- `artifacts/traceability-report.md` — requirement → cluster → artifact → test → deployment chain with broken link and orphan flags

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| SpecFlow | Conductor (traceability required for dispatch) |
| | HITL gate attestations |
| | PortfolioPrioritizer, SpecImpactAnalyzer |
