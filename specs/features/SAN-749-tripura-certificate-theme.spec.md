---
id: SAN-749
title: Government-authority certificate theme (Tripura) + statement token substitution
type: feature
status: in-progress
linear: https://linear.app/sanchiconnect/project/new-certificates-theme-for-tripura-b7327c351058
owner: sandeep.k@sanchiconnect.com
repos: [backend, admin, frontend]
contracts:
  api: ["resolveCertificateSettings() return shape — additive: certificateAddressLine, certificateSchemeLine, certificateLogoSecondary, industry sector on the certificate payload"]
  flags: []
  events: []
tenant_scoped: true
depends_on: []
created: 2026-09-10
---

# Government-authority certificate theme (Tripura) + statement token substitution

## Problem

The Directorate of Information Technology, Govt. of Tripura issues a *Recognition Certificate Under Tripura Start-Up Policy* through the platform (reference: `Rec-2026-7-060`, Jitsuninja Pvt Ltd, 13/07/2026). None of the six existing certificate themes can render it: they are all landscape, carry a single logo, and print the admin-authored statement verbatim — so per-startup values that belong *inside* the sentence (the company name, its industry sector) cannot appear at all.

The wording is legal text on a government document, so it must stay editable by a tenant admin without a release.

## Acceptance criteria

- [ ] `tripura` selectable in the certificate builder for all 9 stakeholder types
- [ ] Rendered output matches the reference PDF at A4 portrait
- [ ] Statement supports `{{startup_name}}`, `{{industry_sector}}`, `{{entity_type}}`, `{{certificate_number}}`, `{{issued_on}}`, `{{valid_till}}`
- [ ] A statement containing no tokens renders byte-identically to today
- [ ] The six existing themes render unchanged
- [ ] Renders without throwing when every setting is undefined (first paint, un-configured tenant)
- [ ] `tsc --noEmit` and `ng build` (AOT + `strictTemplates`) clean; `php -l` clean on touched admin files
- [ ] Module specs updated in both repos

## Per-repo plan

Dependency order: **backend → admin → frontend**. The frontend component can be built and previewed ahead of the backend, because the builder's preview iframe passes settings as query params.

### backend — SAN-747

`src/modules/certificates/certificates.service.ts`

- `resolveCertificateSettings()` returns a **hardcoded allow-list**; a field the admin builder saves but which is absent here is silently dropped. Add `certificateAddressLine`, `certificateSchemeLine`, `certificateLogoSecondary` — all via `pick()`, never raw `settingsMap`, or the prefix/legacy fallback is lost.
- Expose industry sector on the payload. The `certificates` entity has no such column; only a nullable `data` JSON blob.
  - **[DESIGN DECISION PENDING — dev lead]** `data` JSON (no migration, recommended) vs. a new typed column (queryable).
  - **[DESIGN DECISION PENDING — dev lead]** A certificate is a point-in-time legal record. Snapshot the sector at issuance, or join live? A live join silently rewrites already-issued certificates when a startup edits its profile.

### admin — SAN-748

`modules/certificate_builders/edit.php`, `themes/default/html/certificate_builders/edit.php`

- Add `tripura` to `$certificateThemes` (line 79). Line 385 re-syncs `spa_settings.default_data`, so existing tenants pick it up with no migration.
- **Landmine:** `modules/certificate_builder.php:98` holds a stale second copy of the list (`"default,classic,modern"`) and writes the same row at line 313. If reachable it will silently delete theme options. Resolve or confirm dead.
- Add three fields — `address_line`, `scheme_line`, `logo_secondary` — through `storageKey()` so `startup` gets bare keys and others get the `<type>_` prefix.
- Extend the preview iframe query string and the JS param map (~line 1262).

### frontend — SAN-749

`src/app/modules/sc-certificate-renderer/`

- `certificate-tokens.ts` — pure, exported `resolveCertificateTokens()`. Kept out of the theme components so the other six can adopt it later without duplication.
- `tripura-certificate/` — portrait A4 (`aspect-ratio: 1 / 1.414`), two logos, four authority header lines, justified token-substituted body, `Issue Dt.`, signatory zones. Same five `@Input()`s and `signatoriesByAlign()` as every other theme.
- Register in `sc-certificate-renderer.module.ts` and add one `*ngIf` branch to the host template.

## Design decisions taken

**Token substitution over a hardcoded sentence.** Hardcoding "This is to certify that…" into the component would freeze the legal wording behind a release and make the theme Tripura-only. The helper is ~30 lines and works for all 9 stakeholder types and all 7 themes.

**Unresolved tokens stay visible** (`KEEP_UNRESOLVED_TOKENS = true`). On a legal document a silent blank reads as missing data about the startup; a visible `{{industry_sector}}` reads as a configuration error and gets reported. One-line flip if the product owner disagrees.

**No QR code in this theme.** Every other theme renders `<qr-code>` when `certificateShowQRCode === '1'`; this one omits the block per explicit instruction (2026-09-10). The setting is *ignored*, not hidden in the builder, so enabling it for another theme still works.

**Statement is `{{ }}`-interpolated, never `[innerHTML]`.** Token values include the startup's own name, which is user-controlled, and the verification page is public. Angular escapes interpolation. Deliberate paragraph breaks use `white-space: pre-line` in SCSS rather than markup.

**Decorative frame drawn in CSS,** not an image asset, so the theme carries no asset dependency and prints predictably. A corner-flourish asset can be dropped into `.tc-frame::before` later if design supplies one.

## Must not break

- **Additive only.** New component + new `*ngIf` branch; the six existing theme components are untouched.
- **Token substitution is a no-op on token-free text** — every existing tenant's statement is plain prose.
- `globalCertiSettings` deliberately returns `{}` before load so the template can read `.X` on first paint; the new component tolerates every field being undefined.
- **Two settings sources** — preview reads query params, live reads `certificate?.settings || globalSettings?.certificate || {}`. New fields must work through both.
- `applyCertificateBranding()` writes `--color-certificate`; the theme uses that variable rather than a hardcoded colour, or the override fights it.
- Admin side: signature-preservation `unset()`, upsert-never-delete, `clearSettingsAPICache()`, PRG redirect, and the stakeholder-specific audit log all stay.
- Backend side: the `pick()` prefix/legacy fallback chain, and one-deployment-per-tenant scoping (invariant #5).

## Open questions

1. **Industry sector storage** — `data` JSON vs. new column. Blocks SAN-747.
2. **Point-in-time semantics** — snapshot the sector at issuance, or join live? Blocks SAN-747.
3. **Entity type** ("Pvt. Ltd Company") — which profile field is authoritative?

## Post-implementation polish (2026-09-14, uncommitted — awaiting user review)

Two visual-parity fixes against the reference screenshots, on top of the committed baseline (`f59c058`):

- **Row 1 vertical alignment.** `.tc-top` was `align-items: start`, top-aligning the cert-no text against the taller logos beside it; `.tc-cert-no` carried compensating `padding-top`/`margin-top` tuned for that. Changed to `align-items: center` and removed the now-redundant padding — verified against both a long (wrapped, 36-char UUID) and a short (`Rec-2026-7-060`) certificate number via headless-Chrome screenshot.
- **Secondary logo size parity.** `secondaryLogoUrl` requested a wide `w-300,h-160` ImageKit canvas while `emblemUrl` requested a square `w-260,h-260` one; both render into an identical CSS box (`object-fit: contain`), so the wide-canvas source rendered visibly shorter. Unified both getters to the same square `w-260,h-260,cm-pad_resize` transform. Verified against the real live certificate (`Rec-2026-7-060R`) — both logos now render equal size.
- **Secondary logo size parity, round 2 (same day).** The square-canvas fix above equalized the *bounding box* but not the *visible mark size*: downloaded and inspected the two real uploaded files directly — `certificate_logo` is a circular seal filling its own canvas edge to edge, `certificate_logo_secondary` is a small mark centred on a lot of baked-in white margin. `cm-pad_resize` preserves that margin, so the two 260x260 canvases still looked visibly mismatched. Added ImageKit's trim step (`t-true`) as its own chained transform stage ahead of the resize (`?tr=t-true:w-260,h-260,cm-pad_resize` — NOT `w-260,h-260,cm-pad_resize,t-true` in one group, which was tried first and instead trimmed the padding pad_resize had just added, undoing the square fit; confirmed by downloading and measuring both variants). Verified: the already-tight emblem's output is pixel-identical with or without trim; the secondary logo's visible mark now fills its square the same way.

Verification for both: `tsc --noEmit` clean, `ng build --configuration development` (AOT + strictTemplates) clean app-wide, `git status --short` on the whole `sc-certificate-renderer/` module confirms only this theme's own files changed — the six existing themes and shared host untouched. No automated test suite exists for this module (per the workspace's standing "guardian skill not yet available" substitution rule); verification is type-check + build + real-DOM/screenshot inspection, stated explicitly per process step 6.

## Notes

**Not a defect after all.** The reference PDF shows a broken image labelled "Captcha" where the QR belongs. Investigated: `grep -ri captcha` returns **zero hits across all four cloned repos**, and `<qr-code>` (`angular2-qrcode`) draws into a `<canvas>`, which has no alt text. The string does not originate in platform code. The export path (`html-to-image` `toPng()` → `jsPDF`) does not reliably capture `<canvas>`, which explains a broken image — but not the label. No bug filed; would have been a false claim. Moot for this theme, which has no QR.
