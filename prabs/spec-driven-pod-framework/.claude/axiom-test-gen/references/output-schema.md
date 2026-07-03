# Output Schema — AxiomTestGen Reference

AxiomTestGen writes four artifacts to `/mnt/user-data/outputs/`.

## 1. `tests/<epic-id>/…` — Test Files
Runnable test files in the detected framework, named per framework convention
(`test_<module>.py`, `<module>.test.ts`, `<Module>Test.java`). Each test function:
- carries a docstring/comment with its `case_id` and source `AC-ID`,
- asserts a spec-derived oracle,
- uses deterministic fixtures only.

## 2. `test-plan.<epic-id>.yaml` — Machine-Readable Case Manifest
Handoff to Guardian/CI. Schema:

```yaml
epic_id: string            # e.g. EP-03
task_id: string            # e.g. TASK-03.2
ac_version: string         # spec hash/version stamped at generation
framework: string          # pytest | jest | junit | go-test | ...
language: string
generated_by: axiom-test-gen
coverage_target:
  line: 90
  branch: 90
cases:
  - case_id: string        # TC-03.2-001
    title: string
    level: unit|integration|contract|acceptance
    technique: ep|bva|decision-table|state-transition|pairwise|property
    type: positive|negative|boundary|edge|idempotency|concurrency
    ac_refs: [AC-ID, ...]   # >=1 — every case is traceable
    target_symbol: string  # function/endpoint under test (verified)
    fixtures: [string, ...]
    oracle: string         # expected outcome, spec-derived
    test_ref: string       # file::function
gaps_ref: coverage-gap-report.md
```

## 3. `test-traceability.md` — AC → Test Matrix
Bidirectional map. Feeds the Planning-phase `traceability-report.md`.

```markdown
| AC ID | AC summary | Cases | Levels | Status |
|-------|-----------|-------|--------|--------|
| AC-03.2.1 | Requests under limit succeed | TC-03.2-001,002 | unit | ✅ covered |
| AC-03.2.2 | Request at limit+1 is throttled | TC-03.2-003,004,005 | unit,acceptance | ✅ covered |
| AC-03.2.4 | Window rollover resets count | TC-03.2-009 | state-transition | ⚠ partial |
```
Every AC must appear. Uncovered ACs show status ❌ and cross-link the gap report.

## 4. `coverage-gap-report.md` — Gaps + HITL Flags
```markdown
# Coverage Gap Report — <epic-id>
## 🔴 Blocking
- AC-03.2.5 (critical): spec silent on behaviour when clock skews backward — needs decision.
## 🟡 Caution
- Branch `limiter.py:_evict()` else-path uncovered (non-critical).
## 🟢 Info
- Concurrency class N/A: limiter is single-threaded per spec §4.2.
## Coverage estimate
- Lines ~93% · Branches ~91% · Negative cases: 6 (>= 1/AC ✅)
- Mutation run recommended: yes (criticality=critical)
```
