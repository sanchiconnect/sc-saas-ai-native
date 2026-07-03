# Guardian

Converts locked acceptance criteria into executable Gherkin test suites before the Build phase begins, then continuously executes those tests as code modules land from AI Builders. Every failure is triaged into exactly one of three categories. No artifact can progress to Release without a Guardian `coverage-report.md` showing ≥ 80% requirement coverage and zero untriaged failures.

---

## When to Use

**Generation Mode:** Run before source code exists to generate the full `.feature` file set.
**Execution + Triage Mode:** Run after code modules land to execute tests and triage failures.

**Trigger phrases:** `generate tests`, `run tests`, `triage failures`, `coverage report`

---

## Inputs

| Input | Required |
|---|---|
| `artifacts/openspec.yaml` | Mandatory |
| `artifacts/ai-manifest.json` | Mandatory |
| `artifacts/traceability-report.md` | Mandatory |
| Source code modules (`src/**`) | Execution mode only |
| `artifacts/eval-rubric.yaml` | Optional |

## Outputs

- `tests/*.feature` — executable Gherkin test suites
- `artifacts/test-results.json` — pass/fail results with triage categories
- `artifacts/coverage-report.md` — requirement coverage summary

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| Gate 0 clearance (openspec locked) | Build phase (generation mode) |
| DevCopilot code lands | InsightOps |
| EvalHarness rubric defined | NexusDeploy |
