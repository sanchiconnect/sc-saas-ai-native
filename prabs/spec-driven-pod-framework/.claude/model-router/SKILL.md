---
name: model-router
description: "Routes each task step to the least expensive model capable of meeting its quality bar. Classifies reasoning depth across six dimensions, applies budget-pressure overrides from BudgetGovernor, and escalates automatically when a quality gate fails. The single largest cost lever in the optimization layer — proper routing typically cuts model"
---

**name:** model-router

**description:** Routes each task step to the least expensive model capable of meeting its quality bar. Classifies reasoning depth across six dimensions, applies budget-pressure overrides from BudgetGovernor, and escalates automatically when a quality gate fails. The single largest cost lever in the optimization layer — proper routing typically cuts model spend several-fold.


# ModelRouter Skill

## Overview

ModelRouter runs as a lightweight classifier on `claude-haiku-4-5`. For every
task step submitted to the optimization layer, it produces a `(model, rationale,
escalation_path)` triple. Because Haiku costs roughly 30x less than Opus per
token, routing one step correctly can offset the classifier's entire cost.

---

## Classification Framework

### Six Complexity Dimensions

Score each dimension 1–10, then compute `weighted_composite_score` using the
weights below. The composite drives the tier decision unless overrides apply.

| Dimension              | Weight | Description |
|------------------------|--------|-------------|
| `reasoning_depth`      | 0.30   | Inferential steps required from input to output. 1 = direct lookup; 10 = multi-layered causal reasoning with unresolved ambiguity. |
| `ambiguity_level`      | 0.15   | Degree of underspecification in the task. 1 = fully specified; 10 = open-ended with many valid interpretations. |
| `domain_expertise`     | 0.20   | Breadth of specialized knowledge required. 1 = common knowledge; 10 = cross-domain expert synthesis (legal + technical + policy). |
| `multi_step_planning`  | 0.15   | Whether the task requires sequencing sub-goals with dependency tracking. 1 = single atomic action; 10 = coordinated multi-phase plan. |
| `safety_criticality`   | 0.10   | Harm potential of a wrong answer. 1 = trivially reversible; 10 = legal liability, financial loss, or regulatory breach. |
| `output_precision`     | 0.10   | Tolerance for errors or approximation. 1 = any reasonable answer acceptable; 10 = exact, verifiable, zero-error required. |

**Composite formula:**

```
weighted_composite = (reasoning_depth * 0.30) +
                     (ambiguity_level * 0.15) +
                     (domain_expertise * 0.20) +
                     (multi_step_planning * 0.15) +
                     (safety_criticality * 0.10) +
                     (output_precision * 0.10)
```

---

## Routing Rules

### Tier Thresholds (baseline, before overrides)

| Composite Score | Assigned Model         | Tier Label  |
|-----------------|------------------------|-------------|
| 1.0 – 3.4       | `claude-haiku-4-5`     | MECHANICAL  |
| 3.5 – 6.4       | `claude-sonnet-4-5`    | STANDARD    |
| 6.5 – 10.0      | `claude-opus-4-5`      | DEEP        |

### MECHANICAL — Route to Haiku

Use Haiku when the task requires no inferential chaining and a correct answer
can be produced by pattern matching or table lookup.

**Canonical step types:**
- Intent classification against a fixed taxonomy (e.g., "Is this a billing
  inquiry, technical issue, or cancellation request?")
- Simple field lookup (account status, order number, subscription tier)
- Format conversion (date normalization, address standardization, unit conversion)
- Regex or template generation from a clear spec
- Boolean / yes-no decisions with explicit criteria already provided
- Template filling where all slots map directly to provided context
- Call transcript transcription summarization (extract facts, no interpretation)

**Signal patterns:**
- Input contains all information needed; no retrieval or synthesis required
- Output is short and verifiable against the input
- The same answer would be given by any junior support agent reading the same data
- Zero ambiguity about what "correct" means

---

### STANDARD — Route to Sonnet

Use Sonnet when the task requires multi-turn reasoning, moderate synthesis, or
tool orchestration, but does not demand expert cross-domain judgment.

**Canonical step types:**
- Multi-turn conversational reasoning (tracking context across several exchanges)
- Code generation for standard patterns (CRUD endpoints, form validation logic)
- Document summarization with interpretation (extracting intent, not just facts)
- Tool orchestration — deciding which tools to call and in what order
- Standard policy application to a described scenario
- Upsell recommendation based on account history and product catalog
- Refund eligibility determination against a documented policy
- Sentiment analysis with nuanced polarity (sarcasm, ambivalent feedback)
- Data conflict identification across two systems (detect discrepancies, flag for
  human review — not root-cause analysis)

**Signal patterns:**
- Requires holding state or context across multiple reasoning steps
- Multiple valid approaches exist; the model must select the best one
- Output involves generating novel text that must be coherent and on-brand
- Task involves a defined policy but requires applying judgment to edge cases

---

### DEEP — Route to Opus

Reserve Opus for tasks where an error has material consequences and the
reasoning requires expert-level synthesis across multiple knowledge domains.

**Canonical step types:**
- Adversarial review (find flaws in an argument or attack surface in a plan)
- Compliance and legal analysis (GDPR, PCI-DSS, TCPA, consumer protection law)
- Complex multi-system debugging (tracing a failure across microservices,
  database state, and network conditions simultaneously)
- Critical safety decisions (fraud determination with irreversible account action)
- Novel problem solving with no established template
- Root-cause analysis of a data conflict across systems with contradictory state
- Drafting legally binding or regulatory-facing communications
- High-stakes escalation path design

**Signal patterns:**
- A wrong answer triggers irreversible action (account suspension, legal filing,
  financial charge)
- The task involves reasoning across domains that rarely appear together
- Output will be reviewed by a human expert and any error is immediately visible
- Historical misclassification of similar tasks produced costly rework

---

## Confidence Threshold

The classifier emits a `classification_confidence` score (0.0–1.0) with each
decision.

```
if classification_confidence < 0.70:
    assigned_model = max(assigned_model, "claude-sonnet-4-5")
    routing_rationale += " [escalated: low-confidence classification]"
```

Low confidence typically arises from:
- Novel task types not seen in training examples
- Contradictory signals across dimensions (e.g., low reasoning_depth but high
  safety_criticality)
- Ambiguous task descriptions that could span two tiers

---

## Budget Pressure Overrides

Budget signals come from BudgetGovernor via `input/budget-signal.json`.
The `budget_utilization` percentage drives the override tier:

```
if budget_utilization >= 90%:
    # Hard constraint: force Haiku except where safety_criticality >= 7
    if safety_criticality < 7:
        assigned_model = "claude-haiku-4-5"
        routing_rationale += " [budget: >90% utilization, forced downgrade]"

elif budget_utilization >= 80%:
    # Soft constraint: downgrade one tier if not safety-critical
    if safety_criticality < 7:
        assigned_model = downgrade_one_tier(assigned_model)
        routing_rationale += " [budget: >80% utilization, optional downgrade applied]"
```

**Safety criticality anchor:** Tasks with `safety_criticality >= 7` are never
downgraded below Sonnet, regardless of budget pressure.

**Downgrade ladder:** `opus → sonnet → haiku`
(Haiku cannot be downgraded further; it is the floor.)

---

## Escalation Policy

Escalation is triggered by a failed quality gate — typically when the
downstream agent or a verifier detects insufficient reasoning depth.

```
Trigger:  quality_gate_fail OR output_confidence < threshold
Action:   escalate one tier (haiku → sonnet, sonnet → opus)
Max:      2 escalations per task (prevents infinite loops)
Backfeed: failed classification is logged with dimension scores for
          offline calibration of tier thresholds
```

Escalation cost accounting:
- Log `original_model`, `escalated_model`, `additional_cost_usd`
- Compare against cost of having routed directly to the escalated tier
- If escalation frequency for a task type exceeds 15%, promote that type's
  default tier in the routing policy

---

## Customer Service Step-Type Reference

Pre-classified routing for 15 common customer service pipeline steps.
Override with live classification when task complexity hints are present.

| Step Type                           | Default Tier | Notes |
|-------------------------------------|--------------|-------|
| classify_customer_intent            | MECHANICAL   | Closed taxonomy, direct pattern match |
| lookup_account_status               | MECHANICAL   | Single DB read, no reasoning |
| fill_ticket_template                | MECHANICAL   | All slots provided in context |
| transcribe_call_summary             | MECHANICAL   | Extract facts only, no interpretation |
| format_data_for_crm                 | MECHANICAL   | Transform, no judgment |
| suggest_upsell_opportunity          | STANDARD     | Requires product knowledge + account context |
| draft_standard_apology_email        | STANDARD     | Brand voice + tone matching |
| determine_refund_eligibility        | STANDARD     | Policy application, some edge cases |
| generate_personalized_empathy_response | STANDARD  | Tone calibration + context synthesis |
| summarize_case_history              | STANDARD     | Multi-document synthesis |
| resolve_simple_billing_dispute      | STANDARD     | Policy application + CRM write |
| orchestrate_multi_tool_workflow     | STANDARD     | Tool sequencing + error handling |
| analyze_fraud_pattern_in_dispute    | DEEP         | Cross-signal pattern + irreversible action |
| draft_legal_compliance_email        | DEEP         | Legal domain + regulatory requirement |
| resolve_multi_system_data_conflict  | DEEP         | Cross-system root cause + data integrity |

---

## Integration Notes

- **Input contract:** `task-metadata.json` must include `input_complexity_hints`
  for all six dimensions, or the classifier will score them from the description
  alone (lower confidence expected).
- **Budget signal freshness:** Refresh `budget-signal.json` at the start of each
  routing batch. Stale signals cause incorrect override decisions.
- **Escalation loop:** The downstream executor must return a `quality_gate_result`
  field so the escalation trigger can fire. Without it, misclassifications
  are silent.
- **Calibration cadence:** Review escalation-log.json weekly. Any task type with
  escalation rate > 15% should have its default tier promoted in routing-policy.json.
