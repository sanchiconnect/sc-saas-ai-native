# Policy Library
**SpecPod Framework v2.1.0 · PolicyCatalog Reference**
**Last Updated:** 2026-05-27

---

## Purpose and Usage

This is the authoritative compliance rail library for PolicyCatalog. Each policy entry defines:
- **Signal keywords** — terms in requirements that trigger this policy
- **Guard prompt** — concrete instruction injected into the AI Builder's context window
- **Reviewer check** — what the POD Lead or Gate reviewer must verify before sign-off
- **Gate blocker** — whether a missing implementation of this policy blocks a HITL gate

PolicyCatalog matches requirement text and PII field annotations against signal keywords to assign policies. Requirements with compliance signals but no policy match become `POLICY_GAP` entries — these block Gate-1.

---

## Adding New Policies

1. Choose a framework prefix: `GDPR` / `SOC2` / `ISO27001` / `HIPAA` / `INTERNAL`
2. Assign the next sequential number for that framework
3. Fill all four fields: signal keywords, guard prompt, reviewer check, gate blocker
4. Commit this file and restart PolicyCatalog for the change to take effect in the current sprint

---

## Framework Index

| Framework | Policies | Coverage |
|-----------|----------|----------|
| GDPR | POL-GDPR-001 through POL-GDPR-010 | Data protection, consent, rights |
| SOC 2 | POL-SOC2-001 through POL-SOC2-007 | Security, availability, confidentiality |
| ISO 27001 | POL-ISO-001 through POL-ISO-005 | Information security management |
| HIPAA | POL-HIPAA-001 through POL-HIPAA-004 | Health information protection |
| Internal | POL-INT-001 through POL-INT-008 | Organisation-specific engineering standards |

---

---

# GDPR — General Data Protection Regulation (EU) 2016/679

---

### POL-GDPR-001 — Security of Processing (Art. 32)
**Signal keywords:** `password`, `credential`, `authentication`, `login`, `session`, `token`, `secret`, `api key`, `bearer`
**Guard prompt:** Passwords must be hashed using bcrypt (minimum 12 rounds) or Argon2id. Argon2id is preferred for new implementations — parameters: memory 64MB, iterations 3, parallelism 2. Never log credentials, tokens, or secrets in any form — plaintext or hashed. All authentication-related API endpoints must enforce HTTPS-only transport at the application layer (do not rely solely on infrastructure TLS termination). Implement exponential back-off rate limiting on login endpoints: lock after 5 consecutive failures within 10 minutes; lockout duration minimum 15 minutes. Store session tokens in HttpOnly, Secure, SameSite=Strict cookies. Implement CSRF protection on all state-changing endpoints.
**Reviewer check:** (1) Confirm no plaintext credentials appear in any log output, error response, or database column. (2) Verify bcrypt/Argon2 with correct parameter configuration in the auth module. (3) Confirm rate limiting middleware is applied to `/login`, `/register`, and `/reset-password`. (4) Check cookie flags: HttpOnly, Secure, SameSite=Strict present on session tokens. (5) Verify HTTPS redirect at application layer.
**Gate blocker:** YES — auth-related requirements cannot proceed past Gate-1 without this policy satisfied.

---

### POL-GDPR-002 — Data Minimisation (Art. 5.1c)
**Signal keywords:** `collect`, `store`, `user data`, `personal`, `profile`, `record`, `field`, `capture`, `gather`, `persist`
**Guard prompt:** Collect only the minimum PII fields strictly necessary for the stated purpose of each feature. Every PII field in any database schema or API payload must have a documented purpose annotation (e.g., `-- purpose: "Required for account recovery"` in schema comments or OpenAPI description). Do not add convenience fields that are not required by the current sprint requirements. Do not persist derived PII (e.g., full name derived from first + last) unless there is an explicit performance justification. When in doubt, collect less and expand later.
**Reviewer check:** (1) Review every new column in the schema against the requirement it serves. (2) Verify purpose annotations are present on all PII-tagged columns. (3) Flag any field that cannot be mapped to a specific requirement in openspec.yaml.
**Gate blocker:** YES — schema migrations with unannotated PII fields block Gate-1.

---

### POL-GDPR-003 — Right to Erasure (Art. 17)
**Signal keywords:** `delete user`, `account deletion`, `data removal`, `gdpr delete`, `right to erasure`, `anonymise`, `purge`, `wipe account`
**Guard prompt:** Implement hard delete or full anonymisation for user PII — soft delete (setting `deleted_at`) is not sufficient to satisfy Art. 17 unless combined with immediate PII field nullification in the same transaction. Cascade deletion must be verified against all related tables: activity logs (anonymise, do not delete — preserve aggregate integrity), consent records (retain with PII stripped), session tokens (hard delete), profile data (hard delete). Log all deletion events to the immutable audit trail with: user ID (hashed post-deletion), timestamp, initiating actor, and erasure method. Exclude anonymised/deleted records from all analytics aggregations and data exports.
**Reviewer check:** (1) Verify PII fields are nullified or removed — not just flagged — in the users table. (2) Confirm cascade behaviour covers all related tables identified in specs/database.md. (3) Confirm audit log entry is written before the deletion transaction completes. (4) Verify analytics queries have `WHERE deleted_at IS NULL OR pii_erased = false` filters applied.
**Gate blocker:** YES — any deletion-related requirement without this policy is a Gate-1 blocker.

---

### POL-GDPR-004 — Data Portability (Art. 20)
**Signal keywords:** `export data`, `download my data`, `data portability`, `csv export`, `user export`, `data download`, `take my data`
**Guard prompt:** Data exports must include all PII fields associated with the requesting user — including fields the user may not see in the UI (e.g., internal classification tags, inferred attributes). Export format must be machine-readable: JSON (preferred) or CSV. Require re-authentication (password confirmation or MFA challenge) before initiating any export. Rate-limit export requests: maximum 3 export requests per user per 24-hour window. Log all export events to the audit trail with: user ID, timestamp, export format, and field count. Do not include data from other users, aggregate data, or data derived from third-party sources not originally provided by the user.
**Reviewer check:** (1) Confirm re-auth gate is enforced before export initiates. (2) Verify all PII fields from specs/database.md are present in the export payload. (3) Check rate limit implementation on the export endpoint. (4) Verify audit log entry per export event. (5) Confirm the export does not leak other users' data in multi-tenant contexts.
**Gate blocker:** YES.

---

### POL-GDPR-005 — Consent Management (Art. 7)
**Signal keywords:** `consent`, `opt-in`, `opt-out`, `marketing`, `newsletter`, `tracking`, `cookies`, `subscribe`, `agree`, `accept terms`, `preference`
**Guard prompt:** All consent collection must use explicit opt-in mechanisms — pre-checked checkboxes are prohibited. For each consent category (marketing emails, analytics tracking, third-party sharing) maintain a separate, granular consent record with: user ID, consent type, consent version (linked to the legal text at time of consent), timestamp, and collection method (e.g., "registration form v2.3"). The consent schema must support versioning — if the consent text changes, existing users must re-consent before processing resumes. Provide a clearly accessible opt-out mechanism for every opt-in. Do not bundle consent for different purposes into a single checkbox. Do not gate product access on non-essential consent.
**Reviewer check:** (1) Confirm all consent checkboxes are unchecked by default. (2) Verify consent record schema includes: user_id, consent_type, consent_version, consented_at, method. (3) Confirm consent is stored before any downstream processing begins. (4) Verify opt-out is as easy to find as opt-in. (5) Confirm product access is not gated on marketing consent.
**Gate blocker:** YES — any feature involving communication preferences or tracking without this policy blocks Gate-1.

---

### POL-GDPR-006 — Lawful Basis Documentation (Art. 6)
**Signal keywords:** `process`, `use data`, `share data`, `analyse`, `third party`, `partner`, `send to`, `forward`
**Guard prompt:** Every data processing operation must map to one of the six GDPR lawful bases: (1) consent, (2) contract, (3) legal obligation, (4) vital interests, (5) public task, (6) legitimate interests. Do not implement new data processing pathways without a lawful basis annotation in code comments referencing the specs/knowledge.md legal basis register. When legitimate interests is the stated basis, a brief LIA (Legitimate Interests Assessment) note is required in the decision-ledger, not in code.
**Reviewer check:** (1) Confirm all new processing operations have a lawful basis comment in the implementation. (2) Verify the basis is documented in specs/knowledge.md or the decision-ledger.
**Gate blocker:** YES — undocumented processing operations block Gate-1.

---

### POL-GDPR-007 — Data Breach Notification Readiness (Art. 33)
**Signal keywords:** `encryption`, `security incident`, `breach`, `unauthorised access`, `data leak`
**Guard prompt:** Any feature that stores or transmits PII must ensure the data is identifiable in the audit log sufficient to reconstruct what data was affected in a breach. PII storage must be encrypted at rest (see POL-ISO-002). Access to PII data in bulk (>100 records) must require elevated authorisation and generate an audit event. Implement database-level query logging for PII tables to enable breach scope assessment.
**Reviewer check:** (1) Confirm audit log captures sufficient field-level detail for breach scoping. (2) Verify bulk access thresholds are enforced. (3) Confirm PII table query logging is enabled.
**Gate blocker:** NO — warning level. Flag for POD Lead awareness.

---

### POL-GDPR-008 — Data Retention (Art. 5.1e)
**Signal keywords:** `retain`, `archive`, `keep`, `history`, `log`, `expire`, `purge`, `ttl`, `retention period`
**Guard prompt:** Every data entity that persists PII or user activity must have a documented retention period. Retention periods must be implemented as automated cleanup jobs — not manual processes. Default retention periods (override in specs/database.md if different): user activity logs: 24 months; session tokens: 24 hours; email logs: 12 months; audit trail: 7 years (immutable). Deletion from primary storage does not satisfy retention if backups are not also rotated. Document backup retention policy in specs/database.md.
**Reviewer check:** (1) Verify each new table has a retention period annotation. (2) Confirm automated cleanup jobs exist for time-limited entities. (3) Verify backup rotation policy is documented.
**Gate blocker:** NO — warning for Gate-1; blocker for Gate-2 if cleanup jobs are absent.

---

### POL-GDPR-009 — Privacy by Design (Art. 25)
**Signal keywords:** `new feature`, `design`, `architecture`, `system`, `component`, `module`
**Guard prompt:** Apply privacy-enhancing design patterns by default: pseudonymisation of user IDs in logs (use hashed user ID, not raw UUID or email), separate PII storage from behavioural data where practical, avoid unnecessarily joining PII fields into analytics queries. Do not include PII fields in URL parameters, query strings, or browser history. Use opaque reference tokens (not user IDs) in shareable links.
**Reviewer check:** (1) Confirm logs use hashed user IDs. (2) Verify PII is not present in URL parameters. (3) Check that shareable links use opaque tokens.
**Gate blocker:** NO — warning level.

---

### POL-GDPR-010 — Records of Processing Activities (Art. 30)
**Signal keywords:** `processing`, `data flow`, `pii`, `personal data`, `third party send`, `api integration`, `outbound`
**Guard prompt:** Any new data processing activity (new table storing PII, new outbound API sending PII, new analytics pipeline consuming PII) must be documented in the programme's Art. 30 register maintained in specs/knowledge.md under the section "Records of Processing Activities". The entry must include: purpose, lawful basis, data categories, retention period, and recipients (if shared externally).
**Reviewer check:** (1) Confirm any new PII processing is documented in specs/knowledge.md Art. 30 section. (2) Verify recipients are named for any externally shared data.
**Gate blocker:** NO — warning for Gate-1; escalate to POD Lead for Art. 30 update.

---

---

# SOC 2 — System and Organisation Controls (AICPA Trust Services Criteria)

---

### POL-SOC2-001 — Logical Access Controls (CC6.1)
**Signal keywords:** `login`, `authentication`, `admin`, `role`, `permission`, `access control`, `mfa`, `two-factor`, `2fa`, `privileged`, `superuser`
**Guard prompt:** Enforce MFA for all admin-level and privileged roles using TOTP (RFC 6238) or WebAuthn — SMS OTP is not acceptable for admin access due to SIM-swap vulnerability. Implement role-based access control (RBAC) with the principle of least privilege: no role should have permissions beyond what is required for its function. Session tokens expire after 24 hours of inactivity for standard users and 8 hours for admin users. Implement token rotation on privilege escalation. Log all access control grants, revocations, and role changes to the immutable audit trail with approver identity.
**Reviewer check:** (1) Confirm MFA is enforced (not optional) for admin roles. (2) Verify session expiry values per role tier. (3) Confirm RBAC implementation matches the permission matrix in specs/design.md. (4) Verify all role-change events appear in the audit log.
**Gate blocker:** YES — admin access features block Gate-1 without this policy.

---

### POL-SOC2-002 — Audit Logging (CC7.2)
**Signal keywords:** `audit`, `log`, `event`, `action`, `history`, `track changes`, `record`, `trail`, `immutable`
**Guard prompt:** Implement structured audit logging for all create, update, and delete operations on business entities. Each log entry must contain: `event_id` (UUID), `event_type` (CRUD action + entity), `user_id` (hashed), `timestamp` (UTC ISO 8601), `ip_address`, `user_agent`, `affected_record_id`, `before_state` (hash or JSON diff for updates), `after_state` (hash or JSON diff). The audit log table must enforce no UPDATE or DELETE permissions at the database role level — append-only enforced at the DB constraint layer, not just application layer. Retain audit logs for a minimum of 12 months in primary storage, 7 years in cold archive. Log query performance must not degrade primary transaction performance — use async write patterns.
**Reviewer check:** (1) Confirm all CRUD endpoints write an audit event before returning 2xx. (2) Verify UPDATE and DELETE are revoked on the audit_events table at the DB role level. (3) Check that `before_state` and `after_state` are captured for all update operations. (4) Confirm async write pattern is used (no synchronous log blocking primary transaction).
**Gate blocker:** YES — any feature with CRUD operations without audit logging blocks Gate-1.

---

### POL-SOC2-003 — Availability and Fault Tolerance (A1.2)
**Signal keywords:** `background job`, `async`, `queue`, `retry`, `timeout`, `circuit breaker`, `health check`, `uptime`, `sla`, `availability`
**Guard prompt:** All asynchronous operations (email sends, export generation, background processing) must use an idempotent job queue with: at-least-once delivery semantics, configurable retry with exponential back-off (base: 1s, max: 300s, jitter: ±20%), dead-letter queue for jobs that exhaust retries, and a job status API observable by monitoring. Each job must carry a unique idempotency key to prevent duplicate processing on retry. Implement health check endpoints (`/health` and `/ready`) for all service components — do not return 200 from `/health` if a critical dependency (database, cache) is unavailable.
**Reviewer check:** (1) Confirm idempotency keys are generated and stored per job. (2) Verify retry configuration matches the exponential back-off spec. (3) Confirm dead-letter queue is configured. (4) Verify `/health` and `/ready` endpoints exist and accurately reflect dependency status.
**Gate blocker:** NO — warning level. Blocker for async-heavy features at Gate-2 if retry/DLQ absent.

---

### POL-SOC2-004 — Change Management (CC8.1)
**Signal keywords:** `deploy`, `release`, `migration`, `schema change`, `rollback`, `version`, `changelog`
**Guard prompt:** All schema migrations must be versioned, forward-only, and reversible (include both `up` and `down` migrations). Migrations must be committed to version control alongside the code that requires them — never apply a migration manually outside of the automated pipeline. All API changes must increment the API version for breaking changes (new major version) or be additive-only for non-breaking changes. Maintain a CHANGELOG.md updated in the same commit as the code change.
**Reviewer check:** (1) Verify all migrations have `up` and `down` implementations. (2) Confirm no manual migration instructions exist outside the automated pipeline. (3) Verify breaking API changes have incremented the version number. (4) Confirm CHANGELOG.md is updated.
**Gate blocker:** NO — warning. Blocker at Gate-2 for migrations without rollback.

---

### POL-SOC2-005 — Vulnerability Management (CC7.1)
**Signal keywords:** `dependency`, `package`, `library`, `cve`, `vulnerability`, `security scan`, `npm audit`, `pip audit`
**Guard prompt:** Run dependency vulnerability scanning (`npm audit --audit-level=moderate` or equivalent) as part of the sprint start and CI pipeline. Do not introduce new dependencies with known HIGH or CRITICAL CVEs without an approved exception logged in the decision-ledger. For MEDIUM CVEs, document the reachability assessment: is the vulnerable code path reachable in this application? Pin dependency versions in package.json/requirements.txt — do not use unbounded ranges (`^`, `~`, `*`) for production dependencies.
**Reviewer check:** (1) Confirm no HIGH/CRITICAL CVE dependencies are introduced. (2) Verify all new production dependency versions are pinned. (3) Check that a vulnerability scan was run at sprint start.
**Gate blocker:** YES — HIGH or CRITICAL CVEs without an approved exception block Gate-1.

---

### POL-SOC2-006 — Encryption in Transit (CC6.7)
**Signal keywords:** `api call`, `http`, `external`, `webhook`, `outbound`, `send`, `transmit`, `transfer`
**Guard prompt:** All data transmission between services, to external APIs, and to client browsers must use TLS 1.2 minimum; TLS 1.3 preferred. Disable TLS 1.0 and 1.1 at the server configuration level. Validate server certificates on outbound connections — do not set `verify=False` or equivalent. For webhook delivery, use HTTPS endpoints only and implement HMAC signature verification so the recipient can verify payload integrity. Do not send PII in URL parameters or query strings over any network boundary.
**Reviewer check:** (1) Confirm TLS minimum version configuration in server/nginx/load balancer config. (2) Verify outbound HTTP clients have certificate verification enabled. (3) Check webhook implementations include HMAC signing. (4) Confirm no PII appears in URL query strings crossing a network boundary.
**Gate blocker:** YES — any new outbound HTTP client without TLS enforcement blocks Gate-1.

---

### POL-SOC2-007 — Incident Response Readiness (CC7.3)
**Signal keywords:** `alert`, `monitor`, `pagerduty`, `on-call`, `incident`, `error rate`, `threshold`, `slo`, `sla`
**Guard prompt:** Every new service component must have at least one health/error rate alert configured before deployment. Alerts must notify the on-call rotation within 5 minutes of threshold breach. Define SLOs for each new endpoint in the specs/api.md: error budget, latency p95 target, and availability target. Log all alert firings to the audit trail with: alert name, severity, triggered at, acknowledged at, resolved at. Do not configure alerts with a silence period longer than 30 minutes without documenting the rationale.
**Reviewer check:** (1) Confirm alerts are configured for new service components. (2) Verify SLO targets are documented in specs/api.md. (3) Confirm alert-to-on-call notification path is tested.
**Gate blocker:** NO — warning. Escalate if new components deploy without alerts.

---

---

# ISO 27001:2022 — Information Security Management

---

### POL-ISO-001 — Access Control Policy (Annex A 5.15)
**Signal keywords:** `user role`, `permission matrix`, `access level`, `entitlement`, `privilege`, `admin`, `superuser`, `read-only`, `write`, `execute`
**Guard prompt:** Implement access control based on the principle of least privilege and need-to-know. Document the permission matrix for all roles in specs/design.md before implementation begins — do not implement roles without a pre-approved permission matrix. Separate roles for: read, write, delete, and administrative functions. No single role should combine data access with the ability to modify access control settings (segregation of duties). Review and reconfirm all access grants at the end of each sprint — remove dormant permissions.
**Reviewer check:** (1) Confirm permission matrix is documented in specs/design.md. (2) Verify no single role combines data write + access control modification. (3) Check that no dormant permissions accumulate across sprints.
**Gate blocker:** NO — warning for Gate-1. Blocker at Gate-2 if no permission matrix exists.

---

### POL-ISO-002 — Encryption at Rest (Annex A 8.24)
**Signal keywords:** `store`, `persist`, `database`, `file storage`, `s3`, `blob`, `sensitive data`, `at rest`, `disk`, `backup`
**Guard prompt:** Encrypt all PII fields at rest using AES-256-GCM or equivalent AEAD cipher. Field-level encryption is preferred for PII columns over full-disk-encryption alone — both should be present. Encryption keys must be managed via a dedicated key management service (AWS KMS, GCP Cloud KMS, HashiCorp Vault) — hardcoded keys or keys in environment variables are prohibited. Implement key rotation policy: encryption keys must support rotation without service downtime. Document the encryption strategy and key management approach in specs/database.md.
**Reviewer check:** (1) Confirm PII fields in the schema are encrypted at the field level. (2) Verify no hardcoded encryption keys exist in source code or environment variable files. (3) Confirm KMS integration is configured. (4) Verify key rotation is achievable without downtime.
**Gate blocker:** YES — any PII storage feature without field-level encryption blocks Gate-1.

---

### POL-ISO-003 — Secure Development Lifecycle (Annex A 8.25)
**Signal keywords:** `code review`, `pull request`, `merge`, `commit`, `branch`, `ci`, `pipeline`, `build`
**Guard prompt:** No code touching authentication, authorisation, PII handling, or payment flows may be merged without a human code review by the POD Lead. All code must pass the automated CI pipeline (lint, unit tests, security scan) before merge. Branch protection rules must prevent direct commits to `main`/`master`. Static analysis security testing (SAST) must run on every pull request for security-sensitive modules. Scan for secrets in commits using a pre-commit hook or CI step — fail the build if secrets are detected.
**Reviewer check:** (1) Confirm branch protection rules are configured in the repository. (2) Verify SAST is running on PRs for security-sensitive modules. (3) Confirm secret scanning is active. (4) Verify no direct commits to main exist in the sprint's commit history.
**Gate blocker:** YES — any security-sensitive code merged without review blocks Gate-2.

---

### POL-ISO-004 — Third-Party Risk (Annex A 5.19)
**Signal keywords:** `third party`, `vendor`, `external service`, `api integration`, `sdk`, `library`, `plugin`, `saas`, `cloud provider`
**Guard prompt:** Before integrating a new third-party service or library that will handle PII or security-sensitive operations: document the service name, data categories shared, processing location, and contractual safeguards (DPA, SCCs where GDPR applies) in the specs/knowledge.md third-party register. Do not hard-code third-party API credentials in source code — use environment variables or a secrets manager. Implement a circuit breaker or fallback for any critical third-party dependency to prevent a third-party outage from cascading into a system failure.
**Reviewer check:** (1) Confirm new third-party integrations are documented in specs/knowledge.md. (2) Verify no credentials are committed to source control. (3) Confirm circuit breaker/fallback is implemented for critical dependencies.
**Gate blocker:** NO — warning. Escalate to POD Lead if a DPA has not been executed for a PII-handling third party.

---

### POL-ISO-005 — Business Continuity (Annex A 5.30)
**Signal keywords:** `backup`, `recovery`, `restore`, `disaster recovery`, `rto`, `rpo`, `failover`, `replica`
**Guard prompt:** Any new database table or file storage bucket that stores business-critical or PII data must be included in the backup schedule. Document RPO (Recovery Point Objective) and RTO (Recovery Time Objective) targets for the new data store in specs/database.md. Validate that restore procedures work by performing a test restore in the staging environment before the first production deploy. Do not introduce a new persistent data store without confirming it is covered by the existing backup policy or adding it explicitly.
**Reviewer check:** (1) Confirm new data stores are included in the backup schedule. (2) Verify RPO/RTO are documented. (3) Confirm a test restore was performed in staging.
**Gate blocker:** NO — warning for Gate-1. Blocker at Gate-2 for production-bound PII stores without confirmed backup coverage.

---

---

# HIPAA — Health Insurance Portability and Accountability Act (US)

> Note: HIPAA policies activate only when `pii_present: true` AND `pii_categories` includes `health` in openspec.yaml, OR when the organisation is a Covered Entity or Business Associate under HIPAA.

---

### POL-HIPAA-001 — Protected Health Information Safeguards (§ 164.312)
**Signal keywords:** `health`, `medical`, `diagnosis`, `treatment`, `prescription`, `patient`, `clinical`, `phi`, `ehr`, `ehrs`, `hipaa`
**Guard prompt:** Protected Health Information (PHI) must be encrypted in transit (TLS 1.2+) and at rest (AES-256). PHI must never appear in application logs, error messages, or stack traces. Access to PHI must be role-restricted with individual user accountability — shared credentials are prohibited. Implement automatic session termination after 15 minutes of inactivity for any session with PHI access. Maintain an access log for all PHI access events including read operations (not just writes).
**Reviewer check:** (1) Confirm PHI fields are identified and encrypted. (2) Verify PHI does not appear in any log output. (3) Confirm session timeout is 15 minutes for PHI-capable sessions. (4) Verify read access to PHI tables is also logged.
**Gate blocker:** YES — any feature touching PHI without this policy blocks Gate-1.

---

### POL-HIPAA-002 — Minimum Necessary Standard (§ 164.502(b))
**Signal keywords:** `health data`, `patient data`, `medical record`, `phi`, `clinical data`, `query health`
**Guard prompt:** API endpoints and queries that access PHI must request and return only the minimum PHI necessary for the disclosed purpose. Do not join PHI tables broadly and filter in application code — apply WHERE clauses at the database query level to limit PHI exposure. Document the minimum necessary justification for each PHI field accessed in code comments.
**Reviewer check:** (1) Confirm PHI queries apply field-level and row-level filters at the DB layer. (2) Verify minimum necessary justification comments are present on PHI queries.
**Gate blocker:** YES.

---

### POL-HIPAA-003 — Audit Controls (§ 164.312(b))
**Signal keywords:** `phi access`, `health record access`, `medical data`, `patient access`, `health log`
**Guard prompt:** Implement hardware, software, and procedural mechanisms to record and examine activity in information systems containing PHI. Audit records must be tamper-evident and retained for a minimum of 6 years. All PHI access (including read operations) must generate an audit record containing: user identity, date and time, type of action, and the record(s) accessed. Audit records must be stored separately from primary PHI storage to prevent their modification by a compromised application layer.
**Reviewer check:** (1) Confirm read access to PHI tables generates audit events. (2) Verify audit storage is separate from PHI storage. (3) Confirm 6-year retention policy is configured.
**Gate blocker:** YES — PHI features without PHI-specific audit logging block Gate-1.

---

### POL-HIPAA-004 — Business Associate Agreement Compliance (§ 164.308(b))
**Signal keywords:** `third party health`, `phi to vendor`, `health data integration`, `send health`, `share patient`
**Guard prompt:** Before transmitting PHI to any third-party service (cloud provider, analytics platform, email service), confirm that a fully executed Business Associate Agreement (BAA) is in place. Document the BAA in the specs/knowledge.md third-party register with: vendor name, BAA execution date, data categories covered, and storage region. Do not implement the integration until the BAA is confirmed — log the BAA confirmation in the decision-ledger.
**Reviewer check:** (1) Confirm BAA is documented in specs/knowledge.md for all PHI-receiving third parties. (2) Verify decision-ledger contains the BAA confirmation entry.
**Gate blocker:** YES — PHI-sharing integration without BAA confirmation blocks Gate-1.

---

---

# Internal Policies

---

### POL-INT-001 — API Rate Limiting
**Signal keywords:** `api`, `endpoint`, `public`, `external client`, `third party client`, `webhook receiver`, `rate limit`
**Guard prompt:** All externally accessible API endpoints must implement rate limiting at the API gateway or application middleware layer. Standard limits: 100 requests/minute per API key for authenticated endpoints; 10 requests/minute per IP for unauthenticated endpoints. Return `429 Too Many Requests` with a `Retry-After` header specifying the seconds until the limit resets. Log all rate limit violations with: IP, API key (if authenticated), endpoint, and timestamp. Implement a whitelist mechanism for trusted internal service-to-service calls that bypasses rate limits but still logs.
**Reviewer check:** (1) Confirm rate limiting middleware is applied to all external endpoints. (2) Verify 429 response includes `Retry-After` header. (3) Confirm rate limit violations are logged. (4) Verify internal service bypass whitelist is implemented and restricted.
**Gate blocker:** YES — public API endpoints without rate limiting block Gate-1.

---

### POL-INT-002 — PII Field Classification
**Signal keywords:** `name`, `email`, `phone`, `address`, `date of birth`, `national id`, `payment`, `health`, `biometric`, `photo`, `ip address`, `device id`
**Guard prompt:** All PII fields in every database schema and API payload must carry a classification annotation. Use the following classification taxonomy: `PII_DIRECT` (identifies a person: name, email, phone, national ID), `PII_INDIRECT` (identifies a person in combination: IP address, device ID, location), `PII_SENSITIVE` (special category: health, biometric, financial, political), `PII_DERIVED` (computed from other PII: age from DOB, full name from first+last). Annotate in schema comments: `-- pii: PII_DIRECT | purpose: "account identification"`. Never return PII in error messages, stack traces, or debug output. Apply field-level access controls — not all roles should have access to all PII_SENSITIVE fields.
**Reviewer check:** (1) Confirm all PII fields have classification annotations. (2) Verify PII_SENSITIVE fields have field-level access controls applied. (3) Confirm no PII appears in any error response body.
**Gate blocker:** YES — unannotated PII fields in schema migrations block Gate-1.

---

### POL-INT-003 — Error Handling Standards
**Signal keywords:** `error`, `exception`, `catch`, `try`, `throw`, `status code`, `error response`, `400`, `500`, `fault`
**Guard prompt:** Never expose internal system details (stack traces, database error messages, internal IDs, file paths, server hostnames) in API error responses returned to clients. Implement a consistent error response schema: `{ "error": { "code": "MACHINE_READABLE_CODE", "message": "Human-readable message", "request_id": "UUID" } }`. Use a global error handler to catch unhandled exceptions and return a generic 500 response while logging the full exception detail server-side with the request_id for correlation. Map all validation errors to 400 with field-level error arrays. Log all 5xx errors with full context. Do not use generic error messages that could reveal implementation details (e.g., "MySQL error 1062" — instead: "A record with this value already exists").
**Reviewer check:** (1) Confirm no stack traces appear in API responses. (2) Verify error response schema is consistent across all endpoints. (3) Confirm global error handler is implemented. (4) Check that 5xx errors are logged with full server-side context.
**Gate blocker:** YES — any endpoint returning internal details in error responses blocks Gate-1.

---

### POL-INT-004 — Secrets Management
**Signal keywords:** `api key`, `secret`, `credential`, `password`, `token`, `private key`, `certificate`, `connection string`, `env`, `.env`
**Guard prompt:** No secrets (API keys, database passwords, private keys, third-party tokens) may be committed to source control in any form — including in `.env` files, test fixtures, or comments. Use environment variables loaded from a secrets manager (AWS Secrets Manager, HashiCorp Vault, or equivalent) at runtime. The `.gitignore` must exclude all `.env*` files. Implement pre-commit hooks (e.g., git-secrets, truffleHog) that fail the commit if a secret pattern is detected. When rotating a secret, update all deployment environments within the same sprint day — do not leave stale secrets in any environment.
**Reviewer check:** (1) Confirm `.gitignore` excludes `.env*` files. (2) Verify pre-commit secret scanning hook is installed and active. (3) Confirm no secrets are hardcoded in any source file, including tests. (4) Verify secrets are loaded from environment variables backed by a secrets manager.
**Gate blocker:** YES — any committed secret blocks Gate-1 immediately and requires a secret rotation before proceeding.

---

### POL-INT-005 — Input Validation and Injection Prevention
**Signal keywords:** `user input`, `form data`, `query param`, `path param`, `request body`, `search`, `filter`, `sql`, `query`, `database`, `html`, `render`, `template`
**Guard prompt:** Validate and sanitise all user-supplied input at the API boundary before use in any database query, file system operation, or HTML rendering context. Use parameterised queries or prepared statements exclusively — never concatenate user input into SQL strings. Apply a schema validation library (e.g., Zod, Joi, Pydantic) to all request bodies and parameters — reject requests that fail schema validation with a 400 response and a field-level error message. Encode all user-supplied content before rendering in HTML (XSS prevention). Apply Content Security Policy headers on all HTML responses. Validate file uploads: check MIME type, file extension, and maximum size server-side — do not trust client-supplied content-type headers.
**Reviewer check:** (1) Confirm parameterised queries are used for all database interactions — grep for string concatenation patterns in SQL. (2) Verify schema validation is applied at every API entry point. (3) Confirm HTML output encoding is applied to all user-controlled content. (4) Verify file upload validation covers MIME type, extension, and size.
**Gate blocker:** YES — SQL injection or XSS vulnerabilities detected during review block Gate-2.

---

### POL-INT-006 — Dependency Version Pinning
**Signal keywords:** `package.json`, `requirements.txt`, `pyproject.toml`, `go.mod`, `pom.xml`, `gemfile`, `dependency`, `install`, `npm`, `pip`, `yarn`
**Guard prompt:** All production dependencies must be pinned to an exact version — do not use unbounded version ranges (`^`, `~`, `>=`, `*`). Use a lock file (`package-lock.json`, `yarn.lock`, `poetry.lock`, `Pipfile.lock`) committed to source control. Update dependencies intentionally (sprint-start dependency review) not automatically via Dependabot auto-merge. For development dependencies, caret/tilde ranges are acceptable but still prefer exact pinning. Document any intentional version range exception in a comment.
**Reviewer check:** (1) Confirm all production dependency entries in the manifest use exact versions. (2) Verify the lock file is committed. (3) Confirm no Dependabot auto-merge is enabled for production dependencies.
**Gate blocker:** NO — warning. Flag for POD Lead if unbounded ranges are introduced.

---

### POL-INT-007 — Database Migration Safety
**Signal keywords:** `migration`, `schema change`, `alter table`, `drop column`, `rename`, `add column`, `index`, `constraint`
**Guard prompt:** All schema changes must be backward-compatible with the currently deployed application version — do not drop or rename columns in the same migration that deploys code depending on the new schema (use the expand-contract pattern: add new, migrate data, update code, then remove old in a later sprint). Non-null columns must have a server-side default or be added in a separate migration after the application code that populates them is deployed. Large table migrations (>100K rows) must use a background migration strategy to avoid locking. Test all migrations in the staging environment before production deploy.
**Reviewer check:** (1) Confirm no destructive schema changes (DROP, RENAME) are paired with code changes in the same deploy without the expand-contract pattern. (2) Verify new NOT NULL columns have defaults or are deployed after the application code. (3) Confirm large-table migrations use a background strategy.
**Gate blocker:** YES — destructive schema changes without expand-contract pattern block Gate-2.

---

### POL-INT-008 — Frontend Security Headers
**Signal keywords:** `html response`, `web page`, `browser`, `frontend`, `http headers`, `csp`, `cors`, `cookie`, `iframe`, `clickjacking`
**Guard prompt:** All HTML responses must include the following security headers: `Content-Security-Policy` (define an explicit policy — do not use `unsafe-inline` or `unsafe-eval` without a documented exception), `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy` (disable unused browser features). Configure CORS to allow only explicitly listed origins — do not use `Access-Control-Allow-Origin: *` on authenticated endpoints. Set cookie attributes: `HttpOnly`, `Secure`, `SameSite=Strict` (or `Lax` for cross-site navigation needs).
**Reviewer check:** (1) Run a security header check (securityheaders.com or equivalent in CI) and confirm all required headers are present. (2) Confirm CSP does not include `unsafe-inline` or `unsafe-eval` without documented exception. (3) Verify CORS origin whitelist is explicit. (4) Confirm session cookies carry all three security flags.
**Gate blocker:** YES — missing `X-Frame-Options` or `X-Content-Type-Options` blocks Gate-2 for any feature with an HTML response surface.

---

## Maintenance Log

| Date | Change | Author |
|------|--------|--------|
| 2026-05-27 | Initial v2.1.0 release — GDPR, SOC2, ISO27001, HIPAA, Internal | SpecPod Framework |

