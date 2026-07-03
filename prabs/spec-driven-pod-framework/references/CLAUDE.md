# CLAUDE.md — AI Collaboration Guide

## Program
See `specs/program.md` for the authoritative program definition.
All AI-assisted work in this repo must be consistent with that spec.

## Specification Files
All specs live in `specs/`. Read the relevant spec before working in its domain:
- `specs/program.md`   — Program charter, goals, stakeholders, timeline
- `specs/knowledge.md` — Domain entities, business rules, state machines, glossary
- `specs/design.md`    — Tech stack, frameworks, libraries, infrastructure, coding standards
- `specs/ui-ux.md`     — Design tokens, components, motion, accessibility (shared across features)
- `specs/database.md`  — Schema, tables/collections, indexes, migrations
- `specs/api.md`       — REST endpoints, request/response schemas, auth contract

## Key Conventions
- Source code lives in `src/`
- Tests live in `tests/` and mirror the `src/` structure
- All AI pod sessions must read the relevant spec(s) before generating or modifying code
- Spec files are the single source of truth — code must conform to specs, not the other way around
- If a spec needs updating, run the corresponding spec skill before changing code

## Skills
Skills are in `.claude/<skill-name>/SKILL.md`.
| Skill | Purpose |
|-------|---------|
| `program-charter` | Initialize or update the program charter |
| `spec-knowledge`  | Review/update domain knowledge spec |
| `spec-design`     | Review/update technical design spec |
| `spec-uiux`       | Review/update UI/UX spec |
| `spec-database`   | Review/update database schema spec |
| `spec-api`        | Review/update API endpoint spec |
