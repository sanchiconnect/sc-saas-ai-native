# ui-ux.md — SanchiConnect Design System & UI Specification

**Spec set:** SanchiConnect canonical specification (`specs/`) · **Document:** 6 of 6
**Consolidates:** UI/UX Design Document v6 (design standards, screen catalogue), `ai-credits-ui-ux` (the credit screens), the `sc-saas-frontend` design doc (Bootstrap-5 tokens), and the Bulk Email BRD (attachment UI).
**Positioning:** the presentation layer — design tokens, navigation, the component/pattern library, and the screen catalogue across the platform's UI surfaces.

> Gaps are marked inline as **GAP · U-N** and collected in **§99** (forward-only).

---

## 1. Purpose & Scope

Defines the platform's UI: design philosophy, the design tokens actually in use, navigation and layout, the reusable component and interaction patterns, and the screen catalogue. It is the source of truth for *how the product looks and behaves at the surface*. Per-screen behaviour lives in the module and feature specs.

## 2. Design Philosophy

- **Role-based, multi-surface** — a member Frontend Portal, a tenant Administration Panel, and a platform-operator Admin Panel.
- **Minimal-training usability** — clean interfaces usable without training.
- **Data-first** — filterable tables, bulk actions, and CSV import/export on list views.
- **AI-in-workflow** — AI-assisted evaluation embedded in the program-management workflow.
- **Responsive, navigable, gated** — responsive layouts, breadcrumb navigation, and role-based access control.

## 3. Applications & Entry Points

| | Member Portal | Tenant Admin | Operator Admin |
|--|---------------|--------------|----------------|
| Repo | `sc-saas-frontend` | `sc-saas-admin` | `sanchiconnect-saas-tenants-admin` |
| Audience | Stakeholders | A tenant's operators | Sanchi's own platform staff |
| Stack | Angular PWA | PHP server-rendered | PHP server-rendered (generic CRUD engine) |
| Example URL (ref) | `thub.sanchidev.in` | `adm.thub.sanchidev.in` | `adm.tenants.sanchidev.in` |

Branding is per-tenant across the member and tenant-admin surfaces; the UI/UX v6 palette below is the **TRISE/T-Hub reference theme**, not a fixed brand.

## 4. Design Tokens — a fragmented landscape

There is **no single unified design system**; each surface has its own styling approach. This is the honest current state:

| Surface | Styling system |
|---------|----------------|
| `sc-saas-frontend` (member) | **Bootstrap 5.1.3** (stock) — 5 breakpoints (576/768/992/1200/1400), a 6-step spacer scale; per-tenant branding overlaid |
| `sc-saas-admin` (tenant admin) | **Bootstrap 4.6.1** (vendored), 4 breakpoints (576/768/992/1200); generic CRUD-engine (`add.php`/`edit.php`/`table.php`) styling layered on top as per-template inline `<style>` blocks reusing the Bootstrap 4 grid, plus a single hardcoded 576px split of its own |
| `sanchiconnect-saas-tenants-admin` (operator) | **The same vendored Bootstrap 4.6.1** as `sc-saas-admin` (byte-identical file) — confirmed 2026-07-27, correcting the "four systems" framing below: this is not a third distinct system, the two PHP admin panels are already unified with each other on Bootstrap version |
| AI-Credits screens (both panels) | A self-contained `aic-`-prefixed CSS system, brand colour from `$_SESSION['primary_color']` — confirmed 2026-07-27: redefined inline per-page across ~14 template files in both panels (no shared stylesheet), with **zero responsive breakpoints of its own** (fixed-layout, non-responsive) |

### 4.1 Reference palette (UI/UX v6, member surface)
| Token | Value | Usage |
|-------|-------|-------|
| Primary Orange | `#E65100` | Header, primary CTAs, active indicators, borders |
| Deep Blue | `#1A237E` | Section headings, links, Kanban/table headers, modal titles |
| Action Blue | `#1565C0` | Details buttons, edit icons, in-table links |
| Success Green | `#2E7D32` | Accepted/Approved/Active/ON |
| Neutral Grey | `#616161` | Pending/Draft, secondary buttons, inactive toggles |
| Alert Red | `#C62828` | Delete/Cancel, Rejected, close ticket |
| Backgrounds | `#F5F5F5` page · `#FFFFFF` cards · `#F3F4F6` table headers · `#1A237E` Kanban headers | Surface hierarchy |

### 4.2 Typography (member surface)
System sans-serif (Inter/Roboto); H1 24–28px Bold `#222`; H2 18–20px Semi-bold `#333`; table header 13px Bold `#1A237E` with sort icon; body 14px Regular `#333`; status badge 12px Medium white-on-pill; caption 12px `#888`; hyperlink 14px `#1565C0`.

### 4.3 Frontend spacing/grid (Bootstrap 5.1.3)
The member frontend's spacing and grid are stock Bootstrap 5.1.3: the five standard breakpoints and the six-step spacer scale. Four non-standard ad-hoc breakpoints exist in the app's own stylesheet as accumulated one-off fixes; future work should stick to the five stock tiers.

> **GAP · U-1 — decided 2026-07-27 (Linear SAN-58).** The Bootstrap 5 (frontend) vs. Bootstrap 4 (both admin panels, already unified with each other) split is **formally accepted as permanent** — the two surfaces are genuinely different tech stacks (Angular SPA vs. PHP+jQuery) serving different audiences (end-users vs. platform/tenant operators); unifying them would mean rewriting one stack into the other for a purely cosmetic goal with no functional bug behind it, not a real design-system migration. The CRUD-engine's per-template inline styling is also accepted as-is — low risk, no functional problem, high migration cost relative to benefit (372 + 47 template files across both admins). **The one piece worth fixing is the `aic-` system**, which is a genuine, cheap-to-fix inconsistency rather than a deliberate architectural difference: it has zero responsive breakpoints at all (fixed-layout pages sitting inside otherwise-responsive Bootstrap-4 admin panels) and is redefined inline across ~14 files with no shared stylesheet. Filed as a separate follow-up (per this issue's own acceptance criteria: migration scoped as its own work, not built here) — see Linear SAN-68: extract `aic-` into one shared stylesheet per admin repo, adopting the existing Bootstrap 4 breakpoint scale (576/768/992/1200) both panels already use everywhere else.

## 5. Navigation & Layout

- **Left sidebar** — collapsible per module group; the current item shows a dark background with white text. Groups: Dashboard, Startup Programs, Custom Programs, Facility Management, Ecosystem, Engagement, Task Management, Content Management, Performance, Support, Settings.
- **Header bar** — logo, Quick Actions, Broadcast Message, Outreach Requests (with a count badge), environment badge, Settings, user menu.
- **Breadcrumbs** — a clickable Dashboard / Module / Sub-page trail on every inner page.

## 6. Component & Pattern Library

- **List page layout** — page title, filter bar, search, records-per-page selector, sortable table with checkboxes, pagination footer.
- **Action button set** — Details, Edit (blue), Clone (green), Delete (red), in consistent order.
- **Status badges** — pill-shaped, colour-coded: green = active/approved, grey = pending/draft, red = rejected/cancelled, orange = limited access.
- **Modals** — centred overlays, tabbed (the Edit Round modal has **8 tabs**) or simple form.
- **Form fields** — labelled inputs with example placeholders, required (`*`) indicators, inline validation.
- **Toggles** — green pill ON, grey pill OFF.
- **Bulk actions** — row checkboxes → Select-All → bulk email/download/move.
- **Import/Export** — sample-CSV download, Import CSV, Export CSV on stakeholder lists.
- **Pagination** — "Showing X of Y" with a records-per-page dropdown and prev/next.

## 7. Screen Catalogue

**Member & tenant-admin (UI/UX v6):** 32 modules. Admin structure: Dashboard; Startup Programs (list, Kanban/table pipeline, the **8-tab Edit Round**, AI Analysis, Program Timeline); Custom Programs; Facility Management; Ecosystem (8 stakeholder directories, Connections Matrix/List); Engagement (Meetings, Introductions, Events, Booster Kit, Community Wall, Business Challenges, Jobs); Task Management; Content Management; Performance (Ranking, Growth Metrics, Reports, Milestones); Support; Broadcast Messages; Settings. Frontend Portal: Dashboard, Profile, Community Wall, Events, Meetings, Jobs, Programs & Challenges, Resources, Growth Metrics, Reports, Support Tickets, Account Settings.

**AI-Credits (`ai-credits-ui-ux`):** nine screens across the two PHP panels, all using the `aic-` design language.
- **Operator (`sanchiconnect-saas-tenants-admin`):** (1) Packages, (2) Task Rates — *live: AI Analysis 10, AI Rescore 2, AI Source Refresh 12 credits/unit, all "Fixed per unit"; the "Cost multiplier" option is selectable but a no-op (SAN-21)* — (3) Grants, (4) Orders (cross-tenant, read-only).
- **Tenant (`sc-saas-admin`):** (5) Overview (balance + embedded ledger), (6) Buy Credits (pack cards + custom amount + Easebuzz checkout), (7) Orders (tenant-scoped, with an Invoice column), (8) History (tenant ledger view), (9) Invoice Print.

**Bulk Email (BRD):** an attach control (button + drag-drop), a per-file list (name, size, remove/retry), a live combined-size indicator, per-file progress, a pre-send inline-vs-link delivery indication. *(As-shipped, the feature lacks malware-scan/quarantine states, link expiry, and a send gate — `design.md` D-4.)*

The **two-track program model** surfaces as separate Startup Programs and Custom Programs navigation; the **AI Analysis** screen sits inside the program pipeline.

## 8. Branding & Theming

Branding is **per-tenant** — logos, colours, login/register customisation, policies, and certificate/ID templates configured in Settings. The `aic-` credit screens read the tenant's `primary_color` from session and derive their accent from it, so they brand per-tenant even though they are a separate visual system.

## 9. Accessibility & Responsiveness

Responsive layouts are required; the member frontend uses Bootstrap 5's responsive grid. Accessibility is present but ad-hoc: `aria-label`/`role` attributes appear ~234 times in the member frontend and ~285 times in the tenant admin — component-by-component effort, not a tracked conformance target. No WCAG level, audit, or acceptance criteria exists.

> **GAP · U-2 — decided 2026-07-27 (Linear SAN-59): explicitly deferred, not a current priority.** Product owner confirmed no WCAG conformance target is being set right now — the existing ad-hoc, component-by-component `aria-label`/`role` coverage stands as-is, with no tracked target or acceptance criteria. This is a stated decision, not an oversight; revisit if/when accessibility compliance becomes a real product priority.

## 10. Source Traceability

Consolidates **UI/UX v6** (philosophy, reference tokens, navigation, patterns, the 32-module catalogue), **`ai-credits-ui-ux`** (the nine credit screens and the `aic-` system), the **`sc-saas-frontend` design doc** (Bootstrap-5 tokens), and the **Bulk Email BRD** (the attachment UI). Reconciliation is recorded in the companion Reconciliation document.

---

## 99. Gaps & Information Required

| ID | Section | Open item | Why it matters | Provider |
|----|---------|-----------|----------------|----------|
| U-1 | §4 | No unified cross-surface design system; four ad-hoc frontend breakpoints | Four styling systems; consistency and maintenance cost | Team + design |
| U-2 | §9 | Accessibility standard and target undefined | No conformance level or acceptance criteria | Product + design |

**Note (resolved):** the frontend spacing/grid is documented (Bootstrap 5.1.3), and the net-new AI-Credits UI is fully specced (nine screens); the Bulk Email attachment UI is specced with its as-shipped control gaps tracked in `design.md` D-4.

**Note (U-1, resolved 2026-07-27 — Linear SAN-58):** BS5-vs-BS4 and the CRUD-engine's inline styling are accepted as permanent (see §4). Only the `aic-` system's lack of shared stylesheet/breakpoints is being fixed, tracked separately as Linear SAN-68.

**Note (U-2, resolved 2026-07-27 — Linear SAN-59):** explicitly deferred by product owner decision, not a current priority (see §9).

*This completes the six-document canonical specification set: `program`, `design`, `knowledge`, `database`, `api`, `ui-ux`.*
