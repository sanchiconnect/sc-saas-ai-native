---
id: SAN-577
title: Cannot read 'message' of null — startup.effect
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-577
sentry:
  - SC-SAAS-FRONTEND-3X
repos: [frontend]
commit: e10a960c (branch ai_native_setup_vishali) — pre-existing (SAN-474), verified only
created: 2026-09-03
updated: 2026-09-03
---

# SAN-577 — message-of-null in startup.effect

## Root cause
Same class as SAN-212/SAN-572 — a `catchError` reading `.message` off a possibly-null error object, this time in the sibling `startup.effect` (not `startup.dashboard.effects`).

## Finding — already fixed
Commit `e10a960c` (SAN-474, the same shared `httpFaultMessage()` rollout described in SAN-572's doc) also covers this file. Confirmed all 5 `catchError` sites in `startup.effect.ts` already use `httpFaultMessage(err)` — grep for raw `.message` access in the file: no matches.

No new change made in this session — verified only.

## Blast radius
None — no new change.

## Verification
`git log`/`git show --stat` on `e10a960c` confirmed the fix's presence; grep confirmed no raw `.message` reads remain.

## Related
SAN-474, SAN-572 (sibling file, same commit).
