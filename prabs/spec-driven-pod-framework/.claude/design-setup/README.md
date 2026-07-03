# design-setup

Conducts a structured interactive design session to define the to-be technical architecture and populate all design documents. Writes authoritative TO-BE content to `design.md`, `uiux.md`, `api.md`, `database.md`, and `impl.md`. AS-IS sections are preserved and never overwritten.

---

## When to Use

Trigger when a Pod Lead or Program Lead wants to define or finalize the technical design for the new system. Prerequisite: `knowledge-review` should be completed first.

---

## Inputs

| Input | Required |
|---|---|
| `specs/knowledge.md` | Mandatory |
| `specs/features.md` | Mandatory |
| `specs/design.md` | Mandatory |
| `specs/ui-ux.md` | Mandatory |
| `specs/api.md` | Optional |
| `specs/database.md` | Optional |
| `specs/impl.md` | Optional |

## Outputs

- `specs/design.md` — TO-BE system architecture and stack decisions
- `specs/ui-ux.md` — TO-BE UI/UX design direction
- `specs/api.md` — TO-BE API design
- `specs/database.md` — TO-BE data model
- `specs/impl.md` — technology stack summary, standards, CI/CD, pending decisions

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| knowledge-review | spec-generation |
