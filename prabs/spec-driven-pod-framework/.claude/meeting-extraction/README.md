# meeting-extraction

Processes meeting transcripts or call notes from customer sessions to extract structured knowledge. Produces a structured meeting brief for Pod/Program Lead consumption and routes extracted content to the correct knowledge file.

---

## When to Use

Trigger whenever a transcript, call recording summary, meeting notes, or any record of a customer conversation is provided.

---

## Inputs

| Input | Required |
|---|---|
| Meeting transcript / call notes / session record | Mandatory |
| `specs/knowledge.md` | Optional (read for conflict detection) |
| `specs/features.md` | Optional (read for conflict detection) |
| `specs/design.md` | Optional (read for conflict detection) |

## Outputs

- Meeting Brief (inline) — executive summary, decisions, open items, stakeholder intelligence
- `specs/knowledge.md` — business context, rules, workflows, constraints, open items
- `specs/features.md` — to-be feature requirements
- `specs/design.md` — to-be technology and architecture decisions

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| Customer meeting occurs | knowledge-review |
| Program charter initialization | design-setup |
