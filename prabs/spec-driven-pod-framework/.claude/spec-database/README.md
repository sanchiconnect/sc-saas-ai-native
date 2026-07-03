# spec-database

Creates, reviews, and updates the database specification (`specs/database.md`). Supports both relational databases (PostgreSQL, MySQL) with full schema definitions and document databases (MongoDB, DynamoDB, Firestore) with JSON schema definitions. Derives entities and business rules from `knowledge.md`.

---

## When to Use

Activate when defining the schema, adding tables, updating database design, modeling data, defining indexes, or making any decision about tables, columns, data types, relationships, constraints, migrations, or database technology.

---

## Inputs

| Input | Required |
|---|---|
| `specs/program.md` | Mandatory |
| `specs/knowledge.md` | Mandatory |
| `specs/design.md` | Optional |
| `specs/database.md` | Optional (Review Mode) |

## Outputs

- `specs/database.md` — complete database schema with tables/collections, indexes, constraints, relationships, migration strategy, and compliance fields

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| spec-knowledge | spec-api |
| spec-design | spec-generation |
