# Sprint Board — Sprint CS-CHAT-S07

**Sprint ID:** CS-CHAT-S07  
**Sprint Dates:** 2025-09-01 → 2025-09-05  
**POD Lead:** Alex M.  
**Builders:** Builder-01 (Priya), Builder-02 (Sam)

---

## Sprint Goal

Ship customer notification preferences centre: users can manage email, SMS, and push notification opt-ins per feature category.

---

## Task Board

| Task ID | Component | Description | Assignee | Status | Spec Ref |
|---------|-----------|-------------|----------|--------|----------|
| T-041 | NotifAPI | POST /v1/notifications/preferences endpoint | Builder-01 | DONE | FR-088 |
| T-042 | NotifAPI | GET /v1/notifications/preferences endpoint | Builder-01 | DONE | FR-089 |
| T-043 | NotifDB | Schema: user_notification_preferences table | Builder-01 | DONE | FR-090 |
| T-044 | NotifDB | Migration: backfill defaults for existing users | Builder-01 | IN REVIEW | FR-090 |
| T-045 | NotifUI | Preferences page component (React) | Builder-02 | DONE | FR-091, FR-092 |
| T-046 | NotifUI | Toggle component with optimistic UI | Builder-02 | DONE | FR-093 |
| T-047 | NotifUI | Accessibility: WCAG 2.1 AA compliance | Builder-02 | DONE | FR-094 |
| T-048 | EmailSvc | Unsubscribe link integration (Mailgun webhook) | Builder-01 | DONE | FR-095 |
| T-049 | PushSvc | Firebase FCM token cleanup on opt-out | Builder-01 | DONE | FR-096 |
| T-050 | AuthGate | Middleware: enforce auth on all /notifications/* routes | Builder-02 | DONE | FR-097 |

---

## Descoped This Sprint

| Task ID | Description | Reason | Deferred To |
|---------|-------------|--------|-------------|
| T-051 | In-app notification badge count | Dependency on NotifStream service (not built) | S08 |

---

## Builder Notes

- T-044 migration reviewed by Builder-01; rollback script written and tested in staging DB snapshot.
- T-048 Mailgun webhook secret rotated; new value in staging secrets manager.
