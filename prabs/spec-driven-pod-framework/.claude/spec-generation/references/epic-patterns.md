# Epic Patterns Reference

Common epic structures by system archetype. Use these as starting templates when deriving
epics from features.md and design.md. Adapt to the specific program — these are patterns,
not prescriptions.

---

## Archetype 1: CRUD / Line-of-Business Application

A system whose primary purpose is creating, managing, and querying business entities
(e.g., CRM, ERP module, case management, inventory system).

**Typical Epic Structure:**

| Epic | Type | Typical Stories |
|---|---|---|
| Technical Foundation & Infrastructure | TECHNICAL | CI/CD setup, environment provisioning, observability, auth scaffolding |
| Authentication & Access Control | TECHNICAL | Login, RBAC, session management, password reset |
| [Core Entity 1] Management | BUSINESS | CRUD operations, validation, state machine, search/filter |
| [Core Entity 2] Management | BUSINESS | CRUD operations, relationships to Entity 1 |
| [Workflow Name] Workflow | BUSINESS | Multi-step process, approval flows, notifications triggered |
| Reporting & Dashboards | BUSINESS | Summary views, exports, KPI displays |
| Administration & Configuration | BUSINESS | System settings, user management, audit log |
| Data Migration | MIGRATION | Schema mapping, migration scripts, validation, cutover |
| External Integrations | INTEGRATION | One story or sub-epic per external system |

**Story pattern for a managed entity:**
- Create [Entity]: form, validation, persistence
- View/Search [Entity] list: filtering, pagination, sort
- View [Entity] detail: read-only display, related records
- Edit [Entity]: update form, validation, optimistic locking
- [Entity] state transitions: status changes, guards, audit trail
- [Entity] notifications: triggered alerts on state change

---

## Archetype 2: Workflow / Process Automation System

A system whose primary purpose is routing work items through defined steps with
human or automated decision points (e.g., approval systems, onboarding flows,
claims processing, procurement).

**Typical Epic Structure:**

| Epic | Type | Typical Stories |
|---|---|---|
| Technical Foundation | TECHNICAL | Same as above |
| Auth & Access Control | TECHNICAL | Same as above |
| Work Item Lifecycle | BUSINESS | Creation, assignment, transitions, closure |
| Workflow Configuration | BUSINESS | Define workflow templates, steps, routing rules |
| Task Queue & Assignment | BUSINESS | Queue views, manual/auto assignment, SLA tracking |
| Approvals & Escalations | BUSINESS | Approval requests, delegation, escalation rules, audit |
| Notifications & Reminders | BUSINESS | Email/in-app alerts, SLA breach warnings |
| Reporting & SLA Tracking | BUSINESS | Throughput metrics, SLA compliance, bottleneck reports |
| Integration with Source Systems | INTEGRATION | Ingest work items from external triggers |
| Administration | BUSINESS | Workflow template management, user/role management |

**Story pattern for an approval step:**
- Request approval: initiate approval request, notify approvers
- Approve/Reject: action form, required comment, state transition
- Delegation: assign approval to another user
- Escalation: auto-escalate after SLA breach
- Approval audit trail: immutable history of decisions

---

## Archetype 3: Data / Reporting Platform

A system whose primary value is ingesting, transforming, and surfacing data
(e.g., analytics dashboard, operational reporting tool, data warehouse UI).

**Typical Epic Structure:**

| Epic | Type | Typical Stories |
|---|---|---|
| Technical Foundation | TECHNICAL | Same as above |
| Auth & Access Control | TECHNICAL | Row-level security, report-level permissions |
| Data Ingestion Pipeline | TECHNICAL | Source connectors, ETL jobs, scheduling |
| Data Model & Storage | TECHNICAL | Schema design, partitioning, retention |
| Core Dashboards | BUSINESS | KPI panels, date range controls, drill-down |
| Ad-Hoc Reporting | BUSINESS | Query builder, saved reports, scheduled delivery |
| Data Export | BUSINESS | CSV/Excel export, API data access |
| Data Quality & Alerts | BUSINESS | Anomaly detection, freshness alerts |
| Administration | BUSINESS | Data source management, user access, refresh schedules |

---

## Archetype 4: Integration Hub / API Platform

A system whose primary purpose is connecting multiple systems (e.g., middleware,
event broker, API gateway, data sync platform).

**Typical Epic Structure:**

| Epic | Type | Typical Stories |
|---|---|---|
| Platform Foundation | TECHNICAL | Core message routing, error handling, retry framework |
| Auth & Security | TECHNICAL | API key management, OAuth server, IP allowlisting |
| [Source System A] Connector | INTEGRATION | Inbound adapter, event parsing, schema validation |
| [Source System B] Connector | INTEGRATION | Same pattern |
| [Target System X] Connector | INTEGRATION | Outbound adapter, retry, dead-letter handling |
| Transformation Layer | TECHNICAL | Data mapping engine, schema registry |
| Monitoring & Dead-Letter | TECHNICAL | Message failure dashboard, replay capability |
| Developer Portal | BUSINESS | API documentation, sandbox, onboarding |

---

## Archetype 5: Customer-Facing Web / Mobile Application

A system whose primary users are customers or end-users (e.g., portal, self-service
app, marketplace, consumer product).

**Typical Epic Structure:**

| Epic | Type | Typical Stories |
|---|---|---|
| Technical Foundation | TECHNICAL | Same as above + mobile build pipeline if applicable |
| Auth & Profile | BUSINESS | Registration, login, profile management, password reset |
| [Core User Journey 1] | BUSINESS | Primary value-delivery flow for the target persona |
| [Core User Journey 2] | BUSINESS | Secondary flow |
| Search & Discovery | BUSINESS | Search, filters, recommendations |
| Notifications & Preferences | BUSINESS | Notification centre, user preference management |
| Help & Support | BUSINESS | FAQ, contact form, ticket creation |
| Administration (internal) | BUSINESS | Customer management, moderation, support tooling |
| Analytics & Instrumentation | TECHNICAL | Event tracking, funnel analysis, A/B test framework |

---

## Universal Technical Epic Contents

Regardless of archetype, a Technical Foundation epic should always contain stories for:

1. **Repository & project structure** — monorepo or polyrepo setup, conventions, linting, formatter
2. **CI pipeline** — build, lint, test, security scan gates
3. **CD pipeline to dev** — automated deployment on merge to main
4. **Environment provisioning** — dev, staging, prod infrastructure (IaC)
5. **Authentication scaffolding** — JWT/OAuth implementation, token validation middleware
6. **Logging & observability baseline** — structured logs, metrics endpoint, health check
7. **Database baseline** — connection pooling, migration framework, seed data
8. **Error handling framework** — global error handler, error response shape, alerting hook
9. **Developer onboarding** — README, local dev setup, first-run validation script
