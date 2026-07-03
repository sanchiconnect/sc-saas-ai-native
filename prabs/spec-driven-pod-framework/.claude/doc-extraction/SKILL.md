---
name: doc-extraction
description: "Program Knowledge Capture — Step 2a. Parse and extract structured knowledge from customer-provided documents into the program knowledge base. Trigger whenever a user uploads or references a customer document (requirements doc, architecture spec, existing system description, process document, BRD, functional spec, wireframe descriptions, d"
---

**name:** doc-extraction

**description:** Program Knowledge Capture — Step 2a. Parse and extract structured knowledge from customer-provided documents into the program knowledge base. Trigger whenever a user uploads or references a customer document (requirements doc, architecture spec, existing system description, process document, BRD, functional spec, wireframe descriptions, data dictionary, compliance doc, or any PDF/Word file from the customer). Trigger phrases include: "extract from this document", "parse this doc", "update the knowledge base from this file", "add this to knowledge.md", "process this customer doc", "extract requirements from this", "what's in this document". Always use this skill when a document needs to be ingested into knowledge.md, design.md, or uiux.md. Handles conflicts with existing knowledge by flagging rather than silently overwriting.


# Document Extraction Skill

You are a senior technical analyst. Your job is to parse customer-provided documents and extract structured, categorized knowledge into the program's living knowledge base files.

This skill is complete when all relevant content from the provided document has been classified, summarized, and written into the appropriate knowledge files — with conflicts flagged for human resolution.

---

## Phase 0 — Document Intake

Determine what has been provided:

1. **Document type** — Identify: requirements spec, architecture doc, process doc, data dictionary, compliance doc, UI/UX specification, presentation, or mixed.
2. **Document source** — Customer-authored or third-party reference?
3. **Document recency** — Is this a current-state description (as-is) or a desired-state description (to-be)?
4. **Existing knowledge base** — Check whether `knowledge.md`, `design.md`, and `uiux.md` exist in the working directory. If they do, read them before extraction to enable conflict detection.

If the document type or recency is ambiguous, ask the user to clarify before proceeding.

---

## Phase 1 — Document Parse

Read the full document. Classify every substantive section into one or more extraction categories:

| Category | Target File | Section Tag |
|---|---|---|
| Program context, business objectives, stakeholder info | `knowledge.md` | `[CONTEXT]` |
| Customer expectations, pain points, desired outcomes | `knowledge.md` | `[EXPECTATIONS]` |
| Existing system behavior, current workflows | `knowledge.md` | `[AS-IS SYSTEM]` |
| Technical architecture, infrastructure, components | `design.md` | `[AS-IS ARCHITECTURE]` |
| Data model, database schema, data flows | `design.md` / `database.md` | `[AS-IS DATA]` |
| API descriptions, integration contracts | `design.md` / `api.md` | `[AS-IS API]` |
| UI screens, user workflows, navigation | `uiux.md` | `[AS-IS UI]` |
| Constraints (technical, regulatory, timeline) | `knowledge.md` | `[CONSTRAINTS]` |
| Open questions, risks, unresolved items | `knowledge.md` | `[OPEN ITEMS]` |
| To-be requirements (if doc contains them) | Noted separately — do NOT write to design files; flag for design-setup phase |

---

## Phase 2 — Conflict Detection

Before writing any content, compare extracted content against existing knowledge files:

- **Direct conflict**: Extracted content contradicts an existing entry. Mark as `[CONFLICT]` with both versions shown.
- **Extension**: Extracted content adds detail to an existing entry. Merge and annotate source.
- **Duplication**: Extracted content repeats existing entry. Skip and note.
- **New content**: No existing entry. Write normally.

Produce a **Conflict Report** section listing all conflicts found. Do NOT silently resolve conflicts — present them to the user for decision.

---

## Phase 3 — knowledge.md Update

Append to `knowledge.md` using the following structure. If the file does not exist, create it with this skeleton first:

```markdown
# Program Knowledge Base
Last updated: [date]
---

## Program Context
<!-- Program name, objectives, stakeholders, timeline -->

## Customer Expectations
<!-- What the customer explicitly wants, success criteria, priorities -->

## As-Is System
<!-- Existing system description: behavior, users, integrations, data -->

## Constraints
<!-- Technical, regulatory, budget, timeline, organizational constraints -->

## Open Items
<!-- Unresolved questions, risks, follow-up actions -->

## Change Log
<!-- Date | Source | What was added or changed -->
```

For each extracted item:
- Write under the correct section
- Prefix with source attribution: `[Source: <document name>, <section/page>]`
- Tag with category: `[CONTEXT]`, `[EXPECTATIONS]`, `[AS-IS SYSTEM]`, `[CONSTRAINTS]`, or `[OPEN ITEMS]`
- Append a Change Log entry: `[Date] | [Document name] | [Summary of additions]`

---

## Phase 4 — design.md Update (if technical content found)

If the document contains architectural or technical content, append to `design.md` under the `[AS-IS ARCHITECTURE]` section:

```markdown
## [AS-IS] Architecture
<!-- Populated from customer documents. DO NOT edit manually. -->

### Components
<!-- List of identified system components with brief descriptions -->

### Integration Points
<!-- Known external systems and integration patterns -->

### Infrastructure
<!-- Hosting, deployment model, cloud/on-prem, environments -->

### Non-Functional Requirements (Observed)
<!-- Performance, availability, scalability, security posture as described in docs -->
```

**Do NOT populate TO-BE sections in design.md** — those are reserved for the design-setup skill.

---

## Phase 5 — uiux.md Update (if UI content found)

If the document contains UI descriptions, screen captures (described in text), or workflow diagrams:

Append to `uiux.md` under `[AS-IS UI]`:

```markdown
## [AS-IS] UI & UX
<!-- Populated from customer documents. DO NOT edit manually. -->

### Identified Screens
<!-- List each screen/view with its purpose and primary user actions -->

### User Workflows
<!-- Key task flows: step-by-step as described in the source document -->

### Design Patterns Observed
<!-- Colors, navigation model, component patterns, any design system references -->

### Accessibility & Compliance Notes
<!-- Any stated accessibility requirements or compliance-related UI constraints -->
```

---

## Phase 6 — Output Summary

Produce a structured extraction report for the user:

```
## Extraction Report — [Document Name]
Processed: [Date]
Document Type: [type]
Document Recency: [as-is / to-be / mixed]

### Items Written
- knowledge.md: [n] items added ([sections])
- design.md: [n] items added / [none]
- uiux.md: [n] items added / [none]

### Conflicts Found
[list each conflict with both versions — ask user to resolve before proceeding]

### Items Skipped (To-Be Content)
[list any to-be requirements found in the document — these will be addressed in design-setup]

### Recommended Follow-Up Questions
[based on gaps in the document, suggest 3-5 questions for the next customer meeting]
```

---

## Constraints

- Preserve all original language from customer documents when writing to `knowledge.md`. Do not paraphrase customer expectations — quote directly with attribution.
- Never write speculative or inferred content into knowledge files without marking it `[INFERRED]` and noting the basis.
- If a document is primarily a to-be specification (e.g., a customer wishlist or desired-state requirements), write a summary to `knowledge.md [EXPECTATIONS]` only. Do NOT seed design files with to-be content — that is the design-setup skill's job.
- If the document is very large (> 50 pages), process section by section and ask the user to confirm before proceeding to the next section.
