---
id: SAN-786                     # Linear Project created (team: Sanchiconnect); anchored to its lowest-numbered
                                 # per-repo issue, SAN-786 (tenants). Full issue set: SAN-786 (tenants), SAN-787 (admin).
title: Startup Grant Release Letter — Admin PDF Download
type: feature
status: in-review
linear: https://linear.app/sanchiconnect/project/startup-grant-release-letter-admin-pdf-download-c08ce3782ae3
owner: nirmal.s@sanchiconnect.com
repos: [tenants, admin]
                                 # No backend/frontend change — Evidenced: sibling `call_for_applications_download_*`
                                 # flags have zero presence in sc-saas-backend's Feature enum and zero presence in
                                 # sc-saas-frontend's IFeatures (see Contracts & invariants).
contracts:
  api: []                       # None — no new/changed sc-saas-backend routes. Evidenced: this feature reads the
                                 # tenant DB directly via Medoo (admin's existing pattern), same as the sibling
                                 # call_for_applications_download_* precedent.
  flags:
    - "startup_grant_release_format_download_enable"
  events: []
tenant_scoped: true
depends_on: []
created: 2026-09-15
---

# Startup Grant Release Letter — Admin PDF Download

## Problem

`sc-saas-admin`'s Application Detail page (`application-submission-detail.php`) already lets an admin download a generic "Application Submission" PDF (a plain label/value field dump — Evidenced, `sc-saas-admin/modules/application-submission-detail.php:330-459`). The user (Nirmal Singh) wants a second, purpose-built download option that produces a formal government-style **Grant Release Letter** — addressed to a program's grant authority, carrying a tenant logo, the applicant's name, organization name, Recognition No., and Applied Date — reproducing the exact format of an attached reference PDF (a Tri-Seed Fund / Tripura Start-Up Policy release letter). Today no such letter format exists anywhere in the codebase; the only PDF output is the generic field dump.

**User-facing ask (verbatim):** "start the implementation of Application details download functionality within provided format from Application Detail page."

## Resolved scope decisions (do not re-litigate)

These were made directly by the requesting user and are recorded here as settled design, not open questions:

1. **Scope — Evidenced (user directive):** the letter format applies to **all programs, unconditionally**. Every application's "Download" dropdown on Application Detail can produce this letter when the new flag is on. Not scoped to Tri-Seed Fund, no per-program toggle.
2. **Logo — Evidenced (user directive):** **one tenant-wide logo**, held on a single settings page, used on every generated letter regardless of program.
3. **Flag name and ownership — Evidenced (user directive, exact string given):** `startup_grant_release_format_download_enable`, a new boolean column on `sanchiconnect-saas-tenants`'s `TenantUsersEntity` — "this feature is handled from tenants features," per the user. Cockpit-owned per workspace invariant #1.
4. **Template must not be hardcoded — `[INFERRED — requires validation]`, but follows directly from decision 1 and is treated as resolved design, not open:** since the letter now must serve arbitrary programs (not just Tri-Seed Fund), the body text — currently only imagined as hardcoded government/policy wording (addressee, policy name, grant amount) — must be an **admin-editable template**, stored alongside the logo on the same tenant-wide settings page, with documented placeholders: at minimum `{{applicant_name}}`, `{{organization_name}}`, `{{recognition_no}}`, `{{recognition_date}}`, `{{applied_date}}`, `{{program_name}}`. It defaults to wording that reproduces the reference PDF's exact current text, so Tri-Seed Fund keeps working exactly as shown today with zero admin action required.

## Acceptance criteria

- [x] A new `startup_grant_release_format_download_enable` boolean column exists on `TenantUsersEntity`, default `false`, following the exact shape of `call_for_applications_download_pdfs_enabled` (no `Feature` enum entry in `sc-saas-backend`, no `IFeatures` entry in `sc-saas-frontend`, no `config.php` `define()` in `sc-saas-admin`).
- [x] With the flag off (or unset), the "Download Grant Release Letter" option is absent from the Application Detail download dropdown — server-side route also refuses direct hits, mirroring the existing `download_pdf` handler's own flag check.
- [x] With the flag on, a new, distinct download option appears in the same dropdown as the existing "Download as PDF" option, without altering that existing option's behavior, flag, or gating.
- [x] An admin with the appropriate role can, from the existing `developer/settings_management.php` page (already `super_admin_role_id`/`developer_role_id`-only, `:5-13` — no new role-gating to build), upload one tenant-wide logo image and edit the letter-body template text, via two new `spa_settings` rows seeded idempotently — per the user's explicit direction to manage this from the existing Settings Management page, not a new one.
- [x] The two new settings rows are seeded exactly once per tenant (existence-guarded, never overwrites an admin's already-saved `setting_value` on subsequent boots) — Evidenced pattern, `gtagEventsSettings()`, `includes/core_functions.php:7926-7980`.
- [x] The template defaults, out of the box (no admin action), to wording that reproduces the reference PDF's Tri-Seed Fund letter text with placeholders substituted for applicant name, organization name, Recognition No., recognition date, applied date, and program name.
- [x] Generating the letter for a given application substitutes all six documented placeholders with real values sourced from the tenant DB (see Per-repo plan — admin) and renders them into the admin-edited (or default) template.
- [x] The generated PDF embeds the tenant logo as a base64 `data:` URI — never a live/signed S3 URL passed to dompdf.
- [x] The generated PDF uses the same dompdf mechanism (`\Dompdf\Dompdf`, `Options->set('isRemoteEnabled', true)`, `setPaper('A4','portrait')`) already used by the existing `download_pdf` handler and the bulk/proforma precedents — no new PDF library introduced.
- [x] The existing generic "Download as PDF" option's behavior, flag (`call_for_applications_download_pdfs_enabled`), and output are completely unchanged by this work.
- [x] Certificate Builder and ID Card Builder modules are untouched by this work.
- [x] **Added 2026-09-16, follow-up request:** the same letter is downloadable in bulk from the Application Management list's existing "Download" dropdown, reusing the established client-side-zip-via-manifest pattern (`get_bulk_grant_letter_urls`) — no server-side PDF-generation duplication, since the manifest points at the same single-application `download_grant_letter` route.
- [x] **Added 2026-09-16, follow-up request:** the letter fits on one page for a normal-length template — signature block ("Yours faithfully" onward) is right-aligned and split from the body, and blank lines between paragraphs (including `\r\n`-normalized ones from a template resaved via the Settings Management textarea) are collapsed to single line breaks.

## Per-repo plan

### tenants

- Add one new column to `TenantUsersEntity` (`sanchiconnect-saas-tenants/src/modules/tenants/entities/tenant-users.entity.ts`), following the exact pattern of the most recently added flag of this same admin-only shape, `operational_cost_reimbursement_enabled` (lines 2315-2321) and, further back, the `call_for_applications_download_*` trio (lines 2168-2190):

  ```ts
  @Column({
    type: 'boolean',
    name: 'startup_grant_release_format_download_enable',
    width: 1,
    default: false,
  })
  startup_grant_release_format_download_enable: boolean;
  ```

- **Evidenced — no other tenants-side change needed.** `call_for_applications_download_pdfs_enabled` / `_download_attachments_enabled` / `_download_reports_enabled` have zero presence in `sc-saas-backend/src/core/constants/enum.ts`'s `Feature` enum and zero presence in `sc-saas-frontend/src/app/core/domain/brand.model.ts`'s `IFeatures` — confirmed by direct inspection. This new flag follows the identical shape: cockpit column only, consumed directly by `sc-saas-admin` off `$brandSettings`.
- No migration tooling exists in this repo (`synchronize: true` in prod per this repo's own CLAUDE.md) — the column applies automatically on next boot. No other tenant is affected until an operator sets it (default `false`).

### admin

**1. Settings — REUSE the existing generic `developer/settings_management.php` framework, no new module or table.** `[CORRECTED 2026-09-16 — supersedes the original "new module" design below the user explicitly redirected: "manage according to https://.../developer/settings_management"]`

Evidenced — read in full: `sc-saas-admin/modules/developer/settings_management.php` + `includes/settings_fields_generator.php`. This is a generic, per-tenant admin settings framework already storing arbitrary key/value settings in the `spa_settings` table, grouped into sections by a `type` column, with a `data_type` column selecting the rendered field widget — including `upload_image` (`generateUploadImageField()`, `settings_fields_generator.php:161-185`, already does the S3 upload + preview + "Change"/"Remove" UI) and `textarea` (`generateTextaraField()`, `:76-88`). Both widgets, the file-upload handling, and the settings-value read/write round-trip already exist and need **zero new code** for the plumbing — only two new setting rows and a seeding function.

- **Two new `spa_settings` rows**, seeded idempotently on page load, mirroring `gtagEventsSettings()` EXACTLY (`includes/core_functions.php:7926-7980` — existence-guarded insert-or-sync-schema-fields, NEVER touches `setting_value` once a row exists, called once from `settings_management.php:222` alongside the existing `gtagEventsSettings($database)` call):
  - `setting_name = 'startup_grant_release_letter_logo'`, `data_type = 'upload_image'`.
  - `setting_name = 'startup_grant_release_letter_template'`, `data_type = 'textarea'`, seeded with `setting_value` = the default template text reproducing the reference PDF's Tri-Seed wording (with the six placeholders substituted in) — so it renders correctly in the textarea and generates correctly with zero admin action, on first boot, for every tenant.
  - Both rows share one new `type` section (working name `startup_grant_release_letter` — renders as its own "Startup Grant Release Letter" section per `format_names()`'s underscore-splitting convention, same as gtag's own `analytics_/_tracking` section name choice).
- **File upload — already fully handled by `settings_management.php`'s existing `updateSetting` POST handler** (`:136-206`): `$_FILES['data']['name'][$post_key]` keyed by `setting_name`, uploaded via `S3Client::putObject` to `"settings/" . $post_key . "-" . md5(time()) . "." . $extension` with `ACL => 'public-read'` (`:146-170`), and the relative key written into `spa_settings.setting_value` (`:172-198`). No new upload code needed — the existing generic handler already does this for every `upload_image` setting.
- **Read-back for display**: `generateS3FileUrl($value)` (`includes/core_functions.php:3311-3323`) already turns the stored relative key into a public, unsigned URL (`imagekit_url` CDN prefix — no expiry, since the upload's ACL is `public-read`) for the settings page's own preview `<img>`. The new dompdf handler (below) reads the SAME stored value directly off `spa_settings` and fetches it itself for embedding — it does not need `generateS3FileUrl()`'s browser-facing form, just the raw relative key to build the fetch URL or S3 call.
- **Role-gating and the tenant-flag gate are already exactly what this feature needs, unmodified**: `settings_management.php` is already `super_admin_role_id`/`developer_role_id`-only (`:5-13`); the new section simply appears alongside every other settings section once the two rows exist — no additional role check to add. (Optional, not required: hide the new section when `startup_grant_release_format_download_enable` is off, by filtering `$settingsArray` before it reaches the template — a small, easy addition if wanted, but not load-bearing since the settings page overall is already admin-role-gated.)
- Documented placeholder list (`{{applicant_name}}`, `{{organization_name}}`, `{{recognition_no}}`, `{{recognition_date}}`, `{{applied_date}}`, `{{program_name}}`) shown via the existing `placeholder_text`/`info_text` columns on the seeded textarea row (matches the 100-char `info_text` limit noted in the gtag precedent's own comment — keep it short, point to fuller docs elsewhere if needed).

**2. New dompdf letter-generation handler** — new `case` in `modules/application-submission-detail.php`, alongside the existing `download_pdf` handler (`:330-459`):
- Fetch the tenant logo from S3 to a temp file server-side (`tempnam()` + `streamS3ToFile()`, the exact helper already used at `submission-application-management.php:2118-2123`) and embed as `data:<mime>;base64,...` — **never** a live/signed URL inside dompdf's HTML. This mirrors both `submission-application-management.php`'s bulk PDF image-embed strategy and `finance_management/proforma_invoices/generate.php:579-612`'s supplier-logo embed (that one uses a signed-URL fetch via cURL rather than a raw S3 stream — the newer, safer pattern in `submission-application-management.php`/`operation_cost` style S3 access is preferred for this new handler).
- Look up the two settings values directly off `spa_settings` (`setting_name IN ('startup_grant_release_letter_logo', 'startup_grant_release_letter_template')`) — no separate table, per the corrected design above. Decrypt `setting_value` first if `$_ENV['encrypt_settings'] == "yes"`, matching `settings_management.php:258-264`'s own read pattern.
- **New `startups` join, added specifically for this handler** — Evidenced: `application_program_submission_rounds_view` (`includes/table_views_functions.php:214-226`) joins `application_program_submission_rounds` → `application_program_rounds` → `forms_submissions` → `users`, carrying `s.user_id AS submission_user_id`, but has no `startup_id` column and no join to `startups` at all today. Add a follow-up query (or an ad hoc join) keyed off `submission_user_id`:
  ```sql
  SELECT recognition_id, recognition_generated_at, recognized
  FROM startups WHERE user_id = :submission_user_id
  ```
  (columns confirmed on `startups` entity, `sc-saas-backend/src/modules/startup/entities/startup.entity.ts:203-241`: `recognition_id` varchar unique nullable — the full assembled string, e.g. `"Rec-2026-7-060"`; `recognition_generated_at` timestamp nullable — the "Dated-" value. **Use `recognition_generated_at` only — NOT `recognition_regenerated_at`, not even as a fallback.** Hard-won lesson from this same workspace, this same week (SAN-756/OCR work): `recognition_regenerated_at` is null on a startup's first recognition, so any `recognitionRegeneratedAt || recognitionGeneratedAt`-style fallback silently breaks the common case — OCR's own eligibility-date logic had to be corrected away from exactly this pattern.) Precedent for the general shape of a startups↔users join: `includes/portfolio_functions.php:103` (`startups LEFT JOIN users ON startups.user_id = users.id`).
- **Applicant name / organization name / applied date do NOT require `forms_submissions.data` JSON parsing** — Evidenced, `includes/submission_export_helpers.php:27-38`: `application_program_submission_rounds_view` already exposes `name` (applicant name, from `forms_submissions.name`), `company_name` (organization name, from `forms_submissions.company_name`), and the submission's own timestamp column (used there as `submitted_on`) directly as plain columns on the view row — no JSON decode needed for these three fields.
- Substitute the six documented placeholders into the admin-edited (or default) template string, render via the same `\Dompdf\Dompdf` / `Options->set('isRemoteEnabled', true)` / `setPaper('A4','portrait')` setup as the existing handler (`:420-428`), and stream the output using the same chunked-flush pattern (`:430-442`) for progress-bar compatibility.
- Wrap in the same `try/catch` + output-buffer-flush error pattern as the existing handler (`:445-458`).

**3. New download option in the UI** — add a new `<a class="dropdown-item js-submission-download">` entry to the dropdown in `themes/default/html/application-submission-detail.php` (alongside the existing entries starting `:361`), gated by:
  ```php
  $__grantLetterDlEnabled = ($this->brandSettings["startup_grant_release_format_download_enable"] ?? '0') == '1';
  ```
  (default `'0'`, unlike the existing PDF/attachments/reports flags which default `'1'`/`'0'` per their own historical rollout — this is a brand-new capability, so it must default OFF even if `$brandSettings` doesn't yet carry the key). Wire the dropdown-visibility `if` condition (`:352`) to also account for this new flag so the dropdown itself appears when only this option is enabled.
- Exact label text is an Open question (see below); working label "Download Grant Release Letter."

**4. Explicitly not touched:** the existing `download_pdf` handler, its flag, and its output; Certificate Builder; ID Card Builder; `config/config.php` (no new `define()`).

**5. Bulk download — added 2026-09-16, follow-up request (supersedes the original "Out of scope" line for this item):**
- New manifest endpoint `get_bulk_grant_letter_urls` in `modules/application_management/submission-application-management.php`, mirroring the existing `get_bulk_pdf_urls` exactly but flag-gated on `startup_grant_release_format_download_enable` and pointing each entry's URL at the same single-application `download_grant_letter` route above — no new PDF-generation code, since the browser fetches and zips each letter client-side via the existing `ClientZipDownloader` pattern.
- New "Download Grant Release Letters (.zip)" option in the bulk download dropdown (`themes/default/html/application_management/submission-application-management.php`), flag-gated the same way.
- The `.js-bulk-download` click handler's manifest-URL selection was a hardcoded two-way ternary (`pdf` vs. everything else); extended with a `data-manifest` HTML attribute override (checked first, falling back to the original ternary) so this third manifest-backed kind didn't need another branch — the two pre-existing buttons are unaffected since they don't set `data-manifest`.

**6. Letter pagination/alignment — added 2026-09-16, follow-up request:** the signature block ("Yours faithfully" through "Applied Date"/value) is split off by its literal marker text and right-aligned via CSS, matching the reference PDF; body `line-height` was tightened then later reverted to the browser default per explicit feedback, the logo's max size was increased, and blank lines between paragraphs are collapsed to single line breaks (normalizing `\r\n`/`\r` to `\n` first, since a template resaved through the Settings Management textarea comes back with CRLF endings that a plain `\n{2,}` regex wouldn't collapse).

## Contracts & invariants

- **Flags:** `startup_grant_release_format_download_enable` — new flag, `tenants`-owned, defaulting `false`. **Deliberately not propagated** to `sc-saas-backend`'s `Feature` enum or `sc-saas-frontend`'s `IFeatures` — Evidenced precedent: the sibling `call_for_applications_download_*` trio (and `operational_cost_reimbursement_enabled`'s own admin-only nav check) already establishes that an admin-only, Medoo-consumed flag has no backend/frontend obligation. This is a deliberate, confirmed exception to the flag's normal 4-consumer propagation checklist (invariant #1) — the flag has exactly one real consumer, `sc-saas-admin`, reading it inline off `$brandSettings`.
- **API:** none. No `sc-saas-backend` route added or changed. This feature is entirely `sc-saas-admin` (PHP + Medoo + direct S3) reading the tenant DB directly, same access pattern the sibling `call_for_applications_download_*` flags and the `operation_cost` settings page already use.
- **Events:** none.
- **Invariants at risk:**
  - **Flag names (#1):** new flag, cockpit-first, but intentionally NOT propagated beyond `tenants` → `admin` — documented above as a confirmed, precedented exception, not an oversight. `/trace-flag` should be run at implementation time and is expected to report "admin-only, no backend/frontend consumer" as a pass, not a gap.
  - **API contract (#2):** unaffected — no backend route touched.
  - **Tenant scoping (#5):** `sc-saas-admin`'s existing per-request tenant-DB-selection mechanism (`admin_domain` → tenant DB, per this repo's own CLAUDE.md) already scopes every Medoo query in this feature; the new settings table and the new `startups` join both live inside that same per-tenant connection — no cross-tenant read risk introduced.
  - Auth (#4), the tenant-verification contract (#3), and the cross-workspace PowerPitch contract (#6) are unaffected.

## Test plan

- tenants: manual verification the new column appears in `verify_tenant`/`tenant-settings` responses, default `false`.
- admin: `php -l` on all new/edited files. Manual QA: (1) with the flag off, confirm the new dropdown option is absent and a direct URL hit to the new handler 404s; (2) with the flag on and no settings row yet, confirm the letter renders with the built-in default template text and no logo (graceful placeholder/blank, not a fatal error); (3) upload a logo + edit the template, confirm the next-generated letter reflects both; (4) generate the letter for a recognized startup with a real Recognition No. and confirm all six placeholders substitute correctly; (5) confirm the existing "Download as PDF" option is completely unaffected (same output, same flag) before and after this change; (6) confirm Certificate Builder / ID Card Builder pages are untouched.
- cross-repo: with the tenant flag off, confirm zero visible change anywhere on Application Detail; with it on, walk logo+template upload → generate letter for a Tri-Seed-style application → confirm output visually matches the reference PDF's layout/wording with real data substituted.

## Rollout

1. Add the flag column in `tenants` first (default `false`) — inert until an operator sets it.
2. Deploy `sc-saas-admin`'s two seeded `spa_settings` rows + dompdf handler + new dropdown option, flag-gated — inert on every tenant until the flag is explicitly enabled.
3. Enable `startup_grant_release_format_download_enable` for the requesting tenant only; verify end-to-end (including a real Tri-Seed-style application) before considering any other tenant.

## Out of scope

- Any change to `sc-saas-backend` or `sc-saas-frontend` — confirmed unnecessary per the sibling-flag precedent.
- Per-program letter formats or per-program logos — decision 1/2 above rule this out explicitly.
- Any change to the existing generic "Download as PDF" option, Certificate Builder, or ID Card Builder.
- Any payment-gateway, sanction, or fund-disbursement workflow — this is a document-generation feature only.

**Scope correction, 2026-09-16:** bulk/multi-select generation was originally scoped out above ("only the single-application Application Detail page is in scope"). Per an explicit follow-up request ("action is visible for single application but not visible for bulk download... fix this"), this was implemented after all — see the new acceptance criteria and the Per-repo plan (admin) addendum below. The existing bulk PDF handler in `submission-application-management.php` itself is still untouched; a new, separate manifest endpoint was added alongside it.

## Open questions

Resolved by the requesting user on 2026-09-16 (recorded here, not re-litigated):

- **Settings storage:** reuse the existing `developer/settings_management.php` page and `spa_settings` table — no new module, no new table. See the corrected Per-repo plan (admin) above.
- **UI label:** confirmed as "Download Grant Release Letter."
- **Template editor:** confirmed plain textarea (not rich-text/WYSIWYG).

Still open — explicitly deferred by the requesting user ("this will bind later"), not resolved now:

- **Recognition-No.-less startups:** should an application whose startup has no `recognition_id` (not yet recognized) be blocked from generating this letter, show a placeholder value, or fall back gracefully? The reference PDF assumes a recognized startup with a real Recognition No. **Interim behavior for this build** (safe default, not a business-rule decision): render the letter with a plain placeholder (e.g. an em dash or "Not yet recognized") wherever `recognition_id`/`recognition_generated_at` is null, rather than blocking generation or throwing an error — never fabricate a fake Recognition No. This interim choice is explicitly provisional and must be revisited once the real business rule is decided; do not treat this placeholder behavior as final.

Three of the four items above are resolved; the Recognition-No.-less interim behavior is intentionally left open per the requesting user's own instruction ("this will bind later") and does not block this spec — the interim placeholder behavior is implemented and treated as provisional, to be revisited once the real business rule is decided.
