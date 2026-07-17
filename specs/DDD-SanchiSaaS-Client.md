# SanchiSaaS Platform
## Database Design Document

---

**Document Type:** Database Design Document (DDD)
**Product:** SanchiSaaS — Incubator & Accelerator Management Platform
**Modules Covered:** Member Web Application, Administration Panel (shared data layer)
**Version:** 1.0
**Date:** July 2026
**Prepared For:** Client Technical Review
**Companion Documents:** FRS v1.0, SRS v1.0, TAD v1.0
**Classification:** Confidential

---

## Table of Contents

1. Introduction
   1.1 Purpose
   1.2 Audience
   1.3 Scope
   1.4 References
2. Database Design Overview
   2.1 Design Approach
   2.2 Multi-Tenant Data Model
   2.3 Common Entity Conventions
3. Entity-Relationship Overview
   3.1 Control Plane
   3.2 Identity & Stakeholder Profiles
   3.3 Programs & Applications
   3.4 Business Challenges
   3.5 Ecosystem Engagement
   3.6 Commercial
   3.7 Learning Management
   3.8 Content
   3.9 Administrative & Platform Services
   3.10 Facilities
4. Data Dictionary
   4.1 Control Plane
   4.2 Identity & Stakeholder Profiles
   4.3 Programs & Applications
   4.4 Business Challenges
   4.5 Connections
   4.6 Community Wall
   4.7 Meetings & Events
   4.8 Messaging
   4.9 Commercial
   4.10 Learning Management
   4.11 Content
   4.12 Administrative & Platform Services
   4.13 Facilities
5. Referential Integrity & Relationship Summary
6. Indexing & Performance Design
7. Data Isolation (Multi-Tenancy)
8. Data Retention & Lifecycle
9. Appendices
   A. Entity Count Summary
   B. Glossary

---

## 1. Introduction

### 1.1 Purpose

This Database Design Document (DDD) describes the logical data model underlying the SanchiSaaS platform: its core entities, their attributes, the relationships between them, and the design principles governing data isolation, integrity, and performance. It provides the level of detail needed for a technical stakeholder to understand how platform data is structured, without requiring direct access to the underlying schema migrations.

### 1.2 Audience

This document is intended for client-side database architects, integration engineers, and technical reviewers evaluating the platform's data model — for example, ahead of a reporting integration, a data migration, or a technical due-diligence review.

### 1.3 Scope

This document describes the data model supporting the Member Web Application and Administration Panel described in the FRS, SRS, and TAD. It covers the platform's business data domains in full; it does not cover internal operational tables used purely for infrastructure purposes (queues, caches, job schedulers) as these carry no business meaning.

### 1.4 References

- SanchiSaaS Functional Requirement Specification (FRS), v1.0
- SanchiSaaS System Requirement Specification (SRS), v1.0
- SanchiSaaS Technical Architecture Document (TAD), v1.0

---

## 2. Database Design Overview

### 2.1 Design Approach

The platform's data model follows standard relational design principles: every entity has a stable primary identifier, relationships are expressed through foreign keys, and lookup/reference data (industries, geographies, categories) is normalized into dedicated tables rather than duplicated inline. Polymorphic references — used where a single entity type (e.g. a payment order, or an audit-log entry) can relate to more than one kind of business object — are documented explicitly in Section 4 wherever they occur.

### 2.2 Multi-Tenant Data Model

As described in the TAD, the platform uses a **database-per-tenant** isolation model for business data, combined with a single shared **control-plane database** for tenant identity, branding, and feature configuration. This document describes:

- The **control-plane schema** (Section 4.1) — shared across all tenants.
- The **per-tenant business schema** (Sections 4.2–4.13) — structurally identical across every tenant, with each tenant holding its own independent set of rows in its own database instance.

### 2.3 Common Entity Conventions

Unless otherwise noted, every entity in the per-tenant business schema follows a consistent base structure:

| Convention | Description |
|---|---|
| Primary Key | A numeric internal identifier (`id`), plus a globally unique identifier (`uuid`) used in all external-facing references (URLs, API responses) so that internal sequential IDs are never exposed to clients. |
| Soft Deletion | A `deletedAt` timestamp marks a record as removed without physically deleting it, preserving referential and audit history; most list queries filter these out automatically. |
| Active Flag | A boolean `status`/`isActive` flag distinguishes an active record from an administratively disabled one, independent of soft deletion. |
| Audit Timestamps | `createdAt` and `modifiedAt` timestamps are maintained automatically on every entity. |
| Approval Workflow (Stakeholder Profiles) | Every stakeholder profile type shares a consistent approval-state shape: an approval status (pending/approved/rejected), the approving/rejecting administrator, the approval/rejection timestamp, and an optional message — described once in Section 4.2 rather than repeated per entity. |

---

## 3. Entity-Relationship Overview

The diagrams below present each major domain's entities and their primary relationships at a conceptual level. Full attribute-level detail follows in Section 4.

### 3.1 Control Plane

```
      Organization (billing/legal parent)
            |
            | 1..N
            v
        Tenant (one row per deployment)
    - domain, branding, feature flags
    - per-tenant database connection
```

### 3.2 Identity & Stakeholder Profiles

```
                     User (account/session identity)
                          |
        +--------+--------+--------+--------+--------+--------+--------+
        |        |        |        |        |        |        |        |
        v        v        v        v        v        v        v        v
     Startup  Investor  Mentor  Corporate  Partner  Service  Program   Individual
                                                      Provider  Office
                                                              Member
```
A `User` account links to at most one active profile of each stakeholder type at a time. Each stakeholder profile carries its own approval workflow and, where relevant, a link to a sponsoring `Partner`.

### 3.3 Programs & Applications

```
   Program (profile-linked track)          Application Program ("Call for Applications" track)
        |                                            |
        v                                            v
   Program Round  <---- Jury Assignment        Application Program Round <---- Jury Assignment
        |                                            |
        v                                            v
   Startup's Round Progress                  Form Submission's Round Progress
                                                      |
                                                      v
                                              Submission Rating / Jury Q&A

   Form (definition) ----------------------> Form Submission (the applicant's answers)
```
The platform supports two parallel program models sharing the same underlying evaluation pattern (rounds, jury assignment, ratings): a **profile-linked track** for startups with an existing platform profile, and a **general application track** ("Call for Applications") that does not require an existing profile before applying.

### 3.4 Business Challenges

```
   Corporate ----> Challenge ----> Challenge Participant (a startup's submission)
                       |
                       v
              (optional) Application Program
              — a Challenge can be run as a
                Call for Applications
```

### 3.5 Ecosystem Engagement

```
   User <----> Connection <----> User          User <--- Meeting ---> User
       (with global + per-profile                          |
        connection policy matrix)                           v
                                                     Meeting Notes / Feedback

   User ---> Community Post ---> Comments / Reactions / Poll

   Chat Conversation <---> Chat Conversation Member (User)
        |
        v
   Chat Message (supports threaded replies)

   Event ---> Event Attendee (User)
```

### 3.6 Commercial

```
   Membership Type ----> Membership (purchased, held by a stakeholder profile)
                              |
                              v
                        Payment Order ----> Payment Transaction
                              |
                              v
                     Coupon / Tax applied

   Proforma Invoice (independent pre-payment quote document)
```

### 3.7 Learning Management

```
   Course ---> Section ---> Lesson ---> Lesson Progress (per user)
     |            |            |
     v            v            v
  Price Plan   (n/a)      Video Asset / Resource

   Course ---> Enrollment (per user, per price plan) ---> Course Review
                     |
                     v
                Quiz Attempt ---> Quiz Answer
```

### 3.8 Content

```
   Resource Category ---> Resource File
   News, Glossary — standalone reference/content entities
```

### 3.9 Administrative & Platform Services

```
   Stakeholder Profile ---> Certificate / ID Card (issued record)

   User ---> Ticket ---> Ticket Conversation

   Any Entity ---> Profile Audit Log (change history)

   User ---> Milestone ---> Qualitative / Quantitative Sub-Goals
                       ---> Milestone Notes / Messages

   Startup ---> Metric (value) ---> Metric Type (definition)
```

### 3.10 Facilities

```
   Partner ---> Facility Type ---> Facility ---> Facility Availability
                                       |
                                       v
                              Facility Booking ---> Booking Check-in/out
                                       |
                                       v
                              Booking Add-ons
```

---

## 4. Data Dictionary

Attribute lists below focus on business-meaningful fields; the common conventions in Section 2.3 (id, uuid, status, timestamps) are omitted from each entity's listing to avoid repetition.

### 4.1 Control Plane

| Entity | Purpose | Key Attributes | Related Entities |
|---|---|---|---|
| **Organization** | The billing/legal parent of one or more tenants. | Name, website, official/technical email, hub flag | 1..N Tenant; 1..N Invoices, Payments, Contacts, Contracts |
| **Tenant** | One row per client deployment — domain, connection details, and feature configuration. | Name, domain, custom domain, API/admin URLs, per-tenant database connection details, currency, SSO configuration, IP/domain access restrictions, and 150+ feature-enablement flags (e.g. chat, startup kit, jobs, community feed, application management, venture studio, IP management, facility management) | N..1 Organization |

### 4.2 Identity & Stakeholder Profiles

| Entity | Purpose | Key Attributes | Related Entities |
|---|---|---|---|
| **User** | The account/login identity for every platform user. | Account type & role, name, designation, email, mobile/WhatsApp number, verification flags, active/blocked flags, links to one profile per stakeholder type, parent-account link (for sub-accounts), last-login timestamp | 0..1 each of Startup, Investor, Corporate, Mentor, Service Provider, Program Office Member, Partner, Individual; 1..N Meetings, Notifications, Form Submissions, Community Posts, Milestones, Tickets, Chat Messages |
| **User Login Session** | Tracks an active login session/token per user, backing single-session enforcement. | Session token | N..1 User |
| **Startup** | Startup stakeholder profile. | Company name, incorporation year, registered location, company size, funding status, technology readiness level, industry classification, government/registration numbers, approval workflow fields | N..1 User; 1..1 Product Info, Financials, Pitch Deck; 1..N Founders, Supporting Documents, Funding Commitments, Ratings, Advisory Board, Challenge Participation, Metrics |
| **Investor** | Investor stakeholder profile (individual or organizational). | Investor type, organization name/type, portfolio size, funding-provision status, registered location, approval workflow fields | N..1 User; 1..1 Representative Info, Investment Details; 1..N External Investments |
| **Mentor** | Mentor stakeholder profile. | Name, current organization, designation, domain/sector interests, application number & status, registered location, approval workflow fields | N..1 User; 1..N Mentorship Sessions, Ratings |
| **Corporate** | Corporate stakeholder profile. | Company name, incorporation year, company size, internal innovation program details, sector interests, registered location, approval workflow fields | N..1 User; 1..N Business Challenges |
| **Partner** | Ecosystem partner profile, with delegated management capability over an associated set of stakeholders. | Name, partner type, active flag, invite code, stakeholder-access scope, industry/technology focus, registered location, approval workflow fields | N..1 User; 1..N Facilities, Facility Types, Partner Events, Grant Allotments |
| **Service Provider** | Service-provider stakeholder profile. | Name, provider type & category, sector interests, "service kit provider" flag, registered location, approval workflow fields | N..1 User |
| **Program Office Member** | Institutional program-office stakeholder profile. | Name, department, designation, sector/key interest areas, registered location, approval workflow fields | N..1 User |
| **Individual** | Non-organizational member profile. | Name, short/long description, program associations, registered location, approval workflow fields | N..1 User; 1..N Ratings |

**Shared Approval Workflow** (repeated on every stakeholder profile type above): approval status (pending/approved/rejected), approval type, approving/rejecting administrator, approval/rejection timestamp, and an optional message — plus an optional link to a sponsoring Partner for partner-delegated approval.

### 4.3 Programs & Applications

| Entity | Purpose | Key Attributes | Related Entities |
|---|---|---|---|
| **Program** | A cohort/accelerator/incubation program on the profile-linked track. | Title, code, source, profile requirement, application window, jury & program-manager assignment, re-application policy, payment configuration | 1..N Program Round, Content Section, FAQ, Pitch Video Topic |
| **Program Round** | A sequential evaluation stage within a Program. | Round name, jury assignment, rating method (weighted/unweighted), rating requirement, priority, payment configuration | N..1 Program; 1..N Jury Question |
| **Program–Startup Round Progress** | A startup's application record and progress through a Program's rounds. | Application number, current round, completed rounds, application/submission status, rejection details, submission timestamp | N..1 Startup, Program Round |
| **Program Round Jury Assignment** | Assigns a jury member to evaluate a startup within a round. | Jury member, "not interested" flag & reason | N..1 Startup, Program, Program Round |
| **Application Program** | A program/Call-for-Applications on the general application track (no existing profile required). | Title, code, public URL, program type, application window, payment requirement, document/pitch requirements, jury-masking option, re-application policy, cross-tenant promotion configuration | 1..N Application Program Round, Content Section, FAQ, Pitch Video Topic, Document Type, Analysis Record; optionally linked from a Business Challenge |
| **Application Program Round** | A round within the general application track. | Round name, jury assignment, document/rating requirements, rating method | N..1 Application Program; 1..N Jury Question |
| **Application Program Submission Progress** | An applicant's submission and its progress through the application track's rounds. | Application number, current round, completed rounds, application/submission status, rejection details, pitch document | N..1 Application Program Round; N..1 Form Submission |
| **Application Program Submission Rating** | A jury member's evaluation/score of a submission. | Rater, recommendation, structured ratings, overall score, comments, approval state | N..1 Form Submission |
| **Application Program Round Jury Assignment** | Assigns a jury member to a submission within a round. | Jury member, "not interested" flag & reason | Plain reference columns to Application Program, Round, Submission |
| **Application Program Jury Question** | A structured question jury members must answer while evaluating a round's submissions. | Question text, position, mandatory flag, answer field type, value range | N..1 Application Program Round, Application Program; 1..N Jury Question Answer |
| **Application Program Jury Question Answer** | A jury member's answer to a jury question for a specific submission. | Answer text | N..1 Jury Question, Form Submission |
| **Application Program Round Notes** | Internal notes (admin/jury/partner) attached to a submission's round. | Notes text | Plain reference columns to submission/program/round/author |
| **Application Program Jury Call Request** | A scheduling record for a live jury evaluation call. | Scheduling status & timestamps, jury message | Plain reference columns to submission/program/round/jury member |
| **Form** | A dynamic form definition (field schema) attachable to programs, rounds, or challenges. | Title, code, target account type, field schema, form usage type, visibility, default/mandatory flags | 1..N Form Submission |
| **Form Submission** | An applicant's answers to a Form — the core application record. | Applicant identity fields, answer data, submission/re-submission state, pitch document, acquisition-source attribution | N..1 Form, User; 1..N Ratings, Jury Answers |
| **Analysis Record** | An AI-assisted scoring run against a set of applicants within an Application Program — submitted to the AI analyzer service and tracked through cost and AI-credit settlement. | Folder reference, application/completion status, thesis text, model & provider used, aggregate input/output token counts, aggregate cost (USD), batches-priced vs. batches-total counters, cost-computed timestamp, AI-credit charge amount & ledger reference, archive (soft-delete) timestamp | N..1 Application Program; 1..N Analysis Rating, Analysis Rescore |
| **Analysis Rating** | The AI analyzer's per-applicant score and justification for a given Analysis Record. | Submission reference, round reference, numeric rating (0.000–5.000 scale), justification text, enrichment source citations | N..1 Analysis Record; N..1 Form Submission |
| **Analysis Rescore** | A supplementary scoring sub-job that scores applicants who joined an Analysis Record's scope after its initial run, then merges results back into the parent run. | Status (uploaded/running/finalized/failed), submitted applicant count, merged applicant count, error message, finalized timestamp | N..1 Analysis Record |

### 4.4 Business Challenges

| Entity | Purpose | Key Attributes | Related Entities |
|---|---|---|---|
| **Challenge** | A business/innovation challenge posted by a corporate. | Title, hosting platform (internal/external), visibility, status, approval status, deadline, public-submission flag, assigned reviewers | N..1 Corporate; optionally linked to an Application Program (as its Call-for-Applications); 1..N Challenge Participant |
| **Challenge Participant** | A startup's submitted solution to a Challenge. | Product name, maturity stage, delivery model, deployment cycle, participation status, submitter contact details | N..1 Challenge, Startup |

### 4.5 Connections

| Entity | Purpose | Key Attributes | Related Entities |
|---|---|---|---|
| **Connection** | A connection request/relationship between two users. | Requester & recipient, account types, status, connection type, acceptance/rejection details, moderation state, linked group chat | N..1 User (requester), N..1 User (recipient) |
| **Connection Global Policy Matrix** | Platform-wide default rules for whether two stakeholder types may search/connect. | Profile-type pair, search/connect permissions, moderation requirement, daily request limit | Standalone configuration entity |
| **Connection User Policy Override** | A per-profile override of the global policy matrix. | Profile, target profile type, search/connect permissions, moderation requirement, request limit | N..1 the overriding stakeholder profile |

### 4.6 Community Wall

| Entity | Purpose | Key Attributes | Related Entities |
|---|---|---|---|
| **Community Post** | A post on the community feed. | Author, text, media, admin-post flag, pinned flag, visibility by account type | N..1 User (author); 1..N Comments, Reactions; 1..1 Poll |
| **Post Comment** | A comment or threaded reply on a post. | Comment text, parent-comment link (for threaded replies) | N..1 User, Community Post; 1..N Comment Reactions |
| **Post Reaction** | A user's reaction to a post. | Reaction type | N..1 User, Community Post |
| **Comment Reaction** | A user's reaction to a comment. | Reaction type | N..1 User, Post Comment |
| **Post Poll** | An optional poll attached to a post. | Question, timeframe | 1..1 Community Post; 1..N Poll Option, Poll Vote |
| **Poll Option** | A selectable answer for a poll. | Option text | N..1 Post Poll; 1..N Poll Vote |
| **Poll Vote** | A user's vote for a poll option. | (Join record) | N..1 Post Poll, Poll Option, User |
| **Post Report** | A user's flag of a post for moderation review. | Reason | N..1 User, Community Post |

### 4.7 Meetings & Events

| Entity | Purpose | Key Attributes | Related Entities |
|---|---|---|---|
| **Meeting** | A scheduled or proposed meeting between two users. | Title, location/tool type, status, meeting type, date/time, reschedule proposal, acceptance/rejection details, optional link to a job interview | N..1 User (creator), N..1 User (invitee); optionally N..1 Job Application; 1..N Meeting Notes |
| **Meeting Notes** | A note taken about a meeting, optionally shared. | Note text, sharing scope | N..1 User, Meeting |
| **Calendar Availability** | A user's configured availability for meeting scheduling. | Availability window configuration | 1..1 User |
| **Meeting Feedback Question** | A configurable post-meeting feedback question. | Question text, position, mandatory flag, answer type | 1..N Feedback Answer |
| **Meeting Feedback Answer** | A respondent's answer to a feedback question. | Respondent identity, answer | N..1 Meeting Feedback Question |
| **Event** | A platform-hosted event (webinar, one-to-one slot booking, or physical/virtual gathering). | Title, publish status, event type/delivery mode, booking visibility & eligibility rules, payment requirement, organizer, speaker details | N..1 User (organizer); 1..N Attendee, Content Section, FAQ, Question, Agenda, Location, Floor, Booth |
| **Event Attendee** | A user's registration/RSVP for an event, or a booked slot within it. | Date/time, RSVP response, attendee type, approval status | N..1 User, Event; optionally linked to a Meeting for slot-booking events |

### 4.8 Messaging

| Entity | Purpose | Key Attributes | Related Entities |
|---|---|---|---|
| **Chat Conversation** | A private or group messaging thread. | Conversation type, name, creator, members/admins list, last message reference | N..1 User (creator); 1..N Messages, Members |
| **Chat Conversation Member** | Membership record for a user in a group conversation. | (Join record) | N..1 Chat Conversation, User |
| **Chat Message** | A single message within a conversation, supporting threaded replies. | Sender, message content, message type, metadata, read-by tracking, edited flag, reply count | N..1 Chat Conversation, User (sender) |

### 4.9 Commercial

| Entity | Purpose | Key Attributes | Related Entities |
|---|---|---|---|
| **Payment Order** | A checkout order for any payable module (membership, course, facility booking, etc.). | Gateway type, order status, payment mode, purchased-item reference, amount, discount, tax, final amount, currency, order number, billing details | 1..N Payment Transaction; references Coupon, Tax Profile |
| **Payment Transaction** | An individual payment attempt/settlement against an Order. | Transaction type/status, gateway type, amount, transaction reference, invoice reference | N..1 Payment Order |
| **Coupon** | A discount coupon definition. | Name, code, discount type & value, applicable module(s), usage limits, validity window | Referenced by Payment Order, Coupon Usage |
| **Coupon Usage** | Records a single redemption of a coupon. | Usage timestamp, user, purchased-item reference | References Coupon |
| **Tax Profile** | A tax rate/type definition. | Name, tax percentage, GST flag | Referenced by Membership Type, Payment Order, Proforma Invoice |
| **Proforma Invoice** | A pre-payment quote/estimate document, independent of the order/transaction records. | Invoice number, purchased-item reference, payment type, amount breakdown, validity, payment/mail status, billing details | References Coupon, Tax Profile |
| **Membership Type** | A membership plan/tier definition. | Name, code, eligible profile type, pricing per billing cycle, expiry policy, tax inclusion, applicable coupons/charges, multi-booking rules | N..1 Tax Profile; 1..N Membership |
| **Membership** | A purchased/active membership held by a stakeholder profile. | Start/end date, amount paid, duration, status, profile reference, order reference, billing details | N..1 Membership Type; associated Upgrade Request and Reminder records |

### 4.10 Learning Management

| Entity | Purpose | Key Attributes | Related Entities |
|---|---|---|---|
| **Course** | An LMS course. | Title, slug, thumbnail, description, completion mode, certificate settings, catalog visibility, level, language, tags | N..1 Category; 1..N Section, Enrollment, Price Plan, Resource, Instructor Link |
| **Section** | A grouping of lessons within a course. | Title, sort order, publish state | N..1 Course; 1..N Lesson |
| **Lesson** | A learning unit (video, article, or resource) within a section. | Type, title, description, sort order, content (for article type), preview flag | N..1 Section, Video Asset; 1..N Lesson Progress, Resource |
| **Enrollment** | A user's access grant to a course under a specific price plan. | Price plan, status (active/expired/revoked/refunded), access window, order reference | N..1 User, Course, Price Plan; 1..N Review; referenced by Quiz Attempt, Certificate |
| **Course Price** | A pricing plan/SKU for a course. | Code, pricing type, amount, billing period, access duration, active flag | N..1 Course; 1..N Enrollment |
| **Course Category** | Course taxonomy for catalog browsing. | Title, slug, description | 1..N Course |
| **Instructor** | An instructor profile assignable to courses. | Name, designation, description, avatar | 1..N Course Instructor Link |
| **Course Instructor Link** | Join record linking instructors to courses with display order. | Sort order | N..1 Course, Instructor |
| **Course Review** | A learner's rating/feedback for a course. | Rating, comment, structured survey responses | N..1 Course, User, Enrollment |
| **Lesson Progress** | Tracks a user's completion/playback progress on a lesson. | Completion timestamp, last playback position | N..1 User, Lesson |
| **Lesson Resource** | A downloadable file attached to a course or lesson. | Title, file reference | N..1 Course; optionally N..1 Lesson |
| **Video Asset** | A video media asset backing video lessons. | Provider, media identifiers, duration, streaming URL, thumbnail, processing status | 1..N Lesson |
| **Quiz** | A quiz attached to a course, section, or lesson. | Scope, title, description, publish state, time limit, pass threshold, results-display mode | N..1 Course, optionally Section/Lesson; 1..N Question, Attempt |
| **Quiz Question** | A question within a quiz. | Type (single/multi-choice, true/false, short text), title, points, sort order, required flag | N..1 Quiz; 1..N Option, Answer |
| **Quiz Option** | An answer option for a question. | Label, text, correctness flag, sort order | N..1 Question; 1..N Answer |
| **Quiz Attempt** | A learner's attempt at a quiz. | Status, start/submit timestamps, time spent, score, pass/fail outcome | N..1 Quiz, User, Enrollment; 1..N Answer |
| **Quiz Answer** | A learner's answer to a question within an attempt. | Correctness, points awarded | N..1 Attempt, Question, Option |

### 4.11 Content

| Entity | Purpose | Key Attributes | Related Entities |
|---|---|---|---|
| **News** | A news/article item. | Title, description, source attribution, thumbnail, URL, tags, active/privacy state, associated industries | Standalone |
| **Glossary Term** | A single glossary entry. | Term, meaning, explanation, active flag | Standalone |
| **Resource Category** | Category grouping for downloadable resources. | Title, description, active flag | 1..N Resource File |
| **Resource File** | A downloadable resource file. | Title, description, file reference, view/download counters, privacy setting | N..1 Resource Category |

### 4.12 Administrative & Platform Services

| Entity | Purpose | Key Attributes | Related Entities |
|---|---|---|---|
| **Certificate** | An issued certificate (profile-level or course-completion). | Organization name, certificate number, image, account type, certificate type, issued/valid-till dates, certificate text fields | References the owning profile, and optionally an Enrollment or Membership |
| **ID Card** | A digital/printable identity card issued to a stakeholder. | Card number, account type, profile snapshot (name, designation, photo), issued/valid-till dates, card status | References the owning profile |
| **Ticket** | A support ticket raised by a user. | Ticket number, title, issue type, severity, status, assignment, close/reopen tracking | N..1 User, Issue Type; 1..N Conversation |
| **Ticket Conversation** | A message within a ticket's thread. | Message text, attachments, author (user or administrator) | N..1 Ticket, User, Administrator |
| **Ticket Issue Type** | Lookup of ticket categories with default assignment routing. | Name, default assignee, dev-team flag | 1..N Ticket |
| **Profile Audit Log** | Immutable record of changes to stakeholder profile entities. | Profile owner, acting user, stakeholder type, changed entity, action (create/update/delete), before/after change detail, request metadata | References the affected entity and acting user |
| **Milestone** | A goal tracked by a user, combining qualitative and quantitative sub-goals. | Title, description, reviewers, start/target/completion dates, progress notification settings | N..1 User; 1..N Qualitative Sub-Goal, Quantitative Sub-Goal, Note, Message |
| **Milestone Quantitative Sub-Goal** | A measurable numeric target under a milestone. | Parameter, target value, unit, completed value, update history | N..1 Milestone |
| **Milestone Qualitative Sub-Goal** | A checklist-style sub-goal under a milestone. | Title, completion flag & date | N..1 Milestone |
| **Milestone Note** | A note (with optional attachments) logged against a milestone. | Note text, attachments | N..1 Milestone, User |
| **Milestone Message** | A discussion-thread entry on a milestone. | Message text, attachments | N..1 Milestone, User |
| **Metric Type** | Defines a growth-metric field a startup reports against. | Title, field type & formatting, mandatory flag, program scoping, chart type | 1..N Metric |
| **Metric** | A single reported value for a metric type, by a startup, for a given date. | Value, date, editability, edit-request state, edit history count | N..1 Startup, Metric Type |
| **Metric Defaulter** | Tracks a startup's failure to submit a required metric for a period, and reminder state. | Date, reminder-email tracking, upload-confirmation tracking | N..1 Startup |
| **Metric Reviewer Assignment** | Assigns reviewer(s) responsible for a startup's metric submissions. | Reviewer list | 1..1 Startup |
| **Metric Custom Chart** | An admin-configured chart combining one or more metric types. | Title, chart type, included metric types | Standalone |

### 4.13 Facilities

| Entity | Purpose | Key Attributes | Related Entities |
|---|---|---|---|
| **Facility** | A bookable physical facility owned by a partner. | Name, description, type, address, contact details, publish/payment status, capacity, images, featured flag | N..1 Partner, Facility Type; 1..N Availability, Booking, Add-on, Amenity, Image, Meta Answer |
| **Facility Type** | Category of facility, scoped to a partner. | Name, active flag | N..1 Partner; 1..N Facility |
| **Facility Booking** | A reservation for a facility over a date/time range. | Booking number, requester & point-of-contact details, date/time range, status, capacity booked, order reference, session token | N..1 Facility, Partner; 1..N Check-in/Check-out record |
| **Facility Add-on** | An optional add-on item/service for a facility. | Item name, quantity available, chargeable flag, unit price | N..1 Facility |
| **Facility Booking Add-on** | Line item recording an add-on selected for a specific booking. | Quantity, unit price, total price | References Booking, Add-on |
| **Facility Booking Check-in/out** | Records actual check-in/out for a booking, with headcount and post-use ratings. | Headcount, check-in/out timestamps & time zone, ratings, comments | N..1 Facility Booking, User |
| **Facility Availability** | Defines booking-availability rules for a facility. | Availability window configuration, lead time, cancellation window, time zone | N..1 Facility, Partner |
| **Facility Amenity** | An amenity tag associated with a facility. | Amenity key, active flag | N..1 Facility |
| **Facility Image** | A gallery image for a facility. | Image URL, primary flag, sort order | N..1 Facility |
| **Facility Meta Question** | A custom intake question defined per facility type. | Question text, field type, mandatory flag, active flag | 1..N Meta Answer |
| **Facility Meta Answer** | A facility's answer to a facility-type meta question. | Answer value | N..1 Facility, Meta Question |
| **Facility Rating Criteria** | Rating criteria applicable to a facility type. | Name, description, active flag | N..1 Facility Type |

---

## 5. Referential Integrity & Relationship Summary

- **Cascading deletion** is applied where a child record has no meaning without its parent (e.g. a Lesson without its Section, a Payment Transaction without its Order, a Facility Booking Check-in without its Booking) — removing the parent removes the dependent children.
- **Nullifying deletion** is applied where a child record retains meaning independent of its parent's continued existence (e.g. a Quiz Attempt whose Enrollment is later removed retains its scoring history).
- **Polymorphic references** — a small number of entities (Payment Order, Proforma Invoice, Certificate, ID Card, Profile Audit Log) reference "the purchased item" or "the affected entity" generically via a type-plus-identifier pair rather than a single fixed foreign key, because the same entity must be able to relate to more than one kind of business object (e.g. a Payment Order might be for a membership, a course, or a facility booking). These are documented explicitly wherever they occur rather than modeled as a conventional single-target foreign key.
- **Approval-workflow fields** are structurally identical across all eight stakeholder profile types, allowing consistent administrative tooling (Section 4.2 of the FRS) to operate uniformly regardless of stakeholder type.

---

## 6. Indexing & Performance Design

- Every foreign-key relationship is indexed to support efficient joins and cascade operations.
- High-traffic lookup patterns — resolving a jury member's assigned submissions, resolving a startup's current round within a program, and resolving a user's unread message/notification count — are supported by composite indexes aligned to the exact query patterns used by the application, rather than relying solely on single-column indexes.
- Large, high-volume tables with time-bounded relevance (event attendee records, certain audit and log data) are periodically moved to archive tables of the same shape, keeping the primary operational tables performant as data accumulates over a tenant's lifetime.
- List and search endpoints across the platform apply pagination at the database layer; no endpoint is designed to return an entire table's contents in a single response.

---

## 7. Data Isolation (Multi-Tenancy)

- Every business entity described in Section 4.2 onward exists once per tenant, within that tenant's own database instance — there is no tenant-identifier column threaded through business tables, because isolation is achieved structurally (separate databases) rather than by row-level filtering.
- The Control Plane schema (Section 4.1) is the sole exception: it is intentionally shared across all tenants, as its purpose is to hold the configuration that identifies and describes each tenant.
- A small number of platform capabilities are deliberately cross-tenant by design (for example, an intellectual-property/patent registry and certain ecosystem-wide facility listings, described in the FRS); these are explicitly modeled as shared reference data, distinct from the isolated per-tenant business schema described in this document.

---

## 8. Data Retention & Lifecycle

- **Soft deletion** (Section 2.3) is the default removal mechanism for entities with downstream referential impact, preserving historical accuracy for financial, audit, and evaluation records even after a record is removed from active use.
- **Immutable records** — Profile Audit Log entries and Payment Transaction records are never modified after creation; corrections are represented as new records, preserving a complete history.
- **Configurable retention** — how long a tenant's data is retained overall is governed by the commercial service agreement, consistent with the SRS's data retention requirements (SRS §7.3).

---

## 9. Appendices

### Appendix A — Entity Count Summary

| Domain | Approximate Entity Count |
|---|---|
| Control Plane | 2 |
| Identity & Stakeholder Profiles | 10 |
| Programs & Applications | 18 |
| Business Challenges | 2 |
| Connections | 3 |
| Community Wall | 8 |
| Meetings & Events | 7 |
| Messaging | 3 |
| Commercial | 8 |
| Learning Management | 16 |
| Content | 4 |
| Administrative & Platform Services | 16 |
| Facilities | 12 |
| **Total** | **~109** |

### Appendix B — Glossary

See FRS Section 6, SRS Appendix B, and TAD Appendix C for the shared functional, system, and architectural glossary. Additional data-modeling terms:

| Term | Definition |
|---|---|
| Entity | A distinct business object represented by a database table (e.g. Startup, Program, Membership). |
| Primary Key | The unique internal identifier for a row within an entity's table. |
| Foreign Key | A column referencing the primary key of another entity, expressing a relationship between them. |
| Polymorphic Reference | A relationship where a single column pair (type + identifier) can point to more than one kind of related entity, rather than a fixed single target. |
| Soft Deletion | Marking a record as removed via a timestamp field, rather than physically deleting the row, to preserve history and referential integrity. |
| Cardinality | The number of related records permitted on each side of a relationship (e.g. one-to-many, denoted 1..N). |

---

*End of Document*
