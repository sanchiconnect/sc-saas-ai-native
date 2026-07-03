---
name: spec-knowledge
description: "Create, review, and update the domain knowledge specification (specs/knowledge.md) for a program. Activate whenever the user says 'update knowledge', 'review knowledge spec', 'add domain knowledge', 'capture business rules', 'document domain concepts', 'update specs/knowledge.md', or describes business logic, domain rules, entities, workf"
---

**name:** spec-knowledge

**description:** Create, review, and update the domain knowledge specification (specs/knowledge.md) for a program. Activate whenever the user says "update knowledge", "review knowledge spec", "add domain knowledge", "capture business rules", "document domain concepts", "update specs/knowledge.md", or describes business logic, domain rules, entities, workflows, or constraints that should be captured formally. Always reads specs/program.md first for context. This spec is the shared domain vocabulary for the entire program — all pods reference it when building features. Use this skill proactively whenever domain understanding appears to be missing or incomplete across any spec file.


# Spec: Knowledge

## Purpose

Capture and maintain the **domain knowledge layer** of the program — the business rules, domain entities, workflows, terminology, and constraints that all pods must understand to build correctly. This is the shared vocabulary layer; without it, pods make conflicting assumptions.

`specs/knowledge.md` is consumed by:
- All AI pod sessions (backend, frontend, data)
- `spec-design`, `spec-database`, `spec-api` skills when making domain-informed decisions
- Feature brief sessions for acceptance criteria

---

## Pre-flight

Before eliciting or editing, always:
1. Read `specs/program.md` — extract domain, users, system domains, and scope
2. Check if `specs/knowledge.md` already exists — if yes, load it and enter **Review Mode**; if no, enter **Initialize Mode**

---

## Initialize Mode (file does not exist)

Run elicitation in three groups:

### Group 1 — Domain Entities
- What are the core business objects? (e.g., Order, Customer, Product, Payment)
- What are the key attributes of each?
- What are the relationships between entities? (one-to-many, ownership, dependency)

### Group 2 — Business Rules & Constraints
- What rules govern state transitions? (e.g., "An order cannot be confirmed without payment authorization")
- What are the validation rules? (field-level, cross-entity)
- What are the compliance or regulatory constraints? (PCI, GDPR, HIPAA, etc.)
- What are the edge cases the system must handle explicitly?

### Group 3 — Glossary & Workflows
- Are there domain-specific terms that need a canonical definition?
- What are the key business workflows? (step-by-step, with actors and triggers)
- Are there any legacy system concepts or naming conventions the team must know?

After elicitation, confirm summary, then generate `specs/knowledge.md`.

---

## Review Mode (file exists)

Present a structured review agenda:
1. **Scan for gaps** — Read current file; identify sections that are thin, missing, or outdated
2. **Surface changes** — Ask: "Has anything changed in the domain since this was last updated?"
3. **Targeted updates** — Make surgical edits; never rewrite sections that are still accurate
4. **Version note** — Append a `## Changelog` entry with date and summary of changes

---

## Output: specs/knowledge.md

See `references/knowledge-template.md` for the full canonical structure.

### Section Summary
| Section | Content |
|---------|---------|
| Domain Overview | 2–3 sentence summary of the business domain |
| Core Entities | Entity name, description, key attributes, relationships |
| Business Rules | Numbered rules, grouped by entity or workflow |
| State Machines | State transitions with triggers and guards |
| Workflows | Step-by-step flows with actors, triggers, outcomes |
| Constraints & Compliance | Regulatory, contractual, data residency rules |
| Glossary | Canonical definitions for domain terms |
| Changelog | Date-stamped history of changes |

---

## Execution Steps

1. Read `specs/program.md`
2. Detect Initialize vs Review mode
3. Run elicitation or gap review
4. Confirm changes with user
5. Write or update `specs/knowledge.md`
6. Report what changed and flag any downstream specs that may need updating (design, database, api)

---

## Reference Files
- `references/knowledge-template.md` — Canonical template
- `sample_output/knowledge.md` — Example for mobile checkout program
