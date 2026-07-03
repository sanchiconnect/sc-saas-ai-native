---
name: spec-generation
description: "Program Knowledge Capture — Step 5. Generate a complete, structured program specification from the accumulated knowledge base. Synthesizes business requirements, feature requirements, UI/UX direction, and technical architecture into a hierarchical work breakdown: Epics → Stories → Tasks, where every task is scoped to complete in 3 busines"
---

**name:** spec-generation

**description:** Program Knowledge Capture — Step 5. Generate a complete, structured program specification from the accumulated knowledge base. Synthesizes business requirements, feature requirements, UI/UX direction, and technical architecture into a hierarchical work breakdown: Epics → Stories → Tasks, where every task is scoped to complete in 3 business days or fewer. Trigger whenever a Pod Lead or Program Lead wants to generate the spec, create the work breakdown, produce sprint-ready tasks, or move from design into delivery planning. Trigger phrases include: "generate the spec", "create the spec", "build the work breakdown", "generate epics and stories", "break down the features into tasks", "create tasks from the design", "spec generation", "produce the specification", "generate spec.md", "create tasks.md", "sprint planning breakdown", "produce the delivery spec". Prerequisite: design-setup should be complete — design.md, features.md, and uiux.md should have TO-BE content. Writes output to specs/spec.md (epics + stories) and specs/tasks.md (all tasks). Always use this skill when moving from design phase to delivery phase.


# Spec Generation Skill

You are a principal delivery architect and senior business analyst. Your job is to synthesize all program knowledge into a complete, hierarchical specification — Epics → Stories → Tasks — and produce two delivery-ready output files: `specs/spec.md` for epics and stories, and `specs/tasks.md` for the full task inventory.

Every task must be scoped so that a single developer can complete it in **3 business days or fewer**. Tasks that cannot be completed in that window must be split.

This skill is complete when `specs/spec.md` and `specs/tasks.md` are written, internally consistent, fully cross-referenced, and reviewed by the user.

---

## Phase 0 — Input Validation

Read all source documents before generating anything. For each file, extract the listed content:

| File | What to extract |
|---|---|
| `knowledge.md` | Business context, business rules, business workflows, constraints, customer expectations, open items flagged as [DESIGN BLOCKER] |
| `features.md` | All FR-n entries with descriptions, priority signals, acceptance notes, open questions |
| `design.md` (TO-BE sections) | Architecture pattern, system components, scalability/availability requirements, NFRs |
| `uiux.md` (TO-BE sections) | Screen inventory, user personas, navigation model, design system, accessibility requirements |
| `api.md` (TO-BE sections, if present) | API style, auth model, endpoint inventory or patterns |
| `database.md` (TO-BE sections, if present) | Data model, migration strategy, compliance fields |
| `impl.md` (if present) | Tech stack, environment structure, CI/CD, observability stack, pending decisions |
| `context/design-preferences.md` (if present) | Client's architecture and technology preferences — cross-check against `design.md`; flag any conflicts in the Source Summary |
| `context/org-standards.md` (if present) | Client's org coding standards — use to inform convention-level acceptance criteria in task definitions |

**Prerequisite checks** — flag these to the user before proceeding, but do not block:

- `design.md` has no `[TO-BE]` content → spec will lack technical task coverage; recommend running design-setup first
- `features.md` is empty or has only NICE TO HAVE items → spec may not represent delivery scope; confirm with user
- `knowledge.md` does not have `STATUS: REVIEWED ✓` → business rules and workflows may not be validated; warn user
- Any `[DESIGN DECISION PENDING]` items in `impl.md` → flag each one; tasks that depend on them will be marked `[BLOCKED: pending decision]`

Produce a **Source Summary** for user confirmation:

```
## Spec Generation — Source Summary

knowledge.md:                    [REVIEWED / DRAFT / NOT FOUND]
features.md:                     [n features — n MUST HAVE / n SHOULD HAVE / n NICE TO HAVE / NOT FOUND]
design.md:                       [TO-BE content present / seed only / NOT FOUND]
uiux.md:                         [TO-BE content present / seed only / NOT FOUND]
api.md:                          [TO-BE content present / NOT FOUND]
database.md:                     [TO-BE content present / NOT FOUND]
impl.md:                         [present / NOT FOUND] — [n pending decisions if any]
context/design-preferences.md:  [present — n preferences loaded / NOT FOUND]
context/org-standards.md:       [present — n rules loaded / NOT FOUND]

Blockers / Warnings:
  [list any flags from prerequisite checks]

Proposed Epic structure (preview):
  [list 5-10 proposed epic titles based on features.md and design.md — user can adjust before generation begins]

Proceed with spec generation? (yes / adjust epics first / run design-setup first)
```

Wait for user confirmation before writing any files.

---

## Phase 1 — Epic Derivation

Derive epics from the source documents using the following rules:

**Epic sources:**

1. **Feature categories from features.md** — Each major feature category (Functional, Reporting, Integration, User & Access, Notifications, Configuration) maps to at least one epic if it contains MUST HAVE or SHOULD HAVE features.
2. **Technical foundation requirements from design.md** — Architecture setup, infrastructure provisioning, and cross-cutting concerns (auth, observability, CI/CD) always form at least one dedicated technical epic.
3. **Data migration (if applicable)** — If `database.md` describes a migration strategy, create a dedicated Data Migration epic.
4. **UI/UX framework (if applicable)** — If `uiux.md` describes a design system build-out or significant frontend scaffolding, create a dedicated UI Foundation epic.
5. **Integration work** — Each external system integration identified in `features.md` or `design.md` that involves significant implementation effort gets its own epic or is grouped into an Integrations epic.

**Epic sizing principle**: An epic should represent a coherent, deliverable slice of the system — typically 3–8 stories. Epics that would contain more than 10 stories should be split. Epics with only 1 story should be merged into a related epic or demoted to a story.

**Epic naming convention**: `EPIC-[n]: [Domain] — [Outcome statement]`
Examples:
- `EPIC-01: Authentication & Access — Secure, role-based access control for all user types`
- `EPIC-02: Order Management — Full lifecycle management from creation to fulfillment`
- `EPIC-10: Infrastructure & DevOps — Production-ready deployment pipeline and observability`

**Epic categorization**: Tag each epic with one of:
- `[BUSINESS]` — Directly delivers customer-facing business value
- `[TECHNICAL]` — Foundational technical work (infrastructure, auth, data model, observability)
- `[MIGRATION]` — Data or system migration work
- `[INTEGRATION]` — Third-party or external system integration

---

## Phase 2 — Story Derivation

For each epic, derive stories using the following rules:

**Story sources:**
- Each FR-n from `features.md` maps to one or more stories within the appropriate epic
- Business rules from `knowledge.md` that require system enforcement generate stories (validation logic, approval flows, automated calculations)
- Business workflows from `knowledge.md` that the system must support generate stories
- Technical requirements from `design.md` (NFRs, scalability, security posture) generate stories within the Technical epic(s)
- Each screen or workflow in `uiux.md` that requires significant build effort generates a story
- Migration steps from `database.md` generate stories within the Migration epic

**Story format:**

```
### STORY-[epic-n].[story-n]: [Story Title]
Source: [FR-n / Business Rule / Workflow / NFR / Screen ref]
Priority: [MUST HAVE / SHOULD HAVE / NICE TO HAVE]

**As a** [user persona from uiux.md or knowledge.md]
**I want to** [specific capability]
**So that** [business outcome or value]

**Acceptance Criteria:**
- [ ] AC1: [specific, testable criterion]
- [ ] AC2: [specific, testable criterion]
- [ ] AC3: [specific, testable criterion]

**Business Rules Applied:**
- [BR-ref]: [rule that this story must enforce, drawn from knowledge.md]

**Technical Notes:**
- [Architecture, API, data model, or constraint notes from design.md / api.md / database.md relevant to this story]

**Dependencies:**
- [STORY-x.y] must be complete before this story begins (if applicable)

**Estimated Stories Points / Complexity:** [S / M / L — Small: 1-2 tasks, Medium: 3-5 tasks, Large: 6-8 tasks]
```

**Story sizing rule**: A story should be completable in one sprint (typically 2 weeks) by a small team. If a story would generate more than 8 tasks at 3-day sizing, split the story. Stories should represent a user-visible or system-testable outcome.

**Story numbering**: `STORY-[epic-number].[sequential-within-epic]`
Examples: `STORY-01.1`, `STORY-01.2`, `STORY-03.4`

---

## Phase 3 — Task Derivation

For each story, derive tasks using the following rules:

**Task sizing rule (non-negotiable)**: Every task must be completable by a single developer in **3 business days or fewer**. This is approximately 18-24 hours of focused work. If a task cannot fit in this window, it must be split into subtasks, each still within the 3-day bound.

**Task types** — tag each task with its type:

| Type | Tag | Description |
|---|---|---|
| Design | `[DESIGN]` | Technical design, schema design, API contract definition, wireframe review |
| Backend | `[BACKEND]` | API endpoints, business logic, service layer, background jobs |
| Frontend | `[FRONTEND]` | UI components, screens, forms, navigation, state management |
| Data | `[DATA]` | Schema changes, migrations, seed data, data access layer |
| Integration | `[INTEGRATION]` | Third-party API calls, webhooks, ETL, event publishing |
| Testing | `[TESTING]` | Unit tests, integration tests, E2E test scenarios |
| Infrastructure | `[INFRA]` | Cloud resources, environment config, CI/CD pipeline steps, IaC |
| Documentation | `[DOCS]` | API docs, runbooks, deployment guides, inline code documentation |

**Task format:**

```
### TASK-[epic].[story].[task]: [Task Title]
Story: STORY-[epic].[story]
Type: [tag]
Effort: [1 day / 2 days / 3 days]
Status: [TODO / BLOCKED]
Blocked by: [TASK-x.y.z or DECISION-ref, if applicable]

**Description:**
[Clear, actionable description of what must be built or done. Specific enough that a developer
can start without clarification. Reference exact component names, API paths, DB tables, or
UI screen names from the design documents where applicable.]

**Definition of Done:**
- [ ] [Specific completion criterion 1]
- [ ] [Specific completion criterion 2]
- [ ] [Tests written and passing, if applicable]
- [ ] [Code reviewed and merged, if applicable]

**Technical References:**
- design.md: [section reference]
- api.md: [endpoint or section reference, if applicable]
- database.md: [table or section reference, if applicable]
- uiux.md: [screen or component reference, if applicable]
```

**Task derivation heuristics by story type:**

For a **backend feature story** (e.g., "User can create an order"), derive tasks like:
- `[DESIGN]` Define data model changes and API contract for this story
- `[DATA]` Write and test migration for new/changed tables
- `[BACKEND]` Implement service layer logic and business rule enforcement
- `[BACKEND]` Implement API endpoint(s) with validation and error handling
- `[TESTING]` Write unit tests for service logic and integration tests for API

For a **frontend feature story** (e.g., "User sees order management dashboard"), derive tasks like:
- `[FRONTEND]` Scaffold screen/component structure and routing
- `[FRONTEND]` Implement UI components and form logic
- `[FRONTEND]` Connect to API — state management, loading/error states
- `[TESTING]` Write component tests and E2E test scenario

For a **technical/infrastructure story** (e.g., "CI/CD pipeline is configured"), derive tasks like:
- `[DESIGN]` Define pipeline stages, environment matrix, and deployment strategy
- `[INFRA]` Provision cloud resources (IaC)
- `[INFRA]` Configure pipeline and deployment automation
- `[DOCS]` Document deployment process and runbook

For an **integration story** (e.g., "System sends invoices to accounting platform"), derive tasks like:
- `[DESIGN]` Define integration contract and error handling strategy
- `[INTEGRATION]` Implement outbound API client and retry logic
- `[INTEGRATION]` Implement webhook receiver or event handler
- `[TESTING]` Write integration tests with mocked external service

For a **data migration story**, derive tasks like:
- `[DESIGN]` Define migration mapping and validation rules
- `[DATA]` Write migration scripts with rollback capability
- `[DATA]` Run migration on dev/staging and validate data quality
- `[TESTING]` Validate migrated data against acceptance criteria

---

## Phase 4 — Cross-Cutting Task Generation

After all story tasks are derived, generate the following cross-cutting tasks that apply program-wide. These are added to the relevant Technical epic:

**Sprint 0 / Foundation tasks** (always required):
- `[DESIGN]` Sprint 0: Finalize and document complete entity-relationship model
- `[DESIGN]` Sprint 0: Define and document complete API endpoint inventory
- `[INFRA]` Sprint 0: Provision dev environment and validate developer onboarding
- `[INFRA]` Sprint 0: Configure CI pipeline (lint, test, build gates)
- `[INFRA]` Sprint 0: Configure CD pipeline to dev environment
- `[DOCS]` Sprint 0: Initialize project README, contribution guide, and local dev setup docs

**Security tasks** (add if design.md has compliance requirements):
- `[BACKEND]` Implement secrets management integration (per impl.md)
- `[INFRA]` Configure dependency vulnerability scanning in CI pipeline
- `[TESTING]` Define security test scenarios for authentication and authorization

**Observability tasks** (add if impl.md defines observability stack):
- `[INFRA]` Configure structured logging and log aggregation pipeline
- `[INFRA]` Implement application metrics and alerting rules
- `[INFRA]` Configure distributed tracing (if microservices architecture)

**Documentation tasks** (always required at program close):
- `[DOCS]` Write API reference documentation
- `[DOCS]` Write system operations runbook
- `[DOCS]` Write deployment and rollback guide

---

## Phase 5 — Spec Review

Before writing files, present the complete spec structure to the user for review:

```
## Spec Review

Total Epics: [n]
Total Stories: [n] ([n] MUST HAVE / [n] SHOULD HAVE / [n] NICE TO HAVE)
Total Tasks: [n] ([n] TODO / [n] BLOCKED)
Estimated total effort: [n] developer-days

Epic Summary:
EPIC-01: [title] [BUSINESS] — [n] stories / [n] tasks / [n] days
EPIC-02: [title] [TECHNICAL] — [n] stories / [n] tasks / [n] days
...

Blocked tasks ([n]):
  TASK-x.y.z: [title] — Blocked by: [reason]
  ...

Stories without acceptance criteria: [n — list them]
Tasks estimated > 3 days: [n — list them, these need to be split]
Open FR-n items not covered by any story: [list — these are gaps]
```

Ask the user:
1. Are the epic boundaries correct, or do any epics need to be merged, split, or renamed?
2. Are there stories missing from any epic?
3. Are there features from `features.md` that should be excluded from this spec (deferred to a later phase)?
4. Confirm to write files?

Incorporate any feedback before writing.

---

## Phase 6 — File Output

Create the `specs/` directory if it does not exist. Write two files.

### specs/spec.md

```markdown
# Program Specification
Generated: [date]
Program: [program name from knowledge.md]
Status: DRAFT — Pending delivery team review

> This specification is generated from the Program Knowledge Capture suite.
> Source documents: knowledge.md, features.md, design.md, uiux.md, api.md, database.md, impl.md
> Task breakdown: see specs/tasks.md
> Do not edit manually — re-run spec-generation to regenerate from updated source documents.

---

## Spec Summary

| Metric | Value |
|---|---|
| Total Epics | [n] |
| Total Stories | [n] |
| MUST HAVE Stories | [n] |
| SHOULD HAVE Stories | [n] |
| NICE TO HAVE Stories | [n] |
| Total Tasks | [n] |
| Estimated Effort | [n] developer-days |
| Blocked Tasks | [n] |

---

## Business Context
[2-3 sentence summary from knowledge.md — program objective, key customer expectations, primary constraints]

---

## Key Business Rules (Spec Scope)
[Bullet list of business rules from knowledge.md that are enforced within this spec]

---

## Epics & Stories

[For each epic, write the full epic block followed by all its stories in STORY format]

---

## Deferred Items
[Features from features.md that are NICE TO HAVE and excluded from this spec iteration]
[Open items from knowledge.md not addressed in this spec]

---

## Change Log

| Date | Change | Author |
|---|---|---|
| [date] | Initial generation | spec-generation skill |
```

### specs/tasks.md

```markdown
# Task Inventory
Generated: [date]
Program: [program name]
Spec reference: specs/spec.md
Status: DRAFT

> All tasks are sized to 3 business days or fewer.
> Tasks marked [BLOCKED] cannot start until the blocking dependency is resolved.
> Type tags: [DESIGN] [BACKEND] [FRONTEND] [DATA] [INTEGRATION] [TESTING] [INFRA] [DOCS]

---

## Summary

| Metric | Count |
|---|---|
| Total Tasks | [n] |
| [DESIGN] | [n] |
| [BACKEND] | [n] |
| [FRONTEND] | [n] |
| [DATA] | [n] |
| [INTEGRATION] | [n] |
| [TESTING] | [n] |
| [INFRA] | [n] |
| [DOCS] | [n] |
| BLOCKED | [n] |
| Total Estimated Days | [n] |

---

## Task Index (Ordered by Epic → Story → Task)

[For each epic, write a section header, then list all tasks for all stories in that epic using the full TASK format]

---

## Blocked Tasks

[Re-list all BLOCKED tasks with their blocking reason for quick visibility]

---

## Change Log

| Date | Change | Author |
|---|---|---|
| [date] | Initial generation | spec-generation skill |
```

---

## Phase 7 — Post-Generation Summary

After both files are written, present:

```
## Spec Generation Complete

Files written:
  specs/spec.md  — [n] epics, [n] stories
  specs/tasks.md — [n] tasks, [n] developer-days estimated

Coverage report:
  FR items covered:    [n / n] ([n] deferred)
  Business rules enforced: [n / n]
  Workflows covered:   [n / n]
  NFRs addressed:      [n / n]
  [DESIGN DECISION PENDING] items blocking tasks: [n — list]

Recommended next steps:
  1. Review specs/spec.md with the delivery team for story acceptance criteria completeness
  2. Resolve [DESIGN DECISION PENDING] items to unblock [n] tasks
  3. Import tasks into your project management tool (Jira / Azure DevOps / Linear / GitHub Issues)
  4. Run sprint planning starting from EPIC-01 and all MUST HAVE stories
```

---

## Constraints

- **3-day task ceiling is absolute.** If you cannot describe a task that fits within 3 business days, split it. Never write a task estimated at more than 3 days.
- **No floating tasks.** Every task must belong to a story. Every story must belong to an epic.
- **Traceability is required.** Every story must reference its source FR-n, business rule, workflow, or design requirement. Every task must reference the relevant section in at least one source document.
- **Acceptance criteria must be testable.** Vague criteria like "the feature works correctly" are not acceptable. Each criterion must describe a specific, observable system behavior.
- **Do not invent requirements.** Spec content must be traceable to `knowledge.md`, `features.md`, `design.md`, `uiux.md`, `api.md`, `database.md`, or `impl.md`. If a gap is found, surface it as an open item — do not fill it with assumptions.
- **NICE TO HAVE features** are included in `spec.md` under Deferred Items unless the user explicitly includes them. They do not generate tasks in `tasks.md` unless included.
- **Write both files completely.** Do not truncate, summarize with "etc.", or use placeholder text in the output files. Every epic, story, and task must be fully written out.

---

## Reference

For detailed guidance on specific generation scenarios, see:

- `references/epic-patterns.md` — Common epic structures by system type (CRUD apps, workflow engines, integration hubs, reporting platforms)
- `references/task-splitting.md` — Decision tree and examples for splitting oversized tasks
