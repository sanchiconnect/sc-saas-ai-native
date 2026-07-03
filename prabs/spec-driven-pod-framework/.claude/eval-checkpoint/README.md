# EvalHarness

Verification loops, graders, and quality gates for the AI agent optimization layer.

EvalHarness catches failures before they propagate. It sits between any agent
that produces output and any downstream stage that would consume or publish that
output. The cost of a defect grows with distance — a bad response stopped at the
gate costs a re-generation; the same response delivered to a customer costs
reputation, regulatory exposure, and churn.

---

## How to Build Effective Graders

Graders are the core unit of EvalHarness. A weak grader suite produces false
confidence. A well-designed suite catches real defects cheaply.

### Start with a failure taxonomy

Before writing a single grader, list the 5-10 most common failure modes for
your domain. For customer service responses, these were: PII overshare, wrong
SLA, unauthorized commitments, tone failures, and format violations. Every
grader should map to at least one failure mode. If you cannot name the failure
mode a grader catches, the grader is probably too generic to be useful.

### Use the cheapest grader that is sufficient

Graders have a cost hierarchy:

```
regex_check (~50 tokens) < exact_match (~50 tokens) < rubric (~900 tokens) < adversarial (~4000 tokens)
```

Always ask: can a regex catch this? If yes, use regex. Only escalate to a rubric
call when the failure mode requires judgment that pattern matching cannot provide.
Reserve adversarial for the small set of issues that require creative attack
thinking to surface.

Common traps:
- Using a rubric grader for a check that a regex can do (e.g., "response is under
  300 words" — just count words)
- Using adversarial mode for every response because it feels safer (it isn't —
  adversarial adds latency and token cost, which you will stop paying after a
  few weeks of no findings)
- Writing graders that overlap heavily (e.g., tone_rubric and resolution_accuracy
  both partially measuring "professionalism" — consolidate)

### Weight graders by failure consequence, not importance

Grader weight should reflect the cost of that failure type reaching production,
not how much you care about the criterion in the abstract. PII safety is weighted
0.30 not because quality matters three times as much as tone, but because a PII
failure has 10x the downstream cost of a slightly off-tone sentence. Weight
calibration is a risk prioritization exercise.

### Mark critical graders explicitly

If a single failure of a grader should halt the pipeline regardless of all other
scores, mark it `"critical": true`. A high tone score cannot compensate for a
PII leak. The weighted average exists for soft trade-offs; critical overrides
exist for hard blockers. Use them for:
- PII and data safety violations
- Security or compliance blockers
- Any check where a 0.0 score indicates the artifact is legally or ethically
  undeliverable

### Combine grader types with rubric+regex

The rubric+regex hybrid is underused. It costs roughly half what a standalone
rubric call costs when the fast path triggers. For any grader that has clear
hard violations (detectable by regex) but also requires qualitative judgment
(needs rubric) for the non-obvious cases, rubric+regex is the right choice.
The fail_fast_on_regex path skips the LLM call entirely when the pattern fires.

### Test your graders on known-bad artifacts

Before deploying a grader suite to production, run it against a set of
deliberately defective artifacts. Verify each grader catches the failure it
was designed to catch. It is common to discover that a regex is too narrow
(misses a variant of the pattern) or a rubric criteria is too vague
(scores 0.7 on something that should score 0.0). The `test-artifact.md` in this
directory is an example of a known-bad artifact with two deliberate defects
built in — use it as a template for building your own regression test set.

---

## When to Use Adversarial (Opus) vs. Standard (Sonnet)

Adversarial mode is not a stronger version of standard evaluation. It is a
different kind of evaluation — creative, goal-directed attack rather than
criteria-based scoring.

### Use adversarial when:

**The artifact makes commitments.** Any response that commits the company to a
financial, legal, or service-level action is worth adversarial review. Sonnet
rubric graders evaluate whether the response looks correct. Opus adversarial
asks: "How could this commitment be weaponized or misread?"

**The artifact reaches high-value or regulated customers.** Enterprise customers
have more leverage and more sophisticated ability to use your words against you.
Regulated domains (finance, healthcare, legal) have compliance exposure that
general-purpose rubric graders may not catch.

**The artifact will be templated.** A single response to one customer can be
absorbed. A response template used for 10,000 customers amplifies every defect
by 10,000. Adversarial review before templating is cheap at that scale.

**You have found zero adversarial findings for several consecutive runs.** Zero
findings is not evidence that adversarial mode is no longer needed — it may mean
your standard graders have improved to the point where only subtle issues remain,
and those are exactly what adversarial catches.

### Do not use adversarial when:

**Any critical grader has already scored 0.0.** If pii_safety fails, halt
immediately. Do not spend 4,000 tokens confirming a verdict that is already
decided. The `skip_adversarial_if_critical_already_failed` config option
implements this.

**The artifact is internal only.** Tool call outputs, intermediate agent state,
internal routing messages — if no human customer will read it, adversarial review
adds no value.

**You are in continuous mode.** Continuous mode is designed for lightweight
monitoring between checkpoints. The adversarial pass is exclusively a checkpoint
operation.

**You are over budget.** If the eval is exceeding its token budget, disable
adversarial first. A well-designed standard grader suite with accurate weights
and critical overrides will catch 90% of defects. Adversarial catches the
remaining 10% that are subtle and creative. If budget forces a trade-off,
take the coverage reduction from adversarial, not from the standard graders.

---

## Integrating Continuous vs. Checkpoint Evaluation

Checkpoint and continuous evaluation are complementary, not alternatives.

### The two-mode model

**Continuous mode** runs during an active agent session on a cadence (every N
turns). It uses only fast graders (regex_check, exact_match). Its job is early
warning — catching drift before it accumulates. Think of it as a smoke detector.
It will not tell you the precise source of the fire, but it tells you something
is wrong early enough to avoid a major incident.

**Checkpoint mode** runs at the end of a phase, before an artifact is committed
or delivered. It uses the full grader suite. Its job is final gate — ensuring
nothing proceeds that shouldn't. Think of it as the structural inspection before
occupancy. It is thorough, it is slow relative to continuous, and it is the
definitive record.

### Recommended integration pattern

```
[Agent generates turn N output]
        |
        v
[Continuous eval: fast graders only]
        |
    WARN?  --> log warning, flag to orchestrator, continue
        |
    FAIL?  --> immediate halt, escalate
        |
        v
[Agent continues to end of phase]
        |
        v
[Checkpoint eval: full grader suite + adversarial if conditions met]
        |
    PASS  --> advance pipeline, write gate attestation
    WARN  --> flag + proceed, notify human
    FAIL  --> halt, write failure analysis, reroute upstream
```

### Choosing your continuous eval cadence

Every 3-4 turns: high-stakes real-time conversations (live chat, voice AI
transcription). Quality drift in these contexts is fast and costly.

Every 6-8 turns: batch response generation, email drafting, report generation.
Drift is slower; the checkpoint at the end is the primary gate.

Every 10+ turns: internal agent workflows, tool call chains, non-customer-facing
pipelines. Use continuous as a very lightweight health check.

Never every turn: the token cost makes this impractical, and continuous mode
fast graders will produce false positives if run too frequently on in-progress
artifacts.

---

## How to Reduce Eval Cost While Maintaining Coverage

Evaluation is not free. A full checkpoint run with adversarial costs ~10,000
tokens. At high volume, this adds up. Here are the cost reduction levers in
order of impact.

### 1. Disable adversarial mode on passing streaks

Track your adversarial findings rate. If you run 50 consecutive checkpoint evals
and adversarial finds zero material issues beyond what standard graders caught,
your standard graders are covering the attack surface well. Reduce adversarial
to every 5th checkpoint run ("adversarial sampling") rather than every run.
Maintain the ability to re-enable adversarial immediately if the environment
changes (new model, new prompt, new domain).

### 2. Use fail_fast_on_regex in rubric+regex graders

Every rubric call skipped by a regex fail saves ~700 tokens. For graders where
hard violations are common (policy compliance in billing, PII in CRM-adjacent
responses), the fail_fast path fires frequently and the savings are real. Design
your blocklist patterns to be broad enough to catch true violations but specific
enough to avoid false positives that would skip a necessary rubric call.

### 3. Consolidate rubric criteria

Three rubric graders with overlapping criteria cost 3x a single well-scoped
rubric grader. Before adding a new rubric grader, check whether its criteria
can be added to an existing rubric as an additional dimension. The trade-off is
interpretability (a single rubric score covers multiple criteria) vs. cost
(separate graders are cheaper to debug). For production pipelines at scale,
consolidated rubric graders with multi-dimensional scoring are often the right
call.

### 4. Scale eval depth with artifact risk

Not all artifacts warrant a full grader suite. Define a risk tier:

- **Tier 1 (High):** Customer-facing, financial commitments, enterprise accounts,
  regulated data. Run full suite + adversarial.
- **Tier 2 (Medium):** Customer-facing, informational only, no financial
  commitments. Run standard suite, no adversarial.
- **Tier 3 (Low):** Internal artifacts, tool call outputs, intermediate state.
  Run regex graders only. Skip rubric and adversarial entirely.

Most pipelines have a mix. Routing to the appropriate eval tier per artifact
type can cut average eval cost by 40-60% without reducing coverage where it
matters.

### 5. Cache rubric grader calls for identical inputs

If the same artifact is re-evaluated (e.g., in a pass@k loop with a deterministic
generator), rubric graders on the same input will return the same score. Cache
rubric results keyed on (artifact_hash, grader_id, criteria_hash). This is
particularly valuable in pass@k evaluation where k=3 with the same artifact.

### 6. Short-circuit on critical failure

If a critical grader scores 0.0 on the first grader to run, halt the remaining
graders immediately. The verdict is FAIL regardless of what the other graders
would score. Order your graders from cheapest to most expensive, with critical
graders running first. Running regex_check graders before rubric graders
implements this naturally — a PII safety regex fail stops the eval before any
Sonnet calls are made.

---

## File Structure

```
skills/EvalHarness/
  SKILL.md                          # Skill definition, mode specs, grader reference
  README.md                         # This file — operational guide
  input/
    test-artifact.md                # Sample customer service response (known-bad)
    acceptance-criteria.json        # Full grader suite for customer service domain
    eval-config.json                # Mode, thresholds, adversarial config
  output/
    eval-results.json               # Per-grader scores and weighted verdict
    adversarial-findings.json       # Opus red-team findings
    failure-analysis.json           # Root causes and reroute instructions
    gate-attestation.md             # Human-readable HITL sign-off document
```

---

## Quick Reference: Grader Selection

| Failure Mode | Recommended Grader | Cost |
|---|---|---|
| PII/sensitive data exposure | regex_check | Low |
| Format constraints (length, structure) | regex_check | Low |
| Required language / disclaimers | regex_check or exact_match | Low |
| Tone and empathy | rubric | Medium |
| Policy compliance (with hard violations) | rubric+regex | Medium |
| Factual accuracy / resolution correctness | rubric | Medium |
| Code / structured output behavior | functional | Medium |
| Unauthorized commitments | adversarial | High |
| Social engineering vectors | adversarial | High |
| Novel policy gaps | adversarial | High |
| Subtle guarantee language | adversarial or rubric | Medium-High |
