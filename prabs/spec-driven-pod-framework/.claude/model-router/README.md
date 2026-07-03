# ModelRouter

Complexity-based model selection for AI agent pipelines.

ModelRouter uses `claude-haiku-4-5` as a lightweight classifier to route each
task step to the least expensive model capable of meeting its quality bar.
Correct routing is the single largest cost lever in the optimization layer —
it typically reduces model spend several-fold versus routing everything to
Sonnet or Opus.

---

## Files

```
ModelRouter/
  SKILL.md                                  # Full routing instructions and rules
  README.md                                 # This file
  input/
    task-metadata.json                      # Task steps requiring routing decisions
    routing-policy.json                     # Complexity-to-model mapping + rules
    budget-signal.json                      # Real-time utilization from BudgetGovernor
  output/
    routing-decisions.json                  # Primary routing table (nominal budget)
    routing-decisions-budget-pressure.json  # Routing at 87% budget utilization
    escalation-log.json                     # Escalation traces for audit and calibration
```

---

## Calibrating the Routing Policy for Your Use Case

The default thresholds in `routing-policy.json` were set using offline evaluation
on 200 labeled customer service tasks. They will not be optimal for your pipeline
without calibration.

### Step 1: Label a representative sample

Run 50-100 tasks through the pipeline without routing (use Sonnet for all). Have
a domain expert score each output for quality. Separately, have the same expert
score the complexity dimensions (reasoning_depth, ambiguity_level, etc.) for
each task.

### Step 2: Fit tier boundaries

Plot `weighted_composite_score` on the x-axis and `output_quality_when_using_haiku`
on the y-axis. Find the composite score at which Haiku output quality drops below
your acceptable threshold. That is your MECHANICAL/STANDARD boundary. Repeat for
Sonnet vs. Opus to find the STANDARD/DEEP boundary.

Typical findings from customer service pipelines:
- MECHANICAL/STANDARD boundary: 2.8 to 3.8 (default: 3.5)
- STANDARD/DEEP boundary: 5.5 to 7.2 (default: 6.5)

If your tasks are more complex on average (e.g., technical support vs. billing
support), lower both thresholds. If simpler (e.g., FAQ chatbot), raise them.

### Step 3: Calibrate dimension weights

The default weight set (reasoning_depth=0.30, domain_expertise=0.20) was designed
for a generalist customer service pipeline. Adjust based on what actually drives
misclassification in your domain:

- **Technical support**: Increase `domain_expertise` weight (0.30), reduce
  `ambiguity_level` (0.10). Technical correctness matters more than ambiguity.
- **Legal/compliance**: Increase `safety_criticality` weight (0.20) and
  `output_precision` (0.15). Errors are expensive.
- **Sales/CX**: Increase `ambiguity_level` (0.25). Customer intent is often
  underspecified and tone judgment is critical.

### Step 4: Update the step-type reference table

Add all your pipeline's recurring step types to the `customer_service_step_type_defaults`
section in `routing-policy.json`. Pre-classification of known step types is faster
and more consistent than live scoring on every task.

For each new step type:
1. Run 10 examples and observe escalation rate.
2. If escalation rate > 15%, promote the default tier.
3. If escalation rate is 0% for 30+ runs, consider demoting the default tier.

---

## Monitoring Escalation Rates to Improve Classification

The `output/escalation-log.json` file is the primary calibration signal.
Review it weekly.

### Key metrics to track

| Metric | Target | Action if Exceeded |
|--------|--------|--------------------|
| Overall escalation rate | < 10% | Review composite score thresholds |
| Escalation rate per task type | < 15% | Promote that task type's default tier |
| Confidence-below-threshold rate | < 20% | Improve complexity hint generation |
| Budget-downgrade escalation rate | < 8% | Tighten downgrade eligibility rules |

### Reading the escalation log

Each entry in `escalation-log.json` contains:
- `original_classification` — what the classifier scored and why
- `quality_gate_result` — what specifically failed and by how much
- `root_cause_analysis` — why the initial classification was wrong
- `policy_feedback` — concrete rule changes to prevent recurrence

The `aggregate_analysis` section at the end of the log summarizes escalation
rates by task type and flags any type approaching the 15% promotion threshold.

### Common misrouting patterns

**1. Framing mismatch (most common)**
A task is described as "verify X" or "check Y" when it actually requires
independent adversarial analysis. The passive framing misleads the classifier
into scoring lower reasoning_depth. Fix: Add keyword detection for verification
tasks in safety-critical domains and auto-boost `safety_criticality`.

**2. Hidden legacy context**
A task looks like a standard lookup but depends on historical commitments or
legacy configurations that require policy-history reasoning. The initial
complexity hints capture only the surface task. Fix: Add fields to
`input_complexity_hints` for `has_historical_dependency` and
`involves_verbal_commitment` — these should automatically increase
`reasoning_depth` by 2.

**3. Borderline confidence under budget pressure**
The combination of a marginal confidence score (0.70-0.80) and a budget-pressure
downgrade creates a predictable failure mode. The downgrade makes an already
uncertain classification fail. Fix: Add the compound rule described in
ESC-002's `policy_feedback` — do not apply budget downgrade when confidence < 0.80.

**4. Multi-record pattern detection underestimated**
Tasks requiring synthesis across N records (case histories, transaction sequences)
are frequently underscored on `reasoning_depth` because each individual record
seems simple. The complexity comes from the cross-record patterns, which only
emerge at synthesis time. Fix: When `num_input_records > 3`, automatically add
+1 to `reasoning_depth` and +1 to `multi_step_planning`.

**5. Escalation not triggered because quality gate is absent**
Misclassifications are silent when the downstream executor does not return a
`quality_gate_result` field. The escalation loop never fires. Fix: Enforce that
all task types have a quality gate defined, even if it is a simple confidence
threshold check. Tasks without quality gates should default to Sonnet.

---

## Integration with BudgetGovernor

ModelRouter consumes the `active_signal` block from `input/budget-signal.json`.
This file is written by BudgetGovernor before each routing batch.

### Signal refresh timing

Refresh the budget signal:
- At the start of each routing batch (mandatory)
- After any Opus task completes (Opus tasks move spend significantly)
- When `trend.risk` is "high" — refresh every task, not every batch

Do not use a signal that is more than 5 minutes old during an active session.
Stale signals cause incorrect override decisions: a session that crossed 80%
utilization will be incorrectly treated as nominal.

### Handling the 90% hard-constraint tier

When `budget_pressure = "critical"` (>= 90% utilization), the force-Haiku rule
applies to all non-safety-critical tasks. Before routing under this condition:

1. Identify all Opus tasks remaining in the queue.
2. If remaining Opus tasks alone exceed the remaining budget, alert the operator
   before proceeding. Do not silently defer critical tasks.
3. Consider whether to raise the session cap (via BudgetGovernor) or reschedule
   Opus tasks to a new session.

The `routing-decisions-budget-pressure.json` sample illustrates this: three
protected Opus tasks ($0.158 combined) would exceed the $0.019 remaining budget
at 87% utilization. The system flags this in `projected_session_completion`.

### Coordinating cap raises

If BudgetGovernor raises the session cap mid-session, ModelRouter must re-evaluate
any tasks already downgraded under the previous pressure tier. Tasks that were
downgraded from Sonnet to Haiku under `elevated` pressure should be re-routed at
their baseline complexity scores once the cap raise brings utilization below 80%.

---

## Cost Reference

| Model | Input (per 1K tokens) | Output (per 1K tokens) | Relative to Haiku |
|-------|-----------------------|------------------------|-------------------|
| Haiku | $0.00025 | $0.00125 | 1x |
| Sonnet | $0.003 | $0.015 | 12x |
| Opus | $0.015 | $0.075 | 60x |

A typical routing mix for a customer service pipeline (40% Haiku, 45% Sonnet,
15% Opus) costs approximately 38% of what all-Sonnet routing would cost, and
8% of all-Opus.

The classifier itself (running on Haiku, ~2K tokens per invocation) costs
~$0.0005 per routing batch. This overhead is recovered immediately: correctly
routing a single Sonnet task to Haiku saves more than the classifier's cost.

---

## Quick Calibration Checklist

Before deploying ModelRouter to a new pipeline:

- [ ] Replace `input/task-metadata.json` with your pipeline's actual task types
- [ ] Run the step-type labeling exercise (50-100 tasks, scored by domain expert)
- [ ] Fit tier boundaries to your quality-vs-composite data
- [ ] Adjust dimension weights for your domain's primary complexity driver
- [ ] Add recurring step types to `customer_service_step_type_defaults`
- [ ] Verify all task types have a quality gate returning `quality_gate_result`
- [ ] Set `budget-signal.json` refresh to trigger from BudgetGovernor on each batch
- [ ] Set a calendar reminder to review `escalation-log.json` weekly for the first month
