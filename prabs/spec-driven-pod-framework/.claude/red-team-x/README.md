# RedTeamX

Subjects every AI-generated component to systematic adversarial attack before deployment. Covers prompt injection, jailbreaks, PII extraction probes, role confusion, and boundary manipulation — the attack surface that functional tests cannot reach. A component that passes Guardian's functional tests but fails RedTeamX is not releasable.

---

## When to Use

Invoke during the Validate phase after build is complete to adversarially test AI-facing components.

**Trigger phrases:** `adversarial testing`, `red team`, `attack testing`, `prompt injection test`, `RedTeamX`

---

## Inputs

| Input | Required |
|---|---|
| `artifacts/openspec.yaml` | Mandatory |
| `artifacts/ai-manifest.json` | Mandatory |
| `artifacts/eval-rubric.yaml` | Mandatory |
| Source prompts / handlers (`src/`) | Mandatory |
| `references/adversarial-vector-library.yaml` | Mandatory |
| `artifacts/policy-catalogue.yaml` | Optional |

## Outputs

- `artifacts/adversarial-test-suite.json` — adversarial test results with pass/fail per attack vector
- Blocking gate report for any critical safety failures

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| EvalHarness rubric defined | InsightOps |
| Build phase complete | Release phase |
