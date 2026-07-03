# API Specification
**Program:** {Program Name}
**Program ID:** {PRG-ID}
**Last Updated:** {Date}
**Version:** {N}
**Framework:** FastAPI {0.111+}
**Pod:** Backend Pod

---

## API Foundation

| Property | Value |
|----------|-------|
| Base URL (dev) | `http://localhost:8000/api/v1` |
| Base URL (prod) | `https://api.{domain}.com/v1` |
| Versioning | URL path prefix (`/v1/`) |
| Content-Type | `application/json` |
| Charset | UTF-8 |
| Date format | ISO 8601 with timezone: `2026-04-21T12:00:00Z` |
| ID format | UUID v4 string |
| Null fields | Included in response (explicit null); omit in requests when optional |

### Global Request Headers
| Header | Required | Description |
|--------|----------|-------------|
| `Authorization` | On protected routes | `Bearer {jwt_token}` |
| `Content-Type` | On POST/PUT/PATCH | `application/json` |
| `X-Request-ID` | Optional | Client-generated UUID for tracing |

### CORS
```python
allow_origins = ["http://localhost:3000", "https://app.{domain}.com"]
allow_methods = ["GET", "POST", "PUT", "PATCH", "DELETE"]
allow_headers = ["Authorization", "Content-Type", "X-Request-ID"]
allow_credentials = True
```

---

## Authentication

- **Mechanism:** JWT Bearer tokens (HS256 / RS256)
- **Token lifetime:** Access token: 15 min | Refresh token: 7 days
- **Issuance:** `POST /auth/login` or `POST /auth/refresh`
- **Validation:** Middleware validates signature + expiry on all protected routes
- **Claims:** `sub` (user ID), `email`, `roles`, `iat`, `exp`

```python
# Dependency injected into protected routes
async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserContext:
    ...
```

---

## Error Contract

### Standard Error Response
```json
{
  "error": {
    "code": "PAYMENT_DECLINED",
    "message": "Payment authorization failed. Please check your card details.",
    "details": [
      { "field": "payment_method", "issue": "Card declined by issuer" }
    ],
    "request_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

### HTTP Status Code Map
| Code | Meaning | When Used |
|------|---------|-----------|
| 200 | OK | Successful GET, PATCH |
| 201 | Created | Successful POST creating a resource |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Malformed request body |
| 401 | Unauthorized | Missing or invalid auth token |
| 403 | Forbidden | Valid token but insufficient permissions |
| 404 | Not Found | Resource does not exist |
| 409 | Conflict | State conflict (e.g., order already confirmed) |
| 422 | Unprocessable Entity | Validation errors (FastAPI default for Pydantic) |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Unexpected server error |

---

## Endpoints

### Authentication

#### POST /auth/login
**Description:** Authenticate with email/password; receive JWT pair
**Auth:** Public

**Request Body:** `LoginRequest`
**Response:** `200 AuthTokenResponse`
**Errors:** `401` (invalid credentials), `422` (validation)

---

#### POST /auth/refresh
**Description:** Exchange refresh token for new access token
**Auth:** Public

**Request Body:** `RefreshRequest`
**Response:** `200 AuthTokenResponse`
**Errors:** `401` (expired/invalid refresh token)

---

### Orders

#### POST /orders
**Description:** Create a new order from cart
**Auth:** Required — Bearer JWT
**Business Rules Applied:** BR-001, BR-004

**Request Body:** `CreateOrderRequest`
**Response:** `201 OrderResponse`
**Errors:** `400`, `401`, `422`

---

#### GET /orders
**Description:** List orders for the authenticated customer
**Auth:** Required

**Query Parameters:**
- `status` — string — optional — filter by order status
- `limit` — integer — optional — default: 20, max: 100
- `cursor` — string — optional — pagination cursor (opaque, from previous response)

**Response:** `200 PaginatedOrderResponse`
**Errors:** `401`

---

#### GET /orders/{order_id}
**Description:** Get a single order by ID
**Auth:** Required

**Path Parameters:**
- `order_id` — UUID

**Response:** `200 OrderResponse`
**Errors:** `401`, `403` (not owner), `404`

---

#### PATCH /orders/{order_id}
**Description:** Update order (quantity changes while in DRAFT status)
**Auth:** Required
**Business Rules Applied:** BR-002

**Path Parameters:**
- `order_id` — UUID

**Request Body:** `UpdateOrderRequest`
**Response:** `200 OrderResponse`
**Errors:** `401`, `403`, `404`, `409` (order not in DRAFT)

---

#### POST /orders/{order_id}/confirm
**Description:** Confirm order and trigger payment authorization
**Auth:** Required
**Business Rules Applied:** BR-001, BR-002

**Path Parameters:**
- `order_id` — UUID

**Response:** `200 OrderResponse`
**Errors:** `401`, `403`, `404`, `409` (already confirmed), `422`

---

### Payments

#### POST /payments
**Description:** Initiate a payment for an order
**Auth:** Required
**Business Rules Applied:** BR-010, BR-011, BR-012, BR-013

**Request Body:** `CreatePaymentRequest`
**Response:** `201 PaymentResponse`
**Errors:** `400`, `401`, `404` (order), `409` (payment already exists)

---

#### GET /payments/{payment_id}
**Description:** Get payment status
**Auth:** Required

**Path Parameters:**
- `payment_id` — UUID

**Response:** `200 PaymentResponse`
**Errors:** `401`, `403`, `404`

---

### Customers

#### GET /customers/me
**Description:** Get authenticated customer profile
**Auth:** Required

**Response:** `200 CustomerResponse`
**Errors:** `401`

---

#### GET /customers/me/addresses
**Description:** List saved addresses
**Auth:** Required

**Response:** `200 List[AddressResponse]`
**Errors:** `401`

---

#### POST /customers/me/addresses
**Description:** Add a new saved address
**Auth:** Required

**Request Body:** `CreateAddressRequest`
**Response:** `201 AddressResponse`
**Errors:** `401`, `422`

---

## Pydantic Schemas

```python
from pydantic import BaseModel, UUID4, EmailStr
from datetime import datetime
from typing import Optional, List
from enum import Enum

# --- Enums ---
class OrderStatus(str, Enum):
    DRAFT = "DRAFT"
    PENDING_PAYMENT = "PENDING_PAYMENT"
    CONFIRMED = "CONFIRMED"
    FULFILLED = "FULFILLED"
    CANCELLED = "CANCELLED"

class PaymentMethod(str, Enum):
    CARD = "CARD"
    APPLE_PAY = "APPLE_PAY"
    GOOGLE_PAY = "GOOGLE_PAY"

class PaymentStatus(str, Enum):
    INITIATED = "INITIATED"
    AUTHORIZED = "AUTHORIZED"
    CAPTURED = "CAPTURED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"

# --- Auth ---
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

class AuthTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds

# --- Orders ---
class OrderLineItemRequest(BaseModel):
    product_id: UUID4
    quantity: int  # min: 1

class CreateOrderRequest(BaseModel):
    items: List[OrderLineItemRequest]
    shipping_address_id: Optional[UUID4] = None

class UpdateOrderRequest(BaseModel):
    items: Optional[List[OrderLineItemRequest]] = None
    shipping_address_id: Optional[UUID4] = None

class OrderLineItemResponse(BaseModel):
    id: UUID4
    product_id: UUID4
    quantity: int
    unit_price: float
    subtotal: float

class OrderResponse(BaseModel):
    id: UUID4
    customer_id: UUID4
    status: OrderStatus
    items: List[OrderLineItemResponse]
    total_amount: float
    currency: str
    created_at: datetime
    updated_at: datetime
    confirmed_at: Optional[datetime]

class PaginatedOrderResponse(BaseModel):
    items: List[OrderResponse]
    next_cursor: Optional[str]
    total: int

# --- Payments ---
class CreatePaymentRequest(BaseModel):
    order_id: UUID4
    method: PaymentMethod
    gateway_token: str  # One-time token from client-side payment SDK

class PaymentResponse(BaseModel):
    id: UUID4
    order_id: UUID4
    method: PaymentMethod
    status: PaymentStatus
    amount: float
    authorized_at: Optional[datetime]
    created_at: datetime

# --- Addresses ---
class CreateAddressRequest(BaseModel):
    line1: str
    line2: Optional[str] = None
    city: str
    state: Optional[str] = None
    postal_code: str
    country: str  # ISO 3166-1 alpha-2
    is_default: bool = False

class AddressResponse(BaseModel):
    id: UUID4
    line1: str
    line2: Optional[str]
    city: str
    state: Optional[str]
    postal_code: str
    country: str
    is_default: bool
    is_validated: bool

# --- Customers ---
class CustomerResponse(BaseModel):
    id: UUID4
    email: EmailStr
    is_guest: bool
    created_at: datetime
```

---

## Rate Limiting

| Endpoint Group | Limit | Window |
|---------------|-------|--------|
| `POST /auth/*` | 10 requests | per minute, per IP |
| `POST /payments` | 5 requests | per minute, per user |
| Global (all endpoints) | 300 requests | per minute, per user |

Rate limit headers returned on all responses:
```
X-RateLimit-Limit: 300
X-RateLimit-Remaining: 297
X-RateLimit-Reset: 1714651260
```

---

## Changelog

| Date | Version | Author | Summary |
|------|---------|--------|---------|
| {Date} | 1.0 | {Name} | Initial API spec |
