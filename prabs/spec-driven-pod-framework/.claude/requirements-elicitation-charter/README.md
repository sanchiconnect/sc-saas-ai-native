# requirements-elicitation-charter

Generates a disciplined, domain-organized question pack from a program charter that a Program Lead or Pod Lead can use in early customer meetings to close knowledge gaps and validate assumptions. Always use before the first substantive customer meeting.

---

## When to Use

Trigger when a Program Lead or Pod Lead needs to prepare structured discovery questions for customer meetings, based on a program charter, SOW, or initial brief.

---

## Inputs

| Input | Required |
|---|---|
| `specs/program.md` | Mandatory |
| Prior question pack outputs (if present) | Optional |

## Outputs

- `questions-[YYYY-MM-DD].md` — domain-organized question pack with gap references, intent notes, and charter ambiguity flags

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| program-charter | Customer kickoff / discovery meeting |
| | doc-extraction, meeting-extraction |
