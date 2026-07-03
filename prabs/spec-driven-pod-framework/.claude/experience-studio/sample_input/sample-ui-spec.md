# Sample Input — ExperienceStudio

## Sample: `ui-ux.md` Fragment (Authentication Flow)

### Journey: User Login (J-AUTH-001)
**Requirement:** REQ-UI-001
**Role:** Authenticated user

**Intent:** The user must be able to log in to the platform using email and password credentials within 3 interactions. Authentication failure must provide actionable guidance — not a generic error. The login screen must not require scrolling on mobile viewports.

**Success State:** User lands on their personalised dashboard within 2 seconds of successful authentication.

**Failure States:**
1. Invalid credentials — show inline field-level error with "Forgot password" affordance immediately visible
2. Network timeout — show retry option with status indicator; do not clear entered email
3. Account locked — show clear locked state with support contact path

**Stakeholder Priority:** Speed of task completion and confidence in error recovery.

---

### Journey: Password Reset (J-AUTH-002)
**Requirement:** REQ-UI-002
**Role:** Unauthenticated user

**Intent:** User can initiate password reset from the login screen without navigating away. Reset confirmation must arrive in email within 60 seconds. The flow must not expose whether an email address is registered (security requirement per policy-catalogue).

**Success State:** Confirmation screen shown; user knows to check email.
**Failure States:** Invalid email format — inline validation. Email not found — same success screen shown (security policy).

---

## Sample: `openspec.yaml` Excerpt (UI Requirements)

```yaml
requirements:
  - id: REQ-UI-001
    feature: authentication
    type: functional
    description: "Login form accepts email + password; submits on Enter or button click"
    acceptance_criteria:
      - "Form validates email format client-side before submission"
      - "Password field has show/hide toggle"
      - "Submit button disabled while request in flight"
      - "Error state shown inline per field on 401 response"
    nfr:
      mobile_viewport: "No scroll required on 375px width"
      latency: "Post-auth redirect < 2s p95"

  - id: REQ-UI-002
    feature: authentication
    type: functional
    description: "Password reset flow accessible from login screen"
    acceptance_criteria:
      - "Reset link visible without scrolling on login screen"
      - "Success screen shown regardless of whether email exists (security)"
      - "No navigation away from login flow required"
```
