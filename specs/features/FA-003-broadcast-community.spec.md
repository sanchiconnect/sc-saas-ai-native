---
id: FA-003
title: Broadcast & Community
repos:
  - sc-saas-admin
  - sc-saas-backend
status: draft
contracts:
  api:
    - (none — broadcast delivery and community moderation are admin-direct; backend is not called)
  flags: []
admin_modules:
  - sc-saas-admin/modules/outreach-communications/module.spec.md
  - sc-saas-admin/modules/community-connections/module.spec.md
backend_modules:
  - sc-saas-backend/src/modules/community-wall/module.spec.md
  - sc-saas-backend/src/modules/notifications/module.spec.md
updated: 2026-07-27
---

# FA-003: Broadcast & Community

## Summary

The broadcast and community flow covers two distinct but related admin responsibilities: sending bulk outreach messages to segmented audiences (via email, in-app chat, or a community wall post), and moderating the tenant's community wall (posts and comments). Audience resolution uses direct PDO queries against the client DB; community moderation deletes rows directly from the client DB, bypassing the backend API entirely. **Broadcast email delivery does not bypass the backend API** — corrected 2026-07-27, see below — the admin process calls `sc-saas-backend`'s `admin-actions/broadcast-ceo-message` route, which queues the send and dispatches it via `sc-saas-backend`'s own SES pipeline, not PHPMailer called directly from admin. Access to the broadcast feature is controlled by a session variable rather than a `tenant_users` feature flag column.

> **Correction (2026-07-27, Linear SAN-57):** this document previously claimed WhatsApp was a broadcast delivery channel ("email and optionally WhatsApp," "up to 12 cURL calls to the WATI REST API for template-based WhatsApp delivery"). That was never true of the as-built code and has been removed throughout this document. `modules/broadcast_messages/create.php`'s delivery-channel checkboxes are Email/Chat Tool/Community Wall only (`value="email"|"chat"|"community_wall"`, confirmed `create.php:363-378`); its POST handler never branches on a `whatsapp` value, and `broadcast_messages.delivery_methods` has never stored one. The real WATI/`wati_functions.php` cURL code is genuinely live — but it powers a separate, unrelated feature: WhatsApp *template* management on the Developer settings screen (`modules/developer/whatsapp_management.php`, gated by `wa_enable`), not Broadcast Messaging's send flow. `sc-saas-admin/modules/outreach-communications/module.spec.md` already carries this correction (2026-07-17); this document was the one still out of date.

## Admin entry points

**Broadcast creation — `modules/broadcast_messages/create.php`:** The admin user composes a message (subject, body, optional attachments), selects one or more delivery channels (Email, Chat Tool, Community Wall — no WhatsApp option exists), and defines the audience. Audience can be segmented by industry, technology stack, program membership, or individual user selection. On submission, the message is stored in the client DB and delivery begins synchronously within the same request.

**Community wall posts — `modules/community_wall/feeds.php`:** Admin sees all posts across the tenant in a time-sorted feed. No audience filter is applied — the admin always sees the full wall. Each post row has a delete action.

**Community wall comments — `modules/community_wall/comments.php`:** Admin drills into a post's comment thread and can delete individual comments. Author names are resolved by joining against the appropriate entity table based on `account_type`.

## DB flow

**Broadcast flow:**

1. **Client DB (read) — audience resolution:** Direct PDO query (not Medoo) using `JSON_CONTAINS()` against JSON columns in `tenant_users` (e.g., `industries`, `technologies`). For program-based segmentation, joins against `program_members`. The query is constructed dynamically based on the admin's filter selections. Results are a list of `user_id` + email tuples.
2. **Client DB (write) — broadcast record:** Inserts a row into `broadcast_messages` with the message content, selected channels, audience parameters, and delivery status.
3. **Client DB (write) — delivery log:** Inserts one row per recipient into `ses_email_queue` (email channel only) recording delivery status (pending → sent/failed).
4. **External delivery — via `sc-saas-backend`, not PHPMailer direct-from-admin (corrected 2026-07-27):** `sendBroadcastEmail()` (`includes/core_functions.php:4127`) cURL-POSTs to `sc-saas-backend`'s `POST admin-actions/broadcast-ceo-message/:adminToken` (`create.php:1081`), passing the filtered recipient list and message content. The backend queues the send into `ses_email_queue` (keyed by `broadcast_message_id`) and a backend cron later drains it, calling out to `sc-saas-3rdparty-webservices`'s SES module (nodemailer SMTP) — not PHPMailer, and not synchronous within the admin request.

**Community moderation flow:**

1. **Client DB (read) — post list:** SELECTs from `community_posts` ordered by `created_at` desc. No tenant filter beyond the DB connection itself (the per-tenant DB is already selected).
2. **Client DB (read) — author resolution:** Joins `community_posts.user_id` + `community_posts.account_type` to the appropriate entity table (`startups`, `investors`, `users`, etc.) to resolve the author's display name.
3. **Client DB (write) — post delete:** Direct DELETE on `community_posts` by `post_id`. No backend API call; the backend's own community-wall module reads from the same client DB, so the row disappears from the frontend immediately.
4. **Client DB (read) — comment list:** SELECTs from `community_comments` filtered by `post_id`.
5. **Client DB (read) — comment author resolution:** Same join pattern as post author resolution, keyed on `account_type . "_id"` to pick the join table. Fails for `program_office` type (see Known issues).
6. **Client DB (write) — comment delete:** Direct DELETE on `community_comments` by `comment_id`.

## Backend API calls

**Corrected 2026-07-27:** broadcast email delivery *does* call the backend API — `POST admin-actions/broadcast-ceo-message` (see DB flow step 4 above) — contrary to this document's earlier claim of "no backend API calls." That route now also enforces a permission check (`canBroadcastMessages`, added 2026-07-27, Linear SAN-52) that didn't exist when this document was last updated. Community moderation is the flow that genuinely bypasses the backend API, writing directly to the client DB. The backend's `community-wall` and `notifications` modules read from the same client DB, so admin-direct writes are immediately reflected in backend-served responses to frontend clients — but there is no API handshake and no event emitted to the backend on moderation actions specifically.

## Feature flags

No `tenant_users` feature flag column governs access to broadcast or community moderation. Access to broadcast is controlled by the **`canbroadCastMessage`** PHP session variable: the admin user's session must contain this key with a truthy value. This is set during login based on a role-permission check at session creation time, not evaluated dynamically per request. Community wall moderation is always visible in the admin sidebar for any authenticated admin user with sufficient role level; there is no flag gate.

## Auth & access

- Admin must have an active PHP session.
- **Broadcast (admin UI):** Requires `$_SESSION['canbroadCastMessage']` to be truthy. This is a session-level permission, not a per-request role check. It is set at login time and persists for the session lifetime. A role change during an active session does not revoke broadcast access **from the admin UI's own page-level checks** until the next login — but see Known Issue 3, corrected 2026-07-27: the backend route itself now independently re-checks this permission on every request.
- **Community moderation:** Requires role level 1 or 2. Post and comment deletion do not require a separate permission beyond the role level gate.

## Cross-repo impact

- **sc-saas-backend community-wall module:** The backend serves community posts and comments to the frontend PWA from the same client DB tables the admin writes directly. Admin deletion of a post or comment takes effect immediately from the frontend's perspective on the next API call. There is no soft-delete or tombstone pattern — the row is hard-deleted; if the backend caches community data (e.g., in Redis or in-memory), a deleted post may still appear on the frontend until the cache expires.
- **sc-saas-backend notifications module:** The backend's notification system may have already sent push notifications for a community post that the admin subsequently deletes. There is no retraction mechanism — users who received a push notification for a post that is later deleted will see a 404 or empty state when they tap through.
- **sc-saas-frontend:** The frontend PWA's community wall feed relies on the backend API. Deleted posts are invisible after the next API call. The service-worker cache on the PWA may serve a stale feed that includes deleted content; a hard-refresh is required to force cache invalidation.

## Known issues

1. **`program_office` account type missing from comment author resolution:** In `modules/community_wall/comments.php`, comment author names are resolved by constructing a join table name as `account_type . "_id"` (e.g., `startup_id` → join `startups` table). The `program_office` account type does not follow this naming convention and has no corresponding entity table in the join map. When a `program_office` user has posted a comment, the author name resolves to null, and the comment displays with a blank or null author name in the admin view. There is no fallback and no error — the resolution fails silently.

2. ~~WATI access token stored unencrypted in `spa_settings`~~ — **out of scope for this spec, moved 2026-07-27.** This bug is real, but belongs to a separate, unrelated feature: WhatsApp *template* management on the Developer settings screen (`modules/developer/whatsapp_management.php` + `modules/ajax/whatsapp_actions.php`, gated by `wa_enable`), not Broadcast Messaging. WhatsApp is not, and has never been, a broadcast delivery channel — see the Summary correction above. Tracked wherever that feature's own module spec lives, not here.

3. **Broadcast access persists across role changes within an active session — partially fixed 2026-07-27 (Linear SAN-52).** The `canbroadCastMessage` session variable is still set once at login and never re-evaluated during the session, so the admin UI itself may still show/hide the Broadcast button based on a stale permission. However, `sc-saas-backend`'s `admin-actions/broadcast-ceo-message` route (the actual send endpoint, see DB flow step 4) now independently checks `AdminUsersEntity.canBroadcastMessages` fresh on every request — a downgraded admin can no longer actually send, even if the UI hasn't caught up yet. The remaining gap is UI staleness only, not a real authorization bypass.
