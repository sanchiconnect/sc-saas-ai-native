# Chunking Strategy — KnowledgeMesh

## Design Principles
1. **Atomic coherence** — each chunk must be independently useful without surrounding context
2. **Retrievability** — chunk boundaries must align with logical document units (endpoint, table, ADR), not arbitrary token counts
3. **Traceability** — every chunk must carry its `source_file + section_heading` so downstream agents can cite provenance

---

## File-Type Chunking Rules

### `specs/api.md`
- **Unit:** One chunk per HTTP endpoint definition
- **Must include:** Method, path, request schema, response schema, error codes
- **Chunk ID format:** `api-[METHOD]-[path-slug]` (e.g. `api-POST-users`, `api-GET-products-id`)
- **Max tokens per chunk:** 400

### `specs/database.md`
- **Unit:** One chunk per table or entity definition
- **Must include:** Table name, all column definitions with types, foreign keys, indexes
- **Chunk ID format:** `db-[table_name]` (e.g. `db-users`, `db-order_items`)
- **Max tokens per chunk:** 350

### `specs/design.md`
- **Unit:** One chunk per architectural layer or major section heading
- **Must include:** Layer description, technology choices, key patterns, inter-layer contracts
- **Chunk ID format:** `design-[section-slug]` (e.g. `design-frontend-state`, `design-api-layer`)
- **Max tokens per chunk:** 500

### `artifacts/openspec.yaml`
- **Unit:** One chunk per requirement block (single `id:` entry with all sub-fields)
- **Must include:** Requirement ID, description, acceptance criteria, NFR targets
- **Chunk ID format:** `spec-[requirement_id]` (e.g. `spec-REQ-API-003`)
- **Max tokens per chunk:** 300

### `specs/knowledge.md`
- **Unit:** One chunk per system domain section (Authentication, Payments, Notifications, etc.)
- **Must include:** Domain description, existing patterns, integration points, known constraints
- **Chunk ID format:** `know-[domain-slug]` (e.g. `know-auth`, `know-notifications`)
- **Max tokens per chunk:** 500

### `artifacts/decision-ledger.md`
- **Unit:** One chunk per ADR entry
- **Must include:** Decision title, context, decision made, consequences, status (accepted/superseded)
- **Chunk ID format:** `adr-[sequence]` (e.g. `adr-001`, `adr-015`)
- **Max tokens per chunk:** 300

### `artifacts/task-breakdown.yaml`
- **Unit:** One chunk per epic or task group (not per individual task)
- **Must include:** Epic ID, task IDs in group, requirement IDs, assigned builder
- **Chunk ID format:** `task-[epic_id]`
- **Max tokens per chunk:** 250

### `artifacts/ai-manifest.json`
- **Unit:** One chunk per component entry
- **Must include:** Component name, file path, spec IDs implemented, last modified sprint
- **Chunk ID format:** `manifest-[component-slug]`
- **Max tokens per chunk:** 200

---

## Version Hashing
Each chunk receives a `version_hash` computed as:
```
SHA256(source_file_path + section_heading + chunk_content)
```
On each retrieval request, KnowledgeMesh recomputes the hash for the source section and compares to the stored hash. If they differ, the chunk is marked `STALE`.

---

## Relevance Scoring Weights
When scoring chunks against a query, apply these weights:
- `requirement_id` match (exact): +0.40
- `domain_keyword` match (in chunk metadata): +0.25
- `section_heading` similarity to query: +0.20
- `source_file` type relevance (code gen query → api.md + database.md ranked higher): +0.15

Minimum relevance threshold for serving: **0.50**. Chunks below this threshold are not served even if they are the best available — instead, KnowledgeMesh reports "low confidence" for the query domain.
