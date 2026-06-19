---
type: index
repo: sc-saas-3rdparty-webservices
updated: 2026-06-19
---

# 3rd-Party Webservices Module Specs — Index

All 7 `sc-saas-3rdparty-webservices` modules have a `module.spec.md`. This service is a **stateless integration gateway** — no database, no tenant context. Every module proxies one third-party provider and is called exclusively by `sc-saas-backend`.

> **How to use:** When working on a module, read its spec first — it records the route(s), DTO fields, env vars, external API call format, and error handling. When adding a new proxy endpoint, also update the matching `core/services/*.service.ts` in `sc-saas-backend` and this index.

---

## Module inventory

| Module | Spec | Route(s) | Provider | Backend caller |
|---|---|---|---|---|
| `sms` | [spec](../sc-saas-3rdparty-webservices/src/modules/sms/module.spec.md) | `POST api/v1/sms/send-otp` | Auth.key.io | `sc-saas-backend/src/core/services/sms.service.ts` |
| `sendGrid` | [spec](../sc-saas-3rdparty-webservices/src/modules/sendGrid/module.spec.md) | `POST api/v1/sendgrid/send-email`, `POST api/v1/sendgrid/template/send-email` | SendGrid | `sc-saas-backend/src/core/services/ses-email.service.ts` |
| `ses` | [spec](../sc-saas-3rdparty-webservices/src/modules/ses/module.spec.md) | `POST api/v1/ses/send-email` | AWS SES | `sc-saas-backend/src/core/services/ses-email.service.ts` |
| `cometChat` | [spec](../sc-saas-3rdparty-webservices/src/modules/cometChat/module.spec.md) | `POST api/v1/comet-chat/...` | CometChat | `sc-saas-backend/src/core/services/comet-chat.service.ts` |
| `videoSDK` | [spec](../sc-saas-3rdparty-webservices/src/modules/videoSDK/module.spec.md) | `POST api/v1/video-sdk/...`, `POST api/v1/video-sdk/v2/...` | VideoSDK | `sc-saas-backend/src/core/services/video-sdk.service.ts` |
| `shortIo` | [spec](../sc-saas-3rdparty-webservices/src/modules/shortIo/module.spec.md) | `POST api/v1/short-io/shorten` | short.io | `sc-saas-backend/src/core/services/url.service.ts` |
| `convertKit` | [spec](../sc-saas-3rdparty-webservices/src/modules/convertKit/module.spec.md) | `POST api/v1/convert-kit/...` | ConvertAPI | `sc-saas-backend/src/core/services/convertapi.service.ts` |

---

## Architecture notes

- **Stateless leaf node.** No DB, no tenant state. All credentials come from `.env`. This service never calls back into any SanchiSaaS repo.
- **Internal-only.** No auth on any endpoint — the service relies on network-level trust (only `sc-saas-backend` should reach it). CORS is wide-open (`origin: true`) — acceptable because it must not be public-internet-accessible.
- **Single caller.** Only `sc-saas-backend` calls this service via `THIRD_PARTY_SERVICE_BASE_URL`. If any endpoint changes, the matching backend service file must change too.
- **Body size limit: 250 MB.** Configured in `main.ts` for all content types — required for document conversion payloads.

---

## Security findings summary

| Severity | Module | Finding |
|---|---|---|
| 🟠 High | all | No auth on any endpoint — relies entirely on network isolation. If this service is exposed to the public internet (misconfigured firewall/proxy), any caller can invoke third-party APIs billed to the platform. |
| 🟠 High | all | CORS `origin: true` — all origins allowed. Combined with no auth, a browser exploit on any same-network host could reach these endpoints. |
| 🟡 Medium | `convertKit` | Large body limit (250 MB) on all content types including JSON — potential DoS vector if not network-isolated. |
