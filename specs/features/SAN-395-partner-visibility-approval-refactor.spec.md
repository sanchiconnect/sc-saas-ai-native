---
id: SAN-395                     # Linear Project created (team: Sanchiconnect); anchored to its lowest-numbered
                                 # issue, SAN-395. Full issue set: SAN-395 (de-duplication refactor), SAN-396
                                 # (unified bulk view), SAN-397 (reject action + reset-bug fix, admin),
                                 # SAN-400 (reject-notification email route, backend — added 2026-08-19 once
                                 # the document owner confirmed rejection reasons are emailed, not just shown
                                 # in-app). All assigned to Nirmal Singh per the document owner's instruction.
title: Partner Visibility & Approval Refactor
type: feature
status: approved                # Approved by the document owner 2026-08-20 to begin implementation. Zero blocking Open Questions remain as of
                                 # 2026-08-19 — the one open item (reject-notification channel) was resolved
                                 # by the document owner (email, mirroring Outreach Requests/SAN-392). Moving
                                 # to `approved` remains an explicit call for the document owner.
linear: https://linear.app/sanchiconnect/project/partner-visibility-and-approval-refactor-4ef2a5b8e218
owner: nirmal.s@sanchiconnect.com
repos: [backend, admin]        # Corrected 2026-08-19 — was [admin] only; now touches sc-saas-backend too,
                                 # since the confirmed reject-notification-by-email design requires a new
                                 # backend email-sending route (mirroring SAN-392's pattern). Backend first
                                 # in dependency order — admin's reject action calls its new route.
contracts:
  api:
    - "POST v1/admin-actions/partner-visibility-request-rejected/{adminToken} (sc-saas-backend, NEW — emails
       the requesting partner a rejection reason for a partner-visibility/association request; patterned
       after SAN-392's partner-broadcast-rejected route and outreach_requests' sendRejectedEmailApi(), not
       the same endpoint as either)"
  flags: []                     # No tenant/cockpit flag gates this feature today (gated by admin role +
                                 # session type, not a TenantUsersEntity flag) and none is added.
  events: []
tenant_scoped: true             # sc-saas-admin selects the per-tenant DB via admin_domain per the workspace's
                                 # tenant-scoping rule (invariant #5); every table this feature reads/writes
                                 # (startups, investors, mentors, corporates, service_providers, individuals,
                                 # program_office_members) lives in that per-tenant DB. The one new backend
                                 # route lives inside that same tenant's own one-deployment-per-tenant API.
depends_on: []
created: 2026-08-19
---

# Partner Visibility & Approval Refactor

## Reference

This spec did **not** originate from a pre-existing Linear issue. It was flagged by the document owner
(Nirmal) while reviewing `startup-detail.php` directly in his IDE and sharing screenshots of the live
Hub-admin and Partner-portal views. Every file/line reference in this spec was verified directly against the
live `sc-saas-admin` code during this session — cited below, not re-derived. This feature is related in
spirit to SAN-384 (Multi-Tenant Hub/Spoke Domain & White-Label Architecture) and SAN-392 (Spoke Broadcast
Messages with Hub Approval) — same Hub/Spoke ecosystem — but is tracked as its own spec and Linear project
per the document owner's explicit decision not to fold it into either.

## The requirement (as stated by the document owner)

"these actions also implemented for Hub/Spoke ecosystem. please review this and i want this more flexible
because its implemented on every startup details page. hub/spoke need to go every startups details page then
performed on the action of that page. no any common area for manage that. please review this and check how
can make this more flexible"

In plain terms: the existing "Visibility" (Hub admin grants specific partners visibility into a stakeholder
record) / "Send Request" (a partner requests Hub approval to associate with a stakeholder) / "Approval
Request" (Hub admin reviews and accepts) feature is duplicated per-page across every stakeholder detail page,
forcing Hub/Spoke users to visit each stakeholder's detail page individually with no common/bulk way to
manage requests across many stakeholders at once. Confirmed via follow-up with the document owner to mean:
(1) de-duplicate the copy-pasted implementation into shared, parameterized code, and (2) add a bulk/unified
management view so this doesn't require visiting every detail page one at a time.

## Decisions (confirmed with the document owner)

1. **Genuinely separate feature/spec/Linear project**, not folded into SAN-384 or SAN-392 (confirmed).
2. **The bulk/common management view is one unified list across all 7 stakeholder types** (startups,
   investors, mentors, corporates, service_providers, individuals, program_office_members), with a type
   column/filter — not 7 separate per-type lists (confirmed).
3. **Two behavior fixes are explicitly in scope alongside the pure refactor**: (a) fix
   `partner_approval_request` never resetting to `0` after a cycle completes, and (b) add a proper reject
   action for partner-association requests (today only accept exists) (confirmed).
4. **Reset-bug trigger — decided by this document's author, per the requirement's instruction to "use your
   judgment and document the choice"**: `partner_approval_request` resets to `0` in exactly two cases —
   (i) when the new reject action (Decision 3b / SAN-397) is exercised, and (ii) when the Hub admin removes
   the requesting partner from `associated_partners` via the Visibility panel for that stakeholder (i.e. the
   partner that had `partner_approval_request = 1` pending is no longer in the visibility list — treat that
   as an implicit withdrawal of the association, not just a visibility change). No other trigger resets it
   (e.g. accepting a request does *not* reset it — accept already sets `approval_type => "fully"` and leaves
   the flag at `1`, which this spec preserves as-is per the behavior-preserving-refactor rule; the reset
   applies only going forward from reject/removal, both new/changed paths).
5. **Reject notification channel — confirmed by the document owner 2026-08-19**: a rejection reason is
   emailed to the requesting partner, mirroring the Outreach Requests (`sendRejectedEmailApi()`) and
   SAN-392 (Spoke Broadcast) pattern — not shown only in-app. This resolves the spec's one previously-open
   question and adds a new, narrow `sc-saas-backend` route (see Per-repo plan) — the one place this
   feature now crosses a repo boundary.

## Problem

The partner-visibility/approval-request mechanism — `associated_partners` (JSON array of partner IDs),
`partner_approval_request` (0/1 flag), `approval_type` (`"partially"`/`"fully"`) — is implemented as
~180-190 lines of copy-pasted controller + template code (≈90-97 controller lines + ≈87-92 template lines,
plus duplicated inline JS) repeated verbatim across all 7 stakeholder detail pages in `sc-saas-admin`, with
only the record-ID variable name and destination table/entity name changing between copies. A normalized
diff between the investor and corporate controller blocks showed only one further difference beyond the
ID/table tokens: a single error-message string ("Missing investor ID." vs "Missing corporate ID."). This is
genuine copy-paste duplication, not parameterized reuse — `grep -rln "associated_partners\|partner_approval_request" includes/ core/` returns zero files, confirming no shared code exists today.

Consequences of the duplication, beyond maintenance cost:
- **No bulk/cross-stakeholder view exists anywhere.** `partner_approval_request` never appears in any
  `list.php` outside the 7 detail files. A Hub/Spoke user today has no way to see or act on pending
  partner-approval requests without opening each stakeholder's detail page individually.
- **`partner_approval_request` never resets to `0`.** Both `sendApprovalRequest` (sets it to `1`) and
  `acceptApprovalRequest` (sets it to `1` again, plus `approval_type => "fully"`) only ever write `1` —
  confirmed by direct read of all 7 controller blocks. Nothing anywhere writes `0` back.
- **No reject action exists.** Only accept is implemented anywhere in this controller pattern.

## Important distinction (do not conflate)

This mechanism (`associated_partners` / `partner_approval_request` / `approval_type`) is **not** the same as
the stakeholder's own general profile-approval workflow (`approval_status` / `is_approved` / `is_rejected` /
`approved_by` / `approved_on`, handled by a separate `submitAction == "updateApprovalStatus"`). The two
mechanisms coexist independently on the same row. This spec touches only the former; the latter is explicitly
out of scope (see Out of scope).

`modules/outreach_requests/` (`list.php`/`tracking.php`) is also unrelated — confirmed — it operates on a
completely different table (`program_promotions`, shared main DB) for cross-tenant program-promotion
requests, not partner-to-stakeholder visibility/association. Its own `module.spec.md` explicitly notes no
overlap with any connections/visibility mechanism. It is cited here only as the existing precedent for the
`rejection_message`-style free-text-reason convention this spec's new reject action follows.

## Evidence — current code state (all verified this session)

**Controller blocks** (`modules/*-detail.php`), each implementing 3 `submitAction`s
(`sendApprovalRequest`, `acceptApprovalRequest`, `updateVisibility`):

| File | Lines | Table written |
|---|---|---|
| `modules/startup-detail.php` | 1813-1909 | `startups` |
| `modules/investor-detail.php` | 808-899 | `investors` |
| `modules/mentor-detail.php` | 840-931 | `mentors` |
| `modules/corporate-detail.php` | 727-818 | `corporates` |
| `modules/service-provider-detail.php` | 720-811 | `service_providers` |
| `modules/individual-detail.php` | 740-831 | `individuals` |
| `modules/program-office-detail.php` | 587-678 | `program_office_members` |

(Module+template pair for program office members is named `program-office-detail`, not
`program-office-member-detail` — covers the `program_office_members` table.)

`sendApprovalRequest` sets `partner_approval_request => 1` (e.g. `startup-detail.php:1826-1828`);
`acceptApprovalRequest` sets `approval_type => "fully", partner_approval_request => 1` (e.g.
`startup-detail.php:1859-1862`). `updateVisibility` writes `associated_partners` via a plain overwrite —
`$database->update($table, $postData, ["id" => $recordId])` — no merge/diff against the existing list.

**Template blocks** (`themes/default/html/*-detail/*-detail.php`), each rendering 3 cards, gated by
session-type + record-state conditions re-typed identically in every file (shown for `startup-detail`, same
pattern/offsets in all 7):

| File | Lines |
|---|---|
| `themes/default/html/startup-detail/startup-detail.php` | 1309-1400 |
| `themes/default/html/investor-detail/investor-detail.php` | 750-836 |
| `themes/default/html/mentor-detail/mentor-detail.php` | 598-684 |
| `themes/default/html/corporate-detail/corporate-detail.php` | 594-680 |
| `themes/default/html/service-provider-detail/service-provider-detail.php` | 654-740 |
| `themes/default/html/individual-detail/individual-detail.php` | 743-829 |
| `themes/default/html/program-office-detail/program-office-detail.php` | 602-688 |

- Hub-admin "Visibility" card (`startup-detail.php:1309`):
  `($_SESSION['admin_roles']['code'] == developer_role_id || $_SESSION['admin_roles']['code'] == super_admin_role_id) && $this->brandSettings['associated_partners_visibility_enabled'] == "1"`.
  Renders a multi-select of ALL partners in the tenant (`$this->partners`, loaded unconditionally),
  pre-selected from `json_decode($this->record['associated_partners'])`.
- Hub-admin "Approval Request" review card (`:1351`): `$this->record["approval_type"] == "partially" && $this->record["partner_approval_request"] == "1"` plus the same admin-role check. Shows only an Approve
  action today — no reject.
- Partner-portal "Send Request" card (`:1377`): `$this->record["partner_approval_request"] == "0" && $this->record["approval_type"] == "partially" && isset($_SESSION['partner_id'])`.

**Session-branching duplicated per file, not shared**: `$_SESSION['admin_roles']['code']` checked against
`developer_role_id`/`super_admin_role_id` constants for Hub-admin views, `isset($_SESSION['partner_id'])`
for the Partner-portal view — no shared `isHubAdminSession()`/`isPartnerSession()` helper exists anywhere in
`includes/`.

**No shared code today.** The only reference outside the 7 detail modules is `modules/common.php:493-494`,
which adds `associated_partners` as a read-only display column on the generic startups list-view (renders
raw JSON, no management capability) — not shared business logic.

## Acceptance criteria

- [ ] The 3-`submitAction` logic (`sendApprovalRequest`, `acceptApprovalRequest`, new `rejectApprovalRequest`,
      `updateVisibility`) exists in exactly one shared, parameterized location, called from all 7
      `modules/*-detail.php` controllers — no duplicated copy remains in any of the 7 files.
- [ ] The 3-card (now 3-card-with-reject) template block exists in exactly one shared partial, included from
      all 7 `themes/default/html/*-detail/*-detail.php` templates — no duplicated copy remains.
- [ ] Session-branching checks (`isHubAdminSession()`, `isPartnerSession()`) exist as shared helpers in
      `includes/`, used by the new shared code.
- [ ] For every one of the 7 stakeholder types, existing behavior is unchanged for: visibility multi-select
      save (`updateVisibility`), send-request (`sendApprovalRequest`), and accept
      (`acceptApprovalRequest` → `approval_type => "fully"`, `partner_approval_request` stays `1`) —
      verified by manual walkthrough per type (see Test plan).
- [ ] A Hub admin can reject a pending partner-approval request from the stakeholder detail page, providing a
      free-text rejection reason; the reason is persisted **and emailed to the requesting partner** via the
      new `POST v1/admin-actions/partner-visibility-request-rejected/{adminToken}` route — the partner is
      never left to discover a rejection only by revisiting the UI.
- [ ] Rejecting a request sets `partner_approval_request` back to `0` for that stakeholder record.
- [ ] Removing a partner from `associated_partners` (via the Visibility panel) for a stakeholder that has a
      pending request (`partner_approval_request == 1`) from that same partner also resets
      `partner_approval_request` back to `0` for that record.
- [ ] A new unified list view (reachable from a common nav location, not from within any stakeholder detail
      page) shows every pending partner-approval request (`partner_approval_request = 1`) across all 7
      stakeholder types in a single table, with a column/filter identifying the stakeholder type.
- [ ] Approve and reject actions are available directly from the unified list view, without navigating to the
      individual stakeholder's detail page, and produce the same end state as acting from the detail page.
- [ ] The unified list view is gated by the same Hub-admin role check used today
      (`developer_role_id`/`super_admin_role_id`).
- [ ] The general profile-approval workflow (`approval_status`/`is_approved`/`is_rejected`/`approved_by`/
      `approved_on`/`updateApprovalStatus`) is verified unchanged (no field renamed, no behavior altered) on
      all 7 stakeholder types.
- [ ] `php -l` passes clean on every new/changed file.

## Per-repo plan

### backend (`sc-saas-backend`) — Linear: SAN-400

- New controller method alongside the existing `admin-actions` controller that already serves
  `broadcast-ceo-message`/SAN-392's two new routes (exact file TBD at implementation, following that
  controller's existing conventions): `POST v1/admin-actions/partner-visibility-request-rejected/{adminToken}`
  — resolves the requesting partner's contact email (via the partner's linked `users` account, same
  resolution `PartnerEntity` already supports elsewhere in this codebase), and emails them the stakeholder
  name, entity type, and the Hub admin's free-text rejection reason.
- No change to any existing route, DTO, or the general profile-approval workflow's email templates — this
  is a new, narrow, purpose-built notification, not a repurposing of `broadcast-ceo-message` or the
  `outreach_requests` promotion-request email endpoints.

### admin

1. **Shared controller functions** (SAN-395) — new file `includes/partner_visibility_functions.php`
   exposing parameterized functions for `sendApprovalRequest`, `acceptApprovalRequest`,
   `rejectApprovalRequest` (new), and `updateVisibility`, each taking `$table`, `$idField`, `$recordId`,
   `$entityLabel` (for error messages, e.g. "Missing investor ID.") as parameters. Update all 7
   `modules/*-detail.php` files to call these shared functions instead of their own copy-pasted blocks,
   passing their own table/idField/label.
2. **Shared session helpers** (SAN-395) — new functions `isHubAdminSession()` and `isPartnerSession()` in
   `includes/` (exact file at implementer's discretion, e.g. `includes/session_helpers.php` or an existing
   suitable include), replacing the duplicated `$_SESSION['admin_roles']['code'] == developer_role_id ||
   ... == super_admin_role_id` / `isset($_SESSION['partner_id'])` checks in both the new shared controller
   functions and the shared template partial below. Note as available for future reuse elsewhere in these
   same files, without touching unrelated logic.
3. **Shared template partial** (SAN-395) — new file
   `themes/default/html/elements/partner_visibility_cards.php`, parameterized by the same
   `$table`/`$idField`/`$entityLabel` (plus `$record`, `$partners`, `$brandSettings` already available in
   each detail template's scope), rendering the Visibility card, the Approval Request review card (now with
   both Approve and Reject actions), and the Send Request card. Update all 7
   `themes/default/html/*-detail/*-detail.php` templates to `include` this partial instead of their own
   copy-pasted card markup + inline JS.
4. **Reject action** (SAN-397) — implement `rejectApprovalRequest` in the shared controller functions from
   step 1: accepts a free-text rejection reason, persists it (new column or reuse of an existing
   `rejected_message`-style field — implementer's choice, follow the `rejection_message` naming convention
   already used by the general profile-approval workflow and `outreach_requests`), resets
   `partner_approval_request => 0`, and calls the new backend route (see backend plan above) so the
   requesting partner is emailed the reason — confirmed by the document owner, not just an in-app display.
   Update the shared template partial (step 3) to render a Reject button + reason field alongside the
   existing Approve button on the "Approval Request" review card.
5. **Reset on visibility removal** (SAN-397) — in the shared `updateVisibility` function (step 1), after
   computing the new `associated_partners` list, detect whether the partner that currently holds
   `partner_approval_request == 1` for this record has been removed from the new list; if so, also write
   `partner_approval_request => 0` in the same update call.
6. **Unified bulk view** (SAN-396) — new module `modules/partner-requests/list.php` (+ matching template),
   querying all 7 tables for `partner_approval_request = 1` rows (UNION-style query or a per-table loop
   merged in PHP — implementer's choice), each row tagged with its stakeholder type, rendered in one list
   with a type column/filter. Gated by the same `developer_role_id`/`super_admin_role_id` check as the
   detail-page cards (via the new `isHubAdminSession()` helper from step 2). Approve/Reject actions on each
   row call the same shared functions from step 1 (passing that row's table/idField), so no separate
   business logic is written for the bulk view.
7. **Nav entry** (SAN-396) — add a common nav link to the new `modules/partner-requests/list.php` view,
   visible only to Hub-admin sessions.
8. **No changes** to `approval_status`/`is_approved`/`is_rejected`/`approved_by`/`approved_on`/
   `updateApprovalStatus` anywhere.

## Contracts & invariants

- **Flags:** none — this feature is gated by admin role (`developer_role_id`/`super_admin_role_id`) and
  session type (`$_SESSION['partner_id']`), plus the existing tenant-level brand setting
  `associated_partners_visibility_enabled` (a `brandSettings` value, not a `TenantUsersEntity` flag) — no
  change to any of these gates' names or semantics.
- **API:** one new, narrow `sc-saas-backend` route (`partner-visibility-request-rejected`), under the same
  `admin-actions`/`{adminToken}` auth convention already used by SAN-392's two new routes — the one place
  this feature now crosses a repo boundary, added 2026-08-19 once the document owner confirmed reject
  notifications are emailed. No existing route, DTO, or the general profile-approval workflow's email
  templates are touched.
- **Events:** none.
- **Invariants at risk:** **Invariant #5 (tenant scoping)** — every table this feature reads/writes
  (`startups`, `investors`, `mentors`, `corporates`, `service_providers`, `individuals`,
  `program_office_members`) already lives in the per-tenant DB selected via `admin_domain`
  (`sc-saas-admin/config/config.php`); the new unified list view's UNION-style query must run against that
  same per-tenant connection for all 7 tables — no cross-tenant query, no hardcoded tenant reference.
  **Invariant #2 (API contract, owned by `sc-saas-backend`)** — one new additive route; no existing route's
  path/method/DTO shape changes, lowest-risk category of contract change. No other one of the 6 cross-repo
  invariants (flag names, tenant-verification contract, auth, PowerPitch contract) is touched. Run
  `/check-isolation` on the new unified-view query and on the modified `updateVisibility` function, and
  `/audit-contract` once the new backend route exists, before `in-review`.

## Test plan

- backend: unit test for the new `partner-visibility-request-rejected` route (correct partner email
  resolution, correct template/reason interpolation).
- admin: `php -l` on every new/changed file (7 controllers, 7 templates, new shared include, new shared
  template partial, new `modules/partner-requests/` module + template). Manual walkthrough per stakeholder
  type: Hub-admin sets visibility → partner sends request → Hub-admin sees pending request on both the
  detail-page card and the unified list → Hub-admin rejects with a reason → `partner_approval_request`
  confirmed reset to `0`, reason visible to partner, **and rejection email received** → repeat, this time
  Hub-admin removes the requesting partner from `associated_partners` directly → `partner_approval_request`
  confirmed reset to `0` without a reject action (and without an email) having been taken. Separately verify
  the general profile-approval workflow (`approval_status`/`is_approved`/`is_rejected`) is unaffected on at
  least 2 of the 7 stakeholder types.
- cross-repo: confirm the new backend route is deployed and reachable before enabling the admin-side reject
  action — rejecting against a not-yet-deployed backend route should fail loudly (visible error), not
  silently drop the notification, matching SAN-392's equivalent requirement.

## Rollout

Deploy order: `sc-saas-backend` first (new, additive-only route — safe to deploy standalone, unreachable
until called), then `sc-saas-admin`. No migrations required in either repo if the rejection-reason field
reuses an existing `rejected_message`-style column pattern (schema-only addition if a new column is
needed — additive, backward compatible, no default-value hazard since existing rows simply have it null
until first used). No feature flag needed — behavior-preserving for the 7 existing detail pages except the
two explicitly-approved fixes (reject action, reset-on-reject/reset-on-removal), which are net-additive and
carry no risk to existing accepted/pending requests (an already-accepted request with
`partner_approval_request == 1` and `approval_type == "fully"` is unaffected unless and until a reject or a
visibility removal is newly performed against it). Per the Test plan, do not enable the admin-side reject
action until the new backend route is confirmed deployed and reachable.

## Out of scope

- The general profile-approval workflow (`approval_status`/`is_approved`/`is_rejected`/`approved_by`/
  `approved_on`, `submitAction == "updateApprovalStatus"`) — untouched, a completely separate mechanism on
  the same tables.
- `modules/outreach_requests/` and the `program_promotions` table — unrelated, cross-tenant
  program-promotion requests, not touched.
- The Hub/Spoke domain/CORS/white-label architecture (SAN-384) and Spoke Broadcast with Hub Approval
  (SAN-392) — related in spirit, tracked separately, not folded in here.
- Any change to `associated_partners_visibility_enabled` or other `brandSettings` gating semantics.

## Open questions

None. The one previously-open item — reject notification channel — was resolved by the document owner on
2026-08-19: rejection reasons are emailed to the requesting partner, mirroring the Outreach Requests /
SAN-392 pattern (see Decision #5 and the new backend route in the Per-repo plan). This spec has zero
blocking open questions as of this revision.
