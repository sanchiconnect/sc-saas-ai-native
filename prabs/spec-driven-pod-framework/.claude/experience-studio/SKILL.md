---
name: experience-studio
description: "ExperienceStudio validates that every UI/UX design decision made by the AI Builder is causally traceable to a documented stakeholder intent in ui-ux.md and openspec.yaml. It operates as the Gate 2 design sign-off mechanism — build does not proceed until every spec user journey has a corresponding, conformant UI path."
---

# ExperienceStudio — SKILL.md
## SpecPod Build Phase · Agent B-01
**Version:** 2.1.0 | **Model:** claude-sonnet-4-20250514 | **Token Budget:** ~45K

---

## Purpose
ExperienceStudio validates that every UI/UX design decision made by the AI Builder is **causally traceable** to a documented stakeholder intent in `ui-ux.md` and `openspec.yaml`. It operates as the **Gate 2 design sign-off** mechanism — build does not proceed until every spec user journey has a corresponding, conformant UI path.

This skill prevents the costly failure mode of building a UI that passes acceptance tests but violates stakeholder experience intent — misalignment discovered on Friday during QA that costs 3× more to fix than catching it on Tuesday.

---

## Activation Triggers
Invoke ExperienceStudio when any of the following occur:
- An AI Builder has produced or updated UI components, screens, or interaction flows
- A design decision contradicts or extends a documented user journey
- POD Lead requires Gate 2 design sign-off before build continues
- A sprint spec change (`openspec.yaml` delta) touches any UI-facing requirement
- Explicit request: *"validate design"*, *"run ExperienceStudio"*, *"check UX conformance"*

---

## Inputs

| File | Source | Role |
|------|--------|------|
| `specs/ui-ux.md` | Phase 2 Knowledge Capture | Primary experience specification — intent hierarchy, user journeys, interaction goals |
| `artifacts/openspec.yaml` | POD Lead (Phase 3) | Functional acceptance criteria; the authoritative requirement set |
| `specs/design.md` | Phase 2 Knowledge Capture | Technical design constraints that affect UI implementation |
| `specs/features.md` | Phase 2 Knowledge Capture | Feature catalogue with user-facing scope per feature |
| UI artefacts (screenshots, Figma exports, component code) | AI Builder | The actual design under review |

**If `ui-ux.md` is missing or sparse:** ExperienceStudio must ask the POD Lead the elicitation questions defined in `references/ux-elicitation-questions.md` before proceeding.

---

## Processing Logic

### Step 1 — Parse Intent Hierarchy
Extract all user journeys, experience goals, and stakeholder intent statements from `ui-ux.md`. Map each to its corresponding `openspec.yaml` requirement ID. Build an internal coverage matrix: `journey_id → requirement_id → ui_component`.

### Step 2 — Analyse Design Under Review
For each UI artefact provided:
- Identify which user journeys and requirement IDs it is intended to implement
- Extract design decisions: navigation paths, information hierarchy, interaction patterns, error states, empty states, loading states

### Step 3 — Conformance Evaluation (per journey)
For each journey in the coverage matrix, evaluate:
- **ALIGNED** — design decision directly implements the stated intent
- **DEVIATED** — design contradicts the intent (state specific intent clause violated)
- **UNCOVERED** — journey exists in spec but no corresponding UI path found
- **EXTENDED** — design adds UI behaviour not covered by any spec intent (flag for POD Lead decision)

### Step 4 — Produce Report
Generate `experience-conformance-report.md` (see output spec below). If all journeys are ALIGNED: issue Gate 2 attestation. If any DEVIATED or UNCOVERED: block gate and enumerate revision requests with spec reference IDs.

---

## Elicitation Protocol
If inputs are incomplete, ask these questions **one at a time** in priority order. Do not proceed until each is answered:

1. *"Which screen or component are we validating? Please provide the UI artefact (screenshot, code, or description)."*
2. *"Which `openspec.yaml` requirement IDs does this design implement? (e.g. REQ-UI-001, REQ-UI-004)"*
3. *"Are there any stakeholder experience preferences not yet captured in `ui-ux.md` that should govern this review?"*
4. *"Has this design been informed by any prior sprint user feedback? If so, please summarise the key signals."*

---

## Outputs

### Primary: `experience-conformance-report.md`
```markdown
# Experience Conformance Report
**Sprint:** [sprint_id]  **Date:** [date]  **Reviewer:** ExperienceStudio B-01

## Gate 2 Status: [PASS ✅ | BLOCKED 🚫]

## Coverage Matrix
| Journey ID | Requirement ID | UI Component | Status | Notes |
|------------|---------------|--------------|--------|-------|
| J-001 | REQ-UI-001 | LoginForm.tsx | ALIGNED | — |
| J-002 | REQ-UI-003 | Dashboard.tsx | DEVIATED | See revision #1 |
| J-003 | REQ-UI-005 | — | UNCOVERED | No UI path found |

## Revision Requests (Blocking)
### Revision #1 — J-002 deviates from REQ-UI-003
**Intent violated:** "User must be able to filter results without losing current context"
**Observed:** Modal overlay clears filter state on dismiss
**Required change:** Persist filter state across modal lifecycle

## Gate 2 Attestation
[Issued when all journeys ALIGNED]
Signed off: ExperienceStudio B-01 | All [N] journeys conformant
```

### Secondary: Inline revision requests embedded in the report with:
- `journey_id` reference
- `requirement_id` reference
- Specific design change required (not a preference — a traceable spec obligation)

---

## Limitations & Escalation
- Cannot enforce **unstated** aesthetic preferences. If POD Lead has implicit expectations not in `ui-ux.md`, they must be documented before ExperienceStudio can enforce them.
- **EXTENDED** items (design additions beyond spec) require POD Lead decision: accept as scope addition, reject, or defer.
- Does not validate accessibility compliance (WCAG) — that is within `policy-catalogue.yaml` scope.

---

## Integration Points
| Skill | Direction | Data Exchanged |
|-------|-----------|----------------|
| KnowledgeMesh | Upstream | Retrieves relevant `ui-ux.md` chunks and prior sprint feedback |
| DevCopilot | Downstream | Passes conformance report so builders know which revisions to implement |
| ReviewPilot | Downstream | Conformance report is attached as evidence to the PR for spec-ID verification |
| Conductor | Reports to | Gate 2 attestation triggers sprint board state update |

---

## References
- `references/ux-elicitation-questions.md` — Full elicitation question bank
- `references/journey-mapping-guide.md` — How to extract journeys from `ui-ux.md`
- `references/conformance-scoring-rubric.md` — Detailed ALIGNED/DEVIATED/UNCOVERED/EXTENDED criteria
- `sample_input/sample-ui-spec.md` — Example `ui-ux.md` fragment
- `sample_output/sample-conformance-report.md` — Worked example output
