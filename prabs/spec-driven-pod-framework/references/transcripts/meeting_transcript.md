# Sample Elicitation: Accounts Payable Invoice Automation

> **Program Charter Skill — Sample Dialogue**
>
> This document demonstrates how the `program-charter` skill conducts a structured elicitation workshop. The conversation below is a realistic simulation of a charter discovery session between Acme Corp (acting as a senior Business Analyst) and Finance stakeholders at a large enterprise organisation.

---

## Participants

| Role | Name |
|---|---|
| Acme Corp (Business Analyst) | Facilitating |
| Program Lead | Michael Torres, Director of Finance Transformation |
| Head of Accounts Payable | Lisa Park |
| Procurement Manager | James Okafor |
| Enterprise Architect | Priya Mehta |
| Internal Audit Lead | Robert Chen |

---

## Elicitation Transcript

---

### Opening

**Acme Corp:**

Good morning, everyone. Thank you for making time for this charter workshop. My role today is to help us build a shared, documented understanding of what we are trying to achieve with the Accounts Payable Invoice Automation program before we commit to delivery planning.

I want to be direct about what this session is and what it is not. We are not here to design the solution — that comes later. We are here to get crisp alignment on the problem we are solving, the outcomes we expect, who is affected, what is in scope, and what risks we need to manage. The output will be a program charter that the delivery team can use to make good decisions without needing to re-litigate these conversations.

I will work through five topic areas: program purpose and objectives, scope, stakeholders and user needs, delivery approach, and risks and constraints. I will ask follow-up questions where I need more precision. If something is genuinely unknown right now, we will capture it as an open decision — that is equally valuable.

Let us start with the foundation. Michael, can you describe what is driving this program in your own words?

---

**Michael Torres:**

Sure. We process around four thousand invoices a month across our AP team. Right now, every invoice comes in through email or a shared mailbox, and an analyst has to open it, pull out the relevant fields — vendor name, invoice number, line items, amounts — then go find the purchase order it is supposed to match against, track down the goods receipt or acceptance note if it is a services invoice, and compare them line by line. When something does not match, they send an email chain to procurement or the budget owner and wait for a response. The whole thing takes about thirty minutes per invoice on average, and we still miss things. Our matching accuracy is sitting around ninety percent, which sounds acceptable until you realise that ten percent of four thousand invoices is four hundred invoices a month with errors or disputes. We want to automate that end-to-end and get the team focused on exceptions rather than routine processing.

---

**Acme Corp:**

That is a clear picture, Michael, thank you. Before we move to outcomes, I want to make sure I have the baseline right, because these numbers will anchor our success criteria.

You mentioned thirty minutes per invoice on average. Is that end-to-end elapsed time, or active handling time? In other words, does that thirty minutes include waiting for someone to respond to a discrepancy email?

---

**Michael Torres:**

Good question. The thirty minutes is active handling time — the time an analyst is actually working on it. The elapsed time from invoice receipt to payment approval can be anywhere from two days to two weeks depending on whether there are exceptions. We have had invoices sit in queues for three weeks waiting on a response from a budget owner.

---

**Acme Corp:**

That is an important distinction. So we have two separate problem dimensions: the analyst's active processing time, and the total cycle time from receipt to payment approval. Which of these is the primary driver of the business case — the cost of analyst time, the impact on vendor relationships from late payments, or both?

---

**Michael Torres:**

Honestly, both, but if I had to rank them — supplier dissatisfaction is the bigger reputational risk. We have had three strategic vendors flag payment delays in the last quarter. One of them is renegotiating payment terms with us. The internal efficiency is the cost justification, but the vendor relationship piece is what got executive sponsorship.

---

**Acme Corp:**

That is helpful framing. I will make sure the charter reflects two distinct outcome dimensions: operational efficiency and supplier relationship health. We will need a metric for each.

Lisa, from the AP team's perspective, where does the thirty minutes actually go? I want to understand the distribution of effort across the steps John described.

---

**Lisa Park:**

The biggest time sink is honestly finding the PO. Our ERP system is not well integrated with the invoice inbox, so an analyst has to manually search for the PO number, and sometimes the vendor puts the wrong PO reference on the invoice or none at all. That alone can take ten to fifteen minutes. Then the GRN lookup is another five minutes because goods receipts are in a different module. The actual comparison is maybe five minutes if the documents are clean. The rest is writing up the exception and chasing approvals.

---

**Acme Corp:**

So roughly half the active processing time is document retrieval rather than comparison. That has a direct implication for where automation will deliver the most immediate value — and it also tells me that PO reference quality on incoming invoices is a risk we need to call out explicitly. I will come back to that when we discuss risks.

Let me ask about the ninety percent matching accuracy figure. How is that measured today? Is it the percentage of invoices that clear without any exception, or something else?

---

**Lisa Park:**

It is the percentage that pass our manual review without a discrepancy. So if an analyst looks at an invoice and says it matches the PO and GRN, that counts as a match. The ten percent are the ones that go into an exception queue.

---

**Acme Corp:**

I want to flag an assumption here for the group. If the current accuracy measurement is based on analyst judgment during manual review, then the ninety percent baseline may itself contain errors — invoices that passed review but had undetected discrepancies. The automated system will apply rule-based logic that may surface issues the manual process missed. That means our early accuracy metrics might initially look worse than ninety percent even if the system is performing correctly. Is the group comfortable with how we will communicate that nuance during the pilot?

---

**Robert Chen:**

That is exactly the kind of thing Audit has been raising for two years. We have done sample audits and found that a meaningful portion of the "matched" invoices had minor discrepancies that were within informal tolerance ranges that never got documented. So yes, the automated system may surface more exceptions initially, and we need to be prepared for that narrative.

---

**Acme Corp:**

Robert, thank you — that is important context. I will capture that as both a risk and a communication dependency in the charter. We will need an agreed tolerance framework before go-live so that the definition of a "match" is explicit and documented rather than a matter of analyst judgment.

---

### Group 1: Program Purpose and Objectives

**Acme Corp:**

Let us formalise the objectives. I am going to reflect back what I have heard and ask you to push back where I have it wrong.

The program has four primary objectives:

One — reduce analyst active processing time per invoice from thirty minutes to under five minutes.

Two — improve matching accuracy from ninety percent to at least ninety-eight percent, with the acknowledgment that we need a documented tolerance framework for what constitutes a match.

Three — reduce the proportion of invoices requiring manual intervention from the current eighty percent to no more than twenty percent — so a sixty percentage-point reduction.

Four — improve supplier payment cycle time, though we have not yet defined a specific target for that. Michael, what does a good outcome look like for payment cycle time?

---

**Michael Torres:**

We would want to get the average invoice-to-payment-approval cycle time down from the current average of — Lisa, what is that number?

---

**Lisa Park:**

For invoices that have no exceptions, the average is about four business days from receipt to approval. For invoices with exceptions, it is closer to twelve days. End-to-end including payment run scheduling it is typically five to seven days for clean invoices, three to four weeks for exceptions.

---

**Acme Corp:**

So let me propose a target: for clean invoices, reduce approval cycle time from four business days to same-day or next-business-day. For exception invoices, reduce from twelve business days to under five. Does that feel directionally correct, or is that too aggressive for the first iteration?

---

**Michael Torres:**

Same-day for clean invoices is the aspiration, yes. Under five days for exceptions is realistic if the routing is working well.

---

**Acme Corp:**

I will document those as aspirational targets for the pilot and flag that we will refine them based on Phase 5 data before setting formal SLAs.

One more question on objectives: is there an explicit compliance or audit readiness objective? Robert mentioned audit sample findings. Is there a regulatory driver here — for example, SOX compliance, IFRS requirements, or an internal audit finding that needs a remediation response?

---

**Robert Chen:**

Yes. We have an open internal audit finding from last year's review that cited inadequate documentation of matching decisions. We do not have a consistent audit trail showing who approved what and on what basis. The automated system needs to close that finding. That is a hard requirement, not a nice-to-have.

---

**Acme Corp:**

Understood. I will elevate audit trail completeness to a primary objective rather than a non-functional requirement. That changes its priority and means it needs to be designed in from day one, not added later. Priya, does that have architectural implications we should note now?

---

**Priya Mehta:**

Yes. Audit logging needs to be immutable and tamper-evident. We will need to think about log storage separately from the transaction database, and we need retention policies agreed with Legal and Audit before we design the schema. That is a dependency we should flag.

---

**Acme Corp:**

Noted. I will capture that as a pre-implementation dependency: Legal and Audit must confirm log retention requirements and tamper-evidence standards before the audit logging architecture is finalised.

---

### Group 2: Scope Definition

**Acme Corp:**

Let us move to scope. I find it is often more useful to start with what is explicitly out of scope, because that tends to generate more debate and surfaces hidden assumptions faster.

Michael, the briefing I received indicates that actual payment execution is out of scope — the system recommends approval but does not trigger the payment run. Can you confirm that, and explain the rationale?

---

**Michael Torres:**

Correct. Payment execution stays in the ERP. We are not touching the payment module in this program. The risk of automating payments without a full controls review is too high, and frankly the CFO would not approve it. What we want is for the system to get invoices to the point where a human can see a clear recommendation and click approve with confidence, rather than spending thirty minutes validating it themselves.

---

**Acme Corp:**

That is a clean boundary. The system's terminal output is a structured approval recommendation with supporting evidence — not a payment instruction. I want to confirm one related question: when the system routes an exception to a human reviewer, is the expectation that the reviewer works within the automation system's interface, or do they receive a notification and then work in the ERP?

---

**Lisa Park:**

We have not fully decided that. Our preference would be to have the exception routed to a review queue within whatever interface we build, so the reviewer can see the extracted invoice, the PO, the GRN, and the discrepancy explanation in one place rather than switching between systems.

---

**Acme Corp:**

That preference has a significant scope implication. If the human review interface is in scope, we need a UI — which adds design, accessibility, and user acceptance testing work. If it is out of scope and we are only sending notifications, the surface area is much smaller. I would recommend we explicitly decide this and document it. What is the group's view?

---

**James Okafor:**

From procurement's perspective, we need the exception to come to us with context. If I just get an email saying "invoice 12345 has a discrepancy," I am going to spend twenty minutes digging through the ERP to understand why. The value is in the explanation. So the interface matters, but it does not have to be elaborate — it just needs to show me the three documents and highlight what does not match.

---

**Acme Corp:**

That is a good articulation of the minimum viable requirement: a human review interface that presents the three source documents alongside the discrepancy explanation, sufficient for the reviewer to make a decision without leaving the system. I will scope that in as a core component of Phase 4 rather than leaving it ambiguous.

Now let me walk through the in-scope list and flag a few areas that need clarification.

You mentioned acceptance notes for services and software invoices. Currently, goods-based invoices are matched against a Goods Receipt Note. For services and software, the equivalent document is an acceptance note or service confirmation. Who generates that document today, and where does it live?

---

**James Okafor:**

It varies, which is part of the problem. For professional services, the internal requestor is supposed to confirm receipt in the procurement system, but compliance on that is inconsistent. For software, sometimes there is a licence acceptance email, sometimes it is just assumed. We probably have acceptance documentation for sixty percent of services invoices. The other forty percent are either missing or informal.

---

**Acme Corp:**

That is a significant data quality risk for services invoices specifically. If the acceptance note does not exist or is not in a system the automation can access, what should the system do? Options are: flag it as an exception requiring manual acceptance confirmation, treat a prior-period acceptance as a proxy, or apply a different matching rule for services. This is a decision the program needs to make before we design the matching logic.

---

**James Okafor:**

Flag it as an exception. We should not be auto-approving a services invoice if we cannot confirm the service was received.

---

**Acme Corp:**

Agreed, and I will document that as a matching rule decision: absence of acceptance documentation for services invoices is an automatic exception trigger. That will inflate our initial exception rate for services invoices — we should factor that into the pilot scope and the communications plan.

Let me confirm the out-of-scope items quickly. ERP migration — out of scope. Vendor onboarding — out of scope. Tax filing — out of scope. Supplier portals — out of scope. Procurement process redesign — out of scope. Are there any other areas the team has been asked about that we should explicitly exclude?

---

**Priya Mehta:**

We have had a few questions about whether this system will integrate with the vendor master data management system. Vendor validation — confirming that an invoice comes from an approved vendor with the correct bank details — is a related control. Is that in scope?

---

**Acme Corp:**

Good flag. Vendor validation against a vendor master is different from invoice matching. It is a financial controls step. My recommendation would be: the system should perform a lookup against the vendor master to confirm the vendor is active and the bank details on the invoice match the master record, and flag discrepancies. That is a validation step, not a procurement or onboarding step, so it is consistent with the in-scope boundary. But I want the group to confirm that explicitly rather than assume it.

---

**Michael Torres:**

Yes, that should be in scope. An invoice from an unknown vendor or with mismatched bank details is a fraud risk, not just a process risk. We need that check.

---

**Acme Corp:**

Confirmed. I will add vendor master validation to the in-scope validation framework with a specific callout that bank detail mismatches are a high-priority exception category.

---

### Group 3: Stakeholders and User Needs

**Acme Corp:**

Let us turn to stakeholders and user needs. I want to understand who interacts with this system, what they need from it, and where their interests might create tension.

Maria, walk me through a typical AP Analyst's day. How many invoices does each analyst handle, and what does their current workflow look like from start to finish?

---

**Lisa Park:**

We have eight analysts. Volume varies, but on average each analyst handles roughly twenty invoices a day — some days more during month-end. They work through a shared mailbox queue, download the invoice, open the ERP to find the PO, open the warehouse module to find the GRN, do the comparison in a spreadsheet or just in their head, and then either mark it as approved in the ERP or send a discrepancy email. There is no formalised workflow system — it is all manual queue management.

---

**Acme Corp:**

So today there is no system of record for the AP workflow itself — analysts are managing their own queues informally. That means the automation program is not just automating a step in an existing workflow, it is introducing a workflow system for the first time. That is a meaningful change management dimension. Has the analyst team been consulted on what they want from a review interface, or is this being designed for them?

---

**Lisa Park:**

They know the program is coming. We have briefed them at a high level. But no, we have not done any user research with them yet.

---

**Acme Corp:**

I would recommend we include at least two structured user interviews with AP Analysts during the requirements phase, before the review interface is designed. Their current workarounds often reveal requirements that stakeholders at the management level do not see. I will note that as a recommended activity in the delivery plan.

Now, Raj, from procurement's perspective — when an exception gets routed to your team, what information do you need to resolve it, and how quickly are you expected to respond?

---

**James Okafor:**

We need to see the original PO, the specific line item with the discrepancy, the invoice line, and ideally a plain-language explanation of what does not match — not just "line 3 quantity mismatch" but "invoice shows 50 units, PO shows 40 units, GRN shows 45 units." We need context. As for response time, there is no current SLA. Realistically, procurement managers are not sitting watching an inbox — we have other responsibilities. A two-business-day response target would be workable.

---

**Acme Corp:**

The plain-language explanation is interesting. You are describing exception explainability — not just flagging that a mismatch occurred, but generating a human-readable explanation of what specifically does not reconcile and why it matters. That is a more sophisticated requirement than basic exception routing. Priya, is that something the current architecture is designed to handle, or is that a new capability?

---

**Priya Mehta:**

The current thinking was rule-based matching with structured output. Generating plain-language explanations was not explicitly in the design. It could be done with a template approach — "Invoice quantity [X] does not match PO quantity [Y]. GRN quantity [Z] was received." That is feasible without generative AI. If we want something more sophisticated, it is a different conversation.

---

**Acme Corp:**

Let me propose a minimum viable approach: structured exception explanations using templated language that identifies the specific field, the expected value, the actual value, and the source document for each. That is deterministic, auditable, and does not require generative AI. If pilot feedback indicates that reviewers need richer context, we can iterate. Does that work for the group?

---

**James Okafor:**

That works. Templated is fine as long as it tells me the three numbers.

---

**Acme Corp:**

Good. Robert, from an audit perspective — what does your team need from this system that you are not getting today?

---

**Robert Chen:**

Three things. First, a complete decision log — every invoice, every validation check, every matching decision, who reviewed exceptions, and what action was taken, with timestamps. Second, the ability to run queries against that log without involving IT every time. Third, confidence that the log cannot be altered after the fact. Right now if I want to audit an invoice from six months ago, I am emailing three different people and waiting a week to get the information.

---

**Acme Corp:**

Those are well-defined requirements. Let me translate them into system capabilities: immutable audit log with structured fields for every processing event; a query interface accessible to Audit without requiring IT involvement; and log retention for a period agreed with Legal. On the query interface — are you envisioning a reporting dashboard, an export to Excel, or something else?

---

**Robert Chen:**

Excel export would satisfy most of our needs. We have our own analysis tools. We do not need a dashboard built for us — just the ability to pull the data ourselves.

---

**Acme Corp:**

Understood. That simplifies the audit interface requirement considerably. I will specify it as a self-service data export capability for the Audit role — structured CSV or Excel, filterable by date range, vendor, invoice status, and exception type. That is achievable without a custom reporting UI.

---

### Group 4: Delivery Approach and Timeline

**Acme Corp:**

Let me move to delivery structure. I understand the program is planned as a phased rollout across five phases. Before I confirm that breakdown, I want to understand the driving constraint on timeline. Michael, is there a hard deadline — a board commitment, a budget cycle, a contract renewal — that is anchoring the overall delivery date?

---

**Michael Torres:**

We have committed to the CFO that we will have a working pilot by end of Q3. That is roughly four months from now. The full rollout is expected to follow in Q4. We have budget approved for this fiscal year, and if we do not show results before year-end, the program will go back into the prioritisation queue next year.

---

**Acme Corp:**

Four months to pilot is a meaningful constraint. Let me check the phase plan against that. Phase 1 is invoice extraction, Phase 2 is validation, Phase 3 is three-way matching, Phase 4 is exception explainability and human review, and Phase 5 is the pilot. That is five sequential phases in four months, which is ambitious. Have those phases been sized, or is the breakdown currently notional?

---

**Michael Torres:**

Notional. We have not done any sizing yet.

---

**Acme Corp:**

I want to flag a delivery risk here without wanting to be alarmist. Five phases in four months assumes each phase is roughly three weeks of elapsed time, including build, test, and handoff. That is achievable if the team is fully dedicated and there are no significant integration blockers, but it leaves very little buffer for the document quality and missing PO issues we discussed earlier. I would recommend we identify which elements of Phases 1 through 3 can run in parallel, and whether Phase 4's human review interface can be scoped to a minimum viable version for the pilot. I will flag this in the charter as a delivery risk requiring early sprint planning.

James, from procurement's perspective — what is your team's dependency during delivery? Will you need to provide test data, validate matching rules, or review outputs?

---

**James Okafor:**

We will need to validate the matching tolerance thresholds. Procurement has informal rules about what we accept — for example, a quantity variance of up to two percent is often allowed under blanket POs. Those rules have never been formally documented. Someone needs to sit down with us and capture them before the matching logic is built.

---

**Acme Corp:**

That is a critical dependency. The matching rules workshop with procurement needs to happen before Phase 3 build starts. If that slips, Phase 3 cannot be completed correctly. I will call that out explicitly as a sequencing dependency in the charter.

Priya, on the integration side — what systems does this program need to connect to, and which of those integrations are greenfield versus existing?

---

**Priya Mehta:**

The ERP integration for PO and GRN retrieval is the most complex. We have an API available but it is not well documented and the team that built it has since left. Email ingestion for invoice receipt is relatively straightforward. The vendor master lookup is a read-only API call that should be simple. The audit log persistence is internal. So the ERP integration is the one I am most concerned about.

---

**Acme Corp:**

Is there a risk that the ERP API has limitations that would prevent us from retrieving GRN data reliably — for example, performance limits, incomplete historical data, or undocumented gaps?

---

**Priya Mehta:**

Potentially. We will need a spike to assess it. I would want two weeks of technical investigation before we can confirm what the ERP integration can and cannot deliver.

---

**Acme Corp:**

I will document the ERP integration spike as a Phase 1 prerequisite activity. If that investigation surfaces blockers, the delivery timeline will need to be revisited. That is a known unknown we should be transparent about with the CFO's office.

---

### Group 5: Risks and Constraints

**Acme Corp:**

We are in the home stretch. I want to spend this final section on risks, because this is where programs often get surprised. I am going to name the risks I have already inferred from our conversation and ask the group to rate and add to them.

**Risk 1: Invoice data quality.** Invoices from different vendors arrive in different formats — some structured PDFs, some scanned images, some potentially handwritten or in foreign languages. If the OCR or extraction layer cannot reliably parse a subset of invoices, those will either fail silently or generate incorrect extracted data. Lisa, what is your rough sense of what proportion of your incoming invoices are clean digital PDFs versus scans or other formats?

---

**Lisa Park:**

I would estimate sixty percent are clean PDFs, thirty percent are scanned or image-based, and maybe ten percent are other — Excel attachments, Word documents, the occasional email with no attachment and the invoice in the body of the email.

---

**Acme Corp:**

So forty percent of invoice volume presents a data quality challenge from the outset. That is significant. The extraction accuracy on that forty percent will be lower than on clean PDFs, and errors in extraction propagate directly into matching errors. I would recommend the program sets an explicit minimum extraction confidence threshold — below which an invoice is automatically flagged for manual data entry rather than automated processing — and that we measure extraction accuracy separately from matching accuracy in the pilot. Does the group agree with that approach?

---

**Michael Torres:**

Yes. We should not be feeding garbage into the matching engine and wondering why results are inconsistent.

---

**Acme Corp:**

Agreed. I will specify extraction confidence thresholds as a configurable parameter, with a default that errs toward flagging uncertain extractions rather than propagating them.

**Risk 2: Missing or incomplete PO references.** You mentioned that vendors sometimes put incorrect PO numbers on invoices or none at all. If the system cannot find a matching PO, it cannot perform three-way matching. What is the current fallback when a PO cannot be located?

---

**Lisa Park:**

The analyst calls or emails the vendor to ask for the correct reference. That can take days.

---

**Acme Corp:**

That manual escalation path needs to be preserved in the automated system — with an appropriate notification to the vendor contact and a tracking record in the audit log. It also means we need vendor contact information accessible from within the system. Is that data available in the vendor master?

---

**Lisa Park:**

For most vendors, yes. Not all. Some of our smaller vendors only have a generic accounts email in the master.

---

**Acme Corp:**

I will note that as a data quality dependency: vendor contact completeness in the master data is a prerequisite for exception escalation workflows. That should be assessed during Phase 1 and remediated before the pilot.

**Risk 3: False positive exceptions.** If the matching thresholds are set too tightly, the system will generate a high volume of exceptions for minor variances that analysts currently resolve informally. This risks burdening reviewers and eroding adoption. James, how confident is the procurement team that it can document all the informal tolerance rules before Phase 3 build?

---

**James Okafor:**

Moderately confident for standard goods POs. Less confident for services and framework contracts where the rules are more contextual. There are probably scenarios we will not anticipate until we see them in the pilot.

---

**Acme Corp:**

That is an honest answer. My recommendation would be to set initial thresholds conservatively — err toward generating more exceptions than fewer — and use pilot data to tighten them. The risk of releasing a system that approves invoices it should not have approved is materially higher than generating too many exceptions in the early weeks. Is the group aligned on that philosophy?

---

**Michael Torres:**

Yes. The CFO has been explicit on this: we do not release a system that passes invoices incorrectly. Exception volume is manageable. Incorrect payments are not.

---

**Acme Corp:**

Noted, and I will document that as a governing principle: the program prioritises payment accuracy over automation rate. Exception volume is a tuning variable; payment accuracy is a hard constraint.

**Risk 4: Change resistance from the AP team.** The program effectively changes the AP Analyst's role from invoice processor to exception handler. That is a meaningful shift. Has the team been prepared for that change, and is there a change management plan?

---

**Michael Torres:**

We have communicated the vision but we have not done formal change management planning yet. That is on the list.

---

**Acme Corp:**

I will flag the absence of a formal change management plan as a delivery risk. The pilot's success depends on AP Analysts engaging constructively with the exception review workflow rather than reverting to the manual process in parallel. I would recommend we add a lightweight change management workstream to the delivery plan that includes role briefings, interface training, and a structured feedback mechanism during the pilot.

**Risk 5: ERP integration complexity.** David flagged this earlier. I will document it as a high-likelihood, high-impact risk given the underdocumented API and the team turnover that has occurred since it was built.

Are there any risks the group feels I have missed?

---

**Robert Chen:**

Regulatory change. We are currently operating under our existing internal controls framework, but there are emerging discussions in the industry about AI-assisted or automated financial processing and whether existing internal control standards need to be updated. If our external auditors or a regulator starts requiring specific documentation of how automated matching decisions were made, we need to be prepared for that.

---

**Acme Corp:**

That is a forward-looking risk worth capturing. I will document it as an emerging regulatory dependency: the program should design for full explainability of automated decisions from the outset, so that if external auditors require evidence of decision logic, we can produce it from the audit log without redesigning the system. That reinforces the case for immutable, structured logging with decision rationale captured at each step.

Any other risks before we move to the summary?

---

**Priya Mehta:**

Scalability. We are designing for four thousand invoices per month today. If the business grows or if we bring additional entities into scope, volume could increase materially. The architecture should not require a redesign to handle two or three times current volume.

---

**Acme Corp:**

Good addition. I will capture that as a non-functional scalability requirement: the system must support at least three times current invoice volume — approximately twelve thousand invoices per month — without architectural changes, and performance targets must hold at that scale.

---

### Pre-Generation Summary

**Acme Corp:**

Before I generate the charter, let me present a structured summary of everything we have agreed today. Please push back on anything that does not reflect the discussion accurately.

---

## Summary for Confirmation

### Program Identity

| Field | Value |
|---|---|
| Program Name | Accounts Payable Invoice Automation |
| Program Lead | Michael Torres, Director of Finance Transformation |
| Primary Sponsor | CFO (to be named in charter) |
| Target Pilot Date | End of Q3 (approximately four months from session date) |
| Full Rollout Target | Q4, current fiscal year |

---

### Problem Statement

The organisation manually processes approximately 4,000 vendor invoices per month through a shared mailbox workflow. Eight AP Analysts spend an average of 30 minutes per invoice in active handling time, with the majority of that time consumed by document retrieval rather than analysis. Total cycle time from receipt to payment approval averages four business days for clean invoices and twelve business days for exceptions, with some invoices sitting in queue for three weeks.

Matching accuracy is approximately 90%, measured by analyst judgment. Internal audit findings suggest this figure may understate the true error rate, as informal tolerance thresholds have never been formally documented. An open internal audit finding cites inadequate audit trails for matching decisions. Strategic vendor relationships are under strain from payment delays, with at least one vendor renegotiating payment terms.

---

### Objectives and Success Criteria

| Objective | Current Baseline | Target |
|---|---|---|
| Analyst active processing time per invoice | 30 minutes | Under 5 minutes |
| Matching accuracy | ~90% (judgment-based) | ≥98% (rule-based, documented tolerance) |
| Invoices requiring manual intervention | ~80% | ≤20% |
| Cycle time — clean invoices | 4 business days to approval | Same-day or next-business-day |
| Cycle time — exception invoices | 12 business days to approval | Under 5 business days |
| Audit trail completeness | Inadequate (open audit finding) | Immutable log, self-service export, agreed retention period |

**Governing Principle:** The program prioritises payment accuracy over automation rate. Exception volume is a tuning variable. Incorrect payments are not acceptable.

---

### Scope

**In Scope:**
- Invoice ingestion from email and shared mailboxes
- Invoice field extraction with configurable confidence thresholds; low-confidence extractions flagged for manual entry
- Invoice validation, including vendor master validation and bank detail verification against the vendor master
- Purchase Order retrieval via ERP integration
- Goods Receipt Note retrieval via ERP integration
- Acceptance Note handling for services and software invoices; absence of acceptance documentation is an automatic exception trigger
- Three-way matching with configurable, formally documented tolerance thresholds
- Exception identification, structured plain-language templated explanation, and routing
- Human review interface presenting source documents and discrepancy explanation in a single view
- Approval recommendation output — structured and auditable, not a payment instruction
- Immutable audit log with self-service CSV or Excel export for the Audit role, filterable by date range, vendor, invoice status, and exception type
- Role-based access controls

**Out of Scope:**
- Payment execution or ERP payment module integration
- ERP migration or replacement
- Vendor master data remediation (dependency of this program, not a deliverable)
- Vendor onboarding
- Tax filing
- Supplier portal development
- Procurement process redesign

---

### Stakeholders and Primary Needs

| Stakeholder Group | Primary Need |
|---|---|
| AP Analysts | Exception-focused workflow, single-view review interface, reduced routine processing burden |
| Finance Managers | Approval recommendations with clear confidence rationale, reduced payment delays |
| Procurement Specialists | Contextual exception notifications with three-document comparison and templated discrepancy explanation; two-business-day response SLA |
| Internal Audit | Immutable decision log, self-service data export, tamper-evident storage, agreed retention period |
| IT / Enterprise Architecture | Supportable integrations with documented API contracts, scalable log storage, maintainable configuration |
| Executive Sponsors | Pilot results by Q3, measurable ROI against stated objectives, improved vendor relationship metrics |

---

### Architecture Assumptions Confirmed

- OCR or document extraction capability is available or will be provided as an input to Phase 1
- Validation logic is rule-based with configurable thresholds; no generative AI required in initial release
- Matching logic uses configurable tolerance thresholds formally documented with Procurement before Phase 3 build
- Exception explanations use structured templates, not generative AI, in the initial release; iteration possible post-pilot
- System outputs are structured JSON with an ERP-compatible approval recommendation payload
- Audit log is immutable, stored separately from the transaction database, with tamper-evident design
- Log retention period to be confirmed with Legal and Audit before architecture is finalised — pre-implementation dependency
- ERP API for PO and GRN retrieval exists but requires a two-week investigation spike before integration scope and timeline can be confirmed
- System must support at least 12,000 invoices per month (3× current volume) without architectural changes

---

### Phased Delivery Plan

| Phase | Scope | Notes |
|---|---|---|
| Phase 1 | Invoice ingestion and field extraction | Includes ERP API spike; extraction confidence thresholds defined; vendor master data quality assessed |
| Phase 2 | Validation framework | Includes vendor master validation and bank detail check |
| Phase 3 | Three-way matching | Requires completed Procurement tolerance rules workshop as hard prerequisite |
| Phase 4 | Exception explainability and human review interface | Scoped to minimum viable interface for pilot; AP Analyst user interviews completed before design |
| Phase 5 | Pilot rollout | Subset of invoice volume; all five objectives measured against baselines |

**Delivery Risk:** Five sequential phases in four months is an aggressive schedule. Parallel execution of Phases 1–3 where possible is recommended. Phase 4 should be scoped to MVP. A delivery planning workshop is required immediately after the ERP spike completes.

---

### Key Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| ERP API limitations or undocumented gaps | High | High | Two-week spike in Phase 1; timeline contingency if blockers surface |
| Invoice data quality — 40% non-PDF formats | High | Medium | Confidence threshold flagging; extraction accuracy measured separately from matching accuracy |
| Missing or incorrect PO references | High | Medium | Exception workflow with vendor escalation; vendor contact data dependency assessed in Phase 1 |
| Undocumented Procurement tolerance rules | Medium | High | Formal matching rules workshop before Phase 3 build — hard sequencing dependency |
| False positive exception volume from conservative thresholds | Medium | Medium | Conservative initial thresholds accepted as governing principle; tuned using pilot data |
| Acceptance note absence on services invoices | High for services | Medium | Auto-exception for missing acceptance documentation; flagged explicitly in pilot communications |
| AP Analyst change resistance | Medium | High | Lightweight change management workstream; role briefings; structured pilot feedback loop |
| Emerging regulatory requirements on automated financial decisions | Low–Medium | Medium | Decision explainability designed in from the outset; full rationale captured in audit log |
| Vendor master data incompleteness affecting escalation workflows | Medium | Low–Medium | Assessed and remediated as Phase 1 dependency before pilot |

---

## Open Decisions Requiring Confirmation

The following items were raised during the workshop but were not fully resolved. Each must be confirmed before the relevant implementation decision is made.

**1. Matching tolerance thresholds**
Procurement has informal tolerance rules — such as accepting quantity variances up to 2% under blanket POs — that have never been formally documented. Services and framework contracts are particularly uncertain. A formal matching rules workshop with Procurement must be completed before Phase 3 build begins. Until that workshop is complete, the matching logic cannot be correctly specified.
*Owner: James Okafor, Procurement.*

**2. Audit log retention period**
The required retention period for the immutable audit log has not been agreed. Legal and Internal Audit must confirm the retention period and any applicable regulatory minimums before the log storage architecture is designed. This must be resolved before Phase 1 architecture sign-off.
*Owner: Robert Chen / Legal.*

**3. ERP API capability and completeness**
The ERP API for PO and GRN retrieval is underdocumented and the original development team has departed. A two-week technical investigation spike is required to confirm data availability, historical completeness, and performance characteristics. The Phase 3 scope and delivery timeline cannot be finalised until this spike completes.
*Owner: Priya Mehta, IT.*

**4. Formal definition of a confirmed match**
The current 90% accuracy baseline is measured by analyst judgment under undocumented informal tolerances. Before the pilot, the program must formally define and document what constitutes a confirmed match — including tolerance bands, acceptable variance types by category, and how partial matches are classified. This definition becomes the baseline against which automated matching accuracy is measured.
*Owner: Lisa Park / Michael Torres.*

**5. Services invoice acceptance note resolution path**
Approximately 40% of services invoices currently lack formal acceptance documentation. The program has agreed to treat the absence of acceptance documentation as an automatic exception. The resolution path — specifically, whether the internal requestor must formally confirm receipt within the system before the invoice can progress to approval — has not yet been defined.
*Owner: James Okafor / Lisa Park.*

**6. Change management resourcing**
A lightweight change management workstream has been recommended but not resourced. A named change lead and a communications plan are required before the Phase 5 pilot begins. Without this, adoption risk for the AP Analyst role transition remains unmitigated.
*Owner: Michael Torres.*

**7. Vendor escalation workflow design**
When an invoice cannot be matched due to a missing or incorrect PO reference, the system must escalate to the vendor. The escalation method — automated email, manual task creation, or a combination — and the expected vendor response SLA have not been defined.
*Owner: Lisa Park.*

**8. External auditor acceptance of automated matching approach**
Robert Chen flagged emerging regulatory and auditor discussion around automated financial controls. Before the pilot goes live, it is recommended that the program confirm with the external auditor that the proposed automated matching approach, decision logging, and audit trail design are acceptable under the current audit framework. If the external auditor requires additional controls or documentation, this should be identified before the audit log architecture is finalised rather than after.
*Owner: Robert Chen / CFO office.*

---

**Acme Corp:**

That is the full summary. Does the group have any corrections, additions, or disagreements before I generate the charter?

If we are aligned, I will produce the Program Charter document now. I will incorporate everything we have discussed, flag the open decisions within the charter, and structure the document so the delivery team can use it as a working reference throughout the program lifecycle.

---

*End of elicitation transcript.*
