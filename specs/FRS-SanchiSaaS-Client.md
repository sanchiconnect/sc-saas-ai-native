# SanchiSaaS Platform
## Functional Requirement Specification

---

**Document Type:** Functional Requirement Specification (FRS)
**Product:** SanchiSaaS — Incubator & Accelerator Management Platform
**Modules Covered:** Member Web Application, Administration Panel
**Version:** 1.0
**Date:** July 2026
**Prepared For:** Client Review
**Classification:** Confidential

---

## Table of Contents

1. Introduction
   1.1 Purpose of This Document
   1.2 Scope
   1.3 Intended Audience
   1.4 Definitions & Abbreviations
2. Product Overview
   2.1 Platform Description
   2.2 System Components
   2.3 User Roles
3. Functional Requirements — Member Web Application
   3.1 Registration & Authentication
   3.2 Account & Profile Management
   3.3 Stakeholder Profiles (Startup, Investor, Mentor, Corporate, Partner, Service Provider, Program Office, Individual)
   3.4 Programs & Call for Applications
   3.5 Business Challenges
   3.6 Jobs & Hiring
   3.7 Community, Networking & Connections
   3.8 Messaging
   3.9 Learning Management (Courses)
   3.10 Events, Meetings & Calendar
   3.11 Content & Resource Library
   3.12 Facilities Booking
   3.13 Payments & Membership Plans
   3.14 Certificates & Digital ID Cards
   3.15 Support Tickets
   3.16 Growth Metrics & Milestones
   3.17 Search & Discovery
4. Functional Requirements — Administration Panel
   4.1 Administrator Authentication & Access Control
   4.2 Stakeholder Management
   4.3 Program & Application Management
   4.4 Business Challenge Management
   4.5 Jury & Evaluation Management
   4.6 Learning Management (Administration)
   4.7 Events & Meetings (Administration)
   4.8 Community Moderation & Connection Settings
   4.9 Finance & Membership Administration
   4.10 Outreach & Communications
   4.11 Content Management
   4.12 Certificates & ID Card Administration
   4.13 Growth Metrics & Milestone Oversight
   4.14 Support Ticket Management
   4.15 Reporting & Analytics
   4.16 Facilities Management (Administration)
   4.17 Partner & Recruitment Administration
   4.18 Custom Form Builder
   4.19 Third-Party Integrations
   4.20 System Configuration
5. Cross-Cutting Platform Capabilities
   5.1 Multi-Tenancy & Branding
   5.2 Feature Configuration
   5.3 Notifications
6. Glossary

---

## 1. Introduction

### 1.1 Purpose of This Document

This Functional Requirement Specification (FRS) describes the functional capabilities of the SanchiSaaS platform as currently implemented, covering both the member-facing web application and the administration panel used by incubator/accelerator program operators. It is intended to give stakeholders a complete, business-readable description of what the platform does, organized by functional area rather than by technical component.

### 1.2 Scope

This document covers two of the platform's application layers:

- **Member Web Application** — the platform used by startups, investors, mentors, corporates, partners, service providers, program offices, individuals, and job seekers.
- **Administration Panel** — the platform used by program operators (super-administrators, program managers, jury members, finance staff, and ecosystem partners) to run and manage their incubator or accelerator program.

Backend services, third-party integration gateways, and the platform's tenant-provisioning control plane are not described in this document, as they do not present a direct user interface to end users or program operators.

### 1.3 Intended Audience

This document is intended for client stakeholders, product owners, and program teams evaluating or overseeing the SanchiSaaS platform's functional coverage.

### 1.4 Definitions & Abbreviations

| Term | Definition |
|---|---|
| Tenant | A single incubator/accelerator organization using the platform, with its own branding, data, and configuration. |
| Stakeholder | Any registered profile type on the platform (startup, investor, mentor, corporate, partner, service provider, program office, individual). |
| CFA | Call for Applications — a structured program application process with configurable rounds. |
| Program | An accelerator, incubator, or venture studio cohort that stakeholders apply to and progress through. |
| Round | A stage within a program's evaluation pipeline (e.g. Screening, Interview, Selection). |
| Jury | A panel of reviewers assigned to score and evaluate program applications. |
| PWA | Progressive Web Application — the member-facing web application. |

---

## 2. Product Overview

### 2.1 Platform Description

SanchiSaaS is a multi-tenant Software-as-a-Service platform purpose-built for startup incubators and accelerators. It provides program operators with the tools to run application cycles, evaluate and progress startups through structured rounds, and manage an ongoing ecosystem of startups, investors, mentors, corporates, and partners — while giving those stakeholders a self-service portal to manage their own profiles, apply to programs, and engage with one another.

Each client organization ("tenant") operates on the platform with its own branding, domain, and independently configurable feature set, while sharing the same underlying application.

### 2.2 System Components

| Component | Description |
|---|---|
| Member Web Application | A responsive, installable web application used by all stakeholder types to manage their profile, apply to programs, and use ecosystem features (networking, learning, events, payments, etc.). |
| Administration Panel | A web-based console used by program operators to configure the platform, manage stakeholders and applications, run evaluations, and administer finance, content, and communications. |

### 2.3 User Roles

**Member Web Application:**

| Role | Description |
|---|---|
| Startup | The primary applicant/member type; manages a company profile, applies to programs, tracks growth metrics and milestones, posts jobs. |
| Investor | Manages an investor profile (organizational or individual); discovers and connects with startups. |
| Mentor | Provides mentorship to startups; logs and has mentorship sessions approved. |
| Corporate | Posts business challenges and engages with startups on innovation initiatives. |
| Partner | An institutional partner managing its own sub-ecosystem of startups, contacts, and a program team. |
| Service Provider | Offers services to startups; maintains a directory profile. |
| Program Office | An institutional program-running partner with its own profile, team, and dashboard. |
| Individual | A non-organizational member profile (e.g. an independent professional). |
| Job Seeker | Searches and applies to job postings on the platform. |
| Public Visitor | An unauthenticated visitor browsing public directories, job/challenge listings, and marketing content. |

**Administration Panel:**

| Role | Description |
|---|---|
| Super-Administrator | Full access to all administrative functions for the tenant. |
| Program Manager | Manages the programs and challenges they are assigned to; reviews and progresses applications. |
| Corporate Program Manager | Manages challenges and applications on behalf of a specific corporate account. |
| Jury Member | Reviews and scores applications, startups, or candidates assigned to them. |
| Recruitment Partner | Manages job postings and applicants for jobs they are assigned to. |
| Partner Administrator | Manages a scoped slice of the ecosystem (their own stakeholders, programs, and contacts). |
| Finance/Operations Staff | Manages membership plans, payment configuration, invoicing, and taxation. |
| Developer/Technical Administrator | Configures platform-level settings, integrations, and reporting infrastructure. |

---

## 3. Functional Requirements — Member Web Application

### 3.1 Registration & Authentication

The platform uses a passwordless, one-time-password (OTP) based authentication model for all member sign-in and registration.

**FR-3.1.1 — OTP-Based Login**
A visitor can log in using either their registered email address or mobile number. The system sends a one-time verification code to the chosen channel; upon entering the correct code, the visitor is authenticated and directed to their role-specific dashboard.

**FR-3.1.2 — Guided Registration**
A new visitor selects their account type (startup, investor, mentor, corporate, partner, service provider, program office, individual, or job seeker) and completes a guided registration flow collecting the relevant profile information. Depending on the program's configuration, the visitor verifies their email and/or mobile number via OTP before the account is created. Upon successful registration, the user is automatically signed in and directed to complete their profile.

**FR-3.1.3 — Invite-Only Registration**
Programs may be configured to restrict registration to holders of a valid invitation code. When enabled, a visitor must present a valid invite code before registration is permitted.

**FR-3.1.4 — Email Verification**
Users receive a verification link by email to confirm their email address as part of the registration and account-security process.

**FR-3.1.5 — Alternative Sign-In Channels**
Where enabled, users may also authenticate via WhatsApp-delivered one-time codes or through an external identity import flow, providing flexible sign-in options per tenant configuration.

**FR-3.1.6 — Session Management & Logout**
Users can log out of the platform at any time, ending their active session. Where a program enforces single active sessions, signing in on a new device automatically ends any prior session.

**FR-3.1.7 — Account Deactivation & Deletion**
Users may temporarily deactivate ("sleep mode") or permanently delete their own account from their account settings, subject to confirmation.

**FR-3.1.8 — Administrator-Assisted Access**
Program administrators can, from the administration panel, initiate a supervised access session into a member's account for support purposes, without requiring the member's credentials.

### 3.2 Account & Profile Management

All authenticated users have access to a personal account settings area, independent of their stakeholder-type profile.

**FR-3.2.1 — Personal Details**
Users can update their name, designation, and contact numbers, and manage a profile photo.

**FR-3.2.2 — Social Links**
Users can add professional social media links (e.g. LinkedIn, X/Twitter) to their profile.

**FR-3.2.3 — Notification Preferences**
Users can control which categories of notifications they receive and through which channel (email, WhatsApp), including a one-click unsubscribe option delivered via email footers.

**FR-3.2.4 — Certificates & ID Cards**
Where enabled, users can view and download certificates and digital ID cards issued to them (see Section 3.14).

**FR-3.2.5 — Membership & Billing History**
Users can view their active membership plan, purchase history, and order/payment status, and download proforma invoices where issued (see Section 3.13).

**FR-3.2.6 — Multiple Profile Types**
Where enabled, a user may hold and switch between more than one profile type on the same account (e.g. a user who is both a mentor and an investor).

**FR-3.2.7 — Team Members**
Organizational account types (startup, investor, corporate, partner, etc.) can add and remove additional team members who share access to the organization's account.

### 3.3 Stakeholder Profiles

Each organizational stakeholder type follows a consistent profile lifecycle, with fields specific to that stakeholder type.

**FR-3.3.1 — Profile Completion**
The stakeholder completes their profile across defined sections (organizational details, industry/technology classification, engagement details, and any tenant-specific custom questions). Profile completeness is tracked and displayed to the user throughout.

**FR-3.3.2 — Logo/Media Upload**
The stakeholder can upload a logo or profile image.

**FR-3.3.3 — Submit for Approval**
The stakeholder submits their completed profile for administrator review and approval, after which the profile becomes visible in relevant directories and search results.

**FR-3.3.4 — Public Profile Page**
Each approved stakeholder has a shareable public profile page that can be viewed by other members and, where configured, by the public.

**FR-3.3.5 — Dashboard**
Each stakeholder type has a dedicated home dashboard summarizing relevant activity: pending tasks, recommendations, upcoming meetings and events, and content of interest.

**Startup-specific capabilities** additionally include:
- Company financials, funding stage, and ongoing funding requirements.
- Founders, team, and advisory board management.
- Pitch deck submission — by file upload, live video recording, or connecting an external recording tool — across multiple pitch purposes (fundraising, sales, hiring).
- Supporting document uploads.
- A public "raising funds" status toggle.
- Growth metrics and milestone tracking (see Section 3.16).

**Investor-specific capabilities** additionally include:
- Organizational or individual investor profile types, each with tailored fields.
- Investment focus and funding-provision status.
- Side-by-side comparison of multiple investor profiles.

**Mentor-specific capabilities** additionally include:
- Mentorship-hours logging, with sessions requiring startup or mentor confirmation and subsequent approval (see Section 3.16 pattern; mentorship approval sits with the counterpart role).

**Corporate-specific capabilities** additionally include:
- Posting and managing business challenges (see Section 3.5).

**Partner-specific capabilities** additionally include:
- A public partner directory listing and detail page with a contact form.
- Managing their own sub-ecosystem of startups (onboarding individually or via bulk invitation).
- Managing a dedicated program team.

**Program Office-specific capabilities** additionally include:
- A public team-member directory for the office.

### 3.4 Programs & Call for Applications

**FR-3.4.1 — Program Discovery**
Members can browse all programs open for application across the program's supported tracks (structured accelerator programs, venture studio programs, and general calls for applications), filtered to the tracks relevant to their account type.

**FR-3.4.2 — Application Submission**
A member applies to a program by completing the program's configured application form. Forms support text, file/media uploads, multi-part sections, and conditional questions, and can auto-save progress as the applicant completes them.

**FR-3.4.3 — Application Fees**
Where a program or a specific evaluation round requires a fee, the applicant completes payment as part of the submission process before the application can be finalized (see Section 3.13).

**FR-3.4.4 — Guest Application**
Prospective applicants can begin an application without first creating a full account, with the system guiding them through registration if needed before finalizing submission.

**FR-3.4.5 — Application Status Tracking**
Applicants can check the status of their application at any time, including by email lookup without needing to log in.

**FR-3.4.6 — Document Re-Submission**
Where a program requests corrected or additional documents after initial submission, the applicant can re-submit the requested items through a dedicated flow.

**FR-3.4.7 — My Applications**
Authenticated applicants can view a consolidated list of all programs they have applied to, along with the current round/status of each.

### 3.5 Business Challenges

**FR-3.5.1 — Challenge Creation**
Corporate members (and, where relevant, other authorized posters) can create a business challenge — a defined problem statement — for startups to respond to, entering review before publication.

**FR-3.5.2 — Public Challenge Discovery**
Visitors and members can browse published business challenges, filter by industry/sector, and view curated challenge collections.

**FR-3.5.3 — Challenge Application**
A startup (authenticated, or registering during the flow) can apply to a published challenge with a solution proposal.

**FR-3.5.4 — Challenge Management**
The posting corporate can view and manage all applicants to their challenge, including reviewing proposed solutions.

**FR-3.5.5 — External Challenge Submission**
Organizations can submit a business challenge through a public submission form without first holding a platform account, entering the same review workflow as authenticated submissions.

### 3.6 Jobs & Hiring

**FR-3.6.1 — Job Posting**
An approved startup can post a job opening, specifying role details, required/preferred skills, compensation range, and workplace type.

**FR-3.6.2 — Public Job Discovery**
Visitors and job seekers can search and filter published job postings by industry, role type, workplace type, skills, and location.

**FR-3.6.3 — Job Application**
A job seeker applies to a posting with a cover letter and resume upload; if not registered, they are guided to register as a job seeker.

**FR-3.6.4 — Applicant Management**
The posting startup reviews applicants, shortlists or rejects candidates, and schedules video interviews directly within the platform.

**FR-3.6.5 — Video Interviews**
Scheduled interviews take place through an embedded video-calling experience with a personal notes panel for the interviewer.

**FR-3.6.6 — Applied Jobs Tracker**
Job seekers can view all jobs they've applied to, their status, and their upcoming interview schedule.

**FR-3.6.7 — Resume Submission Campaigns**
Job seekers can submit their resume for general consideration outside of a specific job posting, to be matched against future openings.

### 3.7 Community, Networking & Connections

**FR-3.7.1 — Community Feed**
Members can post updates, images, and polls to a shared community feed, and comment on and react to others' posts.

**FR-3.7.2 — Connection Requests**
A member can send a connection request to another member; the recipient can accept or decline, optionally with a reason. Accepted connections unlock direct messaging and, where applicable, scheduling.

**FR-3.7.3 — Connection Management**
Members can view their active, pending, sent, and declined connection requests, and remove existing connections.

**FR-3.7.4 — Save for Later**
Members can bookmark other profiles to a personal watch list for future reference.

**FR-3.7.5 — Email-Based Connection Actions**
Members can accept or decline a connection request directly from a link in their notification email, without needing to log in first.

**FR-3.7.6 — Directory Browsing**
Members can browse dedicated directories for each stakeholder type (startups, investors, mentors, corporates, partners, service providers, individuals, program offices), each with tailored search filters.

**FR-3.7.7 — Global Search**
A single search bar allows members to search across all stakeholder types, news, reports, and other content simultaneously.

### 3.8 Messaging

**FR-3.8.1 — Direct Messaging**
Connected members can exchange direct messages, including file attachments, within the platform.

**FR-3.8.2 — Group Conversations**
Members can participate in group conversations, with the ability to rename the group, manage membership, and set a group avatar.

**FR-3.8.3 — Real-Time Delivery**
Messages, typing indicators, and online-status indicators update in real time without needing to refresh the page.

**FR-3.8.4 — Notification Fan-Out**
Members can be notified of new messages via email and push notification, in addition to the in-app inbox.

### 3.9 Learning Management (Courses)

**FR-3.9.1 — Course Catalogue**
Members can browse the tenant's course catalogue, filtered by category, level, and language.

**FR-3.9.2 — Enrollment**
A member enrolls in a course, completing payment first where the course is paid.

**FR-3.9.3 — Course Playback**
Enrolled learners progress through video and article lessons, with playback progress tracked automatically.

**FR-3.9.4 — Quizzes & Assessment**
Courses may include quizzes; learners can attempt a quiz a limited number of times per enrollment and view their results.

**FR-3.9.5 — Course Completion & Certification**
Completing a course automatically triggers issuance of a completion certificate (see Section 3.14), where certificates are enabled.

**FR-3.9.6 — Course Reviews**
Learners can rate and review completed courses.

### 3.10 Events, Meetings & Calendar

**FR-3.10.1 — Webinars**
Members can browse and watch hosted webinars directly within the platform.

**FR-3.10.2 — Program Events & Agenda**
Members can view the full multi-day agenda, sessions, speakers, and booth/venue layout for the program's flagship event.

**FR-3.10.3 — Public Event Registration**
Visitors can register for a public event via a shared link without needing an existing account.

**FR-3.10.4 — One-on-One Meetings**
Members can schedule, accept, decline, and propose alternate times for one-on-one meetings with other members, with automatic calendar integration.

**FR-3.10.5 — Video Meetings**
Scheduled meetings are conducted through an embedded video-calling experience, with shared and personal notes.

**FR-3.10.6 — Meeting Feedback**
Participants can submit structured feedback after a meeting concludes.

**FR-3.10.7 — Availability & Calendar**
Members can set their weekly availability for meeting scheduling and view a consolidated calendar of their meetings and registered events.

### 3.11 Content & Resource Library

**FR-3.11.1 — News Feed**
Members can browse a curated feed of startup ecosystem and technology news, with the ability to set personal topic preferences.

**FR-3.11.2 — Glossary**
Members can browse a searchable glossary of startup, finance, and business terminology.

**FR-3.11.3 — Resource Library**
Members can browse and download curated business documents (templates, guides, policies) and industry reports, with in-app document preview.

**FR-3.11.4 — Platform Updates**
Members can view a feed of platform release notes and announcements.

**FR-3.11.5 — Startup Booster Kit**
Eligible startups can browse and apply for discounted third-party services and perks curated by the program.

**FR-3.11.6 — Market Insights**
Members can access curated market and ecosystem analytics dashboards.

### 3.12 Facilities Booking

**FR-3.12.1 — Facility Directory**
Members can browse the incubator's bookable physical spaces and equipment, viewing details, availability, and pricing.

**FR-3.12.2 — Booking**
A member selects an available time slot and completes the booking, including payment where the facility carries a fee.

**FR-3.12.3 — Booking Management**
Members can view their booking history, check in and out of a booking, and cancel a booking within the program's cancellation policy.

**FR-3.12.4 — Post-Visit Rating**
Members can rate a completed facility booking against configured criteria.

**FR-3.12.5 — Ecosystem Facility Directory**
Where enabled, members can also browse bookable facilities offered by partner organizations across the wider ecosystem.

### 3.13 Payments & Membership Plans

**FR-3.13.1 — Checkout**
Wherever a payment is required (program fees, facility bookings, course enrollment, or membership purchase), the member completes a unified checkout experience presenting the price breakdown, applicable taxes, and any discount applied.

**FR-3.13.2 — Payment Methods**
Payments are supported through multiple configurable payment gateways, selectable per tenant.

**FR-3.13.3 — Coupons & Discounts**
Members can apply a valid coupon code at checkout to receive a discount.

**FR-3.13.4 — Membership Plans**
Members can browse and subscribe to available membership plans, with pricing shown per billing cycle (monthly, quarterly, half-yearly, yearly, or lifetime, as configured).

**FR-3.13.5 — Membership Renewal & Upgrade**
Members are prompted to renew their membership as it approaches expiry, and can request an upgrade to a higher membership tier.

**FR-3.13.6 — Order History & Invoices**
Members can view their full order history and download proforma invoices for completed transactions.

### 3.14 Certificates & Digital ID Cards

**FR-3.14.1 — Certificates**
Where enabled, members receive digital certificates for milestones such as course completion or membership status, each verifiable via a unique certificate number and QR code.

**FR-3.14.2 — Digital ID Cards**
Approved startups (and other stakeholder types, per configuration) can be issued a digital ID card, downloadable and verifiable via QR code.

**FR-3.14.3 — Public Verification**
Anyone holding a certificate or ID card number can verify its authenticity through a public verification page.

### 3.15 Support Tickets

**FR-3.15.1 — Raise a Ticket**
Members can raise a support ticket describing their issue, with the option to attach supporting files.

**FR-3.15.2 — Ticket Conversation**
Members can exchange messages with the support team on an open ticket and view the full history of prior tickets.

### 3.16 Growth Metrics & Milestones

**FR-3.16.1 — Growth Metrics Reporting**
Startups periodically report against a set of key performance indicators defined by the program (e.g. revenue, user growth, custom metrics), viewable as both a data table and trend charts.

**FR-3.16.2 — Metrics Sharing**
Startups can grant selected connections (mentors, investors, etc.) read access to their reported metrics, or invite an external reviewer by email.

**FR-3.16.3 — Milestone Tracking**
Startups can define milestones — both binary (complete/incomplete) and progress-based — with target dates, and track progress over time with supporting notes and file attachments.

**FR-3.16.4 — Milestone Reviewers**
Startups can assign reviewers to their milestones, who can view progress and participate in a discussion thread.

**FR-3.16.5 — Mentorship Hours**
Mentors and startups can log completed mentorship sessions, which require confirmation before being recorded, and can be rated afterward.

### 3.17 Search & Discovery

**FR-3.17.1 — Advanced Filters**
Each stakeholder directory offers advanced filtering (industry, geography, stage, and other relevant attributes), with the ability to save a filter configuration for reuse.

**FR-3.17.2 — Intellectual Property Directory**
Where enabled, members can browse a directory of patents and other intellectual property, and initiate a connection request with the holder's technology transfer office.

---

## 4. Functional Requirements — Administration Panel

### 4.1 Administrator Authentication & Access Control

**FR-4.1.1 — Administrator Login**
Administrators log in with their credentials, or via single sign-on where the tenant has enterprise SSO configured, and are directed to a role-appropriate landing dashboard.

**FR-4.1.2 — Password Recovery**
Administrators can request a password reset link by email.

**FR-4.1.3 — Administrator Account Management**
Super-administrators can create new administrator accounts (which triggers a welcome email with onboarding instructions) and define custom roles with tailored permissions.

**FR-4.1.4 — Role-Based Access**
Every administrative screen and action is scoped to the logged-in administrator's role and, where applicable, their specific assignment (e.g. a program manager sees only the programs they are assigned to; a partner administrator sees only their own ecosystem).

### 4.2 Stakeholder Management

**FR-4.2.1 — Stakeholder Directory**
Administrators can view, search, filter, and sort every stakeholder type registered on the platform.

**FR-4.2.2 — Profile Review**
Administrators can view a stakeholder's complete submitted profile, including all uploaded documents and pitch materials.

**FR-4.2.3 — Approve / Reject**
Administrators approve or reject a stakeholder's profile submission; approval makes the profile visible in public directories and, where configured, triggers automatic certificate or ID card issuance.

**FR-4.2.4 — Ratings**
Administrators can score a stakeholder against configured evaluation criteria.

**FR-4.2.5 — Document & Video Requests**
Administrators can request additional supporting documents or a video pitch submission from a stakeholder, triggering an automated notification to the stakeholder.

**FR-4.2.6 — Connection Permissions**
Administrators can configure, per stakeholder-type pairing, whether members of those types may connect with and search for each other, and set daily connection-request limits.

**FR-4.2.7 — Master Data Management**
Administrators maintain the platform's reference/lookup data (e.g. industries, technology categories) used throughout stakeholder profiles.

**FR-4.2.8 — Bulk Data Import & Export**
Administrators can export stakeholder data to a spreadsheet, and bulk-import or update stakeholder records from a spreadsheet.

### 4.3 Program & Application Management

**FR-4.3.1 — Program Creation Wizard**
Administrators create a new program through a guided, multi-step wizard covering program details, application form design, and assignment of program managers and jury.

**FR-4.3.2 — Program Publishing**
Administrators publish a program to make it visible for applications, and can close, reopen, or archive it as the cycle progresses.

**FR-4.3.3 — Round Configuration**
Administrators define the evaluation rounds a program's applicants will progress through, including scoring criteria and jury assignment per round.

**FR-4.3.4 — Application Review Board**
Administrators review incoming applications on a visual pipeline (kanban) or table view, with filtering, search, and bulk actions.

**FR-4.3.5 — Progressing Applications**
Administrators move an application forward, mark it tentative, or reject it; each action automatically notifies the applicant.

**FR-4.3.6 — Bulk Communication**
Administrators can send a bulk email to all applicants currently in a given round.

**FR-4.3.7 — Data Export**
Administrators can export the full set of applications for a program, or per-round evaluation ratings, to a spreadsheet.

**FR-4.3.8 — AI-Assisted Evaluation**
Where enabled, administrators can run AI-assisted scoring of applications against a configurable evaluation thesis, review the generated results, and re-run scoring for newly added applicants.

**FR-4.3.9 — Program Promotion**
Administrators can request that a program be promoted to another tenant's ecosystem (and approve or decline incoming promotion requests from other tenants), and track resulting engagement.

**FR-4.3.10 — Venture Studio Programs**
Administrators run a parallel program track for venture-studio-style programs, where individual applicants (rather than existing companies) apply and can subsequently be grouped into founding teams.

### 4.4 Business Challenge Management

**FR-4.4.1 — Challenge Creation & Approval**
Administrators review, approve, and publish business challenges submitted by corporates or via public submission.

**FR-4.4.2 — Challenge Assignment**
Administrators assign challenges to specific program managers for ongoing management.

**FR-4.4.3 — Participant Review**
Administrators review the list of startups that have applied to solve a given challenge, along with their proposed solutions.

### 4.5 Jury & Evaluation Management

**FR-4.5.1 — Jury Dashboard**
Jury members see a dedicated dashboard summarizing their assigned evaluations, broken down by status (pending, rated, not interested).

**FR-4.5.2 — Application Review & Scoring**
Jury members review assigned applications and submit scores against the program's configured evaluation criteria, with the option to answer supplementary jury-specific questions.

**FR-4.5.3 — Rating Approval**
A designated reviewer or administrator can review and bulk-approve jury ratings before they are finalized.

### 4.6 Learning Management (Administration)

**FR-4.6.1 — Course Authoring**
Administrators create and structure courses into sections and lessons, assign instructors, and organize courses into categories.

**FR-4.6.2 — Publishing**
Administrators publish or unpublish a course, controlling its visibility to learners.

**FR-4.6.3 — LMS Dashboard**
Administrators view a summary dashboard of course and learner activity, including enrollment trends and top-performing courses.

**FR-4.6.4 — Enrollment Reporting**
Administrators can view and filter enrollment records by date range and course.

### 4.7 Events & Meetings (Administration)

**FR-4.7.1 — Event Creation**
Administrators create multi-date events with defined time slots, and publish them for member registration.

**FR-4.7.2 — Booking Management**
Administrators approve, reschedule, or decline attendee booking requests, and can manually register an attendee.

**FR-4.7.3 — Event Cancellation**
Administrators can cancel a published event, notifying all registered attendees.

**FR-4.7.4 — Meeting Oversight**
Administrators can review the notes, feedback, and session history for any meeting held between members.

**FR-4.7.5 — Feedback Configuration**
Administrators define the questionnaire members complete after a meeting.

### 4.8 Community Moderation & Connection Settings

**FR-4.8.1 — Community Moderation**
Administrators can remove posts and comments from the community feed, and publish official announcements as admin-authored posts.

**FR-4.8.2 — Connection Oversight**
Administrators can view all connection requests across the platform for support and ecosystem-health purposes.

**FR-4.8.3 — Connection Matrix Configuration**
Administrators configure the platform-wide default connection, search, and moderation rules between every pair of stakeholder types, and can reset an individual profile's settings back to those defaults.

### 4.9 Finance & Membership Administration

**FR-4.9.1 — Membership Plan Configuration**
Administrators define membership plans per stakeholder type, including pricing across billing cycles and applicable taxes.

**FR-4.9.2 — Manual Membership Assignment**
Administrators can manually create, adjust the dates of, or remove a membership record on behalf of a member, and process membership upgrade requests.

**FR-4.9.3 — Payment Gateway Configuration**
Administrators configure which payment gateways are active for the tenant, designate a primary gateway, and switch between test and live payment modes.

**FR-4.9.4 — Orders, Transactions & Invoicing**
Administrators can view all payment orders and transactions, generate and resend proforma invoices, and backfill invoices for historical orders.

**FR-4.9.5 — Coupon Management**
Administrators create and manage discount coupons available at checkout.

**FR-4.9.6 — Tax Configuration**
Administrators maintain the tax profiles (rate, type, jurisdiction) applied to orders and invoices.

### 4.10 Outreach & Communications

**FR-4.10.1 — Broadcast Messaging**
Administrators compose and send bulk email or WhatsApp messages to member cohorts filtered by profile status, industry, or geography.

**FR-4.10.2 — Broadcast History**
Administrators can review the history of all broadcasts sent, including delivery details.

**FR-4.10.3 — CRM Contacts**
Administrators maintain a lightweight contact book for outreach purposes, independent of registered members.

**FR-4.10.4 — Canned Chat Responses**
Administrators configure reusable response templates available in the support chat composer.

### 4.11 Content Management

**FR-4.11.1 — News & Announcements**
Administrators publish news articles, glossary terms, and platform product updates.

**FR-4.11.2 — Resource & Report Library**
Administrators upload downloadable resources and industry reports, tagged by industry and visibility.

**FR-4.11.3 — Media Gallery**
Administrators manage a video gallery and homepage/login advertisement banners.

**FR-4.11.4 — Startup Booster Kit**
Administrators curate the catalogue of third-party service offers available to eligible startups.

### 4.12 Certificates & ID Card Administration

**FR-4.12.1 — Template Design**
Administrators design the visual template for certificates and digital ID cards per stakeholder type, including branding, signatories, and validity rules.

**FR-4.12.2 — Bulk Issuance**
Administrators issue certificates or ID cards to eligible stakeholders individually or in bulk.

**FR-4.12.3 — Revocation & Reissuance**
Administrators can revoke, reactivate, or reissue an ID card, and regenerate a certificate's rendering while preserving its original verification number.

### 4.13 Growth Metrics & Milestone Oversight

**FR-4.13.1 — Metrics Configuration**
Administrators define the reporting cadence and the set of key performance indicators startups report against, optionally scoped to specific programs.

**FR-4.13.2 — Metrics Review**
Administrators review submitted metrics per startup and manage requests from startups to amend previously submitted values.

**FR-4.13.3 — Milestone Oversight**
Administrators can view startup-reported milestones and their progress across the platform.

### 4.14 Support Ticket Management

**FR-4.14.1 — Ticket Triage**
Administrators view, search, and assign incoming support tickets to team members.

**FR-4.14.2 — Ticket Response**
Administrators respond to tickets, attach files, adjust ticket severity, and close or reopen tickets as needed.

### 4.15 Reporting & Analytics

**FR-4.15.1 — Custom Dashboards**
Administrators build role-gated analytics dashboards composed of chart and table widgets drawing on the tenant's own program and stakeholder data.

**FR-4.15.2 — Drill-Down & Export**
Administrators can drill into a chart to see the underlying records, and export dashboard data to a spreadsheet.

### 4.16 Facilities Management (Administration)

**FR-4.16.1 — Facility Setup**
Administrators define facility types, individual bookable facilities, availability windows, per-category pricing, and add-ons.

**FR-4.16.2 — Booking Oversight**
Administrators view all bookings on a calendar dashboard and inspect individual booking details.

**FR-4.16.3 — Custom Booking Questions & Ratings**
Administrators configure the questions asked at booking time and the criteria used for post-visit ratings, per facility type.

### 4.17 Partner & Recruitment Administration

**FR-4.17.1 — Partner Portal**
Partner administrators access a dedicated login and dashboard scoped to their own ecosystem, with the ability to manage their stakeholders, invite new members, and maintain a photo gallery.

**FR-4.17.2 — Recruitment Partner Access**
Recruitment partner administrators manage job applicants and interview scheduling for the specific jobs they are assigned to.

**FR-4.17.3 — Premium Feature Requests**
Partner administrators can submit a request for access to premium platform modules not currently enabled for their organization.

### 4.18 Custom Form Builder

**FR-4.18.1 — Form Design**
Administrators build custom application and data-collection forms using a drag-and-drop field builder supporting a wide range of field types and validation rules.

**FR-4.18.2 — Version History**
Every saved change to a form is retained as a recoverable version, which administrators can review and restore.

**FR-4.18.3 — Form Preview**
Administrators can preview a form exactly as an applicant would see it before publishing.

### 4.19 Third-Party Integrations

**FR-4.19.1 — CRM Synchronization**
Administrators connect the platform to a CRM system and configure field-level data mapping for ongoing synchronization.

**FR-4.19.2 — File Storage Management**
Administrators can browse and manage files stored in the platform's cloud storage.

**FR-4.19.3 — Directory Import Tools**
Administrators can run one-off import utilities to bring external directory data into the platform.

**FR-4.19.4 — Intellectual Property Registry**
Administrators (and authorized partners) manage patent and IP records available in the cross-tenant IP directory.

### 4.20 System Configuration

**FR-4.20.1 — Branding & Navigation**
Technical administrators configure the platform's navigation menus and branding elements.

**FR-4.20.2 — Email & Notification Templates**
Technical administrators configure outbound email settings and the content of transactional email templates.

**FR-4.20.3 — Data & Table Configuration**
Technical administrators configure which fields and columns are shown, filterable, and exportable across the platform's data tables and forms.

**FR-4.20.4 — Audit Logging**
Administrators can review a complete history of administrative actions and profile changes for accountability and support purposes.

**FR-4.20.5 — Internal Task Tracking**
Administrators maintain an internal task list for their own team's operational work.

---

## 5. Cross-Cutting Platform Capabilities

### 5.1 Multi-Tenancy & Branding

The platform serves multiple independent client organizations from a shared application, with each tenant presenting its own domain, visual branding, and data — fully isolated from every other tenant.

### 5.2 Feature Configuration

Each tenant's feature set is independently configurable. Modules described in this document — programs, challenges, jobs, learning management, facilities, community, growth metrics, and others — can each be enabled or disabled per tenant to match the client's specific program design.

### 5.3 Notifications

Across both the member application and the administration panel, key actions (approvals, connection requests, meeting invitations, application status changes, ticket updates, and more) trigger notifications delivered via in-app alerts, email, and — where configured — WhatsApp.

---

## 6. Glossary

| Term | Definition |
|---|---|
| Dashboard | The summary home screen presented to a user upon login, tailored to their role. |
| Directory | A searchable, filterable listing of a given stakeholder type. |
| Profile Completeness | A calculated measure of how much of a stakeholder's required profile information has been completed. |
| Kanban Board | A visual, column-based board used to track applications as they move through evaluation rounds. |
| Checkout | The unified payment flow used across all paid actions on the platform. |
| Feature Flag | A per-tenant configuration switch that enables or disables a platform module or capability. |

---

*End of Document*
