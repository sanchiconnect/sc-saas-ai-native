# Rollback Plan
**Sprint:** CS-CHAT-S07  
**Generated:** 2025-09-05 17:15  
**Composite RTO Target:** 25 minutes (parallel execution) from trigger detection to service restoration  
**Status:** FINAL

---

## Rollback Overview

| Component | Rollback Method | Individual RTO | Data Recovery Needed? |
|-----------|----------------|---------------|-----------------------|
| NotifUI | Feature flag disable (`notifications_v2` → 0%) | <1 min | No |
| NotifAPI | Container redeploy (previous tag) | 5 min | No |
| EmailSvc | Webhook deregistration + image revert | 10 min | No |
| PushSvc | Config flag disable + image revert | 5 min | No |
| AuthGate | Image revert (middleware is additive; low risk) | 5 min | No |
| NotifDB | Migration reversal script (0045 → 0044) | 20 min | No — migration is additive; reversal drops added rows, no user data loss |
| **Composite** | NotifUI + API/Services parallel; DB last | **25 min** | No |

---

## NotifUI — Rollback Procedure

**Trigger conditions:**
- Smoke test item #4 or #5 fails (page does not render or state does not persist)
- Any JavaScript critical error from NotifUI pods logged in New Relic for >2 continuous minutes

**Rollback method:** Feature flag disable  
**RTO target:** <1 minute  
**Data recovery required:** No

### Steps:
1. In production feature flag service, set `notifications_v2` to `0%` (disabled for all users)
2. Confirm flag state reflects 0% in flag service dashboard (allow up to 30s propagation)
3. Verify `/settings/notifications` route is no longer accessible or redirects to prior state
4. Log rollback action in Slack `#deployments`: `[ROLLBACK] notifications_v2 flag disabled. Time: HH:MM`

**Rollback verified when:** `notifications_v2` flag shows 0% in flag service; `/settings/notifications` returns pre-sprint behaviour.

---

## NotifAPI — Rollback Procedure

**Trigger conditions:**
- 5xx error rate >2% above baseline for >2 continuous minutes on NotifAPI pods
- Any smoke test item #1 or #2 fails
- Health check on any NotifAPI pod failing for >1 continuous minute

**Rollback method:** Container redeploy to previous image tag  
**RTO target:** 5 minutes  
**Data recovery required:** No

### Steps:
1. (If not already done) Disable `notifications_v2` flag immediately (see NotifUI rollback Step 1)
2. Identify previous image tag:
   ```bash
   kubectl get deployment notif-api -n production -o jsonpath='{.spec.template.spec.containers[0].image}'
   # Should be myapp/notif-api:pre-s07 (kept available per rollback window policy)
   ```
3. Revert to previous image:
   ```bash
   kubectl set image deployment/notif-api notif-api=myapp/notif-api:pre-s07 -n production
   ```
4. Watch rollout complete:
   ```bash
   kubectl rollout status deployment/notif-api -n production --timeout=3m
   ```
5. Verify health check passes on all pods:
   ```bash
   kubectl get pods -n production -l app=notif-api | grep Running
   curl -sf https://app.myapp.com/api/v1/health | jq .status
   ```
6. Confirm error rate returns to baseline in New Relic (allow 2 minutes normalisation)
7. Log in Slack `#deployments`: `[ROLLBACK] NotifAPI reverted to pre-s07. Time: HH:MM`

**Rollback verified when:** All NotifAPI pods show Running; /health returns 200; 5xx error rate at baseline.

---

## EmailSvc — Rollback Procedure

**Trigger conditions:**
- Webhook processing failure rate >10% over 5 consecutive minutes
- Smoke test item #6 fails
- Mailgun webhook delivering to wrong endpoint (verify in Mailgun dashboard)

**Rollback method:** Deregister Mailgun webhook + revert EmailSvc image  
**RTO target:** 10 minutes  
**Data recovery required:** No — opt-outs processed during the failure window will need manual reprocessing. Log affected event IDs from Mailgun webhook history (available 7 days).

### Steps:
1. Deregister the Mailgun webhook in the Mailgun dashboard (Settings → Webhooks → Unsubscribe)
   - URL: `https://app.myapp.com/api/v1/webhooks/mailgun/unsubscribe`
   - Action: Delete webhook registration
2. Revert EmailSvc image:
   ```bash
   kubectl set image deployment/email-svc email-svc=myapp/email-svc:pre-s07 -n production
   kubectl rollout status deployment/email-svc -n production --timeout=3m
   ```
3. Re-register previous Mailgun webhook URL (from prior sprint config):
   ```bash
   # Check prior webhook URL in secrets manager: /production/mailgun/webhook_url_pre_s07
   ```
4. Verify health check passes
5. Log affected unsubscribe events from Mailgun for manual reprocessing if needed
6. Log in Slack: `[ROLLBACK] EmailSvc reverted to pre-s07. Mailgun webhook re-registered. Time: HH:MM`

**Rollback verified when:** Mailgun dashboard shows previous webhook URL active; EmailSvc health check passes; no new 5xx errors.

---

## PushSvc — Rollback Procedure

**Trigger conditions:**
- FCM API error rate >15% of cleanup calls over 5 minutes
- Smoke test item #7 fails

**Rollback method:** Disable cleanup job via config flag + image revert  
**RTO target:** 5 minutes  
**Data recovery required:** No — FCM tokens not cleaned up during rollback window remain until next cleanup job run.

### Steps:
1. Disable FCM token cleanup job via config:
   ```bash
   kubectl set env deployment/push-svc FCM_CLEANUP_ENABLED=false -n production
   ```
2. Revert PushSvc image:
   ```bash
   kubectl set image deployment/push-svc push-svc=myapp/push-svc:pre-s07 -n production
   kubectl rollout status deployment/push-svc -n production --timeout=3m
   ```
3. Re-enable cleanup job (with previous logic):
   ```bash
   kubectl set env deployment/push-svc FCM_CLEANUP_ENABLED=true -n production
   ```
4. Verify health check passes
5. Log in Slack: `[ROLLBACK] PushSvc reverted to pre-s07. Time: HH:MM`

**Rollback verified when:** PushSvc health check passes; FCM error rate returns to baseline.

---

## AuthGate — Rollback Procedure

**Trigger conditions:**
- Smoke test item #8 fails (unauthenticated request returns 200 instead of 401)
- Authenticated requests unexpectedly receiving 401 (middleware over-blocking)

**Rollback method:** Image revert  
**RTO target:** 5 minutes  
**Data recovery required:** No

### Steps:
1. Revert AuthGate middleware:
   ```bash
   kubectl set image deployment/auth-gate auth-gate=myapp/auth-gate:pre-s07 -n production
   kubectl rollout status deployment/auth-gate -n production --timeout=3m
   ```
2. Verify test request:
   ```bash
   curl -X GET https://app.myapp.com/api/v1/notifications/preferences   # No auth — expect 401
   curl -X GET https://app.myapp.com/api/v1/notifications/preferences \
     -H "Authorization: Bearer $TEST_TOKEN"   # Authed — expect 200
   ```
3. Log in Slack: `[ROLLBACK] AuthGate reverted to pre-s07. Time: HH:MM`

**Rollback verified when:** Unauthenticated requests return 401; authenticated requests return 200.

---

## NotifDB — Rollback Procedure

**⚠️ Execute LAST — only after all API/service pods are on previous image tags.**

**Trigger conditions:**
- Smoke test item #3 fails (row count incorrect)
- Phase 0 validation fails (migration 0045 does not complete within 10 minutes)
- Any DB connection threshold breach that does not recover after API rollbacks

**Rollback method:** Migration reversal script  
**RTO target:** 20 minutes  
**Data recovery required:** No — migration 0045 added default rows; reversal deletes them. No user-authored data is affected.

### Pre-condition check:
```
Before executing DB rollback, confirm:
  □ NotifAPI is on pre-s07 image (no pods writing to notifications preferences table)
  □ EmailSvc is on pre-s07 image
  □ notifications_v2 feature flag is at 0%
```

### Steps:
1. Confirm no application pods are writing to `user_notification_preferences` table:
   ```bash
   # Check active connections to notifications tables
   psql $PRODUCTION_DB_URL -c "SELECT count(*) FROM pg_stat_activity WHERE query LIKE '%user_notification_preferences%';"
   # Expected: 0 or very low (monitoring queries only)
   ```
2. Take a point-in-time snapshot before reversal (belt-and-suspenders):
   ```bash
   # AWS RDS: create manual snapshot before proceeding
   aws rds create-db-snapshot --db-instance-identifier production-db --db-snapshot-identifier pre-rollback-s07-$(date +%Y%m%d%H%M)
   ```
3. Execute rollback script:
   ```bash
   psql $PRODUCTION_DB_URL -f scripts/rollback_migration_0045.sql
   ```
4. Verify migration_id reverted:
   ```bash
   psql $PRODUCTION_DB_URL -c "SELECT id FROM schema_migrations ORDER BY id DESC LIMIT 1;"
   # Expected: 0044
   ```
5. Verify `user_notification_preferences` table is absent or empty:
   ```bash
   psql $PRODUCTION_DB_URL -c "\d user_notification_preferences" 2>&1 | grep "Did not find"
   # Expected: "Did not find any relation named user_notification_preferences"
   ```
6. Confirm all API health checks still passing post-DB rollback
7. Log in Slack: `[ROLLBACK] NotifDB migration 0045 reversed. Migration ID: 0044. Time: HH:MM`

**Rollback verified when:** `schema_migrations` latest ID = 0044; `user_notification_preferences` table absent; all API health checks passing.

---

## Cross-Component Rollback Execution Order

If ALL components require simultaneous rollback (worst-case):

| Order | Component | Can run parallel with | Must complete before |
|-------|-----------|----------------------|---------------------|
| 1 (immediate) | NotifUI | NotifAPI, EmailSvc, PushSvc, AuthGate | Nothing |
| 1 (immediate) | NotifAPI | NotifUI, EmailSvc, PushSvc, AuthGate | NotifDB rollback |
| 1 (immediate) | EmailSvc | NotifUI, NotifAPI, PushSvc | NotifDB rollback |
| 1 (immediate) | PushSvc | NotifUI, NotifAPI, EmailSvc | NotifDB rollback |
| 1 (immediate) | AuthGate | NotifUI, NotifAPI, EmailSvc, PushSvc | NotifDB rollback |
| 2 (after all above) | NotifDB | — | Must be last |

**Estimated composite rollback time (parallel):** 25 minutes  
(Dominated by DB rollback + RDS snapshot at 20 min)

---

## Post-Rollback Verification Checklist

Run after all components rolled back:

| # | Check | Expected Result |
|---|-------|----------------|
| 1 | `GET /v1/notifications/preferences` | 404 Not Found or pre-sprint behavior |
| 2 | `/settings/notifications` URL | Pre-sprint behavior (redirect or 404) |
| 3 | `schema_migrations` latest ID | `0044` |
| 4 | New Relic error rate | Returned to pre-deployment baseline |
| 5 | New Relic p95 latency | Returned to pre-deployment baseline |
| 6 | Feature flag `notifications_v2` | 0% in flag service |

**Escalation if rollback fails or RTO exceeded:**  
Contact: POD Lead (Alex M.) within 5 minutes of RTO breach.  
If DB rollback fails: engage DBA / AWS Support immediately; do not attempt manual SQL intervention.
