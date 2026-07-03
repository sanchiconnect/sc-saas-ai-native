# PolicyEnforcer — Policy Scan Report
**Sprint:** SPRINT-2025-W22 | **Generated:** 2025-05-27T16:30:00Z
**Policy Catalogue Version:** 1.0 | **Scan Mode:** Static + Runtime

---

## Release Gate Verdict: ✅ PASS (with medium-severity items logged)

| Severity | Count | Gate Impact |
|----------|-------|-------------|
| Critical | **0** | ✅ No blockers |
| High | **0** | ✅ No blockers |
| Medium | 2 | Logged — next sprint backlog |
| Informational | 3 | Advisory only |
| **Gate Status** | | **PASS** |

---

## Medium Severity Findings

### PM-001 — Insecure Error Message
**Policy:** POL-015 (Error Response Data Leakage)
**Severity:** MEDIUM
**File:** `src/extraction-engine/error-handler.js:47`
**Finding:** Error response includes internal stack trace path in development mode. The `NODE_ENV` check prevents this in production, but the pattern should be eliminated rather than conditioned.

```javascript
// Line 47 — current code:
if (process.env.NODE_ENV === 'development') {
  res.json({ error: err.message, stack: err.stack }); // stack included
}
```

**Remediation:** Remove stack trace from all response paths. Use structured error codes instead. Log the full stack trace server-side only.
**Effort:** 30 minutes
**Owner:** builder-1

---

### PM-002 — Dependency with Known CVE
**Policy:** POL-022 (Dependency Vulnerability Management)
**Severity:** MEDIUM
**Package:** `pdf-parse@1.1.1`
**CVE:** CVE-2024-XXXX — ReDoS vulnerability in regex processing of malformed PDF metadata
**CVSS:** 5.3 (Medium)
**Finding:** Package version has a known ReDoS vulnerability. The attack requires a malformed PDF — mitigated by the upload-service file validation, but the dependency itself should be updated.

**Remediation:** Update `pdf-parse` to `>=1.1.2`. Run test suite after update.
**Effort:** 1 hour (update + regression test)
**Owner:** builder-1

---

## Informational Findings

### PI-001 — Missing Request ID in Logs
**Policy:** POL-031 (Observability)
**Severity:** INFORMATIONAL
**File:** `src/upload-service/upload-handler.js`
**Finding:** Upload events logged without correlation request ID. Makes distributed tracing difficult.
**Recommendation:** Add `requestId` to all log statements via middleware.

### PI-002 — HTTP Keep-Alive Not Configured
**Policy:** POL-042 (Performance Hardening)
**Severity:** INFORMATIONAL
**Finding:** HTTP server default keep-alive timeout used. Explicit configuration recommended for production.

### PI-003 — Missing Response Compression
**Policy:** POL-043 (API Response Optimisation)
**Severity:** INFORMATIONAL
**Finding:** API responses not compressed. For large extraction results, gzip compression would reduce transfer size by ~60%.

---

## Policies Scanned (full list)

| Policy ID | Name | Category | Result |
|-----------|------|----------|--------|
| POL-001 | No PII in Logs | Data Privacy | ✅ Clean |
| POL-002 | No Hardcoded Secrets | Security | ✅ Clean |
| POL-003 | SQL Injection Prevention | Security | ✅ Clean |
| POL-004 | NoSQL Injection Prevention | Security | ✅ Clean |
| POL-005 | Input Validation on User Endpoints | Security | ✅ Clean |
| POL-006 | Encryption in Transit | Infrastructure | ✅ Clean |
| POL-007 | Authentication on Secured Endpoints | Security | ✅ Clean |
| POL-008 | GDPR Consent Logging | Data Privacy | N/A — no consent flows in sprint |
| POL-015 | Error Response Data Leakage | Security | ⚠️ MEDIUM — see PM-001 |
| POL-022 | Dependency Vulnerability Management | Security | ⚠️ MEDIUM — see PM-002 |
| POL-031 | Observability | Operational | ℹ️ INFO — see PI-001 |
| POL-042 | Performance Hardening | Infrastructure | ℹ️ INFO — see PI-002 |
| POL-043 | API Response Optimisation | Infrastructure | ℹ️ INFO — see PI-003 |

---

## Compliance Attestation

**Release gate status:** PASS
**Critical violations:** 0 ✅
**High violations:** 0 ✅
**Medium violations:** 2 (logged for next sprint — do not block release)

_POD Lead signature required to finalise Release gate evidence:_
`approved_by:` _________________ `date:` _________________
