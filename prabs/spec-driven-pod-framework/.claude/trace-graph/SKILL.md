---
name: trace-graph
description: "TraceGraph builds and maintains a directed traceability graph that links every requirement in openspec.yaml to its implementation artifacts, test scenarios, and deployment entries. It surfaces broken links, orphaned artifacts, and untraced requirements."
---

# SKILL: TraceGraph
**SpecPod Framework v2.1.0 · Planning · 03**
**Model:** claude-haiku-4-5-20251001 · **Context Budget:** ~30K tokens
**Role:** Requirement-to-artifact traceability verification

---

## Purpose
TraceGraph builds and maintains a directed traceability graph that links every requirement in `openspec.yaml` to its implementation artifacts, test scenarios, and deployment entries. It surfaces broken links, orphaned artifacts, and untraced requirements. Its output is the authoritative chain-of-custody record for every HITL gate attestation.

---

## Trigger
Invoke after SpecFlow produces `ai-manifest.json`. Re-run after every spec change or artifact update.

**Activation phrase:** `Run TraceGraph` or `Verify traceability`

---

## Required Input Files

| File | Source | Required? |
|------|--------|-----------|
| `artifacts/openspec.yaml` | POD Lead (locked) | REQUIRED |
| `artifacts/ai-manifest.json` | SpecFlow | REQUIRED |
| `specs/spec.md` | spec-generation (prior phase) | REQUIRED |
| `specs/tasks.md` | spec-generation (prior phase) | REQUIRED |
| `tests/*.feature` | Build phase | IF AVAILABLE |
| `artifacts/deploy-manifest.yaml` | Build/Deploy phase | IF AVAILABLE |

---

## User Inputs Required

TraceGraph operates autonomously on available files. It will ask:

1. **Gate context:** "Which HITL gate is this traceability check for? (Gate-0 / Gate-1 / Gate-2 / Mid-sprint)" — determines which link categories are required.
2. **Orphan policy:** "How should orphaned artifacts be classified? (warn / block-gate / log-only)" — default: warn

---

## Processing Instructions

### Phase 1 — Requirement Inventory
1. Extract all requirement IDs from `artifacts/openspec.yaml`
2. Cross-reference against `specs/spec.md` to confirm ID consistency
3. Build a flat list: `[REQ-ID, description, type, status]`

### Phase 2 — Artifact Inventory
1. Parse `artifacts/ai-manifest.json` — extract all artifact entries with their requirement ID mappings
2. Parse `tests/*.feature` if present — extract scenario IDs and their requirement ID annotations (`@REQ-XXX`)
3. Parse `artifacts/deploy-manifest.yaml` if present — extract deployed components

### Phase 3 — Graph Construction
Build a directed graph for each requirement:
```
REQ-ID
  └─► CLU-ID (cluster in task-breakdown.yaml)
        └─► src/file.ts (artifact in ai-manifest.json)
              └─► tests/scenario.feature (test mapping)
                    └─► deploy-manifest.yaml entry (if deployed)
```

### Phase 4 — Gap Detection
Identify and classify:
- **UNTRACED REQUIREMENT:** REQ-ID exists in openspec.yaml but has no artifact mapping → `CRITICAL`
- **ORPHANED ARTIFACT:** File exists in ai-manifest.json with no REQ-ID → `WARNING`
- **UNTESTED REQUIREMENT:** REQ-ID has artifact but no test scenario → `WARNING` (escalate to CRITICAL at Gate-2)
- **BROKEN LINK:** REQ-ID references a file that does not exist in the manifest → `ERROR`
- **MISSING PROVENANCE HEADER:** File in manifest lacks the SpecPod provenance comment → `WARNING`

### Phase 5 — Gate Attestation
For the specified gate, produce an attestation record:
- Gate-0: All requirements must have cluster assignments
- Gate-1: All requirements must have artifact mappings
- Gate-2: All requirements must have test mappings and no CRITICAL gaps
- Mid-sprint: Report current coverage without blocking

---

## Output Files

### `artifacts/traceability-report.md`
```markdown
# Traceability Report — Sprint [ID] — [Gate]
Generated: [Timestamp]

## Coverage Summary
- Requirements total: N
- Fully traced (req → artifact → test): N (N%)
- Partially traced (req → artifact only): N
- Untraced requirements: N ← CRITICAL if > 0 at Gate-1

## Gap Report

### CRITICAL
| REQ-ID | Description | Missing Link | Action |
|--------|-------------|--------------|--------|

### WARNING
| File/REQ-ID | Issue | Action |
|-------------|-------|--------|

## Full Traceability Graph
[Structured list: REQ-ID → CLU-ID → files → tests]

## Gate Attestation — [Gate Name]
Status: PASS / FAIL
Blocker count: N
Ready to proceed: YES / NO — [reason if NO]
```

---

## Also Active In
- **Build (Tue–Thu):** Verifies every task has a spec ID before Conductor dispatches it
- **Validate:** Confirms every test scenario maps to a requirement before Gate 2 clears

---

## Limitations
- Only traces artifacts with correctly formatted SpecPod provenance headers and `@REQ-XXX` test annotations
- Manually written code without provenance appears as orphaned until annotated
- Graph accuracy is bounded by the completeness of `ai-manifest.json` — SpecFlow must be run first
