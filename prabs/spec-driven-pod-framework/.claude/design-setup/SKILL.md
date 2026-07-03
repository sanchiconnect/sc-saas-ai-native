---
name: design-setup
description: "Program Knowledge Capture — Step 4 (Design Phase). Conduct a structured interactive design session to define the to-be technical architecture and populate all design documents. Trigger whenever a Pod Lead or Program Lead wants to define or finalize the technical design for the new system. Trigger phrases include: 'set up the design', 'def"
---

**name:** design-setup

**description:** Program Knowledge Capture — Step 4 (Design Phase). Conduct a structured interactive design session to define the to-be technical architecture and populate all design documents. Trigger whenever a Pod Lead or Program Lead wants to define or finalize the technical design for the new system. Trigger phrases include: "set up the design", "define the to-be architecture", "let's do the technical design", "start the design phase", "populate the design docs", "technology design session", "design setup", "what tech stack should we use", "design the new system", "architecture decisions", "define the stack". Prerequisite: knowledge-review should be completed first — if knowledge.md does not have a REVIEWED status, warn the user before proceeding. Writes authoritative TO-BE content to design.md, uiux.md, api.md, database.md, and impl.md. AS-IS sections in all files are preserved and never overwritten.


# Design Setup Skill

You are a principal architect conducting a structured design session. Your job is to lead the Pod Lead and Program Lead through a series of targeted design decisions, validate those decisions against the known constraints and requirements in `knowledge.md`, and produce complete, accurate TO-BE content across all design files.

This skill is complete when `design.md`, `uiux.md`, `api.md`, `database.md`, and `impl.md` are populated with the agreed TO-BE design, ready to guide development.

---

## Phase 0 — Pre-Design Context Load

Before the first question is asked:

1. **Read `knowledge.md`** — Extract: business objectives, customer expectations, business rules, business workflows, constraints, technology constraints, as-is system description.
2. **Read `features.md`** — Extract all captured feature requirements, their priority signals, and any open questions. This is the primary input for scoping the to-be design.
3. **Read `design.md`** (if exists) — Note any AS-IS architecture already captured, and any TO-BE technology decisions already seeded by meeting-extraction.
4. **Read `uiux.md`** (if exists) — Note any AS-IS UI already documented.
5. **Check knowledge-review status** — If `knowledge.md` does not contain `STATUS: REVIEWED ✓`, issue a warning:

> ⚠️ `knowledge.md` has not been through knowledge-review. Proceeding without a validated knowledge base may result in design decisions that conflict with actual customer requirements. Recommend completing knowledge-review first.

Ask the user whether to proceed anyway or complete the review first.

5. **Produce a context summary** before starting questions:

```
## Design Session Context
Program: [program name from knowledge.md]
Key Objectives: [top 3 from customer expectations]
Known Constraints: [technology, compliance, timeline constraints from knowledge.md]
Existing System: [brief as-is summary]
AS-IS Stack (if known): [from design.md / code-extraction]
Pre-stated Technology Decisions: [decisions already captured in design.md TO-BE section from meetings]
Feature Count: [n MUST HAVE / n SHOULD HAVE / n NICE TO HAVE features in features.md]
Key Business Rules: [top constraints from business rules that will shape design]
```

Show this to the user and ask them to confirm it is accurate before proceeding.

---

## Phase 1 — Design Questionnaire

Conduct the design session as an interactive dialogue. Ask one domain at a time. Present options where relevant — do NOT ask open-ended questions when a bounded set of choices is appropriate.

For each domain, present the relevant AS-IS context (from `knowledge.md` or `design.md`) as grounding before asking the question.

### Domain 1: System Architecture Pattern

Context presented: Current system topology (monolith, distributed, etc.) from AS-IS findings.

Questions:
1. What is the target architectural pattern for the to-be system?
   - Monolithic (single deployable unit)
   - Modular monolith (single deploy, internal module boundaries)
   - Microservices (independently deployed services)
   - Serverless / Function-based
   - Hybrid (specify)
2. If distributed: How will services communicate? (REST, gRPC, message queue, event bus)
3. What are the scalability targets? (expected concurrent users, data volume, peak load)
4. What are the availability requirements? (SLA: 99.9%, 99.95%, 99.99%)
5. Is multi-tenancy required? If so, what isolation model? (schema-per-tenant, row-level, instance-per-tenant)

---

### Domain 2: Technology Stack

Context presented: Any mandated technologies from constraints section of `knowledge.md`.

Questions:
1. What is the backend language and primary framework?
   - Node.js (Express / NestJS / Fastify)
   - Python (FastAPI / Django / Flask)
   - Java (Spring Boot)
   - Go (Gin / Echo)
   - .NET (ASP.NET Core)
   - Other: [specify]
2. What is the frontend technology?
   - React (with which meta-framework: Next.js, Vite, CRA)
   - Vue.js
   - Angular
   - Mobile native (iOS / Android)
   - Mobile cross-platform (React Native / Flutter)
   - Server-rendered only (no SPA)
   - Other: [specify]
3. Are there existing UI component libraries or design systems to adopt or migrate to?
4. What is the target runtime environment? (Cloud provider, Kubernetes, PaaS, serverless)

---

### Domain 3: Data Architecture

Context presented: AS-IS data model from `database.md` or `knowledge.md`.

Questions:
1. What is the primary database technology?
   - PostgreSQL / MySQL / SQL Server (relational)
   - MongoDB / DynamoDB (document)
   - Redis (key-value / cache)
   - Hybrid (specify combination)
2. What ORM or data access pattern will be used?
3. Is there a migration strategy for existing data? (ETL, dual-write, big-bang cutover)
4. Are there reporting or analytics requirements that require a separate data store or warehouse?
5. What are the data retention, archival, and purge policies?
6. Are there PII or sensitive data fields requiring encryption at rest?

---

### Domain 4: API Design

Context presented: AS-IS API surface from `api.md`.

Questions:
1. What is the API style for the to-be system?
   - REST (with versioning strategy: /v1/, header, content negotiation)
   - GraphQL
   - gRPC
   - Mixed (specify)
2. What authentication mechanism will be used?
   - JWT (with which issuer: internal auth service, Auth0, Cognito, Azure AD, etc.)
   - OAuth 2.0 / OIDC
   - API key
   - Session-based
3. Will the API be public-facing (external consumers) or internal only?
4. Is an API gateway required? (Kong, AWS API Gateway, Azure APIM, etc.)
5. What are the rate limiting and throttling requirements?
6. Which existing endpoints from the AS-IS system must be preserved (backward compatibility)?

---

### Domain 5: UI/UX Design Direction

Context presented: AS-IS UI patterns from `uiux.md`.

Questions:
1. Is there an existing design system or brand guideline to follow?
2. What are the primary user personas and their device preferences? (desktop-first, mobile-first, equal)
3. What accessibility standard must be met? (WCAG 2.1 AA, WCAG 2.1 AAA, Section 508)
4. Are there specific UI frameworks or component libraries prescribed? (Material UI, Ant Design, Tailwind, custom)
5. Describe the navigation model: (sidebar, top nav, tab-based, wizard/stepped, dashboard)
6. Are there screens from the existing system that must be preserved in their current form vs. redesigned?
7. Is internationalization (i18n) and localization (l10n) required? Which locales?

---

### Domain 6: Infrastructure & Deployment

Questions:
1. Target cloud provider: (AWS / Azure / GCP / On-premise / Hybrid)
2. Containerization: (Docker + Kubernetes / Docker Compose / PaaS managed / Serverless)
3. CI/CD pipeline: (GitHub Actions / Azure DevOps / Jenkins / GitLab CI / Other)
4. Environment structure: (dev / staging / prod — any additional like QA, UAT, pre-prod?)
5. Is Infrastructure-as-Code required? (Terraform / Pulumi / CloudFormation / ARM)
6. What is the disaster recovery strategy? (RTO/RPO targets if known)
7. Are there specific regions or data residency requirements?

---

### Domain 7: Security & Compliance

Context presented: Compliance constraints from `knowledge.md`.

Questions:
1. What compliance frameworks apply? (GDPR, HIPAA, SOC 2, PCI-DSS, ISO 27001, FedRAMP, other)
2. What is the secrets management approach? (HashiCorp Vault, AWS Secrets Manager, Azure Key Vault, environment variables — NOT recommended — other)
3. Is penetration testing required before go-live?
4. What is the logging and audit trail requirement? (PII redaction in logs, immutable audit log, SIEM integration)
5. Is there a vulnerability scanning requirement in the CI pipeline?

---

### Domain 8: Cross-Cutting Concerns

Questions:
1. What is the observability stack? (metrics: Prometheus/Datadog/CloudWatch; logs: ELK/Splunk/CloudWatch; tracing: Jaeger/Zipkin/X-Ray)
2. What is the error handling and alerting strategy? (PagerDuty, OpsGenie, Slack alerts)
3. Are feature flags required? (LaunchDarkly, custom implementation, none)
4. What is the caching strategy? (Redis, CDN, in-memory, none — per layer)
5. Are background jobs required? (cron, queue-based workers — Celery, BullMQ, AWS SQS)

---

## Phase 2 — Design Validation

After all domains are answered, perform a validation pass:

1. **Constraint check**: Compare every design decision against the constraints in `knowledge.md`. Flag any decision that conflicts with a stated constraint.
2. **Compatibility check**: Compare TO-BE stack decisions against AS-IS findings. Flag migration risks.
3. **Gap check**: Identify any domain where answers were vague or deferred — these become `[DESIGN DECISION PENDING]` markers in the output files.

Present a **Design Validation Report** before writing files:

```
## Design Validation Report

✅ Decisions Confirmed: [n]
⚠️ Constraint Conflicts: [list]
⚠️ Migration Risks: [list]
⏳ Pending Decisions: [list with owner and target resolution date]
```

Ask the user to confirm they want to proceed with writing the design files.

---

## Phase 3 — File Population

Write TO-BE content to all design files. Use the following document schemas:

### design.md — TO-BE Architecture

```markdown
## [TO-BE] System Architecture
Last updated: [date] | Design session with: [Pod Lead / Program Lead]

### Architecture Pattern
[Pattern chosen] — [rationale]

### System Components
| Component | Responsibility | Technology | Deployment Unit |
|---|---|---|---|

### Scalability & Availability
- Target concurrent users: [n]
- Availability SLA: [%]
- Scaling strategy: [horizontal / vertical / auto-scaling rules]
- Multi-tenancy: [model or N/A]

### Service Communication
[If distributed: communication patterns, message formats, async vs sync]

### Non-Functional Requirements
| Requirement | Target | Measurement |
|---|---|---|
| Response time (p95) | | |
| Availability | | |
| Data durability | | |
```

### uiux.md — TO-BE UI/UX

```markdown
## [TO-BE] UI/UX Design
Last updated: [date]

### Design System
- Component library: [library + version]
- Brand guidelines: [reference or N/A]
- Design tokens: [location or TBD]

### Primary Personas & Devices
| Persona | Primary Device | Key Tasks |
|---|---|---|

### Navigation Model
[Description of navigation structure]

### Accessibility
- Standard: [WCAG 2.1 AA / other]
- Testing approach: [automated / manual / both]

### Internationalization
- i18n required: [Yes/No]
- Locales: [list]

### Key Screen Inventory (TO-BE)
| Screen | Purpose | Primary Actions | Persona |
|---|---|---|---|
```

### api.md — TO-BE API Design

```markdown
## [TO-BE] API Design
Last updated: [date]

### API Style & Versioning
- Style: [REST / GraphQL / gRPC]
- Versioning: [strategy]
- Base URL pattern: [/api/v1/...]

### Authentication & Authorization
- Mechanism: [JWT / OAuth2 / API Key]
- Token issuer: [service/provider]
- Authorization model: [RBAC / ABAC / scope-based]

### API Gateway
- Solution: [gateway name or none]
- Responsibilities: [rate limiting, auth, routing, logging]

### Rate Limiting
- Default limits: [requests per minute per client]
- Burst handling: [strategy]

### Backward Compatibility
- Preserved endpoints from AS-IS: [list]
- Deprecated endpoints: [list with sunset dates]

### Standard Response Envelope
[Define the standard JSON response shape for success and error]

### Endpoint Inventory (TO-BE)
[To be populated during Sprint 0 / detailed design — placeholder]
```

### database.md — TO-BE Data Model

```markdown
## [TO-BE] Data Model
Last updated: [date]

### Database Technology
- Primary DB: [technology + version target]
- ORM / Data Access: [library + pattern]
- Connection pooling: [strategy]

### Data Architecture Pattern
[Single DB / service-per-DB / CQRS read/write split / other]

### Migration Strategy
- Approach: [ETL / dual-write / cutover]
- Data migration tooling: [tool or TBD]
- Rollback plan: [strategy]

### Data Retention & Compliance
- PII fields requiring encryption: [list or N/A]
- Retention policy: [duration by data category]
- Audit log: [approach]

### Entity Model (TO-BE)
[Core domain entities, their relationships, and rationale for changes from AS-IS]
[To be fully elaborated during Sprint 0 detailed design]
```

### impl.md — Implementation Guidance

```markdown
# Implementation Guide
Last updated: [date]
Status: [DRAFT — to be finalized in Sprint 0]

## Technology Stack Summary
| Layer | Technology | Version Target | Notes |
|---|---|---|---|
| Backend | | | |
| Frontend | | | |
| Database | | | |
| Cache | | | |
| Message Queue | | | |
| Infrastructure | | | |
| CI/CD | | | |
| Observability | | | |

## Development Standards
[Coding conventions, linting rules, testing requirements — TBD in Sprint 0]

## Environment Configuration
| Environment | Purpose | Deployment Target |
|---|---|---|
| dev | Local development | [local / shared dev cluster] |
| staging | Integration testing | |
| prod | Production | |

## Security Standards
- Secrets management: [tool]
- Vulnerability scanning: [tool + pipeline stage]
- Dependency audit: [tool + frequency]

## CI/CD Pipeline
- Platform: [CI platform]
- Pipeline stages: [build → lint → test → scan → deploy]
- Deployment strategy: [blue-green / rolling / canary]

## Observability Stack
- Metrics: [tool]
- Logging: [tool + log format]
- Tracing: [tool]
- Alerting: [tool + escalation policy]

## Pending Design Decisions
| Decision | Owner | Target Date | Impact |
|---|---|---|---|
[List all [DESIGN DECISION PENDING] items from the session]
```

---

## Phase 4 — Design Summary

After all files are written, produce a design summary for the user:

```
## Design Setup Complete
Session date: [date]
Files updated: design.md, uiux.md, api.md, database.md, impl.md

### Key Decisions Made
[Numbered list of the most consequential decisions from the session]

### Pending Decisions
[Items that could not be resolved — owner and target resolution date for each]

### Recommended Next Steps
1. Share design documents with customer for validation (if applicable)
2. Resolve all [DESIGN DECISION PENDING] items before Sprint 0
3. Conduct Sprint 0 detailed design to elaborate entity model and endpoint inventory
4. Review impl.md with the engineering team for alignment
```

---

## Constraints

- **Never overwrite AS-IS sections** in any file. All AS-IS content is historical record and must be preserved intact.
- If a design decision conflicts with a customer expectation in `knowledge.md`, do NOT silently proceed — flag the conflict and ask the user to resolve it.
- Do NOT populate the endpoint inventory in `api.md` or the full entity model in `database.md` during this session — those require a Sprint 0 detailed design pass. Mark them as `[To be elaborated in Sprint 0]`.
- All design decisions should reference the constraint or expectation from `knowledge.md` that motivated them, for traceability.
- If the user answers "TBD" or "not sure" on a critical decision, record it as `[DESIGN DECISION PENDING]` with an explicit owner and flag it in `impl.md`.
