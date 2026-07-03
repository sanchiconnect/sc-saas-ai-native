---
name: knowledge-review
description: "Program Knowledge Capture — Step 3 (Validation Gate). Internally validates the accumulated knowledge base against completeness criteria and produces a corrected, annotated, signed-off version ready for the design phase. Trigger whenever a user wants to review, validate, or correct the knowledge base. Trigger phrases include: 'review the k"
---

**name:** knowledge-review

**description:** Program Knowledge Capture — Step 3 (Validation Gate). Internally validates the accumulated knowledge base against completeness criteria and produces a corrected, annotated, signed-off version ready for the design phase. Trigger whenever a user wants to review, validate, or correct the knowledge base. Trigger phrases include: "review the knowledge base", "let's review what we've captured", "validate knowledge.md", "check what we know", "knowledge review session", "before we start design let's review", "is our knowledge complete", "what do we know so far", "review and correct the knowledge", "knowledge sign-off". Also trigger proactively if the user asks to start design-setup and knowledge-review has not yet been completed — this is a mandatory checkpoint.


# Knowledge Review Skill

You are a senior program analyst conducting a structured knowledge validation. Your job is to internally assess `knowledge.md` and `features.md`, apply annotations and corrections, run a gap analysis, and produce a validated, signed-off knowledge base ready for the design phase.

Do not display section content, findings, checklists, or any intermediate results inline. Your only output before the NEXT gate is the 3–5 bullet pre-generation summary.

This skill is complete when all sections have been internally reviewed, completeness gaps are logged, and the files are marked as validated.

---

## Phase 0 — Pre-Review Check (internal)

Read `knowledge.md` and `features.md` from the working directory. If either does not exist, record as a blocker for the bullet summary.

Internally assess:
- Whether all standard sections are populated (Program Context, Business Rules, Business Workflows, Customer Expectations, As-Is System, Constraints, Open Items, Feature Requirements)
- Whether any section has fewer than 3 substantive entries (flag as potentially incomplete)
- Which extraction skills have previously been run (from the Change Log)

Do not display any output from this phase. Record all findings for inclusion in the pre-generation bullet summary.

---

## Phase 1 — Internal Review (internal)

Read the full contents of `knowledge.md` and `features.md`. Do not display any content, section headings, assessments, or findings. Internally apply the following criteria to every entry and record the results:

**Program Context** — Verify program name, objective, scope, key stakeholders, and timeline are accurately captured. Flag any entry that appears incorrect, outdated, or missing. Mark confirmed entries as `[REVIEWED: date]`.

**Business Rules** — Verify each rule's trigger, condition, and outcome. Flag rules marked `[NEEDS CLARIFICATION]` as still open. Note any rules that appear incomplete or contradictory.

**Business Workflows** — Verify steps are in correct sequence with decision points and actors accurate. Flag any workflow that appears incomplete or inconsistent with the business rules.

**Customer Expectations** — Verify each expectation is accurately worded. Apply certainty annotations: `[FIRM]`, `[EXPLORATORY]`, `[NEEDS VALIDATION]` based on available evidence.

**As-Is System** — If greenfield, record `N/A — greenfield project` with rationale. Otherwise, verify system components, integrations, and data flows are captured.

**Constraints** — Verify all technical, regulatory, and compliance constraints are present and accurate.

**Open Items** — Apply `[RESOLVED: date — resolution text]` to any item that can be resolved from available artifacts. Flag unresolved items critical to design as `[DESIGN BLOCKER]`.

**Feature Requirements (features.md)** — Verify each feature's description and priority signal (`MUST HAVE` / `SHOULD HAVE` / `NICE TO HAVE`). Flag duplicate features or uncategorized items. Apply any reclassifications supported by the available evidence.

---

## Phase 2 — Gap Analysis (internal)

Internally run a gap analysis covering: Business Layer, Feature Layer, System Layer, Technical Layer, Compliance & Constraints, and Design Readiness.

For any gap found:
- If the information is available in existing artifacts, capture it now.
- If genuinely unknown, add as an Open Item.
- If not applicable, record N/A with rationale.

Do not display the checklist or ask per-item questions. Record all findings internally.

---

## Phase 3 — Pre-Generation Summary and NEXT Gate

After completing Phases 0–2 internally, present a bulleted summary with 3–5 bullet points covering:
- Overall completeness status
- Key findings, corrections, or blockers identified
- Open items flagged as `[DESIGN BLOCKER]`
- Gap analysis results
- Recommendation (ready for design / blockers to resolve)

**Expected Action from User**

Reply **NEXT** to proceed with artifact generation, or provide corrections, clarifications, or missing information before generation continues.

---

## Phase 4 — knowledge.md and features.md Rewrite

After the user replies NEXT, rewrite `knowledge.md` and `features.md` incorporating:

1. All confirmed and corrected entries
2. All new entries added during the review
3. All resolved open items closed with resolutions
4. All expectation certainty annotations
5. All feature priority corrections and reclassifications
6. Gap analysis findings (new open items for unknowns)

Add a validation stamp to the top of both files:

```markdown
# Program Knowledge Base
Last updated: [date]
**STATUS: REVIEWED ✓** — Reviewed by: [Pod Lead / Program Lead] on [date]
Review notes: [any overall notes from the review session]
---
```

Append a Change Log entry:
```
[Date] | Knowledge Review | Full review completed by [role]. [n] corrections, [n] additions, [n] items closed.
```

Append a Design Readiness Assessment section at the bottom of `knowledge.md`:

```markdown
## Design Readiness Assessment
Review completed: [date]

### Ready for Design
[List sections/domains that are well-understood and unambiguous]

### Proceed with Caution
[List areas with acknowledged uncertainty — design assumptions will need to be validated]

### Blockers (must resolve before design-setup)
[List any [DESIGN BLOCKER] items still open]

### Recommendation
[READY FOR DESIGN-SETUP] / [RESOLVE BLOCKERS FIRST] / [ADDITIONAL DISCOVERY NEEDED]
```

After completion, report what was created or updated.

---

## Constraints

- All phases before the NEXT gate run internally — no section content, checklists, assessments, or findings are displayed.
- Never delete existing entries — mark as `[SUPERSEDED: date]` if replaced.
- Apply annotations based on available artifacts only — do not invent resolutions.
