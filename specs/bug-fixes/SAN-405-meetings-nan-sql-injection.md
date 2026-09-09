---
id: SAN-405
title: "QueryFailedError: Unknown column 'NaN' — unparameterized raw SQL in getUserMeetingsByDate"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-405
sentry:
  - SC-SAAS-BACKEND-B
repos: [backend]
commit: sc-saas-backend@d9ec7f0a (branch ai_native_setup_aman)
created: 2026-08-20
updated: 2026-08-20
---

# SAN-405 — unparameterized raw SQL in getUserMeetingsByDate

## Root cause
`meetings.repository.ts`'s `getUserMeetingsByDate` built its `WHERE`/`LIKE` clauses via raw string template interpolation instead of TypeORM's parameterized `:param` binding used everywhere else in this repository. If `userId` is ever `NaN`, the literal bareword `NaN` is spliced unquoted into the SQL, which MySQL parses as an unquoted column reference. The same unescaped-interpolation shape also applied to `date` — an unparameterized-raw-SQL pattern independent of this specific bug.

## Fix
Rewrote both conditions to use bound parameters (`qb.where('user.id = :userId', { userId })`, `.andWhere('meetings.date LIKE :date', { date })`), preserving exact existing match semantics (no wildcards were present before, none added now).

## Blast radius
Low — single call site (`calendar-availability.service.ts`, `getOtherUserMeetingsByDate`), behavior-preserving for valid input.

## Verification
`tsc --noEmit` clean; `npm run build` clean; lint shows only pre-existing unrelated warnings. A manual call to the other-user-meetings-by-date endpoint was not performed in this session.
