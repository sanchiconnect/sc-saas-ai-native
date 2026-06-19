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
updated: 2026-06-18
---

# FA-003: Broadcast & Community

## Summary

The broadcast and community flow covers two distinct but related admin responsibilities: sending bulk outreach messages to segmented audiences (via email and optionally WhatsApp), and moderating the tenant's community wall (posts and comments). Both flows bypass the backend API entirely — audience resolution uses direct PDO queries against the client DB, message delivery uses PHPMailer (email) or the WATI REST API (WhatsApp) called directly from the admin PHP process, and community moderation deletes rows directly from the client DB. Access to the broadcast feature is controlled by a session variable rather than a `tenant_users` feature flag column.

## Admin entry points

**Broadcast creation — `modules/broadcast_messages/create.php`:** The admin user composes a message (subject, body, optional attachments), selects a delivery channel (email only, WhatsApp only, or both), and defines the audience. Audience can be segmented by industry, technology stack, program membership, or individual user selection. On submission, the message is stored in the client DB and delivery begins synchronously within the same request.

**WhatsApp configuration — `modules/ajax/whatsapp_actions.php`:** Admin manages WATI integration credentials and template message names. This AJAX endpoint handles both reading and writing WATI settings to the `spa_settings` table in the client DB.

**Community wall posts — `modules/community_wall/feeds.php`:** Admin sees all posts across the tenant in a time-sorted feed. No audience filter is applied — the admin always sees the full wall. Each post row has a delete action.

**Community wall comments — `modules/community_wall/comments.php`:** Admin drills into a post's comment thread and can delete individual comments. Author names are resolved by joining against the appropriate entity table based on `account_type`.

## DB flow

**Broadcast flow:**

1. **Client DB (read) — audience resolution:** Direct PDO query (not Medoo) using `JSON_CONTAINS()` against JSON columns in `tenant_users` (e.g., `industries`, `technologies`). For program-based segmentation, joins against `program_members`. The query is constructed dynamically based on the admin's filter selections. Results are a list of `user_id` + email + WhatsApp number tuples.
2. **Client DB (write) — broadcast record:** Inserts a row into `broadcast_messages` with the message content, selected channels, audience parameters, and delivery status.
3. **Client DB (write) — delivery log:** Inserts one row per recipient into a delivery log table (`broadcast_message_recipients` or equivalent) recording email/WhatsApp address and delivery status (pending → sent/failed).
4. **External delivery — PHPMailer (email):** Admin PHP process calls PHPMailer for each recipient. SMTP credentials from `spa_settings`. Each email delivery updates the recipient's delivery log row.
5. **External delivery — WATI API (WhatsApp):** `includes/wati_functions.php` fires up to 12 cURL calls to the WATI REST API for template-based WhatsApp delivery. WATI access token read from `spa_settings` unencrypted.

**Community moderation flow:**

1. **Client DB (read) — post list:** SELECTs from `community_posts` ordered by `created_at` desc. No tenant filter beyond the DB connection itself (the per-tenant DB is already selected).
2. **Client DB (read) — author resolution:** Joins `community_posts.user_id` + `community_posts.account_type` to the appropriate entity table (`startups`, `investors`, `users`, etc.) to resolve the author's display name.
3. **Client DB (write) — post delete:** Direct DELETE on `community_posts` by `post_id`. No backend API call; the backend's own community-wall module reads from the same client DB, so the row disappears from the frontend immediately.
4. **Client DB (read) — comment list:** SELECTs from `community_comments` filtered by `post_id`.
5. **Client DB (read) — comment author resolution:** Same join pattern as post author resolution, keyed on `account_type . "_id"` to pick the join table. Fails for `program_office` type (see Known issues).
6. **Client DB (write) — comment delete:** Direct DELETE on `community_comments` by `comment_id`.

## Backend API calls

This flow makes no backend API calls. Broadcast delivery (email and WhatsApp) is handled entirely within the admin PHP process. Community moderation writes directly to the client DB. The backend's `community-wall` and `notifications` modules read from the same client DB, so admin-direct writes are immediately reflected in backend-served responses to frontend clients — but there is no API handshake and no event emitted to the backend on admin actions.

## Feature flags

No `tenant_users` feature flag column governs access to broadcast or community moderation. Access to broadcast is controlled by the **`canbroadCastMessage`** PHP session variable: the admin user's session must contain this key with a truthy value. This is set during login based on a role-permission check at session creation time, not evaluated dynamically per request. Community wall moderation is always visible in the admin sidebar for any authenticated admin user with sufficient role level; there is no flag gate.

## Auth & access

- Admin must have an active PHP session.
- **Broadcast:** Requires `$_SESSION['canbroadCastMessage']` to be truthy. This is a session-level permission, not a per-request role check. It is set at login time and persists for the session lifetime. A role change during an active session does not revoke broadcast access until the next login.
- **WhatsApp configuration:** Requires role level 1 (super-admin). Writing WATI credentials via `whatsapp_actions.php` is gated on the role level check within the AJAX handler.
- **Community moderation:** Requires role level 1 or 2. Post and comment deletion do not require a separate permission beyond the role level gate.

## Cross-repo impact

- **sc-saas-backend community-wall module:** The backend serves community posts and comments to the frontend PWA from the same client DB tables the admin writes directly. Admin deletion of a post or comment takes effect immediately from the frontend's perspective on the next API call. There is no soft-delete or tombstone pattern — the row is hard-deleted; if the backend caches community data (e.g., in Redis or in-memory), a deleted post may still appear on the frontend until the cache expires.
- **sc-saas-backend notifications module:** The backend's notification system may have already sent push notifications for a community post that the admin subsequently deletes. There is no retraction mechanism — users who received a push notification for a post that is later deleted will see a 404 or empty state when they tap through.
- **sc-saas-frontend:** The frontend PWA's community wall feed relies on the backend API. Deleted posts are invisible after the next API call. The service-worker cache on the PWA may serve a stale feed that includes deleted content; a hard-refresh is required to force cache invalidation.

## Known issues

1. **`program_office` account type missing from comment author resolution:** In `modules/community_wall/comments.php`, comment author names are resolved by constructing a join table name as `account_type . "_id"` (e.g., `startup_id` → join `startups` table). The `program_office` account type does not follow this naming convention and has no corresponding entity table in the join map. When a `program_office` user has posted a comment, the author name resolves to null, and the comment displays with a blank or null author name in the admin view. There is no fallback and no error — the resolution fails silently.

2. **WATI access token stored unencrypted in `spa_settings`:** The WATI API access token used for WhatsApp delivery is written to and read from the `spa_settings` table in plain text. Any admin user with direct client DB read access (via a MySQL client, a DB management tool, or any SQL injection in the admin panel itself) can extract the WATI access token and use it to send WhatsApp messages on behalf of the tenant's WATI account, access WATI contact lists, or exhaust the tenant's WATI message quota.

3. **Broadcast access persists across role changes within an active session:** The `canbroadCastMessage` session variable is set once at login and never re-evaluated during the session. If an admin user's role is downgraded (broadcast permission revoked) while they have an active session, they retain broadcast access until they log out. There is no session invalidation hook on role update.
