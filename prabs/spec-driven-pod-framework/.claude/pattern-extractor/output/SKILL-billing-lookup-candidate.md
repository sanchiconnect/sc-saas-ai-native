---
status: CANDIDATE
review_required: true
confidence: 0.87
evidence: "3 observations across 1 session (sess_20260603_001)"
pattern_id: billing_lookup_sequence
extracted_by: PatternExtractor v1.0.0
extracted_at: "2026-06-03T09:52:00Z"
overlap_warning: "Partial overlap with existing skills: crm_lookup_order, proactive_case_check. See Overlap Notes below before promoting."
anti_pattern_flag: false
promotion_threshold_met: true
---

# Skill Candidate: billing-dispute-lookup-sequence

> CANDIDATE — requires human review and approval before promotion to live skill library.
> See promotion checklist at the bottom of this file.

## Trigger

Apply this skill when:
- A customer reports a billing dispute, unexpected charge, double charge, duplicate transaction, or unrecognised charge
- A customer asks to "check my bill", "review my charges", or "look into a payment"
- You are beginning any investigation that will require examining a customer's financial history

Do NOT apply when:
- The customer is only asking about future pricing or plan costs (no history needed)
- You already have a confirmed customer_id from earlier in the same session AND have already called get_cases for this customer within the last 5 turns

## Instructions

Execute the following three-tool sequence in order before taking any other action. Do not ask the customer for additional details first — the lookup is fast and the data it returns will answer most clarifying questions automatically.

**Step 1 — Establish Identity**

```
lookup_customer(
  identifier: <email or account_id provided by customer>,
  id_type: "email" | "account_id"
)
```

- If the customer provided an email, use `id_type: "email"`
- If the customer provided a numeric or alphanumeric account ID, use `id_type: "account_id"`
- If lookup fails with account_id, retry once with email before returning an error
- Do not proceed to Step 2 until you have a resolved `customer_id`

**Step 2 — Check for Existing Cases**

```
get_cases(
  customer_id: <resolved from Step 1>,
  status: "all",
  limit: 5
)
```

- Checking cases first prevents creating duplicate cases and reveals whether a specialist is already working the issue
- If an open case already exists for the same billing topic, prefer to update it (Step 2 result) rather than creating a new case later
- Note the case IDs returned — you will need them if escalating

**Step 3 — Retrieve Billing History**

```
get_billing_history(
  customer_id: <resolved from Step 1>,
  days: 30
)
```

- Default to 30 days. This covers the most recent full billing cycle for monthly customers and captures the majority of dispute scenarios
- If the customer explicitly specifies a different time period, honour it — but 30 days is the correct default for any unspecified scope
- For "double charge" or "duplicate transaction" complaints: after receiving results, filter for entries with identical `amount` and `description` fields on the same or consecutive `date` values

**After the sequence completes**, you have sufficient context to:
- Confirm or deny the customer's reported issue
- Identify any open cases to reference or update
- Proceed to resolution (refund, credit, escalation, explanation) based on the findings

## Examples

**Example 1 — Double Charge Confirmed**

Customer: "I think I was charged twice this month."

Correct sequence:
```
1. lookup_customer(identifier="marcus.webb@techcorp.io", id_type="email")
   → customer_id: CUS_88412

2. get_cases(customer_id="CUS_88412", status="all", limit=5)
   → [case: CASE_77091, login issue, closed]

3. get_billing_history(customer_id="CUS_88412", days=30)
   → [CHG_4411: $49.99, 2026-06-01] [CHG_4398: $49.99, 2026-06-01]
```

Finding: Two identical charges on same date — confirmed duplicate. Proceed to create_refund for the second charge ID.

**Example 2 — No Duplicate Found**

Customer: "I think I may have been double charged."

Correct sequence:
```
1. lookup_customer(identifier="sarah.chen@techcorp.io", id_type="email")
   → customer_id: CUS_91203

2. get_cases(customer_id="CUS_91203", status="all", limit=5)
   → [] (no cases)

3. get_billing_history(customer_id="CUS_91203", days=30)
   → [CHG_4450: $49.99, 2026-06-01] (single charge)
```

Finding: Only one charge present — no duplicate. Inform customer account is correct. Investigate alternative concern (e.g., promotional discount not applied).

## Caveats

- **Session warm-up exception**: If you have already looked up this specific customer earlier in the same session (within 5 turns), and you already called get_cases at that time, you may skip Steps 1 and 2 and go directly to get_billing_history. However, if there is any doubt about whether the customer's situation has changed since the earlier lookup, repeat the full sequence.
- **High-value disputes**: For disputes involving amounts over $200, the refund step requires supervisor approval even if a duplicate is confirmed. This skill covers the lookup sequence only — not the refund authorisation threshold.
- **Non-monthly billing cycles**: The 30-day window is calibrated for monthly subscribers. For annual or quarterly customers, adjust the days parameter to cover the relevant billing period.
- **Multi-customer sessions**: When handling billing queries for multiple customers in one session (e.g., a company admin), run the full three-tool sequence for each new customer regardless of prior lookups in the session.

---

## Overlap Notes (for reviewer)

Before promoting, assess whether to:

**Option A — Promote as new skill** (recommended)
This skill is specifically scoped to billing disputes and encodes the three-step sequence as a unified billing-domain workflow. It adds the `days=30` parameter, the double-charge filter heuristic, and the billing-specific trigger language that the existing `crm_lookup_order` and `proactive_case_check` skills lack.

**Option B — Enhance `crm_lookup_order`**
Add a billing-dispute sub-section to `crm_lookup_order` with the get_cases + get_billing_history(days=30) continuation. This keeps the library leaner but may make `crm_lookup_order` unwieldy as the canonical identity-lookup skill.

**Option C — Merge `proactive_case_check` into this skill**
Since `proactive_case_check` is effectively Step 2 of this sequence, this skill could subsume it for billing contexts. Risk: `proactive_case_check` also applies to non-billing scenarios.

Reviewer recommendation: Option A. The billing-specific context warrants a dedicated skill with its own trigger and domain notes.

---

## Promotion Checklist

Before copying this file to the live skill library, confirm:

- [ ] Pattern observed in at least 2 distinct sessions (currently: 1 session) — consider waiting for 1 additional session to reduce single-session risk
- [ ] Overlap decision made (Option A / B / C from above) and documented
- [ ] `status: CANDIDATE` header removed from the promoted version
- [ ] Skill added to `existing-skill-library.json` with promoted_date, sessions_observed, and tags
- [ ] If Option A: add a cross-reference note to `crm_lookup_order` pointing to this skill for billing contexts
- [ ] If Option A: update `proactive_case_check` notes to reference this skill as the billing-specific implementation
- [ ] Version bump to `existing-skill-library.json` library_version
