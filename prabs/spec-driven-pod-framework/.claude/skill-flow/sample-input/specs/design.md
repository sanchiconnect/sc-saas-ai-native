# Technical Design Specification
**Program:** Mobile-First Checkout Experience
**Program ID:** PRG-MFCE-001
**Last Updated:** June 2026
**Version:** 1.0

---

## System Architecture

### Architecture Pattern
**Modular Monolith with BFF API layer.** A single deployable backend application, internally structured as four domain modules aligned to the pod ownership model (checkout, payments, identity, analytics). This avoids microservice operational overhead (service discovery, distributed tracing complexity, separate deployment pipelines) for a team of 12 engineers while maintaining clear module boundaries. The API layer implements a Backend-for-Frontend (BFF) pattern to serve mobile-optimized payloads — response field filtering and gzip compression per the program's mobile bandwidth requirement.

### Layer Breakdown
```
[Client Layer]
  Mobile Web (Next.js 14 PWA)  |  iOS App (React Native)  |  Android App (React Native)
         |                               |                          |
         └─────────────────── HTTPS/REST (gzip, field filtering) ──┘
                                         ↓
[API Layer — BFF]
  FastAPI (Python 3.12) — checkout-bff service
  Mobile-optimized request/response contracts; OpenAPI schema auto-generated
                                         ↓
[Service / Domain Modules]
  checkout-module     (CheckoutSession lifecycle, Order orchestration)
  payment-module      (Payment, Stripe gateway, Apple Pay / Google Pay)
  identity-module     (Customer, ShippingAddress, PaymentMethodToken, autocomplete)
  analytics-module    (funnel events, A/B experiment assignment)
                                         ↓
[Data Layer]
  PostgreSQL 16 (RDS Multi-AZ) — Orders, Payments, Customers, Addresses, Tokens
  Redis 7 (ElastiCache Cluster) — CheckoutSession store, geocoding cache, rate limits
                                         ↓
[External Layer]
  Stripe                     — payment gateway, Apple Pay, Google Pay (PCI-DSS SAQ-A)
  Google Maps Geocoding API  — address autocomplete suggestions
  Firebase Cloud Messaging   — push notifications (order confirmation, session recovery)
  AWS SES                    — transactional email (order confirmation, recovery link)
```

### Communication Patterns
- **Sync (client-facing):** REST JSON over HTTPS; gzip encoding on all responses; response field filtering via FastAPI `response_model` exclusions; 30-second gateway timeout (BR-023)
- **Async (internal):** Celery + Redis broker for background jobs — session expiry cleanup (BR-001), post-confirmation notification dispatch, analytics event flushing
- **Caching:** Redis for CheckoutSession (15-min TTL per BR-001), geocoding API responses (24-hour TTL per BR-031 local cache requirement), and rate-limit counters (payment retry enforcement per BR-021)
- **Domain events:** Internal in-process events for cross-module notification (e.g., `OrderConfirmed` triggers analytics instrumentation and notification dispatch without HTTP coupling)

---

## Technology Stack

| Layer | Technology | Version | Rationale |
|-------|------------|---------|-----------|
| Backend Language | Python | 3.12 | Async-first runtime; rich payment/compliance library ecosystem; type-hint enforcement via Pydantic |
| Backend Framework | FastAPI | 0.111 | Async BFF; auto-generates OpenAPI for `spec-api` alignment; native Pydantic v2 integration |
| Frontend Language | TypeScript | 5.x | Strict typing enforced across all payment-path code; eliminates class of type errors near card data handling |
| Frontend Framework (Web) | Next.js | 14.x | PWA support; edge-optimized rendering for LCP <1.5s; App Router for mobile-first layouts |
| Frontend Framework (Native) | React Native | 0.74 | Shared TypeScript business logic with web; native biometric APIs for BR-041; iOS/Android from single codebase |
| Database (primary) | PostgreSQL | 16 | ACID guarantees for Order/Payment state machines; UUID PKs; JSONB for `line_items` snapshot (BR-013) |
| Cache / Session Store | Redis | 7.x | Server-side CheckoutSession TTL (BR-001); geocoding cache (BR-031); Celery broker; rate-limit counters |
| ASGI Server | uvicorn + gunicorn | 0.29 / 21.x | Production-grade async runner; multi-worker for concurrency target (15K sessions) |
| Runtime (frontend build) | Node.js | 20 LTS | Next.js / React Native build toolchain; stable LTS guarantees |

---

## Libraries & Dependencies

### Backend
| Category | Library | Version | Purpose |
|----------|---------|---------|---------|
| Web framework | fastapi | 0.111 | REST API, OpenAPI schema, dependency injection |
| ASGI server | uvicorn | 0.29 | Async request serving |
| Data validation | pydantic | v2 | Request/response schemas; input validation at API boundary (all checkout inputs) |
| ORM | sqlalchemy | 2.x | Async ORM; mapped to PostgreSQL via asyncpg driver |
| DB driver | asyncpg | 0.29 | High-performance async PostgreSQL driver |
| Migrations | alembic | 1.x | Schema migration management; version-controlled alongside models |
| Cache / session | redis (redis-py async) | 5.x | CheckoutSession store (TTL 15 min); geocoding cache; rate-limit counters |
| Task queue | celery | 5.x | Background jobs: session expiry, notification dispatch |
| Auth — JWT | python-jose | 3.x | JWT RS256 token encoding/decoding for customer auth |
| Auth — crypto | cryptography | 42.x | RSA key pair management for JWT signing |
| Payment gateway | stripe | 9.x | Payment authorization, capture, refund; Apple Pay / Google Pay server-side token verification; single-use wallet token enforcement (BR-022) |
| HTTP client | httpx | 0.27 | Async outbound calls to geocoding API, payment gateway |
| Address geocoding | httpx (direct call) | — | Google Maps Geocoding API; response cached in Redis |
| Testing | pytest + pytest-asyncio | 8.x | Unit and async integration tests |
| Test DB | pytest-postgresql | 6.x | Ephemeral PostgreSQL per test session |
| Linting | ruff | 0.4 | Fast Python linter; replaces flake8 + isort |
| Formatting | black | 24.x | Deterministic code formatter |
| Type checking | mypy | 1.x | Static type checking in CI |
| Observability | opentelemetry-sdk | 1.x | Distributed tracing; trace IDs propagated across payment hop chain |
| Metrics | opentelemetry-exporter-otlp | 1.x | OTLP export to Datadog |
| Error tracking | sentry-sdk | 2.x | Exception capture with PII scrubbing (no PAN in Sentry payloads) |

### Frontend (Web — Next.js)
| Category | Library | Version | Purpose |
|----------|---------|---------|---------|
| UI framework | react | 18.x | Component model |
| Routing / SSR | next | 14.x | PWA, App Router, edge rendering for LCP target |
| State management | zustand | 4.x | Lightweight global state for checkout step and cart; avoids Redux overhead |
| Server state | tanstack-query | 5.x | API data fetching, caching, and optimistic updates |
| Forms | react-hook-form | 7.x | Controlled form state for address and card inputs; minimal re-renders |
| Validation | zod | 3.x | Client-side schema validation; mirrors Pydantic models at type level |
| Payment UI | @stripe/stripe-js + @stripe/react-stripe-js | 3.x | Stripe Elements for card input; Apple Pay / Google Pay Payment Request Button |
| Styling | tailwindcss | 3.x | Utility-first; mobile-first breakpoints; WCAG contrast utilities |
| Accessibility | @radix-ui/react-* | 1.x | Unstyled, accessible primitives (dialogs, dropdowns, focus traps) |
| A11y linting | eslint-plugin-jsx-a11y | 6.x | Enforces WCAG 2.1 AA rules at lint time |
| Linting | eslint + prettier | 8.x / 3.x | Code style; Airbnb config base |
| Testing | vitest + @testing-library/react | 1.x | Component unit tests; accessibility queries |
| E2E testing | playwright | 1.x | End-to-end checkout flows on mobile viewport (375px) |
| Error tracking | @sentry/nextjs | 8.x | Frontend error capture; source map upload in CI |
| PWA | next-pwa | 5.x | Service worker, offline shell, manifest |

### Frontend (Native — React Native)
| Category | Library | Version | Purpose |
|----------|---------|---------|---------|
| Navigation | react-navigation | 6.x | Stack and bottom-tab navigation |
| Biometric auth | react-native-biometrics | 3.x | Face ID / Touch ID for BR-041 one-click checkout |
| Payment | @stripe/stripe-react-native | 0.37 | Native Stripe card element; Apple Pay / Google Pay |
| Accessibility | react-native built-in a11y props | — | accessibilityLabel, accessibilityHint on all interactive elements |
| E2E testing | detox | 20.x | Native E2E tests on iOS and Android simulators |

---

## Infrastructure

### Cloud & Hosting
- **Cloud Provider:** AWS — selected for PCI-DSS compliant infrastructure tooling, RDS Multi-AZ, ElastiCache, CloudFront, and Secrets Manager native integration
- **Primary region:** `us-east-1` (default / US traffic)
- **EU region:** `eu-west-1` — EU customer data residency requirement (GDPR; knowledge.md compliance)
- **APAC region:** `ap-southeast-1` (Singapore) — APAC customer data routing; additional markets require legal review before enabling
- **Compute:** ECS Fargate — containerized services, auto-scaling policies on CPU and active-session count
- **Database:** RDS PostgreSQL 16 Multi-AZ — automated failover; synchronous standby replica; target 99.95% availability SLA
- **Cache:** ElastiCache Redis 7 Cluster Mode — horizontal sharding for 15K concurrent session target; AOF persistence for session recovery resilience
- **CDN:** CloudFront — static assets, Next.js edge runtime; minimizes mobile page load latency for LCP <1.5s target
- **Object storage:** S3 — build artifacts, Lambda deployment packages, static asset hosting

### Containerization
- **Docker:** All backend services and frontend builds containerized via multi-stage Dockerfiles (builder → runtime); production images are distroless Python / Node
- **Compose:** `docker-compose.yml` provides local stack: FastAPI + PostgreSQL + Redis + Celery worker
- **Registry:** Amazon ECR — image scanning enabled; critical/high vulnerability findings block deployment
- **Orchestration:** ECS Fargate task definitions per service module; service auto-scaling (min 2, max 20 tasks per module)

### CI/CD
- **Pipeline:** GitHub Actions
- **Stages:** `lint` → `typecheck` → `unit-test` → `integration-test` → `build` → `deploy-staging` → `smoke-test` → `deploy-prod`
- **Branch strategy:** Trunk-based development — all work merged to `main` via short-lived feature branches (<2 days); feature flags (LaunchDarkly) gate in-flight work from live traffic
- **Rollback:** ECS task definition rollback to previous image tag; RDS point-in-time recovery; max 5-minute RTO target
- **Feature flags:** LaunchDarkly — supports phased rollout (5% → 25% → 100% per program timeline Q4 2026)

### Environments
| Environment | Purpose | Deployment Trigger | Data |
|-------------|---------|-------------------|------|
| local | Development | Manual (`docker compose up`) | Seeded fixture data; Stripe test mode |
| staging | Integration and QA | Push to `main` | Anonymized production snapshot; Stripe test mode |
| production | Live traffic | Tagged release (`v*.*.*`) | Live data; Stripe live mode |

### Secrets Management
- **Tool:** AWS Secrets Manager — all secrets (Stripe API keys, JWT RSA private key, Google Maps API key, database credentials) injected at ECS task startup
- **Rule:** No secrets in source code, committed `.env` files, container images, or application logs; secrets rotated quarterly or immediately on suspected breach
- **Local dev:** `.env.local` file (gitignored); populated from Secrets Manager via `aws-vault` or a team bootstrap script

---

## Coding Standards

### Backend (Python)
- **Style:** PEP 8 enforced by `ruff` (fast linter) and `black` (formatter); both run in pre-commit hook and CI lint stage
- **Type hints:** Required on all function signatures and public method return types; `mypy --strict` enforced in CI
- **Error handling:** All exceptions caught at module service boundaries; `HTTPException` raised to API layer only from FastAPI route handlers; internal errors logged with trace ID; raw stack traces never reach API responses
- **Naming:** `snake_case` for variables, functions, and module names; `PascalCase` for classes and Pydantic models; `UPPER_SNAKE_CASE` for constants; entity names match `specs/knowledge.md` exactly (e.g., `CheckoutSession`, `PaymentMethodToken`)
- **Test structure:** `tests/` mirrors `src/`; unit tests mock external dependencies; integration tests use `pytest-postgresql` ephemeral DB; no mocking of the database in integration tests

### Frontend (TypeScript)
- **Style:** ESLint (Airbnb config) + Prettier; config files committed to repo; enforced in CI lint stage
- **Types:** TypeScript `strict` mode; `noImplicitAny` enabled; no `any` without an explicit `// eslint-disable` comment and justification
- **Components:** Functional components only; React hooks for state and side effects; no class components
- **Accessibility:** `eslint-plugin-jsx-a11y` in ESLint config; all interactive elements must have visible focus states and accessible labels; tested with `@testing-library/react` accessibility queries (`getByRole`, `getByLabelText`)
- **Naming:** `PascalCase` for React components and TypeScript interfaces; `camelCase` for functions, variables, and hooks; `kebab-case` for file and directory names
- **Payment path:** Stripe.js card elements must be used for all card data input; no custom card input fields; this enforces Stripe SAQ-A scope and BR-020

### Shared Conventions
- **Commit messages:** Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`, `test:`, `refactor:`) — enforced by commitlint in CI
- **PR size:** Target <400 LOC diff per PR; larger changes require decomposition issue linked in PR description
- **Test coverage:** Minimum 85% line coverage on all domain module business logic; 100% coverage required on payment-module (BR-020, BR-021, BR-024 are safety-critical); E2E tests for all four workflows in `specs/knowledge.md`
- **Business rule traceability:** Code implementing a business rule must reference its BR number in a comment (e.g., `# BR-021: max 3 payment retries`)

---

## Security Design

- **Authentication:** JWT RS256 Bearer tokens — 15-minute access token TTL (aligned with CheckoutSession expiry per BR-001); 30-day refresh tokens stored in `HttpOnly` secure cookies; asymmetric keys rotated quarterly
- **Guest sessions:** Identified by `session_id` only (no JWT); email captured at IDENTITY step per BR-002; no PII beyond email stored client-side
- **Biometric auth:** WebAuthn / FIDO2 for mobile web one-click checkout; native `react-native-biometrics` for iOS / Android native app (BR-041); biometric challenge verified server-side before payment token submission
- **Transport:** HTTPS only across all environments including staging; HSTS header (`max-age=31536000; includeSubDomains`) on all API and web responses; no HTTP fallback
- **Input validation:** All API inputs validated via Pydantic v2 schemas before any domain logic executes; Zod schemas on frontend before API submission; never trust client-supplied `amount` or `order_id` — server re-derives from session state (BR-024 enforcement)
- **Payment scope:** Stripe.js / React Native Stripe SDK handle all card data input client-side; backend receives only `paymentMethodId` (opaque Stripe token); this achieves PCI-DSS SAQ-A scope — no raw PAN enters our systems at any layer (BR-020); Apple Pay and Google Pay wallet tokens are single-use, so the Stripe SDK requests a fresh device wallet token for each payment attempt including retries (BR-022)
- **Secrets:** All API keys and signing keys injected via AWS Secrets Manager at runtime; never in environment files committed to repo or in Docker images; Stripe restricted API keys scoped to minimum required permissions
- **Dependency scanning:** Dependabot enabled for Python (pip) and JavaScript (npm) dependencies; high/critical CVEs block PR merge via GitHub branch protection rules
- **PII in logs:** Sentry and CloudWatch log pipelines configured with PII scrubbing rules — email addresses masked (`c***@domain`), no PAN, no gateway tokens, no JWT payloads in log output; OpenTelemetry span attributes exclude all PII fields

---

## Observability

- **Logging:** Structured JSON to stdout (Python `structlog` library; Next.js custom `pino` logger); fields: `trace_id`, `session_id` (no customer PII), `service`, `level`, `message`, `duration_ms`; ingested by CloudWatch Logs Insights
- **Log levels:** `ERROR` for all exceptions and payment failures; `WARN` for degraded states (geocoding API unavailable per BR-031, payment retry per BR-021); `INFO` for checkout step transitions and Order state changes; `DEBUG` for development only (disabled in staging and production)
- **Distributed tracing:** OpenTelemetry SDK; trace IDs injected in all outbound HTTP headers (to Stripe, Google Maps); traces exported via OTLP to Datadog APM; critical for debugging the multi-hop payment authorization chain
- **Metrics (key):**
  - `checkout.session.created` — counter per region
  - `checkout.step.duration_ms` — histogram per step (IDENTITY, SHIPPING, PAYMENT, REVIEW, SUBMITTING)
  - `payment.authorization.duration_ms` — histogram; alert if p99 > 20s (ahead of 30s BR-023 timeout)
  - `payment.authorization.failure_rate` — gauge per payment method; spike alert threshold 5%
  - `checkout.session.expired_rate` — gauge; elevated rate indicates UX friction
  - `geocoding.api.error_rate` — gauge; elevated rate triggers BR-031 cache fallback monitoring
- **Alerting:** PagerDuty on-call rotation triggered by:
  - Payment failure rate > 5% over 5-minute window
  - Checkout API p99 latency > 2s (threatens LCP NFR)
  - CheckoutSession expiry rate > 10% (UX regression signal)
  - Any ERROR log from payment-module (zero-tolerance)
- **Dashboards:** Datadog — one dashboard per pod; program-level KPI dashboard tracks mobile conversion funnel from session creation to Order CONFIRMED

---

## [AS-IS] Architecture
<!-- Routing: [AS-IS ARCHITECTURE] -->
<!-- Populated by: doc-extraction (architecture docs, system diagrams, technical specs), code-extraction -->
<!-- DO NOT edit manually — use extraction skills only -->
<!-- Note: existing sections above are TO-BE design; this section captures current-state from customer docs -->

> **PLACEHOLDER — PENDING CUSTOMER INPUT**
> No architecture documents have been ingested. Run doc-extraction with system architecture
> specifications, infrastructure docs, or component diagrams to populate this section.

### Components
<!-- Expected: existing system components with brief descriptions and ownership -->
<!-- Entry format: [Source: <doc name>, <page/section>] [AS-IS ARCHITECTURE] <component description> -->

> PLACEHOLDER — no component inventory available yet.

<!-- APPEND BELOW THIS LINE -->

### Integration Points
<!-- Expected: known external systems, third-party APIs, data feeds, and integration patterns -->

> PLACEHOLDER — no integration inventory available yet.

<!-- APPEND BELOW THIS LINE -->

### Infrastructure
<!-- Expected: hosting model (cloud/on-prem/hybrid), deployment topology, current environments -->

> PLACEHOLDER — no infrastructure documentation available yet.

<!-- APPEND BELOW THIS LINE -->

### Non-Functional Requirements (Observed)
<!-- Expected: performance, availability, scalability, and security posture AS STATED in customer docs -->
<!-- Note: these are OBSERVED NFRs from as-is docs — not TO-BE targets -->
<!-- Do not confuse with TO-BE NFRs, which are defined in design-setup -->

> PLACEHOLDER — no NFR documentation available yet.

<!-- APPEND BELOW THIS LINE -->

---

## [AS-IS] Architecture — Code Analysis Findings
<!-- Routing: [AS-IS ARCHITECTURE] — code-extraction sub-section -->
<!-- Populated by: code-extraction after analyzing source code, IaC, and configuration files -->
<!-- DO NOT edit manually — use code-extraction skill only -->

> **PLACEHOLDER — PENDING CODEBASE INGESTION**
> No source code or infrastructure definitions have been provided. Run code-extraction against
> existing source files, IaC (Terraform, CloudFormation, Pulumi), or config files to populate.

### Observed Stack
<!-- Expected: language(s), framework(s), database, API style, auth mechanism, infrastructure — with evidence -->

| Dimension | Observed Value | Source Evidence | Notes |
|-----------|---------------|----------------|-------|
| Language(s) | PLACEHOLDER | PENDING CODEBASE INGESTION | — |
| Framework(s) | PLACEHOLDER | PENDING CODEBASE INGESTION | — |
| Database | PLACEHOLDER | PENDING CODEBASE INGESTION | — |
| API Style | PLACEHOLDER | PENDING CODEBASE INGESTION | — |
| Auth Mechanism | PLACEHOLDER | PENDING CODEBASE INGESTION | — |
| Infrastructure | PLACEHOLDER | PENDING CODEBASE INGESTION | — |

<!-- APPEND BELOW THIS LINE -->

### Architectural Pattern
<!-- Expected: Monolith / Layered MVC / Microservices / Event-driven / Serverless — with file structure evidence -->

> PLACEHOLDER — architectural pattern not yet determined from code analysis.

<!-- APPEND BELOW THIS LINE -->

### Observed Design Patterns
<!-- Expected: Repository, CQRS, Saga, Factory, Observer, etc. — each with file path evidence -->

> PLACEHOLDER — no design patterns identified yet.

<!-- APPEND BELOW THIS LINE -->

### Technical Debt Register
<!-- Populated by code-extraction: legacy issues that constrain or risk the to-be design -->

| Issue | Location | Severity | Migration Risk |
|-------|----------|----------|---------------|
| PLACEHOLDER | PENDING CODEBASE INGESTION | — | — |

<!-- APPEND BELOW THIS LINE -->

### Infrastructure Inventory
<!-- Populated by code-extraction from IaC files, Dockerfiles, CI/CD configs, environment variable references -->

> PLACEHOLDER — no infrastructure definitions analyzed yet.

<!-- APPEND BELOW THIS LINE -->

### Constraints Implied by Code
<!-- Expected: tight coupling, baked-in data model assumptions, hardcoded config, vendor lock-in -->
<!-- These directly constrain to-be design choices -->

> PLACEHOLDER — no code-implied constraints identified yet.

<!-- APPEND BELOW THIS LINE -->

---

## [AS-IS] Data
<!-- Routing: [AS-IS DATA] -->
<!-- Populated by: doc-extraction (data dictionaries, ERDs, schema docs), code-extraction (ORM/DDL) -->
<!-- DO NOT edit manually -->

> **PLACEHOLDER — PENDING CUSTOMER INPUT**
> No data model or schema documents have been ingested. Run doc-extraction with data dictionaries,
> ERDs, or schema specifications — or code-extraction against existing ORM models — to populate.

<!-- APPEND BELOW THIS LINE -->

---

## [AS-IS] API
<!-- Routing: [AS-IS API] -->
<!-- Populated by: doc-extraction (API specs, Swagger/OpenAPI, integration contracts), code-extraction -->
<!-- DO NOT edit manually -->

> **PLACEHOLDER — PENDING CUSTOMER INPUT**
> No API documentation has been ingested. Run doc-extraction with API specs or Swagger/OpenAPI
> files — or code-extraction against existing API source — to populate this section.

<!-- APPEND BELOW THIS LINE -->

---

## [TO-BE] Technology & Architecture Decisions
<!-- Routing: to-be technology and architecture decisions stated or agreed in customer meetings -->
<!-- Populated by: meeting-extraction (customer calls), doc-extraction (if customer provides to-be architectural docs) -->
<!-- DO NOT edit manually — use extraction skills only -->
<!-- Note: existing sections above are TO-BE design from spec-design; this section captures meeting-sourced decisions separately -->
<!-- Authoritative design elaboration is done in design-setup phase — these are raw meeting extracts only -->

> **PLACEHOLDER — PENDING CUSTOMER DISCOVERY**
> No meeting transcripts have been processed. Run meeting-extraction after each customer call to capture
> technology stack preferences, architecture decisions, infrastructure choices, and integration patterns
> stated or agreed by the customer.

### Technology & Architecture Decision Entry Format
<!-- Per decision:
     ### [Decision Topic]
     [MEETING: date] [Source: speaker]
     **Decision / Preference**: [What was stated]
     **Rationale**: [Why, if explained]
     **Constraints implied**: [Any limitations or requirements this creates]
     **Status**: [AGREED / CUSTOMER PREFERENCE / UNDER DISCUSSION / NEEDS VALIDATION]
-->

> PLACEHOLDER — no decisions captured yet.

<!-- APPEND BELOW THIS LINE -->

---

## Changelog

| Date | Version | Author | Summary |
|------|---------|--------|---------|
| Jun 2026 | 1.0 | Sarah Chen | Initial version — derived from program.md PRG-MFCE-001 and knowledge.md v1.0 |
| 2026-06-01 | 1.1 | doc-extraction scaffold | Added [AS-IS] routing sections (Architecture, Data, API) — all PLACEHOLDER pending document ingestion |
| 2026-06-01 | 1.2 | meeting-extraction scaffold | Added [TO-BE] Technology & Architecture Decisions section — PLACEHOLDER pending customer discovery |
| 2026-06-01 | 1.3 | design-setup scaffold | Added [TO-BE] System Architecture, Design Validation Report, Design Decision Tracker — PLACEHOLDER pending design session |

<!-- ============================================================ -->
<!-- DESIGN-SETUP SKILL OUTPUT — DO NOT EDIT MANUALLY             -->
<!-- Populated by design-setup Phase 3 during design session      -->
<!-- ============================================================ -->

## [TO-BE] System Architecture — Design Session Output
<!-- Routing: design-setup Phase 3, Domain 1 — System Architecture Pattern -->
<!-- Populated by: design-setup skill during structured session with Pod Lead and Program Lead -->
<!-- AS-IS sections above are preserved and never overwritten -->

> **PLACEHOLDER — PENDING DESIGN REVIEW**
> No design session has been completed. Run `/design-setup` to begin.
> ⚠️ Prerequisite: `knowledge.md` must carry `STATUS: REVIEWED ✓` — currently blocked.

### Architecture Pattern
> PLACEHOLDER — [DESIGN DECISION PENDING]
> Decision domain: Domain 1. Options: Monolithic / Modular monolith / Microservices / Serverless / Hybrid

<!-- OVERWRITE AFTER DESIGN SESSION -->

### System Components
| Component | Responsibility | Technology | Deployment Unit |
|-----------|---------------|-----------|----------------|
| PLACEHOLDER | PENDING DESIGN REVIEW | [DESIGN DECISION PENDING] | [DESIGN DECISION PENDING] |

<!-- REPLACE TABLE AFTER DESIGN SESSION -->

### Scalability & Availability
- **Target concurrent users:** [DESIGN DECISION PENDING]
- **Availability SLA:** [DESIGN DECISION PENDING]
- **Scaling strategy:** [DESIGN DECISION PENDING] — Options: horizontal / vertical / auto-scaling
- **Multi-tenancy model:** [DESIGN DECISION PENDING] — Options: schema-per-tenant / row-level / N/A

<!-- OVERWRITE AFTER DESIGN SESSION -->

### Service Communication
> PLACEHOLDER — [DESIGN DECISION PENDING]
> Applicable if distributed pattern is selected. Options: REST / gRPC / message queue / event bus.

<!-- OVERWRITE AFTER DESIGN SESSION -->

### Non-Functional Requirements
| Requirement | Target | Measurement Method |
|-------------|--------|--------------------|
| Response time (p95) | [DESIGN DECISION PENDING] | PENDING |
| Availability | [DESIGN DECISION PENDING] | PENDING |
| Data durability | [DESIGN DECISION PENDING] | PENDING |
| Peak throughput | [DESIGN DECISION PENDING] | PENDING |

<!-- REPLACE TABLE AFTER DESIGN SESSION -->

---

## Design Validation Report
<!-- Produced by design-setup Phase 2 — summarises decisions, conflicts, risks, and pending items -->
<!-- Generated before files are written; user confirms before session proceeds -->

> **PLACEHOLDER — PENDING DESIGN SESSION**

| Category | Count | Details |
|----------|-------|---------|
| Decisions Confirmed | 0 | PENDING DESIGN SESSION |
| Constraint Conflicts | 0 | PENDING DESIGN SESSION |
| Migration Risks | 0 | PENDING DESIGN SESSION |
| Pending Decisions | 0 | PENDING DESIGN SESSION |

<!-- OVERWRITE AFTER DESIGN SESSION PHASE 2 -->

---

## Design Decision Tracker
<!-- All [DESIGN DECISION PENDING] items unresolved during the design session -->
<!-- Populated by design-setup Phase 2 gap check and Phase 3 writes -->
<!-- States: OPEN | IN PROGRESS | RESOLVED [date] | DEFERRED -->

> **PLACEHOLDER — PENDING DESIGN SESSION**
> See impl.md Pending Design Decisions for the full domain-by-domain decision inventory.

| # | Domain | Decision | Owner | Target Date | Impact |
|---|--------|----------|-------|-------------|--------|
| DDT-1 | All domains | All design decisions open — run design-setup | — | — | Blocks Sprint 0 |

<!-- REPLACE TABLE AFTER DESIGN SESSION -->
