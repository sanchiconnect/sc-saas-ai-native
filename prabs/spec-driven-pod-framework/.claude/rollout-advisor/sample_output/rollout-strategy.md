# Rollout Strategy
**Sprint:** CS-CHAT-S07  
**Generated:** 2025-09-05 17:15  
**Status:** FINAL  
**Based on:**
- ReleaseIntel verdict: ✅ READY TO DEPLOY (0 P0 blockers; 1 P1 accepted)
- ParityChecker verdict: ✅ ENVIRONMENTS ALIGNED (0 critical drift after resolutions)
- Composite Risk Tier: **MEDIUM** (1 HIGH blast-radius component: NotifDB; 1 P1 risk accepted; 3 notable drift items acknowledged)

---

## Recommended Rollout Method: Feature-Flag Ramp (10% → 50% → 100%)

**Rationale:** NotifDB carries HIGH blast radius due to a user-wide backfill migration affecting 100% of user records. The migration rollback has not been load-tested at production scale, making the P1 risk real. A feature-flag ramp limits initial exposure to 10% of users, providing a monitoring window before the migration's production behavior is fully validated under load. Infrastructure supports feature flags (`notifications_v2` is ready to enable per ParityChecker resolution).

**Deployment Window:** Monday 10:00–12:00 AM local time  
**On-Call Required:** Yes — Platform Engineer available until 14:00  
**Rollback Window:** Keep previous container image tagged `myapp/notif-api:pre-s07` available for 48 hours post-deployment. Database rollback script remains staged at `scripts/rollback_migration_0045.sql`.

---

## Rollout Phases

| Phase | Traffic % | Hold Period | Progression Trigger | Halt Trigger |
|-------|-----------|------------|--------------------|--------------|
| 0 — Pre-deploy | — | — | Apply migration 0045; verify row count; enable `notifications_v2` at 0% | Migration fails or row count incorrect → abort |
| 1 — Canary | 10% | 30 minutes | Error rate <2% above baseline; p95 latency within 20%; all health checks passing; DB connection errors <5/min | Any rollback threshold breached → Phase 1 halt |
| 2 — Expand | 50% | 30 minutes | Same as Phase 1 | Same as Phase 1 |
| 3 — Full | 100% | 15 min monitoring hold | No new errors; smoke test complete; NR transactions nominal | Same as Phase 1 |

**Phase 0 is blocking.** If migration 0045 fails or row count is incorrect, do not proceed to Phase 1 and execute database rollback immediately.

---

## Deployment Sequence

| Step | Phase | Action | Expected Duration | Verification |
|------|-------|--------|-----------------|--------------|
| 1 | 0 | Apply migration 0045 to production DB | 5 min | `SELECT count(*) FROM user_notification_preferences` = total user count |
| 2 | 0 | Deploy NotifAPI pods (rolling update) | 3 min | `kubectl rollout status deployment/notif-api -n production` |
| 3 | 0 | Deploy NotifUI pods (rolling update) | 3 min | `kubectl rollout status deployment/notif-ui -n production` |
| 4 | 0 | Deploy EmailSvc (rolling update) | 2 min | Health check /health on all pods |
| 5 | 0 | Deploy PushSvc (rolling update) | 2 min | Health check /health on all pods |
| 6 | 0 | Deploy AuthGate middleware (rolling update) | 2 min | Test unauthenticated request → 401 |
| 7 | 1 | Enable `notifications_v2` flag at 10% | 1 min | Confirm flag state in flag service dashboard |
| 8 | 1 | Monitor for 30 minutes | 30 min | Watch NR error rate; p95 latency; DB connection pool |
| 9 | 2 | Ramp `notifications_v2` to 50% | 1 min | Confirm flag state |
| 10 | 2 | Monitor for 30 minutes | 30 min | Same metrics as Phase 1 |
| 11 | 3 | Ramp `notifications_v2` to 100% | 1 min | Confirm flag state |
| 12 | 3 | Run smoke test checklist | 23 min | All 8 items pass |
| 13 | 3 | Declare deployment complete | — | Notify POD Lead; close Gate 3 |

**Total deployment window:** ~1 hour 45 minutes

---

## Rollout Trigger Thresholds

### Progression Gates (ALL conditions must hold for full hold period)
- 5xx error rate: within 2% of pre-deployment baseline
- p95 response time: within 20% of pre-deployment baseline
- All pod health checks: passing continuously
- No CRITICAL-severity log events from NotifAPI, NotifDB, EmailSvc, PushSvc

### Rollback Triggers (initiate rollback IMMEDIATELY if ANY condition met)

| Component | Metric | Threshold | Response |
|-----------|--------|-----------|----------|
| NotifAPI | 5xx error rate | >2% above baseline for >2 min | Halt canary; initiate NotifAPI rollback |
| NotifDB | DB connection errors | >5 errors/min | Halt all phases; initiate DB rollback sequence |
| NotifDB | Query latency p95 | >200% of baseline for >3 min | Halt canary; assess DB load; initiate rollback if not recovering |
| EmailSvc | Webhook processing failure | >10% of events failing over 5 min | Disable Mailgun webhook; initiate EmailSvc rollback |
| PushSvc | FCM API errors | >15% of cleanup calls failing | Disable cleanup job via config flag |
| All | Pod health check failure | Any pod failing for >1 continuous min | Halt; initiate rollback for that component |
| All | Smoke test failure | Any smoke test item fails (Phase 3 only) | Execute full rollback |

---

## Monday Smoke Test Checklist

**Run by:** On-call engineer  
**Time window:** First 30 minutes of Phase 3 (after flag at 100%)  
**Total estimated time:** 23 minutes

| # | Component | Test Action | Expected Outcome | Pass/Fail | Time (min) |
|---|-----------|------------|-----------------|-----------|-----------|
| 1 | NotifAPI | `GET /v1/notifications/preferences` as test user (bearer token) | 200 OK; JSON body with email/sms/push fields and boolean values | | 2 |
| 2 | NotifAPI | `POST /v1/notifications/preferences` `{email: false}`; then GET again | 200 OK on POST; GET returns `email: false` | | 3 |
| 3 | NotifDB | `SELECT count(*) FROM user_notification_preferences` in production DB | Row count equals total active user count (from baseline query taken in Step 1) | | 2 |
| 4 | NotifUI | Load `https://app.myapp.com/settings/notifications` in Chrome | Page renders within 3s; all toggles visible; keyboard navigation functional (Tab key) | | 3 |
| 5 | NotifUI | Toggle Email notifications off; reload page | Toggle state persists after reload | | 2 |
| 6 | EmailSvc | Replay test Mailgun webhook event from staging (`scripts/test_mailgun_replay.sh`) | Opt-out status updated in DB within 30s; no 5xx in logs | | 5 |
| 7 | PushSvc | Run `scripts/test_fcm_optout.sh` with test user ID | FCM token absent from Firebase console for test user | | 5 |
| 8 | AuthGate | `curl -X GET https://app.myapp.com/api/v1/notifications/preferences` (no auth header) | 401 Unauthorized | | 1 |
| **Total** | | | | | **23 min** |

**Smoke test pass criteria:** All 8 items pass. No item may be skipped.  
**If any item fails:** Execute rollback plan immediately. Do not attempt to debug in production.

---

## Gate 3 Recommendation

**RolloutAdvisor recommends:** ✅ PROCEED TO DEPLOY — subject to Gate 3 pre-conditions below.

**Conditions for deployment to proceed (all must be checked before Monday):**
- [x] ReleaseIntel: READY TO DEPLOY (0 P0 blockers; P1 accepted by POD Lead)
- [x] ParityChecker: ENVIRONMENTS ALIGNED (critical drifts resolved)
- [ ] Rollout strategy reviewed and approved by POD Lead
- [ ] Rollback plan reviewed; `scripts/rollback_migration_0045.sql` confirmed staged in production
- [ ] On-call engineer briefed on smoke test checklist and rollback triggers
- [ ] `notifications_v2` flag confirmed at 0% (not enabled) in production flag service pre-deployment

**POD Lead Go/No-Go:**
- [ ] ✅ GO — Deployment approved per this strategy
- [ ] ❌ NO-GO — Reason: _______________________
- Signed: _________________________ Date: _____________

> ⚠️ The Go/No-Go deployment decision belongs to the POD Lead. RolloutAdvisor provides an evidence-based recommendation; it does not authorise deployment. No agent may be delegated Go/No-Go authority.
