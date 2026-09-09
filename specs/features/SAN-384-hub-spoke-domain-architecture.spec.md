---
id: SAN-384                     # Linear Project created (team: Sanchiconnect); anchored to its lowest-numbered
                                 # per-repo issue, SAN-384 (tenants). Full issue set: SAN-384..SAN-390.
title: Multi-Tenant Hub/Spoke Domain & White-Label Architecture
type: feature
status: in-progress             # 2026-08-20: the `tenants` (SAN-384), `tenants-admin` (SAN-385),
                                 # `frontend` (SAN-386), `backend` (SAN-387) and `admin` (SAN-388)
                                 # slices are implemented and in review; the two remaining per-repo
                                 # slices (SAN-389, SAN-390) are untouched.
                                 # Approved by the document owner 2026-08-20 to begin implementation. Zero blocking Open Questions (VideoSDK's
                                 # domain-management API, once unconfirmed, was confirmed real 2026-08-19 —
                                 # see Decision #3) — moving to `approved` remains an explicit call for the
                                 # document owner.
linear: https://linear.app/sanchiconnect/project/multi-tenant-hubspoke-domain-and-white-label-architecture-1e2f8bf1555d
owner: nirmal.s@sanchiconnect.com
repos: [tenants, tenants-admin, frontend, backend, admin, power-pitch-sanchiconnect-api, sc-saas-3rdparty-webservices]
                                 # dependency order per the approved plan's Sequencing section. NOTE:
                                 # `power-pitch-sanchiconnect-api` is outside this workspace's declared 7-repo
                                 # `repos:` subset (it lives in the sibling SanchiPowerpitch workspace) — added
                                 # here anyway because the plan gives it real, code-verified scope (workspace
                                 # invariant #6, PowerPitch cross-workspace contract).
contracts:
  api:
    - "GET public/global/resolve-domain/:hostname (sanchiconnect-saas-tenants, NEW — strict superset of the existing GET public/global/verify_tenant/:hostname at global.controller.ts:20-24)"
    - "POST domain-orchestration/sync (sanchiconnect-saas-tenants, NEW, internal-api-key guarded)"
    - "CRUD under /cors-domains (sanchiconnect-saas-tenants, NEW, internal-api-key guarded)"
    - "GET partner-branding/:abbreviation (sc-saas-backend, NEW, public)"
    - "POST/PUT partner-branding (sc-saas-backend, NEW, authenticated, gated by @Features([Feature.HUB_SPOKE_DOMAIN_ENABLED]))"
    - "New scoped Backdoor URL issue/redeem route(s) (sc-saas-backend, partner-domain-access module, NEW — exact path TBD at implementation; explicitly NOT the existing NIR-5 getBackdoorLogin at admin-actions.controller.ts:254)"
    - "POST/GET/DELETE v1/externals-admin/tenants (power-pitch-sanchiconnect-api, NEW, internal-api-key guarded, deliberately not behind the existing ExternalHostInterceptor)"
    - "POST video-sdk/domains (sc-saas-3rdparty-webservices, NEW)"
    - "Partner abbreviation availability check (sc-saas-backend, NEW — mirrors checkEmailAlreadyExists()'s {isExist, message} shape, path TBD at implementation; consumed by both sc-saas-frontend's registration form and sc-saas-admin's new partner-portal settings page's client-side JS, if wired directly rather than via a server-side PHP check)"
    - "PATCH partner/profile-equivalent self-service abbreviation-change route (sc-saas-backend, NEW, authenticated by the existing partner-session JWT guard — added for completeness/consistency; sc-saas-admin's own settings page does not call it, see Per-repo plan)"
    - "Added 2026-08-19: sc-saas-backend becomes a new CONSUMER of the cockpit's /cors-domains CRUD API (added above) — a new cross-repo call direction not previously in this spec, used only by the new partner-cors-domain-push.service.ts after a partner self-registers with an abbreviation"
  flags:
    - "hub_spoke_domain_enabled"   # NEW column on TenantUsersEntity (sanchiconnect-saas-tenants), default
                                    # false. Corrected 2026-08-20: this spec originally proposed reusing the
                                    # existing `incubator_module_enabled` column as the master gate, believing
                                    # it to be dormant. Re-traced via /trace-flag immediately before
                                    # implementation and found to be FALSE — `incubator_module_enabled` is
                                    # already live today, gating unrelated existing functionality (a partner/
                                    # program-office nav item in sc-saas-frontend, and partner-promotion UI
                                    # blocks + custom table columns in sc-saas-admin). Reusing it would have
                                    # meant any tenant already relying on those existing features got this
                                    # entire new architecture (subdomain routing, CORS, branding, the new
                                    # backdoor mechanism, data-visibility scoping) turned on immediately on
                                    # deploy, with no staged/pilot rollout — a real regression risk, not a
                                    # hypothetical. This spec now defines its own, independent flag instead.
  events: []
tenant_scoped: true
depends_on: []
created: 2026-08-19
---

# Multi-Tenant Hub/Spoke Domain & White-Label Architecture

## Reference

This spec did **not** originate from a pre-existing Linear issue. It was authored from a rough set of
action items the document owner (Nirmal) raised about a real, already-observed "Hub/Spoke ecosystem"
white-label pattern (incubator hubs, e.g. `thub.sanchidev.in`, with affiliated partner-org "spokes" at
subdomains like `aaf.thub.sanchidev.in`), then explored in depth across `sanchiconnect-saas-tenants`,
`sanchiconnect-saas-tenants-admin`, `sc-saas-backend`, `sc-saas-admin`, `sc-saas-frontend`, and the sibling
PowerPitch workspace via plan mode, and approved by the document owner as the architecture below. Every
file/line reference in this spec was re-verified directly against the live code during authoring (see
Corrections / Evidence, below) — nothing here is inferred from the plan text alone.

## Corrections / Evidence (spot-checked while authoring this spec)

1. `PartnerEntity.abbreviation` — confirmed exactly as the plan describes: `nullable: true, unique: true`,
   with a doc-comment already stating "Hub is `partnerId IS NULL`... Spoke is `partnerId IS NOT NULL`,
   using this abbreviation" (`sc-saas-backend/src/modules/partner/entities/partner.entity.ts:84-93`). No
   separate Hub/Spoke master table exists — this is the entire mechanism today, just unused for
   routing/CORS/branding.
2. `verify_tenant` route confirmed at `GET public/global/verify_tenant/:hostname`
   (`sanchiconnect-saas-tenants/src/modules/global/global.controller.ts:11-24`, controller prefix
   `public/global`) — the new `resolve-domain/:hostname` route sits alongside it under the same prefix.
   Frontend's existing call site confirmed at `api-endpoint.service.ts:274`
   (`` `${ApiEndpointService.GLOBAL}verify_tenant/` ``) — exactly the one line the plan calls out to swap.
3. **Corrected 2026-08-20, via `/trace-flag` re-run immediately before implementation:** the flag this
   spec originally proposed reusing (`incubator_module_enabled`, `tenant-users.entity.ts:1253-1259`,
   `default: false`) is **not** dormant — it's already read in `sc-saas-frontend`
   (`brand.model.ts:158`'s `IFeatures`, `navMenus.ts:697`'s `program-office-team` nav gate,
   `public-layout-sidebar.component.html:205`'s "Admin Console" nav gate) and in `sc-saas-admin`
   (`modules/common.php:492`, `application_management/program.php:1740,1760` — partner-promotion UI and
   custom table columns), for functionality unrelated to this feature. Reusing it would couple this
   feature's entire rollout to whatever state that flag already holds for existing tenants — a real
   regression risk, not a hypothetical, since the whole premise of this spec's rollout plan is "off by
   default for every tenant until explicitly enabled." This spec now defines its own new column,
   `hub_spoke_domain_enabled` (same shape: boolean, `default: false`, on `TenantUsersEntity`), genuinely
   unused anywhere yet — confirmed by the same `/trace-flag` pass finding zero references to this exact
   new name anywhere in the workspace, as expected for a not-yet-created column.
4. `sc-saas-backend`'s `Feature` enum confirmed at `enum.ts:1024`, `SCREAMING_SNAKE_CASE = 'snake_case'`
   convention (e.g. `STARTUP = 'startups'`) — the new member will be `HUB_SPOKE_DOMAIN_ENABLED =
   'hub_spoke_domain_enabled'`, matching both the existing naming convention and the real flag name.
5. `ses-email.service.ts`'s `sendInstantEmailInvitationEmail()` confirmed at line 2494, with the exact
   `registration_url: getUserTypeRegistrationUrl(...)` call the plan names at line 2556 (a second,
   out-of-scope occurrence exists at line 2699 in a different email method — untouched by this feature).
6. `getBackdoorLogin` confirmed as pre-existing, real code at `admin-actions.controller.ts:254` /
   `admin-actions.service.ts:2584` (the tracked NIR-5 vulnerability) — the new Backdoor URL mechanism in
   this spec is verified to be new, separate code, not a proposed edit to this file.
7. `sanchiconnect-saas-tenants/src/main.ts`'s `getCorsDomain()` (line 148) and the `origin` callback
   (line 67) confirmed as the plan describes — a static array built once at boot.
8. `THIRD_PARTY_SERVICE_BASE_URL` confirmed as a real `saasSettings` key (`enum.ts:1111`); the existing
   `videoSDK` module in `sc-saas-3rdparty-webservices` (`videoSDK.controller.ts`/`.service.ts`/`.module.ts`)
   confirmed present, so the new `videoSDK-domain.*` files are additive siblings, not a new top-level module.
9. **`partner_id` confirmed on every ecosystem stakeholder entity** (`StartupEntity`, `InvestorEntity`,
   `MentorEntity`, `CorporateEntity`, `ServiceProviderEntity`, `IndividualEntity`,
   `ProgramOfficeMemberEntity`), on `ProgramsEntity` (`programs` table), and on `ApplicationProgramsEntity`
   — all `int, nullable: true`, no ORM-level FK to `PartnerEntity` except `UserEntity` (which has a real
   `@ManyToOne`). `PartnerEntity`'s own doc-comment (Evidence #1) states the design intent verbatim: Hub =
   `partnerId IS NULL`, Spoke = `partnerId IS NOT NULL`. Note: "government" is not a real stakeholder
   entity/table in this repo (only a contact-category enum value) — out of scope for partner-scoping until
   it exists as a real module.
10. **Registration-side `partnerId` stamping is fully implemented** for every stakeholder type
    (`auth.service.ts:908-1450`) — a `RegisterUserDto` carrying `partnerUUID` correctly resolves the
    partner and stamps `partnerId` on the new stakeholder record today. The gap is entirely on the
    **invite** side: the partner-self-invite route (`partner.service.ts` `inviteInstantUser`) already
    auto-derives `partnerUUID` from the inviter's own session; the **Hub-admin invite route**
    (`admin-actions.controller.ts` `invite-users[-instant]/:adminMd5`, the one "invite from a stakeholder's
    detail page" actually hits) has **no server-side partner-context derivation at all** — confirmed by
    tracing `adminInviteUsersInstant` (`admin-actions.service.ts:3205-3227`) straight to
    `sendInstantEmailInvitationEmail(inviteUsersDto)` with no `partner` argument.
11. **Existing partner-scoped filtering is real but narrow and inconsistent** — `search.service.ts` (one
    occurrence per stakeholder type, e.g. line 173) correctly scopes ecosystem-stakeholder search results
    when the *viewer's own account* is `accountType === 'partner'`, gated by
    `Feature.STAKEHOLDER_ACCESS_MANAGEMENT` + a `StakeholderAccessType` setting on `PartnerEntity`. Two real
    gaps confirmed by direct trace: (a) the plain `programs` module's listing endpoint
    (`program-management.service.ts` → `programs.repository.ts:71-100`) has **zero** `partnerId` filtering
    of any kind; (b) the `application_programs` listing endpoint
    (`application-program.controller.ts:73-82`) does have correct partner-scoping SQL in its repository
    (`application-programs.repository.ts:97-146`, `partnerId ? (partnerId = X OR promoteWithPartners
    CONTAINS X) : partnerId IS NULL`), but it is driven by an **untrusted client-supplied `?partnerId=`
    query param**, not the authenticated session — any logged-in user can pass any partner's ID. This is a
    real data-exposure gap, confirmed by direct code trace; per the document owner's explicit decision, it
    is tracked as its own separate bug-fix issue (see Out of scope), not folded into this feature's rollout.
12. **The JWT/session payload only carries `partnerId` for `accountType === 'partner'` accounts**
    (`auth.service.ts:320-365`) — a startup/investor/mentor/corporate/service-provider/individual user's
    own stakeholder-record `partnerId` is never echoed onto their session/JWT today. This is the concrete
    gap this spec's new Hub-vs-Spoke visibility scoping closes (see Per-repo plan, backend).

## Problem

Sanchiconnect's incubator "hubs" (tenants) each have affiliated "spoke" partner organizations addressed
today at partner-specific subdomains (e.g. `aaf.thub.sanchidev.in`, `myb.thub.sanchidev.in`,
`abaf.thub.sanchidev.in` under the Anand Foundation hub). This subdomain/white-label pattern currently
works only by accident of DNS/infra: no code anywhere in the platform resolves a spoke subdomain to its
tenant+partner, issues it CORS access, brands it, or generates registration/invite/email links that point
at it. `PartnerEntity.abbreviation` already exists for exactly this purpose but is unused for
routing/CORS/branding [Evidence #1]. CORS is enforced independently and staticly in three places (cockpit,
backend, PowerPitch), each a hand-maintained env var or dead code [Evidence #7], meaning every new tenant
or spoke domain today requires a manual `.env` edit and a redeploy. This spec formalizes real,
DB-backed (no-redeploy) CORS domain management, Partner-Subdomain resolution and branding, subdomain-aware
registration/invite/email links, and automated push of new domains to the two third-party services that
also need to know about them (both PowerPitch and VideoSDK now have confirmed real APIs for this, with a
defensive manual-fallback branch for call failures) — built additively, gated behind a new, dedicated
`hub_spoke_domain_enabled` flag [Evidence #3] (not the pre-existing `incubator_module_enabled`, which
already gates unrelated live functionality — see Evidence #3), so no existing tenant's behavior can
regress.

## Decisions (confirmed with the document owner)

1. **Hub = tenant, Spoke = Partner-within-that-tenant.** A spoke subdomain is
   `{partner.abbreviation}.{tenant.domain}` — not a separate full tenant, and not the same mechanism as
   the existing `is_patent_hub`/`patent_hub_allowed_domains` tenant-to-tenant pattern (do not conflate the
   two).
2. **`ses-email.service.ts`'s one call-site** gets a narrow 1-line conditional edit (swap to the
   partner-aware URL helper when `partner?.abbreviation` is set and the flag is on) rather than a forked
   duplicate email method.
3. **VideoSDK domain automation is a real, confirmed API integration — resolved 2026-08-19.** The document
   owner confirmed VideoSDK's domain-management API: `POST https://api.videosdk.live/v1/apikeys/{apiKeyId}/domains`,
   `{ domain }` body, auth via a self-signed JWT (same mechanism this workspace already uses for the
   VideoSDK meetings integration — see Per-repo plan). This supersedes the earlier manual-fallback-only
   design; the fallback path is kept as a defensive branch, not the primary design.
4. **PowerPitch's own CORS config is explicitly out of scope.** Only its `x-hostname`/
   `ExternalTenantsEntity` allowlist gets automated via the new `external-tenants-admin` module; the
   existing `origin: true` + dead domain list in PowerPitch's `main.ts` is untouched.
5. **The new Backdoor URL mechanism is new, properly-scoped code** (short-lived ~5 min, single-use, bound
   to one issuing admin + one target user + optional partner) — it must not touch or extend the existing
   NIR-5 `getBackdoorLogin` vulnerability [Evidence #6].
6. **Hub-vs-Spoke data-visibility scoping is gated behind `hub_spoke_domain_enabled`**, consistent with
   this whole spec's additive/gated philosophy: JWT/session `partnerId` propagation for all stakeholder
   account types, `programs`-module listing filtering, and any other new scoping logic in this feature are
   all no-ops for a tenant that hasn't enabled the flag [Evidence #12].
7. **The `application_programs` client-supplied-`?partnerId=` data-exposure gap [Evidence #11] is real but
   explicitly tracked as its own separate bug-fix issue**, not bundled into this feature's rollout — per
   the document owner's decision, to keep this already-large rollout's blast radius contained. See Out of
   scope.
8. **Hub-admin invite-from-stakeholder-detail-page partner auto-derivation is sourced from the stakeholder
   being viewed** (that stakeholder's own `partnerId`, if set) — not from the new spoke-subdomain routing
   session context (§ backend/admin plan below), so this works immediately and does not depend on the
   subdomain-resolution middleware being live first.
9. **Added 2026-08-19 — Partner abbreviation is settable at self-registration and editable afterward from
   the Partner Dashboard**, not only by a Hub admin. Confirmed with the document owner: a Partner
   self-registering (`sc-saas-frontend`'s `/auth/register?userType=partner` flow) sees an abbreviation
   input pre-filled by auto-suggestion from the organization-name field they're already entering, editable
   before submit; and the same field becomes editable later from a new self-service page in their own
   Partner Dashboard (`sc-saas-admin`'s `modules/partners/` portal — confirmed by direct code trace this
   session to have **no** existing self-service profile/settings page at all today, only read-only stats).
   **Author's design decisions, not separately re-confirmed, made to fit this cleanly into the existing
   architecture:**
   - Auto-suggestion reuses the exact existing convention (first 3 letters of the name field, uppercased)
     already used in `sc-saas-admin`'s generic add/edit templates [Evidence #1] — implemented three times
     (frontend registration form, the new partner-portal settings page, and the existing admin templates
     already have it), not shared as code across repos/languages, but kept behaviorally identical.
   - Availability is checked via a new, friendly pre-check endpoint (mirroring the existing
     `checkEmailAlreadyExists()` pattern in `auth.service.ts:1529-1561` — a `{isExist, message}` response,
     not a raw unique-constraint error), callable live from both the registration form and the new
     settings page.
   - If a partner submits registration with the abbreviation field left blank (e.g. JS disabled, or they
     cleared the suggestion), the backend auto-generates one server-side using the same
     proactive-check-before-write retry pattern already established in this codebase for an equivalent
     unique-per-tenant, auto-derived-but-editable field —
     `startup-recognition-id-generation.service.ts`'s `assembleUniqueCode()` (`:321-357`) — not the
     backfill's batch-oriented 3→4→5→id fallback chain (that one is for a one-time script processing many
     rows unattended; this one is interactive, one row at a time, so a check-then-suggest loop fits better).
   - **Changing an already-set abbreviation later must deactivate the old Spoke `cors_domains` row, not
     leave it dangling.** Every sync call site (the four already listed in the admin per-repo plan, plus
     the new registration-triggered one below) sets the old row `active = false` when the value actually
     changes, rather than deleting it — preserving audit history, consistent with this spec's
     `source`-tagging philosophy elsewhere.
   - **A self-registered partner's abbreviation needs a new sync path, since none of the existing three
     PHP call sites fire for it.** Partner self-registration happens entirely in `sc-saas-backend`
     (NestJS), which has no direct connection to the cockpit's shared tenants DB where `cors_domains`
     lives — unlike the PHP admin's direct-Medoo writes. This needs a new, best-effort HTTP call from
     `sc-saas-backend` to the cockpit's **already-designed** `cors-domains` CRUD API (no new cockpit
     endpoint required — the tenants section of this spec already specifies a full CRUD controller),
     authenticated via the same `InternalApiKeyGuard` shared secret already designed for that controller.
     Fire only when the abbreviation is non-empty; failure is logged and does not block registration
     success (matching the "no distributed transaction, independently retryable" philosophy already used
     for the PowerPitch/VideoSDK pushes elsewhere in this spec).
10. **Added 2026-08-19 — the Hub-side broadcast approval queue must show the Spoke's chosen recipient
    filters, not just title/partner/actions.** This is properly SAN-392/394's own scope (Spoke Broadcast
    Messages with Hub Approval), not this spec's — recorded here only as a cross-reference since it was
    raised in the same message; see that spec for the actual change.

## Acceptance criteria

- [ ] A staging spoke hostname resolves via the new `GET public/global/resolve-domain/:hostname` to the
      correct tenant **plus** `partnerAbbreviation`; the same tenant's root hostname still resolves
      byte-identically to today's `verify_tenant` response.
- [ ] `sc-saas-frontend`'s tenant-verification call site now targets `resolve-domain/` instead of
      `verify_tenant/`; every existing (non-spoke) tenant's bootstrap behavior is unchanged (regression
      check run first, before any spoke-hostname test).
- [ ] A new `cors_domains` row, once added and cached, allows its origin through both the cockpit's and
      the backend's CORS `origin` callbacks; an origin not present in either the static whitelist or the
      dynamic registry is still rejected by both.
- [ ] Removing/deactivating a `cors_domains` row stops that origin being allowed once the in-memory cache
      TTL (~30s) elapses — not instantly, and this delay is documented, not a bug.
- [ ] A tenant's Hub CORS domain row is created/updated correctly regardless of which of the two tenant
      save paths was used — the new `tenant_management` module **or** the old generic engine
      (`add/tenant_users`, `edit/tenant_users/:id`) — verified by exercising both paths in staging, not
      just the new module.
- [ ] A partner's Spoke CORS domain row is created/updated correctly regardless of which save path set
      `abbreviation` — the generic engine's edit-plain/edit routes **or** the new Domain & Branding tab —
      verified by exercising all reachable paths in staging.
- [ ] The one-time backfill action, run once against staging, first generates and persists a unique
      `abbreviation` for every existing partner that doesn't already have one (never overwriting an
      existing value), then produces a `cors_domains` row (tagged `source = 'backfill'`) for every
      domain-shaped field already populated on every existing tenant, and for every partner's
      `abbreviation` (pre-existing or just backfilled); re-running it a second time changes nothing
      (upsert, not duplicate rows, and no partner that already has an `abbreviation` gets a new one). A
      tenant whose stored DB credentials are stale/unreachable is logged and skipped, not allowed to abort
      the run for every other tenant.
- [ ] With `hub_spoke_domain_enabled` off (the default for every existing tenant), `sc-saas-backend`'s new
      `partner-subdomain.middleware.ts` is a confirmed no-op — zero observable behavior change for any
      current tenant or partner.
- [ ] With the flag on and a partner's `abbreviation` set, a request to that partner's subdomain resolves
      `req.resolvedPartner`, and `GET /partner-branding/:abbreviation` returns that partner's branding
      (logo, header logo, favicon, primary/secondary/danger/success colors, login/register side images) —
      field-for-field parity with the existing tenant-wide `spa_settings` branding shape.
- [ ] A real test invite sent through a partner with an `abbreviation` set delivers an email whose
      `registration_url` points at the spoke host; a partner-less invite's email is byte-identical to
      today's.
- [ ] The program registration "Copy URL" in `sc-saas-admin` returns the partner-subdomain URL when a
      partner context applies, and the existing (non-partner) URL otherwise, including the existing
      `program_request_type == 'external'` verbatim-URL override being preserved unchanged.
- [ ] `POST /domain-orchestration/sync` writes the `cors_domains` row and returns independent
      per-step (PowerPitch / VideoSDK) success-or-failure status — a failure in one step does not roll
      back or block the other, and the registry row itself is written regardless of downstream push
      outcomes.
- [ ] Approving a domain successfully calls VideoSDK's confirmed `POST /v1/apikeys/{apiKeyId}/domains`
      endpoint (self-signed JWT auth, reusing this workspace's existing `createVideoSDKtoken()`-equivalent
      mechanism) and the orchestration response reflects VideoSDK's real success/failure status. If that
      call fails for any reason (auth, network, VideoSDK-side error), the orchestration response falls
      back to surfacing `{status: 'manual_action_required', domain}` verbatim, visible as a plain
      checklist line in the `sanchiconnect-saas-tenants-admin` sync UI — the fallback is now a defensive
      branch for call failures, not the primary path.
- [ ] The new Backdoor URL mechanism issues a token that is single-use, expires (~5 min), and is bound to
      one issuing admin + one target user (+ optional partner) — reusing an already-redeemed or expired
      token fails closed. The existing NIR-5 `getBackdoorLogin` endpoint is untouched by this feature.
- [ ] At least 3 concurrent spokes under one hub (mirroring the real `aaf`/`myb`/`abaf` example) resolve,
      brand, and CORS-authorize independently, with no cache/singleton state bleed between them.
- [ ] `hub_spoke_domain_enabled` is enabled on at most one production tenant (pilot) as part of this
      feature's initial rollout, only after a full staging pass on cloned real-tenant data.
- [ ] With the flag on, a non-`partner`-accountType stakeholder user's JWT/session carries their own
      stakeholder record's `partnerId` (or `null` for a Hub stakeholder); with the flag off, the session
      shape is byte-identical to today for every account type.
- [ ] With the flag on, the `programs` module's listing endpoint returns only Hub-owned programs
      (`partnerId IS NULL`) to a Hub-affiliated viewer and only that partner's own programs to a
      Spoke-affiliated viewer; with the flag off, behavior is unchanged (no filtering, matching today).
- [ ] Inviting a user from a stakeholder's detail page in `sc-saas-admin`, where that stakeholder has a
      `partnerId` set, results in the registered user's own new stakeholder record also carrying that same
      `partnerId` — closing the invite-side gap [Evidence #10] end-to-end.
- [ ] A partner self-registering via `sc-saas-frontend` sees an abbreviation field pre-filled from their
      organization name, can edit it before submit, and their new `PartnerEntity` row lands with that
      value — or, if left blank, a server-generated unique one. A duplicate abbreviation is rejected with
      a friendly message before submit, not a raw DB error after.
- [ ] The new self-service page in the Partner Dashboard (`modules/partners/settings.php`) lets a partner
      view and change their own `abbreviation` post-registration; saving with a value already taken by
      another partner in the same tenant is rejected with a clear error and no partial write.
- [ ] Changing an already-set `abbreviation` (from any of the four sync call sites) deactivates the old
      Spoke `cors_domains` row (`active = false`) rather than deleting it, and creates/activates the new
      one — verified by changing a partner's abbreviation in staging and confirming both rows' states.
- [ ] A self-registered partner's Spoke domain reaches `cors_domains` via the new backend-to-cockpit push,
      without requiring any PHP admin action — verified end-to-end in staging: register a new partner
      with an abbreviation, confirm the corresponding row appears in the cockpit's CORS Domains list.

## Per-repo plan

### tenants (`sanchiconnect-saas-tenants`) — Linear: SAN-384

- **New flag column (corrected 2026-08-20 — see Evidence #3):** `TenantUsersEntity` gets a new
  `hub_spoke_domain_enabled` column (`@Column({ type: 'boolean', name: 'hub_spoke_domain_enabled', width:
  1, default: false })`), matching the exact shape of the existing `incubator_module_enabled` column this
  spec originally (incorrectly) proposed reusing. This is a genuinely new flag — not a rename of the old
  one, which stays exactly as-is for its own existing, unrelated consumers in frontend/admin. Run
  `/trace-flag hub_spoke_domain_enabled` again once this column exists, before any consumer repo is
  deployed, to confirm it reads back cleanly through `verify_tenant`/`tenant-settings` the same way
  `incubator_module_enabled` already does.
- New `src/modules/cors-domains/` — `cors_domains` table (`id`, `domain` unique, `domain_type`
  [`hub`|`spoke`|`api`|`admin`|`other`], `tenant_id` nullable FK, `source` [`manual`|`auto_partner`|`backfill`],
  `active`, timestamps), DTOs, repository, service, controller, `module.spec.md`. **One tenant can own
  multiple rows here** — per the document owner, `TenantUsersEntity` carries seven distinct domain-shaped
  columns (`domain`, `customDomain`, `apiDomain`, `apiUrl`, `admin_domain`, `admin_custom_domain`,
  `adminUrl`), because the platform supports both a default `*.sanchiapp.com`-style domain and a fully
  custom white-label domain per tenant — today's hand-maintained `CORS_DOMAINS` env var already lists all
  of them, not a fixed 3-field triplet, and this registry replaces that env var one-for-one, not a subset
  of it. Duplicate-domain guard mirroring `tenants-admin`'s `tenant_management` convention. In-memory
  cache (`getCachedOrigins()`, ~30s refresh) so the CORS `origin` callback stays synchronous.
- New `src/core/guards/internal-api-key.guard.ts` — shared-secret guard for this controller and the
  orchestration controller below.
- New `src/modules/global/services/domain-resolver.service.ts` +
  `src/modules/global/controllers/domain-resolver.controller.ts` — `GET
  public/global/resolve-domain/:hostname`: tries the existing exact `verify_tenant`-style match first
  (byte-identical response for every current tenant hostname), and on a miss strips the leftmost
  subdomain label and retries; on that second hit, returns the same payload plus `partnerAbbreviation`.
- New `src/modules/domain-orchestration/` — `POST /domain-orchestration/sync`: writes a `cors_domains`
  row, then best-effort pushes the domain to PowerPitch and VideoSDK, returning per-step success/failure
  (no distributed transaction; each step independently retryable).
- **Existing file — required touch:** `src/main.ts` — OR the new `CorsDomainsService.getCachedOrigins()`
  check into the existing `origin` callback (line 67) alongside the static whitelist built by
  `getCorsDomain()` (line 148). Zero behavior change until a row exists (registry starts empty).
- **Existing file — required touch:** `src/app.module.ts` — register the three new modules (additive
  import-array entries only).

**Implementation notes (recorded 2026-08-20, after the slice was built — no scope change, these only
record what the code actually does so the downstream repos are not written against a guess):**

- **`InternalApiKeyGuard` already existed** at exactly the specified path
  (`src/core/guards/internal-api-key.guard.ts`) — added by FT-005/SAN-54 for the AI-Credits routes, and
  already exactly the described mechanism (`x-internal-api-key` vs `AI_CREDITS_INTERNAL_API_KEY`,
  `timingSafeEqual`, fail-closed when unset). It is **reused**, not rewritten. Downstream callers
  (SAN-385's PHP sync, SAN-387's `partner-cors-domain-push.service.ts`) must send the value of
  `AI_CREDITS_INTERNAL_API_KEY` — the config key keeps its historical name.
- **Real route paths carry this repo's global prefix and URI version:**
  `/api/v1/public/global/resolve-domain/:hostname`, `/api/v1/cors-domains[...]`,
  `/api/v1/domain-orchestration/sync`.
- **Every `/cors-domains` route is guarded, reads included** (not only writes): a listing enumerates
  every tenant's and partner's hostnames, and this repo has no session identity to scope it by — same
  reasoning already applied to the AI-Credits invoice reads.
- **`resolve-domain` duplicates `verify_tenant`'s match query but NOT its ~600-line response builder.**
  `DomainResolverService` runs its own cheap `select(['tenant.id'])` probe to decide hit-vs-strip, then
  delegates payload construction to `GlobalService.verifyTenant()`. Duplicating the payload builder
  would have made the "byte-identical for every currently-resolvable hostname" requirement (Contracts &
  invariants #3, this spec's highest-risk invariant) impossible to hold the first time a flag column is
  added to that select list. `verify_tenant`'s own route/controller/service method is untouched.
- **A label is stripped only while at least two labels would remain** — `sanchidev.in` must never
  degrade to `in`, whose `LIKE %in%` match would resolve to an unrelated tenant. Exactly one label is
  ever stripped.
- **The flag reaches consumers via `tenant-settings`, not `verify_tenant`.**
  `hub_spoke_domain_enabled` was added to `getTenantSettings()`'s hand-maintained `select: [...]` list
  (one additive line) so `sc-saas-backend`'s `Feature` gate can actually see it; `verifyTenant()` is
  untouched, and the frontend branches on the presence of `partnerAbbreviation` per this spec's
  Contracts section. Without that line the column would exist in the DB and be invisible to every repo.
- **The PowerPitch and VideoSDK push steps are TODO stubs** returning
  `{status: 'manual_action_required', domain}` — the same shape the real integrations fall back to on
  failure — pending SAN-389 and SAN-390 respectively. The `cors_domains` write is fully implemented.
- **Deferred to SAN-385 (that repo's own line item, not edited here):** the tenants-admin generic CRUD
  engine renders forms from `spa_data_management` field metadata, so an operator-facing toggle for the
  new column needs a metadata row there before it is flippable from the operator UI.

### tenants-admin (`sanchiconnect-saas-tenants-admin`) — Linear: SAN-385

- New module `modules/cors_domain_management/` (`list.php`, `create.php`, `edit.php`, `setup_menu.php`,
  `module.spec.md`) — mirrors the existing `modules/tenant_management/` conventions (direct Medoo
  read/write against the shared DB, hand-validated duplicate-domain guard).
- New `includes/cors_domain_sync_functions.php` — a new function `syncTenantCorsDomain($tenantId,
  $tenantRow)`, that upserts one `cors_domains` row per **non-empty** domain-shaped field on the tenant —
  **correction (per the document owner): this is all seven columns on `TenantUsersEntity`, not just
  three**, because SanchiSaaS supports both a default `*.sanchiapp.com`-style domain and a fully custom
  white-label domain per tenant, and today's hand-maintained `CORS_DOMAINS` env var already includes all
  of them, not a fixed domain/admin/api triplet:
  - `domain`, `customDomain` — tagged `domain_type = 'hub'` (the tenant's public frontend, default and
    white-label variants).
  - `apiDomain`, `apiUrl` — tagged `domain_type = 'api'`. `apiUrl` is stored as a full URL, not a bare
    domain (per this repo's own data model) — the sync function extracts the hostname (e.g.
    `parse_url($apiUrl, PHP_URL_HOST)`) before writing the `cors_domains` row; `apiDomain` and `apiUrl`
    are deduplicated against each other when they resolve to the same hostname.
  - `admin_domain`, `admin_custom_domain`, `adminUrl` — tagged `domain_type = 'admin'`, same
    URL-vs-bare-domain handling and dedup as above for `adminUrl`.
  Any of the seven that is null/empty on a given tenant is simply skipped — not every tenant has a custom
  domain set. A second function wraps the cURL call to the cockpit's `POST /domain-orchestration/sync`
  endpoint for the explicit "Sync to PowerPitch & VideoSDK" button (optional/explicit, not an automatic
  side effect of a plain CRUD save — that part of the design is unchanged).
- **Correction (confirmed by direct code trace this session): a tenant can be created/edited through TWO
  independent, parallel code paths in this repo today — not just the new `tenant_management` module.**
  `modules/tenant_management/create.php`/`edit.php` themselves say so in their own header comments:
  *"Bespoke module — does not touch `modules/add.php` or `spa_data_management`."* The **old, still-live**
  generic CRUD engine (`modules/add.php` for `add/tenant_users`, `modules/edit.php` for
  `edit/tenant_users/:id`) is not disabled or blocked for the `tenant_users` table — confirmed reachable
  today exactly as the document owner described (`table/tenant_users`, `edit/tenant_users/:id`). There is
  **no shared "after save" hook or event system anywhere in this repo** — the existing analogous concern
  (resetting cached SaaS settings on an `api_url` change) is already handled by calling the same plain
  function, `resetAPISaaSSettings()`, independently from **both** engines (`modules/edit.php:256-258`,
  unconditionally, and `modules/tenant_management/edit.php:163`, conditionally on the value actually
  changing) — there is no single hook to attach to instead. **The new `syncTenantCorsDomain()` call must
  therefore be added at every one of the following independent save points, following that exact
  precedent, not routed through one shared hook that doesn't exist:**
  - **Existing file — required touch:** `modules/tenant_management/create.php:184` (immediately after
    `$db->insert("tenant_users", $tenantData)`, using the new `$newTenantId`).
  - **Existing file — required touch:** `modules/tenant_management/edit.php:159-164` (alongside the
    existing `resetAPISaaSSettings()` diffing pattern already there).
  - **Existing file — required touch:** `modules/edit.php:256-258` (the old generic engine's existing
    `tenant_users`-specific block, right next to its own `resetAPISaaSSettings()` call).
  - **Existing file — required touch:** `modules/add.php` — this file has **no** `tenant_users`-specific
    block today (unlike `edit.php`); one must be added, mirroring `edit.php:256-258`'s pattern, so a
    tenant created via the old generic engine's create route is not silently skipped.
  Each of these four call sites is a small, additive, narrowly-scoped edit (one new function call, or one
  new `if ($table_name == "tenant_users")` block modeled on an existing one) — not a rewrite of any of
  these files' surrounding logic.
- **New: one-time backfill of existing Hub and Spoke domains into `cors_domains`.** The live sync hooks
  above only fire on a future create/update — every tenant and partner that already exists today would
  otherwise have zero rows in the new registry. This needs a one-time, explicitly-triggered admin action,
  built on two patterns that already exist in this exact repo:
  - **Correction — exact connection variable per write, matching this repo's own established naming
    (`scrapper.php`/`sql_script_execute.php`), to leave no ambiguity for the implementer:** this backfill
    action holds **two live Medoo connections at once**, and each write below must go through the correct
    one — never the other.
    - `$database` — this module's own, already-open connection to the **shared tenants DB** (the same one
      `tenant_users` lives in). Both the Hub-domain loop and every `cors_domains` insert/update in this
      backfill go through `$database` — `cors_domains` lives in this same shared DB, not in any per-tenant
      database, so no second connection is needed to write it.
    - `$tenantDatabase` — a **fresh connection opened once per tenant inside the loop** (mirroring
      `scrapper.php:9-17`/`sql_script_execute.php:126-134` exactly), using that one tenant's own stored
      `database_host`/`_name`/`_user`/`_password` from its `tenant_users` row. Every read *and write*
      against that tenant's own `partners` table — including the `abbreviation` backfill below — goes
      through `$tenantDatabase`, never `$database`. Defensively check the `partners` table and
      `abbreviation` column exist first via `$tenantDatabase` (mirroring `scrapper.php`'s own
      `information_schema.tables` guard — some older tenant DBs may predate that column).
  - **Hub domains:** trivial — loop every row already in `tenant_users` (via `$database`) and call the
    same `syncTenantCorsDomain()` used by the live hooks, which writes into `cors_domains` via
    `$database`. No new sync logic, just a batch invocation.
  - **Backfilling the `abbreviation` value itself, not just syncing it — a prerequisite step the document
    owner flagged.** `abbreviation` is today only auto-suggested client-side (JS, first-3-letters-of-name,
    uppercased) on the generic engine's non-iframe `add`/`edit` templates — and the practically-used
    partner-edit path, `edit-plain.php`, has **zero** `abbreviation` references in its template at all (per
    this session's earlier exploration). So most existing partners across most existing tenants almost
    certainly have `abbreviation IS NULL` today, not merely "some." For every `partners` row read via
    `$tenantDatabase` with a null/empty `abbreviation`: generate one from the first 3 letters of `name`
    (uppercased, matching the existing SAN-253 auto-suggest convention exactly), check uniqueness against
    every other `partners` row already in that same tenant's table (via `$tenantDatabase`), and on
    collision fall back deterministically — first try 4 letters, then 5, then (guaranteed-unique) append
    the partner's own numeric `id` as a suffix. **Write the generated value back to that `partners` row via
    `$tenantDatabase`** — this update lands in that tenant's own database, never in the shared tenants DB.
    Only ever touches rows where `abbreviation` is currently null/empty — never overwrites an existing,
    intentionally-set value. Only after this step does the row have an `abbreviation` to sync at all.
  - Once every partner in that tenant has a non-empty `abbreviation` (either pre-existing or just
    backfilled via `$tenantDatabase`), select all of them (still via `$tenantDatabase`) and call
    `syncPartnerCorsDomain()` for each — which writes the resulting `cors_domains` row(s) via `$database`
    (no network call needed; tenants-admin already holds that connection to the shared tenants DB).
  - New `source` enum value **`backfill`** (added to `cors_domains.source` above, alongside `manual` and
    `auto_partner`) — so operators can tell historical-import rows apart from ones the live hooks create
    going forward.
  - **Idempotent by design:** `cors_domains.domain`'s existing UNIQUE constraint means both sync functions
    must upsert, not plain-insert — safe to re-run the whole backfill if it fails partway or needs
    re-running later.
  - **Operational shape, mirroring the SQL Script Runner's (SAN-363) own established conventions:** a
    manual, explicit, admin-triggered action (a button, e.g. on the new `cors_domain_management/` list
    screen) — not silent on deploy, since it touches every tenant's live stored DB credentials. Per-tenant
    failure isolation: one tenant's dead connection or missing table logs and skips to the next tenant,
    never aborts the whole run (matching the domain-orchestration flow's own "no distributed transaction,
    independently retryable" philosophy elsewhere in this spec). A dry-run preview (count of domains that
    would be created/updated, per type) before committing, given the blast radius.
  - **Sequencing:** run once, after this repo's `cors_domains` table exists (i.e. after the cockpit's
    module from this section is deployed), and before `hub_spoke_domain_enabled` is enabled on any
    production tenant that already has real, live Spoke-subdomain traffic depending on CORS working for
    it.

**Implementation notes (recorded 2026-08-20, after the slice was built — no scope change, these only
record what the code actually does):**

- **Real column names confirmed against `TenantUsersEntity`, not assumed from this plan's prose:** the
  seven domain-shaped columns are `domain`, `custom_domain`, `api_domain`, `api_url`, `admin_domain`,
  `admin_custom_domain`, `admin_url` (`tenant-users.entity.ts:44-64`) — the plan's `customDomain` /
  `apiDomain` / `adminUrl` are the TypeScript property names, not the DB column names Medoo needs.
- **`cors_domains` has no `parent_domain`/`parent_id` column** (confirmed by reading
  `CorsDomainEntity` directly). A Spoke row is therefore linked back to its Hub through `tenant_id`
  only, which `syncPartnerCorsDomain()` resolves from the hub's own `domain`/`custom_domain`.
- **New `includes/cors_domain_sync_functions.php`** carries, besides the two specified functions:
  `corsDomainNormalizeHostname()` (mirrors the cockpit's own `BARE_HOSTNAME_REGEX` so this panel can
  never store a row the cockpit's DTO would reject), `corsDomainNormalizeAbbreviation()`,
  `corsDomainGenerateAbbreviation()` (the 3→4→5→id chain), `corsDomainUpsert()`, and
  `corsDomainsRegistryTableExists()`.
- **Both sync functions take optional `$source` and `$dryRun` arguments** after the specified ones, so
  the live hooks tag rows `manual`, the backfill tags them `backfill`, and the dry run can compute
  counts without writing. The call shapes named in this plan still work verbatim.
- **`corsDomainUpsert()` reports a fourth outcome, `unchanged`**, alongside created/updated/skipped —
  which is what makes "re-running the backfill changes nothing" an observable property rather than a
  claim, and what the dry run's "already set" counts are built from.
- **A `source = 'manual'` row is never demoted** to `auto_partner`/`backfill` by a later sync, so
  operator-entered rows stay identifiable (the point of the `source` column).
- **The four live save hooks are inert until the cockpit deploys.** Both sync functions return
  immediately when `cors_domains` doesn't exist yet (memoised `information_schema` probe). This repo
  ships independently of the cockpit, so without that guard a tenant save could have started failing
  on a deploy-order mistake — this is the "behaviour-risky change lands off by default" property for
  this slice, achieved without inventing a second flag.
- **`modules/add.php` got the new `if ($table_name == "tenant_users")` block** it was missing; the
  other three call sites are one added call each. All four re-read the committed `tenant_users` row
  rather than trusting the in-flight form array. No other table's special-case block was touched.
- **Orchestration configuration:** `cockpit_api_url` and `cors_orchestration_internal_api_key`, each
  read from a `spa_settings` row first (this repo's own existing convention, per
  `modules/auth/admins.php`'s `api_server_url`) and from `$_ENV` as a fallback
  (`COCKPIT_API_URL`; `CORS_ORCHESTRATION_INTERNAL_API_KEY`, then `AI_CREDITS_INTERNAL_API_KEY`).
  This repo has **no `.env.example` file** despite its CLAUDE.md saying so, so both names are
  documented in `modules/cors_domain_management/module.spec.md` and in the helper file's header
  instead. Real target path confirmed as `POST {base}/api/v1/domain-orchestration/sync`
  (`setGlobalPrefix('api')` + URI versioning), header `x-internal-api-key`.
- **Still open for this repo, deliberately not done here:** the operator-facing toggle for
  `hub_spoke_domain_enabled` (deferred to SAN-385 by the tenants slice's notes). Adding it to
  `tenant_management/_switch_sections.php` would put the column in every tenant INSERT/UPDATE that
  module issues, which hard-fails every tenant save if this repo deploys before the cockpit adds the
  column — so it is left until the column exists. Until then the flag is reachable through the generic
  engine's `edit/tenant_users/:id` form, which enumerates real DB columns (subject to this repo's
  known `spa_form_layouts` blank-form landmine).
- **`localhost`-style single-label hostnames are skipped**, matching the cockpit's own two-label
  minimum — relevant only to local dev tenants.

### frontend (`sc-saas-frontend`) — Linear: SAN-386

- **Existing file — required touch:** `src/app/core/service/api-endpoint.service.ts` — change the
  tenant-verification endpoint path from `verify_tenant/` to `resolve-domain/` (line 274 today) — the new
  cockpit endpoint is a strict superset, identical response for every existing hostname.
- **Existing file — required touch (minimal):** `tenant.service.ts`'s `getTenantDetails()` — store the
  new optional `partnerAbbreviation` field alongside the existing `SetBrandDetails` dispatch.
- New `src/app/core/service/partner-branding.service.ts` + a new NgRx slice
  (`src/app/core/state/partner-branding/`) — fetches `GET /partner-branding/:abbreviation` when a
  `partnerAbbreviation` is present, layering it over the existing tenant-wide brand state (new state
  slice, not an edit to the existing `global` slice).
- Regression-test the endpoint swap against a non-spoke hostname first, per the Verification plan, before
  testing against a spoke hostname.
- **New (Decision #9): abbreviation field on the Partner self-registration form.** The `userType=partner`
  step of the existing `/auth/register` flow gets a new "Subdomain Abbreviation" input, live-suggested
  (client-side, same first-3-letters-uppercased convention as elsewhere) from the organization-name field
  already on that form, editable before submit. Live-checks availability against the new backend pre-check
  endpoint (debounced, same UX pattern this form likely already uses for email-availability checking via
  `checkEmailAlreadyExists()`'s endpoint — reuse that existing debounce pattern if present, don't invent a
  new one).

**Implementation notes (recorded 2026-08-20, after the slice was built — no scope change, these only
record what the code actually does so SAN-387 is not written against a guess):**

- **The endpoint swap is one line**, `api-endpoint.service.ts`'s `VERIFY_TENANT` constant (the constant
  name is deliberately unchanged — it is referenced by `tenant.service.ts` and renaming it would have
  widened the diff on the highest-risk change in this feature). Response type re-verified directly
  against the already-built cockpit code (`domain-resolver.controller.ts` /
  `domain-resolver.service.ts`): same `{message: 'Tenant verified successfully', data}` envelope, `data`
  produced by the same `GlobalService.verifyTenant()` builder, `partnerAbbreviation` the only addition.
  `IBrandDetails` therefore gained exactly one optional field, `partnerAbbreviation?: string`.
- **The branding fetch is dispatched from `app.component.ts`, not `tenant.service.ts`.**
  `GET partner-branding/:abbreviation` lives on the *tenant backend*, so it is only addressable after
  `ApiEndpointService.setApiEndPoint(res.data.apiUrl)` has run — which happens in `AppComponent`'s
  subscriber, downstream of `TenantService`'s `tap`. `tenant.service.ts` keeps the minimal touch the plan
  asked for (dispatching the new `SetPartnerAbbreviation` alongside the existing `SetBrandDetails`); the
  four-line `if (res.data.partnerAbbreviation)` dispatch sits in `app.component.ts`. This is one file
  beyond the three this plan named for this repo — same repo, same slice, additive, and inert for every
  hub hostname.
- **Availability-check path chosen (the plan left it "TBD at implementation") —
  `GET api/v1/public/auth/verify/partner-abbreviation/:abbreviation`**, mirroring the existing
  `public/auth/verify/mobile/:mobileNumber` and `public/auth/verify/email/:email` routes. SAN-387 must
  implement this exact path and the `{data: {isExist, message}}` shape, or the frontend check stays dark.
- **An existing debounced-availability pattern was found and mirrored, not invented:**
  `account-information.component.ts`'s `verifyEmailNumber()` / `verifyMobileNumber()`
  (`distinctUntilChanged()` + `debounceTime(1000)` + `{isExist, message}` + an `isErrorIn*` string that
  feeds `isFormValid()`). The new abbreviation check is the same shape, with two deliberate differences:
  no toast, and the HTTP error is swallowed to `null` in `AuthService.verifyPartnerAbbreviation()` — the
  route 404s until SAN-387 ships, and the field must stay usable (just without live feedback) rather than
  toast on every keystroke or block submit.
- **Registration payload field is `abbreviation`** (optional, `RegisterModel`), sent only when
  `userType === 'partner'` and non-empty. Confirmed safe to ship before SAN-387: `sc-saas-backend`'s
  global pipe is `new ValidationPipe({ whitelist: true })` **without** `forbidNonWhitelisted`
  (`sc-saas-backend/src/main.ts:99`), so an unknown property is silently stripped, not a 400.
- **No frontend flag consumer was added**, per this spec's Contracts section — the frontend branches on
  the *presence* of `partnerAbbreviation`, and `IFeatures` is untouched.
- **Deploy-order note (already implied by Rollout, made explicit here):** this repo's bootstrap now
  depends on `resolve-domain` existing. The cockpit must be deployed first, or every tenant 404s at boot.
- **Tests:** karma/jasmine specs added for the swap (`tenant.service.spec.ts`), the new service, reducer
  and effect, the new auth pre-check, and the registration field. This repo's suite cannot be run
  wholesale — 15 pre-existing spec files elsewhere fail to compile and take the whole karma bundle down
  with them (pre-existing, unrelated to this feature); the new specs were run in isolation via a scoped
  `tsConfig` and all pass.

### backend (`sc-saas-backend`) — Linear: SAN-387

- New `src/core/middleware/partner-subdomain.middleware.ts` — reads `req.hostname`, strips the tenant's
  own domain as a known suffix; if a label remains, looks up `PartnerEntity` by `abbreviation` and sets
  `req.resolvedPartner` (never throws; inert for every non-spoke hostname). Gated no-op when
  `saasFeatures[Feature.HUB_SPOKE_DOMAIN_ENABLED]` is off.
- New `src/core/decorators/resolved-partner.decorator.ts`,
  `src/core/services/partner-subdomain-resolver.service.ts`,
  `src/core/services/partner-cors-registry.service.ts` (same cache pattern as tenants' registry, built
  from `PartnerEntity.abbreviation` rows).
- New `src/modules/partner-branding/` (entity, DTOs, service, controller, module) — new `partner_branding`
  table, field-for-field parity with the existing `spa_settings` branding shape (logo, header logo,
  favicon, primary/secondary/danger/success colors, login/register side images); public
  `GET /partner-branding/:abbreviation` for frontend consumption, authenticated write routes gated by
  `@Features([Feature.HUB_SPOKE_DOMAIN_ENABLED])`.
- New `src/core/utils/partner-subdomain-url.utils.ts` — `getPartnerFrontEndUrl()` /
  `getPartnerAwareUserTypeRegistrationUrl()`: builds `https://{abbreviation}.{tenantDomain}`-based links
  when applicable, falls back byte-identical to the existing `frontEndUrl`-based helpers otherwise.
- New `src/modules/partner-domain-access/` (`entities/scoped-access-token.entity.ts`,
  `partner-domain-access.service.ts`, `partner-domain-access.controller.ts`) — new, properly-scoped
  Backdoor URL mechanism: short-lived (~5 min), single-use, bound to one issuing admin + one target user +
  optional partner. Does not touch or extend the existing NIR-5 `getBackdoorLogin` endpoint
  (`admin-actions.controller.ts:254`).
- New `src/core/services/domain-registry-sync.service.ts` — new sibling to
  `power-pitch-external.service.ts`; `pushDomainToPowerPitch(hostname)`, called only from the cockpit's
  orchestration flow, never automatically.
- **Existing file — required touch:** `src/core/constants/enum.ts` — add
  `HUB_SPOKE_DOMAIN_ENABLED = 'hub_spoke_domain_enabled'` to the `Feature` enum (line 1024) so
  `@Features([...])` can reference the flag.
- **Existing file — required touch:** `src/main.ts` — same additive-OR CORS merge as the cockpit's touch,
  using `partner-cors-registry.service.ts`.
- **Existing file — required touch:** `src/app.module.ts` — register the middleware via `configure()`
  (this `AppModule` has no existing middleware consumer today, so this is a net-new consumer chain, not a
  modification of an existing one) and the two new modules.
- **Existing file — required touch (user-confirmed, narrow):** `src/core/services/ses-email.service.ts`'s
  `sendInstantEmailInvitationEmail()` — the single `registration_url: getUserTypeRegistrationUrl(...)`
  line (line 2556) becomes a call to the new partner-aware helper when `partner?.abbreviation` is set and
  the flag is on; byte-identical output otherwise. No other line in this file changes (the second,
  unrelated occurrence at line 2699 is out of scope).
- **New: Hub-vs-Spoke data-visibility scoping (gated by `hub_spoke_domain_enabled`):**
  - **Existing file — required touch:** `src/modules/auth/auth.service.ts`'s session/JWT-payload
    construction (`:320-365`) — for every stakeholder account type (not just `accountType === 'partner'`),
    additionally resolve and echo that stakeholder record's own `partnerId` onto the session/JWT payload
    when the flag is on; byte-identical payload shape when the flag is off.
  - **Existing file — required touch:** `src/modules/program-management/programs.repository.ts`'s listing
    query (`:71-100`, currently zero `partnerId` filtering) — add the same
    `partnerId ? (partnerId = X OR ...) : partnerId IS NULL`-shaped scoping already correctly implemented
    in `application-programs.repository.ts:97-146`, driven by the now-session-carried `partnerId` from the
    point above, gated by the flag.
  - New `src/modules/global/admin-actions/services/invite-partner-context.service.ts` — when an invite is
    issued from a stakeholder's detail page (`admin-actions.controller.ts`
    `invite-users[-instant]/:adminMd5`), auto-derives `partnerUUID` from **the stakeholder being viewed**
    (its own `partnerId`, if set) rather than requiring the admin frontend to supply it — closes the
    invite-side gap [Evidence #10] so "invite → register → lands in partner ecosystem" works end-to-end.
  - **Explicitly out of scope (tracked separately, per the document owner's decision):** hardening
    `application_programs`'s listing endpoint to derive `partnerId` from the session instead of trusting
    the client-supplied `?partnerId=` query param [Evidence #11] — this is a pre-existing data-exposure bug
    independent of this feature; see Out of scope.
- **New: Partner abbreviation at self-registration and self-service editing (Decision #9).**
  - **Existing file — required touch:** `src/modules/auth/dto/register-user.dto.ts` — add a new optional
    `abbreviation` field, `@ValidateIf(user => user.userType === UserTypes.PARTNER)`. Also **extend
    `organizationName`'s existing `@ValidateIf`** (currently `:136-148`, gated to
    `INVESTOR`/`ORGANIZATION` only) to also require it for `PARTNER` — confirmed by direct trace that
    today a partner can self-register with an empty `organizationName`, which would break the
    auto-suggestion this decision depends on; this is a small, pre-existing validation gap this feature
    must close as a prerequisite, not a new regression it introduces.
  - **Existing file — required touch:** `src/modules/partner/type/partner.type.ts`'s `NewPartnerType`
    (`:3-9`) — add `abbreviation?: string`.
  - **Existing file — required touch:** `src/modules/partner/repositories/partner.repository.ts`'s
    `createNewPartner()` (`:337-353`) — accept and set `partnerEntity.abbreviation` when provided.
  - **Existing file — required touch:** `src/modules/auth/auth.service.ts`'s `PARTNER` case (`:1366-1396`)
    — pass `registerUserProfile.abbreviation` through to `createNewPartner()`; if blank/omitted, generate
    one server-side using a new proactive check-before-write loop modeled directly on
    `startup-recognition-id-generation.service.ts`'s `assembleUniqueCode()` (`:321-357`) — same
    check-then-retry shape, different source field (`organizationName` instead of whatever
    `recognitionId` derives from) and different candidate alphabet (first-N-letters, not
    `assembleUniqueCode()`'s own scheme).
  - New `src/modules/auth/services/check-abbreviation-availability.service.ts` (or a method on an existing
    auth service, implementer's choice) + a new endpoint, mirroring `checkEmailAlreadyExists()`
    (`auth.service.ts:1529-1561`)'s `{isExist, message}` friendly-response shape exactly — used by both
    the frontend registration form and the new partner-portal settings page (SAN-388) for live
    availability checks.
  - New `src/core/services/partner-cors-domain-push.service.ts` — new sibling to
    `domain-registry-sync.service.ts`; after a partner self-registers with a non-empty `abbreviation`,
    fires a best-effort HTTP call to the cockpit's **already-specified** `cors-domains` CRUD API (tenants
    section, above) to upsert the new Spoke domain row — authenticated via the same
    `InternalApiKeyGuard` shared secret already designed for that controller. No new cockpit endpoint
    required. Failure is logged, not thrown — registration succeeds regardless of this call's outcome.
  - **New: authenticated partner self-service endpoint to change their own `abbreviation` post-registration**
    — a new route (e.g. `PATCH /partner/profile`, implementer's choice of exact path) gated by the
    existing partner-session JWT guard, re-validates availability via the same check used at registration,
    updates `PartnerEntity.abbreviation`, and calls `partner-cors-domain-push.service.ts` again with both
    the old and new value so the cockpit-side CRUD call can deactivate the stale row (per Decision #9) as
    well as create the new one. **Note this is a distinct write path from SAN-388's new partner-portal
    settings page below** — that PHP page writes directly to the tenant's own DB via Medoo (matching every
    other admin-side write in this spec) and syncs via `sc-saas-admin`'s own PHP sync function; this
    backend endpoint exists only for a future consumer that talks to `sc-saas-backend` directly (e.g. if
    the frontend PWA itself ever grows a partner settings surface) — **not required for SAN-388's PHP
    settings page to work**, which does not call this endpoint. Included for completeness/consistency, not
    because SAN-388 depends on it.

**Implementation notes (recorded 2026-08-20, after the slice was built — no scope change except where
explicitly flagged as a deviation below):**

- **`@Features(...)` is variadic in this repo, not array-taking.** Every occurrence of
  `@Features([Feature.HUB_SPOKE_DOMAIN_ENABLED])` in this plan is written
  `@Features(Feature.HUB_SPOKE_DOMAIN_ENABLED)` in the code, matching the real signature
  (`core/guards/features.decorator.ts`) and every existing call site. `FeatureGuard` also reads its
  metadata off the HANDLER, so the established convention — `@UseGuards(FeatureGuard)` at controller
  level, `@Features(...)` only on the handlers that need it — is what keeps the public
  `GET /partner-branding/:abbreviation` reachable with the flag off while every write route is gated.
- **Real route paths** (global prefix `api` + URI versioning): `GET api/v1/partner-branding/:abbreviation`
  (public), `GET|POST|PUT api/v1/partner-branding` (partner session, flag-gated),
  `GET api/v1/public/auth/verify/partner-abbreviation/:abbreviation` (public pre-check — the exact path
  the already-shipped frontend calls), `PATCH api/v1/partners/abbreviation` (partner self-service),
  `POST api/v1/partner-domain-access/issue/:adminMd5`, `GET api/v1/partner-domain-access/redeem/:token`.
- **The partner-branding write routes authenticate a PARTNER SESSION**, and the partner id comes from
  `session.partnerId` only — no partner identifier in any body or path, so there is no IDOR surface.
  **Open item for SAN-388:** the PHP admin holds an admin token, not a partner JWT, so its planned
  "Domain & Branding" tab cannot call these routes as they stand. It should either write via Medoo (the
  pattern every other admin-side write in this feature already uses) or have an admin-authenticated
  variant added deliberately — the session check must not be loosened to accommodate it.
- **`brandName` is served from `partners.name`**, not stored on `partner_branding`, so the two cannot
  drift. Every other field in the plan's list is a real column.
- **DEVIATION (additive, needs noting): `InviteUsersDto` gained three optional fields** —
  `stakeholderType`, `stakeholderUUID`, `stakeholderId`. Decision #8 sources the invite's partner context
  from "the stakeholder being viewed", but `sc-saas-admin`'s current invite payload
  (`modules/table.php:643-651`) carries **no stakeholder identifier at all**, so there was literally
  nothing server-side to derive from. The new `invite-partner-context.service.ts` therefore resolves in
  order: (1) an explicit `partnerUUID` already on the payload — which on its own fixes the larger half of
  the gap, since `adminInviteUsersInstant()` never passed a `partner` argument to the email builder even
  when one was supplied; (2) the new optional stakeholder fields; (3) nothing → a Hub invite, byte-identical
  to today. Sending none of the three keeps today's behaviour exactly, so this repo's change is safe to ship
  before SAN-388 starts sending them.
- **`programs` scoping is driven by a `partnerScope` argument, not by the flag inside the repository.**
  `undefined` means "no filtering" — what every pre-existing caller (including `GlobalService`) passes —
  so their behaviour is unchanged whatever the flag says. The gate is evaluated in exactly one place, the
  controller. `programs` has no `promote_with_partners` column, so only the `partnerId = X` /
  `partnerId IS NULL` half of `application-programs.repository.ts`'s pattern applies.
- **`OptionalJwtAuthGuard` (not `JwtAuthGuard`) was added to `GET programs-management`** — that route is
  reachable without a token today and must stay so; the guard only makes `req.user` available when a token
  is present. For an anonymous visitor the scope falls back to `req.resolvedPartner` (the spoke subdomain
  they arrived on), then to Hub.
- **JWT `partnerId` is emitted as an explicit `null` for a Hub stakeholder** when the flag is on, so
  "Hub" is observable rather than merely absent. With the flag off the block does not run at all — the
  lookup is never even issued.
- **`domain-registry-sync.service.ts` has no controller.** The cockpit's `domain-orchestration.service.ts`
  was read directly: it plans to call PowerPitch's `POST /v1/externals-admin/tenants` itself, and this
  feature's Contracts block defines no new backend route for the push — adding one would be a contract
  change needing re-approval. The service is therefore a real, callable `pushDomainToPowerPitch(hostname)`
  that POSTs `{hostname}` (the shape of PowerPitch's `ExternalTenantsEntity`, read from the sibling
  workspace) with an `x-internal-api-key` header, and returns the cockpit's own `DomainSyncStepResult`
  shape. Until SAN-389 ships the endpoint 404s and the method reports
  `{status: 'manual_action_required'}` — the same defensive branch a real failure takes.
- **Configuration is read from `process.env` directly** (`COCKPIT_API_URL`,
  `CORS_ORCHESTRATION_INTERNAL_API_KEY` → `AI_CREDITS_INTERNAL_API_KEY`,
  `POWER_PITCH_SERVICE_API_BASE_URL`), matching `power-pitch-external.service.ts`'s own precedent, rather
  than adding entries to this repo's Joi schema — which requires ~48 env vars and would hard-fail boot on
  any environment that hasn't been updated.
- **The new Backdoor mechanism's issue route is authenticated by `:adminMd5`** (`spa_admin_users.auth_token`),
  the same mechanism every other admin-initiated call into this API uses. That token now only authorises
  ISSUING a token bound to one named user; it is never what the redeemer presents. Both routes are
  flag-gated, so the whole new auth surface is off by default. The existing NIR-5 `getBackdoorLogin` was
  not touched.
- **`npm run lint` is `eslint --fix` and rewrites the whole repo.** It reformatted six files unrelated to
  this issue (`application-program.controller.ts`, `connection-remainder-2.service.ts`,
  `program-startup-rounds.repository.ts`, `startup-recognition-id-generation.service.ts`,
  `startup.repository.ts`, `startup.controller.ts`); all six were reverted, leaving the working tree
  scoped to this slice. Worth knowing before anyone else runs it here.
- **Tests:** jest specs added for the resolver, the middleware, the CORS registry, the URL helpers,
  partner branding, the scoped-token service, the abbreviation service, the invite partner-context
  service, the programs scoping, and the JWT `partnerId` propagation. `npm run build` passes; the full
  suite passes except the 2 pre-existing failures in `global-onboarding-design.spec.ts`, which fail
  identically on a clean tree.

### admin (`sc-saas-admin`) — Linear: SAN-388

- New `includes/hub_spoke_functions.php` — `getPartnerAwareProgramRegistrationUrl()`, mirroring
  `getApplicationProgramRegistrationUrl()`'s existing logic (including its
  `program_request_type == 'external'` verbatim-URL override) but substituting the partner subdomain when
  applicable.
- New `modules/partner_domain_branding.php` +
  `themes/default/html/partner_domain_branding/form.php` — new Create/Edit screen for a partner's
  abbreviation/subdomain + branding fields (logo, colors, images) — same field set/UI conventions as the
  hub's `developer/settings_management.php?type=branding`, calling the new `sc-saas-backend`
  partner-branding endpoints.
- **Existing file — required touch:** `index.php` — one new `include` line for
  `hub_spoke_functions.php` (this repo has no per-page autoload; every helper file is included centrally
  here).
- **Existing file — required touch:** `themes/default/html/partner-detail/partner-detail.php` — add one
  new tab (`<li>` + `<div>` pane) containing an iframe onto `partner_domain_branding.php`, copied verbatim
  from the existing "Edit Profile" iframe-tab pattern already in this file. Every existing tab's
  markup/behavior is untouched.
- **New: Spoke CORS domain sync, on every partner create/update — correction confirmed by direct code
  trace this session.** `partners.abbreviation` (the field that determines a spoke's subdomain) is
  writable through **at least three independent save paths**, none of which share a hook, mirroring the
  tenants-admin finding above:
  1. `modules/edit-plain.php:361` — the generic engine's edit path, reached today via
     `partner-detail.php`'s "Edit Profile" iframe tab (the one practically in use).
  2. `modules/edit.php:423` — the generic engine's non-iframe edit route (`edit/partners/:id`) — not
     linked anywhere in this repo's UI, but not blocked either (same `checkTable`/`checkTableAccess` gates
     as every other table), so it must still be covered.
  3. **This spec's own new "Domain & Branding" tab** (`modules/partner_domain_branding.php`, above) — its
     own, separate `update("partners", …)` call, since it bypasses the generic engine entirely.
  New `includes/hub_spoke_functions.php` function `syncPartnerCorsDomain($partnerId, $oldAbbreviation,
  $newAbbreviation, $tenantDomain)` — upserts the `{newAbbreviation}.{tenantDomain}` row into the
  cockpit's `cors_domains` registry (via the same orchestration call pattern as the tenants-admin side)
  whenever `abbreviation` is set or changed, **and, per Decision #9, sets the old
  `{oldAbbreviation}.{tenantDomain}` row's `active = false`** when `$oldAbbreviation` is non-null and
  differs from `$newAbbreviation` — never deletes it, preserving audit history. **Existing files —
  required touch (small, additive `if ($table_name == "partners")` block, following the exact convention
  `modules/edit.php` already uses for other tables — e.g. its existing `events`/`programs` special
  cases):** `modules/edit-plain.php` (near its existing `clearSettingsAPICache()` call at line 365) and
  `modules/edit.php` (near line 426) — plus a direct call from inside the new Domain & Branding tab's own
  save handler, **plus the new partner-portal settings page below** — four call sites total, each passing
  both the pre-update and post-update `abbreviation` values so the deactivation logic has both to compare.
  `modules/add.php`/`modules/add-plain.php` are confirmed **not** currently exercised for `abbreviation`
  at partner-creation time by any real flow (no creation UI sets it), so no change is required there for
  correctness today — noted here only so a future creation flow that does set it doesn't silently bypass
  the sync.
- **New (Decision #9): Partner self-service settings page — the first profile/settings editor in this
  portal.** Confirmed by direct code trace this session: `modules/partners/` has **no** existing
  self-service profile/settings page at all today — only read-only stats (`dashboard.php`), team
  management, and photo gallery. New `modules/partners/settings.php` (routed `partners/settings`, guarded
  by the portal's existing `checkPartnerLoggedIn()` convention) — lets the logged-in partner view/edit
  their own `abbreviation` (pre-filled with the current value), with an availability pre-check before save
  (direct Medoo query against this tenant's own `partners` table — no need to call `sc-saas-backend`'s
  equivalent check endpoint, since this page already holds the same DB connection every other admin write
  in this repo uses). On save, calls `syncPartnerCorsDomain()` (above) with both old and new values — this
  is the fourth call site referenced above. New template
  `themes/default/html/partners/settings.php`, and one new nav link in the partner-portal's own header
  (`themes/default/html/elements/partners/header.php`, alongside the existing Dashboard/Outreach Requests
  links).
- **Existing file — required touch, one line each, as discovered:** templates rendering the existing
  program "Copy URL" (e.g. `themes/default/html/create-program.php`) get a conditional swap to the new
  partner-aware URL function when a partner context applies; falls back to the existing call otherwise.
- **New (Hub-vs-Spoke invite auto-derivation, backend-driven, see backend plan above):** the invite
  action(s) on stakeholder detail pages (e.g. `investor-detail.php`, `mentor-detail.php`, `startup-
  detail.php`, etc.) require no template change — the auto-derivation happens server-side in
  `sc-saas-backend` from the viewed stakeholder's own `partnerId`; this admin repo's existing invite-request
  payload is unchanged.

**Implementation notes (recorded 2026-08-20, after the slice was built — no scope change except where
explicitly flagged as a deviation below):**

- **RESOLVED: the partner-branding auth mismatch SAN-387 flagged as an open item.** The new Domain &
  Branding tab **writes `partner_branding` directly via Medoo** and does not call
  `sc-saas-backend`'s `PATCH`/`POST /partner-branding` routes at all. Those routes take the partner id
  from `session.partnerId` only — no partner identifier in any body or path, which is precisely what
  makes them IDOR-free — and this panel holds an admin token (`spa_admin_users`/`adminMd5`), not a
  partner JWT. Loosening that session check to admit an admin caller would have *created* an IDOR
  surface that does not exist today, so the backend was left untouched. Medoo is also the pattern every
  other admin-side write in this feature already uses, and `partner_branding` lives in this same tenant
  DB. The public `GET /partner-branding/:abbreviation` read route is untouched and unaffected.
- **`partner_branding` and `partners.abbreviation` are both probed via `information_schema` before
  use** (`hubSpokePartnerBrandingTableExists()` / `hubSpokePartnersHaveAbbreviationColumn()`, memoised
  per request). Both are created by `sc-saas-backend`'s TypeORM `synchronize`, which deploys
  independently of this panel, so without the probes an operator reaching these screens first would
  have hit a raw PDO error. Same deploy-order guard the tenants-admin slice used for `cors_domains`.
- **DEVIATION (transport, not behaviour): `syncPartnerCorsDomain()` here is an HTTP call, unlike its
  identically-named twin in `sanchiconnect-saas-tenants-admin`, which is a plain Medoo write.**
  `cors_domains` lives in the shared tenants DB, which in *this* repo is `$mainDatabase`, not the
  `$database` every module writes through. That sibling panel is a platform-level tool whose only
  connection IS the shared DB; this is a per-tenant panel that must not write cockpit-owned global rows
  directly. The logic and outcomes are identical (upsert the new spoke row; set the old one
  `active = false`, never delete); only the transport differs. Real routes used, read off the cockpit's
  own controller/DTOs: `POST /api/v1/cors-domains/upsert`, `GET /api/v1/cors-domains?…`,
  `PATCH /api/v1/cors-domains/:id`, header `X-Internal-Api-Key`.
- **Config reuses `PLATFORM_TENANTS_API_URL` + `AI_CREDITS_INTERNAL_API_KEY`**, both already
  `define()`d in `config/config.php` for the AI-Credits integration — the cockpit's
  `InternalApiKeyGuard` reads its expected value from `AI_CREDITS_INTERNAL_API_KEY` for every internal
  surface, so this is the same secret, not a coincidence. `COCKPIT_API_URL` /
  `CORS_ORCHESTRATION_INTERNAL_API_KEY` are accepted as overrides. **No new env var is required.**
- **TENANT ISOLATION: the cockpit's `/cors-domains` listing is only ever called scoped to this
  tenant's own `tenant_users.id`.** That route enumerates every tenant's and partner's hostnames; a
  per-tenant panel must never issue it unscoped. When this tenant's id cannot be resolved the
  deactivation declines and reports, rather than fetching the global list.
- **The flag is read straight off the `tenant_users` row (`$brandSettings['hub_spoke_domain_enabled']`)
  via a new `hubSpokeDomainEnabled()`, NOT `define()`d as a `config.php` constant** — unlike every
  other flag in this repo. The `array_key_exists()` guard inside it is load-bearing: the column is
  cockpit-owned and this panel deploys independently, so a missing column must read as "off" rather
  than warn, which a `define()` on an absent array key would not do.
- **The Copy-URL swaps are explicit inline conditionals, not bare function-name swaps.** Each site
  reads `hubSpokeDomainEnabled(...) ? getPartnerAware…() : <the original call>`, so with the flag off
  the pre-existing helper is *literally* what executes — a stronger regression guarantee than relying
  on the new helper's internal fallback (which is also byte-identical). Sites touched, exactly the ones
  this plan names: `create-program.php`, `create-venture-studio-program.php`,
  `application_management/program.php`, `facilities/list.php`, and `partners/list.php` (4 sites).
  `program_request_type == 'external'`'s verbatim-URL override is preserved inside the new helper and
  short-circuits before any subdomain is applied.
- **Partner context for a link resolves record-owner FIRST, viewing session second.** In the partner
  portal a Spoke sees programs *promoted* to it by a different partner
  (`partners/list.php`'s `partner_id != $_SESSION['partner_id']` branch); those links must point at the
  owning partner's subdomain, not the viewer's. For a partner's own records both sources agree.
- **Two helpers, not one:** `getPartnerAwareProgramRegistrationUrl(…, $programType)` covers all three
  program helpers (`application` | `program` | `vs_program`), and
  `getPartnerAwareFacilityUrl()` covers `getFacilityUrl()`. Both keep the existing helpers'
  `($database, $brandSettings, $id, …)` parameter order so a call site's change stays one line.
- **DEVIATION (needs noting): the invite stakeholder-identifier wiring is only half-live, and that is a
  property of this repo's UI, not an omission.** `modules/table.php`'s two Hub-admin invite handlers
  now send `stakeholderType` (derived from the listing's own `$table_name`, matching
  `InviteUsersDto`'s enum) and forward `stakeholderUUID` / `stakeholderId` when the request carries
  `stakeholder_uuid` / `stakeholder_id`; `themes/default/html/table.php`'s invite JS forwards them from
  `data-stakeholder-uuid` / `data-stakeholder-id` on the trigger. **But this repo has no
  invite action on any stakeholder detail page** — verified by grep across `modules/` and `themes/`:
  the only Hub-admin invite surface is the page-level "Invite a user" modal on the generic stakeholder
  *listing*, which by definition has no single record in view, so there is no uuid/id to send from it
  today. `InvitePartnerContextService` needs at least one of those two to derive anything, so that half
  stays dormant until a record-scoped invite trigger exists; sending only `stakeholderType` resolves to
  a Hub invite, byte-identical to today. The partner portal's own invite
  (`modules/partners/list.php`) already sends an explicit `partnerUUID`, which is the higher-priority
  branch of the backend's resolution chain and is unaffected. **Follow-up worth filing separately: add
  a per-record "Invite" trigger on the stakeholder detail pages, which is what would make Decision #8
  fire end-to-end.**
- **`add.php`/`add-plain.php` deliberately not hooked** for the CORS sync — confirmed again this pass
  that no creation UI in this repo sets `abbreviation`. Recorded in
  `modules/stakeholder-crud/module.spec.md` so a future creation flow that does set it does not
  silently bypass the sync.
- **Verification bar: `php -l` only.** This repo has no test framework, no CI and no build/lint step
  (its own CLAUDE.md), so no automated test coverage was added — stated explicitly rather than implied.
  All 17 new/changed PHP files lint clean. Everything else was manual review against this repo's
  documented conventions (block comments, `count($arr) > 0`, no `isset()` on a `sparkAdminTpl` magic
  prop, buffer-flush before AJAX JSON, `window.addEventListener('load', …)` for inline scripts).
- **Module specs updated in the same change:** new `modules/partner_domain_branding.spec.md`; plus
  `modules/partners/module.spec.md` (the new self-service page + the cockpit API it consumes),
  `modules/stakeholder-crud/module.spec.md` (the two generic-engine save hooks and the "no shared
  after-save hook" invariant), `module.spec.md` (core-bootstrap: the new central include and why the
  flag is not a constant), and `specs/admin-module-specs-index.md`.

### power-pitch-sanchiconnect-api (sibling SanchiPowerpitch workspace) — Linear: SAN-389

- New module `src/modules/external-tenants-admin/` — `POST/GET/DELETE /v1/externals-admin/tenants` CRUD
  against the existing, untouched `ExternalTenantsEntity` (table `tenants`). Deliberately **not**
  decorated with the existing `ExternalHostInterceptor` (chicken-and-egg — you'd need to already be
  whitelisted to whitelist yourself); gated instead by a new `InternalApiKeyGuard`.
- **Existing file — required touch:** `src/app.module.ts` — register the new module (additive).
- PowerPitch's own CORS config (`main.ts`, currently `origin: true` with a dead domain list) stays as-is
  per the document owner's decision — explicitly out of scope for this feature.
- This module does not change the existing `/v1/externals/*` contract that `sc-saas-backend`'s
  `PowerPitchExternalService` depends on (workspace invariant #6) — it is a net-new, separate admin-only
  surface.

### sc-saas-3rdparty-webservices — Linear: SAN-390

- **Confirmed 2026-08-19: VideoSDK's domain-management API is real.** `POST
  https://api.videosdk.live/v1/apikeys/{apiKeyId}/domains`, body `{ domain }`. Auth is a self-signed JWT —
  the exact same mechanism this repo already uses for the VideoSDK meetings integration
  (`videoSDK.service.ts:210-224`'s `createVideoSDKtoken(apiKey, secret)`: `sign()` from `jsonwebtoken`,
  `HS256`, 5-minute expiry, secret = the existing `videosdkSecretAccessKey` config). `apiKeyId` is the
  same `videosdkAPIKey` config already used for the meetings JWT payload's `apikey` field — no new env
  var needed for it. **Two details need confirming against VideoSDK's own docs before this ships** (not
  verifiable from this codebase, since only the meetings API's exact requirements are proven here): (a)
  whether this endpoint needs the meetings API's `roles: ['CRAWLER']` claim or a different one — the
  design below omits it, since that claim looks meeting-specific; (b) the meetings API sends the JWT
  unprefixed (`Authorization: <token>`), while VideoSDK's own domains-endpoint sample uses a `Bearer `
  prefix — confirm which this specific endpoint expects.
- New `src/modules/videoSDK/videoSDK-domain.service.ts` — `registerDomain(domain)`: signs a token via a
  new `createVideoSDKManagementToken()` (sibling to the existing `createVideoSDKtoken()`, payload `{apikey:
  apiKeyId}` only, per the open item above), calls the real endpoint. On any failure (auth, network,
  VideoSDK-side error) — not on an unconfirmed-API assumption anymore — falls back to returning
  `{status: 'manual_action_required', domain}`, so a transient VideoSDK-side failure never blocks the
  rest of the orchestration flow.
- New `src/modules/videoSDK/videoSDK-domain.controller.ts` — `POST /video-sdk/domains`, called from the
  cockpit's orchestration flow via the existing `THIRD_PARTY_SERVICE_BASE_URL` proxy convention
  (`saasSettings[SaaSSettingKey.THIRD_PARTY_SERVICE_BASE_URL]`).
- The `manual_action_required` fallback is now a defensive branch for call failures, not the primary
  design — still surfaced verbatim back through the orchestration response to the tenants-admin UI as a
  plain checklist line when it does fire.

## Contracts & invariants

- **Flags:** `hub_spoke_domain_enabled` — the master gate for every new backend behavior in this feature
  (middleware, partner-branding writes). Owned by `tenants` (as always, per invariant #1). **Corrected
  2026-08-20:** this is a genuinely new flag column, not a rewiring of the pre-existing
  `incubator_module_enabled` — that flag was re-traced immediately before implementation and found to be
  already live (gating unrelated frontend/admin functionality today), so reusing it would have coupled
  this feature's rollout to whatever state it already holds for existing tenants. Propagation checklist:
  backend `Feature` enum (`HUB_SPOKE_DOMAIN_ENABLED`, new), frontend `IFeatures` (add if/when the frontend
  needs to branch on it directly — currently the plan gates frontend behavior on the *presence* of
  `partnerAbbreviation` in the resolve-domain response, not directly on the flag), admin `config.php` (add
  if an operator toggle is surfaced there). Run `/trace-flag hub_spoke_domain_enabled` again once the new
  column exists, before implementation of any consumer repo.
- **API:** two genuinely new public-facing contracts to get right before anything else lands —
  `GET public/global/resolve-domain/:hostname` (must be byte-identical to `verify_tenant` on every
  existing hostname) and `GET partner-branding/:abbreviation` (must match `spa_settings` branding shape
  field-for-field). Every other new route in this feature (`domain-orchestration/sync`, `cors-domains`
  CRUD, `v1/externals-admin/tenants`, `video-sdk/domains`, the new Backdoor URL routes) is
  internal/admin-facing and gated by a new shared-secret guard, not consumed by any existing client. Run
  `/audit-contract` once `sc-saas-backend`'s new controllers exist.
- **Events:** none — the orchestration flow is synchronous best-effort HTTP, not a pub/sub domain event.
- **Invariants at risk:**
  1. *Flag names (owned by `tenants`)* — one new flag column added (`hub_spoke_domain_enabled`); no
     existing flag renamed or removed, including `incubator_module_enabled`, which this spec no longer
     touches at all.
  2. *API contract (owned by `sc-saas-backend`)* — two new consumer-facing routes added
     (`partner-branding`, and indirectly the frontend's `resolve-domain` swap which is a `tenants` route);
     no existing backend route's path/method/DTO shape changes.
  3. *Tenant-verification contract (owned by `tenants`)* — the existing `verify_tenant` route is
     **untouched**; `resolve-domain` is new and additive, required to be a strict superset. This is the
     single highest-risk invariant in this spec — see Acceptance criteria and the frontend's regression-
     test-first requirement.
  4. *Auth (JWT)* — the new Backdoor URL mechanism is a new, narrowly-scoped auth artifact (short-lived,
     single-use, bound token), explicitly not an extension of the JWT cookie/Bearer model and explicitly
     not a reuse of the existing NIR-5 vulnerable endpoint.
  5. *Tenant scoping* — `cors_domains` rows carry a nullable `tenant_id` FK (tenants side, filtered by
     `domain`/tenant per invariant #5); `sc-saas-backend`'s partner/branding data lives inside that
     tenant's own one-deployment-per-tenant database, consistent with this repo's existing "no tenant
     column, bootstrap-loaded config" model — no cross-tenant reference is introduced.
  6. *Cross-workspace PowerPitch contract* — explicitly **not** touched; the new `external-tenants-admin`
     module is a separate, additive surface, and the existing `/v1/externals/*` contract consumed by
     `power-pitch-external.service.ts` is unchanged.

## Test plan

- tenants: jest unit tests for `CorsDomainsService` (duplicate-domain guard, cache refresh/TTL) and
  `DomainResolverService` (exact-match parity with `verifyTenant()`, subdomain-strip fallback, miss case).
  Manual: hit `resolve-domain` with a real existing tenant hostname and diff against `verify_tenant`'s
  response byte-for-byte.
- tenants-admin: `php -l` on all new files; manual CRUD + duplicate-domain-guard walkthrough; manual
  "Sync to PowerPitch & VideoSDK" button walkthrough against a staging cockpit.
- frontend: karma unit test for the endpoint swap (mock both old and new response shapes); manual
  regression pass against a real non-spoke tenant hostname (must show zero behavior change) before any
  spoke-hostname manual test.
- backend: jest unit tests for `partner-subdomain.middleware.ts` (inert on every non-spoke hostname; flag
  off short-circuits), `PartnerBrandingService` (shape parity with `spa_settings`), and the new
  scoped-token service (single-use, expiry, binding checks). Manual: send a real test invite through a
  partner with an `abbreviation` set and confirm the delivered email's `registration_url`. Additionally:
  jest tests for the session/JWT `partnerId` propagation (all account types, flag on/off byte-identical
  check) and the new `programs.repository.ts` scoping (Hub viewer sees only `partnerId IS NULL`, Spoke
  viewer sees only their own `partnerId`); manual test of inviting from a stakeholder detail page whose
  own `partnerId` is set, confirming the registered user lands with the same `partnerId`.
- admin: manual walkthrough of the new partner-branding tab and the Copy URL conditional swap on at least
  one program with `program_request_type == 'external'` (must still return the verbatim external URL
  unchanged) and one without.
- power-pitch-sanchiconnect-api: jest tests for the new `InternalApiKeyGuard` and CRUD module; confirm the
  existing `/v1/externals/*` routes and `ExternalHostInterceptor` behavior are unaffected.
- sc-saas-3rdparty-webservices: jest test for `videoSDK-domain.service.ts`'s two branches (successful real
  call against VideoSDK's confirmed endpoint vs. the `manual_action_required` fallback firing correctly on
  a simulated call failure); manual test against VideoSDK's sandbox to confirm the JWT claim/prefix open
  items above before this ships.
- cross-repo (staging-first, per the document owner's stated risk tolerance):
  - Routing: a staging spoke hostname resolves correctly; the same tenant's root hostname is unaffected.
  - Auth: JWT/session cookies issued on a spoke subdomain remain valid against the tenant's API domain —
    check cookie `Domain`/`SameSite` attributes against the real spoke hostname.
  - CORS: an origin not in either whitelist is rejected on both cockpit and backend; every currently
    configured origin still passes; a newly-added dynamic origin passes only after being added and stops
    being allowed within the cache TTL after removal.
  - Certificates: confirm valid TLS on the spoke subdomain *before* CORS/cookie testing — a cert gap
    masquerades as a CORS/auth failure.
  - Subdomains: at least 3 concurrent spokes under one hub, to catch cache/singleton state bleed.
  - Full staging pass on cloned real-tenant data before enabling `hub_spoke_domain_enabled` on any
    production tenant; enable on exactly one production tenant (pilot) before wider rollout.

## Rollout

- `hub_spoke_domain_enabled` defaults to (and stays) off for every existing tenant until explicitly
  enabled — zero behavior change on deploy for any repo in this feature.
- Deploy order matches the dependency-ordered `repos:` list: `tenants` (CORS registry + resolver, tested
  in isolation against a synthetic staging spoke hostname first) → `tenants-admin` (operator UI, **then
  the one-time backfill action, run against staging first and reviewed before any production run**) →
  `frontend` (endpoint swap, regression-tested against a non-spoke hostname first) → `backend`
  (middleware/branding/URL helpers/backdoor mechanism, all gated) → `admin` (depends on backend's new
  endpoints) → `power-pitch-sanchiconnect-api` and `sc-saas-3rdparty-webservices` (independent of the
  first five, buildable in parallel; the orchestration trigger is wired last).
- The backfill is a one-time, explicitly-triggered action, not part of any automatic deploy step — run it
  once in production after `tenants-admin`'s module is live, before enabling `hub_spoke_domain_enabled` on
  any tenant with real, existing Spoke-subdomain traffic.
- The Backdoor URL mechanism (backend) is recommended to ship and be verified before any spoke goes live
  in production, even though it is not on the critical path of the other pieces.
- **`admin` (SAN-388) is the only slice that edits live, user-facing links** (the program/facility
  "Copy URL" fields), so it is the behaviour-risky one in this feature. Confirmed 2026-08-20: every one
  of those edits is an explicit `hubSpokeDomainEnabled(...) ? new : <original call>` conditional, so
  with the flag off — the default for every tenant — the pre-existing helper is literally what runs and
  the rendered URL cannot change. The new partner-portal Settings nav link is gated on the same flag, so
  no existing partner portal changes visually either. Smoke check after enabling the flag on the pilot
  tenant: one program with `program_request_type == 'external'` (must still return its verbatim stored
  URL), one without, and one facility.
- Pilot on exactly one production tenant before wider rollout, per the Test plan's cross-repo section.

## Out of scope

- Any change to `verify_tenant`'s existing route, response shape, or the `is_patent_hub` /
  `patent_hub_allowed_domains` tenant-to-tenant pattern — a spoke subdomain is not that mechanism (see
  Decision #1).
- PowerPitch's own CORS configuration (`main.ts`) — stays exactly as-is (see Decision #4).
- Extending or fixing the existing NIR-5 `getBackdoorLogin` vulnerability — tracked separately; this
  feature only adds new, separately-scoped code alongside it.
- Any change to `sc-saas-backend`'s per-deployment, no-tenant-column data model — partner/branding data
  for this feature lives inside that same one-deployment-per-tenant database, not a new multi-tenant
  schema.
- **Hardening `application_programs`'s listing endpoint against its client-supplied-`?partnerId=`
  data-exposure gap [Evidence #11]** — real, pre-existing, independent of this feature; tracked as its own
  separate bug-fix Linear issue (see below), not part of this feature's rollout.
- **The new Spoke Broadcast Message + Hub-approval feature** (partner-initiated broadcasts, "Self" vs
  "Hub" ecosystem targeting, approval workflow) — related in spirit (same Hub/Spoke concept, same
  `hub_spoke_domain_enabled` gate) but tracked as its own separate feature spec/Linear project, not folded
  into this one, per the document owner's explicit decision.

## Open questions

None blocking. VideoSDK's domain-management API existence was resolved 2026-08-19 — the document owner
confirmed the real endpoint (`POST /v1/apikeys/{apiKeyId}/domains`) and its auth mechanism (see Decision
#3, Per-repo plan). Two narrow implementation details remain, not blocking approval, to confirm against
VideoSDK's own docs during SAN-390's implementation: whether the domains endpoint needs a `roles`/
`permissions` claim in its JWT payload (the meetings API's `roles: ['CRAWLER']` claim looks
meeting-specific, so the design omits it — confirm this is correct), and whether the JWT should be sent
unprefixed (as the meetings API does) or `Bearer`-prefixed (as VideoSDK's own domains-endpoint sample
shows) — these two should be resolved by testing against VideoSDK's sandbox before this ships, not
guessed at.
