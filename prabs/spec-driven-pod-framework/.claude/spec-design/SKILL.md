---
name: spec-design
description: "Create, review, and update the technical design specification (specs/design.md) for a program. Activate whenever the user says 'update design spec', 'review technical design', 'choose tech stack', 'define architecture', 'select frameworks', 'what libraries should we use', 'document the design', 'update specs/design.md', or makes decisions"
---

**name:** spec-design

**description:** Create, review, and update the technical design specification (specs/design.md) for a program. Activate whenever the user says "update design spec", "review technical design", "choose tech stack", "define architecture", "select frameworks", "what libraries should we use", "document the design", "update specs/design.md", or makes decisions about programming languages, frameworks, infrastructure, tooling, or architectural patterns. Always reads specs/program.md and specs/knowledge.md first. This is the authoritative technical blueprint — all AI pods must implement consistently with it. Use this skill before any coding begins and whenever technology decisions change.


# Spec: Technical Design

## Purpose

Define and maintain the **technical blueprint** of the program — the programming language, frameworks, libraries, infrastructure, architectural patterns, and tooling decisions that all pods must follow. This spec prevents pods from making independent, conflicting technology choices.

`specs/design.md` is consumed by:
- All AI pod coding sessions
- `spec-api` skill (framework choices, auth patterns)
- `spec-database` skill (ORM, migration tools)
- CLAUDE.md (coding conventions)

---

## Pre-flight

### Step 0 — Client Design Preferences

Check for `context/design-preferences.md`.

**If found:** Read it and extract answers to Groups 1–4 (language, runtime, frameworks, infrastructure, standards). Present a summary to the user:

```
## Design Preferences Detected — context/design-preferences.md

Language & Runtime:   [inferred value or "not specified"]
Frameworks:           [inferred value or "not specified"]
Infrastructure:       [inferred value or "not specified"]
Standards:            [inferred value or "not specified"]

Confirm these or tell me what to change before I proceed.
```

Wait for confirmation. Skip elicitation questions for any group already answered. Only ask about gaps.

**If not found:** Ask once — *"Would you like to provide a design preferences document in `context/design-preferences.md` before we proceed? (Yes / No)"*
- **Yes** → wait for the user to drop the file or paste content, then process it as above.
- **No** → proceed with full elicitation questions below.

---

### Steps 1–3

1. Read `specs/program.md` — extract system domains, NFRs, pod structure, compliance requirements
2. Read `specs/knowledge.md` if it exists — extract entity complexity and workflow needs
3. Check if `specs/design.md` exists — if yes, **Review Mode**; if no, **Initialize Mode**

---

## Initialize Mode

Elicit in four groups:

### Group 1 — Language & Runtime
- What is the primary programming language for backend? (Python, Node.js, Go, Java, etc.)
- What is the primary language for frontend? (TypeScript/React, Vue, Swift, Kotlin, Flutter, etc.)
- Runtime targets: server, serverless, edge, mobile native, or mobile web?

### Group 2 — Frameworks & Libraries
- **Backend framework:** FastAPI, Django, Express, Spring Boot, etc.?
- **Frontend framework:** React, Next.js, Vue, React Native, Flutter, etc.?
- **ORM / Data access:** SQLAlchemy, Prisma, TypeORM, etc.?
- **Auth:** JWT, OAuth2, session-based, third-party (Auth0, Cognito)?
- **Testing:** pytest, Jest, Vitest, Playwright, etc.?
- **Key domain libraries:** payment SDKs, geocoding, caching, queuing?

### Group 3 — Infrastructure & Deployment
- Cloud provider: AWS, GCP, Azure, self-hosted?
- Containerization: Docker, Kubernetes?
- CI/CD: GitHub Actions, GitLab CI, CircleCI?
- Environments: dev / staging / prod?
- Secrets management: Vault, AWS Secrets Manager, env files?

### Group 4 — Standards & Conventions
- Code style / linting: Black + Ruff, ESLint + Prettier, etc.?
- API style: REST, GraphQL, gRPC?
- Logging and observability: structured JSON logs, Datadog, Sentry, OpenTelemetry?
- Branch strategy: trunk-based, Gitflow?
- Documentation standard: docstrings, JSDoc, OpenAPI?

---

## Review Mode

1. Load current `specs/design.md`
2. Identify any technology decisions that conflict with NFRs or new program constraints
3. Ask: "Any new technology decisions or library upgrades since last update?"
4. Make surgical updates; append a `## Changelog` entry

---

## Output: specs/design.md

See `references/design-template.md` for the full canonical structure.

### Section Summary
| Section | Content |
|---------|---------|
| System Architecture | Diagram description, layer breakdown, communication patterns |
| Technology Stack | Language, runtime, frameworks per layer |
| Libraries & Dependencies | Grouped by domain (auth, data, testing, observability) |
| Infrastructure | Cloud, containers, CI/CD, environments |
| Coding Standards | Linting, formatting, naming, documentation conventions |
| Security Design | Auth model, secret handling, input validation approach |
| Observability | Logging, metrics, tracing, alerting strategy |
| Changelog | Date-stamped change history |

---

## Execution Steps

1. Read prerequisite specs
2. Detect Initialize vs Review mode
3. Run elicitation or gap review
4. Confirm choices with user (flag any conflicts with NFRs or compliance requirements)
5. Write or update `specs/design.md`
6. Flag downstream specs that need alignment (database ORM choice affects `spec-database`; auth choice affects `spec-api`)

---

## Reference Files
- `references/design-template.md` — Canonical template
- `sample_output/design.md` — Example for mobile checkout program
