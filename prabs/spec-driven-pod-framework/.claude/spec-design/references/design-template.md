# Technical Design Specification
**Program:** {Program Name}
**Program ID:** {PRG-ID}
**Last Updated:** {Date}
**Version:** {N}

---

## System Architecture

### Architecture Pattern
{Describe the top-level pattern: monolith, modular monolith, microservices, serverless, BFF (Backend for Frontend), etc. Include rationale.}

### Layer Breakdown
```
[Client Layer]     {Mobile Web / iOS App / Android App}
      ↓ HTTPS/REST
[API Layer]        {FastAPI / Express / Spring Boot} — {BFF or Gateway pattern}
      ↓
[Service Layer]    {Business logic, domain services}
      ↓
[Data Layer]       {PostgreSQL / MongoDB / Redis}
      ↓
[External Layer]   {Payment Gateway / Autocomplete API / Push Notifications}
```

### Communication Patterns
- **Sync:** {REST JSON over HTTPS for all client-facing endpoints}
- **Async:** {e.g., Celery + Redis for background jobs; event bus for domain events}
- **Caching:** {e.g., Redis for session data and hot-path queries}

---

## Technology Stack

| Layer | Technology | Version | Rationale |
|-------|------------|---------|-----------|
| Backend Language | {Python / Node / Go} | {3.12 / 20 / 1.22} | {Why chosen} |
| Backend Framework | {FastAPI / Django / Express} | {0.111 / 5.x / 4.x} | {Why chosen} |
| Frontend Language | {TypeScript} | {5.x} | {Type safety, DX} |
| Frontend Framework | {React / Next.js / React Native} | {18 / 14 / 0.74} | {Why chosen} |
| Database (primary) | {PostgreSQL / MySQL / MongoDB} | {16 / 8.x / 7.x} | {Why chosen} |
| Cache | {Redis} | {7.x} | {Session + hot-path caching} |
| Runtime | {Node / Python / JVM} | {version} | {Why chosen} |

---

## Libraries & Dependencies

### Backend
| Category | Library | Version | Purpose |
|----------|---------|---------|---------|
| Web framework | {fastapi} | {0.111} | REST API, OpenAPI generation |
| ASGI server | {uvicorn} | {0.29} | Production ASGI runner |
| ORM | {sqlalchemy} | {2.x} | Database abstraction |
| Migrations | {alembic} | {1.x} | Schema migration management |
| Auth | {python-jose / authlib} | {x.x} | JWT encoding/decoding |
| Validation | {pydantic} | {v2} | Request/response schemas |
| HTTP client | {httpx} | {0.27} | Async external API calls |
| Testing | {pytest + pytest-asyncio} | {8.x} | Unit and integration tests |
| Linting | {ruff} | {0.4} | Fast Python linter |
| Formatting | {black} | {24.x} | Code formatter |
| Observability | {opentelemetry-sdk} | {1.x} | Tracing and metrics |

### Frontend
| Category | Library | Version | Purpose |
|----------|---------|---------|---------|
| UI framework | {react} | {18.x} | Component model |
| State management | {zustand / redux-toolkit} | {x.x} | Global state |
| Data fetching | {tanstack-query} | {5.x} | Server state, caching |
| HTTP client | {axios / fetch} | {—} | API calls |
| Forms | {react-hook-form} | {7.x} | Form state and validation |
| Validation | {zod} | {3.x} | Schema validation |
| Styling | {tailwindcss} | {3.x} | Utility-first CSS |
| Testing | {vitest + testing-library} | {x.x} | Component and unit tests |
| E2E testing | {playwright} | {1.x} | End-to-end browser tests |

---

## Infrastructure

### Cloud & Hosting
- **Cloud Provider:** {AWS / GCP / Azure}
- **Compute:** {ECS Fargate / Cloud Run / App Service — or: EC2 / GKE / AKS}
- **Database hosting:** {RDS / Cloud SQL / Azure Database}
- **CDN:** {CloudFront / Cloud CDN / Azure CDN}
- **Object storage:** {S3 / GCS / Azure Blob}

### Containerization
- **Docker:** All services containerized; multi-stage builds for production
- **Compose:** `docker-compose.yml` for local development
- **Registry:** {ECR / GCR / ACR}
- **Orchestration:** {ECS / GKE / AKS} — or: no orchestration for simple deployments

### CI/CD
- **Pipeline:** {GitHub Actions / GitLab CI / CircleCI}
- **Stages:** lint → test → build → deploy-staging → deploy-prod
- **Branch strategy:** {trunk-based: merge to `main` triggers staging; tag triggers prod}
- **Rollback:** {previous task definition / image tag}

### Environments
| Environment | Purpose | Deployment Trigger |
|-------------|---------|-------------------|
| local | Development | Manual |
| staging | Integration testing | Push to `main` |
| production | Live traffic | Tagged release |

### Secrets Management
- **Tool:** {AWS Secrets Manager / HashiCorp Vault / GCP Secret Manager}
- **Rule:** No secrets in code, `.env` files committed to repo, or logs

---

## Coding Standards

### Backend
- **Style guide:** PEP 8, enforced by `ruff` + `black`
- **Type hints:** Required on all public functions and method signatures
- **Docstrings:** Google-style docstrings on all public modules, classes, and functions
- **Error handling:** All exceptions must be caught at service boundaries; never let raw exceptions reach API responses
- **Naming:** `snake_case` for variables/functions; `PascalCase` for classes; `UPPER_SNAKE` for constants

### Frontend
- **Style:** ESLint + Prettier; config committed to repo
- **Types:** TypeScript strict mode; no `any` without explicit justification comment
- **Components:** Functional components only; hooks for state and side effects
- **Naming:** `PascalCase` for components; `camelCase` for functions/variables; `kebab-case` for file names

### Shared
- **Commit messages:** Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`)
- **PR size:** Target <400 LOC changed per PR; larger PRs require decomposition
- **Test coverage target:** {80%} minimum on business logic; E2E for all critical user paths

---

## Security Design

- **Authentication:** {JWT Bearer tokens / Session cookies / OAuth2 PKCE}
- **Authorization:** {RBAC — roles defined in `specs/knowledge.md`}
- **Transport:** HTTPS only; HSTS headers; no mixed content
- **Input validation:** All inputs validated at API boundary via Pydantic / Zod schemas; never trust client data
- **Secrets:** Injected via environment at runtime; rotated {quarterly / on breach}
- **Dependencies:** Automated vulnerability scanning via {Dependabot / Snyk}
- **PII handling:** {Describe what PII is collected, where it lives, and how it's protected}

---

## Observability

- **Logging:** Structured JSON to stdout; ingested by {CloudWatch / Datadog / Loki}
- **Log levels:** `ERROR` for exceptions, `WARN` for degraded states, `INFO` for business events, `DEBUG` for development only
- **Tracing:** OpenTelemetry; trace IDs propagated in all request headers and logs
- **Metrics:** {Prometheus / CloudWatch Metrics} — track request latency, error rates, queue depths
- **Alerting:** {PagerDuty / OpsGenie} — SLO breach, error rate spike, payment failure spike
- **Dashboards:** {Grafana / Datadog} — one dashboard per pod showing pod-owned KPIs

---

## Changelog

| Date | Version | Author | Summary |
|------|---------|--------|---------|
| {Date} | 1.0 | {Name} | Initial version |
