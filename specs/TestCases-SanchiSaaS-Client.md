# SanchiSaaS Platform
## Test Case Specification

---

**Document Type:** Test Case Specification
**Product:** SanchiSaaS — Incubator & Accelerator Management Platform
**Modules Covered:** Member Web Application, Administration Panel
**Test Levels Covered:** Unit, Integration, System, Performance, Security
**Version:** 1.0
**Date:** July 2026
**Prepared For:** Client Review
**Companion Documents:** FRS v1.0, SRS v1.0, TAD v1.0, DDD v1.0
**Classification:** Confidential

---

> **A note on scope.** This document specifies **test cases** — designed scenarios with defined preconditions, steps, and expected results — for each test level. It is a test *specification*, not a test *execution report*: no pass/fail results, defect counts, or coverage percentages are presented here, since those are only meaningful once a test case has actually been run against a specific build in a specific environment. Execution results belong in a separate Test Execution Report, produced per test cycle once these cases (or an agreed subset) are run.

---

## Table of Contents

1. Introduction
   1.1 Purpose
   1.2 Scope
   1.3 Test Case Format
   1.4 Priority Definitions
   1.5 References
2. Test Strategy Overview
   2.1 Test Levels
   2.2 Entry & Exit Criteria (Indicative)
   2.3 Test Environment Requirements
3. Unit Test Cases
4. Integration Test Cases
5. System Test Cases
6. Performance Test Cases
7. Security Test Cases
8. Coverage Summary & Traceability
9. Appendices
   A. Test Data Categories
   B. Glossary

---

## 1. Introduction

### 1.1 Purpose

This document specifies the test cases designed to verify the SanchiSaaS platform against the functional and system requirements described in the companion FRS and SRS. It covers five test levels — Unit, Integration, System, Performance, and Security — each targeting a different layer of confidence, from an isolated function's correctness up to the platform's behavior under load and adversarial input.

### 1.2 Scope

Test cases in this document provide **representative coverage across every functional area** described in the FRS (both the Member Web Application and the Administration Panel), rather than one case per individual functional requirement. Each section is organized to trace back to the relevant FRS section, and Section 8 provides a consolidated coverage map.

### 1.3 Test Case Format

Each test case is presented with the following fields:

| Field | Description |
|---|---|
| ID | Unique identifier, prefixed by test level (e.g. `UT-`, `IT-`, `ST-`, `PT-`, `SEC-`). |
| Objective | What the test case verifies. |
| Preconditions | System/data state required before the test can be executed. |
| Key Steps | The sequence of actions performed during the test. |
| Expected Result | The observable outcome that constitutes a pass. |
| Priority | See Section 1.4. |

### 1.4 Priority Definitions

| Priority | Meaning |
|---|---|
| Critical | Covers a core revenue, data-integrity, or access-control path; a failure here blocks release. |
| High | Covers a primary user journey or widely used feature; a failure here requires a fix before release. |
| Medium | Covers a secondary or configurable feature; a failure here is tracked but may not block release. |
| Low | Covers an edge case or cosmetic behavior. |

### 1.5 References

- SanchiSaaS Functional Requirement Specification (FRS), v1.0
- SanchiSaaS System Requirement Specification (SRS), v1.0
- SanchiSaaS Technical Architecture Document (TAD), v1.0
- SanchiSaaS Database Design Document (DDD), v1.0

---

## 2. Test Strategy Overview

### 2.1 Test Levels

| Level | Focus | Typical Owner |
|---|---|---|
| **Unit** | A single function, method, or component in isolation — business logic, calculations, validation rules, state transitions — with external dependencies stubbed or mocked. | Development team |
| **Integration** | Interaction between two or more components — a front-end module and its backend API, a backend service and a third-party gateway, a workflow that spans multiple database entities. | Development / QA team |
| **System** | A complete, realistic end-to-end user journey through the live application, exercising multiple modules in the order a real user would encounter them. | QA team |
| **Performance** | System behavior under specified load, concurrency, or data-volume conditions — response time, throughput, and stability. | QA / Performance engineering |
| **Security** | Resistance to unauthorized access, data exposure, and common web-application attack patterns, and correct enforcement of authentication, authorization, and tenant isolation. | QA / Security review |

### 2.2 Entry & Exit Criteria (Indicative)

| Level | Entry Criteria | Exit Criteria |
|---|---|---|
| Unit | Code for the unit under test is complete and compiles/builds. | All unit test cases for the change pass; no reduction in existing coverage. |
| Integration | Dependent components/services are deployed to a shared test environment. | All integration test cases pass; no critical/high defects open. |
| System | A stable build is deployed to a system-test environment with representative tenant configuration and seed data. | All system test cases pass, or all failures are triaged with an agreed disposition. |
| Performance | A system-test-equivalent environment is available, sized to a documented, agreed capacity profile. | Measured response times and throughput meet the agreed targets in the SRS (§6.1–6.2), or deviations are explicitly accepted. |
| Security | A system-test-equivalent environment is available; testing is explicitly authorized against that environment. | No unresolved critical/high-severity findings; all findings are triaged and tracked to resolution or explicit acceptance. |

### 2.3 Test Environment Requirements

- A dedicated, non-production tenant (or set of tenants) representative of the client's intended configuration (enabled feature flags, branding, stakeholder types).
- Seed data covering each stakeholder type, at least one active program with multiple rounds, at least one published course, and test-mode credentials for each integrated payment gateway.
- Test-mode (sandbox) credentials for all third-party integrations exercised by a given test level (payment gateways, email/SMS/WhatsApp delivery, video conferencing), so that Integration, System, and Performance testing does not generate real financial transactions or real communications to real recipients.
- For Performance testing specifically: an environment sized and isolated such that results are not confounded by shared production traffic.
- For Security testing specifically: explicit written authorization scoped to the designated test environment before any adversarial testing begins.

---

## 3. Unit Test Cases

Unit-level cases target discrete business logic where correctness cannot be adequately verified by observation alone — calculations, validation rules, and state transitions.

| ID | Objective | Preconditions | Key Steps | Expected Result | Priority |
|---|---|---|---|---|---|
| UT-AUTH-01 | OTP code is correctly generated and matched against the stored/hashed value at verification. | OTP generation function is available in isolation. | 1) Generate an OTP for a test identifier. 2) Submit the correct code. 3) Submit an incorrect code. | Correct code verifies successfully; incorrect code is rejected; the stored code is never comparable in plain text. | Critical |
| UT-AUTH-02 | Session/account-type guard correctly permits or blocks access based on the expected account type for a route. | Guard function isolated with mock user objects of varying account types. | 1) Invoke the guard with a matching account type. 2) Invoke it with a non-matching account type. 3) Invoke it with no authenticated user. | Matching type is permitted; non-matching type is redirected/blocked; unauthenticated is blocked. | Critical |
| UT-PROF-01 | Profile completeness calculation correctly reflects which required sections are filled. | Completeness function isolated with a mock stakeholder profile object. | 1) Compute completeness for an empty profile. 2) Fill one required section and recompute. 3) Fill all required sections and recompute. | Completeness percentage increases monotonically and reaches 100% only when all required sections are filled. | High |
| UT-PROF-02 | Approval-workflow state transitions (pending → approved / pending → rejected) are mutually exclusive and cannot be applied to an already-finalized profile without an explicit reset. | Approval state-machine function isolated. | 1) Approve a pending profile. 2) Attempt to reject the same (now approved) profile without a reset step. | Step 1 succeeds and sets status to approved. Step 2 is rejected/blocked by the state machine. | High |
| UT-FORM-01 | Dynamic form engine correctly shows/hides a conditional field based on its configured visibility rule. | A form schema with one conditional field is loaded into the form-rendering function. | 1) Set the controlling field to a value that should hide the conditional field. 2) Set it to a value that should show it. | The conditional field's visibility and validators toggle correctly in both directions. | High |
| UT-FORM-02 | Multi-value (repeatable) form sections correctly add and remove entries without corrupting sibling entries. | A form schema with a repeatable section is loaded. | 1) Add three repeated entries with distinct values. 2) Remove the middle entry. | The remaining two entries retain their original values and correct order. | Medium |
| UT-PAY-01 | Checkout price calculation correctly computes subtotal, discount, tax, and final amount for a range of coupon and tax configurations. | Pricing calculation function isolated with representative coupon/tax fixtures. | 1) Calculate price with no coupon, standard tax. 2) Calculate with a percentage coupon. 3) Calculate with a flat-amount coupon exceeding the subtotal. | Amounts are correct in each case; a coupon never drives the final amount below zero. | Critical |
| UT-PAY-02 | Tax split (e.g. dual-component vs. single-component tax) is applied correctly based on whether the billing location matches the tenant's registered location. | Tax calculation function isolated with same-location and different-location fixtures. | 1) Calculate tax for a same-location billing address. 2) Calculate tax for a different-location billing address. | The correct tax treatment is applied in each case, and the two components (where applicable) sum to the configured total rate. | High |
| UT-MEM-01 | Membership end-date calculation correctly applies a hard-expiry cycle vs. a rolling renewal, per plan configuration. | Membership duration calculation function isolated. | 1) Calculate the end date for a new hard-expiry annual plan purchased mid-cycle. 2) Calculate the end date for a rolling renewal of an existing plan. | Hard-expiry plans end on the configured fixed boundary regardless of purchase date; rolling renewals begin the day after the prior term's end date. | High |
| UT-GRM-01 | Growth-metric period labeling correctly reflects monthly vs. quarterly configuration, including a configurable financial-year start month. | Metric period-formatting function isolated with monthly and quarterly fixtures. | 1) Format a period label under monthly configuration. 2) Format a period label under quarterly configuration with a non-January financial-year start. | Labels are correctly formatted and quarters are correctly bucketed relative to the configured financial-year start. | Medium |
| UT-CONN-01 | Connection policy evaluation correctly resolves the effective rule (can-connect, can-search, moderation-required) for a given pair of stakeholder types, applying any per-profile override over the global default. | Policy evaluation function isolated with a global-matrix fixture and an override fixture. | 1) Evaluate a pair with no override — expect the global default. 2) Evaluate the same pair with a profile-level override present. | The override takes precedence when present; the global default applies otherwise. | High |
| UT-CERT-01 | Certificate/ID card number generation produces a correctly formatted, sequential number given a configured prefix and issuance date. | Number-generation function isolated. | 1) Generate a number for the first issuance of a day. 2) Generate a second number for the same day. | Both numbers follow the configured format and are sequential/unique. | Medium |
| UT-ADM-01 | Admin generic form-field validation correctly enforces required/format rules defined in field configuration, independent of entity type. | Field-validation function isolated with a mixed field-configuration fixture (text, email, date, relation). | 1) Submit valid values for every field type. 2) Submit an invalid value for each field type in turn. | Valid submission passes; each invalid field is independently flagged with an appropriate error. | Medium |
| UT-RND-01 | Program round-progression logic correctly determines the next valid round and rejects an out-of-sequence move. | Round-progression function isolated with a fixture program having three ordered rounds. | 1) Move an application from round 1 to round 2. 2) Attempt to move the same application directly from round 1 to round 3. | Sequential move succeeds; skip-ahead move is rejected unless explicitly permitted by configuration. | High |
| UT-SCORE-01 | Weighted vs. unweighted rating aggregation produces the correct overall score for a set of jury sub-ratings. | Score-aggregation function isolated with weighted and unweighted fixtures. | 1) Aggregate three sub-ratings under unweighted configuration. 2) Aggregate the same three sub-ratings under a weighted configuration with distinct weights. | The unweighted result is the simple mean; the weighted result correctly reflects the configured weights. | High |

---

## 4. Integration Test Cases

Integration-level cases verify that two or more components — front end and API, backend and a third-party service, or a multi-entity workflow — work correctly together.

| ID | Objective | Preconditions | Key Steps | Expected Result | Priority |
|---|---|---|---|---|---|
| IT-AUTH-01 | End-to-end OTP login issues a valid session for a registered user. | A registered, approved test account exists. | 1) Request an OTP for the account's email. 2) Retrieve the OTP from the test-mode delivery channel. 3) Submit it to the verification endpoint. | A valid session is established and the user is redirected to their role-appropriate dashboard. | Critical |
| IT-AUTH-02 | New-user registration creates a linked User and stakeholder-profile record, and triggers verification correctly. | Tenant configured for open registration. | 1) Submit registration for a new startup account. 2) Complete required OTP verification(s). | A User record and a linked Startup profile record are created; the account can log in and lands on profile completion. | Critical |
| IT-PROF-01 | Submitting a profile for approval and an administrator approving it updates status consistently across the member view and the admin view, and triggers the expected notification. | A test startup profile is complete but not yet submitted; an admin account exists. | 1) Submit the profile for approval as the member. 2) Approve it as the administrator. | The profile shows "approved" in both the member and admin views; the member receives an approval notification; the profile becomes visible in the public directory. | Critical |
| IT-PROG-01 | A complete program application (form submission, optional payment, and document upload) is correctly recorded and visible on the admin review board in the correct round. | A published program with an application form and at least one round exists. | 1) Complete and submit the application form as a test applicant. 2) Complete any required payment. 3) Log in as an administrator and open the program's review board. | The submission appears in the correct round with all submitted data and any required payment marked as completed. | Critical |
| IT-PROG-02 | Administrator round-progression action (move/reject/tentative) updates the applicant's status and triggers the expected notification. | An application exists in an active round. | 1) As an administrator, move the application to the next round. 2) As the applicant, check application status. | The applicant's status reflects the new round; the applicant receives a status-change notification. | High |
| IT-PAY-01 | Checkout completes successfully through each configured payment gateway in test mode, producing a matching order and transaction record. | At least one payment gateway is configured in test/sandbox mode; a payable item (e.g. a membership plan) exists. | 1) Initiate checkout for the payable item. 2) Complete payment via the test-mode gateway flow. | An order and transaction record are created with a "successful" status, and access to the purchased item is granted. | Critical |
| IT-PAY-02 | A failed or cancelled payment does not grant access to the purchased item and is reflected accurately in order status. | Same as IT-PAY-01. | 1) Initiate checkout. 2) Deliberately fail/cancel the payment at the gateway. | The order is marked failed/cancelled; the purchased item remains inaccessible; the checkout UI reflects the failure clearly. | High |
| IT-CONN-01 | Sending, accepting, and messaging a connection request works end-to-end, including the resulting ability to message. | Two approved test accounts of connectable stakeholder types exist. | 1) Send a connection request from account A to account B. 2) Accept it as account B. 3) Send a message from A to B. | The connection status becomes "accepted"; a conversation is available between A and B and the message is delivered. | High |
| IT-COMM-01 | Posting to the community feed and reacting/commenting from a second account updates counts and visibility correctly for both accounts. | Two approved test accounts with community feed enabled. | 1) Post as account A. 2) Comment and react as account B. 3) Reload the feed as account A. | The post shows the new comment and reaction count; account A can view B's comment. | Medium |
| IT-MTG-01 | Scheduling a meeting, the invitee accepting it, and both parties joining the video session works end-to-end. | Two accounts with meeting scheduling enabled. | 1) Schedule a meeting from account A to account B. 2) Accept as account B. 3) Join the meeting from both accounts at the scheduled time (test window). | Both parties can join the same video session; the meeting shows as accepted on both accounts' calendars. | Medium |
| IT-LMS-01 | Enrolling in a paid course, completing checkout, and accessing course content works end-to-end, and completing the course issues a certificate. | A paid course with certificate issuance enabled exists. | 1) Enroll and complete checkout as a test learner. 2) Access and complete all lessons. 3) Check the learner's certificates. | Course content is accessible immediately after payment; a completion certificate is issued once all lessons are marked complete. | High |
| IT-FAC-01 | Booking a facility, completing any required payment, and checking in via the kiosk flow works end-to-end. | A published, bookable facility with a fee exists. | 1) Book an available slot as a test member. 2) Complete payment if required. 3) Check in via the booking's check-in action. | The booking is confirmed, payment (if any) is recorded against it, and check-in is recorded with a timestamp. | Medium |
| IT-OUT-01 | An administrator's broadcast message correctly filters recipients by the configured criteria and is dispatched through the configured channel. | At least two test accounts with distinguishable attributes (e.g. different industries) exist. | 1) Compose a broadcast filtered to one industry. 2) Send it. | Only accounts matching the filter receive the message via the configured channel (email/WhatsApp), verified via the test-mode delivery channel. | Medium |
| IT-AI-01 | Submitting applications for AI-assisted scoring, polling for completion, and reviewing finalized results works end-to-end. | A program with AI-assisted evaluation enabled and at least one submitted application. | 1) Trigger AI-assisted scoring from the admin review board. 2) Poll until scoring completes. 3) Review and finalize results. | Each submitted application receives a score and rationale consistent with the configured evaluation criteria; results are visible on the admin review board after finalization. | Medium |
| IT-TIX-01 | Raising a support ticket, an administrator assigning and responding to it, and the member seeing the response works end-to-end. | A test member account and a test admin account exist. | 1) Raise a ticket as the member. 2) Assign and respond as the administrator. 3) View the ticket as the member. | The member sees the administrator's response in the ticket thread; the member receives a notification of the response. | Medium |

---

## 5. System Test Cases

System-level cases exercise a complete, realistic journey through the live application from the perspective of a specific role, spanning multiple modules in the order a real user would encounter them.

| ID | Objective / Journey | Preconditions | Key Steps | Expected Result | Priority |
|---|---|---|---|---|---|
| ST-STU-01 | A prospective startup founder registers, completes their profile, applies to a program, pays an application fee, progresses through evaluation rounds, and is approved. | A published, paid program with at least two rounds and a jury assigned. | 1) Register as a startup. 2) Complete profile sections to 100%. 3) Apply to the program and complete the form and payment. 4) As an administrator/jury, evaluate and progress the application through both rounds. 5) Approve the startup's profile. | The founder can track status at every stage; the profile is approved and visible in the public directory; a certificate/ID card is issued if configured. | Critical |
| ST-INV-01 | An investor registers, completes their profile, discovers startups via the directory, and connects with one. | At least one approved startup profile exists in the directory. | 1) Register and complete an investor profile. 2) Browse the startup directory with filters. 3) Send a connection request to a startup. 4) Accept from the startup side and exchange a message. | The investor can find and connect with relevant startups end-to-end, and messaging works once connected. | High |
| ST-JOB-01 | A job seeker discovers a job posting, registers, applies with a resume, and is scheduled for a video interview by the employer. | A published job posting from a test employer account exists. | 1) Browse public job listings and open a posting. 2) Register as a job seeker and apply with a resume. 3) As the employer, shortlist the candidate and schedule a video interview. 4) Join the video interview from both accounts. | The full hire-to-interview journey completes without requiring manual intervention outside the documented flow. | High |
| ST-CORP-01 | A corporate posts a business challenge, it is approved, a startup discovers and applies to it, and the corporate reviews the submission. | A test corporate account and a test startup account exist. | 1) Create and submit a challenge as the corporate. 2) Approve it as an administrator. 3) Discover and apply to the challenge as the startup. 4) Review the submission as the corporate. | The challenge lifecycle (creation → approval → discovery → application → review) completes end-to-end. | Medium |
| ST-MEN-01 | A mentor completes their profile, is approved, logs a mentorship session with a startup, and the startup approves and rates it. | Approved mentor and startup accounts exist. | 1) Complete and submit the mentor profile for approval; approve as admin. 2) Log a mentorship session against the startup. 3) Approve the session as the startup. 4) Rate the session. | The session appears as approved and rated on both accounts' views. | Medium |
| ST-PM-01 | A program manager creates a new program end-to-end through the wizard, publishes it, and it becomes visible and applicable to eligible members. | Program manager admin account exists. | 1) Run the program creation wizard (details, form, PM/jury assignment). 2) Publish the program. 3) As a test member, confirm the program appears in discovery and can be applied to. | The program is fully configured and immediately usable by eligible applicants after publishing. | Critical |
| ST-JURY-01 | A jury member logs in, sees their assigned allotments, evaluates and scores an application, and a reviewer approves the rating. | An application is allotted to a test jury account; a reviewer/admin account exists. | 1) Log in as jury and open the dashboard. 2) Open an allotted application and submit ratings/answers. 3) As the reviewer, approve the rating. | The rating is recorded, visible to the reviewer, and reflected in the application's aggregate score once approved. | High |
| ST-FIN-01 | A finance administrator configures a membership plan and payment gateway, a member purchases the membership, and the administrator reconciles the resulting order and invoice. | Finance admin account exists; at least one payment gateway available in test mode. | 1) Configure a new membership plan and activate a payment gateway. 2) As a member, purchase the plan through checkout. 3) As the administrator, locate the resulting order, generate and send the proforma invoice. | The full commercial lifecycle (plan setup → purchase → order → invoice) completes correctly and the member's membership becomes active. | Critical |
| ST-PTR-01 | A partner administrator logs in, onboards a new startup into their ecosystem, and the onboarded startup can log in and complete its profile. | Partner admin account exists. | 1) Log in to the partner portal. 2) Onboard a new startup (individually or via invitation). 3) As the onboarded startup, log in and complete the profile. | The onboarded startup is correctly scoped to the partner and follows the standard profile-completion journey. | Medium |
| ST-SUP-01 | A super-administrator enables a new feature for a tenant, configures its settings, and confirms it becomes available to members without a deployment. | Super-admin account with access to feature configuration exists. | 1) Enable a currently-disabled feature (e.g. facilities or learning management) for the test tenant. 2) Configure any required settings for that feature. 3) Log in as a member and confirm the feature is now visible and usable. | The feature becomes available purely through configuration, with no code deployment required, and functions per its FRS specification. | High |
| ST-REP-01 | An administrator builds a custom reporting dashboard from underlying program and stakeholder data and exports the result. | Program and stakeholder data exist in the test tenant; reporting module enabled. | 1) Build a dashboard with at least two widgets sourced from program and stakeholder data. 2) View the dashboard. 3) Export a widget's data. | The dashboard renders correct, current data reflecting the underlying records, and the export contains matching data. | Medium |

---

## 6. Performance Test Cases

Performance cases verify the system meets its design targets (SRS §6.1–6.2) under specified load, concurrency, or data-volume conditions. Each case should specify its target load profile before execution, agreed with the client ahead of the test cycle.

| ID | Objective | Load Profile (Indicative — to be agreed) | Key Steps | Expected Result | Priority |
|---|---|---|---|---|---|
| PT-01 | Concurrent OTP login requests are served without meaningful degradation. | 100 concurrent login attempts within a 60-second window. | 1) Issue concurrent OTP requests and verifications from distinct test accounts. | 95th-percentile response time remains within the target defined in SRS §6.1; no failed logins attributable to load. | High |
| PT-02 | Stakeholder directory search/filter remains responsive against a large dataset. | A directory seeded with at least 50,000 stakeholder records; 50 concurrent search requests. | 1) Issue concurrent filtered search requests across varied criteria. | Results return within the target response time defined in SRS §6.1.2, with correct pagination. | High |
| PT-03 | The application review kanban board remains usable for a program with a high submission volume. | A single program seeded with at least 10,000 applications across multiple rounds. | 1) Load the review board. 2) Apply filters and page through results. | Board load and filter operations complete within the agreed target; no browser-side unresponsiveness. | Medium |
| PT-04 | Bulk CSV export of a large stakeholder dataset completes without blocking normal platform use. | An export of at least 50,000 records, run concurrently with normal interactive traffic. | 1) Trigger the export. 2) Simultaneously perform normal interactive actions (login, profile edit) as a separate test user. | The export completes successfully within an agreed time bound; interactive operations by other users are not perceptibly degraded. | Medium |
| PT-05 | Checkout and payment-gateway calls remain responsive under concurrent transaction load. | 50 concurrent checkout sessions against a test-mode gateway. | 1) Initiate concurrent checkouts for a payable item. | All transactions complete (success or expected failure) within the target response time, with no order/transaction record corruption or duplication. | Critical |
| PT-06 | Real-time messaging delivers messages with low latency under concurrent active conversations. | 200 concurrent active conversations, each exchanging messages at a defined rate. | 1) Generate concurrent message traffic across the conversation set. | Message delivery latency remains within the target defined in SRS §6.1.4 for the duration of the test. | Medium |
| PT-07 | Video meeting sessions establish successfully under concurrent scheduling. | 50 concurrent meetings scheduled to start within the same 5-minute window. | 1) Join all scheduled meetings at their start time. | All sessions establish successfully within an agreed connection-time target, with no dropped sessions attributable to platform-side load. | Medium |
| PT-08 | Broadcast dispatch to a large recipient cohort completes within an agreed window without impacting other notification delivery. | A broadcast targeted at 50,000 recipients. | 1) Send the broadcast. 2) Concurrently trigger unrelated notifications (e.g. connection requests) to other test accounts. | The broadcast completes dispatch within the agreed window; unrelated notifications are not delayed beyond their own target. | Medium |
| PT-09 | Analytics dashboards render within target time against large underlying datasets. | Dashboards backed by datasets of at least 100,000 rows per widget. | 1) Load a dashboard with multiple data-heavy widgets. | All widgets render within the target response time defined in SRS §6.1.2, using cached results where the platform's caching strategy applies. | Medium |
| PT-10 | The platform sustains a peak submission surge near a program's application deadline. | 500 application submissions within a 10-minute window immediately before a configured deadline. | 1) Submit concurrent applications approaching the deadline cutoff. | All submissions before the deadline are accepted and correctly recorded; the deadline cutoff is enforced consistently across all concurrent submissions. | Critical |
| PT-11 | Large file uploads (pitch decks, videos) complete reliably within target time for typical file sizes. | Concurrent uploads of files at the platform's configured maximum size for each upload type. | 1) Upload multiple large files concurrently from distinct test accounts. | Uploads complete successfully within an agreed time bound proportional to file size; no partial/corrupted uploads. | Medium |
| PT-12 | AI-assisted evaluation completes a large batch of applications within an agreed turnaround time. | A batch of 1,000 applications submitted for AI-assisted scoring. | 1) Trigger batch scoring. 2) Poll until completion. | Scoring completes within the agreed turnaround target, with results available for every submitted application. | Low |

---

## 7. Security Test Cases

Security cases verify authentication, authorization, tenant isolation, and resistance to common attack patterns. All security testing must be performed only against an explicitly authorized, non-production test environment.

| ID | Objective | Preconditions | Key Steps | Expected Result | Priority |
|---|---|---|---|---|---|
| SEC-01 | OTP verification is protected against brute-force guessing. | A test account with a pending OTP verification. | 1) Submit repeated incorrect OTP codes against the same request. | The system locks out or rate-limits further attempts after a defined threshold, rather than allowing unlimited guesses. | Critical |
| SEC-02 | An expired or invalidated session cannot be used to access authenticated functionality. | A test account with an active session. | 1) Log out (or force-expire the session). 2) Attempt to call an authenticated action using the prior session state. | The action is rejected and the user is redirected to re-authenticate. | Critical |
| SEC-03 | Role-based access control correctly blocks an administrator from actions outside their assigned scope. | Test administrator accounts for at least two distinct roles (e.g. program manager scoped to Program A, and a program manager scoped to Program B). | 1) As the Program A manager, attempt to view or act on Program B's applications. | Access is denied; only in-scope programs are visible or actionable. | Critical |
| SEC-04 | Tenant data isolation prevents any cross-tenant data access. | Two distinct test tenants, each with their own seed data. | 1) Authenticate against Tenant A. 2) Attempt to access a record known to exist only in Tenant B (by ID/UUID guessing or direct reference). | The request is rejected or returns no data; no Tenant B data is ever returned to a Tenant A session. | Critical |
| SEC-05 | File upload validates type and size, rejecting disallowed or oversized files. | An upload feature accepting a defined set of file types and a maximum size. | 1) Attempt to upload a disallowed file type. 2) Attempt to upload a file exceeding the configured size limit. | Both attempts are rejected with a clear error; no disallowed or oversized file is stored. | High |
| SEC-06 | Payment and billing data are never exposed in plain, unmasked form outside of the necessary checkout flow. | A completed test transaction exists. | 1) Review API responses and stored records associated with the transaction across order history, invoices, and admin views. | No full card number, CVV, or equivalent sensitive payment credential appears in any response or stored record; the platform relies on the payment gateway's own tokenized handling. | Critical |
| SEC-07 | Search and filter inputs are resistant to injection-style payloads. | Any search/filter input accepting free text. | 1) Submit a range of injection-pattern strings (e.g. SQL metacharacters, script tags) into search/filter fields. | The system treats the input as literal search text; no unintended query behavior or script execution occurs. | Critical |
| SEC-08 | User-generated content (community posts, comments, chat messages) is safely rendered without executing embedded scripts. | A test account able to post community content. | 1) Submit a post/comment/message containing a script-injection payload. 2) View the content as another user. | The payload is rendered as inert text/escaped content; no script executes in the viewing user's browser. | Critical |
| SEC-09 | State-changing administrative actions are protected against cross-site request forgery. | An authenticated administrator session. | 1) Attempt to trigger a state-changing admin action (e.g. approve a profile) via a forged cross-site request rather than the application's own UI. | The forged request is rejected; the action only succeeds when initiated through the application's own protected flow. | High |
| SEC-10 | Signed URLs for private file access expire and cannot be reused indefinitely. | A private file (e.g. a supporting document) with a signed access URL. | 1) Access the file via its signed URL immediately (should succeed). 2) Access the same URL after its configured expiry window. | The first access succeeds; the second is denied. | High |
| SEC-11 | Publicly accessible endpoints do not expose personal or sensitive data beyond what the corresponding public-facing feature requires. | A representative sample of unauthenticated/public endpoints (e.g. public profile pages, public program details). | 1) Call each public endpoint directly and review the full response payload. | No response includes internal identifiers, unrelated personal data, or administrative metadata beyond what the public-facing feature is designed to show. | High |
| SEC-12 | Administrator impersonation ("backdoor login") access is fully captured in the audit trail. | Admin backdoor-login capability enabled for the test tenant. | 1) Initiate an impersonation session into a test member account. 2) Perform an action while impersonating. 3) Review the audit log. | The audit log records the impersonation event, the acting administrator, the impersonated account, and the action taken. | High |
| SEC-13 | Password reset tokens are single-use and time-limited. | A password reset requested for a test administrator account. | 1) Use the reset link to set a new password. 2) Attempt to reuse the same reset link. 3) Request a new reset link and wait past its configured expiry before using it. | The first use succeeds; the second (reuse) and third (expired) attempts are rejected. | High |
| SEC-14 | Rate limiting is enforced on sensitive public-facing endpoints (e.g. OTP dispatch, public resume submission). | Public-facing endpoints known to be rate-limited per the FRS/TAD. | 1) Issue repeated requests to the endpoint in excess of its documented limit within the relevant time window. | Requests beyond the limit are rejected or throttled, rather than processed indefinitely. | Medium |
| SEC-15 | Connection-policy and data-visibility rules (public vs. approved-only content, profile locking) are enforced consistently regardless of entry point. | A tenant configured with restricted content visibility. | 1) Attempt to view restricted content through the standard UI as an ineligible user. 2) Attempt to reach the same content via a direct link/URL. | Both attempts are consistently blocked; there is no direct-link bypass of the configured visibility rule. | High |

---

## 8. Coverage Summary & Traceability

The table below maps each test level's coverage back to the corresponding FRS domain, so that gaps can be identified deliberately rather than by omission.

| FRS Domain | Unit | Integration | System | Performance | Security |
|---|---|---|---|---|---|
| Authentication & Account | UT-AUTH-01/02 | IT-AUTH-01/02 | ST-STU-01 (as part of journey) | PT-01 | SEC-01, SEC-02, SEC-13 |
| Stakeholder Profiles | UT-PROF-01/02 | IT-PROF-01 | ST-STU-01, ST-INV-01 | PT-02 | SEC-04, SEC-11 |
| Programs & Applications | UT-RND-01, UT-SCORE-01 | IT-PROG-01/02 | ST-STU-01, ST-PM-01 | PT-03, PT-10 | SEC-03 |
| Business Challenges | — | — | ST-CORP-01 | — | — |
| Jobs & Hiring | — | — | ST-JOB-01 | — | — |
| Community, Networking & Connections | UT-CONN-01 | IT-CONN-01, IT-COMM-01 | ST-INV-01 | PT-06 | SEC-08, SEC-15 |
| Messaging | — | IT-CONN-01 | ST-INV-01 | PT-06 | SEC-08 |
| Learning Management | — | IT-LMS-01 | — | — | — |
| Events & Meetings | — | IT-MTG-01 | ST-MEN-01 | PT-07 | — |
| Facilities | — | IT-FAC-01 | — | PT-11 | SEC-05 |
| Payments & Membership | UT-PAY-01/02, UT-MEM-01 | IT-PAY-01/02 | ST-FIN-01 | PT-05 | SEC-06 |
| Certificates & ID Cards | UT-CERT-01 | IT-LMS-01 | ST-STU-01 | — | SEC-10 |
| Support Tickets | — | IT-TIX-01 | — | — | — |
| Growth Metrics & Milestones | UT-GRM-01 | — | — | — | — |
| Admin — Stakeholder & Application Management | UT-ADM-01 | IT-PROG-01/02, IT-AI-01 | ST-PM-01, ST-JURY-01 | PT-03, PT-04, PT-12 | SEC-03, SEC-09, SEC-12 |
| Admin — Outreach & Communications | — | IT-OUT-01 | — | PT-08 | SEC-14 |
| Admin — Finance & Reporting | — | — | ST-FIN-01, ST-REP-01 | PT-09 | SEC-06 |
| Admin — Partner & System Configuration | — | — | ST-PTR-01, ST-SUP-01 | — | SEC-04 |

Where a cell is empty, the corresponding combination of domain and test level was judged lower priority for representative coverage and is a candidate for expansion in a subsequent, more exhaustive test cycle — not a statement that the area is untested at every level (most domains are still covered by at least one test level above).

---

## 9. Appendices

### Appendix A — Test Data Categories

| Category | Description |
|---|---|
| Seed Accounts | One approved test account per stakeholder type, plus at least one unapproved/pending account per type. |
| Seed Programs | At least one program per supported track (profile-linked and Call-for-Applications), each with multiple rounds and jury assigned. |
| Seed Commercial Data | At least one membership plan per billing cycle type, at least one active coupon, and test-mode credentials for every configured payment gateway. |
| Seed Content | At least one published course with a quiz, one facility, one event, and representative news/resource/glossary entries. |
| Negative/Edge Data | Deliberately incomplete profiles, expired memberships, cancelled orders, and rejected applications, to support negative-path testing across all levels. |

### Appendix B — Glossary

See FRS Section 6, SRS Appendix B, TAD Appendix C, and DDD Appendix B for the shared glossary. Additional testing terms:

| Term | Definition |
|---|---|
| Test Case | A designed scenario with defined preconditions, steps, and expected result, used to verify a specific behavior. |
| Test Execution Report | A record of the actual outcome (pass/fail, defects raised) of running a set of test cases against a specific build — distinct from this document. |
| Entry/Exit Criteria | The conditions that must be true before a test level can begin, and the conditions that must be true for it to be considered complete. |
| Sandbox/Test Mode | A provider-supplied non-production mode for an integrated third-party service (e.g. a payment gateway), used so that testing does not create real financial or communication side effects. |
| Regression | Re-testing previously verified functionality after a change, to confirm it has not been broken. |

---

*End of Document*
