# Rollout Strategies — NexusDeploy
## Docker-First / Cloud-Agnostic Patterns

---

## Strategy 1: Full Cutover (Simple)
**When to use:** Internal tools, non-production-critical features, first sprint of a new service.

```yaml
rollout_strategy:
  type: "full-cutover"
  description: "Replace previous version entirely"
  pre_deploy_steps:
    - "Run database migrations"
    - "Run smoke tests against staging"
  deploy_steps:
    - "Stop existing containers"
    - "Pull new images"
    - "Start new containers"
    - "Run health checks"
  rollback_trigger: "health_check_fail_after_2min"
  rollback_steps:
    - "Stop new containers"
    - "Start previous image version"
```

---

## Strategy 2: Blue-Green (Recommended for production)
**When to use:** User-facing services where downtime is unacceptable.

```yaml
rollout_strategy:
  type: "blue-green"
  description: "Run new (green) alongside current (blue); shift traffic progressively"
  environments:
    blue: "current production"
    green: "new sprint deployment"
  traffic_shift_steps:
    - { step: 1, green_pct: 10, hold_minutes: 5, on_error: rollback }
    - { step: 2, green_pct: 50, hold_minutes: 10, on_error: rollback }
    - { step: 3, green_pct: 100, hold_minutes: 15, on_error: rollback }
  health_check:
    endpoint: "/health"
    success_criteria: "HTTP 200 + latency_p95 < nfr_threshold"
  rollback_trigger: "error_rate > 1% during hold period"
  rollback_steps:
    - "Shift 100% traffic back to blue"
    - "Stop green containers"
    - "Alert POD Lead"
```

---

## Strategy 3: Canary (For AI feature releases)
**When to use:** AI features, significant algorithmic changes, high-risk PRs.

```yaml
rollout_strategy:
  type: "canary"
  description: "Route small % of real traffic to new version before full rollout"
  canary_config:
    initial_pct: 5
    increment_pct: 15
    hold_per_increment_min: 30
    max_pct: 100
  canary_metrics:
    success_threshold:
      error_rate_max: 0.5       # %
      latency_p95_max: 800      # ms (from openspec.yaml NFR)
      quality_degradation_max: 5 # % drop from baseline
  auto_promote: false           # POD Lead must manually promote each increment
  rollback_trigger: "any metric exceeds threshold"
```

---

## Strategy 4: Feature Flag (For incremental feature delivery)
**When to use:** Features that span multiple sprints, A/B testing, gradual user rollout.

```yaml
rollout_strategy:
  type: "feature-flag"
  description: "Deploy code to production but control activation via feature flags"
  flag_system: "env-var"        # Options: env-var, launchdarkly, custom
  flags:
    - flag_name: "ENABLE_AI_INTENT_CLASSIFIER"
      default: false
      rollout_pct: 0            # Start at 0%; POD Lead enables manually
      target_users: []          # Empty = all users when pct > 0
  deployment_steps:
    - "Deploy with feature flags disabled"
    - "Verify deployment health with flags off"
    - "Enable flag for internal team (QA)"
    - "POD Lead reviews QA feedback"
    - "Enable flag at 10% → 50% → 100% per canary schedule"
```

---

## Database Migration Sequencing

Migrations must always run **before** application containers start. NexusDeploy enforces this via:

```yaml
migrations:
  pre_deploy: true
  framework: "alembic"
  command: "alembic upgrade head"
  run_in_container: "api"
  timeout_seconds: 300
  on_failure: "abort_deploy"    # Never proceed with failed migration
  
migration_safety_checks:
  - "Migration must be reversible (downgrade() implemented)"
  - "No column drops in same migration as data migration"
  - "No NOT NULL additions without default value in same migration"
  - "Long-running migrations must use concurrent index creation"
```

---

## Docker Compose Production Template

```yaml
# docker-compose.production.yaml
# Used by NexusDeploy for cloud-agnostic deployment

version: "3.9"
services:
  api:
    image: "${REGISTRY}/SpecPod-api:${SPRINT_ID}"
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      # All secrets injected from environment — never hardcoded
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      replicas: 2
      update_config:
        parallelism: 1
        delay: 10s
      rollback_config:
        parallelism: 1

  frontend:
    image: "${REGISTRY}/SpecPod-frontend:${SPRINT_ID}"
    restart: unless-stopped
    ports:
      - "3000:3000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000"]
      interval: 30s

  db:
    image: "postgres:16-alpine"
    restart: unless-stopped
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}

volumes:
  postgres_data:
```
