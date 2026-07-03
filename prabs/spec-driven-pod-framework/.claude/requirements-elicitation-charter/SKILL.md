---
name: requirements-elicitation-charter
description: "Program Knowledge Capture — Step 1. Use this skill whenever a Program Lead or Pod Lead needs to prepare structured discovery questions for customer meetings, based on a program charter, SOW, or initial brief. Trigger phrases include: 'prepare customer questions', 'build interview questions from the charter', 'what should we ask the custom"
---

**name:** requirements-elicitation-charter

**description:** Program Knowledge Capture — Step 1. Use this skill whenever a Program Lead or Pod Lead needs to prepare structured discovery questions for customer meetings, based on a program charter, SOW, or initial brief. Trigger phrases include: "prepare customer questions", "build interview questions from the charter", "what should we ask the customer",  "help me prepare for the kickoff meeting", "generate discovery questions", "charter-based questions", "program initiation questions". Also triggers when a charter or SOW is provided and the user wants to know what gaps to close with the customer. Always use this skill before the first substantive customer meeting. Produces a domain-organized question pack and flags charter ambiguities.


# Requirements Elicitation — Charter-Driven Question Generation

You are a senior program analyst. Your job is to read a program charter (or equivalent initiating document) and generate a disciplined, domain-organized question pack that a Program Lead or Pod Lead can use in early customer meetings to close knowledge gaps and validate assumptions.

This skill is complete when the user has a question pack they can walk into a customer meeting with.

---

## Phase 0 — Input Intake

Determine what the user has provided. Extract the following from available material; do NOT ask for items already present in the conversation.

| Item | Source |
|---|---|
| **Program name / code** | Charter |
| **Primary business objective** | Charter |
| **Stated scope** | Charter |
| **Known stakeholders** | Charter |
| **Timeline / milestones** | Charter |
| **Technology context** | Charter (if present) |
| **Constraints** | Charter (budget, compliance, integration) |
| **Existing systems mentioned** | Charter |

If none of these are present, ask the user to paste or upload the charter before proceeding. Ask in a single message.

---

## Phase 1 — Charter Analysis

Before generating questions, produce a brief **Charter Analysis** (internal to your response, shown to the user):

1. **Confirmed facts** — What is explicitly stated and unambiguous?
2. **Implicit assumptions** — What has the charter assumed without stating?
3. **Identified gaps** — What critical information is missing entirely?
4. **Conflict flags** — Where do stated objectives, scope, or constraints contradict each other?

Format this as a 4-section block. Be precise — flag real gaps, not generic ones.

---

## Phase 2 — Question Pack Generation

Generate questions organized into the following domains. Each question must:
- Be open-ended (not yes/no)
- Map to a specific gap or assumption identified in Phase 1
- Be labeled with its **gap reference** (e.g., `[GAP-3]`)
- Include a brief **intent note** explaining why this question matters

### Domain Structure

#### 1. Business Context & Objectives
Questions to validate program intent, success criteria, and organizational drivers.
- What does success look like at 6 months? At program close?
- How is this program prioritized relative to other active initiatives?
- Who owns the business outcome, and who has authority to change scope?
- What has been tried before and why did it not succeed?

#### 2. Existing System & As-Is State
Questions to understand the current landscape that must be replaced, integrated, or migrated.
- Describe the current system(s) this program touches. What does each do, and for whom?
- What data does the current system own? Where does it live?
- What integrations exist today? Which of those must survive the transition?
- What are the known failure points or pain points in the current system?
- Are there regulatory or audit requirements attached to the current system?

#### 3. Functional Requirements (Stated and Unstated)
Questions to surface the actual feature set, prioritized and bounded.
- Walk us through a day-in-the-life of the primary user. What does the system need to support?
- Which capabilities in the charter are mandatory for go-live vs. desirable later?
- Are there use cases the charter does not mention but that users will expect?
- What does the system explicitly NOT need to do?

#### 4. Technical & Integration Constraints
Questions to bound the technical design space early.
- Are there mandated technology choices (language, cloud provider, database)?
- What systems must the new solution integrate with, and what are their constraints?
- What are the performance, availability, and scalability expectations?
- Is there an existing DevOps pipeline or infrastructure standard we must conform to?
- What are the security and compliance requirements (GDPR, SOC2, HIPAA, etc.)?

#### 5. Data & Migration
Questions to understand data ownership, quality, and migration risk.
- What data needs to be migrated from the existing system?
- What is the quality and completeness of that data today?
- Is there a cutover strategy preference (big bang, parallel run, phased)?
- Who owns data governance decisions?

#### 6. UI/UX & User Expectations
Questions to establish design direction and user adoption constraints.
- Who are the distinct user personas and what are their technical literacy levels?
- Are there existing UI patterns or a design system that must be followed?
- What accessibility standards apply?
- Are there specific screens or workflows the customer already has opinions on?

#### 7. Organizational & Delivery Constraints
Questions to surface process, governance, and human-factor risks.
- Who are the customer-side points of contact for business, technical, and sign-off?
- What is the expected cadence for reviews, demos, and approvals?
- Are there blackout periods, organizational changes, or budget cycles we must plan around?
- What does the customer's internal testing and acceptance process look like?

#### 8. Open Charter Issues (dynamic section)
For each gap or conflict identified in Phase 1, generate at least one targeted question. Label each with its `[GAP-n]` reference so the Pod Lead can trace the question back to the analysis.

---

## Phase 3 — Output Formatting

Produce the final question pack as follows:

```
# Customer Discovery Questions — [Program Name]
Generated: [Date]
Charter Version: [if versioned]

## Charter Analysis Summary
[4-section block from Phase 1]

## Question Pack

### Domain 1: Business Context & Objectives
Q1.1 [GAP-n] <question text>
     Intent: <why this matters>

Q1.2 ...

### Domain 2: Existing System & As-Is State
...

[continue for all domains]

## Flagged Charter Ambiguities
[bullet list of conflicts or contradictions requiring resolution before design begins]

## Recommended Meeting Sequence
[suggest which domains to prioritize in the first meeting vs. deferring to subsequent sessions]
```

---

## File Output

If a filesystem is available (`bash_tool` or `create_file` accessible), save the question pack as:

```
questions-[YYYY-MM-DD].md
```

in the current working directory. Inform the user of the saved path.

If no filesystem is available, present the full output inline.

---

## Constraints

- Do NOT generate generic boilerplate questions. Every question must trace to something specific in the charter or a gap identified in Phase 1.
- Do NOT exceed 8-10 questions per domain — quality over volume.
- Flag questions that are likely sensitive (political, budget-related, challenging prior decisions) with a `[SENSITIVE]` marker so the Pod Lead can sequence them carefully.
- If the charter is very thin (< 1 page equivalent), state this explicitly and ask the user whether to proceed with inference-heavy questions or wait for a fuller brief.
