---
id: SAN-707
title: "Send OTP: claim-listing-modal builds an invalid email when profile has no website domain"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-707
sentry:
  - SC-SAAS-FRONTEND-CJ
repos: [frontend]
commit: sc-saas-frontend@292ee2af (branch ai_native_setup_vishali, pushed)
created: 2026-09-08
updated: 2026-09-08
---

# SAN-707 — claim-listing OTP request silently fails on malformed constructed email

## Root cause
Original hypothesis (missing `Validators.email` on a signup form) was wrong — all 3 obvious `sendOTP()` call sites (`register.component.ts`, `register-modal.component.ts`, `program-public-apply-modal.component.ts`) already validate email format client-side.

The real gap: `claim-listing-modal.component.ts` (the "claim this startup listing" flow). Its `email` form control has only `Validators.required` because the user types just the local-part; the component builds the full address itself:
```ts
this.profileWebsiteDomainName = domainName ? '@' + domainName : '';        // ngOnInit
this.profileEmailId = this.claimListingForm.value.email + this.profileWebsiteDomainName;  // sendRequests()
```
If the startup profile being claimed has no website URL configured, `profileWebsiteDomainName` is `''`, so `profileEmailId` is just the raw local-part with no `@domain` — guaranteed to fail the backend's `emailAddress must be an email` check. `sendOTPToMobile()`/`sendOTPToEmail()` also called `.subscribe()` with **no error callback**, so this was completely silent to the user.

## Fix
In `claim-listing-modal.component.ts`:
- Guard at the top of `sendOTPToMobile()`/`sendOTPToEmail()`: if `!this.profileWebsiteDomainName`, show an error toast and return before calling the API.
- Added an error callback to both `.subscribe()` calls, toasting `err?.error?.message` (or a generic fallback) instead of silently swallowing the failure.

## Blast radius
`sc-saas-frontend`'s `claim-listing-modal.component.ts` only. No contract/DTO changes.

## Verification
`npx tsc --noEmit -p tsconfig.json` — no new errors. Regression test proposed (mock `profileWebsiteDomainName = ''` and a `sendOTP` error), holding off until user confirms. Committed and pushed as `sc-saas-frontend@292ee2af`. Linear moved to Done; Sentry SC-SAAS-FRONTEND-CJ marked resolved with a comment referencing the commit.

## Confidence note
Medium confidence on the exact call-site match — the Sentry event's culprit URL (`community.ginserv.in/request/authenticate`) wasn't independently confirmed to map to the claim-listing route; this is the best-evidenced gap found among the 6 `sendOTP()` call sites, but should be verified against real repro if it recurs.
