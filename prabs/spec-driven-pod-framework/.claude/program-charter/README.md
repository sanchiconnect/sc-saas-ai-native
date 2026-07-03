# program-charter

Guides the user through a structured elicitation session to capture all dimensions of a software program, then generates a canonical `specs/program.md` and scaffolds the standard project folder layout. This is the mandatory first step in the program lifecycle — no feature briefs, sprint plans, or architecture decisions should precede it.

---

## When to Use

Trigger when initializing a new program, creating a program charter, or when a user uploads an existing charter and asks to adapt or improve it.

---

## Inputs

| Input | Required |
|---|---|
| User elicitation responses | Mandatory |
| Existing charter document (if adapting) | Optional |
| `transcripts/meeting_transcript.txt` | Optional |

## Outputs

- `specs/program.md` — fully populated program charter
- `specs/knowledge.md` — placeholder stub
- `specs/design.md` — placeholder stub
- `specs/ui-ux.md` — placeholder stub
- `specs/database.md` — placeholder stub
- `specs/api.md` — placeholder stub
- `CLAUDE.md` — placeholder stub
- Standard folder structure (`src/`, `tests/`, `.claude/program-charter/`)

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| — (first skill in the framework) | All other Phase 01 skills |
