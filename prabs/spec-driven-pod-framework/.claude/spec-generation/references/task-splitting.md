# Task Splitting Reference

Use this reference whenever a task exceeds the 3-business-day ceiling. The decision tree
identifies why a task is oversized and prescribes the correct split strategy.

---

## The 3-Day Rule

A task is within bounds if a single developer, with full context of the codebase and
the spec, can complete it — including coding, self-review, and writing the associated
tests — in 3 business days (~18–24 hours of focused work).

A task is oversized if:
- It touches more than one architectural layer (e.g., DB + service + API + tests in one task)
- It involves building more than ~3 distinct API endpoints
- It involves building more than ~2 complex UI screens
- It involves a migration affecting more than one domain entity
- It involves integrating with more than one external service
- Its definition of done has more than 6 line items

---

## Decision Tree

```
Is the task oversized?
│
├─ YES: Why?
│
│   ├─ It spans multiple layers (DB + backend + frontend + tests)
│   │   └─ SPLIT BY LAYER
│   │       → Task A: [DATA] schema and migration
│   │       → Task B: [BACKEND] service logic and API
│   │       → Task C: [FRONTEND] UI component
│   │       → Task D: [TESTING] unit + integration + E2E tests
│   │
│   ├─ It covers too many API endpoints
│   │   └─ SPLIT BY ENDPOINT GROUP
│   │       → Task A: Read endpoints (GET list, GET detail)
│   │       → Task B: Write endpoints (POST create, PUT update)
│   │       → Task C: Action endpoints (POST /approve, POST /cancel)
│   │
│   ├─ It covers too many UI screens or components
│   │   └─ SPLIT BY SCREEN or COMPONENT
│   │       → Task A: List/search screen
│   │       → Task B: Detail/view screen
│   │       → Task C: Create/edit form
│   │
│   ├─ It covers a complex business rule with many edge cases
│   │   └─ SPLIT BY RULE COMPLEXITY
│   │       → Task A: Core rule — happy path implementation
│   │       → Task B: Edge cases and exception handling
│   │       → Task C: Unit tests for all rule branches
│   │
│   ├─ It involves a large data migration
│   │   └─ SPLIT BY MIGRATION PHASE
│   │       → Task A: Migration script — [entity or table group 1]
│   │       → Task B: Migration script — [entity or table group 2]
│   │       → Task C: Migration validation and reconciliation
│   │       → Task D: Cutover runbook and rollback script
│   │
│   ├─ It involves multiple external integrations
│   │   └─ SPLIT BY INTEGRATION
│   │       → One task per external system
│   │
│   └─ It is the first implementation of a new pattern in the codebase
│       └─ SPLIT INTO SPIKE + IMPLEMENTATION
│           → Task A: [DESIGN] Spike — validate approach, write ADR, define interface
│           → Task B: [BACKEND/FRONTEND] Implementation using spiked pattern
│
└─ NO: Task is within bounds. Proceed.
```

---

## Split Examples

### Example 1: Oversized — "Implement order management"

**Bad (too large):**
```
TASK: Implement order management
Effort: 8 days
Description: Build the full order management module including database schema,
API endpoints, frontend screens, and tests.
```

**Good (split by layer and scope):**
```
TASK-02.3.1: [DESIGN] Define order data model and API contract         — 1 day
TASK-02.3.2: [DATA] Order schema migration and seed data               — 1 day
TASK-02.3.3: [BACKEND] Order creation and validation service           — 2 days
TASK-02.3.4: [BACKEND] Order state machine (submit/approve/cancel)     — 3 days
TASK-02.3.5: [BACKEND] Order query endpoints (list, detail, search)    — 2 days
TASK-02.3.6: [FRONTEND] Order list screen with filters and pagination  — 3 days
TASK-02.3.7: [FRONTEND] Order creation form with validation            — 3 days
TASK-02.3.8: [FRONTEND] Order detail screen with action buttons        — 2 days
TASK-02.3.9: [TESTING] Order service unit tests                        — 2 days
TASK-02.3.10: [TESTING] Order API integration tests                    — 2 days
TASK-02.3.11: [TESTING] Order E2E test scenarios                       — 2 days
```

---

### Example 2: Oversized — "Integrate with Salesforce"

**Bad:**
```
TASK: Integrate with Salesforce
Effort: 7 days
Description: Connect to Salesforce API, sync accounts and contacts,
handle webhooks, and build admin configuration screen.
```

**Good (split by concern):**
```
TASK-05.2.1: [DESIGN] Define Salesforce integration contract and error strategy  — 1 day
TASK-05.2.2: [INTEGRATION] Implement Salesforce API client with auth and retry   — 2 days
TASK-05.2.3: [INTEGRATION] Account sync — outbound create/update                — 3 days
TASK-05.2.4: [INTEGRATION] Contact sync — outbound create/update                — 3 days
TASK-05.2.5: [INTEGRATION] Inbound webhook receiver and event routing           — 2 days
TASK-05.2.6: [FRONTEND] Admin screen — Salesforce connection config             — 2 days
TASK-05.2.7: [TESTING] Integration tests with Salesforce sandbox mock           — 2 days
```

---

### Example 3: Oversized — "Implement role-based access control"

**Bad:**
```
TASK: Implement RBAC
Effort: 6 days
Description: Define roles, implement permission checks, build admin UI
for role assignment, and write tests.
```

**Good:**
```
TASK-01.2.1: [DESIGN] Define role taxonomy, permission matrix, and enforcement strategy  — 1 day
TASK-01.2.2: [DATA] Role and permission schema migration                                 — 1 day
TASK-01.2.3: [BACKEND] Permission check middleware and guard decorators                  — 2 days
TASK-01.2.4: [BACKEND] Role assignment and management API endpoints                      — 2 days
TASK-01.2.5: [FRONTEND] Admin UI — user role assignment screen                          — 2 days
TASK-01.2.6: [TESTING] Permission enforcement unit and integration tests                 — 2 days
```

---

## Spike Tasks

Use a spike when the implementation approach is genuinely uncertain. A spike is always
a `[DESIGN]` task, capped at 2 days. Its definition of done is an Architectural Decision
Record (ADR) or a documented proof-of-concept with a recommendation, not working production code.

```
TASK-x.y.z: [DESIGN] Spike — [Topic]
Effort: 1–2 days
Description: Investigate [specific technical question]. Evaluate [option A] vs [option B].
Definition of Done:
- [ ] Options evaluated against [criteria from design.md / constraints]
- [ ] Recommended approach documented in ADR or design note
- [ ] Key risks and mitigations identified
- [ ] Follow-up implementation tasks defined and sized
```

Never write an implementation task that depends on an unspiked unknown. Write the spike
task first and mark the implementation task `[BLOCKED: pending TASK-x.y.z spike]`.

---

## Split Checklist

Before finalizing any set of tasks for a story, run this check:

- [ ] No single task is estimated > 3 days
- [ ] Each task touches a single primary concern (one layer, one endpoint group, one screen, one integration)
- [ ] Design/spike tasks precede implementation tasks that depend on their output
- [ ] Testing tasks are explicit — not folded into implementation tasks as an afterthought
- [ ] Each task has a clear, specific definition of done
- [ ] No task description uses vague scope language ("etc.", "and related", "as needed")
