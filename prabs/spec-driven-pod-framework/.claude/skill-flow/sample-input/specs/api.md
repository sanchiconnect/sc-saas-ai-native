# API Specification
**Program:** Mobile-First Checkout Experience
**Program ID:** PRG-MFCE-001
**Last Updated:** June 2026
**Version:** 1.0
**Framework:** FastAPI 0.111 + Pydantic v2
**Pod:** Backend Pod

---

## API Foundation

| Property | Value |
|----------|-------|
| Base URL (local) | `http://localhost:8000/api/v1` |
| Base URL (prod) | `https://api.checkout.example.com/api/v1` |
| Versioning | URL path prefix — `/api/v1/` |
| Content-Type | `application/json` |
| Charset | UTF-8 |
| Date format | ISO 8601 with timezone — `2026-06-01T12:00:00Z` |
| ID format | UUID v4 string |
| Amount format | Decimal as string — `"42.00"` (preserves precision; matches database.md JSONB convention) |
| Null fields | Included as explicit `null` in responses; omit optional fields in requests |

### Global Request Headers
| Header | Required | Description |
|--------|----------|-------------|
| `Authorization` | On JWT-protected routes | `Bearer {access_token}` |
| `X-Session-ID` | On guest checkout routes | UUID of the active CheckoutSession |
| `Content-Type` | On POST / PATCH | `application/json` |
| `X-Request-ID` | Optional | Client-generated UUID; echoed as `request_id` in error responses for tracing |
| `Accept-Language` | Optional | BCP 47 locale hint; used for address format and currency display |

**Note:** Guest checkout routes accept `X-Session-ID` in place of `Authorization`. Routes that accept both are marked **Auth: Session**. Routes that require a registered account are marked **Auth: Required (JWT)**.

### CORS
```python
allow_origins = [
    "http://localhost:3000",          # local Next.js dev
    "https://checkout.example.com",   # production web
]
allow_methods = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
allow_headers = ["Authorization", "Content-Type", "X-Request-ID", "X-Session-ID", "Accept-Language"]
allow_credentials = True
```

---

## Authentication

| Property | Value |
|----------|-------|
| Mechanism | JWT RS256 Bearer tokens (design.md security spec) |
| Access token TTL | 15 minutes — aligned with CheckoutSession expiry (BR-001) |
| Refresh token TTL | 30 days — stored in `HttpOnly` secure cookie; not returned in response body |
| Signing key | RSA 2048-bit; injected from AWS Secrets Manager at ECS task startup |
| Claims | `sub` (customer_id UUID), `email`, `is_guest`, `iat`, `exp` |
| Guest sessions | No JWT issued — guest checkout identified by `X-Session-ID` header only |

```python
# JWT-protected routes
async def get_current_customer(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> CustomerContext:
    """Validate RS256 JWT. Raises 401 on invalid or expired token."""
    ...

# Session-context routes — accepts JWT (authenticated) or X-Session-ID (guest)
async def get_session_context(
    session_id: UUID | None = Header(None, alias="X-Session-ID"),
    token: str | None = Depends(optional_oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> SessionContext:
    """Raises 401 if neither credential is present or valid."""
    ...
```

---

## Error Contract

### Standard Error Response
```json
{
  "error": {
    "code": "PAYMENT_DECLINED",
    "message": "Payment authorization failed — try a different card or payment method.",
    "details": [
      { "field": "payment_method_id", "issue": "Card declined by issuing bank" }
    ],
    "request_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

### HTTP Status Code Map
| Code | Meaning | When Used |
|------|---------|-----------|
| 200 | OK | Successful GET, PATCH, non-creating POST |
| 201 | Created | Successful POST that creates a resource |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Malformed request body or query params |
| 401 | Unauthorized | Missing, expired, or invalid auth token / session |
| 402 | Payment Required | Payment authorization failed; retry may be available |
| 403 | Forbidden | Valid auth but resource belongs to another customer |
| 404 | Not Found | Resource does not exist or is soft-deleted |
| 409 | Conflict | State transition not permitted |
| 422 | Unprocessable Entity | Pydantic validation error (FastAPI default) |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Unexpected server-side failure |

### Error Code Registry
| Code | HTTP | Description |
|------|------|-------------|
| `VALIDATION_ERROR` | 422 | One or more request fields failed Pydantic validation |
| `SESSION_NOT_FOUND` | 404 | CheckoutSession not found or expired |
| `SESSION_EXPIRED` | 409 | Session status is EXPIRED; start a new checkout |
| `SESSION_STEP_INVALID` | 409 | Prerequisite step not yet complete |
| `ORDER_STATUS_CONFLICT` | 409 | Order not in the required status for this operation |
| `ORDER_CANCELLED` | 409 | Order is CANCELLED; start a new checkout (BR-012) |
| `PAYMENT_DECLINED` | 402 | Gateway declined authorization; `retry_remaining` indicates retries left |
| `PAYMENT_TIMEOUT` | 402 | Gateway did not respond within 30 seconds (BR-023) |
| `PAYMENT_LIMIT_EXCEEDED` | 409 | Third payment failure; Order cancelled (BR-021) |
| `AMOUNT_MISMATCH` | 409 | payment.amount != order.total_amount at initiation (BR-024) |
| `ADDRESS_LIMIT_EXCEEDED` | 409 | Customer already has 5 saved addresses (BR-032) |
| `TOKEN_LIMIT_EXCEEDED` | 409 | Customer already has 3 saved payment methods |
| `ONE_CLICK_INELIGIBLE` | 409 | No saved address or payment token; one-click unavailable (BR-040) |
| `UNAUTHORIZED` | 401 | Missing or invalid auth credential |
| `FORBIDDEN` | 403 | Resource belongs to a different customer |

---

## Endpoints

---

### Authentication

#### POST /auth/register
**Description:** Create a new registered customer account.
**Auth:** Public

**Request Body:** `RegisterRequest`
**Response:** `201 AuthTokenResponse`
**Errors:** `409` (email already registered), `422`
**Notes:** Creates `customers` row with `is_guest = FALSE`. Returns JWT access token immediately.

---

#### POST /auth/login
**Description:** Authenticate with email and password; receive JWT access token.
**Auth:** Public

**Request Body:** `LoginRequest`
**Response:** `200 AuthTokenResponse`
**Errors:** `401` (invalid credentials), `422`

---

#### POST /auth/refresh
**Description:** Exchange a valid refresh token for a new access + refresh token pair.
**Auth:** Public

**Request Body:** `RefreshRequest`
**Response:** `200 AuthTokenResponse`
**Errors:** `401` (expired or invalid refresh token)
**Notes:** Refresh token is rotated on each use; prior token invalidated.

---

#### POST /auth/logout
**Description:** Invalidate the caller's refresh token.
**Auth:** Required (JWT)

**Request Body:** `LogoutRequest`
**Response:** `204 No Content`
**Errors:** `401`

---### Checkout Session

#### POST /checkout/sessions
**Description:** Initialize a new CheckoutSession and DRAFT Order. Returns `session_id` used as `X-Session-ID` on all subsequent checkout requests.
**Auth:** Public

**Request Body:** `InitCheckoutRequest`
**Response:** `201 SessionStateResponse`
**Errors:** `422`

**Business Rules Applied:** BR-001 (sets `expires_at = NOW() + 15 min`)
**Notes:** If `Authorization` header is present, session is linked to that customer immediately. Guest callers receive `customer_id: null` until IDENTITY step completes.

---

#### GET /checkout/sessions/{session_id}
**Description:** Get current checkout session state including the embedded order summary. Used to restore state after network interruption.
**Auth:** Session (X-Session-ID or Bearer JWT)

**Path Parameters:**
- `session_id` — UUID

**Response:** `200 SessionStateResponse`
**Errors:** `401`, `403`, `404` (SESSION_NOT_FOUND)

---

#### PATCH /checkout/sessions/{session_id}/identity
**Description:** Submit customer email. Advances session step from IDENTITY to SHIPPING. Required for guest and authenticated customers (BR-002).
**Auth:** Session (X-Session-ID or Bearer JWT)

**Path Parameters:**
- `session_id` — UUID

**Request Body:** `IdentityStepRequest`
**Response:** `200 SessionStateResponse`
**Errors:** `401`, `403`, `404`, `409` (SESSION_EXPIRED, SESSION_STEP_INVALID)

**Business Rules Applied:** BR-002 (email must be present before step advances)
**Notes:** For authenticated customers, email is pre-populated from JWT claims; request body may be empty `{}`. For guests, `email` is required and sets `recovery_email` on the session.

---

#### PATCH /checkout/sessions/{session_id}/shipping
**Description:** Submit shipping address. Advances session from SHIPPING to PAYMENT. Triggers country-specific format validation (BR-030).
**Auth:** Session (X-Session-ID or Bearer JWT)

**Path Parameters:**
- `session_id` — UUID

**Request Body:** `ShippingStepRequest`
**Response:** `200 SessionStateResponse`
**Errors:** `401`, `403`, `404`, `409` (SESSION_STEP_INVALID), `422` (address validation failure)

**Business Rules Applied:** BR-030 (country-specific format validation), BR-031 (`is_validated` flag set to `true` if address came from autocomplete)
**Notes:** Accepts either `address_id` (saved ShippingAddress) or an inline address object. Inline addresses set `is_validated = false` unless the `autocomplete_confirmed` flag is `true` in the request.

---

#### PATCH /checkout/sessions/{session_id}/payment
**Description:** Select or change payment method. Advances step from PAYMENT to REVIEW. Also used to change payment method during a retry flow before re-confirming.
**Auth:** Session (X-Session-ID or Bearer JWT)

**Path Parameters:**
- `session_id` — UUID

**Request Body:** `PaymentStepRequest`
**Response:** `200 SessionStateResponse`
**Errors:** `401`, `403`, `404`, `409` (SESSION_STEP_INVALID)

**Business Rules Applied:** BR-022 (Stripe.js generates a fresh wallet token per call for Apple/Google Pay)
**Notes:** Accepts either `token_id` (saved PaymentMethodToken) or `payment_method_id` (Stripe one-time token from Stripe.js). Raw card data is never accepted by this endpoint. `gateway_token` is never returned in any response (BR-020).

---

#### POST /checkout/sessions/{session_id}/confirm
**Description:** Place the order. Snapshots `line_items` (BR-013), transitions Order to PENDING_PAYMENT, submits payment to Stripe, transitions to CONFIRMED on authorization success.
**Auth:** Session (X-Session-ID or Bearer JWT)

**Path Parameters:**
- `session_id` — UUID

**Request Body:** *(empty)*
**Response:** `200 OrderConfirmationResponse`
**Errors:**
- `402` (PAYMENT_DECLINED, PAYMENT_TIMEOUT) — payment failed; `retry_remaining` in error body
- `409` (PAYMENT_LIMIT_EXCEEDED) — third failure; Order cancelled; start new checkout
- `409` (ORDER_STATUS_CONFLICT, AMOUNT_MISMATCH, SESSION_EXPIRED)

**Business Rules Applied:** BR-010, BR-013, BR-021, BR-023, BR-024
**Notes:** On `402`: session step resets to PAYMENT; `attempt_count` and `retry_remaining` fields in `PaymentFailedResponse` guide the frontend retry prompt. On third failure (`retry_remaining = 0`): Order is CANCELLED (BR-012); a new checkout session must be started. On success: CheckoutSession → COMPLETE; push notification and confirmation email dispatched as background tasks.

---

#### POST /checkout/sessions/recover
**Description:** Recover an ABANDONED CheckoutSession using the signed token from the recovery email link. Restores session to the last saved step (BR-003).
**Auth:** Public (recovery token in request body)

**Request Body:** `RecoverSessionRequest`
**Response:** `200 SessionStateResponse`
**Errors:** `404` (token not found or expired), `409` (SESSION_EXPIRED — EXPIRED sessions cannot be recovered)

**Business Rules Applied:** BR-003
**Notes:** Recovery token is a short-lived signed JWT containing `session_id` and expiry (30 min). Validates that session status is ACTIVE or ABANDONED.

---

#### POST /checkout/one-click
**Description:** Single-request checkout for returning authenticated customers with saved profile. Loads default ShippingAddress and PaymentMethodToken, confirms the order in one step.
**Auth:** Required (JWT) — guest callers are rejected with 409 ONE_CLICK_INELIGIBLE

**Request Body:** `OneClickRequest`
**Response:** `200 OrderConfirmationResponse`
**Errors:** `401`, `409` (ONE_CLICK_INELIGIBLE), `402` (PAYMENT_DECLINED), `409` (PAYMENT_LIMIT_EXCEEDED)

**Business Rules Applied:** BR-040 (authenticated + saved address + saved token required), BR-041 (`biometric_token` validated before payment submission), BR-022, BR-010, BR-013, BR-024
**Notes:** `biometric_token` is a WebAuthn assertion credential from the client's Face ID / Touch ID challenge (BR-041); verified server-side before payment is submitted to Stripe. Optional `address_id` and `token_id` override the customer's defaults.

---

### Addresses

#### GET /addresses/autocomplete
**Description:** Return up to 5 address suggestions for a partial address string. Backed by Google Maps Geocoding API with 24-hour Redis cache (BR-031).
**Auth:** Session (X-Session-ID or Bearer JWT)

**Query Parameters:**
- `q` — string — required — partial address string (minimum 3 characters)
- `locale` — string — optional — BCP 47 hint for country-specific address formatting (default: `en-US`)

**Response:** `200 AddressSuggestionsResponse`
**Errors:** `400` (q < 3 characters), `401`

**Business Rules Applied:** BR-031 (graceful degradation — returns `{ "suggestions": [] }` on geocoding API unavailability; never returns 5xx)
**Notes:** Response shape matches ui-ux.md Address Autocomplete component contract exactly: `{ suggestions: [{ line1, city, state_province, postal_code, country_code }] }`.

---

### Customers

#### GET /customers/me
**Description:** Retrieve the authenticated customer's profile.
**Auth:** Required (JWT)

**Response:** `200 CustomerResponse`
**Errors:** `401`

---

#### DELETE /customers/me
**Description:** Initiate GDPR erasure for the authenticated customer. Anonymises PII, soft-deletes the record, cascades token deletion. Retains orders and payments as financial records.
**Auth:** Required (JWT)

**Request Body:** `GdprErasureRequest`
**Response:** `204 No Content`
**Errors:** `401`, `409` (active Order in PENDING_PAYMENT or CONFIRMED status — erasure blocked until resolved)

**Notes:** Triggers the 5-step erasure process in database.md. Confirmation email dispatched as a background task before anonymisation. `confirm: true` field in request body is required to prevent accidental erasure.

---

#### GET /customers/me/addresses
**Description:** List the authenticated customer's saved shipping addresses (excludes soft-deleted).
**Auth:** Required (JWT)

**Response:** `200 List[AddressResponse]`
**Errors:** `401`

---

#### POST /customers/me/addresses
**Description:** Save a new shipping address to the customer's profile.
**Auth:** Required (JWT)

**Request Body:** `AddressRequest`
**Response:** `201 AddressResponse`
**Errors:** `401`, `409` (ADDRESS_LIMIT_EXCEEDED — BR-032), `422`

**Business Rules Applied:** BR-032 (max 5 active addresses)
**Notes:** If `is_default = true`, the previous default is updated to `false` atomically in the same transaction.

---

#### PATCH /customers/me/addresses/{address_id}
**Description:** Update a saved address or toggle `is_default`.
**Auth:** Required (JWT)

**Path Parameters:**
- `address_id` — UUID

**Request Body:** `AddressPatchRequest`
**Response:** `200 AddressResponse`
**Errors:** `401`, `403`, `404`
**Notes:** Partial update — only provided fields are modified.

---

#### DELETE /customers/me/addresses/{address_id}
**Description:** Soft-delete a saved address (sets `deleted_at`).
**Auth:** Required (JWT)

**Path Parameters:**
- `address_id` — UUID

**Response:** `204 No Content`
**Errors:** `401`, `403`, `404`, `409` (address is referenced by an active CONFIRMED or PENDING_PAYMENT order)

---

#### GET /customers/me/payment-methods
**Description:** List the authenticated customer's active saved payment method tokens. Used by the Payment Method Selector component (ui-ux.md).
**Auth:** Required (JWT)

**Response:** `200 List[PaymentMethodResponse]`
**Errors:** `401`

**Notes:** Response includes `method_type`, `display_label`, `is_default` per ui-ux.md downstream requirement. `gateway_token` is NEVER returned in any response (BR-020).

---

#### POST /customers/me/payment-methods
**Description:** Save a new Stripe payment method token to the customer's profile for future one-click checkout.
**Auth:** Required (JWT)

**Request Body:** `SavePaymentMethodRequest`
**Response:** `201 PaymentMethodResponse`
**Errors:** `401`, `409` (TOKEN_LIMIT_EXCEEDED — max 3 per customer), `422`

**Notes:** Accepts a Stripe `payment_method_id` (opaque token from Stripe.js). Backend exchanges it for a vault reference via Stripe API. Raw card data never touches this endpoint (BR-020).

---

#### PATCH /customers/me/payment-methods/{token_id}
**Description:** Update a saved payment method — primarily to toggle `is_default`.
**Auth:** Required (JWT)

**Path Parameters:**
- `token_id` — UUID

**Request Body:** `PaymentMethodPatchRequest`
**Response:** `200 PaymentMethodResponse`
**Errors:** `401`, `403`, `404`

---

#### DELETE /customers/me/payment-methods/{token_id}
**Description:** Soft-delete a saved payment method token.
**Auth:** Required (JWT)

**Path Parameters:**
- `token_id` — UUID

**Response:** `204 No Content`
**Errors:** `401`, `403`, `404`

---

### Orders

#### GET /orders
**Description:** List the authenticated customer's orders, newest first. Cursor-based pagination.
**Auth:** Required (JWT)

**Query Parameters:**
- `status` — string — optional — filter by `OrderStatus` value
- `limit` — integer — optional — default `20`, max `100`
- `cursor` — string — optional — opaque cursor from previous response's `next_cursor`

**Response:** `200 PaginatedOrderResponse`
**Errors:** `401`

---

#### GET /orders/{order_id}
**Description:** Retrieve a single order with full line items and current payment summary.
**Auth:** Required (JWT)

**Path Parameters:**
- `order_id` — UUID

**Response:** `200 OrderResponse`
**Errors:** `401`, `403` (not the order owner), `404`

---

### Payments

#### GET /orders/{order_id}/payments
**Description:** List all payment attempts for an order (retry history). Up to 3 records (BR-021). Ordered by `created_at ASC`.
**Auth:** Required (JWT)

**Path Parameters:**
- `order_id` — UUID

**Response:** `200 List[PaymentResponse]`
**Errors:** `401`, `403`, `404`

**Notes:** `gateway_token` is never included in any response (BR-020).

---

#### GET /payments/{payment_id}
**Description:** Retrieve a single payment record by ID.
**Auth:** Required (JWT)

**Path Parameters:**
- `payment_id` — UUID

**Response:** `200 PaymentResponse`
**Errors:** `401`, `403`, `404`

---## Pydantic Schemas

```python
from __future__ import annotations
from decimal import Decimal
from datetime import datetime, date
from typing import Annotated, Optional
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, EmailStr

# ---------------------------------------------------------------------------
# Shared type alias — Decimal as string in JSON (BR-013 precision requirement)
# ---------------------------------------------------------------------------
MoneyAmount = Annotated[Decimal, Field(ge=0, decimal_places=2)]

# ---------------------------------------------------------------------------
# Enums — values match database.md CHECK constraints exactly
# ---------------------------------------------------------------------------
class OrderStatus(str, Enum):
    DRAFT = "DRAFT"
    PENDING_PAYMENT = "PENDING_PAYMENT"
    CONFIRMED = "CONFIRMED"
    FULFILLED = "FULFILLED"
    CANCELLED = "CANCELLED"

class PaymentStatus(str, Enum):
    INITIATED = "INITIATED"
    AUTHORIZED = "AUTHORIZED"
    CAPTURED = "CAPTURED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"

class PaymentMethod(str, Enum):
    CARD = "CARD"
    APPLE_PAY = "APPLE_PAY"
    GOOGLE_PAY = "GOOGLE_PAY"

class CheckoutStep(str, Enum):
    IDENTITY = "IDENTITY"
    SHIPPING = "SHIPPING"
    PAYMENT = "PAYMENT"
    REVIEW = "REVIEW"
    SUBMITTING = "SUBMITTING"
    COMPLETE = "COMPLETE"

class SessionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    COMPLETE = "COMPLETE"
    EXPIRED = "EXPIRED"
    ABANDONED = "ABANDONED"

# ---------------------------------------------------------------------------
# Error
# ---------------------------------------------------------------------------
class ErrorDetail(BaseModel):
    field: Optional[str] = None
    issue: str

class ErrorBody(BaseModel):
    code: str
    message: str
    details: list[ErrorDetail] = []
    request_id: Optional[UUID] = None

class ErrorResponse(BaseModel):
    error: ErrorBody

# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
class RegisterRequest(BaseModel):
    email: EmailStr
    password: Annotated[str, Field(min_length=8, max_length=128)]

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

class LogoutRequest(BaseModel):
    refresh_token: str

class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int             # 900 (15 min in seconds)
    # refresh_token delivered via HttpOnly Set-Cookie header — not in body (design.md)

class GdprErasureRequest(BaseModel):
    confirm: Annotated[bool, Field(description="Must be true to proceed with erasure")]

# ---------------------------------------------------------------------------
# Addresses
# ---------------------------------------------------------------------------
class AddressBase(BaseModel):
    line1: Annotated[str, Field(max_length=255)]
    line2: Optional[Annotated[str, Field(max_length=255)]] = None
    city: Annotated[str, Field(max_length=100)]
    state_province: Optional[Annotated[str, Field(max_length=100)]] = None  # matches database.md column name
    postal_code: Annotated[str, Field(max_length=20)]
    country_code: Annotated[str, Field(min_length=2, max_length=2)]          # ISO 3166-1 alpha-2

class AddressRequest(AddressBase):
    is_default: bool = False

class AddressPatchRequest(BaseModel):
    line1: Optional[Annotated[str, Field(max_length=255)]] = None
    line2: Optional[Annotated[str, Field(max_length=255)]] = None
    city: Optional[Annotated[str, Field(max_length=100)]] = None
    state_province: Optional[Annotated[str, Field(max_length=100)]] = None
    postal_code: Optional[Annotated[str, Field(max_length=20)]] = None
    country_code: Optional[Annotated[str, Field(min_length=2, max_length=2)]] = None
    is_default: Optional[bool] = None

class AddressResponse(AddressBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID                    # maps to shipping_addresses.address_id
    is_validated: bool
    is_default: bool
    created_at: datetime

class AddressSuggestion(BaseModel):
    line1: str
    city: str
    state_province: Optional[str] = None
    postal_code: str
    country_code: str           # matches ui-ux.md autocomplete component contract

class AddressSuggestionsResponse(BaseModel):
    suggestions: list[AddressSuggestion]  # max 5; empty list on geocoding API unavailability (BR-031)

# ---------------------------------------------------------------------------
# Payment Methods
# ---------------------------------------------------------------------------
class SavePaymentMethodRequest(BaseModel):
    payment_method_id: str      # Stripe paymentMethodId from Stripe.js — never raw card data (BR-020)
    method_type: PaymentMethod
    is_default: bool = False

class PaymentMethodPatchRequest(BaseModel):
    is_default: Optional[bool] = None

class PaymentMethodResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID                    # maps to payment_method_tokens.token_id
    method_type: PaymentMethod  # required by ui-ux.md Payment Method Selector
    display_label: str          # e.g., "Visa ending 4242"; required by ui-ux.md
    is_default: bool            # required by ui-ux.md
    expires_at: Optional[date] = None   # None for Apple Pay / Google Pay tokens
    # gateway_token is NEVER returned in any response (BR-020)

# ---------------------------------------------------------------------------
# Order line items (matches database.md line_items JSONB element schema)
# ---------------------------------------------------------------------------
class LineItemInput(BaseModel):
    product_id: UUID
    name: Annotated[str, Field(max_length=255)]
    sku: str
    quantity: Annotated[int, Field(ge=1)]
    unit_price: MoneyAmount     # serialized as string in JSON

class OrderLineItemResponse(BaseModel):
    product_id: UUID
    name: str
    sku: str
    quantity: int
    unit_price: str             # Decimal as string (matches JSONB storage)
    line_total: str             # Decimal as string

# ---------------------------------------------------------------------------
# Checkout Session
# ---------------------------------------------------------------------------
class InitCheckoutRequest(BaseModel):
    line_items: Annotated[list[LineItemInput], Field(min_length=1)]

class IdentityStepRequest(BaseModel):
    email: Optional[EmailStr] = None   # required for guests (BR-002); optional if JWT present

class ShippingStepRequest(BaseModel):
    address_id: Optional[UUID] = None          # saved ShippingAddress
    address: Optional[AddressRequest] = None   # inline new address
    autocomplete_confirmed: bool = False        # true if address came from autocomplete (sets is_validated=true)
    # Exactly one of address_id or address must be provided

class PaymentStepRequest(BaseModel):
    token_id: Optional[UUID] = None            # saved PaymentMethodToken (BR-040)
    payment_method_id: Optional[str] = None   # Stripe one-time token (BR-022)
    method: Optional[PaymentMethod] = None     # required when payment_method_id provided
    # Exactly one of: token_id  OR  (payment_method_id + method)

class RecoverSessionRequest(BaseModel):
    recovery_token: str    # signed JWT from recovery email link (BR-003)

class OneClickRequest(BaseModel):
    line_items: Annotated[list[LineItemInput], Field(min_length=1)]
    biometric_token: str                        # WebAuthn assertion from Face ID / Touch ID (BR-041)
    address_id: Optional[UUID] = None           # override customer default
    token_id: Optional[UUID] = None             # override customer default

class OrderSummary(BaseModel):
    order_id: UUID
    status: OrderStatus
    line_items: list[OrderLineItemResponse]
    total_amount: str           # Decimal as string
    currency: str               # ISO 4217
    shipping_address: Optional[AddressResponse] = None
    confirmed_at: Optional[datetime] = None

class SessionStateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    session_id: UUID
    status: SessionStatus
    step: CheckoutStep
    expires_at: datetime
    order: OrderSummary

# ---------------------------------------------------------------------------
# Order
# ---------------------------------------------------------------------------
class OrderResponse(OrderSummary):
    model_config = ConfigDict(from_attributes=True)
    customer_id: UUID
    session_id: UUID
    created_at: datetime
    updated_at: datetime

class PaginatedOrderResponse(BaseModel):
    items: list[OrderResponse]
    next_cursor: Optional[str] = None   # opaque; null when no further pages
    total: int

# ---------------------------------------------------------------------------
# Payment
# ---------------------------------------------------------------------------
class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID                    # maps to payments.payment_id
    order_id: UUID
    method: PaymentMethod
    status: PaymentStatus
    amount: str                 # Decimal as string
    attempt_count: int
    authorized_at: Optional[datetime] = None
    captured_at: Optional[datetime] = None
    created_at: datetime
    # gateway_token is NEVER included (BR-020)

class PaymentSummary(BaseModel):
    payment_id: UUID
    method: PaymentMethod
    status: PaymentStatus
    amount: str                 # Decimal as string
    authorized_at: Optional[datetime] = None

class PaymentFailedResponse(BaseModel):
    """Body returned with HTTP 402 on payment failure."""
    order_id: UUID
    payment_id: UUID
    status: PaymentStatus       # FAILED
    attempt_count: int
    retry_remaining: int        # = 3 - attempt_count; 0 means Order is now CANCELLED (BR-021)
    decline_reason: Optional[str] = None    # gateway message if available; omit if not provided

# ---------------------------------------------------------------------------
# Order Confirmation
# ---------------------------------------------------------------------------
class OrderConfirmationResponse(BaseModel):
    order: OrderResponse
    payment: PaymentSummary

# ---------------------------------------------------------------------------
# Customer
# ---------------------------------------------------------------------------
class CustomerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID                    # maps to customers.customer_id
    email: EmailStr
    is_guest: bool
    locale: str                 # BCP 47 tag
    created_at: datetime
```

---

## Rate Limiting

| Endpoint | Limit | Window | Scope |
|----------|-------|--------|-------|
| `POST /auth/login` | 10 requests | per minute | per IP |
| `POST /auth/register` | 5 requests | per minute | per IP |
| `POST /auth/refresh` | 20 requests | per minute | per IP |
| `POST /checkout/sessions/{id}/confirm` | 5 requests | per minute | per session |
| `POST /checkout/one-click` | 3 requests | per minute | per customer |
| `GET /addresses/autocomplete` | 60 requests | per minute | per session |
| Global (all other endpoints) | 300 requests | per minute | per customer / session |

Rate limit headers returned on all responses:
```
X-RateLimit-Limit: 300
X-RateLimit-Remaining: 297
X-RateLimit-Reset: 1748774460
Retry-After: 42                  # only on 429 responses
```

---

## FastAPI Implementation Pattern

```python
from fastapi import APIRouter, Depends, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.db.session import get_db
from app.auth.dependencies import get_session_context, SessionContext
from app.schemas.checkout import PaymentStepRequest, SessionStateResponse
from app.services.checkout_service import CheckoutService

router = APIRouter(prefix="/checkout/sessions", tags=["checkout"])

@router.patch(
    "/{session_id}/payment",
    response_model=SessionStateResponse,
    status_code=status.HTTP_200_OK,
)
async def patch_payment_step(
    session_id: UUID,
    payload: PaymentStepRequest,
    ctx: SessionContext = Depends(get_session_context),
    db: AsyncSession = Depends(get_db),
) -> SessionStateResponse:
    """Select or change payment method; advance session step to REVIEW."""
    service = CheckoutService(db)
    return await service.submit_payment_step(session_id, payload, ctx)
```

**Source module structure:**
```
src/
  api/v1/
    auth.py              # POST /auth/*
    checkout.py          # POST|GET|PATCH /checkout/sessions/*, POST /checkout/one-click
    addresses.py         # GET /addresses/autocomplete
    customers.py         # GET|DELETE /customers/me, /customers/me/addresses, /customers/me/payment-methods
    orders.py            # GET /orders, /orders/{id}
    payments.py          # GET /orders/{id}/payments, /payments/{id}
  services/
    checkout_service.py
    payment_service.py
    identity_service.py
    analytics_service.py
  schemas/
    auth.py  checkout.py  customers.py  orders.py  payments.py
  db/
    models/              # SQLAlchemy ORM models matching specs/database.md table definitions
    session.py
```

---

## [AS-IS] Existing API Surface
<!-- Routing: [AS-IS API] -->
<!-- Reverse-engineered from legacy source code routing, controllers, or API definition files -->
<!-- Populated by: code-extraction (source code), doc-extraction (OpenAPI / Swagger / WSDL files) -->
<!-- DO NOT edit manually — use extraction skills only -->
<!-- Note: all sections above are TO-BE design; this section captures current-state from legacy code/specs only -->

> **PLACEHOLDER — PENDING CODEBASE INGESTION**
> No source code or API definition files (OpenAPI, Swagger, WSDL) have been provided.
> Run code-extraction against existing source code or API spec files to populate this section.

### Versioning Strategy
<!-- Expected: URL versioning (/v1/), header-based, or no versioning — as observed in legacy code -->

> PLACEHOLDER — no legacy API analyzed yet.

<!-- APPEND BELOW THIS LINE -->

### Endpoint Inventory
<!-- Entry format per endpoint:
     #### [METHOD] [/path/to/endpoint]
     **Description**: [what it does]
     **Auth**: [None / API Key / Bearer JWT / Session / Other]
     **Request**: headers, path params, query params, body schema summary
     **Response**: 200 schema, error status codes
     **Notes**: deprecation status, known issues, coupling concerns
-->

> PLACEHOLDER — no endpoints reverse-engineered yet.

<!-- APPEND BELOW THIS LINE -->

### Deprecated / Unstable Endpoints
<!-- Populated by code-extraction when deprecated markers, TODO/FIXME comments, or version sunset flags are found -->

> PLACEHOLDER — no deprecation inventory available yet.

<!-- APPEND BELOW THIS LINE -->

---

## Changelog

| Date | Version | Author | Summary |
|------|---------|--------|---------|
| Jun 2026 | 1.0 | Sarah Chen | Initial spec — derived from knowledge.md v1.0 workflows, database.md v1.0 schema, design.md v1.0 stack |
| 2026-06-01 | 1.1 | code-extraction scaffold | Added [AS-IS] Existing API Surface section — PLACEHOLDER pending codebase ingestion |
| 2026-06-01 | 1.2 | design-setup scaffold | Added [TO-BE] API Design session output section — PLACEHOLDER pending design session |

<!-- ============================================================ -->
<!-- DESIGN-SETUP SKILL OUTPUT — DO NOT EDIT MANUALLY             -->
<!-- Populated by design-setup Phase 3, Domain 4                  -->
<!-- ============================================================ -->

## [TO-BE] API Design — Design Session Output
<!-- Routing: design-setup Phase 3, Domain 4 — API Design -->
<!-- Populated by: design-setup skill during structured session -->
<!-- AS-IS sections above are preserved and never overwritten -->

> **PLACEHOLDER — PENDING DESIGN REVIEW**
> No design session has been completed. Run `/design-setup` Domain 4 to populate.

### API Style & Versioning
- **API style:** [DESIGN DECISION PENDING] — Options: REST / GraphQL / gRPC / mixed
- **Versioning strategy:** [DESIGN DECISION PENDING] — Options: /v1/ URL prefix / header / content negotiation
- **Base URL pattern:** [DESIGN DECISION PENDING]

<!-- OVERWRITE AFTER DESIGN SESSION -->

### Authentication & Authorization
- **Mechanism:** [DESIGN DECISION PENDING] — Options: JWT / OAuth 2.0-OIDC / API key / session-based
- **Token issuer:** [DESIGN DECISION PENDING] — Options: internal auth service / Auth0 / Cognito / Azure AD
- **Authorization model:** [DESIGN DECISION PENDING] — Options: RBAC / ABAC / scope-based

<!-- OVERWRITE AFTER DESIGN SESSION -->

### API Gateway
- **Solution:** [DESIGN DECISION PENDING] — Options: Kong / AWS API Gateway / Azure APIM / none
- **Responsibilities:** [DESIGN DECISION PENDING] — rate limiting, auth, routing, logging

<!-- OVERWRITE AFTER DESIGN SESSION -->

### Rate Limiting
- **Default limits:** [DESIGN DECISION PENDING]
- **Burst handling:** [DESIGN DECISION PENDING]

<!-- OVERWRITE AFTER DESIGN SESSION -->

### Backward Compatibility
- **Preserved endpoints from AS-IS:** [DESIGN DECISION PENDING — pending AS-IS API inventory]
- **Deprecated endpoints with sunset dates:** [DESIGN DECISION PENDING]

<!-- OVERWRITE AFTER DESIGN SESSION -->

### Standard Response Envelope
> PLACEHOLDER — [DESIGN DECISION PENDING]
> Define the standard JSON response shape for success and error responses.
> Example structure to confirm or adjust during design session:
> `{ "data": {...}, "error": null, "meta": { "request_id": "...", "timestamp": "..." } }`

<!-- OVERWRITE AFTER DESIGN SESSION -->

### Endpoint Inventory (TO-BE)
> PLACEHOLDER — [To be elaborated in Sprint 0 detailed design]
> Full endpoint inventory is defined after API style, auth mechanism, and domain entity model are confirmed.
> See features.md for the feature requirements that will drive the endpoint list.