---
name: portfolio-prioritizer
description: "PortfolioPrioritizer ranks all backlog items using a composite score of value, urgency, and dependencies, then draws a capacity cut line — above it: this sprint; below it: deferred. It ensures a 2-builder team always builds the highest-value items within their capacity."
---

# SKILL: PortfolioPrioritizer
**SpecPod Framework v2.1.0 · Planning · 11 — Proposed**
**Model:** claude-sonnet-4-20250514 · **Context Budget:** ~35K tokens
**Role:** Sprint backlog ranking and defer analysis

> ⬡ **Proposed** — scoring model and weighting criteria require stakeholder alignment before production use. Strategic context not in the spec (political priorities, stakeholder relationships) cannot be inferred automatically.

---

## Purpose
PortfolioPrioritizer ranks all backlog items using a composite score of value, urgency, and dependencies, then draws a capacity cut line — above it: this sprint; below it: deferred. It ensures a 2-builder team always builds the highest-value items within their capacity. Every defer decision is documented with a rationale that feeds directly into the next sprint's backlog.

---

## Trigger
Invoke after ValueModeler produces `roi-brief.md` (Step 5 of Monday planning, in sequence after ValueModeler).

**Activation phrase:** `Run PortfolioPrioritizer` or `Rank sprint backlog`

---

## Required Input Files

| File | Source | Required? |
|------|--------|-----------|
| `artifacts/roi-brief.md` | ValueModeler | REQUIRED |
| `artifacts/task-breakdown.yaml` | SpecFlow | REQUIRED |
| `artifacts/traceability-report.md` | TraceGraph | REQUIRED |
| `artifacts/opportunity-backlog-rescored.md` | TransformIQ | REQUIRED |
| `specs/features.md` | spec-generation (prior phase) | REQUIRED |
| `specs/program.md` | program-charter (prior phase) | REQUIRED |

---

## User Inputs Required

1. **Sprint capacity:** "What is the total builder-hours available this sprint? (N builders × N hours/day × N days)"
2. **Strategic weights:** "Rate the following scoring dimensions 1–10 for this sprint:
   - [A] Business value (from ValueModeler ROI)
   - [B] Urgency / time-sensitivity
   - [C] Strategic alignment (from program.md objectives)
   - [D] Dependency enablement (unblocks other items)
   - [E] Risk reduction"
3. **Capacity buffer:** "Reserve what % of capacity as a buffer for unplanned work? (default: 15%)"
4. **Must-ship items:** "Are there any non-negotiable items that must ship regardless of score? (list REQ-IDs or NONE)"
5. **Override:** "Any manual priority overrides from the POD Lead or business lead? (describe or NONE)"

---

## Processing Instructions

### Phase 1 — Candidate Inventory
1. Load all in-scope requirements from `artifacts/task-breakdown.yaml`
2. Load all TransformIQ candidate additions from `artifacts/opportunity-backlog-rescored.md`
3. Combine into a unified candidate list with REQ-ID, effort estimate, and ROI brief values

### Phase 2 — Composite Scoring
For each candidate, compute:
```
Score = (Value × WA) + (Urgency × WB) + (Strategic × WC) + (Dependency × WD) + (Risk × WE)
```
Where W values are the POD Lead's strategic weights normalised to sum to 1.

- Value score: from `roi-brief.md` value/hour ratio, normalised 0–10
- Urgency score: POD Lead input or deadline signals in openspec.yaml
- Strategic score: alignment with `specs/program.md` programme objectives (0–10)
- Dependency score: how many other items are unblocked if this ships (from traceability-report.md)
- Risk score: inverse of assumption confidence from assumption-log.md (low confidence = deferred preferred)

### Phase 3 — Must-Ship Override
Insert must-ship items at the top of the ranked list regardless of score. Mark with `OVERRIDE: MUST-SHIP`.

### Phase 4 — Dependency Cluster Locking
Using the dependency graph from `artifacts/traceability-report.md`:
1. Identify dependency clusters: groups of items that must move together
2. Score each cluster as a unit (use the lowest item score in the cluster — the weakest link)
3. If a cluster's lowest-scoring item falls below the cut line, the entire cluster is deferred unless a MUST-SHIP override applies

### Phase 5 — Capacity Cut Line
1. Calculate available capacity: builder_hours × (1 - buffer_pct)
2. Sort ranked list by score descending
3. Walk down the list, accumulating effort hours until capacity is reached
4. Draw the cut line: items above = PROCEED / items below = DEFERRED
5. Flag any item close to the cut line (within 10% of capacity threshold) as `BORDERLINE` for POD Lead judgment

### Phase 6 — Defer Rationale Generation
For each DEFERRED item, generate a one-sentence rationale:
- Low score: "Deferred — value/effort ratio below sprint threshold (score: N)"
- Capacity: "Deferred — capacity consumed by higher-priority items"
- Dependency: "Deferred — cluster dependency [REQ-ID] deferred; cannot proceed without it"

---

## Output Files

### `artifacts/sprint-scope-ranked.md`
```markdown
# Sprint Scope — Ranked — Sprint [ID]
Generated: [Timestamp]

## Capacity Summary
- Available: N builder-hours
- Reserved buffer (15%): N hours
- Usable: N hours
- Allocated (PROCEED items): N hours
- Utilisation: N%

## Sprint Scope — PROCEED
| Rank | REQ-ID | Description | Score | Hours | Cumulative Hours | Flag |
|------|--------|-------------|-------|-------|-----------------|------|
| 1 | REQ-001 | Login flow | 8.7 | 3h | 3h | MUST-SHIP |
| 2 | REQ-003 | Profile API | 7.2 | 2h | 5h | — |
| ... |

— CUT LINE (N hours) —

## Deferred to Next Sprint
| REQ-ID | Description | Score | Defer Rationale | Next Sprint Priority |
|--------|-------------|-------|----------------|---------------------|
| REQ-007 | Bulk export | 3.1 | Low value/effort ratio | LOW |

## Borderline Items (POD Lead Decision Required)
| REQ-ID | Description | Score | Hours | Reason for Review |
|--------|-------------|-------|-------|------------------|

## Dependency Clusters Deferred
[Cluster ID, items affected, reason]
```

---

## Limitations
- Scoring weights must be calibrated by humans. Stale or incorrect weights produce misleading rankings.
- Political priorities and stakeholder relationships not captured in the spec cannot be inferred — POD Lead must apply these manually via overrides.
- PortfolioPrioritizer recommends; the POD Lead decides. Borderline items always require human judgment.
