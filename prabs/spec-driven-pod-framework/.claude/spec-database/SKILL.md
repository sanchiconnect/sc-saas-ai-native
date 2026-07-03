---
name: spec-database
description: "Create, review, and update the database specification (specs/database.md) for the AI pod. Activate whenever the user says 'update database spec', 'define the schema', 'add a table', 'update database design', 'model the data', 'define collections', 'add indexes', 'update specs/database.md', or makes any decision about tables, columns, data"
---

**name:** spec-database

**description:** Create, review, and update the database specification (specs/database.md) for the AI pod. Activate whenever the user says "update database spec", "define the schema", "add a table", "update database design", "model the data", "define collections", "add indexes", "update specs/database.md", or makes any decision about tables, columns, data types, relationships, indexes, constraints, migrations, or database technology choices. Supports both relational databases (PostgreSQL, MySQL) with full schema definitions and unstructured/document databases (MongoDB, DynamoDB, Firestore) with JSON schema definitions. Always reads specs/program.md and specs/knowledge.md first to derive entities and business rules.


# Spec: Database

## Purpose

Define and maintain the **complete database schema** for the AI pod — tables, columns, data types, constraints, indexes, relationships, and migration strategy. For document databases, defines collection schemas as JSON Schema or BSON structure. This spec is the authoritative source that the backend pod uses to write migrations and queries.

`specs/database.md` is consumed by:
- Backend pod coding sessions (ORM models, migration scripts)
- `spec-api` skill (response shapes, query patterns)
- Data pod sessions (analytics queries, reporting models)

---

## Pre-flight

Before eliciting or editing:
1. Read `specs/program.md` — extract system domains, compliance (PCI, GDPR), pod structure
2. Read `specs/knowledge.md` — extract core entities, attributes, relationships, and business rules
3. Read `specs/design.md` if it exists — extract database technology choice, ORM, migration tool
4. Check if `specs/database.md` exists — if yes, **Review Mode**; if no, **Initialize Mode**

---

## Initialize Mode

Elicit in three groups:

### Group 1 — Database Platform
- Relational (PostgreSQL, MySQL, SQLite) or document (MongoDB, DynamoDB, Firestore)?
- Single database or multiple (separate DBs per domain/pod)?
- Read replicas or sharding requirements?
- Cloud managed service or self-hosted?

### Group 2 — Schema Design (derive from knowledge.md entities)
For each entity in `specs/knowledge.md`:
- Confirm table/collection name (plural, snake_case for relational; camelCase collections for Mongo)
- Confirm columns/fields with types and constraints
- Foreign keys / reference fields / embedded vs referenced documents
- Soft delete required? (add `deleted_at` timestamp)
- Audit fields needed? (`created_at`, `updated_at`, `created_by`)
- Sensitive fields requiring encryption at rest?

### Group 3 — Indexes, Performance & Compliance
- Which queries will be high-frequency? (Drives index selection)
- Any full-text search requirements? (Postgres `tsvector` / MongoDB Atlas Search / Elasticsearch?)
- Data retention rules? (GDPR deletion, archival)
- PII fields — which columns require masking or encryption?
- Backup and recovery requirements?

---

## Review Mode

1. Load `specs/database.md` and `specs/knowledge.md`
2. Check: are all entities in `knowledge.md` represented in the schema?
3. Check: do business rules (BRs) have corresponding database constraints?
4. Ask: "Any new entities, fields, or index requirements since last update?"
5. Make surgical edits; add a migration note for breaking changes (column adds/removes, type changes)
6. Append `## Changelog` entry

---

## Output: specs/database.md

See `references/database-template.md` for the full canonical structure.

### Section Summary
| Section | Content |
|---------|---------|
| Platform | DB engine, hosting, version, connection config |
| Schema Overview | Entity-relationship summary (text diagram) |
| Table / Collection Definitions | Full schema per entity |
| Indexes | All non-default indexes with rationale |
| Constraints & Integrity | Foreign keys, unique constraints, check constraints |
| Migrations | Tool, naming convention, migration policy |
| Data Retention & Compliance | PII fields, retention rules, GDPR handling |
| Seed Data | Reference/lookup data required at init |
| Changelog | Date-stamped history |

---

## Relational Schema Format (per table)

```
### table_name
| Column | Type | Nullable | Default | Constraints | Description |
|--------|------|----------|---------|-------------|-------------|
| id     | UUID | NOT NULL | gen_random_uuid() | PK | |
| ...    | ...  | ...      | ...     | ...         | ... |

Indexes:
- idx_table_column ON (column) — [unique] — reason

Foreign Keys:
- column → other_table(id) ON DELETE {CASCADE | RESTRICT | SET NULL}
```

## Document Schema Format (per collection)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema",
  "title": "CollectionName",
  "type": "object",
  "required": ["_id", "field1"],
  "properties": {
    "_id": { "type": "string", "description": "ObjectId" },
    "field1": { "type": "string", "maxLength": 255 }
  }
}
```

---

## Execution Steps

1. Read prerequisite specs
2. Detect Initialize vs Review mode
3. Derive schema from `knowledge.md` entities; confirm additions or deviations with user
4. Confirm all business rules have DB-level enforcement where appropriate
5. Write or update `specs/database.md`
6. Flag if `spec-api` needs updating (new tables → new endpoints) or if ORM models in `src/` need regenerating

---

## Reference Files
- `references/database-template.md` — Canonical template
- `sample_output/database.md` — Example for mobile checkout program
