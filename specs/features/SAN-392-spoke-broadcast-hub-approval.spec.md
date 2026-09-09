---
id: SAN-392                     # Linear Project created (team: Sanchiconnect); anchored to its lowest-numbered
                                 # issue, SAN-392 (backend, schema-only). Full issue set: SAN-392 (backend),
                                 # SAN-393 (admin — partner-portal compose/self-send/my-broadcasts),
                                 # SAN-394 (admin — Hub-side approval queue + notifications).
title: Spoke Broadcast Messages with Hub Approval
type: feature
status: approved                # Approved by the document owner 2026-08-20 to begin implementation. Zero
                                 # blocking Open Questions.
linear: https://linear.app/sanchiconnect/project/spoke-broadcast-messages-with-hub-approval-dff4f7579ef0
owner: nirmal.s@sanchiconnect.com
repos: [backend, admin]         # dependency order — the new table must exist before admin can read/write it.
contracts:
  api:
    - "POST v1/admin-actions/partner-broadcast-approved/{adminToken} (sc-saas-backend, NEW — notify submitting partner their Hub-targeted broadcast was approved+sent; patterned after outreach_requests' sendApprovedEmailApi(), not the same endpoint)"
    - "POST v1/admin-actions/partner-broadcast-rejected/{adminToken} (sc-saas-backend, NEW — notify submitting partner of rejection + reason; patterned after outreach_requests' sendRejectedEmailApi(), not the same endpoint)"
    - "POST v1/admin-actions/broadcast-ceo-message/{adminToken} (sc-saas-backend, EXISTING, REUSED unchanged — email transport for both Self-instant and Hub-approved sends)"
  flags: []                      # No new tenant/cockpit flag. See Decisions #4 for why.
  events: []
tenant_scoped: true
depends_on: []
created: 2026-08-19
---

# Spoke Broadcast Messages with Hub Approval

## Reference

This spec did **not** originate from a pre-existing Linear issue. It was authored from a rough requirement
the document owner (Nirmal) gave directly in plain English, explored in depth against the live
`sc-saas-admin` code this session, with several design decisions confirmed with him along the way. Every
file/line reference below was verified directly against the live code during authoring — nothing here is
inferred from the requirement text alone. This feature is related in spirit to SAN-384 (Multi-Tenant
Hub/Spoke Domain & White-Label Architecture — same Hub/Spoke concept) but is tracked as its own spec and
Linear project, per the document owner's explicit decision not to fold it into SAN-384 (see SAN-384's Out
of scope section, which names this feature explicitly).

## The requirement (as stated by the document owner)

"we have broadcast module for Hub. hub broadcast the message to there ecosystem. now i want to implement
the Broadcast feature for Spoke/incubators/partner. they can broadcast the message to there own ecosystem +
Hub ecosystem. means add check box for selection send to broadcast ecosystem: Self/Hub. on selection self
send broadcast message to there ecosystem instant else if selected the Hub then send request to Hub for
confirmation approval of broadcast. if hub approved the broadcast then broadcast sent to hub ecosystem
users with again send broadcast."

In plain terms: a Partner-portal user composing a broadcast picks a target — **Self** (their own
ecosystem/stakeholders only) or **Hub** (the tenant's whole ecosystem). Self sends instantly, exactly like
today's Hub-admin broadcast but scoped to the partner's own audience. Hub queues the broadcast as a pending
request; a Hub admin must approve it before it actually goes out to the full Hub ecosystem; if rejected,
the partner is told why.

## Decisions (confirmed with the document owner, or made explicitly by this document's author with
rationale — see each)

1. **Genuinely separate feature/spec/Linear project from SAN-384**, not folded into it (confirmed).
2. **On Hub rejection**: a rejection reason is required/recorded, and the partner is notified by email —
   mirroring `outreach_requests`' approve/reject email-notification behavior (Evidence #3), not a bare
   status flip (confirmed).
3. **On the "Self" instant-send path**: the recipient pool is strictly limited to that partner's own
   ecosystem (`partner_id` = the sending partner's own id) — consistent with the general Hub-vs-Spoke
   visibility principle also applied in SAN-384; a partner never broadcasts beyond their own stakeholders
   on the instant path (confirmed).
4. **Partners can see the status (pending/approved/rejected) of broadcasts they've submitted for Hub
   approval** — a "my broadcasts" history view, mirroring the Outreach Requests sent/received tabs pattern
   (confirmed).
5. **One new table, not two, and not a retrofit of `broadcast_messages`** — both the Self and Hub paths
   write into the same new `partner_broadcast_requests` table (Self lands directly in `status = 'sent'`;
   Hub starts `pending` and transitions to `approved` -> `sent`, or `rejected`). This gives the "my
   broadcasts" view (Decision #4) one place to look, and matches every column named in the original
   requirement brief (`target_scope` covers both paths) — **author's design decision**, consistent with
   the brief's exact field list, not re-litigated with the document owner as a separate question.
6. **No new tenant/cockpit-level feature flag is introduced.** The existing `can_broadcast_messages`
   permission (`spa_admin_users`, Evidence #2) continues to gate every Hub-side action unchanged. For the
   new partner-side compose/submit capability, this spec reuses the *pattern* already established by
   `$canImportData` in `modules/common.php:529` (`isset($_SESSION["partner_id"])` alone grants a new
   capability module-wide, no extra per-partner opt-in column) rather than inventing a new tenant_users
   column that would require a `sanchiconnect-saas-tenants` change — **author's design decision**, made to
   honor the document owner's explicit framing of this as a single-repo-centered feature (see Linear
   Project instructions) and because the Hub-approval gate on the higher-blast-radius path (reaching the
   whole ecosystem) is already the real control point; a compromised/malicious partner session can, at
   worst, instantly message only its own already-small ecosystem on the Self path.
7. **The only necessary `sc-saas-backend` touch is schema (one new entity) plus two new narrow,
   broadcast-specific `admin-actions` notification routes** (Evidence #6) — no change to any existing
   controller, DTO, or route.

## Corrections / Evidence (verified directly against the live code this session)

1. **Existing Hub-side `broadcast_messages` module** (`sc-saas-admin/modules/broadcast_messages/`) has
   **no lifecycle/status column at all** on its `BroadcastMessagesEntity`
   (`sc-saas-backend/src/modules/global/broadcast_messages/broadcast_messages.entity.ts:16-122`) — a row is
   written exactly once, synchronously, at send time (`create.php:1044-1062`). This confirms the concrete
   gap a new status-bearing table needs to fill, and that it must be a **new** table, not a retrofit —
   adding a status column to a table with zero existing status semantics, consumed by the existing
   `details.php` stats view, is unnecessary risk for no benefit.
2. **`can_broadcast_messages` gates only real Hub-admin sessions today.**
   `getAdminAccessLevels($database, $tpl)` (`sc-saas-admin/includes/core_functions.php:1890-1897`) strictly
   requires `isset($_SESSION['admin_user_id'])` before it will even query `spa_admin_users`; a partner
   session (per `sc-saas-admin/modules/partners/module.spec.md`'s own confirmed Invariants) **never** sets
   `admin_user_id`. So `$canbroadCastMessage` (`modules/common.php:522-526`) is unconditionally `false` for
   every partner session today — confirming there is no existing partner-side gate to reuse; a new one is
   genuinely required (this spec's Decision #6).
3. **The closest working request -> pending -> approve/reject -> notify cycle** is `outreach_requests`
   (`sc-saas-admin/modules/outreach_requests/list.php` + `module.spec.md`), operating on `program_promotions`
   (shared main/tenants DB, not the client DB). Confirmed real email notifications via
   `sendApprovedEmailApi()` / `sendRejectedEmailApi()` / `sendOutreachRequestEmailApi()`
   (`list.php:17,35,51`), each POSTing to `{api_server_url}v1/application-programs-management/promotion-request/{accept|reject|send}/{adminToken}`.
   Confirmed **two real gaps** in this prior art that this feature must not repeat: (a) `approveRequest` /
   `rejectRequest` load the target row purely by `recordId` with **no check** that it belongs to the acting
   session's own tenant/partner (`module.spec.md` "Watch out for", line 112-125) — a real cross-tenant
   authorization gap, made possible there because `program_promotions` is a *shared* table; (b) **no
   `checkRole()`/role gating at all**, only `checkLoggedIn()`.
4. **Recipient resolution today** (`create.php:789-887` send / `:419-511` dry-run count) is a `switch` per
   profile-type checkbox, each built via `formatQuery()` (`create.php:42`), with **zero `partner_id`
   filtering anywhere** — the existing `partner` checkbox case (`create.php:864-868`) means "send TO
   Partner-type accounts," structurally unrelated to "scope recipients to one partner's sub-audience,"
   which does not exist in this module today. This confirms both (a) the Self path's `partner_id`-scoped
   recipient query is genuinely new logic, and (b) a Hub-approved Hub-targeted send should reuse this exact
   existing **unscoped** resolution unchanged (Decision needed below, see "Hub ecosystem" scope).
5. **`modules/partners/` self-service portal has zero existing messaging/broadcast capability.**
   `dashboard.php` (16-66) is pure read-only summary counts, confirmed by direct read this session. The only
   "message" field anywhere in this module (`partners/list.php:533`) is an unrelated free-text note on a
   `program_promotions` cross-tenant-promotion insert, not a broadcast.
6. **Closest prior art for partner-session-aware use of the email transport** —
   `partner-detail.php`'s abandoned `sendMessage` handler (`sc-saas-admin/modules/partner-detail.php:373-498`,
   Hub-admin-side, sending a one-off message to a single stakeholder). Confirmed at lines 462-466: it
   already branches `isset($_SESSION["partner_id"]) ? generatePartnerRandomStringForBackdoor($database) :
   generateRandomStringForBackdoor($database)` before calling `sendBroadcastEmail()`
   (`includes/core_functions.php:4149-4163`, cURL `POST` to
   `v1/admin-actions/broadcast-ceo-message/{adminToken}`). Lines 468-478 contain a **commented-out**,
   abandoned attempt to write a `broadcast_messages` row with `module_type => "partner"` — a half-built
   audit-trail attempt. **This spec reuses the transport functions
   (`sendBroadcastEmail()`, `generatePartnerRandomStringForBackdoor()`,
   `generateRandomStringForBackdoor()`) — it does not reuse or resurrect this dead code block.**
   `generatePartnerRandomStringForBackdoor()` (`includes/partners_functions.php:429-435`) is confirmed
   **not actually partner-scoped despite its name** — it looks up and overwrites a single fixed
   `spa_admin_users` row (`role => 1`, the "developer" account)'s `auth_token`, so two concurrent callers
   (partner or admin) race on the same row and can invalidate each other's in-flight token. This is a
   pre-existing, independent bug (also flagged in `modules/partners/module.spec.md`'s own "Watch out for");
   **not introduced or worsened by this feature**, but worth knowing before relying on it for a
   partner-initiated backend call under real concurrent load.
7. **`modules/common.php`'s live badge-count pattern** (`pendingPromotionsCount`, lines 630-672) computes a
   `COUNT(*)` on every request, gated by tenant-settings flags plus session type, with **no caching** — the
   pattern this feature's new "pending Spoke broadcast approvals" badge replicates (new variable, new query
   against `partner_broadcast_requests`, not a reuse of `pendingPromotionsCount` itself).
8. **`$canImportData`'s existing precedent** (`modules/common.php:528-531`) —
   `(isset($getAdminAccessLevels["id"]) && ... "can_import_data" == "1") || (isset($_SESSION["partner_id"])
   && $_SESSION["partner_id"])` — confirms this codebase already treats "the session is a partner session"
   as sufficient, on its own, to grant a capability module-wide with no separate per-partner toggle. This is
   the direct precedent Decision #6 relies on.
9. **`sc-saas-backend`'s TypeORM config** (`src/core/database/database.module.ts:23-34`) confirmed
   `synchronize: true` with entities loaded via `autoLoadEntities: true` plus a glob
   (`dist/**/*.entity.js` in production). `BroadcastMessagesEntity` is registered via an explicit import +
   `TypeOrmModule.forFeature([...])` entry in `sc-saas-backend/src/modules/global/global.module.ts:131,232`
   — confirming the new `PartnerBroadcastRequestsEntity` needs exactly the same two-line registration
   (import + forFeature array entry) in that same file, and nothing else, for its table to be auto-created
   per tenant DB on next backend deploy. No controller, service, DTO, or route is required for the table
   itself to exist and be writable by `sc-saas-admin` directly via Medoo — this is exactly how
   `broadcast_messages` itself already works today (admin inserts directly; the backend entity exists only
   for schema).
10. **Partner-approval-request precedent** (a different, partner-*profile*-approval flow, informative but
    not reused) — `sc-saas-backend/src/modules/partner/partner.service.ts::requestApproval() (:589-637)`
    sets `isApprovalRequested`/`approvalStatus = SUBMITTED` and emails only the **submitting user**; there
    is **no existing push notification to a Hub admin anywhere in this codebase** for any "needs review"
    state — Hub admins today discover pending items by browsing a list (pull model). This feature's Hub
    approval queue follows that same pull model (a list + live badge count), not a new push notification to
    the Hub admin — consistent with every other "pending approval" surface in this codebase.

### "Hub ecosystem" scope for an approved Hub-targeted send — explicit design decision

The plain-English requirement is genuinely ambiguous between "the whole Hub ecosystem, unfiltered by
partner" and "every partner's ecosystem except partner-owned records." Per Evidence #4, the existing
Hub-admin broadcast (`create.php:789-887`) has **zero** `partner_id`-based filtering today — it sends to
whoever matches the selected checkboxes/filters, full stop, regardless of any stakeholder's `partner_id`.
**Decision: an approved Hub-targeted Spoke broadcast reuses this exact existing unscoped resolution
unchanged** (the same recipient-building code path the Hub admin's own broadcasts already use), not a new
`partnerId IS NULL`-restricted subset. Rationale: this is what "the Hub's ecosystem" means everywhere else
in this codebase today (there is no other definition to diverge to), and inventing a narrower definition
here would make the approved-Hub-targeted send behave differently from the Hub admin's own send using
identical filter criteria — a confusing, undocumented special case. Stated explicitly here per the
document owner's request, since it could otherwise be read either way.

## Problem

Sanchiconnect's Partner ("Spoke") self-service portal (`sc-saas-admin/modules/partners/`) has no way for a
partner to message their own or the Hub's ecosystem today — the only existing broadcast capability
(`modules/broadcast_messages/`) is Hub-admin-only, gated by a permission column a partner session can never
hold (Evidence #2). This blocks a real, requested workflow: partners want to reach their own
stakeholders instantly, and occasionally reach the Hub's full ecosystem — but the latter must go through
Hub approval, since an unreviewed partner-initiated broadcast to the whole tenant ecosystem is a real
blast-radius/reputation risk the Hub needs to control. This spec adds both paths, a new request/audit table
backing them, a Hub-side approval queue (with the same live-badge-count and reason-required-rejection
pattern already proven in `outreach_requests`, but without repeating that module's two confirmed
authorization gaps), and a partner-facing "my broadcasts" status view.

## Acceptance criteria

- [ ] A logged-in partner session (`checkPartnerLoggedIn()`) can open a new compose form in
      `modules/partners/` with the same field set as the Hub's `broadcast_messages/create.php` (title,
      message, receiver user types/profile statuses, geography, industries, technologies, programs,
      delivery methods, header image, attachment), plus a new Self/Hub target-scope selector.
- [ ] Submitting with **Self** selected sends instantly: recipients are resolved with `partner_id =
      <submitting partner's own id>` only (never another partner's or the Hub's non-partner stakeholders),
      dispatched over the selected channels (email via `sendBroadcastEmail()`, chat, community-wall — all
      reused unchanged), and a `partner_broadcast_requests` row is written with `status = 'sent'`,
      `target_scope = 'self'` in the same request.
- [ ] Submitting with **Hub** selected writes a `partner_broadcast_requests` row with `status = 'pending'`,
      `target_scope = 'hub'` — no send happens yet, and no existing Hub-admin broadcast or its
      `broadcast_messages` audit table is touched.
- [ ] A Hub admin with `can_broadcast_messages = 1` sees pending Hub-targeted Spoke requests in a new
      approval queue, with a live pending-count badge computed the same way `pendingPromotionsCount` is
      today (no caching, recomputed per request) — a Hub admin without this permission cannot see or act on
      the queue.
- [ ] Every pending request in the approval queue displays its full recipient-targeting criteria (user
      types, profile statuses, geography, industries, technologies, programs, delivery methods) — a Hub
      admin can see exactly who a request would reach without leaving the queue, before deciding to
      approve or reject.
- [ ] Approving a pending request sends it to the full, unscoped Hub ecosystem using the exact same
      recipient-resolution code path the Hub admin's own `broadcast_messages/create.php` send already uses
      (no partner-based filtering — see "Hub ecosystem" scope decision above), sets `reviewed_by` /
      `reviewed_on`, and transitions the row `pending -> approved -> sent` (the `sent` transition only after
      dispatch is attempted).
- [ ] Rejecting a pending request requires a non-empty `rejection_message`, sets
      `status = 'rejected'`, `reviewed_by`, `reviewed_on`, and triggers a new email notification to the
      submitting partner via the new `POST v1/admin-actions/partner-broadcast-rejected/{adminToken}` route
      — the partner is never left to discover a rejection only by polling the UI.
- [ ] Every mutating action (submit, approve, reject) enforces that the acting session can only act within
      its own tenant DB connection (structural, already true for every admin module) **and**, additionally,
      a partner session can only read/act on `partner_broadcast_requests` rows where `partner_id` matches
      its own `$_SESSION['partner_id']` — this is a new, explicit check this feature must add, since no
      such per-partner row-ownership table existed before it.
- [ ] A partner can open a "my broadcasts" history view listing every `partner_broadcast_requests` row they
      submitted (both Self and Hub scope) with its current status, mirroring `outreach_requests`'
      sent/received-tabs UI pattern.
- [ ] With `can_broadcast_messages` off for the Hub admin, and `checkPartnerLoggedIn()` failing for a
      non-partner session, none of the new routes are reachable — verified per the same guard-clause
      convention already used throughout both modules.
- [ ] No existing `broadcast_messages` row, `ses_email_queue` correlation, or `details.php` stats view
      behavior changes for any existing Hub-admin broadcast.

## Per-repo plan

### backend (`sc-saas-backend`) — Linear: SAN-392

- New `src/modules/global/broadcast_messages/partner-broadcast-requests.entity.ts` —
  `PartnerBroadcastRequestsEntity` (table `partner_broadcast_requests`), mirroring
  `BroadcastMessagesEntity`'s shape (`geography`, `receiverUserTypes`, `receiverProfileStatuses`,
  `deliveryMethods`, `industries`/`technologies`/`programs`/`applicationPrograms`, `title`, `message`,
  `totalReceivers`, `headerImage`, `attachment`, timestamps), plus new columns: `partnerId` (int, not null —
  the submitting partner), `targetScope` (enum `self`|`hub`), `status` (enum
  `pending`|`approved`|`rejected`|`sent`, default `pending`), `reviewedBy` (int, nullable —
  `spa_admin_users.id` of the acting Hub admin), `reviewedOn` (timestamp, nullable), `rejectionMessage`
  (text, nullable).
- **Existing file — required touch (registration only):** `src/modules/global/global.module.ts` — one
  import line + one entry in the existing `TypeOrmModule.forFeature([...])` array (same pattern as
  `BroadcastMessagesEntity` at lines 131/232 today), so `synchronize: true`
  (`src/core/database/database.module.ts:32`) auto-creates the table on next deploy. No other code in this
  file changes.
- New notification routes (new controller method(s) alongside the existing `admin-actions` controller that
  already serves `broadcast-ceo-message` — exact file TBD at implementation, following that controller's
  existing conventions):
  - `POST v1/admin-actions/partner-broadcast-approved/{adminToken}` — emails the submitting partner that
    their Hub-targeted broadcast was approved and sent.
  - `POST v1/admin-actions/partner-broadcast-rejected/{adminToken}` — emails the submitting partner with
    the `rejection_message`.
  Both are new, narrow, broadcast-specific endpoints — not calls into `outreach_requests`'
  `promotion-request/*` routes, and no change to any existing route/DTO.
- No change to `broadcast_messages.entity.ts` itself, `ses-email.service.ts`'s existing broadcast method, or
  any existing controller route.

### admin (`sc-saas-admin`) — Linear: SAN-393 (partner-portal side), SAN-394 (Hub-side approval)

**Partner-portal side (SAN-393):**
- New `modules/partners/broadcast/create.php` (routed `partners/broadcast/create`, guarded by
  `checkPartnerLoggedIn()`) — compose form + AJAX handlers, mirroring
  `modules/broadcast_messages/create.php`'s field set and `submitAction` branch convention
  (`getStates`/`getCities` reused via the same geography helpers; a new `calculatePartnerBroadCastRecipients`
  dry-run count; a new `submitPartnerBroadcast` action).
  - **Self** branch: recipient resolution is a `partner_id`-scoped sibling of `create.php:789-887`'s
    per-type switch (reused query shapes, added `partner_id = $_SESSION['partner_id']` predicate on the
    relevant stakeholder tables) — not a duplicated copy of the whole file. Dispatches via
    `sendBroadcastEmail()` (using `generatePartnerRandomStringForBackdoor()` per Evidence #6's existing
    branch pattern), chat, community-wall exactly as today. Writes a
    `partner_broadcast_requests` row with `status = 'sent'`, `target_scope = 'self'` directly (no
    intermediate `pending` state).
  - **Hub** branch: writes a `partner_broadcast_requests` row with `status = 'pending'`,
    `target_scope = 'hub'` — no send.
  - Gate: `checkPartnerLoggedIn()` only (Decision #6) — no new permission column.
- New `modules/partners/broadcast/list.php` (routed `partners/broadcast/list`) — "my broadcasts" history
  view, filtered to `partner_id = $_SESSION['partner_id']` only, mirroring `outreach_requests/list.php`'s
  tab/pagination conventions (a single tab here, not sent/received, since a partner only ever submits, never
  receives, a Spoke broadcast).
- New templates under `themes/default/html/partners/broadcast/` (`create.php`, `list.php`).
- **Existing file — required touch:** the partner sidebar menu config (wherever `getPartnerMenus()`
  sources its entries, alongside the existing `feature_key`-gated rows in `config/config.php`) — add one new
  "Broadcast" menu entry. Per Decision #6, this entry ships with **no** `feature_key` gate (always visible
  to any partner session), consistent with menu entries in that config that have no `feature_key` set.

**Hub-side approval (SAN-394):**
- New `modules/broadcast_messages/approvals.php` (routed `broadcast_messages/approvals`, guarded by the
  same `if (!$canbroadCastMessage) { redirect }` convention as every other route in this module) — lists
  `pending`, `target_scope = 'hub'` rows from `partner_broadcast_requests`, with approve/reject AJAX actions.
  **Added 2026-08-19, per the document owner:** each row must display the full recipient-targeting
  criteria the Spoke selected — `receiverUserTypes`, `receiverProfileStatuses`, `geography`, `industries`,
  `technologies`, `programs`, `deliveryMethods` — not just the title and submitting partner's name. A Hub
  admin is about to send to the full unscoped Hub ecosystem on approval; they must be able to see exactly
  who that reaches before approving, not approve blind. Render this either inline on each list row (if
  compact enough) or in an expandable detail panel per row — implementer's choice — but it must be visible
  without leaving this screen, matching this module's "no need to open a separate page" design goal.
  - `approveSpokeBroadcast`: loads the row, **verifies it belongs to this tenant's own DB connection**
    (structural, already true) and is still `pending` (no double-approve race), performs the actual send
    using the exact same unscoped recipient-resolution code path as `create.php:789-887` (see "Hub
    ecosystem" scope decision), sets `reviewedBy`/`reviewedOn`, transitions `approved -> sent`, then calls
    the new `partner-broadcast-approved` backend route.
  - `rejectSpokeBroadcast`: requires a non-empty `rejection_message` in the payload (reject the AJAX call
    with a validation error otherwise), sets `status = 'rejected'`, `reviewedBy`/`reviewedOn`, calls the new
    `partner-broadcast-rejected` backend route.
  - Both actions additionally re-check `can_broadcast_messages` server-side inside the AJAX handler itself
    (not just the page-level redirect guard) — the explicit, new role-gating check this spec requires,
    since `outreach_requests`' equivalent handlers have no role check at all (Evidence #3).
- New template `themes/default/html/broadcast_messages/approvals.php`.
- **Existing file — required touch:** `modules/common.php` — new `$pendingSpokeBroadcastCount` variable,
  computed live (no caching) as `COUNT(*)` on `partner_broadcast_requests` where `status = 'pending' AND
  target_scope = 'hub'`, gated the same way `$canbroadCastMessage` already is
  (`isset($getAdminAccessLevels["id"]) && can_broadcast_messages == "1"`) — replicates the
  `pendingPromotionsCount` pattern (lines 630-647), does not touch or reuse that variable itself.
- **Existing file — required touch (small):** wherever the existing broadcast bell/megaphone nav icon is
  rendered (`themes/default/html/elements/header.php` / `header_without_sidebar.php`, per
  `broadcast_messages/module.spec.md`'s confirmed link location) — add the new pending-count badge next to
  the existing "Broadcast Messages" link, and a link to the new approvals queue.
- No change to `broadcast_messages/list.php`, `create.php`, or `details.php`'s existing behavior, and no
  touch to the dead `broadcast_message.php` (singular) or any `details copy*.php` file.

## Contracts & invariants

- **Flags:** none new. `can_broadcast_messages` (existing `spa_admin_users` permission column) continues to
  gate all Hub-side actions unchanged; no cockpit/tenant-level flag is introduced (Decision #6). Not a
  workspace flag-name invariant concern since nothing here is a `tenant_users` boolean.
- **API:** two new, narrow `sc-saas-backend` routes (`partner-broadcast-approved`, `partner-broadcast-rejected`),
  both under the existing `admin-actions`/`{adminToken}` auth convention, consumed only by the new
  `sc-saas-admin` approval module — no existing controller, DTO, or route changes. Run `/audit-contract`
  once these two routes exist to confirm the DTO shapes admin actually posts match what the new controller
  method(s) expect.
- **Events:** none — synchronous HTTP calls and direct DB writes, same as the existing broadcast module.
- **Invariants at risk:**
  1. *Flag names (owned by `tenants`)* — not touched; no new flag.
  2. *API contract (owned by `sc-saas-backend`)* — two new additive routes; no existing route's
     path/method/DTO shape changes. Lowest-risk category of contract change.
  3. *Tenant-verification contract (owned by `tenants`)* — not touched.
  4. *Auth (JWT)* — not touched; the new backend routes reuse the exact same `{adminToken}` /
     `generateRandomStringForBackdoor()` pattern already used by `broadcast-ceo-message`, including its
     known non-partner-scoped concurrency caveat (Evidence #6) — not worsened by this feature, but worth
     watching if it becomes a real concurrency bottleneck at higher volume.
  5. *Tenant scoping* — `partner_broadcast_requests` lives in the same per-tenant client DB as every other
     table this feature touches (no new cross-tenant surface, unlike `outreach_requests`' shared
     `program_promotions`). The **new** scoping requirement this feature adds is intra-tenant,
     cross-*partner* isolation: every partner-facing read/write on this table must filter by
     `$_SESSION['partner_id']`, exactly as `partners/photo_gallery` already does for `partner_events`. This
     is the concrete, new obligation called out in the Acceptance criteria and the admin per-repo plan —
     explicitly not repeating `outreach_requests`' missing-ownership-check gap.
  6. *Cross-workspace PowerPitch contract* — not touched.

## Test plan

- backend: unit test confirming `PartnerBroadcastRequestsEntity` registers and its table is created via
  `synchronize: true` in a test DB; unit tests for both new `admin-actions` methods (payload validation,
  correct email template selection for approved vs. rejected).
- admin: `php -l` on all new files. Manual walkthrough: (1) partner submits Self broadcast — confirm
  recipients are strictly the submitting partner's own stakeholders, confirm `partner_broadcast_requests`
  row lands as `sent`/`self` in one step; (2) partner submits Hub broadcast — confirm no send happens, row
  is `pending`/`hub`; (3) Hub admin without `can_broadcast_messages` cannot see/act on the approval queue;
  (4) Hub admin with the permission approves — confirm recipients match exactly what the Hub admin's own
  unscoped broadcast would reach for the same filters, confirm email arrives at the submitting partner via
  the new approved-notification route; (5) Hub admin rejects without a reason — rejected client-side/
  server-side; rejects with a reason — confirm `rejection_message` stored and the rejection email arrives;
  (6) a second partner cannot see or act on the first partner's `partner_broadcast_requests` rows via the
  "my broadcasts" view or any direct action call with a guessed `id`.
- cross-repo: confirm the new backend routes are deployed and reachable before enabling the Hub-side
  approve/reject UI in admin (deploy backend first, per `repos:` order) — approving/rejecting against a
  not-yet-deployed backend route should fail loudly (visible error), not silently drop the notification.

## Rollout

- Deploy order matches `repos:`: `sc-saas-backend` first (new entity + `synchronize: true` creates the
  table across all tenant DBs at boot; new notification routes live), then `sc-saas-admin` (partner-portal
  compose/self-send/my-broadcasts, then Hub-side approval queue — these two admin pieces can ship together
  or approval-queue-first, since a `pending` row sitting unactionable causes no harm, but shipping compose
  before approval-queue would let partners submit Hub requests nobody can yet act on; prefer shipping both
  admin pieces in the same release).
- No feature flag / staged rollout beyond normal deploy — this is a net-new, additive capability with no
  existing behavior to regress (no existing route, table, or UI element is modified). If the document owner
  wants a kill switch before general availability, the lowest-risk option is gating the new partner sidebar
  menu entry behind a manually-toggled `feature_key` added at implementation time — not designed here since
  it wasn't requested and isn't required for correctness.

## Out of scope

- Any change to the existing Hub-admin `broadcast_messages` module's own compose/send/list/details behavior
  — this feature is purely additive alongside it.
- Any change to `outreach_requests`' own code — it is cited only as a pattern to mirror, not modified.
- Fixing `outreach_requests`' confirmed missing-ownership-check and missing-role-gating gaps (Evidence #3) —
  those are this module's own pre-existing issues, independent of this feature; not bundled here.
- Fixing `generatePartnerRandomStringForBackdoor()`'s shared-account race condition (Evidence #6) — a
  pre-existing, independent concurrency bug; this feature reuses the function as-is.
- SMS/WhatsApp broadcast channels — the existing module has none (only email/chat/community-wall) and this
  feature doesn't add any.
- A tenant-level kill switch / feature flag for this whole capability — not designed here (see Rollout).
- The Multi-Tenant Hub/Spoke Domain & White-Label Architecture project (SAN-384..SAN-391) — related in
  spirit, tracked separately, not touched by this spec.

## Open questions

None blocking. All ambiguity in the original plain-English requirement was resolved either by an explicit
decision confirmed with the document owner, or by an explicit, evidence-grounded design call made by this
document's author and stated plainly above (see Decisions #5, #6, and the "Hub ecosystem" scope decision) —
each is flagged as an author's call where it wasn't independently confirmed, so the document owner can
override before approving this spec.
