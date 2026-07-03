# Data Contract Schema — TrustFabric

## File Location
All data contracts live in `data-contracts/[entity_name].yaml`
One file per data entity (database table or external data source).

---

## Schema Definition

```yaml
# data-contracts/[entity_name].yaml

entity: string                    # Matches database table name or external source name
version: semver                   # Contract version (update on any field change)
owner: string                     # Team or role responsible for this data entity
last_reviewed: date               # ISO 8601 date of last compliance review
retention_period: string          # e.g. "7 years", "90 days", "indefinite"

fields:
  - name: string                  # Exact column/field name
    pii_class: enum               # See PII Classification Taxonomy
    description: string           # Human-readable field purpose
    encryption_required: boolean  # Must be encrypted at rest
    allowed_roles: list[string]   # Roles permitted to read this field
    masking_rule: string|null     # How to mask in responses (null = no masking required)
    logging_permitted: boolean    # May appear in application logs
    purpose_limitation: string    # Allowed use cases (data minimisation)

access_rules:
  - role: string
    operations: list[enum]        # read | write | delete | export
    conditions: string|null       # e.g. "own record only", "admin context only"
```

---

## Example: `data-contracts/users.yaml`

```yaml
entity: users
version: "1.2.0"
owner: platform-team
last_reviewed: "2025-08-01"
retention_period: "3 years post account deletion"

fields:
  - name: id
    pii_class: NON-PII
    description: "Internal UUID primary key"
    encryption_required: false
    allowed_roles: [authenticated_user, admin, system_service]
    masking_rule: null
    logging_permitted: true
    purpose_limitation: "Any internal use"

  - name: email
    pii_class: PII:CONTACT
    description: "User's primary email address"
    encryption_required: false
    allowed_roles: [admin, system_service]
    masking_rule: "Mask domain: show [user]@[***] for authenticated_user role"
    logging_permitted: false
    purpose_limitation: "Authentication, transactional emails only"

  - name: password_hash
    pii_class: PII:IDENTITY
    description: "bcrypt password hash"
    encryption_required: true
    allowed_roles: [system_service]
    masking_rule: "NEVER return in any API response"
    logging_permitted: false
    purpose_limitation: "Authentication only — never read externally"

  - name: date_of_birth
    pii_class: PII:IDENTITY
    description: "User's date of birth for age verification"
    encryption_required: true
    allowed_roles: [admin]
    masking_rule: "Return [REDACTED] for all non-admin roles"
    logging_permitted: false
    purpose_limitation: "Age verification, legal compliance only"

  - name: created_at
    pii_class: NON-PII
    description: "Account creation timestamp"
    encryption_required: false
    allowed_roles: [authenticated_user, admin, system_service]
    masking_rule: null
    logging_permitted: true
    purpose_limitation: "Any internal use"

access_rules:
  - role: authenticated_user
    operations: [read]
    conditions: "own record only"
  - role: admin
    operations: [read, write]
    conditions: null
  - role: system_service
    operations: [read, write, delete]
    conditions: "automated processes only"
```

---

## Registering a New Field
When TrustFabric encounters an unclassified field, the POD Lead must add it to the relevant `data-contracts/[entity].yaml` file using this process:
1. Determine the field's PII class (use `references/pii-taxonomy.md`)
2. Define `masking_rule`, `logging_permitted`, `purpose_limitation`
3. Increment the contract `version` (patch for new field, minor for policy change)
4. Update `last_reviewed` date
5. Re-run TrustFabric after update to clear the unclassified flag
