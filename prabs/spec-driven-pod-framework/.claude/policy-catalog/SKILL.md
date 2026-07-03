---
name: policy-catalog
description: "PolicyCatalog maps every requirement in openspec.yaml to its applicable compliance policies before build starts. It generates per-task compliance guard prompts that are injected into SpecFlow cluster definitions and Conductor task dispatches — ensuring compliance is baked in at generation time, not audited after the fact."
---

# SKILL: PolicyCatalog
**SpecPod Framework v2.1.0 · Planning · 05**
**Model:** claude-haiku-4-5-20251001 · **Context Budget:** ~25K tokens
**Role:** Compliance rail injection per sprint task

---

## Purpose
PolicyCatalog maps every requirement in `openspec.yaml` to its applicable compliance policies before build starts. It generates per-task compliance guard prompts that are injected into SpecFlow cluster definitions and Conductor task dispatches — ensuring compliance is baked in at generation time, not audited after the fact. Requirements with no policy assignment are flagged as gate blockers.

---

## Trigger
Invoke in parallel with ContextFabric and ResearchCopilot at Step 1 of Monday planning.

**Activation phrase:** `Run PolicyCatalog` or `Generate compliance rails`

---

## Required Input Files

| File | Source | Required? |
|------|--------|-----------|
| `artifacts/openspec.yaml` | POD Lead (locked) | REQUIRED |
| `specs/database.md` | spec-database (prior phase) | REQUIRED |
| `specs/api.md` | spec-api (prior phase) | REQUIRED |
| `specs/features.md` | spec-generation (prior phase) | REQUIRED |
| `references/policy-library.md` | PolicyCatalog references | REQUIRED |

---

## User Inputs Required

PolicyCatalog will ask the following if not defined in `openspec.yaml`:

1. **Jurisdiction:** "What regulatory jurisdiction(s) apply to this sprint? (e.g., EU/GDPR, US/HIPAA, UK/ICO, SOC2, internal-only)"
2. **Data residency:** "Are there data residency constraints? (yes → specify region / no)"
3. **PII present:** "Does this sprint process, store, or transmit personally identifiable information? (yes / no)"
4. **Classification level:** "What is the data classification level for this sprint? (public / internal / confidential / restricted)"
5. **Novel policy:** "Are there any new regulatory requirements not in the policy library that must be enforced this sprint? (describe or type NONE)"

---

## Processing Instructions

### Phase 1 — Requirement Scan
1. Parse all requirements from `artifacts/openspec.yaml`
2. For each requirement, identify compliance-relevant signals:
   - PII field references (name, email, phone, address, payment, health data)
   - Authentication and authorisation flows
   - Data persistence operations
   - External data transmission
   - Audit logging requirements
   - User consent flows
   - Data deletion or retention operations

### Phase 2 — Policy Matching
For each requirement with compliance signals:
1. Match against the policy library in `references/policy-library.md`
2. Assign one or more policy IDs: `POL-[FRAMEWORK]-[NNN]`
3. Extract the specific compliance guard prompt for each matched policy
4. Flag requirements with unmatched signals as `POLICY_GAP` — these block the gate

### Phase 3 — Rail Prompt Generation
For each matched policy:
1. Produce a concise compliance guard prompt (3–5 sentences max) suitable for injection into an AI Builder context window
2. Format: `[POL-ID] Guard: [what the builder must enforce] | Check: [what the reviewer must verify]`

### Phase 4 — Gap Analysis
Requirements with PII/auth/persistence signals but no matching policy → `POLICY_GAP`
Requirements with no compliance signals → `EXEMPT` (log but do not flag)
Requirements fully mapped → `COMPLIANT`

---

## Output Files

### `artifacts/policy-catalogue.yaml`
```yaml
sprint_id: SPRINT-XXX
generated: YYYY-MM-DD
jurisdiction: [EU/GDPR, SOC2]
data_classification: confidential
pii_present: true

mappings:
  - req_id: REQ-001
    description: "User login with email and password"
    compliance_status: COMPLIANT
    policies:
      - id: POL-GDPR-001
        framework: GDPR
        article: "Art. 32 - Security of processing"
        guard_prompt: "Ensure passwords are hashed with bcrypt (min rounds: 12). Never log credentials. Enforce HTTPS-only transport."
        reviewer_check: "Verify no plaintext credential in logs or error responses."
      - id: POL-AUTH-001
        framework: SOC2
        control: "CC6.1"
        guard_prompt: "Implement session token expiry ≤ 24h. Enforce MFA for admin roles."
        reviewer_check: "Confirm session expiry and MFA enforcement in implementation."

  - req_id: REQ-005
    description: "Export user data to CSV"
    compliance_status: POLICY_GAP
    gap_reason: "PII export detected — no data export policy defined in policy library. Manual policy assignment required."
    policies: []

gaps:
  - req_id: REQ-005
    signal: "PII export"
    action_required: "POD Lead must assign or define policy before Gate-1"
```

### Per-task compliance rail prompts (injected into task-breakdown.yaml)
PolicyCatalog appends `policy_rails` arrays to each cluster entry in `task-breakdown.yaml` during SpecFlow's Phase 2.

---

## Also Active In
Build — injects compliance rails into Conductor task dispatch context per AI Builder assignment.

---

## Limitations
- Catalogue coverage is bounded by the policy library maintained in `references/policy-library.md`
- Novel regulatory requirements must be manually added to the policy library before they are enforced
- PolicyCatalog classifies signals but does not perform legal interpretation — final compliance responsibility remains with the POD Lead

---

## References
- `references/policy-library.md` — master policy catalogue with guard prompts per framework
