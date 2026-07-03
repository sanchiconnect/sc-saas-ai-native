# TrustFabric

Enforces data contract governance and PII compliance at code generation time — not at QA time. Operates as an inline gate: every module that accesses a data entity is validated against registered data contracts before the code is accepted. Also provides the data governance sign-off attestation for the QA report in the Release phase.

---

## When to Use

Automatically triggered when DevCopilot generates code that accesses data entities, a new database field appears without a data contract, or a PR diff touches the data access layer.

**Trigger phrases:** `run TrustFabric`, `check data contracts`, `validate PII handling`

---

## Inputs

| Input | Required |
|---|---|
| `specs/database.md` | Mandatory |
| `specs/api.md` | Mandatory |
| `artifacts/openspec.yaml` | Mandatory |
| `artifacts/policy-catalogue.yaml` | Mandatory |
| `data-contracts/*.yaml` | Mandatory |
| Generated code modules | Mandatory |

## Outputs

- `artifacts/trustfabric-classification.yaml` — per-entity PII classification
- `data-contract-violations.yaml` — unresolved violations for NexusDeploy gate
- Data governance sign-off attestation (Release phase)

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| DevCopilot generates data-accessing code | ReviewPilot (provides violations) |
| data-contracts/ populated | NexusDeploy (gate check) |
| | PolicyEnforcer (provides classification) |
