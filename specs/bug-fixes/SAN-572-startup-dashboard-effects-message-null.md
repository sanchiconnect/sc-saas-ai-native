---
id: SAN-572
title: Cannot read 'message' of null — startup.dashboard.effects
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-572
sentry:
  - SC-SAAS-FRONTEND-4E
repos: [frontend]
commit: e10a960c (branch ai_native_setup_vishali) — pre-existing (SAN-474), verified only
created: 2026-09-03
updated: 2026-09-03
---

# SAN-572 — message-of-null in startup.dashboard.effects

## Root cause
Same class as SAN-212 (`investor.dashboard.effect`, Done): a `catchError` reading `.message` off a possibly-null error object.

## Finding — already fixed
SAN-212's original guard was later superseded by a broader commit `e10a960c` (SAN-474), which introduced a shared helper `src/app/shared/utils/http-fault.util.ts` → `httpFaultMessage(err)` and rolled it out to `catchError((err: HttpErrorResponse) => of(new XFault(httpFaultMessage(err))))` across 16 effects files, explicitly listing `SC-SAAS-FRONTEND-7R, -6W, -7C, -81, -6Y` in its commit message. Confirmed all 4 `catchError` sites in `startup.dashboard.effects.ts` already use `httpFaultMessage(err)` — grep for raw `.message` access in the file: no matches.

No new change made in this session — verified only.

## Blast radius
None — no new change.

## Verification
`git log`/`git show --stat` on `e10a960c` confirmed the fix's presence; grep confirmed no raw `.message` reads remain.

## Related
SAN-474 (the superseding shared-helper fix), SAN-212 (original single-file fix), SAN-577 (sibling file, same commit).
