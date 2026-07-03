# spec-design

Creates, reviews, and updates the technical design specification (`specs/design.md`). The authoritative technical blueprint — all AI pods must implement consistently with it. Defines the programming language, frameworks, libraries, infrastructure, architectural patterns, and tooling decisions.

---

## When to Use

Activate when updating the design spec, choosing the tech stack, defining architecture, selecting frameworks, or making any decision about programming languages, frameworks, infrastructure, tooling, or architectural patterns.

---

## Inputs

| Input | Required |
|---|---|
| `specs/program.md` | Mandatory |
| `specs/knowledge.md` | Optional |
| `specs/design.md` | Optional (Review Mode) |

## Outputs

- `specs/design.md` — complete technical blueprint with system architecture, technology stack, libraries, infrastructure, coding standards, security design, and observability strategy

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| spec-knowledge | spec-database |
| | spec-api |
| | spec-uiux |
| | spec-generation |
