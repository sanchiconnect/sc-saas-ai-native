---
id: SAN-1737                    # set: SAN-1737 tenants, SAN-1738 backend, SAN-1739 admin, SAN-1740 tenants-admin
title: SanchiConnect AI Voice Agent — provider-agnostic revamp (from ZenxAI)
type: feature
status: in-review
linear: https://linear.app/sanchiconnect/project/sanchiconnect-ai-voice-agent-provider-agnostic-revamp-from-zenxai-7f44f9081709
owner: nirmal.s@sanchiconnect.com
repos: [tenants, backend, admin, sanchiconnect-saas-tenants-admin]
contracts:
  flags:
    - "NEW ai_voice_agent_enabled (tenant_users, nullable boolean; NULL = inherit zenxai_crm_enabled). Consumer: sc-saas-admin config.php. zenxai_crm_enabled DEPRECATED (kept, never written)."
  api: []
  events: []
  schema:
    - "tenant_users: + voice_agent_provider, voice_agent_assistant_id, voice_agent_input_fields (nullable)"
    - "per-tenant DB: + voice_agent_calls (supersedes zenxai_calls, which is kept untouched)"
    - "ai_credit_ledger.source_ref for voice calls: 'voice_agent:<id>' (new) or 'zenxai:<legacy id>' (migrated)"
tenant_scoped: true
depends_on: [SAN-1028, SAN-1136]
created: 2026-10-06
---

# SanchiConnect AI Voice Agent: provider-agnostic revamp

## Problem
The draft-applicant voice-call module was hard-wired to ZenxAI:
- the HTTP calls, the env names, the table and the flag all named ZenxAI;
- one shared assistant was used for every tenant;
- "ZenxAI" was visible to tenant admins.

The product owner wants the module to work like the AI analyzer's provider abstraction, so another voice agent or CRM can be added later. Tenants can also ask for their own custom assistant.

## Decisions (product owner, 2026-10-06)
- **DB names:** use new generic names and migrate. Old names are left in place and stop being used. Nothing is dropped, because synchronize:true would destroy the data.
- **Per-tenant assistant:** the provider, assistant ID and Call Data keys live on the tenant row. Sanchi operators set them in tenants-admin. Empty means the platform default from env, and API keys stay in env only.
- **UI name:** "SanchiConnect AI Voice Agent". Tenant admins never see the vendor name; developers get a small hint.
- **Owner:** Nirmal Singh.

## Design
### tenants (SAN-1737)
- **New columns on `tenant_users`:**
  - `ai_voice_agent_enabled` (boolean, **nullable**)
  - `voice_agent_provider` (32)
  - `voice_agent_assistant_id` (128)
  - `voice_agent_input_fields` (500)
- **Seed on boot:** `TenantsService.onApplicationBootstrap` copies `zenxai_crm_enabled` into `ai_voice_agent_enabled` where it is NULL. This is idempotent, never overrides an operator's value, and is fail-soft.
- **Old flag:** `zenxai_crm_enabled` is marked deprecated and kept.
- **Not in the public contract:** these fields are not added to verify_tenant / tenant-settings, because sc-saas-admin reads the row directly.

### backend (SAN-1738)
- **New entity `voice_agent_calls`** (`src/core/voice-agent/`): the same shape as `zenxai_calls`, with these changes:
  - `zenx_created_at` / `zenx_ended_at` are renamed to `provider_created_at` / `provider_ended_at`;
  - new `provider` (default `zenxai`) and `assistant_id`;
  - new `credit_source_ref` (unique, nullable): the ledger ref of a migrated row;
  - new `legacy_call_row_id` (unique, nullable): the migration idempotency key.
- **Legacy entity:** `ZenxaiCallsEntity` stays registered so synchronize never touches `zenxai_calls`.

### admin (SAN-1739)
- **`includes/voice_agent/VoiceAgentProvider.php`:** the contract. It returns normalized result kinds (`ok | fatal | rate_limited | transient | rejected | not_cancellable | error`) plus mapped columns. Everything vendor-specific lives behind it: HTTP, auth, endpoints, status and error mapping. Its messages never name the vendor.
- **`includes/voice_agent/providers/ZenxaiVoiceProvider.php`:** the ZenxAI behaviour, moved unchanged.
- **Env model (the same as the AI analyzer, added 2026-10-06 at the product owner's request):**
  - `VOICE_AGENT_DEFAULT_PROVIDER`, plus one generic slot: `VOICE_AGENT_API_KEY`, `VOICE_AGENT_BASE_URL`,
    `VOICE_AGENT_ASSISTANT_ID`, `VOICE_AGENT_INPUT_FIELDS` and `VOICE_AGENT_RESERVE_MINUTES`.
  - `voiceAgentEnv($code, $name)` uses the generic slot only for the default provider. Any other
    provider reads its own `<CODE>_<NAME>` keys, so the generic key is never sent to the wrong vendor.
  - The legacy `ZENXAI_*` keys therefore keep working as fallbacks.
  - Plain `DEFAULT_PROVIDER` / `CLOUD_API_KEY` are deliberately not reused, because they belong to video
    transcription (Gemini).
- **`includes/voice_agent_functions.php`** (formerly `zenxai_functions.php`): the generic core.
  - Registry `voiceAgentProviderClasses()`. `VOICE_AGENT_DEFAULT_PROVIDER` is optional and defaults to `zenxai`.
  - `voiceAgentProvider($tenantRow)` uses the tenant settings and falls back to the defaults.
  - `voiceAgentProviderForRow($row)`: refresh, cancel and resume always use the row's own provider and assistant, so switching provider never strands older calls.
  - Claim/idempotency, eligibility, Call Data, billing and the reconcile are unchanged.
  - `VOICE_AGENT_RESERVE_MINUTES` falls back to `ZENXAI_RESERVE_MINUTES`.
- **Migration:** `voiceAgentReady($database)` copies `zenxai_calls` into `voice_agent_calls` once per tenant, on first use.
  - It runs before any key is computed and is idempotent through `legacy_call_row_id`.
  - Migrated rows keep their timestamps and their existing ledger ref (`credit_source_ref = 'zenxai:<id>'`); new rows use `voice_agent:<id>`. `voiceAgentCreditSourceRef($row)` resolves either one.
- **Ledger:** `reconcileStaleAiCreditReservations()` skips both voice prefixes, and the ledger display labels both.
- **Page:**
  - The route is now `application_management/voice_agent/{id}/{slug}`. `zenxai_dashboard.php` is a stub: a 301 for GET, and a JSON "reload" message for POSTs from stale tabs.
  - AJAX actions are renamed `voiceAgent*`; JS and CSS identifiers `va*`.
  - The Draft Applications button reads "SanchiConnect AI Voice Agent".
  - The flag constant `ai_voice_agent_enabled` falls back to `zenxai_crm_enabled` on NULL.

### tenants-admin (SAN-1740)
- **Switch:** `ai_voice_agent_enabled` replaces `zenxai_crm_enabled` in the switch list. A NULL value displays the inherited value.
- **Edit page:** a new "SanchiConnect AI Voice Agent" card for the provider, assistant ID and Call Data fields, validated by `_voice_agent_settings.php`. Detail shows the same fields read-only.
- **Revenue & Cost:** the note now says "AI Voice Agent call cost".

## Adding a provider later
1. Add `includes/voice_agent/providers/<Vendor>VoiceProvider.php` implementing `VoiceAgentProvider`. Map its statuses onto the canonical set and read its keys from env.
2. Add one line to `voiceAgentProviderClasses()` (admin) and to `voiceAgentProviderOptions()` (tenants-admin).
3. Set it per tenant in tenants-admin, or platform-wide with `VOICE_AGENT_DEFAULT_PROVIDER`.

## Verification (2026-10-06, throwaway MySQL 9.6 + local ZenxAI mock; no real calls)
- **Old vs new:** the old code (git HEAD) and the new provider code ran the same 7 scenarios side by side: queued → completed → settled, 429, 500, 400 invalid_phone, 402, cancel, and an invalid local phone.
  - Identical: billing context, wallet, every ledger row, every call row, and all 8 provider requests (same paths, idempotency keys and bodies).
  - Only two messages changed, by design, because they named ZenxAI.
- **Migration:**
  - 3 legacy rows were copied with timestamps, deleted state and refs intact; a second run copied nothing, and `zenxai_calls` was untouched.
  - An old in-flight reservation was settled through its original `zenxai:12` ref.
  - New keys continue the old numbering (`-2`), and the stale sweep skips both prefixes.
  - The copy was also run against tables created by the **real backend entities**.
- **Per-tenant override:**
  - The tenant's assistant was used in the request path, unknown Call Data keys were dropped, and the row records its assistant.
  - Unknown provider or missing key: the feature is disabled and developers see the reason.
- **Real controller and template:**
  - Rendered the dev, admin and unconfigured views. There were no warnings, and normal admins see no "ZenxAI" anywhere.
  - The AJAX count, batch and refresh actions work.
- **tenants:** the real entity was synced to a throwaway DB. The seed copied the old flag into NULL rows, left an operator's value alone, and was idempotent.
- **tenants-admin:** the settings validator accepts empty and good input, and rejects bad provider, assistant and keys with escaped messages.
- **Not done:** a live call against ZenxAI, and a browser check of the rendered page.

## Rollout
1. **tenants** first: the columns are added and the flag is seeded on boot.
2. **backend**: `voice_agent_calls` is created.
3. **admin**: the legacy rows are copied on the first page load per tenant.
4. **tenants-admin**.

Admin must not deploy before backend: until `voice_agent_calls` exists, the feature is hidden (developers see the reason) and no calls can be placed.

The env needs no change: the existing `ZENXAI_*` keys keep working. The recommended generic keys are
`VOICE_AGENT_DEFAULT_PROVIDER`, `VOICE_AGENT_API_KEY`, `VOICE_AGENT_BASE_URL`, `VOICE_AGENT_ASSISTANT_ID`,
`VOICE_AGENT_INPUT_FIELDS` and `VOICE_AGENT_RESERVE_MINUTES`.

## Out of scope
- A second real provider; this work only adds the slot for one.
- Per-tenant API keys.
- Dropping `zenxai_calls` and `zenxai_crm_enabled`. That is a later cleanup, after every tenant's rows have been verified as migrated.
