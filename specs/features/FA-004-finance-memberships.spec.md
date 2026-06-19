---
id: FA-004
title: Finance & Memberships
repos:
  - sc-saas-admin
  - sc-saas-backend
status: draft
contracts:
  api:
    - POST api/v1/memberships/upgrade — records a manual membership tier upgrade event in the backend
  flags: []
admin_modules:
  - sc-saas-admin/modules/finance-memberships/module.spec.md
backend_modules:
  - sc-saas-backend/src/modules/memberships/module.spec.md
  - sc-saas-backend/src/modules/payment-management/module.spec.md
updated: 2026-06-18
---

# FA-004: Finance & Memberships

## Summary

The finance and memberships flow covers the full lifecycle of membership plan configuration, manual tier upgrades, payment gateway credential management, tax settings, and invoice administration within the admin panel. Most writes in this flow go directly to the client DB via Medoo or raw PDO. One sub-flow — `memberships/settings.php` — is exceptional: it writes to the tenants DB (`$mainDatabase`) rather than the per-tenant client DB, directly modifying the tenant-level membership configuration that the backend reads at bootstrap via the tenant-verification contract. Manual tier upgrades are the only path in this flow that calls the backend API. Payment gateway validation fires a synchronous blocking cURL call to the third-party gateway API, and order number generation has a race condition under concurrent load.

## Admin entry points

**Membership plan management — `modules/memberships/`:** Admin creates, edits, and deactivates membership tiers. Each tier has a name, price, billing interval, and a configurable set of benefits (feature entitlements). Reads and writes go to the client DB `memberships` table.

**Membership settings — `modules/memberships/settings.php`:** Admin configures tenant-level membership options (e.g., whether memberships are enabled, default tier, trial period). This page writes to `$mainDatabase` (the tenants DB), not the client DB. It is one of only three admin modules with a cross-DB write. A change here updates the config that the backend reads at bootstrap from the tenant-verification endpoint.

**Manual membership upgrade — part of `modules/memberships/`:** Admin can manually set a user's membership tier (e.g., for a sponsored upgrade or a support correction). After updating the client DB, the admin calls `POST api/v1/memberships/upgrade` to record the upgrade event in the backend so the backend's membership state stays consistent with the client DB.

**Payment gateway configuration — `modules/payment_gateways/`:** Admin enters gateway credentials (Razorpay key/secret, Stripe publishable and secret keys, etc.). On save, the handler validates the credentials by making a synchronous cURL call to the gateway's API (e.g., a test charge or credential-verify endpoint). If the gateway responds slowly, this blocks the PHP process for the duration of the timeout. Credentials are written to the `spa_settings` table in the client DB.

**Tax management — `modules/tax_management/`:** Admin configures GST rates and tax-applicability rules for memberships. Written directly to the client DB. No backend API call.

**Invoice management — `modules/finance_management/`:** Admin performs invoice backfill for correcting historical data gaps. Not a routine operation; used for support and reconciliation. Direct client DB reads and writes.

## DB flow

**Membership plan create/edit:**

1. **Client DB (read):** Reads existing `memberships` rows for the list/edit view.
2. **Client DB (write):** Inserts or updates the `memberships` row with tier name, price, interval, and benefit flags.

**Membership settings (cross-DB write):**

1. **Tenants DB (write):** `memberships/settings.php` opens a connection to `$mainDatabase` (the tenants DB, whose credentials are in the admin's config) and updates the tenant's membership-configuration row. This is the only step in the flow that touches the tenants DB.
2. **No client DB write:** The settings are stored exclusively in the tenants DB; the client DB is not updated.

**Manual tier upgrade:**

1. **Client DB (read):** Reads the user's current membership row to confirm current tier.
2. **Client DB (write):** Updates `user_memberships` (or equivalent) to the new tier.
3. **Backend API call:** Calls `POST api/v1/memberships/upgrade` (see Backend API calls). On success, the upgrade is considered complete. On failure, the client DB has been updated but the backend is out of sync — there is no rollback.

**Payment gateway configuration:**

1. **External API call (synchronous, blocking):** Admin's PHP process fires a cURL call to the gateway's credential-validation endpoint. This blocks the PHP worker thread for the duration of the network round trip plus gateway processing time.
2. **Client DB (write):** On successful validation, writes gateway credentials (key/secret) to `spa_settings`. Credentials are stored in plain text.

**Order number generation (invoked at payment time, not admin-time):**

1. **Client DB (read):** `generateOrderNo()` executes `SELECT COUNT(*) FROM orders` (or `SELECT MAX(order_no)`).
2. **Client DB (write):** Inserts the new order row with `COUNT + 1` as the order number.
3. There is no uniqueness constraint on the `order_no` column and no transaction wrapping steps 1 and 2.

**Invoice backfill:**

1. **Client DB (read):** Reads orders and payment records without invoices.
2. **Client DB (write):** Inserts corrected invoice rows directly.

## Backend API calls

**POST api/v1/memberships/upgrade**

- Called from the manual tier upgrade flow after the client DB write.
- Payload: `{ userId, fromTier, toTier, reason, adminId }` (field names resolved from the admin form POST).
- What the backend does: records the upgrade event in its own membership-log table, updates any backend-side entitlement cache for the user, and may dispatch a notification to the user.
- Admin action on response: on HTTP 200/201 the admin shows a success flash. On non-200, the admin shows an error — but the client DB row has already been updated and is not rolled back. The client DB and backend are now out of sync until manually corrected.

No backend API call is made for plan creation/editing, gateway configuration, tax management, or invoice backfill.

## Feature flags

No PHP constant feature flag gates the finance or memberships admin surface. The membership plan management, gateway configuration, tax, and invoice modules are available to all authenticated admin users with sufficient role level. The backend-side `memberships` module may have its own feature gate (`memberships_enabled` or similar), but the admin panel does not check this before rendering the membership admin pages.

## Auth & access

- Admin must have an active PHP session.
- Membership plan create/edit/deactivate: role level 1 (super-admin).
- Membership settings (`memberships/settings.php`, which writes to tenants DB): role level 1 (super-admin) only. This is the highest-impact write in the finance flow because it modifies a shared config consumed by the backend bootstrap.
- Manual tier upgrade: role level 1 (super-admin) or explicit finance-manager role.
- Payment gateway configuration: role level 1 (super-admin). Gateway credentials are high-sensitivity; no role level 2 path exists.
- Tax management: role level 1 or 2.
- Invoice backfill: role level 1 (super-admin).

## Cross-repo impact

- **sc-saas-backend bootstrap / tenant-verification contract:** `memberships/settings.php` writes directly to the tenants DB. The backend reads tenant-level config (including membership settings) from the tenants API at bootstrap (`verify_tenant` / `tenant-settings` shape). A change written by the admin to the tenants DB takes effect on the next backend process restart or re-bootstrap. An in-flight backend process that has already bootstrapped will not see the change until it restarts. This means there is a window of inconsistency between what the admin has configured and what the backend enforces.
- **sc-saas-frontend membership display:** The frontend reads membership entitlements and tier info via the backend. If the admin manually upgrades a user's tier in the client DB but the backend API call (`/memberships/upgrade`) fails, the frontend will continue to show the old tier until the backend's state is corrected. The frontend does not read from the client DB directly.
- **sc-saas-frontend payment flow:** If the admin changes gateway credentials in `spa_settings`, the frontend's payment integration (which ultimately routes through the backend to the gateway) uses the new credentials on the backend's next cache refresh. A misconfigured credential (e.g., a test key deployed to production) will cause all frontend payment attempts to fail with a gateway error until the admin corrects and re-saves the credentials.

## Known issues

1. **Payment gateway credential validation blocks PHP worker synchronously:** When the admin saves gateway credentials in `modules/payment_gateways/`, the handler fires a blocking cURL call to the third-party gateway API before writing to the DB. If the gateway is slow, under maintenance, or the admin's server has restricted outbound connectivity, this cURL call blocks the PHP-FPM worker for the full socket timeout (default 60 seconds or the configured `default_socket_timeout`). During this time the worker is unavailable for other requests. Under concurrent admin activity this can exhaust the PHP-FPM worker pool and deadlock the admin panel for all users.

2. **`generateOrderNo()` race condition produces duplicate order numbers:** Order number generation uses `COUNT(*) + 1` (or `MAX(order_no) + 1`) in a non-atomic read-then-write pattern with no DB-level uniqueness constraint on the `orders.order_no` column and no wrapping transaction. Two membership purchases processed concurrently — whether by two users simultaneously or by a retry of a failed request — can both read the same count, both compute the same next order number, and both insert rows with the same `order_no`. Duplicate order numbers break invoice reconciliation, payment gateway webhook matching, and any downstream report that uses `order_no` as a unique identifier.

3. **Silent data loss on tenants DB connection failure in `memberships/settings.php`:** The write to `$mainDatabase` in `memberships/settings.php` is not wrapped in a transaction and has no explicit error-handling path that surfaces a failure to the admin user. If the tenants DB connection drops mid-request (network blip, connection pool exhaustion), the `INSERT`/`UPDATE` is lost silently. The admin sees no error feedback and believes the settings have been saved. The tenants DB retains the previous configuration, which the backend continues to use at its next bootstrap. The admin must manually verify the change took effect by re-opening the settings page.

4. **Gateway credentials stored in plain text in `spa_settings`:** Razorpay and Stripe secret keys are written to and read from `spa_settings` without encryption. Any user with client DB read access can extract live payment credentials. This is the same exposure pattern as the WATI token in FA-003, but the impact is higher because compromised payment gateway credentials can be used to initiate or capture real charges.
