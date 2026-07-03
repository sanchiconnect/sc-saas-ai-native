# spec-generation

Synthesizes all program knowledge into a complete, hierarchical specification — Epics → Stories → Tasks — and produces two delivery-ready output files: `specs/spec.md` for epics and stories, and `specs/tasks.md` for the full task inventory. Every task is scoped to complete in 3 business days or fewer.

---

## When to Use

Trigger when a Pod Lead or Program Lead wants to generate the spec, create the work breakdown, produce sprint-ready tasks, or move from design into delivery planning. Prerequisite: design-setup should be complete.

---

## Inputs

| Input | Required |
|---|---|
| `specs/knowledge.md` | Mandatory |
| `specs/features.md` | Mandatory |
| `specs/design.md` (TO-BE sections) | Mandatory |
| `specs/ui-ux.md` (TO-BE sections) | Mandatory |
| `specs/api.md` (TO-BE sections) | Optional |
| `specs/database.md` (TO-BE sections) | Optional |
| `specs/impl.md` | Optional |

## Outputs

- `specs/spec.md` — complete program specification: epics, stories, acceptance criteria, dependencies
- `specs/tasks.md` — full task inventory with effort estimates, statuses, and definitions of done

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| design-setup | SkillFlow (Phase 01 artifact) |
| knowledge-review | Sprint planning |
