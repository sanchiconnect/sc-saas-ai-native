---
id: FE-008
title: Payments & Membership
type: feature
status: draft
repos:
  - frontend
  - backend
contracts:
  api:
    - GET api/v1/payments/gateways
    - POST api/v1/payments/create-order
    - POST api/v1/payments/discounted/create-order
    - POST api/v1/payments/paypal/capture-order/:orderId
    - POST api/v1/payments/coupon/verify
    - POST api/v1/payments/coupon/verify/membership
    - POST api/v1/payments/create-transaction
    - GET api/v1/payments/orders
    - GET api/v1/payments/module-pricing/:moduleType/:moduleTypeId
    - GET api/v1/payments/round-pricing/:moduleType/:moduleTypeId/:moduleTypeSubId/:userId
    - GET api/v1/payments/verify/:moduleType/:moduleTypeId/:submissionId/:programRoundsId?
    - GET api/v1/payments/latest-order-status/:moduleType/:userId
    - GET api/v1/payments/previous_order/:moduleType/:moduleTypeId/:userId
    - GET api/v1/payments/applicant_payments/:moduleType/:moduleTypeId/:userId
    - GET api/v1/payments/proforma-invoices/history/:profileType/:profileId
    - GET api/v1/payments/proforma-invoices/:id/render/:profileType/:profileId
    - GET api/v1/payments/easebuzz/verify-status/:txnid
    - POST api/v1/payments/easebuzz/webhook
    - POST api/v1/invoice/generate
    - GET api/v1/memberships
    - GET api/v1/memberships/:id
    - GET api/v1/memberships/types/:profileType
    - GET api/v1/memberships/last/:profileType/:profileId
    - GET api/v1/memberships/history/:profileType/:profileId
    - GET api/v1/memberships/upgrade-request/:currentMembershipTypeId/:profileType/:profileId
    - POST api/v1/memberships/upgrade-request
  flags:
    - payment_gateways
  events: []
tenant_scoped: true
depends_on: []
updated: 2026-06-17
---

# FE-008 — Payments & Membership

## Summary

End-to-end payment and membership lifecycle: gateway selection (Stripe, Razorpay, PayPal, Easebuzz, PayU), order creation and capture, coupon/discount validation, order history, membership plan subscription and tier upgrade, proforma invoice management, and SES delivery of membership certificates. The `CheckoutModule` is a shared inline widget embedded across programs, LMS, events, and membership flows — it is never lazy-loaded as a standalone route.

## Frontend entry points

Module specs:
- `sc-saas-frontend/src/app/modules/payment/module.spec.md`

Routes (lazy-loaded):
- `/payment-gateways` — `PaymentGatewaysComponent` (dev/test harness only — never link from nav)
- `/membership` — `MembershipComponent` (plan picker with embedded `CheckoutComponent`)
- `/account/edit/orders` — `OrderComponent` (paginated order history)
- `/account/edit/membership` — `PurchasedplanComponent` (AuthGuard)
- `/account/edit/membership/upgrade/:membershipUpgradeRequestId` — upgrade detail (AuthGuard)
- `/account/edit/proforma-invoices` — `ProformaInvoicesComponent` (AuthGuard)

`CheckoutModule` is imported (not lazy-loaded) by `FacilitiesManagementModule`, `MembershipModule`, `AccountModule`, and `DynamicFormsModule`. It renders the gateway picker, coupon form, and amount breakdown inline in any parent template.

All payment API calls go through `PaymentsService` (`core/service/payments.service.ts`). No dedicated NgRx slice — all data held in component state. Profile `profileType` and `profileId` are read from the existing `profile` store slice.

Libraries: `@stripe/stripe-js` (`loadStripe`), Razorpay via global script (`declare var Razorpay`), PayPal via global script (`declare var paypal`). Easebuzz and PayU are entirely server-side; the frontend only polls status via `GET easebuzz/verify-status/:txnid`.

## Backend modules

Module specs:
- `sc-saas-backend/src/modules/payment-management/module.spec.md`
- `sc-saas-backend/src/modules/memberships/module.spec.md`
- `sc-saas-backend/src/modules/invoice/module.spec.md`

`PaymentManagementController` (path `payments`, v1): class-level `@UseGuards(FeatureGuard)` + `@Features(Feature.PAYMENT_GATEWAYS)` on all routes. `JwtAuthGuard` is present on only two routes (`GET mode`, `GET orders`); all others have it commented out.

`MembershipsController` (path `memberships`, v1): class-level `@UseGuards(FeatureGuard)` + `@Features(Feature.PAYMENT_GATEWAYS)`. `JwtAuthGuard` only on `GET /` and `GET /:id`; all other routes unauthenticated.

`InvoiceController` (path `invoice`, v1): `@UseGuards(FeatureGuard)` applied but no `@Features(...)` declared — gate is effectively inert. No `JwtAuthGuard`. `POST invoice/generate` is fully open.

## Data flow

1. **Gateway listing** — `GET payments/gateways` (unauthenticated) returns mode-filtered gateway credentials. `CheckoutComponent` calls this on init to populate the gateway picker.
2. **Order creation** — `POST payments/create-order` (or `discounted/create-order` for zero-amount). Body includes `gateway`, `moduleType` (e.g. `"membership"`, `"event"`), `moduleTypeId`, `userId`, `amount`. Route to gateway-specific service on backend by `payload.gateway`.
3. **PayPal capture** — after PayPal JS SDK client-side approval, frontend calls `POST payments/paypal/capture-order/:orderId`. Backend stamps `paymentMethod` on the order row.
4. **Easebuzz async flow** — Easebuzz redirects user to success/fail URL; frontend polls `GET payments/easebuzz/verify-status/:txnid`. The backend Easebuzz webhook (`POST payments/easebuzz/webhook`) is called server-to-server by Easebuzz to record transaction status — no auth on either endpoint.
5. **Transaction creation** — `POST payments/create-transaction` (unauthenticated). Called after gateway confirms payment to record the transaction in the platform.
6. **Coupon verification** — `POST payments/coupon/verify` or `POST payments/coupon/verify/membership`. Body is raw `any` (no DTO validation). Frontend must sanitize before sending.
7. **Membership tier upgrade** — `POST memberships/upgrade-request` (unauthenticated). Admin accepts/rejects via email link: `POST memberships/upgrade-request/accept/:id/:adminMd5` and `POST memberships/upgrade-request/reject/:id/:adminMd5`. Accept triggers SES email + certificate generation via `CertificatesEntity` (written directly, outside the certificates module).
8. **Proforma invoices** — `GET payments/proforma-invoices/history/:profileType/:profileId` (unauthenticated). `GET payments/proforma-invoices/:id/render/:profileType/:profileId` returns raw HTML; inject via `[innerHTML]` with `DomSanitizer.bypassSecurityTrustHtml` after confirming backend sanitization.
9. **Invoice PDF** — `POST invoice/generate` (fully open); writes temp PDF to `process.cwd()`, uploads to S3, returns signed URL. Called internally by `payment-management` via injected `InvoiceService`; do not surface this endpoint to users directly.

## Feature flags

- `payment_gateways` — gates all routes in both `payment-management` and `memberships` modules. If off, all checkout and membership calls return 403. Frontend must handle gracefully in `CheckoutComponent` (show a "payments disabled" state rather than a spinner).
- `payment_gateways` must exist in the cockpit `TenantUsersEntity`. Run `/trace-flag payment_gateways` before any rename.

## API contract

- `moduleType` is a free-text polymorphic string (`"membership"`, `"event"`, `"program"`, etc.) used as a key across order creation, pricing, verification, and history lookups. It is NOT an enum — mismatches cause silent payment-verification failures. The frontend and backend must agree on exact strings.
- `PaymentGatewaysService.getPaymentMode()` hits the DB on every call with no caching — every order creation triggers two DB reads. Do not add per-request gateway polling in the frontend.
- Membership response envelope returns `{ data }` without a `message` field (unlike the platform `{ message, data }` convention). Frontend `PaymentsService` must not rely on `response.message` for membership endpoints.

## Auth & security

Cross-repo security gaps (every one is a critical finding):

1. **Almost every payment route is unauthenticated.** Only `GET payments/mode` and `GET payments/orders` have `JwtAuthGuard`. Order creation, transaction recording, coupon verification, pricing lookups, proforma invoice reads, and manual invoice generation are all open to unauthenticated callers. The current intent is to support checkout before login — but `POST invoice/generate` (writes to disk + S3), `POST payments/create-transaction`, and `POST payments/invoice-manual/:orderId/:transactionId` are particularly sensitive and should be re-evaluated.
2. **`POST invoice/generate` is entirely unguarded**: `FeatureGuard` is on the controller but no `@Features()` metadata is declared, so the gate never fires. No `JwtAuthGuard`. Any caller can trigger disk writes and S3 uploads.
3. **`POST memberships/upgrade-request` is unauthenticated and caller-identity is unverified**: any caller who knows a valid `profileId` can submit an upgrade request on behalf of that profile.
4. **Membership history/last/types routes are unauthenticated**: any caller who knows `profileType + profileId` can read full membership history — do not use these to prove subscription status.
5. **`POST payments/coupon/verify` uses `@Body() body: any`** — no DTO validation; coupon code and userId are extracted from a raw object without sanitization.
6. **Easebuzz webhook (`POST payments/easebuzz/webhook`) is intentionally unauthenticated** (called by the Easebuzz platform). Verify the webhook payload against Easebuzz's HMAC signature — the module spec does not mention signature validation. This is a critical gap if not implemented at the service layer.
7. **`PaymentGatewaysComponent` hardcodes `localhost:3000`** for all three gateway create-order calls (Stripe, PayPal, Razorpay) and embeds a test Stripe publishable key. This component MUST NOT be deployed to production without replacing all hardcoded values.

## Known issues / Watch out for

- **`PaymentManagementModule` imports `forwardRef(() => PaymentManagementModule)`** (self-reference) — inert but should be removed to avoid confusion.
- **`EasebuzzService` is registered twice** in `providers` — once as a class and once as a token-based registration. The token-based registration is never injected anywhere; it is dead. Do not add injections using the token form.
- **`getPaymentMode()` queries the DB on every order creation** with no caching — every order creation path hits the DB twice (payment mode + gateway credentials). Consider caching the mode for the request lifecycle.
- **`generateInvoiceManual` swallows errors silently** (`console.log(error)` + return `undefined`). Callers cannot distinguish success from failure; a failed PDF upload will silently skip the invoice.
- **`MembershipsService` directly uses `PaymentChargesTypesEntity` and `PaymentTransactionsEntity`** without importing `PaymentManagementModule`. Cross-module entity access outside the module boundary — if those entity schemas change, the memberships module silently breaks.
- **`CertificatesEntity` is written directly inside `acceptUpgradeRequest`** without importing a certificates module. Another cross-module boundary violation.
- **`getProformaInvoiceHtml` returns raw HTML** (`responseType: 'text'`). Use `DomSanitizer.bypassSecurityTrustHtml` only if the backend guarantees sanitization; otherwise XSS risk.
