---
id: SAN-696
title: "DecimalPipe crash patching financial-details form with non-numeric value (NG02100)"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-696
sentry:
  - SC-SAAS-FRONTEND-CX
repos: [frontend]
commit: none — already fixed, see Investigation
created: 2026-09-08
updated: 2026-09-08
---

# SAN-696 — DecimalPipe NG02100 crash, already fixed (stale event)

## Investigation
`financials-details.component.ts`'s `numberFormatterArray` valueChanges handler (lines 218-231) already wraps `decimalPipe.transform()` in a `try/catch` that falls back to the raw value instead of throwing. This guard was added by commit `8b53d449` ("SAN-524: DecimalPipe NG02100 crash on non-numeric paste into number fields", merged 2026-08-26), which touched this exact file (and 7 others, see [[SAN-701]] below).

The Sentry event carried `environment: local`, `release: sc-saas-frontend@unknown` — no baked-in release tag, consistent with a local/unbuilt dev session that predates or excludes the SAN-524 fix, not a fresh regression.

No code change made — no defect exists in the current `ai_native_setup_vishali` branch.

## Blast radius
None.

## Verification
Read current source of `financials-details.component.ts`; confirmed guard present. Cross-referenced against commit `8b53d449`'s diff.

## Related
[[SAN-701]] (same root cause, sibling component `ongoing-commitments-list`, same SAN-524 fix commit) — filed and closed together as part of a 13-issue Sentry triage batch (SAN-696 through SAN-708).

## Confidence note
High confidence — the fix commit is identified by hash and its diff directly covers the affected file/method.
