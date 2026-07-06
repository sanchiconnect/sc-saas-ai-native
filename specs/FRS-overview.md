---
type: frs-index
updated: 2026-07-06
---

# Functional Requirement Specification — SanchiSaaS (Frontend + Admin)

This is the index for the two-part Functional Requirement Specification covering the end-user PWA and the tenant admin panel:

- **[specs/FRS-sc-saas-frontend.md](FRS-sc-saas-frontend.md)** — `sc-saas-frontend` (Angular 13 PWA). 6 domains, ~45 modules: Authentication & Account, Startups/Programs/Applications, Challenges & Hiring, Community/Networking/Communication, Learning/Events/Content, Facilities/Finance/Certificates/Support.
- **[specs/FRS-sc-saas-admin.md](FRS-sc-saas-admin.md)** — `sc-saas-admin` (PHP tenant admin panel). 6 domains, 22+ modules: Foundation/Auth/CRUD, Application & Program Lifecycle, Learning/Events/Community, Finance & Memberships, Outreach/Content/Certificates/Metrics/Reporting, Facilities/Partners/Forms/Integrations/System Admin.

## How these were built

Both documents were derived directly from the current codebase (components, routing, services, controllers) via parallel research agents, one per functional domain, rather than from design documents — so they describe actual behavior, including known gaps. The admin document additionally drew on a pre-existing suite of 22+ code-verified technical module specs (`sc-saas-admin/modules/*/module.spec.md`, indexed at `specs/admin-module-specs-index.md`) and re-expressed them as functional flows.

## Reading guide

Each functional requirement follows the pattern `FR-<id>: <title> — <trigger> → <steps> → <outcome>`. Every module section also lists its **Dependencies** (backend endpoints, feature flags, other modules) and, where relevant, **Notable business rules / edge cases** — these capture real current behavior (including bugs and inconsistencies uncovered during research), not intended design. Treat them as a map of where guarantees are weaker than a casual read of the UI would suggest, not as a to-do list to fix inline.

## What's out of scope here

This FRS pair covers only `sc-saas-frontend` and `sc-saas-admin`, per the requested scope. It does not cover:
- `sc-saas-backend` (the API contract both consume) — see `specs/backend-module-specs-index.md`.
- `sanchiconnect-saas-tenants` (owns feature-flag names and the tenant-verification contract) — see `specs/tenants-module-specs-index.md`.
- `ai-startups-analyzer`, `sc-saas-3rdparty-webservices`, `sanchiconnect-saas-tenants-admin` — see their respective spec indexes.

## Cross-repo caution

Per the workspace constitution, feature-flag names are owned by `sanchiconnect-saas-tenants` and the API contract is owned by `sc-saas-backend`. Both FRS documents reference flags and endpoints as consumed by the frontend/admin — if you're about to rename, remove, or reshape one of them, run `/trace-flag` or `/audit-contract` first rather than trusting this FRS as the source of truth for the other side of that contract.
