# BRD — Operational Cost Reimbursement (T-RISE) — Rev. 3

Source: `BRD-Operational-Cost-Reimbursement-TRISE-v2.pdf`, pasted into the ai_native_setup session on 2026-09-14. Saved here verbatim (converted from the PDF) as the authoritative source document for the OCR feature spec — supersedes the shorter `Operational-Cost-Reimbursement-Client-Overview.docx` and the rough hour-estimate PDF (`Tripura Add-ons Requirements.pdf`) used in earlier scoping.

Prepared by Aditya Yadav — Senior Product Designer & APM/UI-UX Lead, Sanchi Connect.

Status: Draft — all Rev. 2 open questions resolved. Of the three items originally carried as genuinely open (§13.2), one (the eligibility-gating field) was resolved by direct user confirmation on 2026-09-14; two (SLA turnaround target, DPDP retention period) remain open and non-blocking. **See §18 — FR-6.1 AC3 has also been formally amended for this feature.**

## 1. Purpose & How to Use This Document

This BRD captures the business need for Operational Cost Reimbursement on the T-RISE / SanchiSaaS portal: the problem before the solution, an outcome anyone can verify, acceptance criteria stated as observable checks, and scope stated plainly — in and explicitly out. It does not decide the technical "how" — table names, endpoints, UI composition — which is reserved for the team to resolve when this BRD is turned into Linear issues and run through the spec loop, confirmed by the Product Owner at Spec-Lock.

## 2. Where This Need Comes From

Startup Tripura needs recognized startups to be able to claim a fixed monthly operational cost reimbursement — sized to their category — without refilling the same information every month, and needs administrators to be able to process a high volume of monthly claims through bulk actions rather than one-by-one handling, while keeping every rejection explained and every review auditable.

## 3. Background — Platform Context

- **3.1** Nothing exists for this yet, but `schemes-management` and `grants` exist specifically as unbuilt entity stubs for exactly this kind of feature — the natural home for a scheme-disbursement feature, not a green-field module name to invent. No reimbursement/scheme/disbursement workflow exists anywhere in the live codebase today.
- **3.2** The closest live, working pattern: the Call-for-Applications track (`application_program` → `application_program_round` → `application_program_submission_progress`) — a real status pipeline + admin kanban/table view — is the closest shipped analog to a monthly claim queue. That track's cooldown/eligibility-gating mechanism (`allowReapplication`, `reapplicationDurationType`, `getReapplyActivationDate()`) is recommended as the pattern to adapt for month-by-month eligibility, rather than reinventing it.
- **3.3** SAN-253 (Startup ID Creation Module) adds `recognition_id` and `recognition_generated_at` to `startups`. **Confirmed 2026-09-14 by direct user statement ("yes manage with this recognition_generated_at") as the exact field this feature gates its eligibility window on** — see §13.2's resolution note.
- **3.4** The platform's only payment schema is inbound-only. Nothing moves money out to a startup — this feature is a review-and-approve workflow (download, offline verification, bulk-Sanction), not a payout integration. Must NOT be modelled on `payment-management`'s access pattern (flagged Critical finding).
- **3.5** Reusable building blocks: `PdfRenderHtmlService` (core/upload-module) for the auto-generated Operational Cost Application PDF; the shared upload-module (S3) for every document upload; curated CSV/Excel admin exports as precedent for the report section.
- **3.6** Standard per-tenant table shape applies: uuid, soft deletion, audit timestamps, approval shape (status, acting admin, timestamp, optional message). New feature areas gated by a tenant-owned boolean flag, off by default.

## 4. Problem Statement

Startup Tripura recognizes startups and, for the 12 months following recognition, reimburses a fixed monthly operational cost — sized by category — provided the startup applies for it, one month at a time. None of this exists today: no restriction limiting the module to recognized startups, no month-by-month claim tracker tied to a recognition date, no category-based fixed-amount logic, no rejection-with-reason flow, no admin process for reviewing/downloading/bulk-processing claims.

## 5. Outcome Statement

A startup with a Recognition ID can, starting one month after recognition, see and open its Operational Cost Reimbursement module — invisible to any startup without one. Each month's claim window opens on schedule and stays open until the startup applies for it. On first use, the startup selects a benefit category (General, Women-led, or PH-led), sees that category's fixed monthly amount, provides the category's required document(s) plus one-time bank and self-declaration details, and submits. In every later month, the startup only has to verify its saved details and submit again. The startup can track a claim through Submitted → Under Process → Sanctioned, or see a Rejected status together with the admin's stated reason, and reapply for that same month. An administrator can bulk-change claim statuses; downloading an application's packet is itself what moves it from Submitted to Under Process, recorded against an immutable first-download date; and once offline verification is done, the admin bulk-marks the batch Sanctioned. A report section shows every claim, filterable and exportable month by month.

## 6. Scope

### 6.1 In scope

- Recognition-ID gated visibility: module + every route behind it invisible/unreachable without a Recognition ID.
- Eligibility computed from the recognition date: usable starting one month after recognition, for a 12-month scheme.
- Each month's claim window opens on schedule and stays open — no auto-expiry — until claimed, within the 12-month scheme. Months can be claimed out of order.
- Revoking recognition stops future months from opening; any claim already Submitted/Under Process at that moment is left to ordinary admin Reject/Sanction discretion.
- Admin-side migration: marking specific months Sanctioned directly for already-recognized startups, for periods already reimbursed before this module existed.
- Benefit category selection (General / Women-led / PH-led) with the matching fixed monthly amount displayed before submission.
- Category-conditional document requirements (disability-certificate upload specifically for PH-led).
- One-time capture, at first submission: bank account number, IFSC code, cancelled cheque/passbook image, a shareholding pattern document (mandatory for every category, not just Women-led), and a self-declaration (downloaded template, filled outside the platform, re-uploaded — static, never pre-filled by the system).
- From month 2 onward, a verify-and-submit flow against previously saved details, rather than a full refill.
- One active claim per startup per month; a Rejected claim reopens that month for reapplication (uncapped — reapply as many times as needed until Sanctioned; on that resubmission, category + all documents unlock for editing, in ANY month, not first-time only).
- Statuses: Submitted, Under Process, Sanctioned, Rejected — mandatory admin-entered reason on rejection, visible to the startup.
- Admin bulk status changes (more than one application at a time) — but see FR-6.1: the ONLY bulk action anywhere is bulk-Sanction (Under Process → Sanctioned). No bulk-download, no bulk-reject, no backward status transitions ever. **Amended for this feature — see §18: bulk-download is now also permitted, alongside bulk-Sanction.**
- Admin download of an application's packet (period claimed, category, monthly amount, bank details, uploaded documents, auto-generated Operational Cost Application PDF via `PdfRenderHtmlService`) — downloading is ITSELF the action that transitions Submitted → Under Process. Always single-claim, never bulk. **Amended for this feature — see §18: bulk download is now also permitted.**
- A separate "View Details" action lets an admin inspect a claim with NO status change (resolves the download-vs-view ambiguity).
- An immutable first-download date per claim, unaffected by later re-downloads (captured for future SLA tracking — no SLA target defined yet).
- Bulk-marking a batch of Under Process applications Sanctioned after offline verification (pagination-aware — expected scale is potentially thousands of startups, "select all" must mean every matching record).
- A report section: view claim details, filter and export month by month.
- A new tenant feature flag gating the whole module, off by default (e.g. `operational_cost_reimbursement_enabled`).
- Email notification to the startup on every transition into Under Process, Sanctioned, or Rejected (Rejected email includes the admin's stated reason). Submitted-transition email and SMS are NOT yet confirmed — assume out of scope for now.

### 6.2 Out of scope (explicit)

- Any payment gateway integration or automated fund transfer; no payment reference/date captured. Sanctioned is the system's final state — disbursement is tracked entirely outside the portal.
- Any window model other than the fixed 12 monthly windows anchored to one recognition date.
- Changes to how a Recognition ID is generated — this feature only consumes it.
- Admin-configurable form fields — the application form is fixed and hard-coded (confirmed by Product Owner).
- Any change to the existing payment-management gateway module or its known security gaps.
- A separate appeals/dispute process beyond reapplying after rejection.

## 7. Stakeholders / Actors

| Actor | Role | Needs |
|---|---|---|
| Recognized Startup | Applicant | Sees module only once recognized; selects category, submits first claim; verifies+submits later months; tracks status, sees rejection reason, reapplies. |
| Startup Tripura Administrator | Reviewer | Bulk-changes claim status; downloads packets (advances status); offline verification; bulk-marks Sanctioned; rejects with reason; runs/exports report. |
| Directorate of IT, Govt of Tripura | Programme owner (indirect) | Consumes report for governance/audit. |
| Sanchi Connect Engineering | Build | Turns BRD into Linear issues, drafts spec, implements. |

## 8. Business Process / Workflow (12 steps)

1. Recognition & visibility — Startup receives Recognition ID; module invisible to anyone without one.
2. Eligibility opens one month after the recognition date, for a 12-month scheme.
3. Monthly window stays open — no auto-close — until claimed, however late, within the scheme.
4. First-time application — category & amount: General ₹20,000/mo, Women-led ₹22,000/mo, PH-led ₹24,000/mo — amount displayed immediately on category selection.
5. First-time application — documents & details: category's required document (disability certificate for PH-led), shareholding pattern doc (all categories), self-declaration (downloaded template, filled offline, re-uploaded), bank details (account number, IFSC, cancelled cheque/passbook image).
6. Submission — claim submitted as Submitted. No second claim for the same month while one is active/sanctioned.
7. Later months — verify & submit: startup reviews saved category/documents/bank details, submits — no refill.
8. Admin review, view & download — admin can bulk-change status and open View Details without affecting status. Downloading (period, category, amount, bank details, documents, auto-generated PDF) is what moves Submitted → Under Process. Re-downloading doesn't change the recorded first-download date.
9. Offline verification — admin does manual verification outside the system.
10. Bulk sanction — admin multi-selects verified Under Process applications, marks Sanctioned in one action.
11. Rejection & reapplication — admin can mark Rejected with a free-text reason at any point; startup sees status+reason+dates for every stage; on reapplying (uncapped, any month), every document + category unlock for editing.
12. Reporting — report section shows claim details, filterable/exportable by month.

## 9. Functional Requirements & Acceptance Criteria (full FR list)

### 9.1 Recognition-Gated Access & Eligibility Window

**FR-1.1** Restrict all visibility to recognized startups.
- AC1. No Recognition ID → no entry point anywhere, direct routes blocked too, not just hidden from nav.
- AC2. Direct route call for non-recognized startup rejected server-side, not silently ignored/defaulted.

**FR-1.2** Open eligibility one month after recognition, for 12 months.
- AC1. 12 monthly windows, first eligible-from date = recognition date + 1 month.
- AC2. Month-end rounding: e.g. 31-Jan recognition → eligible-from rounds DOWN to last day of February, never rolls into March. Confirmed by Product Owner.
- Note: this is 12 monthly periods each unlocking postpaid (one month after its own period ends); touches 13 calendar-month labels as a labeling artifact only, not extra delay. Month 12 unlocks at recognition + 12 months.

**FR-1.3** Keep a month's window open until claimed.
- AC1. Never auto-expire/auto-mark-missed — claimable at any later point within the 12-month scheme.
- AC2. Months claimable out of order (e.g. Month 5 while Month 2/3 unclaimed) — no sequential requirement.

**FR-1.4** Revoked recognition closes future months only.
- AC1. No further month unlocks after revocation.
- AC2. A claim Submitted/Under Process at revocation time is untouched by the system — normal admin Reject/Sanction still applies, no special automatic behavior.
- AC3. Already-Sanctioned months unaffected by later revocation.

**FR-1.5** Admin-side migration for already-recognized startups.
- AC1. Admin can mark a specific month, for a specific startup, Sanctioned directly — no claim ever submitted for it.
- AC2. Non-migrated months remain open per the normal unlock schedule.
- Note: exact bulk-migration tooling (CSV import vs. one-by-one) is for the team to design (§15).

### 9.2 Category Selection & Fixed Amount

**FR-2.1** Category selection with fixed monthly amount.
- AC1. General = ₹20,000/month; Women-led = ₹22,000/month; PH-led = ₹24,000/month (confirmed — NOT ₹25,000).
- AC2. Changing category immediately updates displayed amount.
- AC3. Amount is SNAPSHOTTED onto the claim at submission — not a live lookup. A later rate change never alters already-submitted/sanctioned claims.

**FR-2.2** Category-conditional document requirements.
- AC1. PH-led requires disability-certificate upload; Women-led/General do not show that requirement.
- AC2. Submitting PH-led without the disability certificate is blocked.
- Note: shareholding document (FR-3.3) is mandatory for EVERY category, not just Women-led — sits alongside, not instead of, the disability-certificate rule.

### 9.3 One-Time Data Capture (First Submission)

**FR-3.1** Capture bank details once (against the startup, not a single month's claim).
- AC1. Available to verify against, without re-entry, in every later month.
- AC2. First claim blocked without complete account number, IFSC, and cheque/passbook image.

**FR-3.2** Self-declaration via downloadable template.
- AC1. Claim cannot be submitted without a self-declaration document attached.
- Note: static blank form filled by hand and re-uploaded — system does NOT pre-fill it.

**FR-3.3** Shareholding document.
- AC1. Claim cannot be submitted without a shareholding document, for EVERY category (not Women-led only).

### 9.4 Submission Rules, Rejection & Reapplication

**FR-4.1** Enforce one active claim per month.
- AC1. A new claim for a month with an existing Submitted/Under Process/Sanctioned claim is blocked.

**FR-4.2** Rejection requires a reason and reopens the month.
- AC1. Cannot mark Rejected without a reason.
- AC2. Startup sees the exact rejection reason.
- AC3. After rejection, that month's Apply action becomes available again.
- AC4. Rejection reason is free text — no structured reason code.
- AC5. On the resubmission following rejection, EVERY document (self-declaration, shareholding, disability certificate) AND the category are re-editable for that specific claim — in any month, not first-time only. This is the one exception to FR-5.1's normal month-2-onward lock.
- Note: reapplication is uncapped.

**FR-4.3** Startup-visible status timeline with dates.
- AC1. Claim view shows a date for each status passed through, not just current status.

### 9.5 Later Months — Verify & Submit

**FR-5.1** Verify-and-submit from month 2 onward.
- AC1. Claim screen shows saved details (not blank), requires explicit submit action.
- AC2. Only bank/account fields (account number, IFSC, cheque/passbook image) are editable during ordinary verification; category and previously submitted documents are read-only — EXCEPT when this claim was itself Rejected (FR-4.2 override applies regardless of month).

### 9.6 Admin Review, Download & Bulk Actions

**FR-6.1** Status only ever moves forward; no bulk download. **[AMENDED for this feature — see §18: AC3 no longer applies as written; bulk-download is now permitted alongside bulk-Sanction.]**
- AC1. No action moves Under Process back to Submitted.
- AC2. No action moves Sanctioned back to Rejected or earlier.
- ~~AC3. No bulk-download action exists — download (FR-6.3) is always single-claim; the ONLY bulk action anywhere is bulk-Sanction (FR-6.5).~~ **Superseded — see §18.**

**FR-6.2** View application details without changing status.
- AC1. Opening via "View Details" never changes status, however many times viewed.
- AC2. Only Download (not View Details) transitions Submitted → Under Process.

**FR-6.3** Download transitions a claim to Under Process.
- AC1. Downloading a Submitted application changes it to Under Process as part of that same action.
- AC2. The auto-generated Operational Cost Application PDF is included in every download, generated fresh each time.

**FR-6.4** First-download date is immutable.
- AC1. Re-downloading an already-Under-Process application does not change the recorded download date.
- Note: captured for future SLA tracking — no SLA target defined yet (§13.2, open item).

**FR-6.5** Bulk sanction after offline verification — the only bulk action. **[Note: no longer literally "the only" bulk action after §18 — bulk-download now also exists. FR-6.5 itself is unchanged and still deferred to Slice 5 in this spec.]**
- AC1. Admin can multi-select Under Process applications, mark Sanctioned in one action.
- AC2. Bulk-Sanction only offered for Under Process — Submitted must be downloaded first, one at a time. **Superseded in spirit by §18: Submitted can now be downloaded in bulk too, which is what advances it to Under Process.**
- AC3. No other bulk action anywhere (no bulk-download, no bulk-reject, no generic bulk status change). **Superseded — see §18.**
- AC4. Bulk selection works ACROSS PAGINATION — "select all" means every matching record given expected scale of thousands of startups, not just rendered rows.
- Note: single admin role handling the full review-to-Sanction flow is acceptable — no maker-checker separation required.

### 9.7 Reporting

**FR-7.1** Report section with month-wise filter and export.
- AC1. Selecting a month shows only that month's claims.
- AC2. A month with no claims shows a clear empty state, not an error/blank table.
- AC3. Admin can export the report's data.
- Note: exact report columns and export format are for the team to decide (§15).

### 9.8 Notifications

**FR-8.1** Email on every status transition into Under Process, Sanctioned, or Rejected.
- AC1. Each such transition triggers an email to the startup.
- AC2. The Rejected email includes the admin's stated reason, not just the fact of rejection.
- Note: Submitted-transition email and SMS-alongside-email are NOT yet confirmed — assumed out of scope for now.

## 10. Data Requirements (indicative, not final — team decides exact shape)

| Entity/concept | Notes | Key fields |
|---|---|---|
| `OperationalCostClaim` | One row per startup per claimed month; standard base shape (uuid, soft delete, audit timestamps, approval shape) | startup, month index, period, category (locked once set), monthly amount (snapshotted, not live), status, status timestamps (submitted/under-process/sanctioned/rejected — all startup-visible), rejection reason (free text), first-download timestamp (immutable), first-downloaded-by (actor, added per §18) |
| Category document refs | Linked to claim; shareholding mandatory for every category; disability cert PH-led only | self-declaration doc, shareholding doc, disability certificate |
| `StartupBankDetails` | Captured once per startup at first submission; only fields editable during later verify-and-submit | account number, IFSC code, cancelled cheque/passbook image ref |
| Category/amount configuration | Fixed amounts, confirmed | General ₹20,000 · Women-led ₹22,000 · PH-led ₹24,000 |
| Feature flag | New tenant-owned boolean, off by default | e.g. `operational_cost_reimbursement_enabled` |

## 11. Non-Functional Requirements

- Tenant isolation: claims live in the per-tenant DB like every other business entity — no cross-tenant read/write path.
- Auditability: every status change — INCLUDING the download-triggered Submitted→Under Process transition (a write action, not read-only) — must carry an attributable actor and timestamp.
- Rejection reasons retained permanently against a claim's history, even after a later reapplication succeeds — audit trail shows every rejection, not just the latest outcome.
- Security: admin-only download/bulk-status/report routes need real auth + role checks from day one — must NOT be modelled on `payment-management`'s access pattern (flagged Critical).
- PDF generation: reuse `PdfRenderHtmlService`, don't introduce a second PDF pipeline.
- Feature-flag discipline: gated server-side, not just hidden in UI.
- Scale: expected thousands of recognized startups — bulk-select (FR-6.5) and claims queue/report (FR-7.1) must be pagination-aware from the start.
- Roles: single admin role covering the full review-to-Sanction flow is acceptable (no maker-checker).
- DPDP: bank details visible ONLY in claim detail view, never the admin claims-queue list view. Uploaded documents viewable/downloadable by admin from detail view. Reasonable defaults (not yet checked against T-RISE's actual DPDP filing — confirm before Spec-Lock): documents/bank details encrypted at rest; only admin roles granted access to this module can view bank details/documents; uploaded files validated by type+size before acceptance. Retention period after scheme end/startup exit is a genuine open item (§13.2) — should come from the DPDP filing, not be invented.

## 12. Dependencies & Assumptions

- Depends on a reliable Recognition ID + recognition date per startup (both FR-1.1 and FR-1.2).
- Depends on `PdfRenderHtmlService` and the shared upload-module remaining available/stable.
- Application form is fixed/hard-coded (confirmed) — no admin-side field configuration.
- T-RISE is the first tenant to enable this; built generically enough another tenant could enable the same flag.
- Self-declaration signing/filling happens OUTSIDE the platform — no in-platform e-signature/form-fill.
- Eligible-expense policy is outside this system; the fixed category amount is what's approved on Sanction, not a line-item-adjudicated figure, and not a disbursement claim.
- First-time submission is a single uninterrupted sitting — NO save-and-resume/draft state required. An interrupted submission starts over.

## 13. Open Questions

### 13.1 Resolved by the Product Owner (all reflected in the FRs above — do not re-ask)

PH-led amount (₹24,000, snapshotted); shareholding scope (all categories); self-declaration template (static, not pre-filled); reject/reapply cap (uncapped, all fields unlock on that resubmission); rejection reason format (free text only); View-without-triggering-transition (yes, separate "View Details"); first-download date purpose (SLA tracking, no target set yet); bulk-Sanction starting point (Under Process only); 12-month outer boundary (none — unlock-and-stays-open model); verify-and-submit editability (bank/account only, except on rejection-triggered resubmission); category stability (locked except on rejection-triggered resubmission); form configurability (fixed, hard-coded); rejection re-editability (all documents+category unlock, any month); 12-month schedule shape (recognition+12mo, 13 calendar labels is a labeling artifact); no outer claim deadline (confirmed); amount derived-vs-snapshotted (snapshotted); bulk actions/backward transitions (none except bulk-Sanction — **amended by §18 to also include bulk-download**); notifications (email on Under Process/Sanctioned/Rejected); Sanctioned vs. paid (Sanctioned is final state, disbursement out of scope); draft/save state (not required); bank/document visibility DPDP (detail view only); month-end rounding (rounds down); revoked recognition (future months only, in-flight left to admin discretion); pre-launch recognized startups (admin migration tool); sequential claiming (not required); expected scale (thousands, pagination-aware); maker-checker (not required).

**Also resolved, 2026-09-14 (moved here from §13.2):** the eligibility-gating field (§3.3/former §13.2 item 3) — the user directly confirmed, in their own words, "yes manage with this recognition_generated_at." `startups.recognition_generated_at` (falling back to `recognition_regenerated_at` when a regeneration occurred) is the confirmed field this feature's 12-month eligibility window (FR-1.2) gates on. No longer an open item.

### 13.2 Still open — genuinely unresolved, carry into the spec's Open Questions section

1. **SLA turnaround target** — what target, if any, should the first-download date (FR-6.4) be measured against? Field is captured regardless; no SLA to report against until this is set.
2. **DPDP retention period** — how long should documents/bank details be retained after a startup's 12-month scheme ends or the startup exits early? Should come directly from T-RISE's DPDP filing, not be defaulted.

## 14. Suggested Slicing (per the Product Owner's Guide's delivery discipline)

- **Slice 1**: Recognition-gated visibility, eligibility window computation, category selection with the correct fixed amount displayed — no submission yet.
- **Slice 2**: First-time submission — documents, bank details, self-declaration, one-claim-per-month enforcement.
- **Slice 3**: Admin review — bulk status change, download-triggers-Under-Process with the immutable first-download date, and rejection with reason + reapply.
- **Slice 4**: Verify-and-submit for month 2 onward.
- **Slice 5**: Bulk-Sanction after offline verification, and the report section with month-wise export.

Priority against current roadmap: [TBD — Product Owner], left unset deliberately.

**This spec's scope = Slices 1 + 2, PLUS one item pulled forward from Slice 3 by explicit user direction on 2026-09-14 — see §18.** Download (single-claim and bulk) with its status-transition and immutable-first-download-timestamp behavior is now built in this pass. Everything else in Slices 3-5 (View Details, bulk status change beyond what download itself triggers, rejection with reason, verify-and-submit month 2+, bulk-Sanction, report/export) remains deferred exactly as before.

## 15. What This BRD Owns vs. What the Team Decides

| BRD owns (what & why) | Team decides (the how) |
|---|---|
| The problem, and who has it | Technical design — which repo/module this lives in, table/entity design |
| The outcome and its acceptance criteria | API contracts and endpoint shapes |
| Scope — in and explicitly out | UI composition and screen layout |
| Priority and slicing | How eligibility windows, PDF generation, status transitions are implemented |
| The spec's intent, approved at Spec-Lock | The code, tests, and pipeline |

## 16. Wireframes (admin + startup/frontend) — described, not embedded

Admin: claims queue (bulk "Mark Sanctioned" enabled only when every selected row is Under Process; Download always single-claim; a "First downloaded" column). Claim detail / View Details (status timeline with a date per stage; Download, Reject-with-required-reason, Sanction-when-Under-Process as separate explicit actions). Report section (month filter + export, "First downloaded" alongside "Applied on").

Startup: eligibility dashboard (category shown locked once set; a Rejected month shows a reason link + Reapply action; an unlocked month stays claimable with no re-lock). First-time application form (category tiles updating displayed amount live; PH-led's disability-certificate requirement conditional; shareholding required regardless of category; self-declaration download/re-upload). Verify & submit month 2+ (category + documents read-only, only bank details editable). Reapply-after-rejection (rejection reason shown; category, documents, bank details all unlock). Status detail (date per stage, rejection reason, Reapply action).

## 17. Appendix — Source Documents

"Operational Cost – Workflow – T-RISE" (original workflow doc); detailed user-flow dictation (Rev. 2); Product Owner's answers to Rev. 2's open questions; external review of Rev. 2 + Product Owner's answers (Rev. 3); "Sanchi Connect Product Owner's Guide"; sc-saas-ai-native specs repository (platform ground truth for §3, §11).

## 18. Amendment (2026-09-14) — FR-6.1 AC3 formally overridden for this feature

**Date:** 2026-09-14
**Reason:** Explicit user directive during spec review of the Slices 1-2 feature spec (`specs/features/SAN-756-operational-cost-reimbursement.spec.md`), given with product-owner-level authority over this BRD.
**What changed:** BRD FR-6.1 AC3 as originally written — *"No bulk-download action exists — download (FR-6.3) is always single-claim; the ONLY bulk action anywhere is bulk-Sanction (FR-6.5)"* — is **formally amended**. Bulk download (in addition to single-claim download) is now an in-scope capability, pulled forward from Slice 3 into the Slices 1-2 delivery pass, modeled on the existing admin bulk-download pattern in `sc-saas-admin/modules/application_management/submission-application-management.php` (client-side ZIP via a JSON URL manifest, `themes/default/assets/js/client-zip-downloader.js`).

**What did NOT change:**
- FR-6.3's download-triggers-transition behavior and FR-6.4's immutable first-download-date behavior apply identically whether the download is single-claim or bulk — every `Submitted` claim in a downloaded batch transitions to `Under Process`; claims already past `Submitted` in the batch download with no side effect (idempotent).
- FR-6.5 (bulk-Sanction) is unaffected and remains deferred to Slice 5 in this spec — this amendment does not pull forward bulk status-change beyond what download itself triggers.
- View Details, rejection-with-reason, verify-and-submit (month 2+), and the report/export section remain deferred exactly as before.
- The original FR-6.1/FR-6.5 text above is left historically intact (struck through/annotated inline, not deleted) — this section is the authoritative override record.

**Decision recorded (BRD "team decides" per §15):** the download bundles a single combined per-claim package (auto-generated PDF via `PdfRenderHtmlService` bundling period/category/amount/bank details, plus the claim's uploaded documents), per BRD FR-6.3's literal wording — NOT the reference precedent's two-separate-dropdown-options shape (PDF-only vs. attachments-only), since OCR has no equivalent "form PDF vs. supporting attachments" distinction to preserve. See the feature spec's Per-repo plan for the concrete endpoint/entity design.

## 19. Amendment (2026-09-14) — FR-1.1 formally extended with an admin-configurable visibility scope

**Date:** 2026-09-14
**Reason:** Explicit user directive, given with product-owner-level authority over this BRD.
**What changed:** BRD FR-1.1 as originally written — *"A startup has no Recognition ID → ... a non-recognized startup cannot see or reach the module at all"* — is **extended, not replaced**, with a new admin-configurable visibility scope. By default, visibility remains exactly as FR-1.1 originally specified (Recognition ID only). An admin may additionally enable a second setting — **"also visible to approved startups"** — which extends visibility (and visibility ONLY) to any startup whose `approvalStatus === ProfileAccountStatuses.APPROVED` (the existing general-purpose platform profile-approval status used elsewhere for program/CFA eligibility), even without a Recognition ID.

**What did NOT change:**
- **Claim submission still requires `recognized === true`, unconditionally.** This amendment only widens who can SEE the module (FR-1.1); it does not touch FR-1.2's eligibility-window computation or FR-4.1's submission rules. An approved-but-not-recognized startup can open the module but cannot submit a claim — see below for what they see instead.
- For an approved-but-not-recognized startup let in under this setting: since no `recognitionGeneratedAt` exists to anchor FR-1.2's 12 monthly windows, their eligibility grid renders with **all 12 months shown but locked/unclaimable** — a preview state, not a functional claim window. This is a genuinely new UI/API state not previously specced (neither "fully visible+functional" per original FR-1.1's recognized path, nor "404/entirely invisible" per FR-1.1's default-off path) — a third, explicit "visible but locked" state.
- FR-1.3/FR-1.4/FR-1.5 (window persistence, revocation, migration) are all still scoped entirely to `recognized` startups and are unaffected.

**Decision recorded (BRD "team decides" per §15):** this setting is implemented as a per-tenant, admin-configurable toggle stored alongside the existing self-declaration-template setting (same settings row/table, edited from the same `operation_cost` admin dashboard page) — NOT a new tenants-cockpit-owned boolean flag. Rationale: this is a narrower, single-tenant operational knob for how one already-flagged feature behaves, not a new cross-repo feature gate in its own right; it doesn't need the full flag-propagation pipeline (cockpit → backend `Feature` enum → frontend `IFeatures` → admin `config.php` constant) that `operational_cost_reimbursement_enabled` itself required. Default: **off** (Recognition-ID-only, matching the BRD's original FR-1.1 exactly) — an admin must deliberately opt in to the wider visibility.

## 20. Amendment (2026-09-14) — FR-6.2 (View Details) and FR-4.2 (Reject with reason) pulled forward from Slice 3

**Date:** 2026-09-14
**Reason:** Explicit user directive, comparing the live admin claims list against this BRD's own §16.1 wireframes (pages 17-19) and flagging the missing View Details / Reject actions directly.
**What changed:** Two more pieces of Slice 3, previously deferred by this spec's "Out of scope" section, are pulled forward into the current build, on top of the download capability already pulled forward by §18:

- **FR-6.2 (View Details)** — a read-only claim inspection view, reachable per-claim from the admin claims list, that never changes status no matter how many times it's opened. Per the BRD wireframe (§16.1, "Bamboo Weave Co. — Month 3 claim"): shows the claim's status timeline (a date per stage passed through, FR-4.3), claim details (period, category, monthly amount — all already on the claim row), bank details (account/IFSC — masked/partial per the existing DPDP note that bank details are detail-view-only, never the list view), and the list of uploaded document names. Download and Reject remain separate, explicit actions available from this same view (Sanction is explicitly NOT added in this pass — see below).
- **FR-4.2 (Reject with a required reason)** — an admin can reject a claim (from Under Process — the natural point in this flow, since Submitted claims must be downloaded first per FR-6.1/FR-6.3, which itself already only fires from this claims list) with a mandatory free-text reason (AC1/AC4). The startup-visible reason display and status-timeline (FR-4.3) are Slice-2/frontend-facing and were already partially built (the eligibility grid already renders `Submitted`/`Under Process`) — extending it to also render `Rejected` + the reason is part of this pull-forward too, on the frontend side.
- **Reapply after rejection is full FR-4.2 AC5 behavior, confirmed by explicit user directive**: a Rejected claim reopens that month, and the startup's resubmission has category and every document re-editable again (not locked), matching the BRD exactly — not a partial/simplified version.
- **Sanction (FR-6.5) is explicitly NOT part of this pull-forward** — it stays deferred, tied to bulk-Sanction and the "Under Process is a required gate" rule, which is a larger, separately-scoped piece of Slice 5. The admin claim-detail view must not show a working Sanction control in this pass.

**Architectural issue surfaced and must be resolved as part of this work, not worked around**: the SAN-756 code-review pass added a DB-level `UNIQUE(startupId, monthIndex)` constraint on `OperationalCostClaimEntity` specifically to close a submission race condition — correct at the time, since no claim could ever reach `Rejected` and therefore at most one row per (startup, month) could ever legitimately exist. Now that Reject is reachable and reapplication for the same month is required, that same blanket unique constraint would permanently block any resubmission after a claim's first rejection — a real regression this amendment must not introduce. This needs a proper redesign of the one-active-claim-per-month enforcement (e.g., a nullable "active slot" marker column unique-indexed together with (startupId, monthIndex), since MySQL/InnoDB treats each `NULL` in a unique index as distinct — letting many `Rejected` rows coexist for the same month while still hard-enforcing at most one truly active claim at the DB layer), not just a reversion to the pre-fix racy check-then-insert.

**Decision recorded (BRD "team decides" per §15):** endpoint/table design for View Details and Reject, and the one-active-claim-per-month redesign, are left to the team — see the feature spec's Per-repo plan for the concrete shape.

## 21. Amendment (2026-09-15) — Slice 4 (verify-and-submit) brought into scope, and the Rejected-transition email gap closed

**Date:** 2026-09-15
**Reason:** Following the §20 pull-forward, the user asked for a full accounting of what remained per the BRD's own slicing and directed that implementation continue with the next coherent piece.

**What changed:**
- **Slice 4 (FR-5.1) is now built**, not deferred: from Month 2 onward, a startup reviews its previously saved category, documents, and bank details, and submits without refilling from scratch (AC1); only bank/account fields are editable during this ordinary verification — category and previously submitted documents stay read-only (AC2), exactly as FR-5.1 specifies, and exactly as this BRD already specified — nothing about FR-5.1 itself is amended, it is simply no longer out of scope.
- **The FR-8.1 Rejected-transition email is now built.** §20 deferred it only because `Rejected` wasn't reachable yet at the time of that pull-forward — that reason no longer applies once Reject shipped. This closes the gap rather than leaving a claim's rejection silently unnotified to the startup, reusing the same `SesEmailService` mechanism as the existing Under-Process email (a new per-purpose method, same shape), and including the admin's stated reason in the email body per FR-8.1 AC2.

**What did NOT change:** Sanction (FR-6.5, single or bulk) and the report/export section (FR-7.1) remain deferred to Slice 5, unaffected by this amendment. The admin migration tool (FR-1.5) remains unassigned to any slice.

**Decision recorded (BRD "team decides" per §15):** the verify-and-submit endpoint/screen design (whether it's a new endpoint vs. an extension of the existing Month-1 submission endpoint, and the exact "which claim's category/documents are carried forward" resolution when a startup has multiple past claims for different months) is left to the team — see the feature spec's Per-repo plan for the concrete shape.

## 22. Amendment (2026-09-15) — real client paperwork corrects the FR-3.1/FR-3.3 document and field requirements

**Date:** 2026-09-15
**Reason:** The user shared T-RISE's actual reference forms — `Beneficiary_Details.pdf` (the real bank/beneficiary-details form) and `Self_Declaration_ShareHolding_Pattern.pdf` (the real self-declaration letterhead) — which correct two assumptions this BRD and the implementation had carried since Rev. 3.

**What changed:**

1. **Self-declaration and shareholding pattern are ONE document, not two (corrects FR-3.2/FR-3.3).** The real self-declaration template is already a combined "Declaration of Shareholding Pattern" letterhead — a startup filling it out is, in the same document, both self-declaring AND disclosing its shareholding pattern (name/DIN-PAN/designation/appointment-date/%-holding/gender/PH-status per shareholder). There is no genuinely separate "shareholding pattern document" in the real workflow. The claim form's Step 2 (Shareholding) and Step 3 (Self-declaration) are merged into one upload — a startup uploads this ONE filled letterhead, not two files.
2. **Bank details are replaced by the full Beneficiary Details field set (corrects FR-3.1).** The real form collects, all mandatory: Beneficiary Company/Firm name, Beneficiary Company/Firm Address, PAN Number, Bank Name, Bank Branch Name, Bank Account Type, MICR Code, Bank IFSC Code, Bank Account Number, Beneficiary Email ID, Beneficiary Mobile Number — considerably more than the BRD's originally-stated "account number, IFSC code, cancelled cheque/passbook image."

**What did NOT change:** the cancelled cheque/passbook image upload (FR-3.1) is still collected, now alongside the fuller beneficiary field set rather than instead of it. The disability certificate (PH-led only, FR-2.2) is unaffected and remains its own separate upload — only shareholding+self-declaration are merged, not the disability certificate.

**Decision recorded (BRD "team decides" per §15):** exact field validation (e.g. PAN format, bank account type as free text vs. a fixed Savings/Current choice) is left to the team. This is a purely additive data-model change (new columns on the existing bank/beneficiary-details entity, one fewer required document upload) — it must not touch the `operational_cost_claims` unique-index/FK structure that was the subject of the 2026-09-15 boot incident (§20/§21 history); that structure is unrelated and must be left exactly as currently deployed.

## 23. Amendment (2026-09-15) — Sanction (FR-6.5, single AND bulk) pulled forward from Slice 5

**Date:** 2026-09-15
**Reason:** Explicit user directive, comparing the live admin claim-detail view against this BRD's own §16.1 wireframe (which shows Download / Sanction / Reject as three side-by-side actions) and asking for the missing Sanction action, confirmed as full single-claim-and-bulk scope when asked directly.

**What changed:** BRD FR-6.5 (Sanction) is now built, both forms:
- **Single-claim Sanction**, from the admin's claim detail (View Details) view — a Sanction button, enabled only when the claim is currently `Under Process` (AC2's "Submitted must be downloaded first" gate still applies — Sanction is never offered from `Submitted`).
- **Bulk-Sanction**, from the admin claims list — multi-select (reusing the exact same pagination-aware "select all" infrastructure already built for bulk-download per BRD §18) then Sanction the batch in one action. Per FR-6.5 AC2, only offered when every selected row is currently `Under Process` — any row not in that state is excluded/blocked from the batch, not silently skipped without telling the admin.
- Bulk-Sanction and bulk-download now coexist as this feature's two bulk actions (both amendments to the original FR-6.1 AC3/FR-6.5 AC3 "no other bulk action" wording — already superseded once, by §18, for download; now also for Sanction). Bulk-Reject is explicitly still NOT added — Reject stays single-claim only, as it has been since §20.
- **The Sanctioned-transition startup email (FR-8.1) is included in this pass, not deferred** — the same reasoning as §21's Rejected-email fix: FR-8.1 explicitly names all three transitions (Under Process, Sanctioned, Rejected) as needing an email, and now that Sanctioned is reachable, deferring its email would just recreate the exact gap §21 already had to come back and close once for Rejected. Built proactively this time using the same `SesEmailService` pattern as the other two transition emails.

**What did NOT change:** `sanctionedAt`/`claimStatus` are existing columns on `OperationalCostClaimEntity`, provisioned from the entity's original design specifically so the full status lifecycle could be supported without a later schema change — this amendment requires **zero new columns and zero index changes** on that entity, a deliberate low-risk choice given the 2026-09-15 boot incident history on that exact table. FR-6.1 AC1/AC2 (status only ever moves forward — no reverting Under Process back to Submitted, no reverting Sanctioned to anything) are unaffected and still enforced. The report/export section (FR-7.1) remains deferred — this amendment covers Sanction only, not reporting.

**Decision recorded (BRD "team decides" per §15):** exact bulk-Sanction endpoint shape (dedicated endpoint vs. extending the download-manifest endpoint's selection-resolution logic) is left to the team — see the feature spec's Per-repo plan.
