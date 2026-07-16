# SanchiSaaS Platform
## Third-Party Services & Sub-Processor Inventory

---

**Document Type:** Third-Party Services Inventory
**Product:** SanchiSaaS — Incubator & Accelerator Management Platform
**Version:** 1.0
**Date:** July 2026
**Prepared For:** Internal Security / Compliance Review
**Classification:** Internal — Confidential
**Companion Documents:** SanchiSaaS Technical Architecture Document (TAD) v1.0 §7 (Integration Architecture, vendor-neutral)

---

## Purpose

This document lists every external, named third-party service the SanchiSaaS codebase integrates with, grounded directly in source (environment configuration schemas and service files), not in operational/company tooling (CRM, helpdesk, project tracking). It exists to support vendor/sub-processor review, data-flow mapping, and security compliance documentation (e.g. the "Monitoring tools" / sub-processor sections of an information security policy).

Unlike the client-facing FRS/SRS/TAD/DDD documents — which deliberately describe integrations in vendor-neutral terms (e.g. "a third-party video-conferencing SDK") to avoid tying the product's public specification to a specific commercial vendor — this document intentionally **names** the actual vendor behind each integration, for internal compliance use only. Do not share this document externally without review; vendor names and architecture detail here are more specific than what is disclosed in the client-facing specs.

---

## Summary Table

| Category | Vendor | Purpose | Integrated In |
|---|---|---|---|
| Cloud Storage & CDN | **AWS S3** | File storage — uploads, documents, avatars | `sc-saas-backend`, `sc-saas-3rdparty-webservices`, `ai-startups-analyzer` |
| CDN | **AWS CloudFront** | Signed URLs for private document delivery | `sc-saas-backend` |
| Media Processing | **AWS MediaConvert** | Video transcoding | `sc-saas-backend` |
| Database | **MySQL** (self-hosted/managed) | Primary data store, database-per-tenant | all repos |
| SMS / WhatsApp | **AuthKey.io** | OTP delivery, WhatsApp template messaging | `sc-saas-3rdparty-webservices` (`sms` module), templates configured in `sc-saas-backend` |
| Email | **SendGrid** | Transactional email | `sc-saas-3rdparty-webservices` (`sendGrid` module) |
| Email (fallback) | **AWS SES / SMTP** | Fallback email delivery | `sc-saas-3rdparty-webservices` (`ses` module) |
| Video | **VideoSDK** | Meetings, panel interviews, pitch recording | `sc-saas-3rdparty-webservices` (`videoSDK` module) |
| Document Conversion | **ConvertAPI** | Pitch deck PPT → PNG conversion | `sc-saas-3rdparty-webservices` (`convertKit` module) |
| Image CDN | **ImageKit** | Image optimization/delivery | `sc-saas-frontend` |
| URL Shortening | **Short.io** | Short/action links (invites, notifications) | `sc-saas-3rdparty-webservices` (`shortIo` module) |
| Payments | **Razorpay, Stripe, Easebuzz** | Payment gateway processing (tenant-selectable) | `sc-saas-backend/src/modules/payment-management/services/` |
| AI / LLM | **Google Gemini** | Startup application scoring (`DEFAULT_PROVIDER=google`; OpenAI/Anthropic supported but not active) | `ai-startups-analyzer` |
| Search Enrichment | **Serper** | Search-based enrichment for AI scoring | `ai-startups-analyzer` |
| Web Scraping | **Firecrawl** | Website-content enrichment for AI scoring | `ai-startups-analyzer` |
| Product Analytics | **Mixpanel** | Client-side usage analytics | `sc-saas-frontend` |
| External Platform | **PowerPitch** (`power-pitch-sanchiconnect-api`) | Video pitch session management (sister SanchiConnect product) | `sc-saas-backend` (`power-pitch-external.service.ts`) |

---

## Detail by Category

### 1. Cloud Infrastructure

- **AWS S3** — object storage for all uploaded files (pitch decks, supporting documents, avatars, chat/community attachments). Bucket, region, and credentials configured per-service via `AMAZON_S3_*` / `AWS_*` environment variables in `sc-saas-backend`, `sc-saas-3rdparty-webservices`, and `ai-startups-analyzer` independently — each service holds its own credentials, there is no shared bucket-access layer.
- **AWS CloudFront** — signs time-limited URLs for private document access (`cloudfront-private-key.pem`, intentionally committed in `sc-saas-backend` per that repo's guardrails).
- **AWS MediaConvert** — used for video transcoding jobs (`AWS_MEDIACONVERT_ENDPOINT`, `AWS_MEDIACONVERT_ROLE_ARN` in `sc-saas-backend`).
- **MySQL** — the platform's only database engine, used by every repo. `sanchiconnect-saas-tenants` and `sc-saas-backend` each own their own schema; database-per-tenant model for business data.

### 2. Communications

- **AuthKey.io** — SMS/OTP and WhatsApp Business API messaging. Credentials (`AUTHKEYIO_APIKEY`, `AUTHKEYIO_SENDERID`, `AUTHKEYIO_OTPTEMPLATEID`, `MESSAGE_API_URL`) live in `sc-saas-3rdparty-webservices`; message template identifiers (`WA_TEMP_*`) are configured in `sc-saas-backend` and passed through the gateway at send time — the backend never talks to AuthKey.io directly.
- **SendGrid** — transactional email (registration, notifications, digests). API key (`SENDGRID_KEY`) lives in `sc-saas-3rdparty-webservices`.
- **AWS SES / SMTP** — fallback/alternate email delivery path alongside SendGrid.

### 3. Real-Time & Media

- **VideoSDK** — powers one-on-one meetings, panel interviews, and pitch video recording, invoked from the Member Web Application with session details supplied by the backend at meeting-creation time.
- **ConvertAPI** — converts uploaded pitch decks (PPTX) into per-slide PNG images for in-app viewing.

### 4. Frontend-Facing Services

- **ImageKit** — image CDN/transformation layer for avatars, logos, and other user-uploaded images displayed in the Member Web Application (`imageKitBaseUrl` in `sc-saas-frontend` environment config).
- **Short.io** — generates short action links used in notification emails/messages (login links, registration links, action confirmations).
- **Mixpanel** — client-side product analytics, loaded in the Member Web Application (`mixPanelKey`).

### 5. Payments

Three gateway integrations exist side by side in `sc-saas-backend/src/modules/payment-management/services/`: **Razorpay**, **Stripe**, and **Easebuzz**. The active gateway(s) are tenant-configurable, consistent with the platform's "support integration with multiple third-party providers per capability" design principle (see SRS §2.6.3).

### 6. AI Evaluation (ai-startups-analyzer)

- **Google Gemini** — LLM provider for automated startup application scoring, selected via the `DEFAULT_PROVIDER` environment variable (currently `google`). The codebase also supports `openai`/`anthropic` as alternate providers behind the same variable, but Google Gemini is the one active provider in use.
- **Serper** — optional search-API enrichment step (`ENABLE_SEARCH_ENRICHMENT`) that supplements the LLM's context with live web search results before scoring.
- **Firecrawl** — optional website-scraping enrichment step (`ENABLE_WEBSITE_ENRICHMENT`) that pulls a startup's own website content into the scoring context.

### 7. Cross-Workspace External Platform

- **PowerPitch** (`power-pitch-sanchiconnect-api`) — a separate SanchiConnect product, not a commercial third party, but architecturally external to this workspace. `sc-saas-backend`'s `power-pitch-external.service.ts` calls its `/v1/externals/*` endpoints (session creation, video CRUD, transcript retrieval) using an `x-hostname` header for tenant identity and a cached, auto-refreshed session token.

---

## Internal Operational Tooling by Department

Unlike the sections above (verified directly against source code), this section is compiled from team responses — tools used operationally by each department, not integrated into the product codebase. Updated as teams confirm their tooling.

| Department | Tool | Used For | Users |
|---|---|---|---|
| Finance | **Zoho** | Tracking revenue, collections, and expenses |
| Company-wide | **Google Workspace** | Team email, docs, drive, calendar |
| Marketing | **Xemail** | Email marketing |
| Marketing | **Canva** | Design |
| Marketing | **Ampli** | Social media automation |
| Marketing | **Levo** | Website automation |
| Company-wide | **ChatGPT Teams** | AI assistance (general use) |
| Company-wide | **Claude** | AI assistance |

---

## Explicitly Not Integrated (in code)

The following tools sometimes appear in generic compliance/monitoring templates but are **not** present anywhere in the SanchiSaaS codebase as product integrations. Per the table above, some are confirmed as legitimate internal operational tooling for the teams running the business — but they are not sub-processors of platform data via source code and should not be listed as such in that capacity:

- Slack
- Zoho (CRM / Desk) — see Internal Operational Tooling above for confirmed Finance usage
- Rocket Lane
- Google Workspace / G Suite — see Internal Operational Tooling above for confirmed company-wide usage
- Box
- MongoDB (the platform is exclusively MySQL — no document-store engine is used anywhere)

---

## Maintenance Note

This inventory reflects the state of each repo's environment-configuration schema and service layer as of the document date above. Any new external API call, SDK, or credential added to `validation-schema.ts` / `configuration.ts` / `.env.example` in any repo should be added here. This document is not auto-generated — re-verify against source before relying on it for a compliance submission.
