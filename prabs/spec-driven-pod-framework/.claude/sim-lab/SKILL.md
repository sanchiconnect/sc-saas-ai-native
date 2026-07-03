---
name: sim-lab
description: "SimLab validates that every built component meets its Non-Functional Requirements (NFRs) under realistic stress conditions before deployment. It generates load test scripts, injects failure scenarios, and validates that circuit-breakers and fallback behaviours match the spec."
---

# SimLab — Load, Chaos & Resilience Simulation
**SpecPod Framework · Validate Phase · Agent V-04**
Version: 2.1.0 | Model: claude-haiku-4-5-20251001 | Token Budget: ~35K

---

## Purpose

SimLab validates that every built component meets its Non-Functional Requirements (NFRs) under realistic stress conditions before deployment. It generates load test scripts, injects failure scenarios, and validates that circuit-breakers and fallback behaviours match the spec. A component that passes functional tests but fails its p95 latency target or lacks a working circuit-breaker is **not deployable**.

SimLab runs against the staging environment. Environment equivalence must be confirmed by the POD Lead before results are treated as production-representative.

---

## Trigger Phrases

Activate SimLab when the user says:
- "load test", "performance test", "stress test", "NFR validation"
- "chaos engineering", "failure injection", "circuit-breaker test"
- "resilience testing", "dependency down scenario"
- "SimLab" (explicit invocation)
- Any reference to p95 latency, concurrent users, error rate, throughput targets

---

## Input Files

| File | Location | Required | Notes |
|------|----------|----------|-------|
| `openspec.yaml` | `artifacts/openspec.yaml` | ✅ REQUIRED | NFR targets: latency, concurrency, error rate ceiling |
| `deploy-manifest.yaml` | `artifacts/deploy-manifest.yaml` | ✅ REQUIRED | Integration endpoint list for load targeting |
| `task-breakdown.yaml` | `artifacts/task-breakdown.yaml` | Optional | Edge case scenarios from acceptance criteria |
| `context.yaml` | `artifacts/context.yaml` | Optional | Delivery context for environment assumptions |

---

## NFR Target Extraction

SimLab reads the following fields from `openspec.yaml`. If these fields are absent, it prompts the POD Lead before proceeding:

```yaml
# Expected NFR block in openspec.yaml:
nfr:
  latency:
    p50_ms: 200
    p95_ms: 500
    p99_ms: 1000
  concurrency:
    target_users: 100
    peak_users: 500
  error_rate:
    ceiling_pct: 1.0
  availability:
    target_pct: 99.9
  circuit_breaker:
    timeout_ms: 3000
    failure_threshold_pct: 50
    recovery_window_s: 30
```

**HITL elicitation if NFR block absent:**
> "No NFR block found in `openspec.yaml`. Before SimLab can run, I need the following from you:
>
> 1. **Target concurrency:** How many simultaneous users should the system handle? (e.g., 100 normal, 500 peak)
> 2. **Latency target:** What is the acceptable p95 response time in milliseconds? (e.g., ≤ 500ms)
> 3. **Error rate ceiling:** What percentage of requests can fail under load? (e.g., ≤ 1%)
> 4. **Dependencies:** Which external services does the system call? What should happen if each one is unavailable?
> 5. **Circuit-breaker behaviour:** Is one specified? What are the timeout and failure thresholds?"

---

## Step-by-Step Execution

### Step S1 — Parse NFR Targets and Endpoint Inventory

Extract NFR targets from `openspec.yaml`. Extract all integration endpoints from `deploy-manifest.yaml`. Build a test matrix: each endpoint × each NFR scenario.

### Step S2 — Generate Load Test Scripts

For each endpoint in the manifest, generate load test scripts using **k6** format (default) or the framework specified in `openspec.yaml`:

```javascript
// Generated k6 load test — [endpoint-name] — SPRINT-2025-W22
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

const errorRate = new Rate('errors');

export let options = {
  stages: [
    { duration: '2m', target: [TARGET_USERS] },   // ramp-up
    { duration: '5m', target: [TARGET_USERS] },   // steady state
    { duration: '1m', target: [PEAK_USERS] },     // spike
    { duration: '2m', target: 0 },                // ramp-down
  ],
  thresholds: {
    http_req_duration: ['p(95)<[P95_TARGET_MS]'],
    errors: ['rate<[ERROR_CEILING_PCT / 100]'],
  },
};

export default function() {
  const res = http.post('[ENDPOINT_URL]', JSON.stringify([SAMPLE_PAYLOAD]), {
    headers: { 'Content-Type': 'application/json' },
  });
  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < [P95_TARGET_MS]ms': (r) => r.timings.duration < [P95_TARGET_MS],
  });
  errorRate.add(res.status !== 200);
  sleep(1);
}
```

SimLab generates one script per endpoint. Scripts are parameterised with values from `openspec.yaml` NFR block — no hardcoded values.

### Step S3 — Generate Failure Injection Scenarios

For each dependency in `deploy-manifest.yaml`, generate chaos scenarios:

**Scenario Types:**
1. **Dependency Unavailable** — Target service returns 503/timeout
2. **Dependency Degraded** — Target service returns 200 but with 5× normal latency
3. **Dependency Rate-Limited** — Target service returns 429
4. **Partial Failure** — 50% of requests to dependency fail
5. **Cascade Failure** — Multiple dependencies fail simultaneously

For each scenario, validate that the component under test:
- Activates its circuit-breaker within the specified `timeout_ms`
- Returns the correct fallback response defined in `openspec.yaml`
- Does not propagate the failure to the caller as an unhandled error
- Recovers correctly after the dependency becomes available again

**Circuit-breaker validation script format:**
```javascript
// Failure injection test — [dependency-name] unavailable
// Expected: circuit-breaker opens within [timeout_ms]ms
// Expected fallback: [fallback behaviour from openspec]
```

### Step S4 — Generate Edge Case Simulations

Read acceptance criteria from `task-breakdown.yaml` for any edge cases flagged as performance-sensitive. Generate simulation scenarios for:
- Minimum viable input (empty documents, single-character strings)
- Maximum input (documents at size limit, maximum field counts)
- Concurrent duplicate requests (idempotency validation)
- Rapid successive requests from the same user (rate-limit behaviour)

### Step S5 — Execute Simulations and Capture Results

Run all generated scripts against the staging environment endpoints from `deploy-manifest.yaml`. Capture:

**Load test metrics per endpoint:**
- p50, p95, p99 latency
- Requests per second at peak load
- Error rate under normal load
- Error rate at peak load
- Latency degradation ratio (peak vs. normal)

**Failure injection metrics per scenario:**
- Time-to-circuit-breaker-open (ms)
- Fallback response correctness (match/mismatch vs. spec)
- Recovery time after dependency restoration (s)
- Error propagation count (should be 0 for correct circuit-breaker)

### Step S6 — NFR Pass/Fail Verdict

Compare captured metrics against `openspec.yaml` NFR targets. Apply the following verdict rules:

| Metric | Condition | Verdict |
|--------|-----------|---------|
| p95 latency | ≤ target | PASS |
| p95 latency | > target by ≤ 20% | WARN |
| p95 latency | > target by > 20% | FAIL |
| Error rate | ≤ ceiling | PASS |
| Error rate | > ceiling | FAIL |
| Circuit-breaker opens | Within timeout_ms | PASS |
| Circuit-breaker opens | Does not open | FAIL |
| Fallback response | Matches spec | PASS |
| Fallback response | Does not match spec | FAIL |

**Any FAIL verdict blocks the Release gate.**

---

## Output Files

| File | Location | Description |
|------|----------|-------------|
| `load-test-scripts/` | `tests/load/` | Generated k6 scripts (one per endpoint) |
| `chaos-scenarios/` | `tests/chaos/` | Generated failure injection test scripts |
| `simlab-results.json` | `artifacts/simlab-results.json` | Raw metrics — p50/p95/p99 + failure injection pass/fail |
| `nfr-verdict.md` | `artifacts/nfr-verdict.md` | Human-readable NFR pass/fail with Release gate input |

---

## HITL Gates

| Condition | Action |
|-----------|--------|
| NFR block absent from openspec.yaml | Must elicit NFR targets from POD Lead before proceeding |
| Staging ≠ production equivalence unconfirmed | POD Lead must confirm environment parity before results are treated as valid |
| Any FAIL verdict | Immediate POD Lead notification — Release gate blocked |
| Any WARN verdict | POD Lead must accept or fix before Release gate |
| Circuit-breaker behaviour not specified in openspec | Must elicit expected fallback behaviour from POD Lead |

---

## Environment Equivalence Warning

SimLab results are only valid if the staging environment is functionally equivalent to production. Before accepting SimLab results as Release gate evidence, the POD Lead must confirm:

1. Staging uses the same compute tier or a documented equivalent
2. Database sizes are representative (not empty test databases)
3. All integration dependencies point to staging equivalents, not production
4. Network latency between services is comparable to production topology

Document this confirmation in `artifacts/nfr-verdict.md`.

---

## Limitations

- Simulations run against staging. Infrastructure differences can produce false-pass results.
- Load test scripts are generated — they must be reviewed by a builder before execution in sensitive environments.
- SimLab generates k6 scripts by default. If the project uses a different framework (JMeter, Locust, Gatling), specify in `openspec.yaml` under `nfr.test_framework`.
- Chaos scenarios simulate dependency failures via mock responses — actual network fault injection requires infrastructure tooling (e.g., Toxiproxy, AWS Fault Injection Simulator) configured separately.

---

## Integration Points

| Consumer | Input From SimLab |
|----------|------------------|
| InsightOps | `simlab-results.json` — performance pattern analysis |
| Release Gate | `nfr-verdict.md` — NFR pass/fail verdict |
