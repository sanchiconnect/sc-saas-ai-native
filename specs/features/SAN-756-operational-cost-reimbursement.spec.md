---
id: SAN-756                     # Linear Project created (team: Sanchiconnect); anchored to its lowest-numbered
                                 # per-repo issue, SAN-756 (backend). Full issue set: SAN-756 (backend),
                                 # SAN-757 (frontend), SAN-758 (admin).
title: Operational Cost Reimbursement — Slices 1-2 (Tripura)
type: feature
status: done
linear: https://linear.app/sanchiconnect/project/operational-cost-reimbursement-slices-1-2-tripura-bd9afb3dfb3e
owner: nirmal.s@sanchiconnect.com
repos: [tenants, backend, frontend, admin]
                                 # `tenants` carries only a one-line flag-column addition (see Contracts) and
                                 # deliberately has no separate Linear issue — folded into the backend issue
                                 # (SAN-756) as its prerequisite, per this feature's explicit 3-repo scope.
contracts:
  api:
    - "GET api/v1/operational-cost-reimbursement/eligibility (sc-saas-backend, NEW — Slice 1: 12-month window/status grid + live category→amount preview for the logged-in startup)"
    - "POST api/v1/operational-cost-reimbursement/claims (sc-saas-backend, NEW — Slice 2: Month-1 first-time submission only: category choice, documents, bank details, one-claim-per-month enforcement, amount snapshotted at submission)"
    - "GET api/v1/operational-cost-reimbursement/self-declaration-template (sc-saas-backend, NEW — serves the admin-uploaded template file to the startup form)"
    - "GET api/v1/operational-cost-reimbursement/admin/claims (sc-saas-backend, NEW — admin-authenticated, paginated claims list: startup/recognition no., month, category, amount, status; minimal, download-only queue — pulled forward from Slice 3 by 2026-09-14 user directive, see BRD §18)"
    - "POST api/v1/operational-cost-reimbursement/admin/claims/download-manifest (sc-saas-backend, NEW — admin-authenticated; accepts explicit claim ids OR a selectAll+filters instruction; for every currently-Submitted claim in the resolved set, transitions it to Under Process, write-once-sets firstDownloadedAt/firstDownloadedByAdminId, and sends the startup a transition email via SesEmailService; renders each claim's packet PDF via PdfRenderHtmlService; returns a client-zip-downloader.js-compatible JSON manifest of per-claim {folder, files:[{url,name}]} — same shape whether 1 or many claims are selected)"
  flags:
    - "operational_cost_reimbursement_enabled"
  events: []
tenant_scoped: true
depends_on: []
created: 2026-09-14
---

# Operational Cost Reimbursement — Slices 1-2 (Tripura)

## Problem

Startup Tripura (T-RISE) recognizes startups and, for the 12 months following recognition, reimburses a fixed monthly operational cost sized by category — provided the startup applies for it, one month at a time. None of this exists today. This spec covers **Slices 1-2, plus one item pulled forward from Slice 3**, per the authoritative BRD (`specs/features/BRD-Operational-Cost-Reimbursement-TRISE-v2.md`, Rev. 3, §14 "Suggested Slicing" + §18 "Amendment"), which **supersedes** the earlier client-overview docx and hour-estimate PDF used in initial scoping on every point of conflict: Slice 1 (recognition-gated visibility, eligibility-window computation, category selection with the correct fixed amount displayed — no submission yet) + Slice 2 (first-time submission: documents, bank details, self-declaration, one-claim-per-month enforcement) + **the Slice-3 download capability (single-claim AND bulk), pulled forward by explicit user directive on 2026-09-14, including the FR-8.1 transition email**. Everything else in Slices 3-5 (View Details, bulk status change beyond what download itself triggers, rejection-with-reason, verify-and-submit for month 2+, bulk-Sanction, reporting) remains deferred — Evidenced, BRD §14/§18.

**Corrections vs. earlier scoping (do not build to the old numbers):**
- Three fixed categories, not two — General ₹20,000/mo, Women-led ₹22,000/mo, **PH-led ₹24,000/mo** (confirmed by the Product Owner, not ₹25,000) — and the amount is **snapshotted onto the claim at submission time**, never a live lookup — Evidenced, BRD FR-2.1.
- **BRD FR-6.1 AC3 ("no bulk-download action exists... always single-claim") is formally amended for this feature** (BRD §18, dated 2026-09-14): bulk download is now in scope alongside single-claim download, modeled on `sc-saas-admin`'s existing bulk-download pattern.
- **The eligibility-gating field is confirmed, not open**: the user directly confirmed on 2026-09-14 ("yes manage with this recognition_generated_at") that `startups.recognition_generated_at`/`recognition_regenerated_at` is the correct field — BRD §13.1.
- **The download-triggered transition email is confirmed, not open**: the user confirmed the download-triggered Submitted→Under Process transition SHOULD fire BRD FR-8.1's "email on transition into Under Process" notification to the startup, same as any other transition into Under Process — this is now in scope for the download endpoint, reusing `SesEmailService` (`core/services/ses-email.service.ts`), the platform's existing single transactional-email mechanism (e.g. `sendProfileUnderReviewEmail`/`sendProfileRejectedByAdminEmail` are the closest existing analogs), not a new one.
- **BRD FR-1.1 is formally extended (BRD §19, dated 2026-09-14)**: an admin-configurable, per-tenant, OFF-by-default toggle ("also visible to approved startups") widens module VISIBILITY (only) to any startup with `approvalStatus === ProfileAccountStatuses.APPROVED`, even without a Recognition ID. Claim submission still unconditionally requires `recognized === true`. An approved-but-not-recognized startup let in this way sees all 12 months as locked/unclaimable (no `recognitionGeneratedAt` to anchor a real window) — a new, explicit "visible but locked" state. Implemented as a setting on the same admin-editable settings row as the self-declaration template, not a new tenants-cockpit flag.

## Acceptance criteria

*(Numbered against the BRD's own FR/AC references where applicable.)*

- [ ] A new `operational_cost_reimbursement_enabled` flag exists on `sanchiconnect-saas-tenants`'s `TenantUsersEntity`, defaulting `false`; with it off, no route/UI/admin page in this feature is reachable — BRD FR-1.1, NFR "feature-flag discipline."
- [ ] No Recognition ID → no entry point anywhere, including direct route calls (server-side reject, not just hidden nav) — BRD FR-1.1 AC1/AC2 — **unless the "also visible to approved startups" setting (BRD §19) is on AND the startup's `approvalStatus === APPROVED`, in which case the module is reachable but shows all 12 months locked/unclaimable, and claim submission is still blocked server-side (recognized-only, unconditionally).**
- [ ] The "also visible to approved startups" setting defaults OFF (Recognition-ID-only behavior unchanged from the original FR-1.1) and is editable only from the admin `operation_cost` dashboard, stored on the same settings row as the self-declaration template — BRD §19.
- [ ] A recognized startup sees a 12-month eligibility grid; the first eligible-from date is `recognition_generated_at + 1 month` (confirmed field), and month-end rounds DOWN — BRD FR-1.2 AC1/AC2.
- [ ] Once unlocked, a month's window never auto-expires and stays claimable at any later point within the 12-month scheme; months are claimable out of order — BRD FR-1.3 AC1/AC2.
- [ ] Revoking a startup's recognition (`recognized = false`) stops any future month from unlocking; a claim already Submitted/Under Process at the moment of revocation is left untouched — BRD FR-1.4 AC1/AC2.
- [ ] The startup selects a benefit category (General / Women-led / PH-led) and sees that category's fixed monthly amount update live before submitting — BRD FR-2.1 AC1/AC2.
- [ ] The amount is snapshotted onto the claim row at submission time, not derived from a live category lookup — BRD FR-2.1 AC3.
- [ ] PH-led requires a disability-certificate upload; submitting PH-led without it is blocked. Women-led/General show no such requirement — BRD FR-2.2 AC1/AC2.
- [ ] A shareholding pattern document is mandatory for the first submission **regardless of category** — BRD FR-3.3 AC1.
- [ ] The first claim is blocked without complete bank details: account number, IFSC, and a cancelled cheque/passbook image — BRD FR-3.1 AC2. Bank details are captured once, against the startup, for reuse in later slices.
- [ ] The claim cannot be submitted without a self-declaration document attached — a static, platform-provided downloadable template, filled offline and re-uploaded — BRD FR-3.2.
- [ ] A new claim for a month that already has a Submitted/Under-Process/Sanctioned claim is blocked server-side — BRD FR-4.1 AC1.
- [ ] The claim's `status` column supports the full `Submitted / Under Process / Sanctioned / Rejected` set; `Submitted` and `Under Process` are both reachable by code shipped in this spec (the latter via download), `Sanctioned`/`Rejected` are not — BRD §14 note.
- [ ] **An admin can download a single claim's packet, or several/all selected claims' packets in bulk (pagination-aware "select all"), from a minimal new admin claims list** — BRD FR-6.3/FR-6.4, as amended by BRD §18.
- [ ] **Downloading a `Submitted` claim (single or as part of a bulk batch) transitions it to `Under Process` as part of that same action; a claim already `Under Process` in the batch downloads with no side effect** — BRD FR-6.3 AC1.
- [ ] **Each claim's first-download timestamp and downloading admin are recorded write-once (set only when null); a later re-download never changes them** — BRD FR-6.4 AC1, NFR auditability.
- [ ] **Every downloaded packet includes a freshly-generated Operational Cost Application PDF (via `PdfRenderHtmlService`) bundling period/category/amount/bank details, plus the claim's uploaded documents** — BRD FR-6.3 AC2.
- [ ] **Every claim that transitions Submitted → Under Process via download triggers a transactional email to the startup, via `SesEmailService`** — BRD FR-8.1 AC1, confirmed in scope 2026-09-14. Re-downloading an already-Under-Process claim does NOT re-send the email (matches FR-6.4's write-once/idempotent behavior).
- [ ] The admin claims list added to support downloading shows no Reject/Sanction/View-Details actions (those stay deferred) and exposes bank details only in a future detail view, never this list — BRD NFR (DPDP).
- [ ] An admin with the appropriate role can upload a sample self-declaration/letterhead template from a new `operation_cost` module dashboard page; any other admin role is refused.
- [ ] The flag propagates end-to-end: cockpit column → backend `Feature` enum + `FeatureGuard` → frontend `IFeatures` → admin `config.php` constant, mirroring `hub_spoke_domain_enabled`'s confirmed wiring.
- [ ] No Slice 3 (beyond the pulled-forward download), 4, or 5 functionality (View Details, bulk status change beyond download's own transition, rejection, verify-and-submit for month 2+, bulk-Sanction, reporting) exists anywhere in the shipped code for this spec.

## Per-repo plan

### tenants
- Add `operational_cost_reimbursement_enabled` boolean column (`width: 1, type: 'boolean', default: false`) to `TenantUsersEntity` (`sanchiconnect-saas-tenants/src/modules/tenants/entities/tenant-users.entity.ts`), following the exact pattern of the most recently added flag, `hub_spoke_domain_enabled`. Cockpit-owned per invariant #1 — no other tenants-side change needed.

### backend
- **Module placement (Practice 1 check):** the BRD (§3.1) points at `schemes-management` and `grants` as pre-existing stubs. Verified directly — both are real but genuinely empty of business logic: `SchemesController` has zero routes, `grants` is entity-only (single `amountGranted` per beneficiary, no status lifecycle, no documents, no month index). Decision: build a **new** module, `src/modules/operational-cost-reimbursement/` (mirrors `payment-management`'s controller→service→repository→entities/dto shape), reusing `SchemesEntity` as its parent scheme row (one seeded `schemes` row) rather than inventing a second grouping concept.
- **Eligibility-window algorithm:** reuse the Call-for-Applications reapplication-cooldown pattern (BRD §3.2), evidenced at `application-management/application-program.service.ts` / `program-management/program-management.service.ts` (`allowReapplication` / `reapplicationDurationType` / `getReapplyActivationDate()`), adapted to 12 fixed monthly windows anchored to `startups.recognitionGeneratedAt` (falling back to `recognitionRegeneratedAt` — confirmed gating field), with month-end-rounds-down semantics.
- Entities (TypeORM, `synchronize: true`):
  - `OperationalCostClaimEntity` — FK to `schemes.id` and `startups.id`; month index; period start/end; category (locked once set); `amount` (snapshotted, integer); `status` enum (full `Submitted/UnderProcess/Sanctioned/Rejected` set); status timestamps per stage (nullable); rejection reason (nullable, unused in this scope); `firstDownloadedAt` (nullable timestamp, write-once) and `firstDownloadedByAdminId` (nullable). Standard base shape: uuid, soft-delete, audit timestamps.
  - `OperationalCostDocumentEntity` — one row per claim's document slot, stored via the shared `UploadService`/`AmazonS3Service` (`core/upload-module/`).
  - `OperationalCostBankDetailsEntity` — one row per startup.
  - `OperationalCostSelfDeclarationTemplateEntity` — admin-uploaded template ref; schema owned here, written directly by `sc-saas-admin` via Medoo against the same tenant DB. **Extended (BRD §19):** also carries a `visibleToApprovedStartups` boolean (default `false`) on this same singleton settings row — a per-tenant operational toggle, not a new cockpit flag (see Contracts & invariants).
- `GET operational-cost-reimbursement/eligibility` — Slice 1 grid + category preview. **Extended (BRD §19):** visibility check becomes `startup.recognized === true` OR (`settings.visibleToApprovedStartups === true` AND `startup.approvalStatus === ProfileAccountStatuses.APPROVED`); only the first branch computes real unlock dates — the second returns all 12 months in a `locked` state (no eligible-from date, `claimable: false`), a new explicit response shape distinct from both the normal grid and the 403/404 fully-blocked response.
- `POST operational-cost-reimbursement/claims` — Slice 2 Month-1-only first-time submission. **Unaffected by BRD §19**: requires `startup.recognized === true` unconditionally, regardless of the visibility-scope setting — an approved-but-not-recognized startup that can now SEE the module still cannot submit a claim; this must be enforced server-side, not left to the frontend disabling the button.
- `GET operational-cost-reimbursement/self-declaration-template`.
- **`GET operational-cost-reimbursement/admin/claims`** — NEW, admin-authenticated: paginated list (startup name/recognition no., month, category, amount, status). Must support resolving "select all matching current filter" server-side (mirrors `sc-saas-admin`'s own `resolveBulkIds()` pattern) so bulk selection works across pagination at the expected thousands-of-startups scale.
- **`POST operational-cost-reimbursement/admin/claims/download-manifest`** — NEW, admin-authenticated. Accepts either explicit claim ids or a `{selectAll: true, filters}` instruction. For each resolved claim: (a) if `status === Submitted`, transition to `UnderProcess`, write-once-set `firstDownloadedAt`/`firstDownloadedByAdminId`, **and call a new `SesEmailService` method (e.g. `sendOperationalCostClaimUnderProcessEmail(...)`, mirroring the shape of existing per-purpose methods like `sendProfileUnderReviewEmail`/`sendProfileRejectedByAdminEmail`) to notify the startup — per BRD FR-8.1, confirmed in scope 2026-09-14**; claims already past `Submitted` are included with no side effect and no re-send (idempotent re-download, BRD FR-6.4); (b) render a fresh packet PDF via `PdfRenderHtmlService`; (c) build a manifest entry `{folder, files: [{url: pdfUrl, name}, ...documentUrls]}`. Response shape mirrors `sc-saas-admin`'s existing `get_bulk_attachment_urls` JSON shape (flat for a single claim, foldered for many) so the admin side can reuse `client-zip-downloader.js` unmodified. **Design decision (BRD §18):** one combined package per claim (PDF + that claim's documents together), not the reference precedent's separate PDF-vs-attachments dropdown options.
  - **Admin-auth note:** the exact guard for these two new admin-facing routes is an implementation-time decision — `sc-saas-admin` already calls the backend with `Authorization: Bearer <token>` for other admin-triggered actions (`sc-saas-admin/includes/core_functions.php`); mirror whatever concrete guard that pattern uses. `admin-actions.controller.ts`'s own guard shape (class-level `FeatureGuard`) is the nearest example to check first.
- Add `OPERATIONAL_COST_REIMBURSEMENT_ENABLED = 'operational_cost_reimbursement_enabled'` to `Feature` enum; gate every route with `@Features(...) @UseGuards(FeatureGuard, ...)`, mirroring `partner-branding.controller.ts`'s pattern.
- Jest tests: eligibility-window math, one-claim-per-month enforcement, category→amount snapshot, PH-led document validation, flag-off refusal, download-triggers-transition (only for Submitted, no-op for later statuses), write-once first-download timestamp/actor, manifest shape for 1 vs. many claims, **and the transition email fires exactly once per claim (on the transitioning download call, not on any later re-download)**. **Add (BRD §19):** eligibility returns the real grid for `recognized` startups regardless of the setting; returns the all-locked grid for approved-but-not-recognized startups only when the setting is on; returns 403/404 for neither-recognized-nor-approved startups regardless of the setting; and `submitClaim()` rejects an approved-but-not-recognized startup even when the setting is on.

### frontend
- New lazy-loaded module (mirror `startup-kit`'s shape) gated on `features.operational_cost_reimbursement_enabled` (add to `IFeatures` in `core/domain/brand.model.ts`).
- 12-month eligibility grid consuming `GET .../eligibility`. Must correctly render `Under Process`, not only `Submitted` (an admin can now reach that state via download within this scope). **Extended (BRD §19):** must also render the new all-locked preview state (approved-but-not-recognized) distinctly from both the normal grid and a fully-blocked/404 state — e.g. a banner explaining the module unlocks once the startup is recognized, with every month tile shown but disabled, and no Claim action anywhere. The module-entry-point/nav-link gate (previously "has Recognition ID") must also now check this same combined condition, not just `recognized`, so the entry point itself isn't hidden for a startup the backend would actually let in.
- Category-selector UI (General / Women-led / PH-led tiles) updating the displayed fixed amount live.
- Month-1 application form: bank details + document uploads (self-declaration download-then-reupload, shareholding required for all categories, disability certificate conditional on PH-led), submitting to `POST .../claims`. Static fields, not admin-configurable.
- No Month-2+ claim UI — verify-and-submit is Slice 4, unaffected by this pull-forward.
- Wire new endpoints into `core/service/api-endpoint.service.ts`; NgRx state slice for eligibility/claim-in-progress, extended to recognize the `Under Process` status value.
- Karma/jasmine tests for grid state derivation (covering both `Submitted` and `Under Process`) and category-conditional document logic; manual QA. **Add (BRD §19):** grid rendering for the new all-locked (approved-but-not-recognized) response shape, and confirming the Claim action is absent/disabled in that state.

### admin
- New `operation_cost` module directory (`modules/operation_cost/`):
  1. **Template upload dashboard page** — self-declaration/letterhead template upload, direct Medoo write against `OperationalCostSelfDeclarationTemplateEntity`'s table, mirroring `analysis_cost_dashboard.php`'s role-gating shape. **Extended (BRD §19):** the same page gets a second control — a checkbox/toggle for "Also visible to approved (not-yet-recognized) startups", default unchecked, direct Medoo write to the same settings row's new `visible_to_approved_startups` column.
  2. **Minimal claims list page**, built ONLY to support the pulled-forward download action: a table of claims (startup/recognition no., month, category, amount, status) consuming `GET .../admin/claims`, with row checkboxes + a pagination-aware "select all" (reusing the "All / N selected" badge pattern from `submission-application-management.php` ~lines 396-415) and a single-option download dropdown ("Download Claim Packet(s) (.zip)") calling `POST .../admin/claims/download-manifest` via cURL, then handing the manifest to the existing, already-shared `themes/default/assets/js/client-zip-downloader.js` asset unmodified.
  - **Explicitly NOT added to this list:** Reject, Sanction, or "View Details" row actions — those remain Slice 3/5, deferred.
- Role-gating: same shape as `analysis_cost_dashboard.php`'s `checkRole('is_dev') || in_array(...)`.
- Add `define('operational_cost_reimbursement_enabled', ...)` to `config/config.php`, gate nav-menu visibility to both new pages on it.
- **Design note:** the manifest+transition+email logic lives entirely in the new backend endpoint (not duplicated in PHP against Medoo, unlike the CFA precedent) because `PdfRenderHtmlService` and `SesEmailService` both only exist in `sc-saas-backend`, and a status-lifecycle write belongs in the module that owns the claim's business rules. `sc-saas-admin`'s role is a thin cURL caller plus reuse of the client-side zip JS.

## Contracts & invariants

- **Flags:** `operational_cost_reimbursement_enabled` — new flag, `tenants`-owned, defaulting `false`, propagated per `hub_spoke_domain_enabled`'s pattern. **`visibleToApprovedStartups` (BRD §19) is deliberately NOT a cockpit flag** — a per-tenant operational setting on the OCR settings row, admin-editable, no flag-propagation pipeline needed.
- **API:** Five new backend routes — see `contracts.api`. The two new admin routes are a genuinely bigger API-contract surface than originally speced; `sc-saas-admin` becomes a real REST consumer of `sc-saas-backend` for this feature, so `/audit-contract` must check both the admin cURL callers AND the manifest response shape's exact match to what `client-zip-downloader.js` expects.
- **Events:** none.
- **Invariants at risk:**
  - **Flag names (#1):** unchanged — new flag, cockpit-first.
  - **API contract (#2):** five new routes; two of them (admin claims list + download-manifest) are a genuinely new admin↔backend contract surface and need their own auth-guard decision before implementation.
  - **Tenant scoping (#5):** every query scoped by the bootstrap-loaded one-deployment-per-tenant backend config; explicitly NOT modelled on `payment-management`'s access pattern per BRD NFR.
  - Auth (#4) and the tenant-verification contract (#3) are unaffected.

## Test plan

- tenants: manual verification the new column appears in `verify_tenant`/`tenant-settings` responses.
- backend: jest tests for eligibility-window math, one-claim-per-month enforcement, category/amount snapshot, PH-led document validation, flag-guard refusal, download-triggers-transition only for `Submitted` claims (no-op otherwise), write-once first-download timestamp/actor, manifest shape for 1 vs. many claims, **and the FR-8.1 transition email firing exactly once per claim, on transition only**.
- frontend: karma tests for grid state derivation covering both `Submitted` and `Under Process`; manual QA end-to-end.
- admin: `php -l` on all edited/new files; manual QA of the template-upload page + role-gate; manual QA of the claims list: select one claim and download (confirm status flips to Under Process, email sent, and both stay unchanged on re-download), select several/all across a paginated set and bulk-download, confirm the zip's contents match BRD FR-6.3's bundle, confirm no Reject/Sanction/View-Details controls are present. **Add (BRD §19):** manual QA of the new "also visible to approved startups" toggle on the dashboard page — confirm it persists, defaults unchecked, and is a separate control from the template upload.
- cross-repo: with the flag off on a control tenant, confirm zero visible change anywhere; with it on, walk eligibility grid (all 3 categories) → Month-1 submission → admin claims list shows the new claim as Submitted → admin downloads it (single) → status flips to Under Process, startup receives the transition email, and the startup's own eligibility grid now shows Under Process for that month → admin bulk-downloads a mixed batch (some Submitted, some already Under Process) → confirm only the Submitted ones transition/email and every claim's first-download fields are correct. **Add (BRD §19):** with the approved-visibility setting OFF, confirm an approved-but-not-recognized startup gets the original fully-blocked behavior; with it ON, confirm that same startup can open the module and sees all 12 months locked with no Claim action, and that a direct `POST .../claims` call for that startup is still rejected server-side; confirm a recognized startup's behavior is completely unaffected by this setting either way.

## Rollout

1. Add the flag column in `tenants` first (default `false`).
2. Deploy backend with the new module + flag-gated routes, including the two new admin download routes (inert until the flag is set for Tripura).
3. Deploy admin's `operation_cost` pages (template upload + claims list/download), also flag-gated.
4. Deploy frontend's flag-gated UI (including the `Under Process` grid state).
5. Enable `operational_cost_reimbursement_enabled` for the Tripura tenant only; verify end-to-end before considering any other tenant.

## Out of scope

Deferred to Slices 3 (remainder)/4/5 per the BRD's §14 slicing as amended by §18 (NOT built in this spec):
- **Slice 3 remainder:** admin "View Details" (no-status-change inspection), bulk status change beyond what download itself triggers, rejection-with-required-reason.
- **Slice 4:** verify-and-submit for Month 2 onward.
- **Slice 5:** bulk-Sanction after offline verification, and the report section with month-wise export.
- **BRD FR-1.5** (admin migration tool): BRD-general scope, not assigned to any slice built here.
- Any payment-gateway integration or automated fund transfer (BRD §6.2).
- Sanctioned/Rejected-transition emails (BRD FR-8.1) — those transitions aren't reachable in this scope. Only the Under-Process (download-triggered) email is built here, per the 2026-09-14 confirmation.

## Open questions

- **SLA turnaround target** — what target, if any, should the first-download date (BRD FR-6.4) be measured against? Not blocking. (BRD §13.2 item 1.)
- **DPDP retention period** — how long should documents/bank details be retained after a startup's 12-month scheme ends or exits early? Should come from T-RISE's actual DPDP filing. Not blocking. (BRD §13.2 item 2.)

Both remaining items are explicitly non-blocking per the BRD's own status line — this spec has no other open items and is otherwise ready for review/approval.

**Resolved, no longer open:**
- **2026-09-14** — the eligibility-gating field: confirmed as `startups.recognition_generated_at`/`recognition_regenerated_at` (user: "yes manage with this recognition_generated_at"). See BRD §3.3/§13.1.
- **2026-09-14** — the download-triggered Under-Process transition email: confirmed in scope, reusing `SesEmailService`. See Acceptance criteria and Per-repo plan (backend) above.
