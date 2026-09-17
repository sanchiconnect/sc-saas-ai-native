---
id: SAN-702
title: "Login blocked: Startup profile not attached to your account — needs data/account-linkage investigation"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-702
sentry:
  - SC-SAAS-FRONTEND-CY
repos: [frontend]
commit: none — not a frontend code defect
created: 2026-09-08
updated: 2026-09-08
---

# SAN-702 — login blocked by backend business rule, correctly surfaced

## Investigation
The message is correctly surfaced to the user — `login.component.ts:110` toasts `err?.error?.message` on the `login()` catchError path. Not a silent-failure bug. The message itself is a backend-issued business rule (account exists but has no linked startup profile) — could be legitimate (account genuinely has no startup profile) or a data/linkage defect elsewhere (`sc-saas-backend` / `sanchiconnect-saas-tenants`).

No frontend code change applies. Flagged for a data check outside this ticket's scope — if the affected account should have a startup profile, a follow-up `Repo: Backend` or `Repo: Tenants` issue is warranted (not filed here, since it requires a data investigation this session couldn't perform).

## Blast radius
None — no change made.

## Confidence note
Low confidence either way without a data-level check on the specific account; documented as an open question rather than guessed at.
