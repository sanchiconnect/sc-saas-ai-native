# Parity Check Report
**Sprint:** CS-CHAT-S07  
**Generated:** 2025-09-05 15:10  
**Run Mode:** Diff Mode  
**Config Files Used:**
- Staging: `artifacts/release/env-config-staging.yaml`
- Production: `artifacts/release/env-config-production.yaml`

---

## ❌ CRITICAL DRIFT DETECTED

**Critical Drift Items:** 2 — **Gate 3 BLOCKED**  
**Notable Drift Items:** 3 — require POD Lead acknowledgement  
**Expected Differences:** 4 — documented and accepted  
**Total Config Dimensions Checked:** 32

---

## ❌ Critical Drift — Deploy Blockers

| # | Dimension | Config Key | Staging Value | Production Value | Rule | Resolution Required |
|---|-----------|-----------|--------------|-----------------|------|---------------------|
| 1 | Feature Flags | `notifications_v2` | `true` | `false` | B3 — In-sprint feature flag OFF in production | Enable `notifications_v2` flag in production feature flag service before deployment window |
| 2 | Database | `latest_migration_id` | `0045` | `0044` | B4 — Staging migration ahead of production | Apply migration 0045 to production database before deployment. Verify rollback script is tested. |

**⛔ Gate 3 cannot proceed until both critical drift items are resolved.**

---

## ⚠️ Notable Drift — POD Lead Acknowledgement Required

| # | Dimension | Config Key | Staging Value | Production Value | Risk | POD Lead Acknowledged? |
|---|-----------|-----------|--------------|-----------------|------|----------------------|
| 1 | Database | `connection_pool_max` | `20` | `5` | Notification preferences API may queue under production load that staging absorbed. Recommend smoke test under moderate load (>10 concurrent users). | ⬜ Pending |
| 2 | Monitoring | `log_level` | `DEBUG` | `INFO` | Staging debug logs may have masked errors that were silently swallowed. INFO level in production means some diagnostic data will not appear. | ⬜ Pending |
| 3 | Monitoring | `apm_agent` | `datadog` (v5.2.1) | `newrelic` (v11.0.0) | Different APM agents means staging and production observability dashboards differ. Post-deploy monitoring must use New Relic, not Datadog. Alert POD Lead and on-call engineer. | ⬜ Pending |

---

## ℹ️ Expected Differences — Documented & Accepted

| # | Dimension | Config Key | Staging Value | Production Value | Rationale |
|---|-----------|-----------|--------------|-----------------|-----------|
| 1 | Database | `read_replicas` | `0` | `2` | Cost-appropriate staging design. Read replica behavior (replication lag) not tested in staging — add to smoke test checklist: verify read API responses after write under production replica lag. |
| 2 | Network | `cors_origins` | Includes `localhost:3000`, `localhost:5173` | `app.myapp.com` only | Local dev origins correct for staging; must not be present in production (confirmed absent). |
| 3 | Network | `waf_enabled` | `false` | `true` | WAF disabled in staging to avoid blocking test traffic. Production WAF rules may block request patterns not tested in staging — note for smoke test. |
| 4 | Feature Flags | `debug_panel` | `true` | `false` | Debug panel correctly disabled in production. |

---

## Full Configuration Diff

<details>
<summary>Expand — all 32 config fields compared</summary>

| Dimension | Config Key | Staging | Production | Classification |
|-----------|-----------|---------|-----------|----------------|
| runtime | orchestration | kubernetes-1.28 | kubernetes-1.28 | ✅ Match |
| runtime | base_image | node:20.11.0-alpine | node:20.11.0-alpine | ✅ Match |
| runtime | cpu | 2vCPU | 2vCPU | ✅ Match |
| runtime | memory | 4GB | 4GB | ✅ Match |
| runtime | region | us-east-1 | us-east-1 | ✅ Match |
| runtime | autoscaling.min_replicas | 1 | 2 | ℹ️ EXPECTED_DIFF |
| runtime | autoscaling.max_replicas | 3 | 10 | ℹ️ EXPECTED_DIFF |
| application | runtime_version | 20.11.0 | 20.11.0 | ✅ Match |
| application | lockfile_hash | sha256:a3f9c821... | sha256:a3f9c821... | ✅ Match |
| application | build_image | myapp-build:2025-09-04-sha-abc123 | myapp-build:2025-09-04-sha-abc123 | ✅ Match |
| database | engine | postgresql | postgresql | ✅ Match |
| database | version | 16.1 | 16.1 | ✅ Match |
| database | latest_migration_id | 0045 | 0044 | ❌ CRITICAL_DRIFT |
| database | read_replicas | 0 | 2 | ℹ️ EXPECTED_DIFF |
| database | connection_pool_min | 2 | 5 | ⚠️ NOTABLE_DRIFT |
| database | connection_pool_max | 20 | 5 | ⚠️ NOTABLE_DRIFT |
| database | cache.engine | redis | redis | ✅ Match |
| database | cache.version | 7.2.3 | 7.2.3 | ✅ Match |
| external | Mailgun.sdk_version | 5.0.1 | 5.0.1 | ✅ Match |
| external | Mailgun.endpoint_type | sandbox | live | ℹ️ EXPECTED_DIFF |
| external | Firebase FCM.sdk_version | 12.3.0 | 12.3.0 | ✅ Match |
| external | Firebase FCM.endpoint_type | sandbox | live | ℹ️ EXPECTED_DIFF |
| external | Auth0.sdk_version | 4.1.0 | 4.1.0 | ✅ Match |
| feature_flags | notifications_v2 | true | false | ❌ CRITICAL_DRIFT |
| feature_flags | legacy_auth | false | false | ✅ Match |
| feature_flags | payments_v3 | false | false | ✅ Match |
| feature_flags | debug_panel | true | false | ℹ️ EXPECTED_DIFF |
| monitoring | log_level | DEBUG | INFO | ⚠️ NOTABLE_DRIFT |
| monitoring | apm_agent | datadog | newrelic | ⚠️ NOTABLE_DRIFT |
| monitoring | health_check_path | /health | /health | ✅ Match |
| network | cors_origins | localhost included | app.myapp.com only | ℹ️ EXPECTED_DIFF |
| network | waf_enabled | false | true | ℹ️ EXPECTED_DIFF |

</details>

---

## Gate 3 Parity Attestation

This report was generated by ParityChecker (SpecPod v2.1.0) on 2025-09-05 15:10.

**ParityChecker certifies:**
- [x] All config dimensions diffed against structured YAML source files
- [x] Each difference classified per classification-rules.md
- [x] Critical drift count confirmed: 2
- [x] Parity verdict issued

**Critical drift resolution required before Gate 3:**
1. `notifications_v2` feature flag — enable in production feature flag service
2. Migration `0045` — apply to production database; verify rollback script ready

**POD Lead action required:**
- [ ] Resolve Critical Drift #1: enable `notifications_v2` in production
- [ ] Resolve Critical Drift #2: apply migration 0045 to production
- [ ] Acknowledge Notable Drift #1 (connection pool)
- [ ] Acknowledge Notable Drift #2 (log level)
- [ ] Acknowledge Notable Drift #3 (APM agent — alert on-call engineer)
- [ ] Re-run ParityChecker after resolutions to confirm zero critical drift
- [ ] Confirm: ✅ PARITY VERIFIED | ❌ DRIFT UNRESOLVED
- [ ] Sign: _________________________ Date: _____________

> ⚠️ ParityChecker compares declared configuration only. Undocumented manual changes applied directly to production infrastructure are not visible to this agent. POD Lead attestation confirms they are unaware of any such changes.
