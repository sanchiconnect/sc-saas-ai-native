---
name: research-copilot
description: "ResearchCopilot validates each draft requirement against available discovery evidence — interviews, user feedback, analytics, support tickets, and prior sprint reports. It classifies evidence strength per requirement, surfaces contradictions between stated requirements and observed user behaviour, and flags weak-evidence requirements a..."
---

# SKILL: ResearchCopilot
**SpecPod Framework v2.1.0 · Planning · 07**
**Model:** claude-sonnet-4-20250514 · **Context Budget:** ~80K tokens
**Role:** Discovery evidence synthesis for requirements

---

## Purpose
ResearchCopilot validates each draft requirement against available discovery evidence — interviews, user feedback, analytics, support tickets, and prior sprint reports. It classifies evidence strength per requirement, surfaces contradictions between stated requirements and observed user behaviour, and flags weak-evidence requirements as AssumptionTracker candidates. Prevents building requirements that lack user or data evidence.

---

## Trigger
Invoke in parallel with PolicyCatalog, ContextFabric, and TransformIQ at Step 1 of Monday planning.

**Activation phrase:** `Run ResearchCopilot` or `Synthesise discovery evidence`

---

## Required Input Files

| File | Source | Required? |
|------|--------|-----------|
| `artifacts/openspec.yaml` | POD Lead (locked) | REQUIRED |
| `specs/knowledge.md` | spec-knowledge (prior phase) | REQUIRED |
| `specs/features.md` | spec-generation (prior phase) | REQUIRED |
| Interview transcripts or meeting notes | User (upload) | IF AVAILABLE |
| Analytics exports / usage telemetry | User (upload) | IF AVAILABLE |
| Prior sprint validation reports | User (upload) | IF AVAILABLE |
| Support ticket exports | User (upload) | IF AVAILABLE |

---

## User Inputs Required

ResearchCopilot will ask the following at the start of the session:

1. **Evidence availability:** "Which evidence sources are available for this sprint? Select all that apply: [a] interview transcripts [b] user survey results [c] analytics/telemetry export [d] support ticket export [e] prior sprint validation report [f] stakeholder meeting notes [g] none"
2. **Evidence recency:** "What is the date range for the evidence you're providing? (Older evidence is weighted lower)"
3. **Contradiction handling:** "When a requirement contradicts observed user behaviour, should I: [a] flag and block until resolved [b] flag as warning but proceed [c] log only"
4. **Minimum evidence level:** "What is the minimum evidence strength required to proceed without AssumptionTracker escalation? (confirmed / partial — default: partial)"

If no evidence sources are available:
> "No discovery evidence is available. All requirements will be classified as NO-EVIDENCE and escalated to AssumptionTracker. Do you want to proceed? (yes/no)"

---

## Processing Instructions

### Phase 1 — Requirement Extraction
1. Extract all requirements from `artifacts/openspec.yaml` with their IDs and descriptions
2. Load `specs/knowledge.md` for domain context and prior research signals
3. Load `specs/features.md` for feature-level intent context

### Phase 2 — Evidence Indexing
For each evidence document provided:
1. Extract key observations, data points, and user statements
2. Tag each observation with: source, date, evidence type (qualitative/quantitative), strength
3. Build a searchable evidence index

### Phase 3 — Cross-Reference
For each requirement:
1. Search the evidence index for supporting observations
2. Classify evidence strength:
   - **CONFIRMED:** ≥2 independent sources directly support the requirement
   - **PARTIAL:** 1 source or indirect support — requirement is directionally validated
   - **WEAK:** Evidence is anecdotal, single-stakeholder opinion, or >90 days old
   - **CONTRADICTED:** Available evidence suggests the requirement is not what users need
   - **NO-EVIDENCE:** No evidence found in any source
3. Record the top 2–3 evidence citations per requirement (source + excerpt summary)

### Phase 4 — Contradiction Detection
For requirements classified CONTRADICTED:
1. Summarise the contradiction: what the requirement states vs. what evidence shows
2. Classify contradiction severity: MINOR / MAJOR / BLOCKING
3. BLOCKING contradictions prevent the requirement from being dispatched until resolved

### Phase 5 — AssumptionTracker Escalation
Flag requirements classified WEAK, CONTRADICTED, or NO-EVIDENCE as candidates for AssumptionTracker with:
- Current evidence classification
- Confidence score estimate (0–1)
- Recommended resolution action (additional research / stakeholder interview / proceed with risk acceptance)

---

## Output Files

### `artifacts/evidence-map.md`
```markdown
# Evidence Map — Sprint [ID]
Generated: [Timestamp] · Evidence Sources: N

## Evidence Coverage Summary
- CONFIRMED: N requirements
- PARTIAL: N requirements
- WEAK: N requirements
- CONTRADICTED: N requirements
- NO-EVIDENCE: N requirements

## Requirement Evidence Breakdown

### REQ-001 — [Description]
**Evidence Strength:** CONFIRMED
**Citations:**
- [Source: Interview transcript 2026-05-10] User stated: "[paraphrased observation]"
- [Source: Analytics export Q1] 73% of users navigated to this feature in the first session
**AssumptionTracker:** NOT REQUIRED

---

### REQ-007 — [Description]
**Evidence Strength:** CONTRADICTED — BLOCKING
**Stated Requirement:** Users want bulk export functionality
**Observed Behaviour:** Analytics shows < 2% of users have ever used export features. Support tickets show complaints about export complexity, not demand for bulk.
**Contradiction Severity:** MAJOR
**Recommended Action:** Stakeholder review before proceeding. Consider scoping to a simpler export improvement.
**AssumptionTracker:** ESCALATED — confidence: 0.2

---

## AssumptionTracker Escalation List
| REQ-ID | Evidence Level | Confidence | Recommended Action |
|--------|---------------|------------|-------------------|
| REQ-007 | CONTRADICTED | 0.2 | Stakeholder review |
| REQ-012 | NO-EVIDENCE | 0.1 | Additional research |

## Contradiction Summary
| REQ-ID | Severity | Action Required |
|--------|----------|-----------------|
```

---

## Limitations
- Only as good as the evidence inputs provided. Tribal knowledge in verbal meetings or undocumented stakeholder decisions are invisible without transcript input.
- Evidence classification is heuristic — ResearchCopilot identifies signals, not legal proof of user need.
- Recency bias: evidence older than 90 days is automatically downweighted to WEAK unless corroborated by a recent source.
