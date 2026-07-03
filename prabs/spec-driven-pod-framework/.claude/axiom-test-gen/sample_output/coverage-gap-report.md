# Coverage Gap Report — EP-03 / TASK-03.2

## 🔴 Blocking
- **AC-03.2.5 (critical)** — Spec is silent on behaviour when the injected clock
  moves backward (NTP correction). No oracle exists, so no test can be authored
  without guessing. **Action:** POD Lead to obtain an architecture decision
  (DecisionLedger ADR) defining expected behaviour, then re-run AxiomTestGen.

## 🟡 Caution
- None. All implemented branches are exercised.

## 🟢 Info
- **Concurrency class N/A** — limiter is single-threaded per spec §4.2; no
  concurrency cases generated (justified omission).

## Coverage Estimate (verified)
- Line coverage: **100%** (29/29 statements) — measured via pytest-cov.
- Negative cases: 4 across AC-03.2.2 / AC-03.2.3 (≥ 1 per relevant AC ✅).
- Mutation run: **recommended** (criticality=critical) — line coverage alone does
  not prove the throttle threshold is asserted at the exact boundary.

> Note: 100% line coverage with one **uncovered acceptance criterion** (AC-03.2.5)
> is the canonical illustration that coverage % is a floor, not proof of completeness.
