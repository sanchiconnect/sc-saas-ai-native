# SanchiSaaS Platform
## Technical Architecture Document

---

**Document Type:** Technical Architecture Document (TAD)
**Product:** SanchiSaaS — Incubator & Accelerator Management Platform
**Modules Covered:** Member Web Application, Administration Panel
**Version:** 1.0
**Date:** July 2026
**Prepared For:** Client Technical Review
**Companion Documents:** SanchiSaaS Functional Requirement Specification (FRS) v1.0; SanchiSaaS System Requirement Specification (SRS) v1.0
**Classification:** Confidential

---

## Table of Contents

1. Introduction
   1.1 Purpose
   1.2 Audience
   1.3 Scope
   1.4 References
2. Architecture Overview
   2.1 Architectural Style
   2.2 High-Level Architecture
   2.3 Component Inventory
3. Member Web Application Architecture
   3.1 Technology Stack
   3.2 Application Structure
   3.3 State Management
   3.4 Client-Server Communication
   3.5 Real-Time Communication
   3.6 Progressive Web App Capabilities
4. Administration Panel Architecture
   4.1 Technology Stack
   4.2 Application Structure
   4.3 Multi-Tenant Data Access Pattern
   4.4 Session & Templating Model
   4.5 Asynchronous Interaction Pattern
5. Backend Services Architecture (Consumed Interfaces)
   5.1 API Design Principles
   5.2 Tenant Resolution & Bootstrapping
   5.3 Feature Configuration Architecture
   5.4 Notification Architecture
6. Data Architecture
   6.1 Multi-Tenant Data Model
   6.2 Core Data Domains
   6.3 File & Media Storage
7. Integration Architecture
   7.1 Payments
   7.2 Communications (Email, SMS, WhatsApp)
   7.3 Video Conferencing
   7.4 Real-Time Messaging
   7.5 AI-Assisted Evaluation
   7.6 Search
   7.7 CRM Synchronization
   7.8 Single Sign-On
8. Security Architecture
   8.1 Authentication Model
   8.2 Authorization & Access Control
   8.3 Tenant Data Isolation
   8.4 Transport & Storage Security
   8.5 Auditability
9. Deployment Architecture
   9.1 Environment Strategy
   9.2 Deployment Topology
   9.3 Content Delivery
   9.4 Release Model
10. Cross-Cutting Concerns
    10.1 Logging & Monitoring
    10.2 Error Handling
    10.3 Caching Strategy
    10.4 Configuration Management
11. Appendices
    A. Technology Stack Summary
    B. Component Interaction Diagram
    C. Glossary

---

## 1. Introduction

### 1.1 Purpose

This Technical Architecture Document (TAD) describes how the SanchiSaaS platform is built: its component decomposition, technology choices, data architecture, integration points, and security and deployment model. It translates the behavioral requirements in the Functional Requirement Specification (FRS) and the system-level requirements in the System Requirement Specification (SRS) into a concrete architectural design, for a technical audience.

### 1.2 Audience

This document is intended for client-side technical stakeholders, solution architects, integration engineers, and security/compliance reviewers who need to understand how the platform is constructed in order to evaluate, extend, or integrate with it.

### 1.3 Scope

Consistent with the FRS and SRS, this document focuses on the architecture of the two client-facing applications — the **Member Web Application** and the **Administration Panel** — and describes the backend services and third-party integrations they depend on to the extent needed to explain those two applications' behavior. It does not provide a full architectural specification of the backend services or the tenant-provisioning control plane in their own right.

### 1.4 References

- SanchiSaaS Functional Requirement Specification (FRS), v1.0
- SanchiSaaS System Requirement Specification (SRS), v1.0

---

## 2. Architecture Overview

### 2.1 Architectural Style

The platform follows a **layered, service-oriented architecture** with a clear separation between presentation, application/business-logic, and data layers. The two client-facing applications are architecturally independent front ends, each communicating with backend services exclusively through versioned HTTP APIs (and, for real-time features, WebSocket channels) — neither application accesses a database directly.

Key architectural principles applied throughout:

- **Separation of concerns** — presentation, business logic, and data persistence are implemented as distinct, independently deployable layers.
- **API-first integration** — every cross-boundary interaction (between the two front ends, backend services, and third parties) is mediated by a defined API contract.
- **Configuration over code** — tenant-specific behavior (branding, enabled features, custom forms, evaluation criteria) is expressed as data-driven configuration rather than per-tenant code branches.
- **Tenant isolation by design** — every data-access path is scoped to a single resolved tenant, enforced at the point of data access rather than left to caller discipline.

### 2.2 High-Level Architecture

```
                        End Users
                 (Members)      (Administrators)
                     |                  |
                     v                  v
        +-------------------+  +-------------------+
        |  Member Web App   |  | Administration    |
        |  (Presentation)   |  | Panel              |
        +-------------------+  +-------------------+
                     |                  |
                     +--------+---------+
                              |
                              v
              +----------------------------------+
              |     Business API Services          |
              |  (application logic, workflow,     |
              |   validation, orchestration)        |
              +----------------------------------+
                 |            |              |
                 v            v              v
        +---------------+ +----------+  +---------------------+
        | Tenant Control | | Data     |  | Integration Gateway |
        | Plane          | | Layer    |  | (3rd-party services)|
        | (identity,     | | (per-    |  |                     |
        |  branding,     | | tenant   |  |  payments, email,   |
        |  feature flags)| | database)|  |  SMS/WhatsApp,      |
        +---------------+ +----------+  |  video, storage,    |
                                          |  AI evaluation,     |
                                          |  search, CRM, SSO   |
                                          +---------------------+
```

### 2.3 Component Inventory

| Component | Role |
|---|---|
| Member Web Application | Single-page web application serving all member-facing functionality described in FRS §3. |
| Administration Panel | Server-rendered web application serving all administrative functionality described in FRS §4. |
| Business API Services | Backend services implementing core business workflows, validation, and data access; the single API surface both front ends consume for business data. |
| Tenant Control Plane | A dedicated service resolving tenant identity from the requesting domain and serving each tenant's branding and feature configuration. |
| Data Layer | Per-tenant relational databases holding all business data. |
| Integration Gateway | A set of services and direct integrations bridging the platform to external providers (Section 7). |

---

## 3. Member Web Application Architecture

### 3.1 Technology Stack

| Concern | Technology |
|---|---|
| Application Framework | Angular (component-based single-page application framework) |
| State Management | A centralized, reactive state store (Redux-pattern: actions, reducers, effects, selectors) |
| Delivery Model | Progressive Web Application (installable, service-worker-backed) |
| Styling | Component-scoped stylesheets with a shared design-system layer |

### 3.2 Application Structure

The application is organized into feature modules, each owning a bounded area of functionality (e.g. startup profile management, programs and applications, community and networking, learning management, payments). Each feature module is lazily loaded — its code is only downloaded to the browser when the user navigates into that area — which keeps initial page-load size small as the platform's feature surface grows.

Cross-cutting concerns (HTTP communication, authentication guards, shared UI components, formatting utilities) are implemented in shared infrastructure modules consumed by every feature module, ensuring consistent behavior (e.g. how a session expiry is handled, or how a date is formatted) across the entire application.

### 3.3 State Management

Application state is held in a centralized, reactive store, organized into slices aligned with the feature modules above (e.g. authentication/session state, current user profile, active tenant configuration, notification counts). Components read state through composable selectors and trigger state changes by dispatching actions, which are processed by dedicated effect handlers that perform the corresponding API calls. This pattern keeps components free of direct HTTP logic and provides a single, traceable path for how server data enters and updates the client.

### 3.4 Client-Server Communication

- The application communicates with Business API Services exclusively over versioned REST endpoints, secured by an HTTP-only session cookie established at login.
- A centralized HTTP interceptor layer attaches required headers, handles session-expiry redirects, and surfaces API errors to the state-management layer in a consistent shape.
- At application bootstrap, the client resolves its active tenant by calling the Tenant Control Plane with the requesting domain, receiving that tenant's branding, enabled features, and the base API address to use for all subsequent business calls.

### 3.5 Real-Time Communication

Features requiring live updates — messaging, presence/online status, and notification delivery — use a persistent WebSocket connection to a real-time messaging service, layered on top of the standard REST API for anything that does not require sub-second delivery. This avoids polling for the majority of the application while keeping the interactive, time-sensitive features responsive.

### 3.6 Progressive Web App Capabilities

The application is delivered as an installable Progressive Web App: it can be added to a user's home screen on supporting devices, and a service worker caches static application assets to improve repeat-visit load times. Core functionality requires network connectivity; the platform does not currently provide full offline data entry or synchronization.

---

## 4. Administration Panel Architecture

### 4.1 Technology Stack

| Concern | Technology |
|---|---|
| Application Framework | PHP, using a lightweight MVC-style routing and templating approach |
| Data Access | A minimal database abstraction layer providing query building and connection management |
| Presentation | Server-rendered HTML templates with a shared admin UI component/theme layer |
| Client-Side Interactivity | Progressively enhanced with JavaScript/AJAX for dynamic, in-page actions |

### 4.2 Application Structure

The panel is organized into modules aligned one-to-one with the administrative feature areas in FRS §4 (stakeholder management, program and application management, finance, content, reporting, system configuration, and so on). Each module owns its own request handlers, view templates, and any module-specific data-access logic, while sharing a common bootstrap layer responsible for tenant resolution, session handling, and access-control enforcement on every request.

A generic, configuration-driven CRUD (create/read/update/delete) engine underlies the majority of stakeholder and reference-data management screens: list, add, edit, and detail views are generated from field-level configuration rather than hand-written per entity type, allowing new stakeholder attributes or lookup tables to be exposed through the admin UI via configuration rather than code changes.

### 4.3 Multi-Tenant Data Access Pattern

Every administrative request opens two logically distinct data connections:

1. A connection to the tenant's own business database, holding that tenant's stakeholder, program, and operational data.
2. A connection to the shared Tenant Control Plane database, consulted (read-mostly) for tenant identity, branding, and feature-flag state, and written to by a small, deliberately limited set of administrative actions that manage cross-tenant or platform-wide configuration (for example, certain ecosystem-directory and tenant-level settings actions).

This dual-connection pattern is established once per request, at the point the tenant is resolved from the requesting domain, and is the mechanism by which tenant data isolation is enforced within the panel.

### 4.4 Session & Templating Model

Administrator sessions are stored server-side (database-backed, rather than in the local file system of a single application server), which allows administrator sessions to remain valid regardless of which underlying server instance handles a given request in a horizontally scaled deployment. Page rendering uses server-side templates that apply the resolved tenant's branding (colors, logo) at render time, so the same codebase produces a distinctly branded experience per tenant.

### 4.5 Asynchronous Interaction Pattern

Interactive, in-page actions (inline editing, modal-based workflows, dashboard widgets, bulk actions) are implemented as asynchronous requests from the browser to a small set of dedicated handler endpoints, which return data or partial view fragments consumed by client-side JavaScript, rather than full page reloads. This gives the administration panel a responsive, app-like feel for its most frequently used workflows while keeping the majority of the application server-rendered.

---

## 5. Backend Services Architecture (Consumed Interfaces)

### 5.1 API Design Principles

- All business functionality exposed to the two front-end applications is served through versioned REST APIs, allowing the API contract to evolve without breaking existing clients.
- Endpoints validate and authorize every request independently; no endpoint trusts client-side validation as an authorization boundary.
- API responses use consistent, structured error shapes, allowing both front-end applications to render uniform error handling.

### 5.2 Tenant Resolution & Bootstrapping

Both front-end applications resolve their operating tenant at startup by calling a tenant-verification endpoint with the requesting domain. The response establishes, for the remainder of the session: which backend API address to use for business calls, which features are enabled, and the tenant's branding configuration. This bootstrapping step is what allows a single deployed codebase to serve many differently branded and differently configured tenants.

### 5.3 Feature Configuration Architecture

Every optional capability described in the FRS is governed by a named feature configuration value, owned centrally by the Tenant Control Plane and read by both front-end applications and their backend services. This allows a capability to be enabled for one tenant and disabled for another without any code branching — the same binaries run for every tenant, with behavior differing purely by configuration.

### 5.4 Notification Architecture

Cross-application notifications (approvals, connection requests, meeting invitations, ticket updates, and similar events) are generated by backend business logic and fanned out through the appropriate channel — in-app notification feed, email, WebSocket push, and/or WhatsApp — based on the tenant's configuration and the individual user's notification preferences.

---

## 6. Data Architecture

### 6.1 Multi-Tenant Data Model

The platform uses a **database-per-tenant** isolation model at the business-data layer: each tenant's operational data resides in its own logical relational database, resolved dynamically based on the tenant identified for the current request. Tenant identity, branding, and platform-wide configuration are held in a single shared control-plane database, structurally distinct from every tenant's business data.

A small number of platform-level features are explicitly designed to be cross-tenant by nature (for example, the intellectual property/patent registry and certain ecosystem-wide facility listings), and these are the only paths permitted to read or write beyond a single tenant's own database.

### 6.2 Core Data Domains

| Domain | Representative Data |
|---|---|
| Identity & Accounts | User accounts, credentials/session state, role assignments |
| Stakeholder Profiles | Startup, investor, mentor, corporate, partner, service provider, program office, and individual records |
| Programs & Applications | Programs, rounds, application forms, submissions, evaluations, and ratings |
| Ecosystem Engagement | Connections, messages, community posts, events, and meetings |
| Commercial Records | Orders, transactions, invoices, memberships, coupons, and tax configuration |
| Content & Learning | Courses, lessons, enrollments, news, and resource library items |
| Administrative Records | Audit logs, support tickets, and system configuration metadata |

### 6.3 File & Media Storage

Uploaded and generated files (documents, images, videos, certificates, exported reports) are stored in cloud object storage rather than on application servers, referenced from the relational data model by a stored object key. Access to non-public files is brokered through short-lived, signed URLs generated on demand, rather than exposing storage locations as permanently public addresses.

---

## 7. Integration Architecture

Each integration category below is implemented as a discrete boundary, so that a given provider can be swapped or a new provider added within a category without affecting the platform's core domain logic.

### 7.1 Payments

The platform integrates with multiple payment gateway providers, with the tenant's active gateway(s) and primary gateway selectable through administrative configuration. A unified checkout flow abstracts the provider-specific integration details (redirect-based, embedded-widget, or server-to-server flows, depending on the provider) behind a consistent client-side experience and a consistent internal order/transaction record, regardless of which gateway processed a given payment.

### 7.2 Communications (Email, SMS, WhatsApp)

Transactional and broadcast communications are dispatched through dedicated email and messaging provider integrations. One-time-password delivery, which underlies the platform's passwordless authentication model, is dispatched through the same channel integrations.

### 7.3 Video Conferencing

One-on-one meetings, panel interviews, and video pitch recording are delivered through an embedded third-party video-conferencing SDK, invoked from within the Member Web Application with session details (participants, meeting identifier) supplied by the backend at meeting-creation time.

### 7.4 Real-Time Messaging

In-app chat and live presence/notification delivery are backed by a real-time messaging infrastructure layer, supporting either a fully in-house messaging implementation or an integrated third-party chat platform, selectable per tenant.

### 7.5 AI-Assisted Evaluation

Where enabled, program application scoring can be delegated to an independently deployed AI evaluation service. The administration panel submits applicant data and an evaluation thesis/criteria set to this service, polls for completion, and retrieves finalized scoring results for administrator review — the evaluation service itself supports multiple underlying large-language-model providers behind a consistent internal interface.

### 7.6 Search

Directory and global search can be served either by standard relational database queries or, where enabled for higher-volume tenants, by a dedicated search infrastructure layer offering faster, typo-tolerant full-text search across large stakeholder and content datasets.

### 7.7 CRM Synchronization

Administrative tooling supports configurable field-level synchronization of stakeholder records with an external CRM system, authenticated via an OAuth-based connection established once per tenant.

### 7.8 Single Sign-On

Administrator authentication supports an optional enterprise SSO integration, allowing tenant administrators to authenticate using their organization's existing identity provider rather than platform-specific credentials.

---

## 8. Security Architecture

### 8.1 Authentication Model

- **Member authentication** is passwordless: identity is established by verifying a one-time code delivered to a registered email address, mobile number, or WhatsApp number. An authenticated session is represented by a secure, HTTP-only session cookie, minimizing exposure of session credentials to client-side script.
- **Administrator authentication** supports credential-based login (with password-reset-by-email recovery) and optional enterprise SSO, with server-side session state.
- A supervised, single-use, time-limited access mechanism allows an administrator to open a support session into a member's account for assistance purposes, without requiring or exposing that member's credentials.

### 8.2 Authorization & Access Control

Every request is authorized against the requesting user's role and, for administrative users, their specific scope of assignment (e.g. the programs, partner ecosystem, or corporate account they are limited to). Authorization is evaluated on the backend for every request; the front-end applications' role-aware navigation and layout are a usability convenience, not the enforcement boundary.

### 8.3 Tenant Data Isolation

Tenant isolation is enforced at the data-access layer: every business-data request is scoped to the single tenant resolved for that request, using the database-per-tenant model described in Section 6.1. This is a structural property of the data-access layer rather than a per-query convention, meaning isolation does not depend on every individual feature remembering to apply a tenant filter.

### 8.4 Transport & Storage Security

- All communication between the front-end applications, backend services, and third-party integrations is encrypted in transit using industry-standard TLS.
- Sensitive credentials required for third-party integrations (payment gateway keys, messaging provider tokens, and similar) are managed as protected configuration, separate from application source code.
- File storage access is brokered through signed, time-limited URLs for non-public content, as described in Section 6.3.

### 8.5 Auditability

Administrative actions with material impact — approvals, financial transactions, configuration changes, and data exports — are recorded in an audit log capturing the acting administrator, the action taken, and the timestamp, supporting after-the-fact review and accountability.

---

## 9. Deployment Architecture

### 9.1 Environment Strategy

The platform maintains logically separated environments for active development, pre-release validation, and production, allowing new functionality to be verified before it reaches tenant-facing production traffic.

### 9.2 Deployment Topology

- The Member Web Application, the Administration Panel, and each backend service are deployed as independent, horizontally scalable units, allowing capacity for one to be adjusted without affecting the others.
- Each tenant's business database is provisioned and can be scaled independently of the application tier, in line with the data-isolation model in Section 6.1.
- Integration Gateway components are deployed as stateless services that can be scaled based on third-party call volume independent of core application traffic.

### 9.3 Content Delivery

Static application assets (compiled application bundles, images, and publicly cacheable files) are served through a content delivery network, reducing latency for end users and offloading repetitive static-asset traffic from the application tier.

### 9.4 Release Model

Each deployable service is released independently, following its own build-and-release pipeline. Interface contracts between services (API shapes, event/notification formats) are versioned so that a service can be updated without requiring simultaneous redeployment of every service that consumes it, except where a breaking contract change is deliberately introduced and coordinated.

---

## 10. Cross-Cutting Concerns

### 10.1 Logging & Monitoring

Application and infrastructure logs are captured centrally across all deployed services, providing the operational visibility needed to detect and diagnose issues, and to support the audit and traceability requirements described in the SRS.

### 10.2 Error Handling

Both front-end applications present user-facing errors in clear, non-technical language, while capturing the underlying technical detail server-side for diagnostic purposes. Transient failures in third-party integrations are surfaced to the user as a recoverable state (e.g. "payment pending, please wait") rather than a hard failure, wherever the integration's nature allows it.

### 10.3 Caching Strategy

- Frequently read, infrequently changing reference and content data (e.g. published articles, glossary terms, resource listings) is cached at the backend service layer for a bounded time window, trading a small propagation delay for reduced database load.
- Static front-end assets are cached at the browser and content-delivery-network layers, invalidated automatically on each new application release.
- Real-time and transactional data (session state, application status, payment status) is never served from a stale cache — these paths always read current data.

### 10.4 Configuration Management

Tenant-specific configuration (branding, feature flags, custom forms, evaluation criteria, integration credentials) is stored as data rather than code and is applied at runtime, per the design principle in Section 2.1. Platform-level configuration (deployment settings, service credentials, infrastructure parameters) is managed separately from tenant configuration and is not exposed through either front-end application.

---

## Appendix A — Technology Stack Summary

| Layer | Technology |
|---|---|
| Member Web Application | Angular (single-page application framework), reactive state management, Progressive Web App delivery |
| Administration Panel | PHP with a lightweight MVC/templating framework, progressively enhanced with JavaScript |
| Backend Business Services | Modern server-side application framework(s) exposing versioned REST APIs |
| AI Evaluation Service | Independently deployed service supporting multiple large-language-model providers |
| Data Persistence | Relational database management system, database-per-tenant |
| File & Media Storage | Cloud object storage with signed-URL access control |
| Real-Time Communication | WebSocket-based messaging infrastructure |
| Search (optional) | Dedicated full-text search infrastructure for high-volume tenants |
| Content Delivery | Content delivery network for static assets |

## Appendix B — Component Interaction Diagram

```
 Member (browser)                     Administrator (browser)
        |                                       |
        v                                       v
 +----------------+                    +--------------------+
 | Member Web App |                    | Administration     |
 | (Angular PWA)   |                    | Panel (PHP)         |
 +----------------+                    +--------------------+
        |   REST + WebSocket                    |  REST + AJAX
        v                                       v
 +--------------------------------------------------------+
 |                Business API Services                    |
 +--------------------------------------------------------+
     |             |                |                |
     v             v                v                v
 +--------+   +-----------+   +-----------+   +----------------+
 | Tenant |   | Per-Tenant |   | AI        |   | Integration    |
 | Control|   | Database   |   | Evaluation|   | Gateway         |
 | Plane  |   |            |   | Service   |   | (payments,      |
 +--------+   +-----------+   +-----------+   |  comms, video,   |
                                                |  storage, CRM,   |
                                                |  search, SSO)    |
                                                +----------------+
```

## Appendix C — Glossary

See FRS Section 6 and SRS Appendix B for the shared functional and system glossary. Additional architectural terms:

| Term | Definition |
|---|---|
| Database-per-Tenant | A data-isolation model in which each tenant's business data resides in its own logical database instance. |
| API Contract | The agreed shape of requests and responses between a service and its consumers, versioned to allow independent evolution. |
| Effect Handler | In the front-end state-management pattern, the component responsible for performing an API call in response to a dispatched action and translating the result back into state updates. |
| Signed URL | A time-limited, access-controlled link to a stored file, generated on demand rather than exposing a permanently public address. |
| Integration Gateway | The architectural boundary layer through which the platform communicates with all external third-party services. |

---

*End of Document*
