---
name: rollout-advisor
description: "SpecPod RolloutAdvisor agent — rollout strategy, rollback plan, and go/no-go recommendation. Activate on Friday after ReleaseIntel and ParityChecker have both cleared. Reads release-intel-report.md, parity-check-report.md, deploy-manifest or inferred sprint scope, and scenario-matrix.md. Recommends rollout method (canary %, blue-green, fe"
---

**name:** rollout-advisor

**description:** SpecPod RolloutAdvisor agent — rollout strategy, rollback plan, and go/no-go recommendation. Activate on Friday after ReleaseIntel and ParityChecker have both cleared. Reads release-intel-report.md, parity-check-report.md, deploy-manifest or inferred sprint scope, and scenario-matrix.md. Recommends rollout method (canary %, blue-green, feature-flag toggle), generates a rollback plan with RTO target and trigger conditions, and defines the Monday smoke test checklist. Outputs rollout-strategy.md and rollback-plan.md. Trigger phrases: "rollout advice", "how should we deploy", "rollout strategy", "rollback plan", "go/no-go recommendation", "RolloutAdvisor", "Monday deploy plan", "deployment strategy", "canary rollout", "blue-green deploy".


# RolloutAdvisor — SpecPod Release Agent R-03

**Phase:** 4 — Release  
**Sprint Day:** Friday (after ReleaseIntel + ParityChecker)  
**Gate:** HITL Gate 3 — QA Sign-off  
**Model:** `claude-sonnet-4-20250514`  
**Target token budget:** ~35K  
**Outputs:** `rollout-strategy.md`, `rollback-plan.md`

---

## Purpose

RolloutAdvisor answers the final question before Friday Gate 3 locks:

> *"Given the risk profile of this deployment, what is the safest way to execute it on Monday — and if something breaks, exactly how do we recover?"*

It removes the ad-hoc Friday-afternoon rollout decision from a fatigued POD Lead. Monday deployment becomes **mechanical execution** of a pre-approved plan rather than improvised decision-making.

---

## Required Inputs (read in this order)

| File | Description | Required |
|------|-------------|----------|
| `artifacts/release/release-intel-report.md` | Readiness verdict + blast-radius table | ✅ |
| `artifacts/release/parity-check-report.md` | Environment parity verdict | ✅ |
| `artifacts/scenario-matrix.md` | Risk/opportunity scenarios from planning | Strongly recommended |
| `artifacts/sprint-board.md` | Deployment scope (fallback) | ✅ if no deploy-manifest |
| `artifacts/task-breakdown.yaml` | Component detail, rollback notes, integration points | ✅ |
| `artifacts/release/deploy-manifest.yaml` | Explicit deployment scope (if present) | Optional |

**If `release-intel-report.md` is missing:**
> *"RolloutAdvisor requires the ReleaseIntel report to proceed. Please run ReleaseIntel first and provide `artifacts/release/release-intel-report.md`."*

**If `parity-check-report.md` is missing:**
> *"RolloutAdvisor requires the ParityChecker report to proceed. Please run ParityChecker first and provide `artifacts/release/parity-check-report.md`."*

**If either report shows a BLOCKED/NOT READY verdict:**
Continue processing but prominently flag that the rollout strategy is contingent on blockers being resolved. State clearly:
> *"⚠️ This rollout strategy is DRAFT ONLY. ReleaseIntel / ParityChecker shows unresolved blockers. This plan activates only after Gate 3 pre-conditions are met."*

---

## Workflow

### Step 1 — Risk Profile Synthesis

Extract and combine the following from input artifacts:

**From `release-intel-report.md`:**
- Overall blast radius rating (LOW / MEDIUM / HIGH / CRITICAL)
- Count and nature of P0 blockers (should be zero; if not, flag as draft)
- Count and nature of P1 risks accepted by POD Lead
- Components with HIGH or CRITICAL blast radius

**From `parity-check-report.md`:**
- Critical drift count (should be zero; if not, flag as draft)
- Notable drift items acknowledged (particularly: migration state, feature flags, connection pools)

**From `scenario-matrix.md` (if present):**
- HIGH/CRITICAL risk scenarios that could activate during or shortly after deployment
- Any scenario with a trigger condition involving deployment itself (e.g., "traffic spike on feature launch")

**Composite risk tier determination:**

| Condition | Composite Risk Tier |
|-----------|-------------------|
| Any CRITICAL blast radius component OR any P0 unresolved | `CRITICAL` (recommend defer) |
| Overall blast radius HIGH OR 2+ P1 risks accepted OR HIGH scenario with no mitigation | `HIGH` |
| Overall blast radius MEDIUM OR 1 P1 risk accepted OR notable drift items present | `MEDIUM` |
| Overall blast radius LOW, zero P1 risks, zero notable drift | `LOW` |

---

### Step 2 — Elicit User Impact Profile

Ask the POD Lead the following questions (can be answered sequentially or together):

> **Q1 — User segments active during Monday deployment window:**
> "What is your planned deployment time window on Monday? Who are your active users at that time (geography, user type)? Approximately what % of your user base is typically active during this window?"

> **Q2 — Feature flag availability:**
> "Do you have a feature flag service in place? Are all components in this release gated behind feature flags, or will any changes be hard-deployed without a flag?"

> **Q3 — Prior incident history (brief):**
> "Have any previous sprints had post-deploy incidents? If yes, briefly — what caused them? (We'll use this to calibrate rollback trigger thresholds.)"

> **Q4 — Infrastructure rollback capability:**
> "Can you perform a blue-green switch or canary rollout in your current infrastructure? Or does your deploy model only support in-place rolling updates?"

> **Q5 — Monday on-call coverage:**
> "Who is on-call Monday post-deployment? Is there a named engineer available for the first 2 hours after deployment?"

Accept partial answers — if POD Lead skips questions, note the gap and make conservative assumptions.

---

### Step 3 — Rollout Method Recommendation

Select the recommended rollout method based on composite risk tier and infrastructure capability (from Q4).

**Decision logic:**

```
IF composite_risk == CRITICAL:
  → Recommend: Defer to next sprint. If business forces deployment, use Feature-Flag Toggle only.
  → Canary % = 0 (feature is off for all users until manually enabled post-verification)

IF composite_risk == HIGH AND feature_flag_available == true:
  → Primary: Feature-Flag Toggle (all users, flag controls exposure)
  → Alternative: Canary 5% → 25% → 100% (3-phase with 30-min hold at each step)

IF composite_risk == HIGH AND feature_flag_available == false:
  → Primary: Canary 10% → 50% → 100% (3-phase with 1-hour hold at each step)
  → Alternative: Blue-Green (if infrastructure supports it)

IF composite_risk == MEDIUM AND feature_flag_available == true:
  → Primary: Feature-Flag Toggle (ramp 10% → 50% → 100% over 2 hours)
  → Alternative: Direct deploy with 30-min post-deploy monitoring hold

IF composite_risk == MEDIUM AND feature_flag_available == false:
  → Primary: Canary 20% → 100% (2-phase with 30-min hold)
  → Alternative: Direct deploy with mandatory 30-min monitoring hold

IF composite_risk == LOW:
  → Primary: Direct deploy (rolling update)
  → No canary required; mandatory 15-min monitoring hold post-deploy
```

**Rollout method definitions:**

| Method | Description | Infrastructure requirement |
|--------|-------------|--------------------------|
| **Feature-Flag Toggle** | Code deploys to 100% of pods; feature activation controlled by flag. Instant revert: flip flag. | Feature flag service required |
| **Canary** | Route X% of live traffic to new pods; monitor; expand incrementally. | Load balancer with weighted routing |
| **Blue-Green** | Spin up full production-equivalent environment with new code; switch traffic; keep old environment live for rapid revert. | 2x infrastructure capacity available |
| **Direct Deploy (Rolling)** | Replace pods in-place, one at a time, with zero-downtime rolling update. | Kubernetes rolling update or equivalent |

---

### Step 4 — Trigger Thresholds

Define the specific conditions that trigger each phase gate (canary expansion) or halt (rollback activation).

Base thresholds on blast radius and risk tier. Adjust based on prior incident history from Q3.

**Progression triggers** (conditions to advance canary to next phase):
- Error rate at new pods remains below baseline for hold period
- p95 response time at new pods within 20% of baseline
- No CRITICAL log entries from new component during hold period
- Health check passing on all new pod instances

**Rollback triggers** (conditions requiring immediate halt and rollback):

| Metric | LOW risk threshold | MEDIUM risk threshold | HIGH risk threshold |
|--------|------------------|----------------------|-------------------|
| Error rate (5xx) | >5% increase over baseline | >2% increase over baseline | >1% increase over baseline |
| p95 latency | >100% increase over baseline | >50% increase over baseline | >25% increase over baseline |
| Health check failures | Any pod health check failing >2 min | Any pod health check failing >1 min | Any pod health check failing >30 sec |
| Database connection errors | >10 errors/min | >5 errors/min | >2 errors/min |
| Feature-specific error | Any crash in core feature path | — | — |

Include component-specific thresholds for any HIGH or CRITICAL blast-radius component (derived from blast-radius table in ReleaseIntel report).

---

### Step 5 — Rollback Plan Generation

For each component in deployment scope, define the rollback procedure.

**Rollback plan structure per component:**
1. **Trigger conditions**: specific metrics or events that activate this rollback
2. **Rollback method**: feature flag flip / container redeploy / migration reversal / blue-green switch
3. **Step-by-step procedure**: numbered steps, no ambiguity
4. **RTO target**: time from trigger to service restoration
5. **Data recovery actions**: required only if data was written during the failed deployment window
6. **Verification steps**: how to confirm rollback succeeded

**Cross-component rollback sequencing:**
- If multiple components share data dependencies (e.g., API + DB), define rollback order
- Database rollbacks always come last (unless the migration itself is the cause of failure)
- Feature flag rollbacks can be done in any order

**Composite RTO target** = maximum individual component RTO + 5-minute coordination buffer.

---

### Step 6 — Monday Smoke Test Checklist

Generate a specific, executable smoke test checklist for the on-call engineer to run in the first 30 minutes post-deployment.

**Checklist structure:**
- Each item is a concrete action with an expected outcome
- Items are ordered from critical path → secondary features
- Each item is marked with the component it validates
- Time estimate per item
- Pass/fail criterion stated explicitly

Derive checklist items from:
- Each component in deployment scope (test its primary function)
- Integration points flagged in blast-radius table
- Notable drift items from ParityChecker (especially connection pool, WAF, APM agent)
- HIGH/CRITICAL scenarios from scenario-matrix that could activate post-deploy

---

### Step 7 — Write Outputs

Produce two files:
1. `rollout-strategy.md` — per `references/output-schema.md` (Strategy section)
2. `rollback-plan.md` — per `references/output-schema.md` (Rollback section)

Write both to `artifacts/release/`.

---

## Running Interactively (Claude.ai / Claude Code chat)

1. Confirm `release-intel-report.md` and `parity-check-report.md` are available and both show READY/ALIGNED (or flag as draft if not).
2. Synthesise risk profile (Step 1).
3. Ask the 5 elicitation questions (Step 2) — accept sequential or grouped responses.
4. Generate rollout recommendation (Step 3).
5. Define trigger thresholds (Step 4).
6. Generate rollback plan (Step 5).
7. Generate smoke test checklist (Step 6).
8. Write `rollout-strategy.md` and `rollback-plan.md` to `artifacts/release/`.
9. Present both files and summarise the rollout method in one sentence.

---

## Running via Script

```bash
python scripts/rollout_advisor.py \
  --release-intel artifacts/release/release-intel-report.md \
  --parity-check artifacts/release/parity-check-report.md \
  --task-breakdown artifacts/task-breakdown.yaml \
  --scenario-matrix artifacts/scenario-matrix.md \
  --sprint-board artifacts/sprint-board.md \
  --output-strategy artifacts/release/rollout-strategy.md \
  --output-rollback artifacts/release/rollback-plan.md \
  --sprint-id SPRINT-ID-HERE
```

Script runs Steps 1, 3–7 automatically. Prompts for Step 2 (elicitation) interactively.

---

## Reference Files

- `references/output-schema.md` — Required sections for both output files, gate-3 recommendation block, attestation format

---

## Sample Files

```
sample_input/
  release-intel-report.md   ← READY verdict, 1 P1 risk (from ReleaseIntel sample)
  parity-check-report.md    ← ALIGNED (0 critical drift, after resolutions applied)

sample_output/
  rollout-strategy.md       ← Feature-flag ramp: 10% → 50% → 100%
  rollback-plan.md          ← 3-component rollback, composite RTO 30 min
```

---

## Key Design Principles

**Recommendations are pre-approved decisions, not suggestions.** When the POD Lead accepts this plan at Gate 3, Monday deployment is execution — not decision-making. Write the strategy and rollback plan at the level of specificity that allows a competent engineer who wasn't in Friday's review to execute it.

**Go/No-Go always belongs to a named human.** RolloutAdvisor recommends; the POD Lead decides. The report ends with a signature block. Delegation of the Go/No-Go to any agent is not permitted under any circumstances.

**Draft status must be unambiguous.** If either upstream report (ReleaseIntel / ParityChecker) shows blockers, every page of the output must carry a DRAFT watermark and a clear statement of the unresolved blockers. A partial plan that looks complete is more dangerous than no plan.

**Conservative thresholds by default.** Calibrate trigger thresholds toward caution. The cost of an unnecessary rollback is 30 minutes of engineer time. The cost of a missed trigger is a production incident. Default thresholds favour early detection over tolerance.
