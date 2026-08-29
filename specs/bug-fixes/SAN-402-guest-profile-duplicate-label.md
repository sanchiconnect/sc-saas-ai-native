---
id: SAN-402
title: getProfileDataByEmailOfGuestUser overwrites real answers with blank duplicate-label fields
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-402
sentry:
  - SC-SAAS-BACKEND-M
  - SC-SAAS-BACKEND-J
  - SC-SAAS-BACKEND-H
  - SC-SAAS-BACKEND-1E
  - SC-SAAS-BACKEND-W
  - SC-SAAS-BACKEND-T
  - SC-SAAS-BACKEND-S
  - SC-SAAS-BACKEND-R
  - SC-SAAS-BACKEND-K
  - SC-SAAS-BACKEND-V
  - SC-SAAS-BACKEND-1N
  - SC-SAAS-BACKEND-1Z
  - SC-SAAS-BACKEND-1Y
  - SC-SAAS-BACKEND-13
  - SC-SAAS-BACKEND-12
repos: [backend]
commit: sc-saas-backend@d9ec7f0a (branch ai_native_setup_aman)
created: 2026-08-20
updated: 2026-08-20
---

# SAN-402 — getProfileDataByEmailOfGuestUser duplicate-label overwrite

## Root cause
`src/modules/user/user.service.ts` (`getProfileDataByEmailOfGuestUser`) built a `mappedData` object keyed by form-field display **label**, unconditionally overwriting on every duplicate label (last-write-wins) regardless of whether the new value was blank. 343+ occurrences across 15 distinct labels, first seen 2026-08-01, still firing daily at the time of investigation.

**History:** SAN-191/192/193 (2026-08-03) "fixed" 3 of these specific labels by patching the tenant's form definitions, not the code — the overwrite logic itself was untouched, which is why new labels kept triggering the same warning weeks later.

## Why not key by field.key instead (the "obvious" fix)?
Checked the cross-repo contract first: `sc-saas-frontend`'s guest-profile prefill (`guest-profile-utils.ts` — `resolveGuestFieldValue`/`GUEST_LABEL_KEYS`/`RULES`) reads this response **by label string** to prefill CFA application forms. Re-keying to `field.key` would have silently broken that prefill feature — invisible from the backend alone. Kept label-keying intact.

## Fix
`user.service.ts` — changed the merge policy from "last non-undefined value wins" to "first non-empty value wins": a later duplicate-label field only overwrites if the existing value was empty/null. The warning now only fires on genuinely conflicting non-empty values, not on every harmless collision.

## Blast radius
None — `dataByKey` (the collision-free, key-based map already returned alongside `data`) is untouched; `data`'s shape and label-keying are unchanged, only which value wins on collision.

## Verification
`tsc --noEmit` clean; `npm run build` clean; `eslint` shows only pre-existing unrelated warnings. No automated test suite covers this path (no guardian/test-scaffolding skill set up in this workspace yet) — manual repro with a tenant form containing a genuine duplicate label was not run in this session.
