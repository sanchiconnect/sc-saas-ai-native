# PromptBench

Benchmarks AI feature prompts before they enter production. Tests 2–5 candidate prompt variants against a representative query sample across multiple models (Claude Haiku/Sonnet/Opus, GPT-4o, GPT-4o-mini), measuring quality, latency, and cost. Delivers a ranked recommendation with NFR pass/fail evidence.

---

## When to Use

Invoke when an AI Builder has implemented an AI feature with candidate prompts, or when the POD Lead needs model selection evidence before the Release gate.

**Trigger phrases:** `benchmark this prompt`, `run PromptBench`, `compare these prompt variants`

---

## Inputs

| Input | Required |
|---|---|
| Candidate prompt variants (2–5) | Mandatory |
| Query sample set (10–50 queries) | Mandatory |
| `artifacts/openspec.yaml` | Mandatory |
| Target model list | Mandatory |
| Evaluation criteria | Mandatory |

## Outputs

- `artifacts/prompt-bench-results.yaml` — ranked prompt × model matrix with quality, latency, and cost scores
- `artifacts/prompt-bench-nfr-evidence.yaml` — NFR pass/fail evidence for NexusDeploy gate

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| DevCopilot generates AI feature prompts | NexusDeploy (provides NFR evidence) |
| | PerformanceOptimizer (provides routing calibration) |
