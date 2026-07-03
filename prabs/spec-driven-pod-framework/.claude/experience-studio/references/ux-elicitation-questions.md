# UX Elicitation Questions — ExperienceStudio

Use this question bank when `ui-ux.md` is absent, sparse, or the design under review covers user journeys not yet documented. Ask questions in priority order. Do not batch; ask one at a time and wait for the answer before proceeding.

---

## Tier 1 — Minimum Required (always ask if missing)

**Q1. User Journey Identification**
> "Which specific user journey or task flow does this design implement? Please describe it in one sentence: 'As a [role], I need to [action] so that [outcome].'"

**Q2. Success Definition**
> "What does a successful interaction look like from the user's perspective? What must they be able to accomplish without friction?"

**Q3. Failure / Edge Cases**
> "What are the 2–3 most likely failure states for this flow? (e.g. empty results, validation error, API timeout) Has the design addressed these?"

**Q4. Stakeholder Experience Priority**
> "For this journey, which experience quality matters most to stakeholders: speed of task completion, discoverability, error recovery, or confidence/trust in the output?"

---

## Tier 2 — Design Depth (ask when reviewing detailed UI implementations)

**Q5. Information Hierarchy**
> "What is the single most important piece of information the user needs to see first on this screen? Does the current layout reflect that priority?"

**Q6. Navigation & Context Continuity**
> "After the user completes this action, where do they go next? Does the design make that next step obvious without breaking their current context?"

**Q7. Progressive Disclosure**
> "Are there elements on this screen that will overwhelm a first-time user but are needed by power users? How does the design accommodate both?"

**Q8. Feedback & Confirmation**
> "How does the user know their action succeeded or failed? Is that feedback immediate, and is it unambiguous?"

---

## Tier 3 — Stakeholder Alignment (ask when Gate 2 sign-off is in dispute)

**Q9. Implicit Preferences**
> "Are there design preferences from key stakeholders that haven't been formally documented in `ui-ux.md`? If so, describe them so I can treat them as constraints."

**Q10. Prior Feedback Integration**
> "Has user testing, stakeholder demo feedback, or InsightOps data from a prior sprint influenced this design? What were the specific signals and how are they reflected here?"

**Q11. Brand / Tone Constraints**
> "Are there visual tone or language constraints (formal vs conversational, brand colour rules, icon library restrictions) that this design must respect?"

---

## How to Document Answers
All answers received through this elicitation must be appended to `specs/ui-ux.md` under a clearly marked section:
```
## Sprint [ID] Elicited Requirements
Source: ExperienceStudio elicitation session [date]
[Answers verbatim, attributed to POD Lead or stakeholder]
```
This ensures future sprints and SpecImpactAnalyzer can reference the captured intent.
