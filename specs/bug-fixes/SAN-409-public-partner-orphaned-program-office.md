---
id: SAN-409
title: Public partner profile page crashes on an orphaned program-office member
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-409
sentry:
  - SC-SAAS-BACKEND-1V
repos: [backend]
commit: sc-saas-backend@d9ec7f0a (branch ai_native_setup_aman)
created: 2026-08-20
updated: 2026-08-20
---

# SAN-409 — orphaned program-office member crashes the public partner profile

## Root cause
`partner.service.ts`'s `getPublicPartner` — a **public, unauthenticated** endpoint — builds `peopleList` from a LEFT JOIN on `program_office`. A `PROGRAM_OFFICE`-type user with no matching `ProgramOfficeMembersEntity` row (orphaned/soft-deleted record, or a race between user creation and profile creation) yields `user.program_office === null`, and the unguarded `user.program_office.uuid` access crashed the entire request for anyone viewing that partner's public page.

## Fix
Skip (don't push) any user whose `program_office` is null, instead of crashing. The rest of the public profile (partner details, startups list) still renders correctly; only the orphaned member is omitted from the people list.

## Blast radius
None for well-formed data — output shape for `peopleList` is unchanged; only removes entries that currently 500 the whole endpoint. Public/unauthenticated surface, so this was reachable by anyone — highest real-world exposure of this batch, hence Urgent priority.

## Verification
`tsc --noEmit` clean; `npm run build` clean; lint shows only pre-existing unrelated warnings. Finding/creating a program-office user with no linked `program_office` row to confirm the page now renders was not performed in this session.
