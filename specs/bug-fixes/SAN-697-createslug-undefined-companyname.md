---
id: SAN-697
title: "createSlug throws when companyName is undefined (profile menu link)"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-697
sentry:
  - SC-SAAS-FRONTEND-CM
repos: [frontend]
commit: sc-saas-frontend@b0beac84 (branch ai_native_setup_vishali, pushed)
created: 2026-09-08
updated: 2026-09-08
---

# SAN-697 — createSlug crashes on non-string input

## Root cause
`createSlug()` in `src/app/shared/utils/common-methods.ts` called `slugify(name, ...)` with no guard. `slugify` throws `TypeError: slugify: string argument expected` when `name` isn't a string. In the captured event, `user-profile-menu.component.ts:152` called `createSlug(res.companyName)` where `res.companyName` was `undefined` for this user's profile record.

## Fix
Added an early guard in `createSlug`: `if (!name || typeof name !== 'string') return '';` before the `slugify()` call, so a missing/non-string name now degrades to an empty slug segment instead of throwing. `createSlug` is a shared utility (also used for missing-fields URL building in `common-methods.ts`'s `getMissingFieldsMap`), so the guard is general-purpose rather than special-cased to the profile menu caller.

## Blast radius
`src/app/shared/utils/common-methods.ts` only — a pure utility function, no template/DTO/contract changes. Callers: `user-profile-menu.component.ts` (profile link) and `getMissingFieldsMap` (custom-form missing-field URLs).

## Verification
`npx tsc --noEmit -p tsconfig.json` — no new errors on the touched file (pre-existing unrelated errors exist in third-party CometChat spec files). No automated test added yet — proposed a `common-methods.spec.ts` case in the Linear comment; holding off on writing it until the user confirms (per the bug-fix workflow's "propose test, wait for go-ahead" step). Committed and pushed as `sc-saas-frontend@b0beac84`. Linear moved to Done; Sentry SC-SAAS-FRONTEND-CM marked resolved with a comment referencing the commit.
