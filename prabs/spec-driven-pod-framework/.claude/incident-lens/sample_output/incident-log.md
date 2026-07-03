# Incident Log — SpecPod Operate Phase
**Maintained by:** IncidentLens v1.0.0
**Project:** [Project Name]
**Last Updated:** 2025-01-01T00:00:00Z

---

## Incident Registry

| ID | Timestamp | Feature | Error Type | Classification | Root Cause | Status | Sprints Seen |
|---|---|---|---|---|---|---|---|
| INC-001 | 2025-01-01T14:32:00Z | summarisation-api | Latency spike | one-off | Anthropic API upstream slowdown | RESOLVED | 1 |
| INC-002 | 2025-01-03T09:15:00Z | classification-api | Error rate spike | pattern | Missing input validation (spec gap) | RESOLVED | 2 |
| INC-003 | 2025-01-08T14:32:00Z | classification-api | Error rate spike | pattern | Missing input validation (spec gap) | RESOLVED | 3 |

---

## Incident Detail Records

### INC-001
- **Timestamp:** 2025-01-01T14:32:00Z
- **Feature:** summarisation-api
- **Symptom:** p99 latency exceeded 4000ms threshold for 8 minutes
- **Error Type:** Latency spike (SLA breach)
- **SLA at incident:** p99=6200ms (threshold: 4000ms), error_rate=0.1%
- **Resolution Steps:** Monitored; Anthropic API returned to normal. No code change required.
- **Root Cause:** Upstream Anthropic API slowdown (transient)
- **Verified Fix:** None required (transient)
- **Classification:** one-off
- **Runbook Section Added:** Yes — `Alert Response Playbooks > summarisation_p99_latency_critical` step 3

---

### INC-002
- **Timestamp:** 2025-01-03T09:15:00Z
- **Feature:** classification-api
- **Symptom:** 5xx error rate spiked to 3.2% for 22 minutes
- **Error Type:** Error rate spike (5xx)
- **SLA at incident:** error_rate_5xx=3.2% (threshold: 1.0%)
- **Resolution Steps:** Identified null input causing unhandled exception. Added input validation guard. Hotfix deployed at 09:37.
- **Root Cause:** Input validation not specified in openspec.yaml for null/empty document payloads
- **Root Cause Type:** spec_gap
- **Verified Fix:** Input validation middleware added to classification-api
- **Classification:** pattern (recurrence pending)
- **Backlog Item Generated:** Yes — `Add null/empty input validation to openspec.yaml acceptance criteria`

---

### INC-003
- **Timestamp:** 2025-01-08T14:32:00Z
- **Feature:** classification-api
- **Symptom:** 5xx error rate 2.8% for 14 minutes (same symptom as INC-002)
- **Error Type:** Error rate spike (5xx)
- **Resolution Steps:** Hotfix from INC-002 not included in sprint-13 deployment (deployment oversight)
- **Root Cause:** Regression — INC-002 hotfix not carried forward to sprint-13
- **Root Cause Type:** missing_test (no regression test for INC-002 fix)
- **Verified Fix:** Re-applied input validation; added regression test
- **Classification:** pattern → escalated to systemic
- **Backlog Item Generated:** Yes — `Add regression test suite for all INC hotfixes to CI pipeline`

---

## Pattern Analysis Summary

**Analysis run:** 2025-01-09T08:00:00Z
**Sprints analysed:** 3
**Thresholds:** pattern≥2, systemic≥4

### Cluster C-001: classification-api input validation failures
- **Incidents:** INC-002, INC-003
- **Classification:** pattern (2 occurrences)
- **Root Cause Type:** spec_gap + missing_test
- **Recommendation:** Add explicit null/empty payload handling to `openspec.yaml` acceptance criteria AND add regression test coverage for INC hotfixes

### Cluster C-002: Anthropic API upstream dependency
- **Incidents:** INC-001
- **Classification:** one-off
- **Recommendation:** Document in runbook; add circuit breaker consideration to next sprint backlog

---

## Sprint Backlog Items (from IncidentLens)

### BACKLOG-001 — Add input validation to openspec.yaml
- **Priority:** High
- **Root Cause:** spec_gap (classification-api, INC-002 + INC-003)
- **Recommended Action:** Update `openspec.yaml` acceptance criteria to explicitly require null/empty input validation for all AI feature endpoints
- **Sprint Impact:** ~2 hours specification + 4 hours implementation

### BACKLOG-002 — Add hotfix regression test requirement to CI
- **Priority:** Medium
- **Root Cause:** missing_test (INC-003 regression)
- **Recommended Action:** Add CI pipeline step that verifies all hotfix test cases pass on each deployment
- **Sprint Impact:** ~4 hours CI configuration
