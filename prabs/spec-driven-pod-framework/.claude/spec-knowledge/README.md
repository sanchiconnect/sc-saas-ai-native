# spec-knowledge

Creates, reviews, and updates the domain knowledge specification (`specs/knowledge.md`). The shared domain vocabulary for the entire program — all pods reference it when building features. Captures business rules, domain entities, workflows, terminology, and constraints.

---

## When to Use

Activate when updating knowledge, capturing business rules, documenting domain concepts, or describing business logic, domain rules, entities, workflows, or constraints that should be captured formally.

---

## Inputs

| Input | Required |
|---|---|
| `specs/program.md` | Mandatory |
| `specs/knowledge.md` | Optional (Review Mode) |

## Outputs

- `specs/knowledge.md` — complete domain knowledge layer with entities, business rules, state machines, workflows, constraints, compliance requirements, and glossary

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| program-charter | spec-design |
| | spec-database |
| | spec-api |
| | knowledge-review |
