# AI Credits — UI/UX Reference (Draft)

**Document Type:** Screen-level UI/UX reference (companion to `specs/features/FT-005-ai-credits-system.spec.md`, which covers architecture/data-flow, not screen-by-screen UI)
**Status:** DRAFT — grounded entirely in direct reads of the live templates; not yet reviewed by a designer or product owner
**Date:** 2026-07-17
**Origin:** Closes the AI-Credits half of external gaps-register item **U-3** ("net-new UI is unspecced in the design system") — the Bulk Email Attachments half was already closed via `sc-saas-admin/specs/features/bulk-email-attachments/ui-ux.md`. As with U-1/U-2, no unified cross-platform "design system §4-6" exists anywhere in this workspace to fold this into — this document instead specs the AI-Credits screens on their own terms, the same way the Bulk Email Attachments doc already does for its feature.

---

## Two audiences, two repos, one shared visual language

AI-Credits has screens in **both** of the workspace's PHP admin panels, serving two different people:

- **Platform operator screens** — `sanchiconnect-saas-tenants-admin` (`adm.tenants.sanchidev.in`), gated to Super Admin/Developer roles only (see `specs/Operator-Persona-and-Scope.md`). The operator manages the commercial catalogue itself: packages, task rates, promotional grants, and a read-only view of every tenant's orders.
- **Tenant-facing screens** — `sc-saas-admin` (each tenant's own admin panel). A tenant's own administrator views their wallet balance, buys credit packages, and reviews their own purchase/consumption history.

Both sets of screens share the identical hand-rolled CSS design language, prefixed `aic-` (confirmed by an explicit comment at the top of every template: `/* ── AI Credits — analysis-page design system ── */`). This is a **self-contained visual system scoped only to AI-Credits pages** — it does not reuse either admin panel's own broader conventions (`sc-saas-admin`'s Bootstrap 4 theme, `sanchiconnect-saas-tenants-admin`'s generic CRUD-engine styling) and is not shared with any other feature area in either repo. Worth flagging on its own: whoever built this feature designed a distinct visual identity for it rather than extending the surrounding admin panel's existing look.

## Shared design conventions (both repos, all 9 screens)

- **Dynamic brand color**: every page reads `$_SESSION['primary_color']` (falling back to `#2563eb`) and derives `--aic-primary` plus three opacity tints (`--aic-primary-10/20/30`) via inline `<style>` — the same tenant-branding mechanism used elsewhere in the platform, applied consistently across every AI-Credits screen.
- **Page shell**: `.aic-page` (light gray `#f7f8fa` background, full viewport height) → `.aic__header` (white card, breadcrumb + title/subtitle + action button) → `.aic-snav-wrap` (a horizontal tab strip linking between that repo's AI-Credits sub-pages) → one or more `.aic-card` content blocks.
- **Tables**: `.aic-tbl` — uppercase gray column headers, 15px row text, subtle row-hover highlight, no zebra striping.
- **Status badges**: `.aic-badge`, pill-shaped, uppercase, color-coded consistently by meaning across every screen: green (`#047857` on `#ecfdf5`) = active/paid/credit, red (`#b91c1c` on `#fef2f2`) = failed/debit, amber (`#92400e`/`#c2410c`) = pending/reserved/created, gray = archived/inactive/expired.
- **Search + pagination toolbar**: `.aic-toolbar` — a live client-side text filter (`.aic-srch-in`, filters visible rows via a `data-search` attribute on each `<tr>`, no server round-trip) plus, on paginated tables, a per-page `<select>` that reloads with a `perpage` query param.
- **Modals**: `.aic-modal` — a gradient header strip in the brand color (`.aic-mhd`), white body, footer with Cancel + a solid brand-color primary action button. Used for Add/Edit Package.
- **Destructive actions confirm via SweetAlert2** (`Swal.fire(...)`), not a native `confirm()` — consistent with the rest of both admin panels' established convention.
- **Empty states**: a large light-gray FontAwesome icon + a one-line message, centered, no call-to-action button in most cases (Buy Credits' empty state is the one exception — it explains *why* nothing is there: "The platform operator hasn't published any AI credit packages yet").

---

## Operator screens (`sanchiconnect-saas-tenants-admin`)

All four share one `.aic-subnav` tab strip: **Packages | Task Rates | Grants | Orders**.

### 1. Packages (`ai_credits/packages`)
**Purpose**: manage the purchasable credit-package catalogue tenants see on their own Buy Credits screen.
**Layout**: a payment-currency toggle card (INR/USD radio pills + Save) above the main table — confirms `sanchiconnect-saas-tenants-admin`'s CLAUDE.md-documented direct DB access, since this setting is read from/written to the shared tenants DB. Table columns: rank/position, package name (+ optional "Featured" star badge and highlight-tagline subtext), Credits (pill), Price (INR) with a computed ₹-per-credit rate shown as secondary text, Price (USD, optional, shows "—" if unset), Status (Active/Archived), Actions (Edit, Archive).
**Add/Edit modal**: Name, Position (display order), Credits, Price (INR), Price (USD, optional), Highlight Feature (short tagline), Description (long text), a **live rate-per-credit calculator** that updates as Credits/Price are typed, and two toggle switches (Active, Featured).
**Archive** (not delete) requires a SweetAlert2 confirmation; archived rows stay visible in the table at reduced opacity rather than disappearing.

### 2. Task Rates (`ai_credits/task_rates`)
**Purpose**: set how many credits each AI operation type costs. **Confirmed live via an operator-shared screenshot** (2026-07-17): 4 task types configured — AI Analysis (10 credits/unit), AI Thesis Generation, AI Rescore (2), AI Source Refresh (12) — all in "Fixed per unit" mode.
**Layout**: a table (Task Type, Rate Mode badge, Credits/Unit, Updated By, Actions) with an Edit modal per row: Task Type (read-only, shown as a name + a monospace code chip, e.g. `ai_analysis`), Credits/Unit (number input), Rate Mode (a `<select>` offering **"Fixed per unit"** and **"Cost multiplier"**, with inline help text: *"Fixed/unit — flat credits deducted per task call. Cost multiplier — credits scale with actual LLM USD cost."*), Description (optional).
**Known issue, not a UI bug**: the "Cost multiplier" option is fully present and functional *in this UI* — an operator can select it and save it — but it is a silent no-op on the consuming side (see `FT-005`'s Open Questions and Linear issue SAN-21). The UI itself doesn't misrepresent anything; the disconnect is between this screen's stored setting and the reserve/settle logic that ignores it.

### 3. Grants (`ai_credits/grants`)
**Purpose**: issue one-off promotional/onboarding credit grants to one or more tenants at once.
**Layout**: two-column — a grant-issuance form (left, `col-lg-4`) beside a searchable grant history table (right, `col-lg-8`).
**Form fields**: Domains (multi-select via `chosen.js`, populated from real tenant records — a tenant picker, not free text), Credits to Grant, Grant Type (`<select>`: Onboarding, Promotional, Support, Referral, Other — matching `AiGrantType`), Reason (required textarea), Promo Reference (optional), Expires At (optional date picker, "Leave blank for no expiry" — this is the one place `ai_credit_grants.expires_at` is actually set by a human, though per FT-005's K-1 finding it's then never enforced by any consuming code).
**Idempotency**: a hidden `grant_idem_token` field, regenerated per page load — a defense against double-submission, consistent with the submit-button-disables-on-click pattern in the footer script.
**History table**: Date, Tenant (name + monospace domain chip), Credits (green `+N` chip), Type (color-coded badge), Reason (truncated with a hover tooltip for the full text), By (issuing operator), Expires (formatted date or "Never").

### 4. Orders (`ai_credits/orders`)
**Purpose**: a **read-only** cross-tenant view of every AI-credit purchase order on the platform.
**Layout**: a stat strip (Total Orders, Paid, Revenue in the configured currency, Credits Sold, Pending, Failed) above a status-filter pill row (All/Created/Paid/Failed/Expired) above the table.
**Table columns**: Date, Domain (monospace chip), Package (resolved from the order's `package_snapshot` JSON, not a live join — so a since-renamed/deleted package still displays its name at time of purchase), Credits, Amount (currency-aware symbol/decimals), Currency badge, Status badge, Gateway Txn ID (monospace, or "—").
**Pagination**: server-side, with a per-page selector (10/20/50/100) and a numbered pager (±2 pages around current).

---

## Tenant screens (`sc-saas-admin`)

Shared `.aic-subnav`: **Overview | Buy Credits | Orders** (History is a separate page reachable from Overview, not in this same tab strip — confirmed by reading each template's own subnav markup independently).

### 5. Overview (`ai_credits/overview`)
**Purpose**: the tenant's wallet dashboard — current balance, reserved balance, and a transaction ledger.
**Layout**: a stat block showing `balance` and `reserved_balance` (both read directly off `ai_credit_wallets`) plus a "Buy Credits" call-to-action button in the header, then a ledger table.
**Ledger table columns**: includes a Type badge distinguishing CREDIT (green), DEBIT (red), RESERVE (amber), REFUND (brand-color tint) — matching the `AiCreditType` enum exactly — and a right-aligned Balance After column, giving a running-balance view of every wallet movement.

### 6. Buy Credits (`ai_credits/buy`)
**Purpose**: the tenant's purchase flow — pick a package, check out via Easebuzz.
**Layout**: a card grid (one card per active package, "Available packages" count in the header stat), each card showing the package name, credits, price, and a full-width "Buy Now" button.
**Checkout data carried client-side**: buyer name/email/phone/address/city/state/pincode are pre-filled from the tenant's last successful order (`$this->lastOrderBuyer`, passed to the page as a JSON blob for the checkout form to read) — sparing a returning buyer from re-typing billing details every purchase.
**Empty state** is the one screen with explanatory copy rather than a bare icon+message, since an empty catalogue here means the *operator* hasn't published anything yet — a state the tenant admin can't fix themselves.

### 7. Orders (`ai_credits/orders`, tenant-scoped)
**Purpose**: the tenant's own purchase history (distinct from the operator's cross-tenant Orders screen above, despite the identical page name).
**Table columns**: adds an **Invoice** column (a "View Invoice" link to `ai_credits/invoice_print?order_uuid=...` plus the invoice number as secondary text) not present on the operator's version — the operator's cross-tenant view has no invoice concept since invoices are per-tenant financial documents.

### 8. History
**Purpose**: appears to be a tenant-facing ledger/transaction-history view distinct from Overview's embedded ledger table — confirmed to exist as its own routed page (`ai_credits/history`) with its own `.aic-tbl` and search box, but this pass did not fully reconcile what, if anything, differs in scope from Overview's own ledger table. `[NOT SPECIFIED IN SOURCE — requires a closer diff between overview.php's and history.php's queries]`.

### 9. Invoice Print (`ai_credits/invoice_print`)
**Purpose**: a printable invoice for a completed order, linked from the tenant Orders screen. Not read in full detail in this pass — noted for completeness since it's a real, routed screen. `[NOT SPECIFIED IN SOURCE]`.

---

## Open Questions

1. Item 8 above (History vs. Overview's ledger) and item 9 (Invoice Print's actual layout/fields) were not fully traced in this pass — a follow-up read of both templates would close this document out completely.
2. Should this document be merged into `FT-005-ai-credits-system.spec.md` directly, or kept as a separate UI-focused companion (mirroring how Bulk Email Attachments keeps `ui-ux.md` separate from `design.md`/`api.md`)? This document assumes the latter.
3. The self-contained `aic-` design language (distinct from either admin panel's own established look) — was this a deliberate design decision, or should AI-Credits screens be restyled to match each panel's native conventions? Not something this document can determine.

---

## Change Log

- 2026-07-17 | Initial draft, closing the AI-Credits half of external gaps-register item U-3. All 7 fully-read screens (Packages, Task Rates, Grants, Orders ×2, Overview, Buy Credits) grounded in direct template reads; Task Rates cross-confirmed against a live operator screenshot. History and Invoice Print flagged as not fully traced rather than guessed at.
