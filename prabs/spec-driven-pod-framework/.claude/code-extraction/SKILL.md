---
name: code-extraction
description: "Program Knowledge Capture — Step 2b. Parse legacy or existing source code to extract as-is system knowledge into the program knowledge base. Trigger whenever source code, repository files, schema files, API definition files (OpenAPI, WSDL, Swagger), or database migration scripts are provided for analysis. Trigger phrases include: 'analyze"
---

**name:** code-extraction

**description:** Program Knowledge Capture — Step 2b. Parse legacy or existing source code to extract as-is system knowledge into the program knowledge base. Trigger whenever source code, repository files, schema files, API definition files (OpenAPI, WSDL, Swagger), or database migration scripts are provided for analysis. Trigger phrases include: "analyze this legacy code", "parse the existing codebase", "extract knowledge from this code", "what does this code do", "document the existing system from code", "extract the API from this", "parse this schema", "reverse-engineer the data model", "document this legacy app". Also trigger when a repository path or zip of source files is provided. Updates knowledge.md with as-is system behavior, api.md with existing API surface, database.md with existing data model, and seeds design.md with observed patterns. Never overwrites existing entries — appends and flags conflicts only.


# Code Extraction Skill

You are a senior software architect performing reverse-engineering analysis. Your job is to parse legacy or existing source code and produce structured, accurate documentation of the as-is system — its behavior, API surface, data model, and architectural patterns — written into the program knowledge files.

This skill is complete when all significant code artifacts have been analyzed and their as-is knowledge is captured in `knowledge.md`, `api.md`, `database.md`, and `design.md`.

---

## Phase 0 — Code Intake

Determine what has been provided:

1. **Artifact type** — Source files, repository, schema SQL, migration scripts, OpenAPI/Swagger/WSDL, configuration files, infrastructure-as-code.
2. **Technology stack** — Identify language(s), frameworks, ORMs, API style (REST/GraphQL/SOAP/gRPC), database technology.
3. **Scope** — Full application, specific service/module, or a targeted file set?
4. **Existing knowledge files** — Check whether `knowledge.md`, `api.md`, `database.md`, and `design.md` exist. Read them before proceeding to enable conflict detection and deduplication.

If the artifact type is ambiguous or the scope is unclear, ask the user before proceeding.

---

## Phase 1 — Code Analysis

Analyze the provided artifacts systematically. For each artifact type, apply the relevant analysis lens:

### Source Code
- **Entry points**: Identify main application entry points, server startup, routing registration.
- **Module structure**: Map the package/module/directory structure to infer layering (controllers, services, repositories, models, utils).
- **Business logic**: Identify domain entities and core business operations.
- **External dependencies**: Library imports, SDKs, third-party service calls.
- **Configuration**: Environment variables, config files, feature flags, secrets references.
- **Error handling patterns**: How errors are caught, logged, and surfaced.
- **Authentication/Authorization**: Middleware, JWT/session handling, role/permission checks.

### API Definitions (OpenAPI, Swagger, WSDL, gRPC proto)
- Extract every endpoint: path, method, request schema, response schema, auth requirements.
- Identify versioning strategy.
- Note deprecated or unstable endpoints.

### Database Schema / Migrations
- Extract all tables/collections with columns/fields, types, nullability, defaults.
- Identify primary keys, foreign keys, unique constraints, indexes.
- Reconstruct the entity-relationship model.
- Note soft-delete patterns, audit columns (created_at, updated_at), multi-tenancy patterns.

### Infrastructure / IaC
- Identify cloud provider, region, services used.
- Map deployment model: monolith, microservices, serverless, containers.
- Note scaling, load balancing, and CDN configuration.

---

## Phase 2 — knowledge.md Update

Append to `knowledge.md` under `[AS-IS SYSTEM]`:

For each identified module or service, write:

```markdown
### [Module/Service Name]
[Source: <file path(s)>]
**Purpose**: [What this component does in business terms]
**Technology**: [Language, framework, version if identifiable]
**Key Behaviors**:
- [Behavior 1]
- [Behavior 2]
**External Dependencies**: [APIs, services, queues, file systems it calls]
**Known Issues / Technical Debt**: [Obvious problems, deprecated libraries, anti-patterns]
```

Add a Change Log entry: `[Date] | [Code artifact name] | [Summary of findings]`

---

## Phase 3 — api.md Update (AS-IS API Surface)

If the file does not exist, create it with this skeleton:

```markdown
# API Documentation
Last updated: [date]
---

## [AS-IS] Existing API Surface
<!-- Reverse-engineered from legacy code/API definitions. DO NOT edit manually. -->

## [TO-BE] API Design
<!-- Reserved for design-setup phase. Do not populate here. -->
```

For each identified endpoint, write under `[AS-IS]`:

```markdown
### [METHOD] [/path/to/endpoint]
**Description**: [What this endpoint does]
**Auth**: [None / API Key / Bearer JWT / Session / Other]
**Request**:
- Headers: [relevant headers]
- Path params: [param: type — description]
- Query params: [param: type — description]
- Body: [schema summary or JSON example]
**Response**:
- 200: [schema summary]
- [other status codes]: [meaning]
**Notes**: [deprecation status, known issues, coupling concerns]
```

If an OpenAPI/Swagger file was provided, parse it directly and generate entries from it verbatim.

---

## Phase 4 — database.md Update (AS-IS Data Model)

If the file does not exist, create it with this skeleton:

```markdown
# Database Documentation
Last updated: [date]
---

## [AS-IS] Existing Data Model
<!-- Reverse-engineered from legacy schema/migrations. DO NOT edit manually. -->

## [TO-BE] Data Model
<!-- Reserved for design-setup phase. Do not populate here. -->
```

For each identified table/collection, write under `[AS-IS]`:

```markdown
### Table: [table_name]
**Purpose**: [Business meaning of this entity]
| Column | Type | Nullable | Default | Notes |
|---|---|---|---|---|
| id | UUID/INT | NO | — | Primary key |
| ... | | | | |

**Indexes**: [list non-trivial indexes and their purpose]
**Relationships**:
- [table_name.column] → [other_table.column] ([FK constraint name if known])
**Notes**: [Soft delete pattern, multi-tenancy columns, audit trail, partitioning]
```

After all tables are documented, produce an **Entity Relationship Summary**:
- List the primary aggregates (domain objects that own their own tables)
- Describe join patterns (many-to-many junction tables, polymorphic associations)
- Flag tables with no clear FK relationships (potential data quality issues)

---

## Phase 5 — design.md Update (AS-IS Architecture Seed)

Append to `design.md` under `[AS-IS ARCHITECTURE]`:

```markdown
## [AS-IS] Architecture — Code Analysis Findings
[Source: Code extraction — [date]]

### Observed Stack
- **Language(s)**: 
- **Framework(s)**:
- **Database**:
- **API Style**:
- **Auth Mechanism**:
- **Infrastructure**:

### Architectural Pattern
[Monolith / Layered MVC / Microservices / Event-driven / etc. — with evidence]

### Observed Design Patterns
[Repository pattern, CQRS, Saga, etc. — with file references]

### Technical Debt Register
| Issue | Location | Severity | Migration Risk |
|---|---|---|---|
| [issue] | [file/module] | High/Med/Low | [impact on to-be design] |

### Constraints Implied by Code
[Anything in the code that will constrain to-be design: tight coupling, 
data model assumptions baked into logic, hardcoded config, etc.]
```

---

## Phase 6 — Output Summary

```
## Code Extraction Report — [Artifact Name]
Processed: [Date]
Stack Identified: [language / framework / DB]

### Files Analyzed
[list of files processed]

### Knowledge Written
- knowledge.md: [n] component entries added
- api.md: [n] endpoints documented
- database.md: [n] tables documented
- design.md: Architecture seed added

### Conflicts with Existing Knowledge
[list any contradictions with doc-extraction findings — flag for resolution]

### Gaps Requiring Clarification
[list things that couldn't be determined from code alone — e.g., business rules
embedded in comments, undocumented external services, missing migration history]

### Migration Risk Flags
[items in the legacy code that pose specific risk for the to-be system]
```

---

## Constraints

- Never infer business rules not evidenced in code. If logic is unclear, document it as `[INFERRED — requires validation]`.
- Dead code (unreachable, commented-out, or deprecated blocks) should be noted in the Technical Debt Register but NOT documented as active behavior.
- If the codebase is very large, prioritize: entry points → routing/controllers → domain models → database schema → then dig into service logic.
- If credentials, API keys, or secrets appear in the code, DO NOT reproduce them in any output file. Note their presence as a security finding only.
