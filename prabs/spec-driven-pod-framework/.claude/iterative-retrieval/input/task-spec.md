# Task Specification — Billing Dispute Resolution

## Task ID
`TASK-2024-11-07-CS-00412`

## Priority
High — customer has threatened to escalate to credit card dispute

## Primary Question
Is Marcus Thompson eligible for a refund of the November 1 charge on account
PRO-34821, given that he cancelled his subscription on October 15?

## Customer Profile

| Field | Value |
|-------|-------|
| Name | Marcus Thompson |
| Account ID | PRO-34821 |
| Plan | Professional (PRO) — $149/month |
| Account status | Cancelled (as of Oct 15, 2024) |
| Customer since | March 2021 |
| Prior disputes | None |
| Lifetime value | $5,373 |

## Incident Summary

Marcus contacted support on November 3, 2024, reporting an unexpected charge
of $149.00 posted to his Visa card on November 1, 2024. He states he
completed the cancellation flow on October 15, 2024, received a cancellation
confirmation email (confirmation ID: CANC-88201), and expected no further
charges. The November 1 charge appeared on his bank statement two days later.

Marcus is requesting a full refund and written confirmation that no future
charges will be processed.

## Agent Task

The agent must:
1. Confirm whether the October 15 cancellation was processed correctly.
2. Determine whether the November 1 charge is valid or erroneous under
   current billing policy.
3. Establish whether Marcus is eligible for a refund under the refund and
   grace period policies.
4. If eligible, initiate the refund workflow and provide Marcus with a
   resolution timeline.
5. If not eligible, provide a clear policy-grounded explanation and offer
   applicable alternatives (credit, goodwill gesture, escalation path).

## Knowledge Needed

The agent requires the following information to complete this task:

| Information needed | Expected source |
|--------------------|-----------------|
| Cancellation effective date policy | subscription_management or billing_policy |
| Billing cycle cutoff rules (when next charge is triggered) | billing_policy |
| Grace period definition and applicability to PRO tier | subscription_management or refund_procedures |
| Refund eligibility criteria (time window, plan type) | refund_procedures |
| Procedure for processing a refund (API call or workflow step) | refund_procedures or account_management |
| Formal dispute / escalation path if refund is denied | legal |

## Index Available

The retrieval agent has access to a knowledge base containing 847 articles.
The provided `document-index.json` contains a representative 30-entry sample
of that index with relevance tags for this task domain. The full index is
queryable via the vector store configured in `retrieval-config.json`.

## Retrieval Budget

As specified in `retrieval-config.json`:
- Maximum retrieval rounds: 5
- Confidence threshold to stop: 0.85
- Maximum tokens to load: 12 000

## Success Criteria

The agent's answer is considered complete when it can state, with citations:
- Whether the charge was valid or erroneous
- Whether the customer is eligible for a full, partial, or no refund
- The specific policy sections that support the determination
- The exact next action the agent should take (with sufficient detail to
  execute without further retrieval)

Coverage confidence must be >= 0.85 to close the task without human review.
If confidence is below 0.85 after retrieval, the case is flagged for
supervisor review before any refund is processed.
