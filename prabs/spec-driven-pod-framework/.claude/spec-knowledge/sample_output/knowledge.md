# Domain Knowledge Specification
**Program:** Mobile-First Checkout Experience
**Program ID:** PRG-SAMPLE-001
**Last Updated:** April 2026
**Version:** 1.0

---

## Domain Overview

This program operates in the e-commerce checkout domain, covering the end-to-end flow from cart review to order confirmation on mobile devices. The core business activity is payment capture and order creation. The domain is complex due to PCI-DSS compliance requirements, multi-party payment orchestration (gateway, fraud engine, bank), and the need to maintain session integrity across intermittent mobile connections.

---

## Core Entities

### Order
**Description:** Represents a customer's intent to purchase one or more items, progressing from cart to fulfillment.
**Key Attributes:**
- `order_id` — UUID — system-generated, immutable
- `customer_id` — UUID — FK to Customer
- `status` — Enum — see State Machine below
- `total_amount` — Decimal(10,2) — sum of line items + shipping; recalculated on change
- `currency` — ISO 4217 — default `USD`
- `created_at` — Timestamp
- `confirmed_at` — Timestamp — null until payment authorized

**Relationships:**
- Has many `OrderLineItem`
- Belongs to `Customer`
- Has one `Payment`
- Has one `ShippingAddress`

**Lifecycle States:** `DRAFT` → `PENDING_PAYMENT` → `CONFIRMED` → `FULFILLED` → `CANCELLED`

---

### Payment
**Description:** Represents a single payment attempt against an Order. Card data never stored; only gateway tokens.
**Key Attributes:**
- `payment_id` — UUID
- `order_id` — UUID — FK to Order
- `gateway_token` — String — returned by payment gateway; used for captures/refunds
- `method` — Enum — `CARD`, `APPLE_PAY`, `GOOGLE_PAY`
- `status` — Enum — `INITIATED`, `AUTHORIZED`, `CAPTURED`, `FAILED`, `REFUNDED`
- `amount` — Decimal(10,2)
- `authorized_at` — Timestamp

**Relationships:**
- Belongs to `Order`

---

### Customer
**Description:** A registered or guest user completing a checkout.
**Key Attributes:**
- `customer_id` — UUID
- `email` — String — unique; used for session recovery
- `is_guest` — Boolean
- `saved_addresses` — List\<Address\>
- `saved_payment_methods` — List\<PaymentMethodToken\> — gateway tokens only

---

### ShippingAddress
**Description:** A physical delivery address associated with an order.
**Key Attributes:**
- `address_id` — UUID
- `line1`, `line2` — String
- `city`, `state`, `postal_code`, `country` — String
- `is_validated` — Boolean — set after autocomplete verification

---

## Business Rules

### Order Rules
- **BR-001:** An Order cannot transition to `CONFIRMED` without a Payment in `AUTHORIZED` or `CAPTURED` status.
- **BR-002:** `total_amount` must be recalculated whenever a line item is added, removed, or quantity changed.
- **BR-003:** A `CANCELLED` order cannot be reinstated; a new Order must be created.
- **BR-004:** Guest orders must capture email before proceeding past cart review.

### Payment Rules
- **BR-010:** Card PAN, CVV, and expiry must never be stored in internal systems; all sensitive data is handled exclusively by the payment gateway.
- **BR-011:** A Payment in `FAILED` status allows the customer to retry up to 3 times before the Order is locked for 15 minutes.
- **BR-012:** Apple Pay and Google Pay tokens are single-use; a new token must be requested for each payment attempt.
- **BR-013:** Payment authorization must complete within 30 seconds or be treated as a timeout failure.

### Session Rules
- **BR-020:** An authenticated session expires after 15 minutes of inactivity.
- **BR-021:** Customer email is persisted in a secure cookie for session recovery; no other PII is cached client-side.

---

## State Machines

### Order States
```
DRAFT --[customer confirms cart]--> PENDING_PAYMENT
PENDING_PAYMENT --[payment authorized]--> CONFIRMED
PENDING_PAYMENT --[payment failed x3]--> CANCELLED
CONFIRMED --[fulfillment system picks up]--> FULFILLED
CONFIRMED --[customer cancels within window]--> CANCELLED
```

| State | Description | Entry Condition | Exit Transitions |
|-------|-------------|-----------------|-----------------|
| DRAFT | Cart is being assembled | Order created | Customer confirms cart |
| PENDING_PAYMENT | Awaiting payment authorization | Cart confirmed | Auth success or 3x failure |
| CONFIRMED | Payment authorized; order locked | Payment authorized | Fulfillment pickup or cancel |
| FULFILLED | Order shipped / delivered | Fulfillment system | Terminal |
| CANCELLED | Order voided | Failure or cancellation | Terminal |

---

## Key Workflows

### One-Click Checkout (Returning Customer)
**Actor:** Returning authenticated customer
**Trigger:** Customer taps "Buy Now" on product page
**Outcome:** Order confirmed in under 10 seconds

1. System loads saved default address and payment method token
2. Customer reviews pre-filled order summary
3. Customer taps "Confirm & Pay" (or uses biometric)
4. System submits token to payment gateway for authorization
5. Gateway returns authorization; system transitions Order → CONFIRMED
6. Confirmation screen shown; push notification dispatched

**Error Paths:**
- Gateway timeout (>30s) → show retry prompt; BR-013 applies
- Authorization declined → show decline reason; BR-011 retry logic applies

---

## Constraints & Compliance

| Constraint | Type | Applies To | Detail |
|------------|------|------------|--------|
| PCI-DSS Level 1 | Regulatory | Payment, Customer | No card data in internal storage or logs; gateway tokenization mandatory |
| WCAG 2.1 AA | Technical | Checkout UI | All interactive elements accessible; contrast ≥ 4.5:1 |
| GDPR (EU customers) | Regulatory | Customer, Order | Right to erasure; data residency in EU for EU customers |
| Session timeout 15min | Security | Session | Idle sessions must be invalidated server-side |

---

## Glossary

| Term | Definition | Notes |
|------|------------|-------|
| Gateway Token | An opaque reference returned by the payment gateway representing a card or wallet; used for subsequent operations without re-transmitting card data | Never store the raw PAN |
| PAN | Primary Account Number — the 16-digit card number | Must never enter our systems |
| One-Click Checkout | A checkout path where a returning customer confirms a pre-filled order with a single interaction | Requires saved address + payment method |
| Authorization | A hold placed on a customer's funds by the issuing bank, confirming availability | Distinct from Capture (actual debit) |
| Capture | The act of debiting an authorized amount from the customer's account | Happens after Order → CONFIRMED |
| Guest Checkout | A checkout completed without a registered account; requires email capture | Converts to registered account post-purchase if opted in |

---

## Changelog

| Date | Version | Author | Summary |
|------|---------|--------|---------|
| Apr 2026 | 1.0 | Sarah Chen | Initial version |
