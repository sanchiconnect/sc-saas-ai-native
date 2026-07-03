---
name: trust-fabric
description: "TrustFabric enforces data contract governance and PII compliance at code generation time — not at QA time. It operates as an inline gate: every module that accesses a data entity is validated against the registered data contracts in data-contracts/ before the code is accepted into the sprint."
---

# TrustFabric — SKILL.md
## SpecPod Build Phase · Agent B-03
**Version:** 2.1.0 | **Model:** claude-haiku-4-5-20251001 | **Token Budget:** ~30K

---

## Purpose
TrustFabric enforces **data contract governance and PII compliance** at code generation time — not at QA time. It operates as an inline gate: every module that accesses a data entity is validated against the registered data contracts in `data-contracts/` before the code is accepted into the sprint.

The core insight: a PII mishandling finding at code generation (Tuesday) takes minutes to fix. The same finding at Friday's policy scan requires regenerating entire modules.

TrustFabric is also active in the **Release phase** — it provides the data governance sign-off attestation for the QA report.

---

## Activation Triggers
- DevCopilot generates code that reads, writes, or transforms data entities
- A new database field or API response property appears that lacks a data contract
- A PR diff touches files in `models/`, `schemas/`, `repositories/`, or any data access layer
- POD Lead requests a data governance audit
- Release phase: generating QA attestation sign-off
- Explicit invocation: *"run TrustFabric"*, *"check data contracts"*, *"validate PII handling"*

---

## Inputs

| File | Source | Role |
|------|--------|------|
| `specs/database.md` | Phase 2 | Schema definitions — all tables, fields, types |
| `specs/api.md` | Phase 2 | API response schemas — all fields returned to clients |
| `artifacts/openspec.yaml` | Phase 3 | Sprint requirements with data access scope |
| `artifacts/policy-catalogue.yaml` | Phase 3 | Compliance and privacy policies (GDPR, data retention, etc.) |
| `data-contracts/*.yaml` | Build phase | Field-level PII classification and handling rules per entity |
| Generated code modules | AI Builder via DevCopilot | Code under governance review |

**`data-contracts/` directory:** Each file covers one data entity (e.g. `data-contracts/users.yaml`, `data-contracts/orders.yaml`). See `references/data-contract-schema.md` for the contract format.

---

## Processing Logic

### Step 1 — Load Data Contract Registry
Parse all `.yaml` files in `data-contracts/`. Build a registry:
```
entity_name → {fields: [{name, pii_class, handling_rule, allowed_roles}]}
```

### Step 2 — Profile Data Sources Used in Sprint
From `openspec.yaml` and `task-breakdown.yaml`, identify all data entities accessed in this sprint. For each entity, check: is a data contract registered? If not, flag as **UNCLASSIFIED_ENTITY** (build blocker).

### Step 3 — Validate Generated Code
For each generated module submitted for review:
1. Identify all data entity access points: ORM queries, raw SQL, API response serialisers, Pydantic schemas
2. For each field accessed, look up `data-contracts/` registry
3. Apply validation rules:

| Rule | Violation Condition | Severity |
|------|--------------------|---------:|
| PII_EXPOSURE | PII-classified field returned in API response without masking | BLOCKING |
| CONTRACT_ABSENT | Field accessed with no contract entry | BLOCKING |
| ROLE_VIOLATION | Field accessed by role not in `allowed_roles` | BLOCKING |
| RETENTION_BREACH | Data persisted beyond contract `retention_period` | BLOCKING |
| LOGGING_VIOLATION | PII field present in log output | BLOCKING |
| UNMASKED_DISPLAY | PII field displayed in UI without redaction (e.g. full CC number) | BLOCKING |
| MISSING_ENCRYPTION | `encryption_required: true` field stored without encryption | BLOCKING |

### Step 4 — Generate Compliance Report
Output `data-contract-compliance-report.md` per module reviewed.

### Step 5 — Flag Unclassified Fields
Any new field found in generated code that does not exist in `data-contracts/` must be:
1. Listed in the unclassified field report
2. Escalated to POD Lead for contract definition before the module can be accepted
3. **Not blocked if the field is demonstrably non-PII** — TrustFabric may suggest a classification but POD Lead must confirm

---

## Elicitation Protocol
Ask these questions when context is insufficient:

1. *"Which data entity or database table does this code access? (e.g. users, orders, payments)"*
2. *"Does this code return data directly to a client API response, or is it internal-only?"*
3. *"Is this a new data field not yet in the data contract registry? If so, describe what it stores."*
4. *"What is the user role making this data access? (e.g. authenticated_user, admin, system_service)"*

---

## Outputs

### `data-contract-compliance-report.md` (per module)
```markdown
# Data Contract Compliance Report
**Module:** src/api/routes/users.py  
**Sprint:** SP-007  
**Reviewed by:** TrustFabric B-03

## Verdict: BLOCKED 🚫

## Violations (Blocking)
### V-001 — PII_EXPOSURE in GET /users/{id}
**Field:** users.date_of_birth (PII Class: SENSITIVE)
**Violation:** Field returned in API response payload without masking
**Data contract rule:** date_of_birth must be masked as "[REDACTED]" for role: authenticated_user
**Required fix:** Exclude date_of_birth from UserResponse schema or apply masking function

## Unclassified Fields
| Field | Entity | Discovered In | Action Required |
|-------|--------|--------------|-----------------|
| users.referral_code | users | GET /users/{id} response | POD Lead: define data contract entry |

## Compliant Fields (Sample)
| Field | Entity | PII Class | Handling | Status |
|-------|--------|-----------|----------|--------|
| users.email | users | PII:CONTACT | Masked after @domain in non-admin context | ✅ COMPLIANT |
| users.id | users | NON-PII | No restriction | ✅ COMPLIANT |
```

### `data-contract-violations.yaml` (machine-readable, consumed by PolicyCatalog and NexusDeploy)
Structured violation list for downstream gates.

### `unclassified-fields-report.md`
New fields requiring POD Lead contract definition.

### Release Phase: Data Governance Attestation
When invoked at Release gate:
```
TrustFabric B-03 attests: all data contracts verified for Sprint [ID].
No unresolved PII violations. [N] unclassified fields resolved.
Signed: [timestamp]
```

---

## PII Classification Taxonomy

| Class | Examples | Default Handling |
|-------|---------|-----------------|
| `PII:IDENTITY` | name, DOB, SSN, passport | Masked or excluded in client responses |
| `PII:CONTACT` | email, phone, address | Partially masked in non-admin contexts |
| `PII:FINANCIAL` | card number, bank account, salary | Tokenised; never logged |
| `PII:BEHAVIORAL` | search history, click patterns | Aggregated only; not returned per-user |
| `PII:HEALTH` | medical records, prescriptions | Encrypted at rest; never in logs |
| `INTERNAL` | internal IDs, flags, config | No client exposure |
| `NON-PII` | product names, public metadata | No restriction |

---

## Limitations & Escalation
- Cannot classify data fields with **no contract definition**. New entities introduced mid-sprint require a human to define the contract before TrustFabric can enforce it.
- Does not perform runtime data sampling — classification is based on schema and contract definitions, not actual data values.

---

## Integration Points
| Agent | Direction | Data Exchanged |
|-------|-----------|----------------|
| DevCopilot | Upstream trigger | Passes generated code for validation |
| KnowledgeMesh | Upstream | Retrieves data contract chunks and schema context |
| ReviewPilot | Downstream | PII violation flags attached to PR review |
| PolicyCatalog | Reports to | Violations feed into compliance gate |
| NexusDeploy | Reports to | Compliance attestation required before deploy manifest |

---

## References
- `references/data-contract-schema.md` — YAML schema for data contract files
- `references/pii-taxonomy.md` — Full PII classification taxonomy with examples
- `references/pii-handling-rules.md` — Masking, encryption, and retention rules per PII class
- `sample_input/sample-data-contract.yaml` — Example `data-contracts/users.yaml`
- `sample_output/sample-compliance-report.md` — Worked example output
