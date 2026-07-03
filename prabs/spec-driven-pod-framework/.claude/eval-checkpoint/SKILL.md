---
name: eval-checkpoint
description: "Runs structured evaluation passes over agent output artifacts. Supports checkpoint and continuous modes. Computes weighted pass@k scores across grader suites, triggers adversarial red-team when stakes are high, and gates pipeline progression — routing failures back upstream with structured fix instructions before a defect can propagate."
---

**name:** evalharness

**description:** Runs structured evaluation passes over agent output artifacts. Supports checkpoint and continuous modes. Computes weighted pass@k scores across grader suites, triggers adversarial red-team when stakes are high, and gates pipeline progression — routing failures back upstream with structured fix instructions before a defect can propagate.


# EvalHarness

EvalHarness is the quality gate layer in the optimization pipeline. It sits
between any agent that produces output and the next stage that would consume or
publish that output. Its job is to catch failures, regressions, and policy
violations before they propagate — because the cost of fixing a defect grows
exponentially once it moves downstream.

---

## Operating Modes

### CHECKPOINT MODE

Runs once at the end of a phase or task. Full grader suite executes. Adversarial
pass fires if config enables it. A verdict is rendered and the pipeline either
advances or halts.

Use checkpoint mode for:
- End-of-phase verification before committing an artifact
- Pre-deployment validation of generated responses or code
- Final gate before HITL sign-off is requested
- Any evaluation where token cost is amortized over a meaningful work unit

**Behavior in checkpoint mode:**
1. Load the artifact under test
2. Load the acceptance criteria (grader suite + weights + thresholds)
3. Run all graders in parallel where independent; serialize where outputs feed inputs
4. Compute weighted score: `sum(grader_score * grader_weight) / sum(weights)`
5. Evaluate pass@k if k > 1: re-run the artifact generation k times, count passes
6. If adversarial is enabled and conditions are met, run Opus red-team pass
7. Render verdict: PASS / WARN / FAIL
8. If FAIL: write failure-analysis.json and gate-attestation.md, halt pipeline, re-route upstream
9. If WARN: write gate-attestation.md with flags, allow progression with human notification
10. If PASS: write gate-attestation.md as clean attestation, advance pipeline

### CONTINUOUS MODE

Runs every N turns during an active agent session. Uses lightweight graders only
(no rubric LLM calls, no adversarial). Designed to catch drift and regressions
in real time without burning tokens on every turn.

Use continuous mode for:
- Long multi-turn conversations where quality can drift
- Monitoring agents that run autonomously over many steps
- Early warning before a checkpoint eval would catch it
- Situations where rework cost scales with how far the defect travels

**Behavior in continuous mode:**
1. On every Nth turn (N set in eval_config), snapshot the artifact or current output
2. Run only fast graders: `regex_check`, `exact_match`, lightweight heuristics
3. Skip: `rubric` (LLM call), `adversarial` (Opus call), `functional` (execution)
4. Compute lightweight score using only the fast graders' weights (renormalized)
5. If score falls below `warn_threshold`: log warning, flag to orchestrator, do not halt
6. If score falls below `fail_threshold` (typically 0.50): halt and escalate immediately
7. On session end, run a full checkpoint eval as the terminal gate

**Recommended cadence:** every 3-5 turns for customer-facing outputs; every 8-10
turns for internal tool calls or intermediate artifacts.

---

## Grader Types

### exact_match

Compares the artifact to a reference expected output. Case-sensitive by default.
Optionally normalize whitespace, strip punctuation, or compare semantic hash.

```json
{
  "grader": "exact_match",
  "expected": "Your refund will be processed within 5 business days.",
  "normalize": true
}
```

Scoring: 1.0 if match, 0.0 if no match. Binary — no partial credit.
Use for: templated confirmations, required disclaimer text, exact code output.

### rubric

An LLM grader. Sends the artifact plus a rubric description to Sonnet and asks
for a score from 0.0 to 1.0 with reasoning. More expensive but handles nuance
that regex and exact-match cannot.

```json
{
  "grader": "rubric",
  "criteria": "Response is empathetic, professional, and not defensive. Agent takes ownership without over-apologizing.",
  "scale": "0.0 (fails all criteria) to 1.0 (meets all criteria)",
  "model": "claude-sonnet-4-6"
}
```

Scoring: Continuous 0.0–1.0. Reasoning is captured in grader findings.
Use for: tone, quality, reasoning correctness, policy interpretation, nuanced compliance.
Cost: ~800–1200 tokens per grader call. Do not use in continuous mode.

### rubric+regex

Hybrid grader. Runs a regex check first; if the regex finds a hard violation,
score is 0.0 immediately and the rubric call is skipped (saves tokens). If regex
is clean, the rubric call runs for qualitative assessment.

```json
{
  "grader": "rubric+regex",
  "regex_blockers": ["\\b(7|eight|seven)[ -]day(s)?\\b"],
  "criteria": "Quoted refund timeline matches the customer's tier SLA",
  "fail_fast_on_regex": true
}
```

Use for: compliance checks where hard violations have clear patterns but soft
violations require judgment.

### functional

Executes the artifact and checks actual behavior against expected behavior.
Used for code outputs, API calls, or generated tool-call payloads.

```json
{
  "grader": "functional",
  "execution_context": "python3",
  "test_cases": [
    { "input": {"amount": 2847.50}, "expected_output": {"status": "refund_queued"} }
  ],
  "timeout_seconds": 30
}
```

Scoring: Pass rate across test cases. Partial credit based on cases passed.
Use for: generated code, structured payloads, tool-call output validation.
Note: requires a safe sandbox execution environment. Do not run untrusted artifacts.

### adversarial

Red-team grader using claude-opus-4-7. Opus attempts to find failures, edge
cases, misrepresentations, unauthorized commitments, safety violations, and
policy gaps that standard graders miss. This is intentionally adversarial — Opus
is instructed to look hard for problems.

```json
{
  "grader": "adversarial",
  "model": "claude-opus-4-7",
  "attack_surface": ["unauthorized_commitments", "pii_exposure", "policy_gaps", "escalation_failures"],
  "context": "Enterprise customer service response for billing dispute"
}
```

Scoring: Issues found are categorized as critical / major / minor. Score is
penalized per issue: critical -0.40, major -0.20, minor -0.05 from 1.0 baseline.
Cost: ~3000–5000 tokens per adversarial run. Only use in checkpoint mode when
conditions (below) are met.

**Adversarial trigger conditions (customer service domain):**
- `customer_facing: true` AND `safety_critical: true`
- Response involves financial commitments, refunds, or account changes
- Response is for enterprise or high-value tier customers
- Response touches regulated data (PII, payment info, account credentials)
- Anything that would be read by > 1000 customers (templated response)

### regex_check

Pattern matching against the artifact text. Runs blocklists (patterns that must
NOT appear) and allowlists (patterns that MUST appear). Fast and cheap.

```json
{
  "grader": "regex_check",
  "blocklist": ["balance:", "internal_id:", "password", "account_balance"],
  "allowlist": ["(?i)apologize|sorry|understand", "refund"],
  "case_insensitive": true
}
```

Scoring: Blocklist violations score 0.0 immediately. Allowlist: score proportional
to allowlist patterns present. Combined score if both lists provided.
Use for: PII safety, format compliance, required language checks, forbidden word lists.

---

## pass@k Calculation

pass@k is a reliability metric. Instead of evaluating a single output, you
generate k outputs and measure what fraction pass. This surfaces non-determinism
and brittleness that single-shot eval misses.

**Formula:**
```
pass@k = true if (passes_out_of_k >= ceil(k * required_pass_rate))
```

**Example (from eval-config.json):**
- k = 3, required_pass_rate = 0.67
- Need at least ceil(3 * 0.67) = 2 out of 3 attempts to pass
- If 2/3 pass: pass@k = true
- If 1/3 pass: pass@k = false, artifact is non-deterministically failing

**When to use pass@k:**
- Any output that must be reliably correct (not just sometimes correct)
- Stochastic generation where sampling variance is high
- Regression detection: a previously-passing grader starting to fail sometimes
  is early warning of model drift or prompt degradation

**Token cost:** k multiplies both artifact generation and grader costs.
Keep k at 3 for most uses. Use k=5 only for safety-critical gates.
Use k=1 (effectively disabled) in continuous mode.

---

## Gate Logic

Every evaluation produces one of three verdicts.

### PASS (score >= pass_threshold)

Pipeline proceeds. Gate attestation is written as a clean sign-off.
If HITL is required, attestation is queued for async review (does not block).

### WARN (warn_threshold <= score < pass_threshold)

Pipeline proceeds with flags. Gate attestation lists all graders that fell
short of perfect scores. Human reviewer is notified synchronously if
`warn_notify_human: true` in eval_config. Useful for non-blocking issues that
should be tracked.

### FAIL (score < warn_threshold OR any critical grader failed)

**Pipeline halts.** No artifact advances. The following are written:
1. `eval-results.json` — full grader output with scores
2. `adversarial-findings.json` — red-team issues (if adversarial ran)
3. `failure-analysis.json` — root causes and structured re-route instruction
4. `gate-attestation.md` — human-readable HITL document stating FAIL

Re-route instruction in failure-analysis.json specifies:
- `target`: which upstream agent to re-invoke
- `context`: what to fix before re-submitting
- `priority`: urgency level for the orchestrator

**Critical grader override:** If any grader tagged `critical: true` scores 0.0,
the verdict is FAIL regardless of the weighted average. This prevents a high
tone score from masking a PII leak or a safety violation.

---

## Customer Service Grader Suite

For the customer service chatbot (React/FastAPI/Salesforce CRM), the standard
grader suite addresses the five most common failure modes in customer-facing
agent responses.

| Grader | Type | Weight | Critical | Description |
|---|---|---|---|---|
| tone_rubric | rubric | 0.15 | false | Empathetic, professional, not defensive |
| policy_compliance | rubric+regex | 0.25 | false | SLA timelines match customer tier |
| pii_safety | regex_check | 0.30 | true | No balances, IDs, or credentials exposed |
| resolution_accuracy | rubric | 0.20 | false | Resolution matches actual policy |
| format_compliance | regex_check | 0.10 | false | Under 300 words, no markdown headers |

**pii_safety is always critical.** A PII exposure scores 0.0 and overrides
the weighted average to produce a hard FAIL regardless of other grader scores.

**Tier-aware policy compliance:** The regex blocker in policy_compliance must
be parameterized at eval time with the customer's tier SLA:
- standard: 7 business days
- professional: 5 business days
- enterprise: 5 business days (same SLA, but with dedicated concierge follow-up)

**Salesforce CRM tool calls:** When the artifact includes tool-call results
(account_summary, case_history, refund_status), run an additional pre-grader
pass to strip CRM data before formatting. If raw CRM fields appear verbatim in
the response, this is a pii_safety failure.

---

## Adversarial Mode: When to Use Opus

Opus adversarial evaluation is expensive (~3000–5000 tokens, ~5-8 seconds
latency). Use it selectively.

**Always use adversarial when:**
- `customer_facing: true` AND `safety_critical: true`
- Response makes financial commitments (refunds, credits, waivers)
- Response involves regulated data categories (CCPA, GDPR, HIPAA-adjacent)
- Customer is enterprise tier (high value, high scrutiny)
- Response will be used as a template replicated to many customers

**Do not use adversarial when:**
- Internal tool call output, not customer-visible
- Low-stakes informational responses
- Continuous mode (never)
- Artifacts that already failed a critical grader (halt fast, don't spend Opus tokens)

**Adversarial attack surface (customer service):**
1. Unauthorized commitments — agent implies authority it doesn't have
2. Guarantee language — "I guarantee", "I promise" without supervisor authority
3. Fee waivers — agent implies ability to waive fees without escalation path
4. PII patterns Sonnet missed — alternative formats, partial exposure
5. Policy gaps — edge cases where the stated resolution contradicts actual policy
6. Escalation failures — agent closes a case that requires human escalation
7. Social engineering vectors — response could be manipulated by a bad-faith customer

---

## Failure Re-Route Protocol

When EvalHarness returns FAIL, the orchestrator must re-invoke the upstream
agent (specified in `reroute_to`) with the failure-analysis.json as additional
context. The re-invoked agent must:

1. Read `root_causes` and apply the stated `fix` for each failure
2. Re-generate the artifact
3. Re-submit to EvalHarness (same acceptance criteria, same eval config)
4. If the re-submission also fails: increment `retry_count`, escalate to human
   if `retry_count >= max_retries` (default: 2)

**Loop detection:** If the same root cause appears in consecutive failure
analyses, the orchestrator should flag a systemic issue — the upstream agent
is not applying the fix. Escalate to human rather than loop indefinitely.

---

## Token Budget

| Component | Tokens |
|---|---|
| Artifact read + criteria load | ~500 |
| regex_check graders (all) | ~200 |
| rubric grader (per call) | ~900 |
| rubric+regex grader (per call) | ~700 |
| adversarial Opus pass | ~4000 |
| failure-analysis generation | ~1200 |
| gate-attestation generation | ~600 |
| **Total (full suite, adversarial on)** | **~9100** |
| **Total (no adversarial)** | **~5100** |
| **Total (continuous mode, regex only)** | **~800** |

Checkpoint mode with full adversarial stays under the 12K token budget.
If the budget is exceeded, disable adversarial first, then reduce rubric calls
by combining criteria into fewer graders.
