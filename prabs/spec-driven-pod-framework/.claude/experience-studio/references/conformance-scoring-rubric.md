# Conformance Scoring Rubric — ExperienceStudio

## Status Definitions

### ALIGNED ✅
The design decision **directly and completely** implements the stated experience intent.

Criteria (all must hold):
- The UI path covers the full journey from trigger to completion
- The information hierarchy matches the stated priority in `ui-ux.md`
- Error and edge-case states are handled per spec
- No spec-mandated step is absent from the UI flow

### DEVIATED ⚠️ (Blocking)
The design **contradicts** a documented intent. Build is blocked on this journey until resolved.

Sub-types:
- **Omission Deviation** — A required step or element is missing from the implementation
- **Inversion Deviation** — The design does the opposite of the stated intent (e.g. spec says "inline error", design shows modal error)
- **Priority Deviation** — Information hierarchy contradicts stated stakeholder priority
- **Context Break** — Design destroys user context in a flow that requires continuity

### UNCOVERED 🚫 (Blocking)
A journey exists in `ui-ux.md` or `openspec.yaml` but **no corresponding UI path** exists in the submitted design.

This is distinct from DEVIATED: DEVIATED means "a path exists but it's wrong"; UNCOVERED means "no path exists at all".

### EXTENDED ℹ️ (Non-blocking, requires POD Lead decision)
The design implements UI behaviour **not covered by any documented journey or requirement**.

EXTENDED items are not automatically rejected — they may represent valid UX enhancements. However, they must be:
1. Explicitly reviewed by the POD Lead
2. Either accepted (added to `features.md`), rejected (removed), or deferred

---

## Severity Classification

| Status | Gate 2 Impact | Who Resolves |
|--------|--------------|--------------|
| ALIGNED | No action | — |
| DEVIATED | Blocks Gate 2 | AI Builder (with DevCopilot), confirmed by POD Lead |
| UNCOVERED | Blocks Gate 2 | AI Builder must implement missing flow |
| EXTENDED | Does not block | POD Lead decision required within same sprint day |

---

## Scoring Thresholds

| Score | Condition | Outcome |
|-------|-----------|---------|
| 100% ALIGNED | All journeys pass | Gate 2 PASS — attestation issued |
| ≥80% ALIGNED, no DEVIATED | Minor gaps only | Conditional pass — UNCOVERED items tracked as sprint debt |
| Any DEVIATED | One or more contradictions | Gate 2 BLOCKED — mandatory revision before build continues |
| >20% UNCOVERED | Major coverage gap | Gate 2 BLOCKED — design scope review required |

---

## Revision Request Format
Every DEVIATED or UNCOVERED finding must generate a revision request in this format:

```
### Revision #[N] — [Journey ID] [Status]
**Requirement reference:** [openspec.yaml requirement ID]
**Intent violated:** "[exact quote from ui-ux.md]"
**Observed:** [what the design currently does]
**Required change:** [precise, implementable change instruction]
**Acceptance condition:** [how ExperienceStudio will verify the fix]
```
