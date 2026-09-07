---
id: SAN-626
title: "NG01002: individual-investor-edit-form setValue() missing field fallbacks"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-626
sentry:
  - SC-SAAS-FRONTEND-5V
  - SC-SAAS-FRONTEND-5W
repos: [frontend]
commit: sc-saas-frontend@fd569395 (branch ai_native_setup_vishali)
created: 2026-09-07
updated: 2026-09-07
---

# SAN-626 — individual-investor-edit-form setValue() missing field fallbacks

## Root cause
`individual-investor-edit-form.component.ts:206` calls `this.organizationForm.setValue({...})` with destructured API-response fields (`aboutUs`, `displayWebsite`, `keyInvestments`, `linkedinUrl`, `askForConnectionDocument`, `organizationName`, `twitterUrl`, `portfolioSize`) and no fallback. Angular's `setValue()` requires every control key present and non-`undefined` — any one of these being `undefined` in the API response throws NG01002. `getTransformedVal()` also implicitly returns `undefined` for falsy input.

SC-SAAS-FRONTEND-5W is the identical bug (same line/stack) — Sentry only split it into a second group because production strips field-level detail from the message.

## Fix
Added `?? ''` fallbacks to all 7 destructured fields, and `?? ''` on `getTransformedVal(portfolioSize)`.

## Blast radius
None — purely additive fallbacks for undefined API fields; valid data flows through unchanged.

## Verification
`npx tsc --noEmit -p tsconfig.app.json` clean. No test suite change — no automated regression coverage added.
