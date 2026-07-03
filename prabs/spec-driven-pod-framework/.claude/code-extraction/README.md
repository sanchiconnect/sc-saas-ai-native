# code-extraction

Parses legacy or existing source code, schema files, API definitions, and infrastructure artifacts to extract as-is system knowledge into the program knowledge base. Never overwrites existing entries — appends and flags conflicts only.

---

## When to Use

Trigger whenever source code, repository files, schema files, API definition files (OpenAPI, WSDL, Swagger), or database migration scripts are provided for analysis.

---

## Inputs

| Input | Required |
|---|---|
| Source code files / repository | Mandatory |
| `specs/knowledge.md` | Optional (read for conflict detection) |
| `specs/api.md` | Optional (read for conflict detection) |
| `specs/database.md` | Optional (read for conflict detection) |
| `specs/design.md` | Optional (read for conflict detection) |

## Outputs

- `specs/knowledge.md` — as-is system components, behaviors, dependencies
- `specs/api.md` — as-is API surface
- `specs/database.md` — as-is data model
- `specs/design.md` — as-is architecture seed

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| Program charter initialization | knowledge-review |
| | design-setup |
