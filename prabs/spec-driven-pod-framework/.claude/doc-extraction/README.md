# doc-extraction

Parses customer-provided documents (requirements specs, BRDs, architecture docs, compliance docs, process documents) and extracts structured knowledge into the program knowledge base. Flags conflicts with existing knowledge rather than silently overwriting.

---

## When to Use

Trigger whenever a user uploads or references a customer document. Handles PDF, Word, and mixed artifact types.

---

## Inputs

| Input | Required |
|---|---|
| Customer-provided document(s) | Mandatory |
| `specs/knowledge.md` | Optional (read for conflict detection) |
| `specs/design.md` | Optional (read for conflict detection) |
| `specs/ui-ux.md` | Optional (read for conflict detection) |
| `specs/database.md` | Optional (read for conflict detection) |
| `specs/api.md` | Optional (read for conflict detection) |

## Outputs

- `specs/knowledge.md` — business context, rules, workflows, constraints, open items
- `specs/design.md` — AS-IS architecture and technical findings
- `specs/ui-ux.md` — AS-IS UI/UX findings
- `specs/database.md` — AS-IS data model findings
- `specs/api.md` — AS-IS API findings
- Conflict report (inline)

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| Program charter initialization | knowledge-review |
| | design-setup |
