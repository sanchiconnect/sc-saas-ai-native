---
name: spec-api
description: "Create, review, and update the backend API specification (specs/api.md) for the AI pod. Activate whenever the user says 'update API spec', 'define endpoints', 'add an API route', 'document the REST API', 'review API design', 'generate FastAPI routes', 'update specs/api.md', 'define request and response schemas', 'add authentication to the"
---

**name:** spec-api

**description:** Create, review, and update the backend API specification (specs/api.md) for the AI pod. Activate whenever the user says "update API spec", "define endpoints", "add an API route", "document the REST API", "review API design", "generate FastAPI routes", "update specs/api.md", "define request and response schemas", "add authentication to the API", or makes any decision about API endpoints, HTTP methods, request/response payloads, authentication, error formats, versioning, or rate limiting. Produces a FastAPI-ready specification with full endpoint definitions, Pydantic schemas, auth strategy, and error contract. Always reads specs/program.md, specs/knowledge.md, and specs/database.md first to derive endpoints from domain entities.


# Spec: API

## Purpose

Define and maintain the **complete backend API specification** for the AI pod — all REST endpoints, request/response schemas, authentication strategy, error contract, and FastAPI implementation patterns. This spec drives code generation: the backend pod implements directly from this spec; the frontend pod consumes it.

`specs/api.md` is consumed by:
- Backend pod coding sessions (FastAPI route implementation, Pydantic schemas)
- Frontend pod coding sessions (API client code, type definitions)
- `spec-database` (cross-reference: endpoint data needs drive query design)
- Feature brief sessions (API contract for acceptance criteria)

---

## Pre-flight

Before eliciting or editing:
1. Read `specs/program.md` — extract system domains, security NFRs, compliance requirements
2. Read `specs/knowledge.md` — extract entities, workflows, business rules → these become endpoints
3. Read `specs/database.md` — extract table structure → drives request/response shapes
4. Read `specs/design.md` — extract auth mechanism, API style, framework versions
5. Check if `specs/api.md` exists — if yes, **Review Mode**; if no, **Initialize Mode**

---

## Initialize Mode

Elicit in four groups:

### Group 1 — API Foundation
- Base URL prefix: `/api/v1` or `/v1`? Versioning strategy (URL, header)?
- Framework: FastAPI (default), Django REST Framework, or other?
- Authentication: JWT Bearer / API Key / OAuth2 / Session? Who issues tokens?
- CORS: Which origins? (dev: localhost:3000, prod: app domain)

### Group 2 — Endpoint Design (derive from knowledge.md)
For each entity/workflow in `knowledge.md`:
- What CRUD operations are needed? (not every entity needs all four)
- Who can perform each operation? (auth vs public; role-based?)
- What are the query/filter parameters for list endpoints?
- What triggers state transitions? (dedicated action endpoints vs PATCH status)
- Are there any bulk operations needed?

### Group 3 — Request/Response Conventions
- Pagination: cursor-based or offset/limit? Default page size?
- Date format: ISO 8601 (`2026-04-21T12:00:00Z`)?
- Enum representation: strings or integers in JSON?
- Null handling: omit null fields or include them?
- ID format in URLs: UUID strings?

### Group 4 — Error & Non-functional Contract
- Standard error response shape (code, message, details)?
- HTTP status code conventions (422 for validation, 409 for conflicts, etc.)?
- Rate limiting: per-user, per-IP, per-endpoint? Limits?
- Request size limits?
- Timeout policy?

---

## Review Mode

1. Load `specs/api.md`, `specs/knowledge.md`, `specs/database.md`
2. Check: every entity in `database.md` has corresponding endpoints (unless intentionally excluded)
3. Check: business rule changes in `knowledge.md` reflected in endpoint guards / validations
4. Ask: "Any new endpoints, schema changes, or auth changes since last update?"
5. Make surgical edits; append `## Changelog` entry
6. Flag breaking changes (removed fields, changed types, status code changes)

---

## Output: specs/api.md

See `references/api-template.md` for the full canonical structure.

### Section Summary
| Section | Content |
|---------|---------|
| API Foundation | Base URL, versioning, auth strategy, CORS, global headers |
| Authentication | Token format, issuance, validation, refresh strategy |
| Error Contract | Standard error schema, HTTP status code map |
| Endpoints | Full definition per endpoint: method, path, auth, request, response, errors |
| Pydantic Schemas | Request and response model definitions (FastAPI-ready) |
| Rate Limiting | Limits per endpoint or global |
| Changelog | Date-stamped change history |

---

## Endpoint Definition Format

Each endpoint is documented as:

```
### {HTTP METHOD} {/path}
**Description:** {What this does}
**Auth:** {Required / Public} — {Bearer JWT / API Key / None}
**Roles:** {Any role restriction}

**Path Parameters:**
- `{param}` — {type} — {description}

**Query Parameters:**
- `{param}` — {type} — {optional/required} — {description, default}

**Request Body:** `{SchemaName}`
**Response:** `200 {SchemaName}` / `201 {SchemaName}`
**Errors:** `400` | `401` | `404` | `422` | `409`

**Business Rules Applied:** BR-{N}, BR-{N}
**Notes:** {Implementation guidance, edge cases}
```

---

## FastAPI Implementation Pattern

All endpoints follow this structure:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.{domain} import {RequestSchema}, {ResponseSchema}
from app.services.{domain} import {DomainService}
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/{resource}", tags=["{domain}"])

@router.post("/", response_model={ResponseSchema}, status_code=status.HTTP_201_CREATED)
async def create_{resource}(
    payload: {RequestSchema},
    current_user = Depends(get_current_user),
    service: {DomainService} = Depends()
) -> {ResponseSchema}:
    """Create a new {resource}."""
    return await service.create(payload, current_user)
```

---

## Execution Steps

1. Read all prerequisite specs
2. Detect Initialize vs Review mode
3. Derive endpoints from domain entities and workflows; confirm scope with user
4. Define auth, error contract, and pagination conventions first (shared across all endpoints)
5. Write endpoint definitions + Pydantic schemas
6. Confirm with user; write or update `specs/api.md`
7. Flag if `spec-database` needs additional indexes for new query patterns

---

## Reference Files
- `references/api-template.md` — Canonical template
- `sample_output/api.md` — Example for mobile checkout program
