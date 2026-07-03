---
name: prompt-bench
description: "PromptBench benchmarks AI feature prompts before they enter production, preventing the costly failure mode of discovering a suboptimal prompt in live operations. For a sprint delivering AI-native features, the quality, cost, and latency of each prompt is a product decision — PromptBench makes that decision data-driven."
---

# PromptBench — SKILL.md
## SpecPod Build Phase · Agent B-06
**Version:** 2.1.0 | **Model:** claude-haiku-4-5-20251001 | **Token Budget:** ~40K

---

## Purpose
PromptBench benchmarks AI feature prompts **before they enter production**, preventing the costly failure mode of discovering a suboptimal prompt in live operations. For a sprint delivering AI-native features, the quality, cost, and latency of each prompt is a product decision — PromptBench makes that decision data-driven.

A typical sprint with PromptBench: AI Builders propose 2–3 prompt variants per AI feature; PromptBench runs each against a representative query sample, measures quality + latency + cost, and delivers a ranked recommendation with NFR pass/fail evidence. Optimal model selection at build time reduces per-sprint LLM costs by 30–60%.

**Multi-provider scope:** PromptBench evaluates prompts across Claude (Haiku/Sonnet/Opus), OpenAI (GPT-4o/GPT-4o-mini/o3-mini), and other providers as configured. Provider selection is independent of the agentic framework's internal model choices.

---

## Activation Triggers
- An AI Builder has implemented an AI feature with one or more candidate prompts
- POD Lead needs model selection evidence before Release gate
- A prompt variant is suspected of failing NFR latency or quality thresholds
- Prior sprint introduced prompt regression — benchmarking baseline needed
- Explicit invocation: *"benchmark this prompt"*, *"run PromptBench"*, *"compare these prompt variants"*

---

## Inputs

| Input | Source | Role |
|-------|--------|------|
| Candidate prompt variants (2–5) | AI Builder | The prompts under evaluation |
| Query sample set (10–50 queries) | POD Lead curated | Representative production queries for this feature |
| `artifacts/openspec.yaml` | Phase 3 | NFR targets: accuracy threshold, latency p95, cost per request |
| Target model list | POD Lead or default | Which models to test against (e.g. claude-haiku, gpt-4o-mini, claude-sonnet) |
| Evaluation criteria | POD Lead or derived from spec | How to score quality: rubric, ground truth labels, or LLM-as-judge |

**Critical requirement:** The POD Lead is responsible for curating the query sample set. PromptBench cannot generate a representative sample — it can only benchmark against what it receives. Small or unrepresentative samples produce misleading rankings.

---

## Elicitation Protocol
PromptBench requires structured input. Ask the following questions if any are missing:

1. *"Please provide your candidate prompt variants. Format each as: `VARIANT-[N]: [full system prompt + user prompt template]`"*
2. *"What is the query sample set? Please provide 10–50 representative user queries for this feature. These should reflect the actual distribution of inputs the feature will receive in production."*
3. *"What models should I test? Default is: claude-haiku-4-5, claude-sonnet-4, gpt-4o-mini, gpt-4o. Remove any you don't have API access to, or add others."*
4. *"How should I score quality? Options: (a) LLM-as-judge with criteria you define, (b) exact-match against ground truth labels you provide, (c) human-defined rubric (1–5 scale with criteria). Which do you prefer?"*
5. *"What are the NFR thresholds from `openspec.yaml`? (Accuracy %, latency p95 ms, max cost per 1K requests)"*

---

## Processing Logic

### Step 1 — Benchmark Matrix Construction
Build an evaluation matrix:
```
Row: query from sample set
Column: prompt_variant × model combination
Cell: response + metrics (quality_score, latency_ms, input_tokens, output_tokens, cost_usd)
```

### Step 2 — Execute Benchmark Runs
For each `(variant, model, query)` combination:
1. Run the prompt against the model (use actual API calls where possible; simulate with recorded responses when budget-constrained)
2. Record: `latency_ms`, `input_tokens`, `output_tokens`, `cost_usd`
3. Score quality using the selected evaluation method:
   - **LLM-as-judge:** Send response to a judge model with a scoring rubric; record 1–5 score
   - **Exact match:** Compare response to ground truth label; binary 0/1
   - **Rubric:** Apply defined criteria; score 1–5 per criterion, average

### Step 3 — Aggregate Metrics
Per `(variant, model)` pair, aggregate across all queries:
- `quality_avg` — mean quality score
- `quality_p10` — 10th percentile (worst-case quality)
- `latency_p50`, `latency_p95` — median and 95th percentile latency
- `cost_per_1k` — cost per 1,000 queries (extrapolated)
- `nfr_quality_pass` — bool: does `quality_avg ≥ openspec threshold`?
- `nfr_latency_pass` — bool: does `latency_p95 ≤ openspec threshold`?
- `nfr_cost_pass` — bool: does `cost_per_1k ≤ openspec threshold`?

### Step 4 — Ranking
Rank all `(variant, model)` pairs on three dimensions:
1. **Best quality** — highest `quality_avg` among NFR-passing combinations
2. **Best cost** — lowest `cost_per_1k` among NFR-passing combinations
3. **Best balanced** — highest composite score: `0.5 × quality_norm + 0.3 × cost_norm_inv + 0.2 × latency_norm_inv`

### Step 5 — Winner Recommendation
Recommend the **best balanced** option as the default unless POD Lead has a specific priority constraint. Flag all combinations that fail any NFR threshold — these cannot enter production.

---

## Outputs

### Primary: `prompt-bench-report.md`
```markdown
# PromptBench Report
**Feature:** User Intent Classification | **Sprint:** SP-007
**Date:** 2025-09-17 | **Sample size:** 40 queries | **Variants tested:** 3 | **Models tested:** 4

## Recommended Winner: VARIANT-2 × claude-haiku-4-5
**Rationale:** Passes all NFRs. Best balanced score. 68% cheaper than VARIANT-1 × gpt-4o with only 3% quality reduction.

## NFR Thresholds (from openspec.yaml)
| NFR | Threshold |
|-----|-----------|
| Quality accuracy | ≥ 85% |
| Latency p95 | ≤ 800ms |
| Cost per 1K requests | ≤ $0.50 |

## Results Matrix
| Variant | Model | Quality Avg | Quality P10 | Latency P95 | Cost/1K | NFR Pass | Balanced Score |
|---------|-------|-------------|-------------|-------------|---------|----------|----------------|
| VARIANT-2 | claude-haiku-4-5 | 91% | 84% | 420ms | $0.08 | ✅ ALL PASS | 0.87 |
| VARIANT-1 | claude-sonnet-4 | 94% | 91% | 680ms | $0.25 | ✅ ALL PASS | 0.79 |
| VARIANT-2 | gpt-4o-mini | 88% | 80% | 550ms | $0.12 | ✅ ALL PASS | 0.76 |
| VARIANT-3 | claude-haiku-4-5 | 82% | 71% | 380ms | $0.06 | ❌ QUALITY | — |
| VARIANT-1 | gpt-4o | 96% | 93% | 740ms | $0.52 | ❌ COST | — |

## Variant Descriptions
- **VARIANT-1:** Verbose system prompt with 5 examples (few-shot)
- **VARIANT-2:** Concise system prompt with 2 examples + chain-of-thought instruction
- **VARIANT-3:** Zero-shot minimal prompt

## Failure Analysis
- VARIANT-3 fails quality NFR: insufficient context for low-frequency query types (queries 12, 28, 35 scored 1/5)
- VARIANT-1 × gpt-4o fails cost NFR: $0.52/1K exceeds $0.50 threshold by 4%

## Model Routing Recommendation
Use **claude-haiku-4-5** for this feature. Quality is within 3% of Sonnet at 68% lower cost. Reserve Sonnet for features where quality p10 < 85% on Haiku.
```

### Secondary: NFR pass/fail evidence file (for Release gate)
`prompt-bench-nfr-evidence.yaml` — structured pass/fail per variant/model combination, consumed by NexusDeploy.

---

## Limitations & Escalation
- Benchmark quality **depends entirely on sample set representativeness**. A 10-query sample with no edge cases produces misleading rankings. POD Lead must curate at minimum 20 queries including known difficult cases.
- Does not run real API calls by default (budget management). When real execution is required, POD Lead must explicitly confirm: *"Run live API calls for this benchmark."*
- LLM-as-judge scoring introduces evaluator bias. For high-stakes features, supplement with human-reviewed ground truth labels.

---

## Integration Points
| Agent | Direction | Data Exchanged |
|-------|-----------|----------------|
| PerformanceOptimizer | Downstream | Benchmark results inform sprint-level model routing decisions |
| DevCopilot | Upstream | DevCopilot may submit prompts for benchmarking before integrating into feature code |
| NexusDeploy | Downstream | NFR evidence required for deploy manifest |
| KnowledgeMesh | Upstream | Retrieves NFR targets and prior sprint benchmark baselines |

---

## References
- `references/evaluation-methods.md` — LLM-as-judge rubric, exact-match, and rubric scoring guides
- `references/model-pricing.md` — Current provider pricing for cost calculations
- `references/sample-set-guidance.md` — How to build a representative query sample set
- `sample_input/sample-benchmark-request.yaml` — Example benchmark input
- `sample_output/sample-bench-report.md` — Worked example output
