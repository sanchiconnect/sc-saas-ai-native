---
id: SAN-376
title: MetaMask/wallet-extension JSON-RPC noise reaching Sentry
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-376
sentry:
  - SC-SAAS-FRONTEND-90
repos: [frontend]
commit: sc-saas-frontend@c0638d20 (branch ai_native_setup_aman)
created: 2026-08-19
updated: 2026-08-19
---

# SAN-376 — MetaMask JSON-RPC Sentry noise

## Root cause
Actual error: `UnhandledRejection: {code: -32603, message: "Internal JSON-RPC error."}` on `/auth/login`, mechanism `onunhandledrejection`, zero first-party stack frames. Code `-32603` is the standard Ethereum JSON-RPC "Internal error" — a browser crypto-wallet extension (e.g. MetaMask) injecting `window.ethereum` and rejecting a promise, unrelated to app code.

## Fix
Added a check at the top of the existing `beforeSend` hook in `main.ts`'s `Sentry.init` that drops any event whose exception value contains both `-32603` and `JSON-RPC`, returning `null` to suppress it before the existing PII-scrubbing logic runs.

## Blast radius
None — grepped the whole `src` tree for `JSON-RPC`/`-32603`; no first-party app code throws or logs either string, so the filter can't accidentally suppress a real app error.

## Verification
`tsc --noEmit` clean.
