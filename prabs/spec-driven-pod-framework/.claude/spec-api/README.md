# spec-api

Creates, reviews, and updates the backend API specification (`specs/api.md`). Produces a FastAPI-ready specification with full endpoint definitions, Pydantic schemas, auth strategy, and error contract. Derives endpoints from domain entities in `knowledge.md`.

---

## When to Use

Activate when defining endpoints, adding API routes, documenting the REST API, reviewing API design, or making any decision about API endpoints, HTTP methods, request/response payloads, authentication, error formats, versioning, or rate limiting.

---

## Inputs

| Input | Required |
|---|---|
| `specs/program.md` | Mandatory |
| `specs/knowledge.md` | Mandatory |
| `specs/database.md` | Mandatory |
| `specs/design.md` | Mandatory |
| `specs/api.md` | Optional (Review Mode) |

## Outputs

- `specs/api.md` — complete API specification with endpoints, Pydantic schemas, auth contract, error contract, and rate limiting rules

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| spec-database | spec-generation |
| spec-design | design-setup |
