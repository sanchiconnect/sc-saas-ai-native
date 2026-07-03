# ReleaseIntel — Readiness Thresholds & Scoring Rules

**Version:** 2.1.0  
**Used by:** ReleaseIntel Step 3, Step 4, Step 6

---

## Gate 3 Pass/Fail Thresholds

### Automatic DEPLOY BLOCKER (P0) Conditions

Any single condition below forces `NOT READY` verdict regardless of all other signals:

| # | Condition | Source Artifact |
|---|-----------|----------------|
| B1 | One or more sprint tasks are `BLOCKED` with no resolution documented | sprint-board.md |
| B2 | One or more sprint tasks are `IN PROGRESS` (not DONE or IN REVIEW) at Friday EOD | sprint-board.md |
| B3 | Requirements coverage below **80%** (traced requirements / total requirements) | traceability-report.md |
| B4 | One or more `CRITICAL` risk scenarios in scenario-matrix with **no documented mitigation** | scenario-matrix.md |
| B5 | One or more unresolved HITL blockers in assumption-log (status ≠ RESOLVED) | assumption-log.md |
| B6 | One or more ADRs with status `CONTESTED` that affect a component in deployment scope | decision-ledger.md |
| B7 | Any component has blast-radius `CRITICAL` on **Data Risk** dimension (destructive migration with no tested rollback) | task-breakdown.yaml |

### P1 — HIGH RISK (POD Lead explicit acceptance required)

| # | Condition |
|---|-----------|
| R1 | Requirements coverage 80–89% |
| R2 | One HIGH risk scenario with mitigation documented but not tested |
| R3 | Open assumptions (not HITL blockers) affecting deployed components |
| R4 | ADR marked `PENDING` (not yet decided) but affects deployment scope |
| R5 | Any component blast-radius `HIGH` on 2+ dimensions |
| R6 | Deployment scope inferred (no deploy-manifest.yaml provided) |

### P2 — MEDIUM RISK (Document and monitor)

| # | Condition |
|---|-----------|
| M1 | Requirements coverage 90–94% |
| M2 | MEDIUM risk scenarios with mitigation |
| M3 | Non-critical ADRs with PENDING status outside deployment scope |
| M4 | Any component blast-radius `HIGH` on exactly 1 dimension |

### P3 — LOW RISK (Informational)

| # | Condition |
|---|-----------|
| L1 | Requirements coverage ≥ 95% |
| L2 | All scenarios mitigated or LOW risk |
| L3 | All blast-radius dimensions LOW or MEDIUM |

---

## Blast Radius Composite Scoring

### Per-Dimension Weights

| Dimension | Weight | Rationale |
|-----------|--------|-----------|
| Data Risk | 35% | Schema/migration failures are hardest to roll back |
| Integration Points | 25% | External breakage affects systems outside team control |
| User Segments | 20% | Breadth of user impact drives incident severity |
| Dependent Features | 15% | Internal coupling determines blast propagation |
| Rollback Complexity | 5% | Affects recovery speed, not initial impact |

### Dimension Rating Criteria

**User Segments**
- `LOW` — Internal/admin users only, or <5% of active user base
- `MEDIUM` — One identifiable user segment, 5–30% of active users
- `HIGH` — Multiple segments or 30–70% of active users
- `CRITICAL` — All users or core authentication/billing flows

**Dependent Features**
- `LOW` — No other features depend on this component
- `MEDIUM` — 1–2 features depend on it, all in current sprint
- `HIGH` — 3–5 features depend on it, some from prior sprints
- `CRITICAL` — Core shared service (auth, payments, data pipeline); 6+ dependents

**Integration Points**
- `LOW` — No external integrations; internal DB reads only
- `MEDIUM` — 1–2 third-party APIs, all with documented fallbacks
- `HIGH` — 3–5 external services, some without fallbacks
- `CRITICAL` — Payment gateway, identity provider, or core data sync

**Data Risk**
- `LOW` — No schema changes; read-only or additive inserts only
- `MEDIUM` — Additive schema changes (new nullable columns); no migrations
- `HIGH` — Non-destructive migrations with tested rollback script
- `CRITICAL` — Destructive migration (column drops, type changes, data transforms) OR migration without tested rollback

**Rollback Complexity**
- `LOW` — Feature flag toggle; zero-downtime revert
- `MEDIUM` — Revert via git tag + container redeploy; <15 min RTO
- `HIGH` — Requires migration reversal or cache flush; 15–60 min RTO
- `CRITICAL` — No clean rollback path; requires full restore from backup

### Composite Score → Overall Rating

```
composite = sum(dimension_rating_value × dimension_weight)

where rating values: LOW=1, MEDIUM=2, HIGH=3, CRITICAL=4

Override rules (applied before composite):
  - Any dimension = CRITICAL on Data Risk → overall = CRITICAL
  - Any dimension = CRITICAL on Integration Points → overall = CRITICAL
  - 2+ dimensions = HIGH → overall = HIGH (minimum)
```

---

## Readiness Score (Informational — does not override binary verdict)

A 0–100 readiness score for context only. Does not determine the verdict.

```
Base score: 100

Deductions:
  Each P0 blocker:    -25 points
  Each P1 risk:       -10 points
  Each P2 risk:        -3 points
  Each P3 item:        -1 point

Floor: 0 (cannot go negative)
```

**Interpretation:**
- 90–100: Exemplary release hygiene
- 75–89: Acceptable; monitor flagged items
- 60–74: Marginal; POD Lead review required
- Below 60: High-risk release; consider deferring scope
- Any P0 present: Score is informational only — verdict is NOT READY regardless

---

## Coverage Calculation Method

When deriving from `traceability-report.md`:

```
coverage_pct = (requirements_with_passing_tests / total_requirements_in_scope) × 100

Exclude from denominator:
  - Requirements explicitly descoped this sprint (document the exclusion)
  - Requirements deferred to future sprint (document with sprint reference)

Include in denominator:
  - All requirements in openspec.yaml that map to tasks in sprint-board.md
```

If `traceability-report.md` is absent, treat coverage as UNKNOWN and raise as P1 risk R1 (cannot confirm 80% threshold met).
