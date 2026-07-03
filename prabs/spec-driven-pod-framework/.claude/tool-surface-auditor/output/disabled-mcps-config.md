# Disabled MCPs Config — customer-service-chatbot-production
# Generated: 2026-06-03T08:15:00Z
# Audit version: 1.0.0
#
# INSTRUCTIONS
# ------------
# 1. Review every section marked REVIEW_REQUIRED before applying.
# 2. Apply the confirmed-disable section first and verify in staging.
# 3. Apply the human-review section only after team sign-off.
# 4. Re-run the ToolSurfaceAuditor audit after applying to confirm token counts.
#
# Projected tokens reclaimed (confirmed disables): 34,200
# Projected tokens reclaimed (if all reviews approved): 35,747
# Window recovered: 17.1% of a 200K-token context window


## ────────────────────────────────────────────────────────────────────────────
## SECTION 1: CONFIRMED DISABLES (safe to apply after staging verification)
## ────────────────────────────────────────────────────────────────────────────

### Environment variable format

```sh
# Entire servers to disable
ECC_DISABLED_MCPS=developer_tools_server,legacy_crm_server,testing_server

# Individual tools to disable within partially-kept servers
ECC_DISABLED_TOOLS=analytics_server.generate_weekly_report,analytics_server.generate_monthly_report,analytics_server.export_to_data_warehouse,analytics_server.get_agent_scorecard,analytics_server.get_topic_distribution,analytics_server.get_channel_mix,analytics_server.get_handle_time_histogram,analytics_server.run_cohort_analysis,analytics_server.get_sentiment_trend,analytics_server.trigger_ad_hoc_query,legacy_crm_server.legacy_lookup_customer,legacy_crm_server.legacy_sync_to_salesforce
```

### JSON config format (.mcp/config.json or equivalent)

```json
{
  "disabled_servers": [
    "developer_tools_server",
    "legacy_crm_server",
    "testing_server"
  ],
  "disabled_tools": [
    "analytics_server.generate_weekly_report",
    "analytics_server.generate_monthly_report",
    "analytics_server.export_to_data_warehouse",
    "analytics_server.get_agent_scorecard",
    "analytics_server.get_topic_distribution",
    "analytics_server.get_channel_mix",
    "analytics_server.get_handle_time_histogram",
    "analytics_server.run_cohort_analysis",
    "analytics_server.get_sentiment_trend",
    "analytics_server.trigger_ad_hoc_query",
    "legacy_crm_server.legacy_lookup_customer",
    "legacy_crm_server.legacy_sync_to_salesforce"
  ]
}
```

### Rationale for confirmed disables

| Server / Tool                             | Reason                                                                 | Tokens |
|-------------------------------------------|------------------------------------------------------------------------|--------|
| developer_tools_server (entire, 15 tools) | Debug tools accidentally left in production. Zero calls. Non-production intent confirmed by server description. | 1,513 |
| testing_server (entire, 5 tools)          | CI/CD tools accidentally left enabled. wipe_test_database is a critical destructive risk in production. | 518    |
| legacy_crm_server (entire, 8 tools)       | Superseded by crm_server. The 3 calls observed had 50–100% error rates. | 846    |
| analytics_server.generate_weekly_report   | Zero calls. Reporting likely handled out-of-band.                      | 122    |
| analytics_server.generate_monthly_report  | Zero calls.                                                            | 124    |
| analytics_server.export_to_data_warehouse | Zero calls. ETL pipeline handles Snowflake sync.                       | 126    |
| analytics_server.get_agent_scorecard      | Zero calls.                                                            | 110    |
| analytics_server.get_topic_distribution   | Zero calls.                                                            | 113    |
| analytics_server.get_channel_mix          | Zero calls.                                                            | 109    |
| analytics_server.get_handle_time_histogram| Zero calls.                                                            | 115    |
| analytics_server.run_cohort_analysis      | Zero calls.                                                            | 132    |
| analytics_server.get_sentiment_trend      | Zero calls.                                                            | 120    |
| analytics_server.trigger_ad_hoc_query     | Zero calls. Direct SQL access is a security concern if unused.         | 126    |
| **Total confirmed tokens reclaimed**      |                                                                        | **34,200** |


## ────────────────────────────────────────────────────────────────────────────
## SECTION 2: HUMAN REVIEW REQUIRED (DO NOT APPLY without team sign-off)
## ────────────────────────────────────────────────────────────────────────────
#
# These tools have error_rate = 0.0 AND calls_30d = 0.
# Per the ToolSurfaceAuditor safety rule, zero errors on zero calls is ambiguous.
# A tool may be emergency-only and simply not needed during the 30-day window.
# Each item below has a recommended decision and risk level.
# A human must confirm before adding these to the active disable list.

### Environment variable format (COMMENTED OUT — pending review)

```sh
# REVIEW: social_media_server — deployment note confirms not used in this deployment
# Confirm with team that no future roadmap item depends on this server.
# ECC_DISABLED_MCPS_REVIEW=social_media_server

# REVIEW: notification_server.broadcast_announcement — zero calls, possible bulk/incident use
# Disable if marketing platform handles announcements outside this agent.
# ECC_DISABLED_TOOLS_REVIEW=notification_server.broadcast_announcement

# REVIEW: document_server.merge_pdfs — zero calls, possible low-frequency utility
# ECC_DISABLED_TOOLS_REVIEW=document_server.merge_pdfs

# REVIEW: document_server.watermark_document — zero calls, confirm with compliance team
# ECC_DISABLED_TOOLS_REVIEW=document_server.watermark_document

# REVIEW: document_server.delete_document — destructive, zero calls, confirm retention policy
# ECC_DISABLED_TOOLS_REVIEW=document_server.delete_document
```

### JSON config format (pending review)

```json
{
  "_comment": "PENDING HUMAN REVIEW — do not apply until sign-off obtained",
  "disabled_servers_review": [
    "social_media_server"
  ],
  "disabled_tools_review": [
    "notification_server.broadcast_announcement",
    "document_server.merge_pdfs",
    "document_server.watermark_document",
    "document_server.delete_document"
  ]
}
```

### Review checklist

- [ ] **social_media_server** — Confirm with product team: is Twitter/X or LinkedIn publishing
  in scope for any customer service workflow in the next 90 days?
  If NO: add to `ECC_DISABLED_MCPS` and apply.
  If YES: keep and re-evaluate after roadmap milestone.

- [ ] **notification_server.broadcast_announcement** — Confirm with ops team: does this agent
  ever need to push bulk announcements during incidents?
  If NO: add to `ECC_DISABLED_TOOLS` and apply.
  If YES: retain and consider adding a `calls_floor` exception in the config.

- [ ] **document_server.merge_pdfs** — Is PDF merging handled by an external document platform?
  If YES: disable.
  If UNSURE: retain for one additional 30-day audit window.

- [ ] **document_server.watermark_document** — Does compliance require watermarking capability
  for any regulatory document workflow?
  If NO: disable.
  If YES: retain and document the use case.

- [ ] **document_server.delete_document** — Are document deletions handled by a scheduled
  retention policy, or does the agent ever need to delete on-demand?
  If policy-driven only: disable.
  If on-demand deletion is a supported workflow: retain.

### Potential additional tokens reclaimed if all reviews approve

| Tool / Server                              | Tokens |
|--------------------------------------------|--------|
| social_media_server (5 tools)              | 554    |
| notification_server.broadcast_announcement | 118    |
| document_server.merge_pdfs                 | 94     |
| document_server.watermark_document         | 106    |
| document_server.delete_document            | 90     |
| **Total additional potential savings**     | **962** |
| **Combined total if all approved**         | **35,162** |


## ────────────────────────────────────────────────────────────────────────────
## SECTION 3: FUTURE CONSOLIDATION RECOMMENDATIONS (not an immediate disable)
## ────────────────────────────────────────────────────────────────────────────
#
# These are structural recommendations that require migration work, not just
# config changes. Discuss with the platform team before acting.

# CONSOLIDATION: notification_server + email_server
# Both servers handle customer communication delivery. Consider merging into a
# single comms_server with unified routing logic. Estimated additional savings
# from removing duplicate tool descriptions: ~200 tokens.
#
# CONSOLIDATION: analytics_server (post-cleanup)
# After disabling 10 tools, analytics_server has only 2 remaining tools
# (get_csat_score, get_resolution_rate). Consider folding these into
# database_server or a lightweight metrics stub server.
# Estimated savings from eliminating server-level overhead: ~50 tokens.
