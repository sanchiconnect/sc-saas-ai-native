# Domain Knowledge Specification
**Program:** Mobile-First Checkout Experience
**Program ID:** PRG-MFCE-001
**Last Updated:** June 2026
**Version:** 1.0
**Review Status:** ⏸ PENDING REVIEW — Not yet reviewed. Run `/knowledge-review` with the Pod Lead and Program Lead before starting design-setup. This is a mandatory validation gate.

---

## Domain Overview

This program operates within the mobile e-commerce checkout domain, governing the end-to-end flow from cart confirmation through payment capture and order creation on mobile devices (iOS, Android, PWA). The core business activity is secure payment orchestration and order creation, with a handoff to downstream fulfillment. The domain carries significant complexity due to PCI-DSS Level 1 compliance requirements, multi-provider payment orchestration (gateway, wallet services, fraud detection), volatile mobile network conditions requiring session resilience, and international regulatory requirements across APAC and EU markets.

---

## Core Entities

### CheckoutSession
**Description:** A transient container that tracks in-progress state for a single checkout attempt. Created on checkout entry; terminated on order confirmation, expiry, or abandonment. Persisted server-side to support session recovery across network interruptions.
**Key Attributes:**
- `session_id` — UUID — system-generated; maps to server-side session store
- `customer_id` — UUID | null — null for guest checkout until email is captured
- `order_id` — UUID — FK to Order; created when session is initialized
- `step` — Enum — `IDENTITY`, `SHIPPING`, `PAYMENT`, `REVIEW`, `SUBMITTING`, `COMPLETE`
- `expires_at` — Timestamp — now + 15 min; refreshed on each customer interaction
- `recovery_email` — String | null — persisted in secure cookie for session recovery only

**Relationships:**
- Owns one `Order`
- References one `Customer` (nullable for guest sessions)

**Lifecycle States:** `ACTIVE` → `COMPLETE` | `EXPIRED` | `ABANDONED`

---

### Order
**Description:** The canonical record of a customer's purchase intent, from cart assembly through fulfillment handoff. Immutable once confirmed; captures a snapshot of line items and pricing at submission time.
**Key Attributes:**
- `order_id` — UUID — system-generated, immutable after creation
- `session_id` — UUID — FK to the CheckoutSession that created it
- `customer_id` — UUID — FK to Customer
- `status` — Enum — `DRAFT`, `PENDING_PAYMENT`, `CONFIRMED`, `FULFILLED`, `CANCELLED`
- `line_items` — List<OrderLineItem> — price-snapshotted at PENDING_PAYMENT transition
- `total_amount` — Decimal(10,2) — sum of line items + applicable shipping rate
- `currency` — ISO 4217 — derived from customer locale; default `USD`
- `shipping_address_id` — UUID — FK to ShippingAddress
- `payment_id` — UUID | null — FK to Payment; assigned on payment initiation
- `created_at` — Timestamp
- `confirmed_at` — Timestamp — null until Payment reaches AUTHORIZED or CAPTURED

**Relationships:**
- Belongs to `Customer`
- Has many `OrderLineItem`
- Has one `Payment`
- Has one `ShippingAddress`

**Lifecycle States:** `DRAFT` → `PENDING_PAYMENT` → `CONFIRMED` → `FULFILLED` → `CANCELLED`

---

### Payment
**Description:** Represents a single payment attempt against an Order. Stores only gateway-issued tokens; raw card data (PAN, CVV, expiry) never enters internal systems. A new Payment record is created for each retry attempt.
**Key Attributes:**
- `payment_id` — UUID
- `order_id` — UUID — FK to Order
- `method` — Enum — `CARD`, `APPLE_PAY`, `GOOGLE_PAY`
- `gateway_token` — String — opaque token from the payment gateway; used for captures and refunds
- `status` — Enum — `INITIATED`, `AUTHORIZED`, `CAPTURED`, `FAILED`, `REFUNDED`
- `amount` — Decimal(10,2) — must equal Order.total_amount at initiation time
- `attempt_count` — Integer — incremented per retry; max 3 before Order is cancelled
- `authorized_at` — Timestamp — null until gateway confirms authorization
- `captured_at` — Timestamp — null until capture completes

**Relationships:**
- Belongs to `Order`

**Lifecycle States:** `INITIATED` → `AUTHORIZED` → `CAPTURED` | `REFUNDED` | `FAILED`

---

### Customer
**Description:** A registered or guest user completing a checkout. Guest customers are identified by email only; they may convert to registered accounts post-purchase.
**Key Attributes:**
- `customer_id` — UUID
- `email` — String — unique; primary identifier for session recovery and order notifications
- `is_guest` — Boolean — true until explicit account registration is confirmed
- `locale` — String — BCP 47 tag (e.g., `en-US`, `zh-CN`); drives currency and address format
- `saved_addresses` — List<ShippingAddress> — maximum 5 per customer
- `saved_payment_methods` — List<PaymentMethodToken> — gateway tokens only; maximum 3 per customer

**Relationships:**
- Has many `Order`
- Has many `ShippingAddress`
- Has many `PaymentMethodToken`

---

### ShippingAddress
**Description:** A validated physical delivery address associated with an Order or saved to a Customer profile. Validation status distinguishes autocomplete-verified addresses from manually entered ones.
**Key Attributes:**
- `address_id` — UUID
- `customer_id` — UUID | null — null for one-time guest addresses
- `line1` — String — required
- `line2` — String | null — optional (apartment, suite, etc.)
- `city` — String
- `state_province` — String | null — required for US/CA; may be absent for some countries
- `postal_code` — String — format varies by country_code
- `country_code` — ISO 3166-1 alpha-2 — required
- `is_validated` — Boolean — true after autocomplete selection or explicit validation API call
- `is_default` — Boolean — at most one default per customer

**Relationships:**
- Belongs to `Customer` (nullable for guest)
- Referenced by `Order`

---

### PaymentMethodToken
**Description:** A saved, gateway-issued reference to a customer's payment instrument that enables one-click checkout without re-entering card details. Tokens are issued and managed by the payment gateway; we store the opaque reference only.
**Key Attributes:**
- `token_id` — UUID — internal reference
- `customer_id` — UUID — FK to Customer
- `gateway_token` — String — opaque token issued by payment gateway
- `method_type` — Enum — `CARD`, `APPLE_PAY`, `GOOGLE_PAY`
- `display_label` — String — e.g., "Visa ending 4242"; for UI display only; never derived from raw PAN
- `is_default` — Boolean — at most one default per customer
- `expires_at` — Date | null — card expiry date; null for wallet-based tokens

**Relationships:**
- Belongs to `Customer`

---

## Business Rules

Rules are numbered for traceability. Reference as `BR-{N}` in other specs and code.

### CheckoutSession Rules
- **BR-001:** A CheckoutSession expires after 15 minutes of inactivity; the server must invalidate the session and any associated Order in `DRAFT` or `PENDING_PAYMENT` status.
- **BR-002:** Customer email must be captured before the session advances past the IDENTITY step; this applies to both guest and returning customers.
- **BR-003:** On session recovery via a recovery link, the session is restored to the last saved step; a session in EXPIRED state cannot be recovered — the customer must start a new checkout.

### Order Rules
- **BR-010:** An Order cannot transition from `PENDING_PAYMENT` to `CONFIRMED` without an associated Payment in `AUTHORIZED` or `CAPTURED` status.
- **BR-011:** `Order.total_amount` must be recalculated whenever a line item quantity changes, a line item is added or removed, or a shipping address change affects the applicable shipping rate.
- **BR-012:** A `CANCELLED` Order cannot be reinstated; the customer must initiate a new CheckoutSession.
- **BR-013:** Order line items and prices are snapshotted at the moment the Order transitions to `PENDING_PAYMENT`; subsequent catalog price changes do not affect the Order.

### Payment Rules
- **BR-020:** Card PAN, CVV, and full expiry date must never be transmitted to, stored in, or appear in logs of internal systems; all sensitive card data is handled exclusively by the PCI-DSS Level 1 certified payment gateway.
- **BR-021:** A Payment in `FAILED` status permits the customer to retry up to 3 times (attempt_count ≤ 3); after the third failure, the Order transitions to `CANCELLED` and the customer must wait 30 minutes before initiating a new checkout.
- **BR-022:** Apple Pay and Google Pay wallet tokens are single-use; a new device wallet token must be requested for each payment attempt, including retries.
- **BR-023:** Payment gateway authorization must complete within 30 seconds; a timeout is treated as a `FAILED` status and BR-021 retry logic applies.
- **BR-024:** The Payment `amount` must exactly equal `Order.total_amount` at the time of authorization initiation; a mismatch must abort the payment attempt before it reaches the gateway.

### Address Rules
- **BR-030:** A ShippingAddress must pass country-specific format validation before the session advances past the SHIPPING step.
- **BR-031:** Address autocomplete suggestions are provided by a third-party geocoding API; if the API is unavailable, manual entry is permitted without autocomplete and `is_validated` is set to false.
- **BR-032:** Saved addresses per Customer are capped at 5; adding a sixth address requires the customer to remove an existing saved address first.

### One-Click Checkout Rules
- **BR-040:** One-click checkout is available only to authenticated (non-guest) customers with at least one saved ShippingAddress and one saved PaymentMethodToken.
- **BR-041:** A biometric authentication challenge (Face ID, Touch ID, or equivalent) must be completed before submitting a one-click payment; a failed biometric falls back to PIN/passcode once before reverting to standard checkout.

---

## State Machines

### Order States
```
DRAFT           --[customer advances past REVIEW / BR-010 precondition check]-->  PENDING_PAYMENT
PENDING_PAYMENT --[Payment authorized; BR-010]-->                                  CONFIRMED
PENDING_PAYMENT --[Payment failed 3 times; BR-021]-->                             CANCELLED
CONFIRMED       --[fulfillment system accepts order]-->                            FULFILLED
CONFIRMED       --[customer cancels within allowed window]-->                      CANCELLED
FULFILLED       --[terminal]-->                                                    (none)
CANCELLED       --[terminal]-->                                                    (none)
```

| State | Description | Entry Condition | Exit Transitions |
|-------|-------------|-----------------|-----------------|
| DRAFT | Cart assembled; session in progress | CheckoutSession initialized | Customer advances past REVIEW step |
| PENDING_PAYMENT | Awaiting payment authorization from gateway | Customer submits payment; Order advances from DRAFT | Auth success (→ CONFIRMED) or 3× failure (→ CANCELLED) |
| CONFIRMED | Payment authorized; order locked for fulfillment | Payment reaches AUTHORIZED or CAPTURED (BR-010) | Fulfillment pickup (→ FULFILLED) or cancellation window (→ CANCELLED) |
| FULFILLED | Order dispatched or delivered to customer | Fulfillment system handoff acknowledged | Terminal — no further transitions |
| CANCELLED | Order voided; cannot be reinstated (BR-012) | 3× payment failure (BR-021) or explicit cancellation | Terminal — no further transitions |

---

### Payment States
```
INITIATED  --[gateway returns authorization success]-->  AUTHORIZED
AUTHORIZED --[Order transitions to CONFIRMED]-->          CAPTURED
AUTHORIZED --[Order cancelled before capture]-->          REFUNDED
INITIATED  --[gateway declines or 30s timeout; BR-023]-->  FAILED
CAPTURED   --[refund requested post-capture]-->            REFUNDED
FAILED     --[BR-021: attempt_count < 3]-->               (new Payment INITIATED)
REFUNDED   --[terminal]-->                                 (none)
```

| State | Description | Entry Condition | Exit Transitions |
|-------|-------------|-----------------|-----------------|
| INITIATED | Payment submitted to gateway; awaiting response | Customer confirms payment | Auth response received or 30s timeout |
| AUTHORIZED | Funds held by issuing bank; not yet debited | Gateway authorization success | Order confirmed (→ CAPTURED); Order cancelled (→ REFUNDED) |
| CAPTURED | Funds debited from customer account | Order transitions to CONFIRMED | Refund request (→ REFUNDED) |
| FAILED | Authorization declined or timed out | Gateway decline or 30s timeout (BR-023) | BR-021 retry (new Payment record) or Order → CANCELLED |
| REFUNDED | Funds returned to customer | Pre-capture cancel or post-capture refund request | Terminal |

---

### CheckoutSession States
```
ACTIVE     --[15 min inactivity; BR-001]-->               EXPIRED
ACTIVE     --[Order confirmed]-->                          COMPLETE
ACTIVE     --[customer exits without completing]-->        ABANDONED
ABANDONED  --[customer taps recovery email link; BR-003]--> ACTIVE (step restored)
EXPIRED    --[terminal]-->                                  (none)
COMPLETE   --[terminal]-->                                  (none)
```

---

## Key Workflows

### 1. Standard Mobile Checkout (New or Guest Customer)
**Actor:** Mobile customer (new or guest)
**Trigger:** Customer taps "Checkout" from cart view
**Outcome:** Order in `CONFIRMED` state; confirmation email and push notification dispatched

1. System creates a `CheckoutSession` (ACTIVE) and `Order` (DRAFT)
2. Customer enters or confirms email (BR-002); session step advances to IDENTITY
3. Customer types shipping address; autocomplete suggestions offered (triggers Workflow 3)
4. System validates address format for target country (BR-030); session step → SHIPPING
5. Customer selects payment: new card, Apple Pay, or Google Pay
6. System presents full order summary; session step → REVIEW
7. Customer taps "Place Order"; session step → SUBMITTING
8. System creates `Payment` (INITIATED); submits gateway token or wallet token
9. Gateway returns authorization; Payment → AUTHORIZED; Order → CONFIRMED (BR-010)
10. CheckoutSession → COMPLETE; confirmation screen displayed; notifications dispatched

**Error Paths:**
- Address format invalid (BR-030) → inline error shown; customer corrects and resubmits
- Gateway timeout >30s (BR-023) → Payment → FAILED; retry prompt shown (BR-021)
- Authorization declined → decline reason displayed; customer may retry up to BR-021 limit
- Session idle 15 min (BR-001) → CheckoutSession → EXPIRED; Order voided; recovery email offered

---

### 2. One-Click Checkout (Returning Authenticated Customer)
**Actor:** Returning authenticated customer with saved address and PaymentMethodToken
**Trigger:** Customer taps "Checkout"; system detects qualifying saved profile (BR-040)
**Outcome:** Order confirmed in under 10 seconds

1. System loads Customer's default `ShippingAddress` and `PaymentMethodToken`
2. Single-page checkout pre-populated; customer reviews order summary
3. Customer authenticates via biometric (BR-041); system verifies challenge
4. System submits saved gateway token to payment gateway
5. Gateway authorizes; Payment → AUTHORIZED; Order → CONFIRMED (BR-010)
6. CheckoutSession → COMPLETE; confirmation screen shown; push notification dispatched

**Error Paths:**
- Biometric fails → fall back to device PIN/passcode once; second failure reverts to standard checkout (Workflow 1)
- Saved PaymentMethodToken expired → customer prompted to select alternate method or re-enter card
- Gateway decline → BR-021 retry logic; customer offered alternate payment method

---

### 3. Address Autocomplete Lookup
**Actor:** Customer entering a shipping address
**Trigger:** Customer types 3 or more characters in the address line1 input field
**Outcome:** Customer selects a validated suggestion or completes manual entry

1. Frontend debounces input and sends partial address string to backend
2. Backend queries third-party geocoding API with partial string and customer locale
3. API returns up to 5 ranked address suggestions
4. Frontend renders suggestions in a dropdown below the address field
5. Customer selects a suggestion; `ShippingAddress.is_validated` set to true
6. Address sub-fields (city, state_province, postal_code, country_code) auto-populated from API response

**Error Paths:**
- Geocoding API unavailable (BR-031) → autocomplete silently disabled; customer enters address manually; `is_validated` = false; country-format validation still applied on submit (BR-030)
- No matching suggestions returned → customer completes manual entry; format validation applied on step submission

---

### 4. Payment Retry Flow
**Actor:** Customer; system
**Trigger:** Payment.status transitions to FAILED
**Outcome:** Successful authorization on retry, or Order cancelled after 3 failures (BR-021)

1. Payment transitions to FAILED; `attempt_count` incremented
2. System displays decline reason (where available from gateway) and retry prompt
3. If `attempt_count` < 3: customer offered retry with current method or option to select alternate payment method
4. Customer confirms retry or selects alternate; new `Payment` record created (INITIATED)
5. Authorization re-attempted; returns to step 1 if FAILED again
6. If `attempt_count` = 3 after failure: Order → CANCELLED; customer shown 30-minute cooldown message and offered to start a new checkout (BR-021)

---

## Constraints & Compliance

| Constraint | Type | Applies To | Detail |
|------------|------|------------|--------|
| PCI-DSS Level 1 | Regulatory | Payment, PaymentMethodToken | No card PAN, CVV, or full expiry in internal storage or logs; mandatory payment gateway tokenization (BR-020) |
| GDPR | Regulatory | Customer, Order, ShippingAddress | EU customers have the right to erasure; EU customer data must reside in EU-region infrastructure; explicit consent required for data processing |
| APAC data localisation | Regulatory | Customer (APAC region) | Select APAC jurisdictions require in-country data residency; legal review required per target market before launch |
| WCAG 2.1 AA | Technical | Mobile Presentation Domain | All interactive elements accessible; color contrast ≥ 4.5:1; touch targets ≥ 44×44px (Apple HIG / WCAG 2.5.5) |
| Apple Pay certification | Contractual | Payment Domain | Apple Pay integration requires Apple certification before production use; certification lead time ~6–8 weeks (see risk register) |
| Google Pay certification | Contractual | Payment Domain | Google Pay requires Google certification before production use; certification lead time ~4–6 weeks (see risk register) |
| Session idle timeout | Security | CheckoutSession | Idle sessions must be invalidated server-side after 15 minutes (BR-001); client-side countdown shown at 12 minutes |

---

## Glossary

| Term | Definition | Notes |
|------|------------|-------|
| Authorization | A hold placed on customer funds by the issuing bank, confirming availability without yet debiting the account | Distinct from Capture; an authorization may expire if not captured within the gateway's window |
| Capture | The act of debiting an authorized amount from the customer's account | Triggered when Order transitions to CONFIRMED |
| Gateway Token | An opaque string issued by the payment gateway representing a specific card or wallet instrument | Replaces PAN in all internal operations; Apple/Google Pay tokens are single-use (BR-022) |
| PAN | Primary Account Number — the 16-digit card number on a payment card | Must never enter internal systems or logs (BR-020) |
| One-Click Checkout | A checkout path where a returning customer confirms a pre-populated order with a single authenticated interaction | Requires saved ShippingAddress + PaymentMethodToken; biometric auth required (BR-040, BR-041) |
| Guest Checkout | A checkout completed without a registered account; customer identified by email only | Eligible for account creation post-purchase |
| Address Autocomplete | Predictive address suggestions provided by a third-party geocoding API as the customer types | Falls back gracefully to manual entry if API is unavailable (BR-031) |
| Session Recovery | The ability to resume an ACTIVE CheckoutSession via a link sent to the customer's recovery email | Session must not be EXPIRED; step is restored to last saved position (BR-003) |
| Order Snapshot | The immutable capture of line items and prices when an Order advances to PENDING_PAYMENT | Prevents catalog price changes from affecting in-flight orders (BR-013) |
| Wallet Payment | Payment via Apple Pay or Google Pay using a device-native wallet | Tokens are single-use; platform certification required before production (BR-022) |
| One-Page Checkout | The UI design pattern where all checkout steps appear on a single scrollable view | No multi-step wizard or page reload between steps |

---

## Document Extraction Scaffold
<!-- Sections below are routing targets for doc-extraction, meeting-extraction, and code-extraction skills -->
<!-- Append extracted content under the correct section with source attribution and routing tag -->
<!-- Do not edit manually — populate via extraction skills only -->

---

## Program Context
<!-- Routing: [CONTEXT] -->
<!-- Populated by: doc-extraction (program charters, SOWs, requirements briefs) -->
<!-- Expected: program name, objectives, stakeholders, timeline, background, executive sponsor -->

> **PLACEHOLDER — PENDING CUSTOMER INPUT**
> No customer documents have been ingested. Run doc-extraction with a customer-provided program
> charter, SOW, or requirements document to populate this section.
>
> Entry format: `[Source: <doc name>, <page/section>] [CONTEXT] <extracted content>`

<!-- APPEND BELOW THIS LINE -->

---

## Customer Expectations
<!-- Routing: [EXPECTATIONS] -->
<!-- Populated by: doc-extraction (customer BRDs, wishlists), meeting-extraction (call transcripts) -->
<!-- Preserve original customer language — quote directly; do not paraphrase -->

> **PLACEHOLDER — PENDING CUSTOMER INPUT**
> No customer-authored documents have been ingested. Run doc-extraction with a BRD, requirements
> specification, or customer-provided document to populate this section.
>
> Entry format: `[Source: <doc name>, <page/section>] [EXPECTATIONS] "<exact customer language>"`

<!-- APPEND BELOW THIS LINE -->

---

## As-Is System
<!-- Routing: [AS-IS SYSTEM] -->
<!-- Populated by: doc-extraction (existing system specs, process docs), code-extraction (source code) -->
<!-- Expected: current system behavior, user roles, existing integrations, data owned, known limitations -->

> **PLACEHOLDER — PENDING CUSTOMER INPUT**
> No existing system documentation has been ingested. Run doc-extraction with system architecture
> specs or process documents — or code-extraction against existing source code — to populate.
>
> Entry format: `[Source: <doc name>, <page/section>] [AS-IS SYSTEM] <extracted description>`

<!-- APPEND BELOW THIS LINE -->

---

### Code Extraction — Module / Service Inventory
<!-- Routing: [AS-IS SYSTEM] — code-extraction sub-section -->
<!-- Populated by: code-extraction when source code files, entry points, or service directories are provided -->
<!-- Per module/service entry format:
     #### [Module/Service Name]
     [Source: <file path(s)>]
     **Purpose**: [business meaning]
     **Technology**: [language, framework, version]
     **Key Behaviors**: [bullet list]
     **External Dependencies**: [APIs, queues, services called]
     **Known Issues / Technical Debt**: [observed problems]
-->

> **PLACEHOLDER — PENDING CODEBASE INGESTION**
> No source code has been provided. Run code-extraction against existing source files to populate.

<!-- APPEND MODULE ENTRIES BELOW THIS LINE -->

---

### Code Extraction — Workflow Inventory
<!-- Routing: [AS-IS SYSTEM] — inferred business workflows from code logic -->
<!-- Populated by: code-extraction when control-flow logic is analyzable in service/controller layers -->

> **PLACEHOLDER — PENDING CODEBASE INGESTION**
> Workflows are inferred from controller/service code during extraction.

<!-- APPEND WORKFLOW ENTRIES BELOW THIS LINE -->

---

### Code Extraction — Integration Inventory
<!-- Routing: [AS-IS SYSTEM] — external systems, SDKs, and third-party calls found in code -->
<!-- Populated by: code-extraction from import analysis, HTTP client calls, SDK initializations -->

| Integration | Type | Direction | Library/SDK | Notes |
|-------------|------|-----------|-------------|-------|
| PLACEHOLDER | PENDING CODEBASE INGESTION | — | — | — |

<!-- APPEND INTEGRATION ENTRIES BELOW THIS LINE -->

---

### Code Extraction — Auth & Authorization
<!-- Routing: [AS-IS SYSTEM] — auth mechanism and permission model found in code -->
<!-- Populated by: code-extraction from middleware, decorators, JWT/session handling, RBAC checks -->

> **PLACEHOLDER — PENDING CODEBASE INGESTION**
> Auth patterns are identified from middleware and route guards during extraction.

<!-- APPEND AUTH ENTRIES BELOW THIS LINE -->

---

### Code Extraction — Extraction Summary Report
<!-- Generated by code-extraction Phase 6 after each extraction run -->
<!-- Per run: artifact name, date, stack identified, files analyzed, conflicts found, gaps, migration risks -->

> **PLACEHOLDER — PENDING CODEBASE INGESTION**
> Extraction summary is auto-generated at completion of each code-extraction run.

<!-- APPEND SUMMARY REPORTS BELOW THIS LINE -->

---

## Open Items
<!-- Routing: [OPEN ITEMS] -->
<!-- Populated automatically when extraction skills detect ambiguities, conflicts, or missing information -->
<!-- Expected: unresolved questions, risks, decisions needed, follow-up actions, conflict flags -->

> **PLACEHOLDER — PENDING CUSTOMER INPUT**
> Open items are generated automatically during extraction when ambiguities or conflicts are detected.
>
> Entry format: `[Source: <doc name>] [OPEN ITEMS] <question or risk> — Owner: <TBD>`

<!-- APPEND BELOW THIS LINE -->

---

## Meeting Extraction Scaffold
<!-- Sections below are meeting-extraction routing targets -->
<!-- Append content after each customer meeting by running meeting-extraction against the transcript -->
<!-- Do not edit manually — populate via meeting-extraction skill only -->

---

### Business Rules — Meeting-Extracted
<!-- Routing: [BUSINESS RULES] from customer meetings -->
<!-- Populated by: meeting-extraction from explicit rules stated by customers (policies, validations, approval flows) -->
<!-- Note: distinct from specs BR-001–BR-041 which are domain model rules; these are customer-stated business policies -->
<!-- Format: `- [MEETING: date] [Rule — trigger, condition, outcome, exception if stated] [Source: speaker]` -->
<!-- Flag unclear rules as: [NEEDS CLARIFICATION] -->

> **PLACEHOLDER — PENDING CUSTOMER DISCOVERY**
> No meeting transcripts have been processed. Run meeting-extraction after each customer call to capture
> explicitly stated business rules (policies, approval flows, calculations, exception handling).

<!-- APPEND BELOW THIS LINE -->

---

### Business Workflows — Meeting-Extracted
<!-- Routing: [BUSINESS WORKFLOWS] from customer meetings -->
<!-- Populated by: meeting-extraction when customers describe step-by-step business processes -->
<!-- Note: these are customer-described process workflows; distinct from technical implementation workflows above -->
<!-- Format per workflow:
     #### [Workflow Name]
     [MEETING: date] [Source: speaker]
     1. [Step 1]
     2. [Step 2]
     Notes: [exceptions, edge cases, decision points mentioned]
-->

> **PLACEHOLDER — PENDING CUSTOMER DISCOVERY**
> Business workflows are captured when customers walk through their current or expected processes.

<!-- APPEND BELOW THIS LINE -->

---

### Pain Points — Meeting-Extracted
<!-- Routing: [PAIN POINTS] from customer meetings -->
<!-- Populated by: meeting-extraction from explicit problems customers raise about the current system or process -->
<!-- Format: `- [MEETING: date] "[Quote or close paraphrase]" [Source: speaker]` -->

> **PLACEHOLDER — PENDING CUSTOMER DISCOVERY**

<!-- APPEND BELOW THIS LINE -->

---

### Risk Signals — Meeting-Extracted
<!-- Routing: [RISK SIGNALS] raised in customer meetings -->
<!-- Populated by: meeting-extraction when any participant raises concerns, warnings, or risks -->
<!-- Format: `- [MEETING: date] [Risk description] — Raised by: [speaker] — Status: [open/acknowledged/mitigated]` -->

> **PLACEHOLDER — PENDING CUSTOMER DISCOVERY**

<!-- APPEND BELOW THIS LINE -->

---

### Scope Signals — Meeting-Extracted
<!-- Routing: [SCOPE SIGNALS] from customer meetings — informal in/out/ambiguous scope statements -->
<!-- Populated by: meeting-extraction; even informal scope statements should be captured here -->
<!-- Format: `- [MEETING: date] [IN/OUT/AMBIGUOUS]: [scope item] [Source: speaker]` -->

> **PLACEHOLDER — PENDING CUSTOMER DISCOVERY**

<!-- APPEND BELOW THIS LINE -->

---

## Knowledge Review Scaffold
<!-- Sections below are populated by the knowledge-review skill during and after each review session -->
<!-- DO NOT edit manually — populate via knowledge-review session only -->
<!-- Each review session updates these sections in-place (append where noted; overwrite status fields) -->

---

### Pre-Review Status Report
<!-- Generated by knowledge-review Phase 0 before each review session -->
<!-- Summarizes extraction coverage and section completeness at time of review -->

**Knowledge Base Status:** PLACEHOLDER — PENDING REVIEW SESSION
**Last Review Run:** Not yet started — no review sessions completed
**Next Recommended Action:** Run doc-extraction, code-extraction, and meeting-extraction to populate knowledge before scheduling review

**Sources Ingested:**

| Source | Status | Last Run |
|--------|--------|---------|
| Documents (doc-extraction) | NOT RUN | — |
| Codebase (code-extraction) | NOT RUN | — |
| Meetings (meeting-extraction) | NOT RUN | — |

**knowledge.md Section Completeness at Last Review:**

| Section | Completeness | Substantive Entries | Notes |
|---------|-------------|-------------------|-------|
| Program Context | EMPTY — PENDING CUSTOMER DISCOVERY | 0 | — |
| Business Rules (meeting-extracted) | EMPTY — PENDING CUSTOMER DISCOVERY | 0 | — |
| Business Workflows | EMPTY — PENDING CUSTOMER DISCOVERY | 0 | — |
| Customer Expectations | EMPTY — PENDING CUSTOMER DISCOVERY | 0 | — |
| As-Is System | EMPTY — PENDING CODEBASE / DOC INGESTION | 0 | — |
| Constraints | EMPTY — PENDING CUSTOMER DISCOVERY | 0 | — |
| Open Items | EMPTY — PENDING EXTRACTION | 0 | — |

**features.md:** 0 requirements captured — EMPTY — PENDING CUSTOMER DISCOVERY

**Recommendation:** PLACEHOLDER — Run extraction skills before scheduling review session.

<!-- OVERWRITE STATUS FIELDS AFTER EACH PRE-REVIEW CHECK -->

---

### Section Review Status
<!-- Updated by knowledge-review Phase 1 as each section is reviewed and confirmed -->
<!-- States: PENDING REVIEW | IN REVIEW | REVIEWED [date] | FLAGGED FOR FOLLOW-UP -->

| Section | Review Status | Reviewed By | Review Date | Corrections Made | Follow-up Items |
|---------|--------------|-------------|-------------|-----------------|----------------|
| Program Context | PENDING REVIEW — AWAITING CUSTOMER VALIDATION | — | — | — | — |
| Business Rules | PENDING REVIEW — AWAITING CUSTOMER VALIDATION | — | — | — | — |
| Business Workflows | PENDING REVIEW — AWAITING CUSTOMER VALIDATION | — | — | — | — |
| Customer Expectations | PENDING REVIEW — AWAITING CUSTOMER VALIDATION | — | — | — | — |
| As-Is System | PENDING REVIEW — AWAITING CUSTOMER VALIDATION | — | — | — | — |
| Constraints | PENDING REVIEW — AWAITING CUSTOMER VALIDATION | — | — | — | — |
| Open Items | PENDING REVIEW — AWAITING CUSTOMER VALIDATION | — | — | — | — |
| Feature Requirements (features.md) | PENDING REVIEW — AWAITING CUSTOMER VALIDATION | — | — | — | — |

<!-- OVERWRITE ROWS DURING REVIEW SESSION — never delete rows, update status fields in-place -->

---

### Ambiguity & Pending Clarification Tracker
<!-- Populated by knowledge-review when entries are marked [NEEDS CLARIFICATION] during review -->
<!-- Items here are design blockers unless explicitly marked N/A by the Program Lead -->
<!-- States: OPEN | IN PROGRESS | RESOLVED [date] | N/A — [rationale] -->

> **PLACEHOLDER — PENDING REVIEW SESSION**
> Ambiguous entries and items needing clarification are surfaced and tracked here during review.
> An item is added here when: (a) a reviewer flags an entry as unclear, (b) a rule has no stated exception handling, or (c) an expectation lacks a priority signal.

| ID | Section | Ambiguous Item | Raised By | Status | Resolution |
|----|---------|----------------|-----------|--------|------------|
| AMBIG-1 | PLACEHOLDER | PENDING REVIEW | — | OPEN | — |

<!-- APPEND CLARIFICATION ITEMS BELOW THIS LINE -->

---

### Unresolved Conflicts
<!-- Populated by knowledge-review Phase 6 conflict detection after each extraction or review session -->
<!-- Items here represent contradictions between different source documents or meeting transcripts -->
<!-- States: OPEN | UNDER REVIEW | RESOLVED [date] — [resolution] | ESCALATED TO PROGRAM LEAD -->

> **PLACEHOLDER — PENDING REVIEW SESSION**
> Conflicts between extracted content from different sources are surfaced, formally tracked, and resolved here.
> Conflict resolution requires explicit sign-off from the Program Lead before it can be marked RESOLVED.

<!-- Format per conflict:
     #### CONFLICT-[n]
     **File:** [knowledge.md / features.md / design.md]
     **Existing entry:** "[text]" — [original source, date]
     **Contradicting entry:** "[text]" — [source, date]
     **Nature:** [direct contradiction / scope change / priority change / technology conflict]
     **Status:** OPEN
     **Recommended action:** [clarify with customer / escalate to Program Lead / supersede existing entry]
     **Resolved by:** PENDING
-->

<!-- APPEND CONFLICTS BELOW THIS LINE -->

---

### Knowledge Completeness Checklist
<!-- Phase 2 gap analysis — all items checked during review session against accumulated knowledge -->
<!-- [ ] = not yet checked | [x] = confirmed present and accurate | [N/A] = not applicable (rationale required) | [OPEN] = gap added to Open Items -->
<!-- Do NOT pre-check items — items are confirmed only during a live review session with the Pod / Program Lead -->

> **PLACEHOLDER — PENDING REVIEW SESSION**
> This checklist is completed during knowledge-review Phase 2. All items start unchecked.
> Items marked [OPEN] are automatically added to the Open Items section.

**Business Layer**
- [ ] Primary business objective is clearly stated and agreed
- [ ] Success criteria are measurable and agreed with the customer
- [ ] Key stakeholders with names and roles are identified
- [ ] Program timeline and key milestones are captured
- [ ] Core business rules are documented (trigger, condition, outcome, exception)
- [ ] Primary business workflows are documented (steps, decision points, actors)

**Feature Layer**
- [ ] Feature requirements captured in features.md
- [ ] All features have a priority signal (MUST HAVE / SHOULD HAVE / NICE TO HAVE)
- [ ] No features remain in "Uncategorized" without a justification
- [ ] Feature requirements trace to a customer expectation or pain point

**System Layer**
- [ ] Existing system components are documented
- [ ] Current user base and usage patterns are described
- [ ] Integration points with external systems are listed
- [ ] Data ownership and data flows are documented
- [ ] Current system pain points are captured

**Technical Layer**
- [ ] Technology stack of existing system is known
- [ ] Infrastructure and hosting model is documented
- [ ] Performance and availability characteristics are noted
- [ ] Security model and authentication mechanism are documented

**Compliance & Constraints**
- [ ] Regulatory requirements are captured (GDPR, PCI-DSS, HIPAA, etc.)
- [ ] Data residency requirements are noted
- [ ] Accessibility requirements are documented
- [ ] Budget and timeline constraints are bounded

**Design Readiness**
- [ ] No unresolved [DESIGN BLOCKER] open items remain
- [ ] Customer expectations are prioritized (FIRM / EXPLORATORY / NEEDS VALIDATION)
- [ ] All MUST HAVE features are clearly defined
- [ ] Constraints are unambiguous and agreed with the customer

<!-- UPDATE CHECKBOXES DURING REVIEW SESSION ONLY — do not pre-check -->

---

### Design Readiness Assessment
<!-- Produced by knowledge-review Phase 4 at conclusion of each review session -->
<!-- States: NOT YET ASSESSED | READY FOR DESIGN-SETUP | PROCEED WITH CAUTION | RESOLVE BLOCKERS FIRST | ADDITIONAL DISCOVERY NEEDED -->

**Overall Status:** NOT YET ASSESSED — PENDING REVIEW SESSION

**Ready for Design** *(sections with sufficient clarity to begin design-setup)*
> PLACEHOLDER — not yet assessed. Sections will be listed here after review confirms they are complete and unambiguous.

<!-- APPEND READY SECTIONS BELOW THIS LINE -->

**Proceed with Caution** *(areas with acknowledged uncertainty — design assumptions will need validation)*
> PLACEHOLDER — not yet assessed.

<!-- APPEND CAUTION AREAS BELOW THIS LINE -->

**Design Blockers** *(must resolve before design-setup begins)*
> PLACEHOLDER — not yet assessed. Any [DESIGN BLOCKER] open items will be listed here.

<!-- APPEND BLOCKERS BELOW THIS LINE -->

**Formal Recommendation:**
> PLACEHOLDER — Run knowledge-review to produce a formal design readiness recommendation.
> Expected output: [READY FOR DESIGN-SETUP] / [RESOLVE BLOCKERS FIRST] / [ADDITIONAL DISCOVERY NEEDED]

<!-- OVERWRITE RECOMMENDATION AFTER EACH REVIEW SESSION -->

---

### Reviewer Sign-Off
<!-- Completed by knowledge-review Phase 3 after a full review session is conducted -->
<!-- States: AWAITING REVIEW | UNDER REVIEW | APPROVED [date] | APPROVED WITH CONDITIONS [date] -->
<!-- Do NOT change status to APPROVED manually — approval is recorded only during a live review session -->

> **AWAITING CUSTOMER VALIDATION**
> No review session has been completed. Run `/knowledge-review` with the Pod Lead and Program Lead.
> Both reviewers must sign off before design-setup can begin.

| Reviewer | Role | Status | Date | Session Notes |
|----------|------|--------|------|--------------|
| PLACEHOLDER | Pod Lead | AWAITING REVIEW | — | — |
| PLACEHOLDER | Program Lead | AWAITING REVIEW | — | — |

**Governance Gate:** design-setup is **blocked** until both sign-offs above are set to APPROVED.

<!-- OVERWRITE ROWS AFTER REVIEW SESSION — never pre-set to APPROVED -->

---

## Changelog

| Date | Version | Author | Summary |
|------|---------|--------|---------|
| Jun 2026 | 1.0 | Sarah Chen | Initial version — derived from program charter PRG-MFCE-001 |
| 2026-06-01 | 1.1 | doc-extraction scaffold | Added extraction routing sections (Program Context, Customer Expectations, As-Is System, Open Items) — all PLACEHOLDER pending document ingestion |
| 2026-06-01 | 1.2 | meeting-extraction scaffold | Added meeting-extraction routing sections (Business Rules, Workflows, Pain Points, Risk Signals, Scope Signals) — all PLACEHOLDER pending customer discovery |
| 2026-06-01 | 1.3 | knowledge-review scaffold | Added governance sections (Pre-Review Status, Section Review Status, Ambiguity Tracker, Conflict Tracker, Completeness Checklist, Design Readiness, Reviewer Sign-Off) — all PLACEHOLDER pending review session |
