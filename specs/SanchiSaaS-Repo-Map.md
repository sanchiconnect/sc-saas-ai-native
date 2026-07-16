# SanchiSaaS — Repo Map

**Document Type:** Internal Architecture Reference
**Product:** SanchiSaaS — Incubator & Accelerator Management Platform
**Date:** 2026-07-16
**Companion documents:** workspace `CLAUDE.md` (blast-radius graph + 6 cross-repo invariants), `knowledge.md` §9

---

## Purpose

A one-page reference for "what is each repo for, what does it own, what does it depend on, and where does
the workspace boundary actually sit." Eight repos live in this workspace folder (seven product repos plus
this orchestration root); four more exist in a separate sibling workspace, `SanchiPowerpitch`, cloned
outside this folder entirely.

---

## How it fits together

```
sc-saas-ai-native (this workspace root — docs & spec process, no runtime code)

sanchiconnect-saas-tenants (cockpit / control plane)
        │  verify_tenant / tenant-settings         │  bootstrap config + ecosystem
        ▼                                          ▼
sc-saas-frontend (end-user PWA)          sc-saas-backend (business API)
        │ business calls via apiUrl               │                    │
        └─────────────────────────────────────────┘                    │
                                                                        │ SMS/email/video/chat/url/docs
sc-saas-admin (accelerator staff panel)                                ▼
        │ api_server_url REST → backend                sc-saas-3rdparty-webservices (integration gateway)
        │ reads tenant DB directly → tenants
        │ score runs, HTTP → ai-startups-analyzer (LLM scoring service)

sanchiconnect-saas-tenants-admin (platform operator UI)
        │ reads + writes DB directly → tenants (shared DB, no API)

sc-saas-backend ──x-hostname + JWT──▶ power-pitch-sanchiconnect-api (external, SanchiPowerpitch workspace)
```

Solid edges are live runtime calls; the `tenants` ↔ `tenants-admin` and `admin` → `tenants` edges are direct
shared-database reads/writes, bypassing any API. `tenants` sits at the root — a change there can reach
`frontend`, `admin`, and (through `backend`) everything `backend` touches.

---

## Repo → purpose → owns → depends on

| Repo | Stack | Purpose | Owns | Depends on |
|---|---|---|---|---|
| `sc-saas-ai-native` (this root) | docs only | Orchestration & docs — the constitution, cross-repo specs (`api`/`database`/`design`/`knowledge.md`), the spec-authoring workflow, Linear automation. | The spec process + the 6 cross-repo invariants. No runtime code. | Reads all 7 product repos, read-only, for documentation. |
| `sanchiconnect-saas-tenants` | NestJS 9 · TypeORM · MySQL | Control-plane cockpit — tenant provisioning, source of truth for feature flags. | Flag names (`TenantUsersEntity`) + the `verify_tenant`/`tenant-settings` contract. | None upstream in this graph. Shares its DB directly with `sanchiconnect-saas-tenants-admin`. |
| `sc-saas-backend` | NestJS 8 · TypeORM · MySQL | The business API every client consumes — controllers, DTOs, tenant-scoped logic. | The API contract (`api/v{n}`, class-validator DTOs). | `tenants` (bootstrap-loaded config) · `sc-saas-3rdparty-webservices` (SMS/email/video/chat/url/docs) · `power-pitch-sanchiconnect-api` (external, invariant #6). |
| `sc-saas-frontend` | Angular 13 · NgRx · PWA | The end-user product surface — what startups, mentors, and investors actually use. | Nothing cross-repo — pure consumer. | `tenants` (`verify_tenant`, receives `apiUrl`) · `sc-saas-backend` (all business calls via that `apiUrl`). |
| `sc-saas-admin` | PHP · Medoo · sparkAdminTpl | Admin panel for accelerator staff — applications, cohorts, broadcasts, bulk actions, AI-scoring orchestration. | Nothing cross-repo — but reads the tenant DB directly for some queries, bypassing backend. | `sc-saas-backend` (`api_server_url` REST) · `tenants` (direct DB reads) · `ai-startups-analyzer` (triggers score runs). |
| `ai-startups-analyzer` | Python · FastAPI · SQLAlchemy | LLM-based startup application scoring — OpenAI, Anthropic, or Gemini via `DEFAULT_PROVIDER`. | The 0–500→1–5 scoring scale — a frozen cross-repo contract. | None; leaf node. Called by `sc-saas-admin`, never calls back (admin polls). |
| `sc-saas-3rdparty-webservices` | NestJS 9 · stateless | Integration gateway — centralizes every third-party call in one place. | Nothing cross-repo — stateless proxy. | None; leaf node. Called by `sc-saas-backend`; also directly by `sc-saas-admin` for 2 routes (undocumented in the original blast-radius graph — see `knowledge.md` §3). Never calls into SanchiSaaS itself. |
| `sanchiconnect-saas-tenants-admin` | PHP · Medoo | Platform-operator UI over the tenants DB — provisioning, roles, global settings, AI-credits management, tenant data export. | Nothing cross-repo. | None via REST from `tenants` — shares the tenants DB directly (reads + writes `tenant_users`, `organizations`, `spa_*`). Also makes direct, unconditional outbound calls to `sc-saas-backend` (`PATCH .../saas/settings` on every `tenant_users` edit). |

---

## What you're not seeing yet: SanchiPowerpitch is a sibling workspace, not a folder here

Four more repos exist under a separate workspace root, `sc-powerpitch-ai-native`, cloned at
`/Users/mac/Desktop/Work/SanchiPowerpitch` — a sibling of this `SanchiSaaS` folder, not nested inside it.
Confirmed directly on disk, 2026-07-16 (each has its own `.git`):

- `power-pitch-sanchiconnect-api`
- `power-pitch-sanchiconnect-frontend`
- `power-pitch-sanchiconnect-admin`
- `power-pitch-partners`

**Exactly one contract crosses the boundary between the two workspaces**: `sc-saas-backend`'s
`PowerPitchExternalService` calls PowerPitch's `/v1/externals/*` endpoints — tenant identity travels via an
`x-hostname` header, and a session token from `create-session` is cached and refreshed 10 minutes before it
expires. PowerPitch never calls back into SanchiSaaS. The other three PowerPitch repos (frontend, admin,
partners) have no confirmed contract with anything in this workspace.

> **Correction to an earlier internal reference (2026-07-15):** an earlier version of this repo-map material
> claimed `power-pitch-sanchiconnect-admin` "had no meaningful commits yet." Checked directly via `git log`
> on 2026-07-16 — this was wrong, not just stale: the repo has 12 commits, including real feature work
> ("plans management", "add partner user", email-template changes) dated 2022-12-21 through 2023-04-21, then
> a three-year gap before a single docs-only commit (CLAUDE.md + module specs) landed 2026-06-19. It has
> genuine historical business logic, just no active development in over three years as of this check —
> don't assume it's an empty/scaffold repo.

Also in this folder, but not part of the graph: `prabs/` holds a third-party "spec-driven-pod-framework"
(SpecPod) that was pulled in, evaluated, and explicitly not adopted — kept for reference, disconnected from
every dependency above.

---

## Sources

- Workspace `CLAUDE.md` (blast-radius graph + 6 cross-repo invariants)
- `knowledge.md` §8 (verification of the `CLAUDE.md` blast-radius graph against all 7 repos' own findings)
  and §9 (SanchiPowerpitch sibling-workspace verification)
- Direct `git log` / filesystem check of `/Users/mac/Desktop/Work/SanchiPowerpitch`, 2026-07-16
