# knowledge-review

Internally validates the accumulated knowledge base against completeness criteria and produces a corrected, annotated, signed-off version ready for the design phase. A mandatory checkpoint before design-setup begins.

---

## When to Use

Trigger when a user wants to review, validate, or sign off the knowledge base. Also trigger proactively if the user asks to start design-setup and knowledge-review has not yet been completed.

---

## Inputs

| Input | Required |
|---|---|
| `specs/knowledge.md` | Mandatory |
| `specs/features.md` | Mandatory |

## Outputs

- `specs/knowledge.md` — validated with certainty annotations, gap resolutions, and `STATUS: REVIEWED ✓` stamp
- `specs/features.md` — validated with priority confirmations and reclassifications

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| doc-extraction, code-extraction, meeting-extraction | design-setup (mandatory prerequisite) |
