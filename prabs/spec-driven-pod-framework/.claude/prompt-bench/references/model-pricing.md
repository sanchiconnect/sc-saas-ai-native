# Model Pricing Reference — PromptBench
## Last updated: 2025-09. Verify against provider pricing pages before sprint.

---

## Anthropic Claude

| Model | Input ($/1M tokens) | Output ($/1M tokens) | Typical latency p95 |
|-------|--------------------|--------------------|---------------------|
| claude-haiku-4-5-20251001 | $0.80 | $4.00 | 300–500ms |
| claude-sonnet-4-20250514 | $3.00 | $15.00 | 500–900ms |
| claude-opus-4 | $15.00 | $75.00 | 800–1500ms |

## OpenAI

| Model | Input ($/1M tokens) | Output ($/1M tokens) | Typical latency p95 |
|-------|--------------------|--------------------|---------------------|
| gpt-4o-mini | $0.15 | $0.60 | 300–600ms |
| gpt-4o | $5.00 | $15.00 | 600–1200ms |
| o3-mini | $1.10 | $4.40 | 1000–3000ms |
| o3 | $10.00 | $40.00 | 2000–8000ms |

## Google Gemini

| Model | Input ($/1M tokens) | Output ($/1M tokens) | Typical latency p95 |
|-------|--------------------|--------------------|---------------------|
| gemini-2.0-flash | $0.10 | $0.40 | 200–400ms |
| gemini-2.5-pro | $1.25 | $10.00 | 500–1000ms |

---

## Cost Calculation Formula

```
cost_per_request = (avg_input_tokens / 1_000_000 × input_rate)
                 + (avg_output_tokens / 1_000_000 × output_rate)

cost_per_1k_requests = cost_per_request × 1000
```

## Model Selection Heuristics

| Task Type | Recommended Model | Rationale |
|-----------|-----------------|-----------|
| Simple classification (≤5 classes) | claude-haiku-4-5 or gpt-4o-mini | Low complexity, cost-optimised |
| Structured extraction (JSON output) | claude-haiku-4-5 | Strong structured output, cheap |
| Complex reasoning (multi-step) | claude-sonnet-4 or gpt-4o | Quality > cost for complex tasks |
| Long document analysis (>20K tokens) | claude-sonnet-4 | Context window + quality |
| Code generation | claude-sonnet-4 | Best code quality per cost |
| Creative content | claude-sonnet-4 or gpt-4o | Highest quality for open-ended tasks |
| Real-time streaming (user-facing) | claude-haiku-4-5 or gpt-4o-mini | Lowest TTFT |

## Sprint Token Budget Guidance

| Sprint size (builder-days) | Recommended token budget | Rationale |
|---------------------------|--------------------------|-----------|
| 6 builder-days (2B × 3d) | 2M tokens | Standard sprint, mixed task complexity |
| 9 builder-days (3B × 3d) | 3M tokens | Larger pod, scale linearly |
| Research/benchmarking sprint | +500K tokens | PromptBench budget allowance |
