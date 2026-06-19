#!/bin/bash
# PreToolUse guard for the SanchiSaaS workspace.
# - DENY writes to secret/key material (.env, *.pem, *.key, credentials, db_settings.php).
# - ASK (second look) on edits to flag-definition or API-contract files, so a cross-repo
#   ripple is never made silently. Emits a reminder to run /trace-flag or /audit-contract.
# Reads the PreToolUse JSON on stdin; decides via hookSpecificOutput.permissionDecision.

input=$(cat)
file_path=$(printf '%s' "$input" | jq -r '.tool_input.file_path // .tool_input.path // empty')

# No file path (e.g. not a file tool) -> defer to normal flow.
if [ -z "$file_path" ]; then
  exit 0
fi

emit() {
  # $1 = decision (deny|ask), $2 = reason
  jq -n --arg d "$1" --arg r "$2" '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: $d,
      permissionDecisionReason: $r
    }
  }'
  exit 0
}

base=$(basename "$file_path")

# 1) Secret / key material -> DENY (cloudfront-*.pem is intentional in git but must never be (over)written here).
case "$base" in
  .env|.env.*|*.pem|*.key|id_rsa|id_rsa.*|credentials|credentials.*|db_settings.php)
    emit "deny" "Blocked write to secret/key material ($base). Never commit or modify secrets via the agent. If this is intentional infra work, do it manually outside Claude."
    ;;
esac

# 2) Flag-definition / API-contract files -> ASK (cross-repo ripple; needs a second look).
case "$file_path" in
  *sanchiconnect-saas-tenants/src/modules/tenants/entities/tenant-users.entity.ts)
    emit "ask" "This file OWNS feature-flag names. Adding/renaming/removing a column ripples to backend Feature enum, frontend IFeatures, and admin config.php. Run /trace-flag (or /flag-impact for rename/remove) before continuing." ;;
  *sanchiconnect-saas-tenants/src/modules/global/global.controller.ts|*sanchiconnect-saas-tenants/src/modules/global/global.service.ts)
    emit "ask" "This is the tenant-verification contract (verify_tenant / tenant-settings). Its shape is consumed by frontend brand.model.ts and the backend at bootstrap. Confirm both consumers before changing the response shape." ;;
  *sc-saas-backend/src/core/constants/enum.ts)
    emit "ask" "This holds the backend Feature enum (flag names). A flag here must match a tenants column and its frontend/admin consumers. Run /trace-flag before continuing." ;;
  *sc-saas-frontend/src/app/core/domain/brand.model.ts)
    emit "ask" "This declares IFeatures (the frontend flag shape) — must mirror the tenants verify_tenant response. Run /trace-flag for the flag you're touching." ;;
  *sc-saas-admin/config/config.php)
    emit "ask" "This define()s tenant flag constants and the tenancy/DB resolution. Flag names must match the cockpit. Run /trace-flag (or /check-isolation if touching DB selection)." ;;
  *sc-saas-backend/src/modules/*/*.controller.ts|*sc-saas-backend/src/modules/*/dto/*.ts)
    emit "ask" "This is part of the backend API contract (controller/DTO). A signature/shape change can break frontend core/service/* and admin cURL callers. Run /audit-contract after this change." ;;
esac

# Everything else: normal permission flow.
exit 0
