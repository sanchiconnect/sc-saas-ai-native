# RolloutAdvisor — Output Schema

**Files produced:**
- `artifacts/release/rollout-strategy.md`
- `artifacts/release/rollback-plan.md`

**Version:** 2.1.0

---

## rollout-strategy.md — Required Sections

### 1. Report Header

```markdown
# Rollout Strategy
**Sprint:** {sprint_id}
**Generated:** {date} {time}
**Status:** FINAL | ⚠️ DRAFT — pending blocker resolution
**Based on:**
  - ReleaseIntel verdict: READY TO DEPLOY | NOT READY (⚠️ DRAFT)
  - ParityChecker verdict: ENVIRONMENTS ALIGNED | CRITICAL DRIFT (⚠️ DRAFT)
  - Composite Risk Tier: LOW | MEDIUM | HIGH | CRITICAL
```

If status is DRAFT, add banner:
```
> ⚠️ DRAFT PLAN — This strategy activates ONLY after the following are resolved:
> {list each unresolved blocker from ReleaseIntel and ParityChecker}
```

### 2. Rollout Recommendation Block

```markdown
## Recommended Rollout Method: {METHOD NAME}

**Rationale:** {2–3 sentences explaining why this method was selected given the risk profile}

**Deployment Window:** Monday {proposed time, e.g., 10:00–10:30 AM}  
**On-Call Required:** Yes — {name/role} available until {time}  
**Rollback Window:** {duration to keep old environment/pods available for instant revert}
```

### 3. Rollout Phases Table

For canary/feature-flag ramp strategies:

```markdown
## Rollout Phases

| Phase | Traffic % | Hold Period | Progression Trigger | Halt Trigger |
|-------|-----------|------------|--------------------|--------------|
| 1 | 10% | 30 minutes | Error rate <baseline; p95 latency within 20%; all health checks passing | Any rollback trigger threshold breached |
| 2 | 50% | 30 minutes | Same as Phase 1 | Same as Phase 1 |
| 3 | 100% | 15 min monitoring hold | No new errors; smoke test passed | Same as Phase 1 |
```

For direct deploy:

```markdown
## Deployment Sequence

| Step | Action | Expected Duration | Verification |
|------|--------|-----------------|--------------|
| 1 | Apply migration 0045 to production | 5 min | Check migration log; verify row count in user_notification_preferences |
| 2 | Deploy NotifAPI pods (rolling update) | 3 min | Health check /health on all new pods |
| 3 | Enable notifications_v2 feature flag (10%) | 1 min | Confirm flag state in flag service |
...
```

### 4. Trigger Thresholds

```markdown
## Rollout Trigger Thresholds

### Progression Gates (advance to next phase if ALL conditions met for full hold period)
- Error rate (5xx): remains within {n}% of baseline
- p95 response time: within {n}% of baseline
- Health checks: all instances passing
- No CRITICAL-severity log events from deployed components

### Rollback Triggers (initiate rollback IMMEDIATELY if ANY condition is met)

| Component | Metric | Threshold | Action |
|-----------|--------|-----------|--------|
| NotifAPI | 5xx error rate | >2% above baseline for 2+ min | Halt canary; initiate rollback |
| NotifDB | Database connection errors | >5/min | Halt canary; initiate rollback |
| EmailSvc | Webhook processing failures | >10% of events failing | Halt; disable Mailgun webhook |
| [All] | Pod health check failure | Any pod failing >1 min | Halt canary; initiate rollback |
```

### 5. Monday Smoke Test Checklist

```markdown
## Monday Smoke Test Checklist
**Run by:** On-call engineer  
**Time window:** First 30 minutes post-deployment  
**Total estimated time:** {n} minutes

| # | Component | Test Action | Expected Outcome | Pass/Fail | Time (min) |
|---|-----------|------------|-----------------|-----------|-----------|
| 1 | NotifAPI | GET /v1/notifications/preferences as test user | 200 OK; returns default preferences object | | 2 |
| 2 | NotifAPI | POST /v1/notifications/preferences; update email: false | 200 OK; preference persists on subsequent GET | | 3 |
| 3 | NotifDB | Verify migration 0045 applied: check user_notification_preferences row count | Row count = total user count ± 0 | | 2 |
| 4 | NotifUI | Load /settings/notifications in browser | Page renders; toggles functional; WCAG focus visible | | 3 |
| 5 | EmailSvc | Trigger test unsubscribe via Mailgun webhook replay | User opt-out reflected in DB within 30s | | 5 |
| 6 | PushSvc | Opt out test user from push; verify FCM token cleanup | Token not present in Firebase console | | 5 |
| 7 | AuthGate | Attempt unauthenticated GET /v1/notifications/preferences | 401 Unauthorized | | 1 |
| 8 | Monitoring | Confirm New Relic receiving traces from new components | Transactions visible in NR dashboard | | 2 |
| **Total** | | | | | **23 min** |

**Smoke test pass criteria:** All 8 items pass within 30 minutes.  
**If any item fails:** Execute rollback plan immediately. Do not attempt to debug in production.
```

### 6. Gate 3 Recommendation & Attestation

```markdown
## Gate 3 Recommendation

**RolloutAdvisor recommends:** ✅ PROCEED TO DEPLOY | ❌ DO NOT DEPLOY — {reason}

**Conditions for deployment to proceed:**
- [ ] ReleaseIntel: READY TO DEPLOY (zero P0 blockers)
- [ ] ParityChecker: ENVIRONMENTS ALIGNED (zero critical drift)
- [ ] Rollout strategy reviewed and approved by POD Lead
- [ ] Rollback plan reviewed and on-call engineer briefed
- [ ] Smoke test checklist distributed to on-call engineer

**POD Lead Go/No-Go:**
- [ ] ✅ GO — Deployment approved per this strategy
- [ ] ❌ NO-GO — Reason: _______________________
- Signed: _________________________ Date: _____________

> ⚠️ The Go/No-Go deployment decision belongs to the POD Lead. RolloutAdvisor provides an evidence-based recommendation; it does not authorise deployment. No agent may be delegated Go/No-Go authority.
```

---

## rollback-plan.md — Required Sections

### 1. Report Header

```markdown
# Rollback Plan
**Sprint:** {sprint_id}
**Generated:** {date} {time}
**Composite RTO Target:** {n} minutes from trigger to service restoration
**Status:** FINAL | ⚠️ DRAFT
```

### 2. Rollback Overview

```markdown
## Rollback Overview

| Component | Rollback Method | Individual RTO | Data Recovery Needed? |
|-----------|----------------|---------------|-----------------------|
| NotifAPI | Container redeploy (previous tag) | 5 min | No |
| NotifDB | Migration reversal script | 20 min | No (additive migration) |
| NotifUI | Feature flag disable | <1 min | No |
| EmailSvc | Webhook deregistration + secret reversion | 15 min | No |
| PushSvc | Config flag disable | 5 min | No |
| **Composite** | (parallel execution possible) | **25 min** | No |
```

### 3. Per-Component Rollback Procedures

For each component, a numbered step-by-step procedure:

```markdown
## {Component Name} — Rollback Procedure

**Trigger conditions:**
- {specific metric threshold, e.g., "Error rate >2% above baseline for 2+ minutes"}

**Rollback method:** {method}  
**RTO target:** {n} minutes  
**Data recovery required:** Yes — {procedure} | No

### Steps:
1. {Specific action — e.g., "kubectl set image deployment/notif-api notif-api=myapp/notif-api:v{previous_tag} -n production"}
2. {Verification — e.g., "Watch pod rollout: kubectl rollout status deployment/notif-api -n production"}
3. {Confirmation — e.g., "Verify /health returns 200 on all pods"}
4. {Post-rollback action — e.g., "Notify POD Lead via Slack #deployments"}

**Rollback verified when:** {explicit success criterion}
```

### 4. Cross-Component Rollback Sequencing

```markdown
## Rollback Execution Order

If ALL components require simultaneous rollback:

| Order | Component | Dependency | Parallel with |
|-------|-----------|-----------|--------------|
| 1 (immediate) | NotifUI | None | NotifAPI |
| 1 (immediate) | NotifAPI | None | NotifUI |
| 2 (after APIs) | EmailSvc | None | PushSvc |
| 2 (after APIs) | PushSvc | None | EmailSvc |
| 3 (last) | NotifDB | All APIs must be rolled back first | — |

**Rationale:** Database migration rollback last to avoid data inconsistency window.
```

### 5. Post-Rollback Verification

```markdown
## Post-Rollback Verification Checklist

Run after all components rolled back:

| # | Check | Expected Result |
|---|-------|----------------|
| 1 | GET /v1/notifications/preferences | 404 (endpoint not present) OR pre-sprint behavior |
| 2 | /settings/notifications page | Redirects or shows pre-sprint state |
| 3 | Database migration_id | Reverted to 0044 |
| 4 | Monitoring | Error rate returned to baseline |

**Escalation if rollback fails:** {POD Lead name}, {contact}, within {n} minutes.
```

---

## Invariants

1. **Composite RTO must be explicitly stated** in both files.
2. **Every rollback step must be numbered** — no prose-only procedures.
3. **Trigger conditions must be metric-based** — no subjective conditions like "if something seems wrong."
4. **Go/No-Go attestation block is mandatory** in rollout-strategy.md.
5. **Draft status propagates** — if either upstream report has blockers, both files carry DRAFT status.
6. **Smoke test items must have explicit pass/fail criteria** — not just action descriptions.
