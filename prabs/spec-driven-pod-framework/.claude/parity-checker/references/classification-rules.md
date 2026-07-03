# ParityChecker — Classification Rules Reference

**Version:** 2.1.0  
**Used by:** ParityChecker Step 3

---

## Canonical Classification Decision Tree

Apply rules top-to-bottom. First match wins.

```
1. Does this difference involve a secret value being ABSENT in production?
   → CRITICAL_DRIFT (B1)

2. Does this difference involve a production environment pointing at a sandbox/test endpoint?
   → CRITICAL_DRIFT (B2)

3. Does this difference involve a feature flag that is ON for a feature in the current sprint scope,
   but the flag is OFF in production?
   → CRITICAL_DRIFT (B3)

4. Does this difference involve a migration ID where staging is ahead of production?
   → CRITICAL_DRIFT (B4) — production has not received a migration that staging tests assume

5. Does this difference involve a runtime version mismatch?
   → CRITICAL_DRIFT (B5)

6. Does this difference involve a dependency lockfile hash mismatch?
   → CRITICAL_DRIFT (B6)

7. Does this difference involve a CORS origin that includes localhost, *.local, or *.test in production?
   → CRITICAL_DRIFT (B7)

8. Does this difference involve a TLS certificate expiring within 7 days?
   → CRITICAL_DRIFT (B8)

9. Could this difference plausibly cause a test to PASS in staging but FAIL in production?
   → If YES: CRITICAL_DRIFT (B9 — judgment call; document rationale)
   → If NO: continue to NOTABLE rules

10. Is this difference intentional and documented in decision-ledger.md or spec.md?
    → EXPECTED_DIFF (E-confirmed)

11. Is this difference clearly by design (sandbox vs. live, debug logging, smaller instance size)?
    → EXPECTED_DIFF (E-by-design) — document rationale

12. Does this difference represent a potential risk worth monitoring post-deploy?
    → NOTABLE_DRIFT

13. None of the above match.
    → NOTABLE_DRIFT (conservative default — never silently ignore a difference)
```

---

## Critical Drift Examples by Dimension

### Runtime & Infrastructure

| Scenario | Classification | Rationale |
|----------|---------------|-----------|
| Node.js 20.11.0 in staging vs 20.8.1 in production | `CRITICAL_DRIFT` | Patch version differences can affect crypto, TLS, or npm package behavior |
| Python 3.12 in staging vs 3.11 in production | `CRITICAL_DRIFT` | Minor version differences can break type hints, match statements |
| 2 vCPU staging vs 1 vCPU production | `NOTABLE_DRIFT` | Load test results from staging may not reflect production behavior |
| us-east-1 staging vs eu-west-1 production | `NOTABLE_DRIFT` | Latency characteristics differ; GDPR implications if data crosses regions |
| ECS staging vs Kubernetes production | `CRITICAL_DRIFT` | Networking, secrets injection, health check behavior fundamentally different |

### Application Dependencies

| Scenario | Classification | Rationale |
|----------|---------------|-----------|
| `package-lock.json` hash differs | `CRITICAL_DRIFT` | Undeclared transitive dependency version change; source of "works on my machine" failures |
| Explicit library version pinned differently (e.g., express@4.18.2 vs 4.18.0) | `CRITICAL_DRIFT` | Bug fixes or breaking changes between patch versions |
| Build image sha256 differs | `CRITICAL_DRIFT` | Container layers may include different system library versions |

### Database & Data Services

| Scenario | Classification | Rationale |
|----------|---------------|-----------|
| Staging migration ID: 0045; Production: 0044 | `CRITICAL_DRIFT` | Production missing migration that staging tests rely on |
| Production migration ID: 0045; Staging: 0044 | `NOTABLE_DRIFT` | Production has an applied hotfix staging lacks; document and monitor |
| PostgreSQL 15 staging vs PostgreSQL 16 production | `CRITICAL_DRIFT` | Query planner, function behavior, extension API may differ |
| Redis 7.0 staging vs Redis 6.2 production | `CRITICAL_DRIFT` | Command compatibility and TTL behavior differ |
| Connection pool max: 20 staging vs 5 production | `NOTABLE_DRIFT` | Production may queue/reject connections under load that staging absorbed |
| No read replica in staging vs 2 replicas in production | `EXPECTED_DIFF` | Cost-appropriate staging design; note replication lag won't be tested |

### External Services

| Scenario | Classification | Rationale |
|----------|---------------|-----------|
| Mailgun sandbox endpoint in production | `CRITICAL_DRIFT` | Emails will not be delivered |
| Stripe test keys in production | `CRITICAL_DRIFT` | Payments will silently fail |
| Firebase project ID: `myapp-staging` in production config | `CRITICAL_DRIFT` | Push notifications routed to wrong project |
| Auth0 SDK 4.1.0 staging vs 4.0.2 production | `NOTABLE_DRIFT` | Verify no breaking change in minor version |
| Third-party API v2 staging vs v1 production | `CRITICAL_DRIFT` | Response schema may differ; app built against v2 contracts |

### Feature Flags

| Scenario | Classification | Rationale |
|----------|---------------|-----------|
| `notifications_v2: true` staging, `false` production (in-sprint feature) | `CRITICAL_DRIFT` | New code will never execute in production; deployment is pointless |
| `legacy_auth: false` staging, `true` production (out-of-sprint feature) | `EXPECTED_DIFF` | Intentional; production not yet migrated |
| `debug_panel: true` staging, `false` production | `EXPECTED_DIFF` | Correct — debug panel should be off in production |
| `payments_v3: true` staging, `false` production (in-sprint feature) | `CRITICAL_DRIFT` | In-sprint feature gated off in production |

### Environment Variables

| Scenario | Classification | Rationale |
|----------|---------------|-----------|
| `MAILGUN_API_KEY` present staging, absent production | `CRITICAL_DRIFT` | Runtime exception on first email send |
| `DEBUG_TOOLBAR_ENABLED` present staging, absent production | `EXPECTED_DIFF` | Debug tooling correctly excluded from production |
| `DATABASE_READ_REPLICA_URL` absent staging, present production | `NOTABLE_DRIFT` | App can run without it; document that read replica not tested in staging |
| `NEW_RELIC_LICENSE_KEY` absent staging, present production | `EXPECTED_DIFF` | APM only in production is common; note in report |

### Network & Security

| Scenario | Classification | Rationale |
|----------|---------------|-----------|
| CORS: `http://localhost:3000` in production allowed origins | `CRITICAL_DRIFT` | Security vulnerability; browser will allow cross-origin requests from any local dev machine |
| TLS cert expiring in 3 days | `CRITICAL_DRIFT` | Post-deploy cert expiry will cause outage |
| WAF disabled in staging, enabled in production | `NOTABLE_DRIFT` | Production traffic may be blocked in ways staging tests didn't cover; note for smoke test |
| Different rate limit thresholds | `NOTABLE_DRIFT` | Load test results may not reflect production behavior |

---

## Edge Cases

### When staging is MORE restrictive than production
Example: staging has a lower rate limit than production.  
Classification: `NOTABLE_DRIFT` (staging tests pass at lower threshold; production may behave differently but tests won't fail because of this). Document and note in smoke test checklist.

### When a difference is in a component NOT in the current sprint scope
Reduce severity by one level. A CRITICAL_DRIFT in an out-of-scope component becomes NOTABLE_DRIFT — it's pre-existing and should be tracked but does not block this sprint's deployment. Flag it for remediation in the next sprint.

### When the POD Lead asserts a difference is intentional
Reclassify to `EXPECTED_DIFF` only if:
1. The rationale is provided and documented in the report.
2. The difference cannot plausibly cause a staging-pass / production-fail scenario.
If both conditions are met, record: `EXPECTED_DIFF (POD Lead asserted: {rationale})`.

### When config files are partially complete
If a field is `null` or missing in one config but present in the other:
- Treat as `CRITICAL_DRIFT` — absence of a value is a meaningful difference.
- Prompt POD Lead to confirm whether the field is intentionally absent.
