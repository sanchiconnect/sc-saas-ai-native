---
id: SAN-529
title: Unhandled 500 on avatar/logo file upload in dynamic forms
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-529
sentry:
  - SC-SAAS-FRONTEND-8
repos: [frontend]
commit: sc-saas-frontend@84530dae (branch ai_native_setup_vishali, not yet pushed to origin as of 2026-08-26)
created: 2026-08-26
updated: 2026-08-26
---

# SAN-529 — unhandled 500 on avatar/logo upload

## Root cause
`FormFieldComponent.uploadAvtarImage()` awaits `this.uploadFile(file)` with no `try/catch`. `uploadFile()` delegates to `FormManagementService.updatePublicFile()`/`updateFile()`, which already `catchError`s the HTTP failure, toasts it, and re-throws — so an unguarded `await` on a backend 500 becomes an unhandled promise rejection, matching this Sentry error exactly (106 events / 65 users, highest-impact open issue in the project).

This is the second call site of `uploadFile()` in the same component. The first, `selectFileDroppedHandler()`, already wraps its `await this.uploadFile(file)` in a `try/catch`, with a comment explicitly citing this same defect class as already fixed once under SC-SAAS-FRONTEND-2M/2V — that fix was never extended to this second site.

Secondary bug in the same block: because `ngxLoaderService.stop()` sat after the unguarded `await`, a failed upload also left the loading spinner stuck forever — the exact "loader stops on success, error, and navigation-away" requirement flagged as an acceptance criterion on the unrelated ngx-ui-loader ticket (SAN-433).

## Fix
Wrapped the upload + patch/emit logic in `try/catch`, matching the established pattern and comment style from `selectFileDroppedHandler()`. Moved `ngxLoaderService.stop()` into a `finally` so it always runs.

## Blast radius
None — no behavior change on the success path. Diff is isolated to the one method, mirroring an already-proven pattern in the same file.

## Verification
`tsc --noEmit` clean. No test suite configured for this repo; type-check + code-review against the existing, already-proven try/catch pattern in the same file was the strongest verification available. Committed (`84530dae`) but not yet pushed to `origin/ai_native_setup_vishali` — checked via `git fetch` + `git rev-list --left-right --count`, local branch is 1 commit ahead of the remote.
