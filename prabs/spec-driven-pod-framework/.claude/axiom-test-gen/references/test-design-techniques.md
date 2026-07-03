# Test-Design Techniques — AxiomTestGen Reference

Apply these formal techniques rather than ad-hoc enumeration. Each generated case
should be attributable to one technique, recorded in `test-plan.yaml > technique`.

## 1. Equivalence Partitioning (EP)
Divide each input domain into classes that the system should treat identically.
Generate **one** representative case per class (valid and invalid classes).
> Example — a limit field accepting 1–100: classes = `{<1}`, `{1–100}`, `{>100}`,
> `{non-integer}`. Four cases, not forty.

## 2. Boundary Value Analysis (BVA)
For every ordered/numeric/length boundary, test **on, just below, and just above**.
Most defects cluster at boundaries.
> Example — window limit of 60: test `59`, `60`, `61` (and `0`, `1` at the lower edge).

## 3. Decision Tables
For logic with multiple interacting conditions, enumerate condition combinations →
expected action. Collapse impossible/duplicate rules. Generate one case per surviving rule.
> Use when an AC reads "if A and (B or C) then …".

## 4. State-Transition Testing
For stateful components, model states + legal transitions. Cover: each valid
transition, at least one invalid transition per state, and entry/exit states.
> Example — rate-limiter window: `OPEN → THROTTLED → OPEN (rollover)`.

## 5. Pairwise / Combinatorial Reduction
When a feature has many independent config flags, full Cartesian coverage explodes.
Generate a **pairwise** set covering every pair of values at least once. This is the
primary lever against token/case blowout.

## 6. Property-Based Testing
For invariants that must hold across all inputs (idempotency, commutativity,
round-trip encode/decode, monotonicity), express the property and let the framework
generate inputs (`hypothesis` for pytest, `fast-check` for JS). Pin the seed.

## Level Selection Guide
| Signal in the AC | Test level |
|------------------|-----------|
| Pure function / single unit behaviour | unit |
| Two+ modules collaborating, DB, queue | integration |
| External/public interface shape & status codes | contract |
| End-user observable outcome of the AC | acceptance |

## Anti-patterns To Reject (Step 10 self-check)
- Tests with no assertion or only `assertIsNotNone`.
- Expected value computed by calling the same code path under test.
- Reliance on real time, network, filesystem state, or unseeded randomness.
- One giant test asserting many unrelated behaviours (split into focused cases).
