# ReviewPilot

The automated PR review layer that executes before the POD Lead's human review. Pre-reviews every PR for spec compliance, acceptance criteria coverage, and convention adherence. Classifies findings as blocking, advisory, or informational. The POD Lead receives only judgment calls — architectural coherence, cross-PR design decisions, and contextual trade-offs.

---

## When to Use

Invoke when an AI Builder opens a pull request, a PR diff is provided for spec-conformance analysis, or the POD Lead requests a review report before merge.

**Trigger phrases:** `review this PR`, `run ReviewPilot`, `check spec conformance for [task_id]`

---

## Inputs

| Input | Required |
|---|---|
| PR diff (changed files + line diffs) | Mandatory |
| `artifacts/openspec.yaml` | Mandatory |
| `.cursorrules` | Mandatory |
| `AGENTS.md` | Mandatory |
| TrustFabric compliance flags | Mandatory |
| `artifacts/ai-manifest.json` | Mandatory |
| `specs/design.md` | Mandatory |

## Outputs

- `artifacts/review-verdict.yaml` — per-requirement PASS / FAIL / PARTIAL / UNTESTABLE verdicts
- Inline review report with blocking and advisory findings

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| DevCopilot submits PR | POD Lead human review |
| TrustFabric validates data contracts | NexusDeploy (review-verdict required) |
