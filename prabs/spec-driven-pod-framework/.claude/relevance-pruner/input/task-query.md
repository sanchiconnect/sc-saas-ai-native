# Task Query — Current Agent Intent

## Customer Context

**Customer Name:** Sarah Chen
**Account ID:** ACC-88234
**Account Tier:** Premium
**Contact Channel:** Live chat (initiated 2026-06-03 at 10:14 AM UTC)

## Issue Summary

Sarah Chen is reporting a double charge of **$149.99** on her account. She states
that her credit card was billed twice on June 1, 2026 — once at 02:31 UTC and
once at 02:33 UTC. She wants the duplicate charge reversed and is asking how
quickly she can expect the refund given her Premium account status.

---

## Intent Decomposition

### Primary Intent
**`billing_dispute`**
Resolve a reported duplicate charge. Identify whether the duplicate is a
confirmed system error, determine the correct refund procedure, and initiate
the refund with appropriate SLA communication.

### Secondary Intent
**`refund_eligibility`**
Confirm whether the customer qualifies for the expedited Premium refund SLA
(24-hour processing) and whether the goodwill credit policy applies given that
this matches the known payment gateway batch processing issue window.

### Tertiary Context
**`premium_account`**
Sarah is a Premium subscriber. All procedures, SLAs, and communication
standards must reflect Premium entitlements. Her prior case history (CS-20241118-4421)
includes a verbal commitment from a previous agent confirming the Premium refund
SLA — this commitment is load-bearing context.

---

## Key Facts Provided by Customer

- Duplicate charge amount: **$149.99** (matches Premium subscription price)
- Charge timestamps: **02:31 UTC and 02:33 UTC on 2026-06-01**
- Customer states both charges appear on her bank statement
- Customer has not yet contacted her bank about a chargeback
- Customer is requesting resolution before end of business today

---

## Keywords for Embedding / Scoring

Primary terms: `billing dispute`, `double charge`, `duplicate charge`, `refund`,
`$149.99`, `Premium`, `payment gateway`, `batch processing`, `02:00 UTC`

Secondary terms: `refund timeline`, `SLA`, `Premium entitlement`, `goodwill credit`,
`expedited refund`, `known issue`, `INC-2847`

Context anchors: `Sarah Chen`, `ACC-88234`, `CS-20241118-4421`, `commitment_made`

---

## Context Budget

**Maximum tokens for injected context: 8,000**

The reasoning model (claude-haiku-4-5) will use the pruned context alongside a
system prompt (~1,200 tokens) and the live conversation transcript (~600 tokens),
leaving 8,000 tokens for retrieved knowledge context.

---

## What Good Context Looks Like for This Query

Highly relevant context should help the agent:
1. Confirm whether the timestamps match the known batch processing issue window.
2. Determine the correct refund procedure for a confirmed duplicate.
3. Quote the correct Premium SLA for refund turnaround.
4. Decide whether the $10 goodwill credit applies automatically.
5. Know that a prior agent already committed to the Premium refund SLA verbally.

Context that is NOT needed for this query:
- WiFi troubleshooting guides
- HR or internal operations documents
- API rate limit documentation
- General onboarding materials
- Office booking policies
