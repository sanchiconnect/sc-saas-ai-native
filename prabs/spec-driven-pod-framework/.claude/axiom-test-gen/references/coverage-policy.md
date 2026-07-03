# Coverage Policy — AxiomTestGen Reference

## Targets
| Metric | Target | Notes |
|--------|--------|-------|
| Line coverage | **> 90%** | Floor, not proof of correctness |
| Branch coverage | **> 90%** | Every decision both true/false |
| Mutation score | ≥ 70% (recommended) | Required gate for `critical` tasks — the real validity signal |
| Negative-case quota | **≥ 1 per acceptance criterion** | More for `critical` |

Coverage % alone is rejected as a sufficiency signal: high coverage with weak
assertions is the most common false-confidence failure. AxiomTestGen reports
coverage *gaps*, and for `critical` tasks recommends a mutation run (the suite must
kill injected faults, not merely execute lines).

## Mandatory Edge Taxonomy
Every task must generate cases across these classes where applicable. If a class is
not applicable, state why in `coverage-gap-report.md` (do not silently skip).

1. **Boundary** — on / just-below / just-above every numeric, length, or time limit.
2. **Empty / null / missing** — empty collections, null inputs, absent optional fields.
3. **Format / type violation** — wrong type, malformed string, out-of-enum value.
4. **Error / exception paths** — every documented failure mode and its error contract.
5. **Idempotency / retry** — repeated calls produce the specified (not duplicated) effect.
6. **Ordering / concurrency** — where the AC implies sequencing or shared state.
7. **Resource exhaustion** — limits hit (quota, window full, pool drained).

Security/abuse cases (injection, auth bypass, fuzzing) are **out of scope** — routed
to RedTeamX. AxiomTestGen covers basic input-validation negatives only.

## Assertion-Strength Rubric (Step 10)
A test passes the self-check only if it:
- asserts a **concrete expected value** derived from the spec, and
- the expected value was **not** produced by the code under test, and
- it isolates **one** behaviour (focused), and
- failure messages identify the violated AC.

## Coverage-Gap Severity
| Severity | Condition | Action |
|----------|-----------|--------|
| 🔴 Block | Uncovered `critical` AC, or ambiguous AC on critical path | HITL before Validate accepts |
| 🟡 Caution | Uncovered branch on non-critical path | Note; POD Lead discretion |
| 🟢 Info | Edge class N/A with justification | Record only |
