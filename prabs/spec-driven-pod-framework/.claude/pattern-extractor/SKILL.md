---
name: pattern-extractor
description: "Mines session transcripts and artifacts for recurring decision patterns, tool call sequences, and reasoning chains. Scores each pattern by confidence, clusters related instincts into candidate skills, drafts SKILL.md stubs, and queues high-confidence candidates for human promotion review."
---

**name:** pattern-extractor

**description:** Mines session transcripts and artifacts for recurring decision patterns, tool call sequences, and reasoning chains. Scores each pattern by confidence, clusters related instincts into candidate skills, drafts SKILL.md stubs, and queues high-confidence candidates for human promotion review.


# PatternExtractor

## Purpose

Every agent session contains tacit knowledge: a lookup sequence that always
works, a phrasing that de-escalates customers, a check that catches 80 % of
billing errors. Left un-captured, this knowledge is re-derived from scratch on
every future session — wasting tokens, time, and consistency.

PatternExtractor systematically harvests that tacit knowledge after each session
and packages it into reviewable, promotable skill candidates.

---

## Extraction Process

### Phase 1 — Mine

Scan the full session transcript and accompanying artifacts for:

1. **Recurring tool call sequences** — tool A always called before tool B before
   tool C, with consistent parameters or parameter shapes.
2. **Repeated reasoning chains** — similar `<thinking>` blocks that lead to the
   same conclusion via the same logical steps.
3. **Consistent phrasing patterns** — response fragments that appear verbatim or
   near-verbatim across multiple turns (apologies, escalation phrases,
   formatting conventions).
4. **Decision heuristics** — if-then rules applied consistently (e.g. "if
   account lookup fails → retry with email").
5. **Artifact patterns** — changes committed to templates, prompts, or configs
   that encode a generalizable rule.

For each candidate, record:
- `pattern_id` — snake_case identifier
- `pattern_type` — one of: `tool_sequence | reasoning_chain | phrasing | decision_heuristic | artifact`
- `occurrences` — count of distinct turns/events where the pattern appeared
- `raw_evidence` — verbatim excerpts from the transcript (max 3, trimmed to 200 chars each)

### Phase 2 — Score

Assign a confidence score in [0, 1] using:

```
confidence = min(1.0,
    (occurrences - 1) * 0.25
    + consistency_score * 0.5
)
```

Where `consistency_score` is the fraction of occurrences that match the
canonical form without deviation (0.0–1.0). A pattern seen once can score at
most 0.5 × consistency; a pattern seen 5 times with perfect consistency scores
1.0 × min(1.0, 1.0 + 0.5) = capped at 1.0.

Interpretation:

| Score    | Meaning                                      | Action               |
|----------|----------------------------------------------|----------------------|
| >= 0.75  | High confidence — strong evidence            | Add to promotion queue |
| 0.50–0.74 | Moderate — more sessions needed             | Store as instinct; watch |
| < 0.50   | Low — possibly one-off or coincidental       | Store as instinct only; do not queue |

### Phase 3 — Cluster

Group patterns with overlapping triggers or intent into **candidate skills**:

1. Compute pairwise similarity between pattern descriptions using keyword
   overlap (Jaccard ≥ 0.4 → related).
2. If two or more low-confidence instincts (each < 0.75) together cover the
   same workflow, their combined confidence may reach the promotion threshold:
   `cluster_confidence = 1 - product(1 - p.confidence for p in cluster)`
3. Check the existing skill library for overlaps. If a candidate substantially
   overlaps an existing skill (trigger match + > 60 % step overlap), flag as
   `OVERLAP` rather than a new skill — suggest enhancing the existing one.

### Phase 4 — Draft

For each pattern (or cluster) with `confidence >= 0.50`, generate a draft
`SKILL-<pattern_id>-candidate.md` with the following structure:

```markdown
---
status: CANDIDATE
confidence: <score>
evidence: <N> observations across <M> sessions
review_required: true
---
# <Skill Name>
## Trigger
<When to apply this skill>
## Instructions
<Step-by-step, imperative voice>
## Examples
<1–2 concrete examples from the evidence>
## Caveats
<Known edge cases or failure modes>
```

### Phase 5 — Queue

Build `promotion-queue.json`:

- **Ready for promotion** (`confidence >= 0.75`): include full draft path,
  confidence, evidence summary, overlap notes, and reviewer checklist.
- **Needs more evidence** (`0.50 <= confidence < 0.75`): include instinct stub,
  what additional sessions would confirm it, and a suggested re-evaluation date.
- **Instinct only** (`confidence < 0.50`): record in catalogue; do not surface
  in queue unless requested.

---

## Promotion Threshold

| Threshold | Rule                                                                |
|-----------|---------------------------------------------------------------------|
| >= 0.75   | Add to `promotion-queue.json` as **ready** candidate               |
| 0.50–0.74 | Add to queue as **needs more evidence** (not yet promotable)        |
| < 0.50    | Store in `pattern-catalogue.json` as instinct only; no queue entry  |

A human reviewer must explicitly approve before any candidate is copied into the
live skill library. No automatic promotion.

---

## Domain Patterns (Customer Service Chatbot)

The following patterns are known to recur in the customer service domain and
should be recognised on first occurrence rather than requiring multiple sessions:

### Billing Lookup Sequence
When a customer raises a billing issue (dispute, double charge, unexpected
amount), the reliable lookup order is:
1. `lookup_customer(identifier)` — establish identity
2. `get_cases(customer_id)` — check for open/recent support cases
3. `get_billing_history(customer_id, days=30)` — retrieve recent charges

Skipping step 2 misses cases already in progress; skipping step 1 breaks the
audit trail. This sequence appears in the existing library as `crm_lookup_order`
and should be checked for overlap before promoting a new skill.

### Double-Charge Check
When a customer mentions "double charge", "charged twice", or "duplicate
transaction", immediately scope `get_billing_history` to the last 30 days and
filter for entries with identical amounts on consecutive dates. Do not ask the
customer for the date first — the lookup is fast and eliminates the need for the
clarifying question.

### Monetary Amount Formatting
Always render monetary amounts as `$X.XX USD` (dollar sign, two decimal places,
space, ISO currency code). Never use `$X`, `X dollars`, or locale-specific
formatting. This ensures downstream parsing by the CRM system and consistent
customer experience.

### Apologise Before Bad News
Before delivering information the customer will experience as negative (claim
denied, charge valid, no refund available), open with a genuine acknowledgement:
"I understand this is frustrating" or "I'm sorry to hear you're experiencing
this." Skipping this step is correlated with escalation events.

### Escalation Phrase
When a supervisor or specialist is required, use exactly:
> "I want to make sure you receive the best assistance — let me connect you with
> a specialist who can resolve this directly."

Deviating from this phrasing (e.g., "I'll transfer you") correlates with
lower first-contact-resolution scores in the quality review data.

---

## Anti-Pattern Detection

During Phase 2 scoring, check each pattern against the session's quality
outcome:

1. Retrieve the session quality flag from the artifact metadata
   (`session_quality_failure: true/false`).
2. If a pattern appears in sessions that are also flagged as quality failures,
   increment the pattern's `failure_session_count`.
3. Compute `failure_rate = failure_session_count / sessions_observed`.
4. If `failure_rate >= 0.40`, flag the pattern as `POTENTIAL_ANTI_PATTERN` and
   add a warning to its queue entry:

```
WARNING: This pattern was present in X% of sessions that resulted in
quality failures. Review whether the pattern causes or merely correlates
with failures before promoting.
```

Anti-patterns are never auto-promoted regardless of confidence score. A human
reviewer must explicitly override the flag to allow promotion.

---

## Running PatternExtractor

### Invocation

```
Input files:
  input/session-transcript.md        — the session to analyse
  input/session-artifacts.json       — git diff and artifacts
  input/existing-skill-library.json  — current live skill library

Output files (written by agent):
  output/pattern-catalogue.json
  output/SKILL-<id>-candidate.md     — one per promotable pattern
  output/promotion-queue.json
  output/extraction-report.json
```

### When to Run

Run PatternExtractor after every session where:
- The session lasted > 10 turns, OR
- The agent used 3 or more distinct tool calls, OR
- A quality reviewer flagged the session for follow-up

For very short sessions (< 5 turns, single tool call), skip extraction to avoid
noise inflation.

### Human Review Workflow

1. Open `output/promotion-queue.json`.
2. For each **ready** candidate:
   a. Read the draft `SKILL-<id>-candidate.md`.
   b. Verify the pattern generalises beyond this session (ask: "Would I want
      every future agent run to follow this?").
   c. Check the overlap note — if flagged, open the existing skill and decide:
      enhance vs. new.
   d. Check for anti-pattern flags. If present, investigate before promoting.
   e. If approved: copy the candidate `.md` into the live skill library,
      remove the `status: CANDIDATE` header, and update
      `existing-skill-library.json` with the new entry.
   f. If rejected: add a `rejection_reason` to the queue entry and set
      `status: REJECTED` — this prevents the same pattern from being
      re-queued in future runs without new evidence.

3. For **needs more evidence** candidates:
   - No action required today.
   - After 3 additional sessions, re-run PatternExtractor; the accumulated
     evidence will re-score the pattern.

---

## Efficiency Rationale

Each promoted pattern removes future re-derivation. Back-of-envelope for this
domain:

- `billing_lookup_sequence`: 3 occurrences/session × ~2 reasoning turns saved
  per use × ~500 tokens/turn = **~3 000 tokens saved per session** once promoted.
- `escalation_phrase`: eliminates a phrasing decision (typically 1 retry) =
  **~200 tokens saved per escalation**.

Over 100 sessions with 5 billing queries each, `billing_lookup_sequence` alone
saves ~150 000 tokens — roughly 10 full PatternExtractor invocations.

---

## Limitations

- **One-off hacks encoded as best practice.** If a session used an unusual
  approach because of a one-time system outage, PatternExtractor cannot
  distinguish this from a genuine best practice. The human review gate is the
  primary defence.
- **Single-session bias.** Confidence scores derived from one session are
  upper-bounded by the formula; the threshold is calibrated to require at least
  two distinct sessions for automatic promotion. Do not override this without
  good reason.
- **Phrasing drift.** Near-duplicate phrases are detected by fuzzy match, but
  semantic equivalents with different wording may be missed. Reviewers should
  look for intent, not just lexical repetition.
- **No causal inference.** Correlation between a pattern and good/bad outcomes
  is detected; causality is not proven. Anti-pattern flags are warnings, not
  verdicts.
