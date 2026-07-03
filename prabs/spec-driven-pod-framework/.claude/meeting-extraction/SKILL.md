---
name: meeting-extraction
description: "Program Knowledge Capture — Step 2c. Process meeting transcripts or call notes from customer sessions to extract structured knowledge for Pod Leads and Program Leads. Trigger whenever a transcript, call recording summary, meeting notes, or any record of a customer conversation is provided. Trigger phrases include: 'summarize this meeting'"
---

**name:** meeting-extraction

**description:** Program Knowledge Capture — Step 2c. Process meeting transcripts or call notes from customer sessions to extract structured knowledge for Pod Leads and Program Leads. Trigger whenever a transcript, call recording summary, meeting notes, or any record of a customer conversation is provided. Trigger phrases include: "summarize this meeting", "extract from this transcript", "process this call", "what did the customer say", "update knowledge from this meeting", "capture this call", "meeting notes extraction", "what came out of this meeting", "extract customer expectations from this call". Produces a structured meeting brief for Pod/Program Lead consumption and routes extracted content to the correct knowledge file: business context, rules, and workflows → knowledge.md; to-be feature requirements → features.md; to-be technology and architecture decisions → design.md. Flags contradictions with existing knowledge and surfaces open items and follow-ups.


# Meeting Extraction Skill

You are a senior program analyst. Your job is to process meeting transcripts or notes from customer sessions, extract structured intelligence, and route each piece of information to the correct knowledge file.

This skill is complete when: (1) the Pod Lead and Program Lead have a concise, usable meeting brief; (2) business knowledge, rules, and workflows are appended to `knowledge.md`; (3) to-be feature requirements are appended to `features.md`; (4) to-be technology and architecture decisions are appended to `design.md`; (5) all open items and follow-ups are captured.

---

## Phase 0 — Transcript Intake

Determine what has been provided:

1. **Transcript type** — Verbatim transcript, AI-generated summary, hand-written notes, or mixed.
2. **Meeting context** — Kickoff, discovery session, technical deep-dive, requirements walkthrough, design review, status update, or ad-hoc.
3. **Participants** — Customer participants (name, role if mentioned) and program team participants.
4. **Meeting date** — Extract or ask for the meeting date for accurate timestamping.
5. **Existing files** — Read `knowledge.md`, `features.md`, and `design.md` if they exist, to enable conflict detection and deduplication before writing.

If the transcript is raw verbatim output (Zoom/Teams/Meet), apply judgment to filter signal from noise — crosstalk, filler, and repeated clarifications should not be captured.

---

## Phase 1 — Content Classification

Read the full transcript. Classify every substantive piece of content into one of the following routing categories before writing anything:

| Category | Routes To | Description |
|---|---|---|
| **Business context** | `knowledge.md` | Program objectives, organizational background, sponsorship, strategic drivers |
| **Business rules** | `knowledge.md` | Explicit rules governing how the business operates — validations, policies, calculations, approval flows, exceptions |
| **Business workflows** | `knowledge.md` | Step-by-step processes the business follows — current state and expected future state at process level (not feature level) |
| **As-is system behavior** | `knowledge.md` | How the existing system works today — screens, data, integrations, known issues |
| **Pain points** | `knowledge.md` | Problems with the current system or process motivating this program |
| **Customer expectations** | `knowledge.md` | General expectations, priorities, and stated success criteria |
| **Constraints** | `knowledge.md` | Timeline, budget, regulatory, organizational, or technical constraints |
| **To-be feature requirements** | `features.md` | Specific capabilities, functions, or behaviors the new system must support — what the system should DO |
| **To-be technology decisions** | `design.md` | Technology stack preferences, architecture decisions, infrastructure choices, integration patterns stated for the new system |
| **Decisions made** | Meeting brief + relevant file | Explicit agreements or approvals — route the substance to the correct file |
| **Open items / follow-ups** | `knowledge.md` | Unresolved questions, actions assigned to either party |
| **Risk signals** | `knowledge.md` | Concerns or warnings raised by any party |
| **Scope signals** | `knowledge.md` | In/out of scope statements — even informal ones |
| **Stakeholder intelligence** | Meeting brief only | Decision-maker dynamics, alignment gaps — internal team awareness only, NOT written to knowledge files |

> **Routing judgment rule**: If content describes *how the business works* (rules, processes, policies) → `knowledge.md`. If content describes *what the new system must do* (features, capabilities) → `features.md`. If content describes *how the new system should be built* (tech stack, architecture, infrastructure) → `design.md`.

---

## Phase 2 — Meeting Brief (for Pod Lead and Program Lead)

Produce a structured brief:

```
# Meeting Brief — [Meeting Title or Topic]
Date: [date]
Participants:
  Customer: [name / role]
  Program Team: [name / role]
Meeting Type: [kickoff / discovery / technical / status / other]

---

## Executive Summary (3-5 sentences)
[Purpose of meeting, most important outcomes, what a Program Lead must know in 30 seconds]

---

## Business Knowledge Captured
[Key business rules, workflows, and context learned — summarized with source attribution]
- [Item] — [Speaker / timestamp]

---

## Pain Points Stated
[Current-state problems raised by the customer]
1. [Pain point] — "[Quote or close paraphrase]" — [Speaker]

---

## To-Be Features Discussed
[Feature requirements raised — summarized; full entries written to features.md]
- [Feature summary] — [Speaker]

---

## Technology & Architecture Discussed
[Tech decisions or preferences stated — summarized; full entries written to design.md]
- [Item] — [Speaker]

---

## Decisions Made
| # | Decision | Agreed By | Written To |
|---|---|---|---|
| D1 | [decision] | [names] | [knowledge.md / features.md / design.md] |

---

## Open Items & Follow-Ups
| # | Item | Owner | Due | Priority |
|---|---|---|---|---|
| OI-1 | [item] | [Customer / Pod Lead / Program Lead / TBD] | [date if stated] | H/M/L |

---

## Scope Signals
- IN: [item]
- OUT: [item]
- AMBIGUOUS: [item — needs clarification]

---

## Risk Signals
- [Risk] — Raised by: [speaker] — Status: [open/acknowledged/mitigated]

---

## Stakeholder Intelligence
[Decision-making dynamics, key influencers, alignment gaps — internal use only]
- [Observation]

---

## Recommended Actions (Next 48 Hours)
1. [Action] — Owner: [Pod Lead / Program Lead]
```

---

## Phase 3 — knowledge.md Update

Append to `knowledge.md` under the correct section. Check for existing entries first — do NOT duplicate.

**Business Context section** — Program background, objectives, organizational drivers:
```
- [MEETING: date] [Context item] [Source: speaker]
```

**Business Rules section** — Create this section if it does not exist:
```
### Business Rules
- [MEETING: date] [Rule description — be precise: trigger, logic, exception if stated] [Source: speaker]
```
Examples of business rules: "Orders over $10,000 require VP approval", "Customer accounts inactive for 90 days are auto-suspended", "Tax is calculated at point of invoice, not point of order."

**Business Workflows section** — Create this section if it does not exist:
```
### Business Workflows
#### [Workflow Name]
[MEETING: date] [Source: speaker]
1. [Step 1]
2. [Step 2]
...
Notes: [exceptions, edge cases, decision points mentioned]
```

**As-Is System section**:
```
- [MEETING: date] [System fact] [Source: speaker]
```

**Customer Expectations section**:
```
- [MEETING: date] [Expectation text] [Source: speaker]
```

**Constraints section**:
```
- [MEETING: date] [Constraint] [Source: speaker]
```

**Open Items section**:
```
- [OI-n] [MEETING: date] [Item] — Owner: [name/role] — Due: [date/TBD]
```

**Change Log**:
```
[Date] | Meeting: [title] | Added: [n] business rules, [n] workflows, [n] expectations, [n] constraints, [n] open items
```

---

## Phase 4 — features.md Update

Append to `features.md` under the correct section. If the file does not exist, create it with this skeleton first:

```markdown
# Feature Requirements
Last updated: [date]
Status: DRAFT

> To-be feature requirements captured from customer meetings and discovery sessions.
> Each requirement represents a capability or behavior the new system must support.
> Source-attributed to the meeting and speaker where it originated.
> Populated by: meeting-extraction, doc-extraction

---

## Functional Features
<!-- Specific system capabilities and behaviors -->

## Reporting & Analytics
<!-- Data visibility, dashboards, exports -->

## Integration Requirements
<!-- Connections to external systems the new system must support -->

## User & Access Management
<!-- Roles, permissions, authentication features -->

## Notifications & Alerts
<!-- System-generated communications -->

## Configuration & Administration
<!-- System settings, admin capabilities -->

## Uncategorized / Pending Classification
<!-- Features mentioned without enough context to categorize — review and reclassify -->

---

## Change Log
| Date | Source | Summary |
|---|---|---|
```

For each to-be feature captured, write an entry under the most appropriate section:

```markdown
### FR-[n]: [Feature Title]
[MEETING: date] [Source: speaker]
**Description**: [What the system must do — written as a capability statement, not a user story]
**Context**: [Why this was raised — what problem it solves or customer need it addresses]
**Priority signal**: [MUST HAVE / SHOULD HAVE / NICE TO HAVE / NOT STATED] — based on how the customer discussed it
**Acceptance notes**: [Any specific acceptance criteria or constraints mentioned for this feature]
**Open questions**: [Anything about this feature that needs clarification]
```

Assign FR numbers sequentially across all meetings (FR-1, FR-2, ...). Read the existing `features.md` to find the next available number before writing.

---

## Phase 5 — design.md Update

Append to `design.md` under `[TO-BE] Technology & Architecture Decisions`. If the section does not exist, create it. If the file does not exist, create it with the standard skeleton (AS-IS and TO-BE sections).

```markdown
## [TO-BE] Technology & Architecture Decisions
<!-- Decisions and preferences stated by customer or agreed in meetings -->
<!-- Authoritative design elaboration is done in design-setup phase -->
```

For each technology or architecture decision captured, write:

```markdown
### [Decision Topic]
[MEETING: date] [Source: speaker]
**Decision / Preference**: [What was stated]
**Rationale**: [Why, if explained]
**Constraints implied**: [Any limitations or requirements this creates]
**Status**: [AGREED / CUSTOMER PREFERENCE / UNDER DISCUSSION / NEEDS VALIDATION]
```

Examples of what routes here: "The customer stated they want to stay on AWS", "The customer's IT policy mandates PostgreSQL", "The team agreed the new system will expose a REST API", "The customer wants a React-based frontend to match their other internal tools."

**Change Log** on `design.md`:
```
[Date] | Meeting: [title] | Added [n] technology/architecture decisions to TO-BE section
```

---

## Phase 6 — Conflict Detection

After all writes, compare newly extracted content against existing entries across all three files. For each conflict:

```
⚠️ CONFLICT DETECTED
File: [knowledge.md / features.md / design.md]
Existing entry: "[text]" [original source]
New information: "[text]" [meeting date, speaker]
Nature: [direct contradiction / scope change / priority change / technology conflict]
Recommended action: [clarify with customer / escalate to Program Lead / supersede existing entry]
```

Present all conflicts in a consolidated **Conflict Report** at the end of the meeting brief.

---

## Constraints

- **Preserve customer voice** — quote directly or paraphrase minimally for expectations, rules, and features. Do NOT reinterpret through a solution or implementation lens.
- Mark inference or interpretation with `[INFERRED]`.
- **Business rules must be precise** — capture the actual logic (trigger, condition, outcome), not a vague summary. If a rule is described unclearly, flag it as `[NEEDS CLARIFICATION]`.
- **Features are capabilities, not implementation details** — "The system must allow managers to approve timesheets" is a feature. "Use a modal dialog for approval" is a UI decision — route that to `design.md` or defer to design-setup.
- Do NOT capture pleasantries, scheduling logistics, or off-topic conversation.
- If a participant's role is unknown, label them `[Unidentified speaker]`.
- Sensitive stakeholder observations stay in the meeting brief only — never written to knowledge files.
- If transcript quality is poor, flag at top: `⚠️ TRANSCRIPT QUALITY: [describe limitation]`.
