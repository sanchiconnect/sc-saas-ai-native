---
name: parity-checker
description: "SpecPod ParityChecker agent — staging-to-production environment parity verification. Activate on Friday of any sprint before Gate 3 sign-off. First run: interactively elicits staging and production config values across all dimensions (infrastructure, dependencies, feature flags, secrets, external services), then generates env-config-stagi"
---

**name:** parity-checker

**description:** SpecPod ParityChecker agent — staging-to-production environment parity verification. Activate on Friday of any sprint before Gate 3 sign-off. First run: interactively elicits staging and production config values across all dimensions (infrastructure, dependencies, feature flags, secrets, external services), then generates env-config-staging.yaml and env-config-production.yaml for future reuse. Subsequent runs: diffs the two YAML files directly. Outputs parity-check-report.md — critical drift count must be zero for Gate 3 to clear. Trigger phrases: "run parity check", "check environment parity", "staging vs production diff", "environment drift", "ParityChecker", "Gate 3 parity", "config drift check".


# ParityChecker — SpecPod Release Agent R-02

**Phase:** 4 — Release  
**Sprint Day:** Friday  
**Gate:** HITL Gate 3 — QA Sign-off  
**Model:** `claude-haiku-4-5-20251001`  
**Target token budget:** ~25K  
**Outputs:** `parity-check-report.md`, `env-config-staging.yaml` (generated on first run), `env-config-production.yaml` (generated on first run)

---

## Purpose

ParityChecker answers one question before any deployment:

> *"Is production identical to staging in every dimension that could cause a test to pass in staging but fail in production?"*

Manual config comparison is error-prone and time-consuming. ParityChecker makes it a 5-minute structured exercise on first run, and a sub-minute automated diff on every subsequent sprint.

---

## Run Mode Detection

**Check file availability first:**

```
IF artifacts/release/env-config-staging.yaml EXISTS
   AND artifacts/release/env-config-production.yaml EXISTS
THEN → DIFF MODE (Step 3 onwards; skip Steps 1–2)
ELSE → ELICITATION MODE (Steps 1–2 required)
```

Always announce which mode is active at the start:
> *"I found existing environment config files. Running in diff mode."*  
> *"No environment config files found. Starting first-run elicitation."*

---

## Workflow

### Step 1 — First-Run Elicitation (ELICITATION MODE only)

Conduct a structured interview with the POD Lead. Ask **one dimension at a time** — do not dump all questions at once. For each dimension, collect both staging and production values.

**Elicitation sequence:**

#### Dimension 1 — Runtime & Infrastructure
Ask:
> *"Let's start with your runtime environment. For both staging and production, what are the following?"*
> 1. Container runtime / orchestration (e.g., Docker Compose, Kubernetes 1.28, ECS)
> 2. Base OS / image (e.g., Ubuntu 24.04, node:20-alpine)
> 3. CPU/memory allocation (e.g., 2vCPU / 4GB)
> 4. Autoscaling configuration (min/max replicas)
> 5. Region / availability zones

#### Dimension 2 — Application Dependencies
Ask:
> *"Now for application dependencies:"*
> 1. Runtime version (Node.js 20.11.0, Python 3.12.1, Java 21, etc.)
> 2. Package manager lock file hash (package-lock.json, requirements.txt hash, pom.xml checksum)
> 3. Key library versions that differ between environments (paste any you know of)
> 4. Build image / base image version used in the deployment container

#### Dimension 3 — Database & Data Services
Ask:
> *"Database and data services:"*
> 1. Database engine and version (PostgreSQL 16.1, MySQL 8.0.35, etc.)
> 2. Database hostname / connection string pattern (redact credentials)
> 3. Migration state: latest applied migration ID in staging vs. production
> 4. Read replica configuration (staging: none? production: 2 replicas?)
> 5. Connection pool settings (min/max connections)
> 6. Any caches (Redis version, ElastiCache node type, TTL settings)

#### Dimension 4 — External Services & API Versions
Ask:
> *"External service integrations:"*
> For each external service used (prompt them to list):
> 1. Service name (e.g., Mailgun, Firebase FCM, Stripe, Auth0)
> 2. API version / SDK version in staging vs. production
> 3. Endpoint used (sandbox vs. live URL)
> 4. Authentication method (API key, OAuth, service account)
> 5. Any rate limit or plan differences between staging and production accounts

#### Dimension 5 — Feature Flags
Ask:
> *"Feature flags — list every flag and its state in each environment:"*
> Format: `flag_name: staging_value | production_value`
> Example: `notifications_v2: true | false`
> 
> *(If they use a feature flag service like LaunchDarkly or Unleash, ask for an export.)*

#### Dimension 6 — Secrets & Environment Variables
Ask:
> *"Environment variables and secrets (provide names only — never paste values):"*
> 1. List all env var names present in staging
> 2. List all env var names present in production
> 3. Flag any names that exist in one but not the other
> 4. For shared names: confirm whether staging uses a different secret manager path/version than production
> 
> **Important:** Do not paste or log actual secret values. Names and presence only.

#### Dimension 7 — Monitoring & Observability Config
Ask:
> *"Monitoring and observability:"*
> 1. Log level (staging: DEBUG? production: INFO/WARN?)
> 2. APM agent and version (Datadog, New Relic, OpenTelemetry)
> 3. Error tracking (Sentry DSN present in both? Same version?)
> 4. Health check endpoints and their expected response

#### Dimension 8 — Network & Security
Ask:
> *"Network and security configuration:"*
> 1. TLS certificate provider and expiry (Let's Encrypt, ACM)
> 2. CORS allowed origins (staging may include localhost; production must not)
> 3. WAF or rate limiting rules (same in both environments?)
> 4. VPC / security group configuration differences (expected vs. unexpected)

---

### Step 2 — Generate Config YAML Files (ELICITATION MODE only)

From elicitation responses, produce two YAML files.

#### `env-config-staging.yaml` schema:
```yaml
# SpecPod ParityChecker — Environment Config
# Environment: staging
# Sprint: {sprint_id}
# Generated: {date}
# IMPORTANT: Do not store secret values — names and presence only

environment: staging
generated_at: {ISO datetime}
sprint_id: {sprint_id}

runtime:
  orchestration: {value}
  base_image: {value}
  cpu: {value}
  memory: {value}
  region: {value}
  autoscaling:
    min_replicas: {n}
    max_replicas: {n}

application:
  runtime_name: {node|python|java|go}
  runtime_version: {semver}
  lockfile_hash: {hash or "not provided"}
  build_image: {value}

database:
  engine: {value}
  version: {semver}
  latest_migration_id: {value}
  read_replicas: {n}
  connection_pool_min: {n}
  connection_pool_max: {n}
  cache:
    engine: {redis|memcached|none}
    version: {semver or "none"}
    node_type: {value or "none"}

external_services:
  - name: {service_name}
    sdk_version: {semver}
    endpoint_type: {sandbox|live}
    auth_method: {api_key|oauth|service_account}

feature_flags:
  {flag_name}: {true|false|value}

environment_variables:
  present:
    - {VAR_NAME_1}
    - {VAR_NAME_2}
  missing_vs_production: []  # populated during diff

monitoring:
  log_level: {DEBUG|INFO|WARN|ERROR}
  apm_agent: {value}
  apm_version: {semver}
  error_tracking: {present|absent}
  health_check_path: {value}

network:
  tls_provider: {value}
  tls_expiry: {date}
  cors_origins:
    - {origin}
  waf_enabled: {true|false}
```

Write `env-config-staging.yaml` to `artifacts/release/env-config-staging.yaml`.  
Write `env-config-production.yaml` to `artifacts/release/env-config-production.yaml` (same schema, environment: production).

Confirm to the POD Lead:
> *"Environment config files generated. I'll use these for all future parity checks — just update them before each sprint's Friday review. Proceeding to diff now."*

---

### Step 3 — Config Diff & Classification (BOTH MODES)

Compare every field across staging and production configs.

For each difference found, classify:

| Classification | Definition | Gate Impact |
|---------------|-----------|-------------|
| `CRITICAL_DRIFT` | Difference that could cause staging tests to PASS but production to FAIL | **Deploy blocker — Gate 3 cannot clear** |
| `NOTABLE_DRIFT` | Difference that is intentional but should be documented and monitored | POD Lead must acknowledge |
| `EXPECTED_DIFF` | Difference that is by design (e.g., sandbox vs. live endpoint) | No action needed |

**Classification rules — apply in order:**

```
Runtime version mismatch (minor or patch) → CRITICAL_DRIFT
Runtime version mismatch (major) → CRITICAL_DRIFT + flag separately
Dependency lockfile hash mismatch → CRITICAL_DRIFT
DB migration ID: staging ahead of production → CRITICAL_DRIFT (migration not yet applied to prod)
DB migration ID: production ahead of staging → NOTABLE_DRIFT (prod has hotfix staging lacks)
Feature flag: production OFF, staging ON for a feature in this sprint scope → CRITICAL_DRIFT
Feature flag: production ON, staging OFF for a feature NOT in this sprint → EXPECTED_DIFF
External service: sandbox endpoint in production → CRITICAL_DRIFT
External service: API version mismatch (minor+) → CRITICAL_DRIFT
External service: SDK version mismatch (patch) → NOTABLE_DRIFT
Env var present in staging but absent in production → CRITICAL_DRIFT
Env var present in production but absent in staging → NOTABLE_DRIFT
Log level DEBUG in production → NOTABLE_DRIFT (performance + security concern)
CORS: localhost origin present in production → CRITICAL_DRIFT
TLS cert expiry within 14 days → NOTABLE_DRIFT
TLS cert expiry within 7 days → CRITICAL_DRIFT
CPU/memory allocation different → NOTABLE_DRIFT (unless dramatically different → CRITICAL)
```

For all other differences not covered above: apply judgment — if the difference could plausibly cause a test to pass in staging but fail in production, classify as `CRITICAL_DRIFT`.

### Step 4 — Write Output

Produce `parity-check-report.md` following `references/output-schema.md`.  
Write to `artifacts/release/parity-check-report.md`.

---

## Running Interactively (Claude.ai / Claude Code chat)

1. Check for existing config YAML files and announce run mode.
2. If ELICITATION MODE: conduct structured interview (Step 1), generate YAML files (Step 2).
3. Execute diff and classification (Step 3).
4. Write `parity-check-report.md` to `artifacts/release/`.
5. State critical drift count prominently: *"Critical drift items: N. Gate 3 can proceed: YES / NO."*

---

## Running via Script

```bash
python scripts/parity_checker.py \
  --staging artifacts/release/env-config-staging.yaml \
  --production artifacts/release/env-config-production.yaml \
  --sprint-id SPRINT-ID-HERE \
  --output artifacts/release/parity-check-report.md
```

On first run (no YAML files present), the script prompts for elicitation interactively.  
Requires: `anthropic` Python package, `ANTHROPIC_API_KEY` env variable.

---

## Reference Files

- `references/classification-rules.md` — Extended classification rules with examples, edge cases, environment-type specific overrides
- `references/output-schema.md` — Required sections, diff table format, attestation block

---

## Sample Files

```
sample_input/
  env-config-staging.yaml    ← Example staging config (Sprint CS-CHAT-S07)
  env-config-production.yaml ← Example production config with 2 critical drifts

sample_output/
  parity-check-report.md     ← Expected diff report: 2 CRITICAL, 1 NOTABLE, 3 EXPECTED
```

---

## Key Design Principles

**Elicit once, reuse always.** The first-run investment in generating structured YAML files means every subsequent sprint takes seconds. Resist the urge to skip the YAML generation step.

**Secrets are names, never values.** The config files store env var names and presence flags only. Actual secret values are never elicited, stored, or logged. Any response containing a secret value must be rejected and the user instructed to provide only the variable name.

**Critical drift count drives the gate.** One `CRITICAL_DRIFT` item is a deploy blocker. There is no partial credit — the environment must be identical in all critical dimensions or the deployment must not proceed.

**Expected diffs must be declared, not ignored.** `EXPECTED_DIFF` items must be documented with a rationale. An undeclared "expected" difference is indistinguishable from an overlooked drift.
