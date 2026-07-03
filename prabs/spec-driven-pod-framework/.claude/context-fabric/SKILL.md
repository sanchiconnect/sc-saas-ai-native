---
name: context-fabric
description: "ContextFabric refreshes the enterprise context snapshot each sprint, mapping new requirements to existing system capabilities (gap vs. existing)."
---

# SKILL: ContextFabric
**SpecPod Framework v2.1.0 · Planning · 13 — Proposed**
**Model:** claude-sonnet-4-20250514 · **Context Budget:** ~80K tokens
**Role:** Enterprise context grounding and capability gap detection

> ⬡ **Proposed** — Context refresh cadence and scope boundary rules need further definition. Primary home is Phase 2 (Specify). Tribal knowledge and undocumented systems remain blind spots requiring human annotation.

---

## Purpose
ContextFabric refreshes the enterprise context snapshot each sprint, mapping new requirements to existing system capabilities (gap vs. existing). It publishes a versioned `context.yaml` that SpecFlow uses as the authoritative system capability reference, preventing AI Builders from re-implementing capabilities that already exist — a common 0.5–1 day waste per sprint. It also flags requirements that assume capabilities not yet in the system.

---

## Trigger
Invoke in parallel with PolicyCatalog, ResearchCopilot, and TransformIQ at Step 1 of Monday planning.

**Activation phrase:** `Run ContextFabric` or `Refresh enterprise context`

---

## Required Input Files

| File | Source | Required? |
|------|--------|-----------|
| `artifacts/openspec.yaml` | POD Lead (locked) | REQUIRED |
| `specs/knowledge.md` | spec-knowledge (prior phase) | REQUIRED |
| `specs/design.md` | spec-design (prior phase) | REQUIRED |
| `specs/database.md` | spec-database (prior phase) | REQUIRED |
| `specs/api.md` | spec-api (prior phase) | REQUIRED |
| `artifacts/ai-manifest.json` | Prior sprint SpecFlow | IF AVAILABLE |
| Enterprise API docs / schema files | User (upload) | IF AVAILABLE |
| Change signals (incident logs, drift reports) | User (upload) | IF AVAILABLE |

---

## User Inputs Required

1. **Scope boundary:** "What is the boundary of the enterprise context for this sprint? (this project only / this project + dependent systems / full enterprise — default: this project + dependent systems)"
2. **Last refresh:** "When was the enterprise context last updated? (date or 'first sprint')"
3. **Known changes since last sprint:** "Have any of the following changed since the last sprint? Select all: [a] API contracts [b] database schema [c] authentication/auth model [d] infrastructure [e] dependent service versions [f] none"
4. **Tribal knowledge:** "Are there any undocumented capabilities or system behaviours the team knows about that aren't in any spec file? (describe or NONE — these will be annotated as MANUAL entries in context.yaml)"
5. **Capability gap handling:** "When a requirement assumes a capability gap, should I: [a] flag as a blocker requiring a new build task [b] flag as a warning for POD Lead awareness [c] log only"

---

## Processing Instructions

### Phase 1 — Capability Inventory
1. Parse `specs/design.md`, `specs/database.md`, `specs/api.md`, and `specs/knowledge.md`
2. Build a structured capability inventory:
   - **API endpoints:** paths, methods, parameters, auth requirements
   - **Database entities:** tables/collections, key fields, relationships
   - **UI components:** reusable components described in design/ui-ux specs
   - **Business logic modules:** documented rules and algorithms
   - **Integration points:** external system connections
3. If `artifacts/ai-manifest.json` is available, include all previously generated artifacts as confirmed capabilities
4. Append any MANUAL tribal knowledge entries provided by the POD Lead

### Phase 2 — Change Detection
If prior `context.yaml` exists:
1. Diff the new capability inventory against the prior snapshot
2. Flag: ADDED, REMOVED, MODIFIED capabilities
3. If change signals (incident logs, drift reports) are provided, annotate affected capabilities

### Phase 3 — Requirement-to-Capability Mapping
For each requirement in `artifacts/openspec.yaml`:
1. Identify which capabilities it depends on
2. Classify each dependency:
   - **EXISTS:** Capability is confirmed in the inventory → reuse, do not regenerate
   - **EXISTS_MODIFIED:** Capability exists but has changed — may require update task
   - **GAP:** Requirement depends on a capability not in the inventory → new build task required
   - **ASSUMED:** Requirement implies a capability without explicitly referencing it → flag for POD Lead

### Phase 4 — Gap Report
For each GAP:
1. Describe what capability needs to be built
2. Estimate complexity: LOW (≤2h) / MEDIUM (2–8h) / HIGH (>8h)
3. Recommend adding a new cluster to `task-breakdown.yaml` via SpecFlow

### Phase 5 — Context Snapshot
Produce a versioned `context.yaml` with all confirmed capabilities, tagged with source and confidence level.

---

## Output Files

### `artifacts/context.yaml`
```yaml
version: SPRINT-XXX-v1
generated: YYYY-MM-DDTHH:MM:SSZ
scope: "this project + dependent systems"

capabilities:
  api_endpoints:
    - path: /api/v1/users
      method: GET
      auth: bearer
      source: specs/api.md
      confidence: confirmed
      last_verified: YYYY-MM-DD

  database_entities:
    - name: users
      type: postgres_table
      key_fields: [id, email, created_at]
      source: specs/database.md
      confidence: confirmed

  ui_components:
    - name: DataTable
      reusable: true
      source: specs/design.md
      confidence: confirmed

  integrations:
    - name: Stripe Payment Gateway
      type: REST
      source: specs/api.md
      confidence: confirmed

manual_annotations:
  - description: "Auth token refresh handled by middleware, not documented in api.md"
    annotated_by: "[POD Lead]"
    confidence: tribal_knowledge

changes_since_last_sprint:
  - capability: /api/v1/users
    change_type: MODIFIED
    note: "Added ?include_deleted query param — prior sprint artifact may need update"

requirement_mapping:
  - req_id: REQ-001
    dependencies:
      - capability: /api/v1/users
        status: EXISTS
      - capability: JWT session middleware
        status: EXISTS
  - req_id: REQ-008
    dependencies:
      - capability: bulk_export_service
        status: GAP
        complexity: HIGH
        recommended_action: "Add CLU-NEW-001 to task-breakdown.yaml"
```

### Capability Gap Report (section of context.yaml rendered for POD Lead)
```markdown
## Capability Gaps — Sprint [ID]

### GAPS (New Build Required)
| REQ-ID | Assumed Capability | Complexity | Recommended Action |
|--------|-------------------|------------|-------------------|
| REQ-008 | bulk_export_service | HIGH | New cluster required — add to SpecFlow |

### EXISTS_MODIFIED (May Require Update)
| REQ-ID | Capability | Change | Action |
|--------|-----------|--------|--------|

### Coverage Confidence Flags
| REQ-ID | Coverage | Note |
|--------|----------|------|
```

---

## Also Active In
Build (Tue–Thu) — provides live context retrieval to Conductor and SpecFlow during code generation, ensuring builders reference the current system state.

---

## Limitations
- Context coverage is bounded by what is machine-readable and accessible in the spec files
- Tribal knowledge and undocumented systems are blind spots — require manual POD Lead annotation
- ContextFabric maps capabilities; it does not validate them against live running systems
