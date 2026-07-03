# SimLab — NFR Verdict Report
**Sprint:** SPRINT-2025-W22 | **Generated:** 2025-05-27T17:00:00Z
**Environment:** staging-us-east-1 | **Equivalence confirmed by:** pod-lead@aligned.io

---

## Release Gate Verdict: ⚠️ WARN (Conditional Pass)

| Metric | Target | Actual | Verdict |
|--------|--------|--------|---------|
| p50 latency — extraction-engine | ≤ 200ms | 145ms | ✅ PASS |
| p95 latency — extraction-engine | ≤ 500ms | 548ms | ⚠️ WARN (+9.6%) |
| p99 latency — extraction-engine | ≤ 1000ms | 920ms | ✅ PASS |
| Error rate under normal load | ≤ 1% | 0.3% | ✅ PASS |
| Error rate at peak load (500 users) | ≤ 1% | 0.8% | ✅ PASS |
| Circuit-breaker — scanner-service down | Opens ≤ 3000ms | Opens at 2850ms | ✅ PASS |
| Fallback response — scanner unavailable | Returns cached result | Returns cached result | ✅ PASS |
| Recovery after scanner restoration | Resumes ≤ 30s | Resumes at 22s | ✅ PASS |

---

## WARN Detail — p95 Latency

**Endpoint:** POST /api/documents/extract
**Target:** ≤ 500ms at p95
**Actual:** 548ms at p95 (9.6% over target)
**At load:** 100 concurrent users (target load)

**Root cause hypothesis:** p95 latency spike correlates with documents > 30 pages. The extraction engine processes pages sequentially, and the p95 population includes a disproportionate share of multi-page documents.

**Recommended action (POD Lead decision required):**
- Option A: Builder-1 to implement parallel page processing — estimated 2h effort. Re-run SimLab.
- Option B: Accept 548ms as revised p95 target. Update `openspec.yaml` NFR block. Document rationale.
- Option C: Add document page count limit (max 30 pages) as a functional constraint. Update acceptance criteria in openspec.

**POD Lead sign-off required before Release gate clears.**

---

## Load Test Raw Metrics

| Load Stage | RPS | p50 | p95 | p99 | Error % |
|------------|-----|-----|-----|-----|---------|
| Ramp-up (0→100 users) | 45 | 130ms | 290ms | 450ms | 0.1% |
| Steady state (100 users) | 95 | 145ms | 548ms | 920ms | 0.3% |
| Peak spike (500 users) | 410 | 220ms | 890ms | 1800ms | 0.8% |
| Ramp-down | 20 | 125ms | 250ms | 380ms | 0.0% |

**Note:** Peak spike (500 users) exceeds all NFR targets. POD Lead should determine whether 500 concurrent users is a realistic scenario for this sprint's release.

---

## Failure Injection Results

| Scenario | Dependency | Expected Behaviour | Actual Behaviour | Verdict |
|----------|------------|-------------------|-----------------|---------|
| Scanner unavailable | security-service | Circuit-breaker opens, return cached clean status | ✅ Correct | PASS |
| Scanner degraded (5× latency) | security-service | Timeout at 3000ms, activate fallback | ✅ Correct | PASS |
| Database unavailable | document-store | Return 503 with retry-after header | ✅ Correct | PASS |
| Database degraded | document-store | Degrade gracefully, p95 ≤ 2× normal | p95 = 1.8× normal | PASS |
| Concurrent duplicate uploads | upload-service | Idempotent — second request returns same document_id | ✅ Correct | PASS |
