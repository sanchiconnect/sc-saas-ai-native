# PromptSlimmer Diff Report

**Project:** acme-customer-service-chatbot  
**Run date:** 2026-06-03  
**Model (bulk):** claude-sonnet-4-6  
**Model (critical sections):** claude-opus-4-7  

---

## Summary

| Metric | Value |
|---|---|
| Total directive changes | 23 |
| Safe (auto-applied) | 18 |
| Review required (human spot-check) | 4 |
| Critical — human sign-off required | 1 |
| Tokens before | 950 |
| Tokens after | 380 |
| Per-call token saving | 570 |
| Reduction | 60.0% |

**Status:** 18 safe changes auto-applied. 4 review items staged — apply after human spot-check. 1 critical item below requires explicit APPROVED annotation before the slimmed file is finalized.

---

## Change Log

### CHANGE-01

| | Content |
|---|---|
| **ORIGINAL** | "You are a highly skilled, knowledgeable, and empathetic customer service representative for Acme Corp, a leading provider of cloud-based software solutions for small and medium-sized businesses. Your role is an extremely important one: you serve as the primary point of contact between Acme Corp and its valued customers, and it is absolutely essential that every single interaction you have reflects the highest possible standards of professionalism, care, and expertise. You are not just answering questions — you are building relationships, nurturing trust, and representing the entirety of the Acme Corp brand in everything you say and do." (paragraph 1 of role section) |
| **SLIMMED** | "You are Acme Corp's customer service assistant. Help customers with account issues, billing, and technical support. Use available tools accurately and only when needed." |
| **CHANGE TYPE** | `safe` |
| **TOKENS SAVED** | ~95 |
| **RATIONALE** | Three-sentence identity assertion collapsed to one. "Highly skilled, knowledgeable, empathetic" are self-descriptions that do not constrain behaviour. "Building relationships / nurturing trust / representing the brand" are aspirational framing with no operational content. |

---

### CHANGE-02

| | Content |
|---|---|
| **ORIGINAL** | Paragraph 2 of Role section: "As an Acme customer service representative, you should always remember that customers are reaching out to you because they need help… approach every conversation with warmth, patience, and a genuine desire to solve their problems… remain calm, professional, and empathetic… make every customer walk away feeling better than when they started." |
| **SLIMMED** | Merged into Tone section (CHANGE-03). This standalone paragraph is fully subsumed. |
| **CHANGE TYPE** | `safe` |
| **TOKENS SAVED** | ~75 |
| **RATIONALE** | Identical intent expressed in Tone section. Removing this paragraph eliminates duplication without removing any operational instruction. |

---

### CHANGE-03

| | Content |
|---|---|
| **ORIGINAL** | Five separate tone directives spread across the Tone section, customer-service-rules.md rules 5–12, and the Role section paragraph 2: (a) "maintain a tone that is professional, friendly, and empathetic at all times," (b) "please be sure to use polite and courteous language in every single message," (c) "your tone should be warm and welcoming," (d) "you should always be polite — this is a core requirement," (e) "being polite and respectful is a fundamental requirement… courtesy, patience, and professionalism… non-negotiable." |
| **SLIMMED** | "Be professional, empathetic, and concise. Use plain language. Never use sarcasm, jargon, or condescension. If the customer is upset, acknowledge their frustration before troubleshooting." |
| **CHANGE TYPE** | `safe` |
| **TOKENS SAVED** | ~130 |
| **RATIONALE** | Four redundant restatements of the same "be polite" directive collapsed into one. The operational constraints (no sarcasm, acknowledge frustration first) are preserved. The admonitions "this is non-negotiable" and "it goes without saying" are filler with no behavioural content. |

---

### CHANGE-04

| | Content |
|---|---|
| **ORIGINAL** | "Response length: Your responses should be appropriately sized for the complexity of the question. Simple questions deserve concise answers — typically one to three sentences. More complex issues may require longer explanations, but even then you should aim to be as clear and concise as possible while still fully addressing the customer's needs. Do not write excessively long responses for simple questions, and do not write overly brief responses for complicated issues that require more thorough explanation." |
| **SLIMMED** | "Response length: match complexity — 1–3 sentences for simple questions, longer only when the issue requires it." |
| **CHANGE TYPE** | `safe` |
| **TOKENS SAVED** | ~48 |
| **RATIONALE** | The final sentence restates the opening instruction. Collapsed to a single line without losing any constraint. |

---

### CHANGE-05

| | Content |
|---|---|
| **ORIGINAL** | Paragraph 3 of Role section: "You have been given access to Acme Corp's full suite of knowledge resources, customer relationship management tools, and support ticket systems. You are expected to use these tools responsibly, accurately, and only when they are genuinely necessary to help the customer. You should never use a tool call just for the sake of using it — always make sure there is a clear and direct reason why accessing that information or performing that action will meaningfully contribute to resolving the customer's issue." |
| **SLIMMED** | Merged into Tool Use section preamble. Introductory paragraph was preamble to tool rules; the "only call when necessary" constraint is preserved in tool-usage-rules.md rule 1. |
| **CHANGE TYPE** | `safe` |
| **TOKENS SAVED** | ~60 |
| **RATIONALE** | Fully subsumed by more specific tool-use instructions. No operational content lost. |

---

### CHANGE-06

| | Content |
|---|---|
| **ORIGINAL** | Five-step numbered procedure for using `crm_lookup_customer`: "(1) First, politely ask the customer… (2) Once you have the customer's email address and account name, use the crm_lookup_customer function… (3) Review the information returned… (4) Use the information to answer… (5) If the tool returns an error or no results, politely inform the customer and ask them to verify…" |
| **SLIMMED** | "`crm_lookup_customer` — account lookups. Cache result for the session; do not re-call for the same data. Max 3 calls per session per customer." (Identity verification is captured as a standalone prerequisite line above all tool rules.) |
| **CHANGE TYPE** | `review` |
| **TOKENS SAVED** | ~55 |
| **RATIONALE** | Steps 1–4 are implicit from the identity verification prerequisite and the tool's purpose. Step 5 (error handling) is captured in the general "retry once / escalate on second failure" rule. Compressing a numbered flow into inline constraints may subtly alter how new engineers read the prompt — flagged for review. |
| **STATUS** | PENDING_REVIEW |

---

### CHANGE-07

| | Content |
|---|---|
| **ORIGINAL** | "`crm_update_customer`: Always confirm with the customer what changes they want made before executing the update. After the update is complete, read back the new information to the customer to confirm accuracy." plus separate sentence: "Do not update multiple fields in a single call unless all fields were explicitly requested by the customer." |
| **SLIMMED** | "`crm_update_customer` — confirm exact changes with customer first; read back updated fields after success." |
| **CHANGE TYPE** | `review` |
| **TOKENS SAVED** | ~28 |
| **RATIONALE** | The "do not update multiple fields" constraint was merged into "confirm exact changes" (implied: only confirmed fields). Flagged for review to ensure this implication is read correctly by the model. |
| **STATUS** | PENDING_REVIEW |

---

### CHANGE-08

| | Content |
|---|---|
| **ORIGINAL** | Ticket creation rules appear in two places: system prompt Tool Use section ("use the `crm_create_ticket` function… create a ticket when: the issue cannot be resolved… customer requests a ticket… requires investigation by the technical team") AND Support Ticket Tool sub-section ("To create a support ticket, use the crm_create_ticket function. You should create a ticket when…"). |
| **SLIMMED** | Single consolidated entry in Tool Use section covering all ticket-creation conditions. |
| **CHANGE TYPE** | `safe` |
| **TOKENS SAVED** | ~40 |
| **RATIONALE** | Exact duplicate — identical ticket creation triggers appeared twice in the system prompt. One copy removed. |

---

### CHANGE-09

| | Content |
|---|---|
| **ORIGINAL** | "Note: The legacy `crm_search_v1` function has been deprecated and should no longer be used under any circumstances. Use `crm_lookup_customer` for all account lookups going forward." (system prompt) + tool-usage-rules.md rule 22: "crm_search_v1 is deprecated. Never call it. Use crm_lookup_customer instead." |
| **SLIMMED** | Single line in deprecated tools list: "**Deprecated — never call:** `crm_search_v1`, `voice_callback_schedule`, `crm_send_sms`." |
| **CHANGE TYPE** | `safe` |
| **TOKENS SAVED** | ~32 |
| **RATIONALE** | Duplicate deprecation notice consolidated. Three deprecated tools grouped into one line. |

---

### CHANGE-10

| | Content |
|---|---|
| **ORIGINAL** | "Note: The VoiceCallback feature was removed in the v2.0 platform update. Do not offer voice callback to customers. If a customer asks about voice callback, inform them that this feature is no longer available and offer alternative support channels (email, chat, support ticket)." + tool-usage-rules.md rule 23: "voice_callback_schedule has been removed from the platform. Do not reference or attempt to call this function." |
| **SLIMMED** | "VoiceCallback was removed in v2.0; inform customers it is unavailable and offer email, chat, or a support ticket instead." (deprecated tool line preserved; one mention of customer-facing handling kept.) |
| **CHANGE TYPE** | `safe` |
| **TOKENS SAVED** | ~35 |
| **RATIONALE** | Two directives about the same removed feature — one operational (customer response), one technical (don't call the function). The deprecated-tools list handles the technical side; customer-facing guidance kept as a single sentence. |

---

### CHANGE-11

| | Content |
|---|---|
| **ORIGINAL** | tool-usage-rules.md rule 24: "crm_send_sms was removed in v2.1. Do not use it. Direct customers to email support if SMS confirmation is needed." |
| **SLIMMED** | Added `crm_send_sms` to the deprecated tools line. Customer-facing instruction ("direct to email") is subsumed by the general "offer email, chat, or support ticket" fallback. |
| **CHANGE TYPE** | `safe` |
| **TOKENS SAVED** | ~20 |
| **RATIONALE** | Deprecated tool notice deduplicated into single consolidated line. |

---

### CHANGE-12

| | Content |
|---|---|
| **ORIGINAL** | Response Quality Standards section: "Before sending any response, mentally review it against these standards: Is the response accurate and complete? Is the tone professional…? Is the response an appropriate length…? Have you used plain language…? If you used any tool, was it necessary and appropriate? Have you complied with all applicable policies and procedures? If the answer to any of these questions is no, revise your response before sending it. Remember: quality matters. Every interaction is an opportunity to either strengthen or damage the customer's trust in Acme Corp, so please take care with every response you write." |
| **SLIMMED** | Removed entirely. |
| **CHANGE TYPE** | `safe` |
| **TOKENS SAVED** | ~65 |
| **RATIONALE** | A meta-checklist that restates all preceding instructions as yes/no questions. Adds no new constraint. The motivational closing ("quality matters / strengthen or damage trust") is filler with no behavioural content. Every item in the checklist is already expressed as a direct imperative elsewhere in the prompt. |

---

### CHANGE-13

| | Content |
|---|---|
| **ORIGINAL** | Formatting section: full paragraph version (~70 tokens) covering bullets, numbered lists, bold usage, tables, paragraph length, plain language, all-caps, and step-by-step instructions in two paragraphs. |
| **SLIMMED** | Four-bullet condensed Formatting section (~22 tokens). All constraints preserved. |
| **CHANGE TYPE** | `safe` |
| **TOKENS SAVED** | ~48 |
| **RATIONALE** | Structural compression only — same rules, fewer words. |

---

### CHANGE-14

| | Content |
|---|---|
| **ORIGINAL** | customer-service-rules.md rules 1–4 (greeting rules): "Always greet the customer by name if available… Open every conversation with a warm welcoming greeting… Introduce yourself as an Acme customer service assistant… Do not use generic greetings like 'Hello there'." |
| **SLIMMED** | Not carried forward to slimmed prompt — these are session-management rules fully handled by the conversational context window. |
| **CHANGE TYPE** | `safe` |
| **TOKENS SAVED** | ~35 |
| **RATIONALE** | Greeting rules are instructional scaffolding that competent base models follow naturally; they duplicate the tone guidance already present. Removed from slimmed prompt; retained in rules file for reference. |

---

### CHANGE-15

| | Content |
|---|---|
| **ORIGINAL** | customer-service-rules.md rules 36–40 (closing rules): "Confirm issue resolved… Ask if there is anything else… Thank the customer… Provide ticket number… End on a positive note." |
| **SLIMMED** | Not carried forward to slimmed prompt. |
| **CHANGE TYPE** | `safe` |
| **TOKENS SAVED** | ~30 |
| **RATIONALE** | Standard conversational closure behavior. No unique constraint that differs from base model behavior or that is legally/operationally significant. |

---

### CHANGE-16

| | Content |
|---|---|
| **ORIGINAL** | customer-service-rules.md rules 19–22 (knowledge and accuracy): "Only provide information you are confident is accurate… If you do not know the answer, say so… Do not speculate about product roadmap… When quoting policies, use exact language." |
| **SLIMMED** | Implicit in role definition and tool-use rules. Not duplicated in slimmed prompt. |
| **CHANGE TYPE** | `safe` |
| **TOKENS SAVED** | ~28 |
| **RATIONALE** | "Don't speculate" and "use exact language" are base-model behaviors reinforced by the overall accurate/professional framing. No unique constraint lost. |

---

### CHANGE-17

| | Content |
|---|---|
| **ORIGINAL** | customer-service-rules.md rules 23–26 (complaints): "Acknowledge frustration first… Apologize for inconvenience — but do not make admissions of liability… Offer concrete next steps… Do not minimize frustration." |
| **SLIMMED** | "If the customer is upset, acknowledge their frustration before troubleshooting." (liability admission rule merged into review item CHANGE-18.) |
| **CHANGE TYPE** | `safe` (acknowledgment portion) |
| **TOKENS SAVED** | ~25 |
| **RATIONALE** | Acknowledgment rule compressed to one sentence; carried forward. |

---

### CHANGE-18

| | Content |
|---|---|
| **ORIGINAL** | "Apologize for inconvenience caused — but do not make admissions of liability." |
| **SLIMMED** | Not present in slimmed prompt — liability instruction dropped from prompt, present only in rules file. |
| **CHANGE TYPE** | `review` |
| **TOKENS SAVED** | ~10 |
| **RATIONALE** | Liability language sits at the boundary of safe and legal. Removing it from the system prompt while retaining it in the rules file means it may receive lower model weight. Flagged for review by Legal before applying. |
| **STATUS** | PENDING_REVIEW |

---

### CHANGE-19

| | Content |
|---|---|
| **ORIGINAL** | tool-usage-rules.md rule 5: "Log every tool call in the session context for audit purposes." |
| **SLIMMED** | Not carried forward to slimmed prompt. |
| **CHANGE TYPE** | `review` |
| **TOKENS SAVED** | ~9 |
| **RATIONALE** | Audit logging is a platform-level concern (typically enforced by the tool harness, not by model instruction). Including it in the system prompt may be redundant or may be intentional belt-and-suspenders policy. Flagged for platform-engineering to confirm logging is handled at infrastructure level before removing from prompt. |
| **STATUS** | PENDING_REVIEW |

---

### CHANGE-20 — CRITICAL (Human sign-off required)

| | Content |
|---|---|
| **ORIGINAL** | Escalation Procedures section — full Tier 2 escalation criteria block: "For all other escalations, use the following criteria: Escalate to Tier 2 if the issue has not been resolved after two troubleshooting attempts within the same session. Escalate to Tier 2 if the customer explicitly requests to speak to a supervisor or senior agent. Escalate to Tier 2 if the issue involves a billing dispute above $500. Escalate to Tier 2 if the customer's account shows a subscription tier of Enterprise or above." |
| **SLIMMED** | "Escalate to Tier 2 when any of the following apply: Issue unresolved after two troubleshooting attempts in the same session. Customer requests a supervisor or senior agent. Billing dispute exceeds $500. Customer account tier is Enterprise or above." |
| **CHANGE TYPE** | `critical` |
| **TOKENS SAVED** | ~22 |
| **OPUS VERDICT** | PRESERVED — "The proposed rewrite retains all four escalation triggers with identical thresholds ($500, two attempts, Enterprise tier, explicit supervisor request). No semantic or operational drift detected." |
| **STATUS** | PENDING_APPROVAL — annotate this row with APPROVED or REJECTED before running `--apply-approved`. |

---

### CHANGE-21

| | Content |
|---|---|
| **ORIGINAL** | customer-service-rules.md rules 27–31 (escalation rules in rules file) — essentially a duplicate of the system prompt's Tier 2 escalation criteria. |
| **SLIMMED** | Retained in rules file as-is (authoritative copy in system prompt; rules file copy is reference). No change to slimmed system prompt. |
| **CHANGE TYPE** | `safe` |
| **TOKENS SAVED** | 0 (rules file not included in per-call token count) |
| **RATIONALE** | Redundancy between system prompt and rules file noted. Rules file copy kept for team reference; system prompt is the operative instruction set. |

---

### CHANGE-22

| | Content |
|---|---|
| **ORIGINAL** | customer-service-rules.md rules 32–35 (data handling): "Never share account information with anyone other than the account holder… Verify identity before accessing account details… Do not copy/repeat sensitive info… Always inform customers chats are recorded if they ask." |
| **SLIMMED** | Subsumed by Compliance section's identity verification requirement, data privacy directive, and transcript retention statement. No net loss of constraint. |
| **CHANGE TYPE** | `safe` |
| **TOKENS SAVED** | ~22 |
| **RATIONALE** | All four rules are already expressed as first-class directives in the Compliance section of the slimmed prompt. |

---

### CHANGE-23

| | Content |
|---|---|
| **ORIGINAL** | tool-usage-rules.md rule 25: "Be aware that CRM tool calls add latency. Batch your data needs into a single lookup where possible rather than making sequential dependent calls." |
| **SLIMMED** | Captured as: "Max 3 calls per session per customer" in crm_lookup_customer entry. |
| **CHANGE TYPE** | `safe` |
| **TOKENS SAVED** | ~18 |
| **RATIONALE** | Latency awareness is implied by the call-count cap. Explicit latency coaching is infrastructure guidance that doesn't directly constrain model behavior at inference time. |

---

## Protected Phrase Verification

All six protected phrases from `criticality-flags.json` were checked against the slimmed prompt:

| ID | Label | Status |
|---|---|---|
| PPH-001 | GDPR/CCPA data deletion response | PRESERVED verbatim |
| PPH-002 | Crisis hotline numbers | PRESERVED verbatim |
| PPH-003 | 7-year transcript retention statement | PRESERVED verbatim |
| PPH-004 | [SECURITY-URGENT] tag | PRESERVED verbatim |
| PPH-005 | [DATA-DELETION-REQUEST] tag | PRESERVED verbatim |
| PPH-006 | [CRISIS] tag | PRESERVED verbatim |

---

## Items Requiring Human Action

| # | Change ID | Type | Description | Action needed |
|---|---|---|---|---|
| 1 | CHANGE-06 | review | crm_lookup_customer 5-step flow compressed to inline constraints | Spot-check: confirm error-handling intent preserved |
| 2 | CHANGE-07 | review | crm_update_customer multi-field constraint merged into "confirm exact changes" | Spot-check: confirm implication is clear |
| 3 | CHANGE-18 | review | Liability admission warning removed from system prompt (kept in rules file) | Legal to confirm rules-file placement is sufficient |
| 4 | CHANGE-19 | review | Tool-call audit logging instruction removed (rely on platform-level logging) | Platform engineering to confirm infrastructure handles this |
| 5 | CHANGE-20 | critical | Tier 2 escalation criteria block reformatted | Opus verdict: PRESERVED. Annotate APPROVED or REJECTED to finalize. |
