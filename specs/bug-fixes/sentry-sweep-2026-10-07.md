# Sentry sweep — 2026-10-07 (69 unresolved groups triaged; SAN-1753 … SAN-1758 filed)

- **Linear:** Production Defects (P-SAN-46), milestone M5 · **Assignee:** Aman kabra · **Org:** Sentry `sanchisaas`
- **Policy applied (user, 2026-10-07):** fix in code ⇒ Linear Done + Sentry resolved, deployment state not required; recurrence on a build containing the fix ⇒ reopen and look at the other side (infra / other call site). Noise with nothing to fix ⇒ resolved with reason.
- **Process:** 10-step loop. Step 6 (tests first) blocked workspace-wide (no `guardian` skill) — substituted `tsc --noEmit` (frontend, backend), `php -l` + a fake-PDO simulation (tenants-admin). **No automated test coverage was added.** Nothing was run against a real DB, a browser or a deployed build.

## New tickets filed
| Ticket | Sentry | Outcome |
|---|---|---|
| SAN-1753 | TENANTS-2 (`PATCH /ecosystem/startups` → GlobalExceptionFilter, 1,145 ev) | **Done — already fixed in code**: `1ef4df9` (SAN-1014, 2026-10-05) validates `x-client-domain` synchronously (400) and drops `validateCustomDecorators`. Events came from a container started 2026-10-04 (pre-fix). Inferred from `app_start_time`; no release tag. |
| SAN-1754 | BACKEND-3M (`Unknown column 'NaN'`, 188 ev) | **Done — hardening, root cause not proven.** `d254dc94` (0/0 guard + `failed_table`/`failedQuery` diagnostics) plus 9 more unguarded `Math.ceil((100*completed)/total)` sites guarded (corporate, individual, mentor, partner, service-provider, startup repos; investor ×2; program-office-member) and `calculateQuantitativeMilestonePercent` (`targetValue > 0`). Reopen if it recurs and read `failed_table`. |
| SAN-1755 | ADMIN-11 / -12 (undefined functions) | **Done — no change.** Both events `environment=local` (dev machine); `zenxaiConfig()` removed by SAN-1739 (`77437530`), `juryVisibilityRoundColumns()` is defined in `includes/jury_visibility_functions.php` and loaded by `index.php:40`. |
| SAN-1756 | FRONTEND-GJ (`countInvalidFields` → `controls` of undefined) | **Done.** `financials-details.component.ts` getter returns 0 until `financeForm` exists (template binds it before `createForm()`). |
| SAN-1757 | TENANTS-ADMIN-4 / -A / -8 (1040, 2006) | **Done.** `config/config.php` bootstrap retry on 1040 (same as SAN-1736) + `core/db.php` reconnect-once for plain SELECTs on 2006/2013. Fake-PDO simulation: 2006/2013 once ⇒ retried; twice ⇒ thrown after 1 reconnect; 1146 / INSERT / UPDATE / FOR UPDATE ⇒ thrown, no reconnect. Writes/transactions on a dead connection are NOT retried. |
| SAN-1758 | FRONTEND-7T / -GM / -ET | **Left OPEN — product decision.** See below. -7T/-ET resolved as noise. |

## Existing tickets re-checked
- **SAN-1672 / SAN-557 (FRONTEND-26, 3,840 ev / 1,747 users)**: retry `e233de1af` is in code; events are on older releases. Resolved. If it recurs on a build with `e233de1af`, the cause is the shared tenants API (timeouts/CORS/capacity), not the frontend.
- **SAN-1663 (BACKEND-4X)**: `21a495f5` in code; running task predates it. Resolved.
- **SAN-1736 (ADMIN-5)**: `c9de651c` in code. **Sentry group resolved under the new policy** — note the SAN-1736 record had deliberately left it open until capacity is addressed; the underlying cause (shared MySQL `max_connections`, SAN-140) is still an infra decision.
- **SAN-454 (BACKEND-9, S3 SignatureDoesNotMatch)**: speculative fix — `attachmentDisposition()` in `amazon-s3.service.ts` keeps the signed `ContentDisposition` header pure ASCII (ASCII fallback + RFC 5987 `filename*=`); ASCII names produce a byte-identical header. Earlier investigations (SAN-406) called this an env/region/credentials problem; if it recurs, that is the cause.
- **SAN-1024 (G5)**: fix `5732ec2db` (2026-09-28) was already in code — an earlier reopen of this ticket in this sweep was **wrong** (searched `git log --grep` by ticket ID, which that commit doesn't cite) and was retracted.
- **SAN-924 (4C)**: `3cf4994d8` (SAN-567) in code; retracted reopen. The trise 504 is infra.
- **SAN-920 (EP, ngx-ui-loader master duplicated)**: event is from release `022eafd6` (2026-07-31). Fixed a proven collision on `/hire`: `dashboard-common-calender` gets `@Input() renderLoader = true` (`*ngIf`), `hire.component.html` passes `[renderLoader]="false"`. ~95 other bare `<ngx-ui-loader>` remain — a collision needs two mounted at once and is not provable from source; bulk renaming would break modals that rely on the master loader. SAN-433 (CI guard / auto-id wrapper) was never implemented.
- **FRONTEND-2W (504 on `profile/data/<type>/<uuid>`)**: all 8 callers of `fetchDynamicFormData` lacked an error handler; each now has a no-op one (service already toasts). The supernova 504 itself is infra.
- **G9, 7W**: fixes already in code (SAN-213 `18eb14037`, SAN-576 `3791f938b`); old builds. **2F, AH**: small frontend fixes (localStorage try/catch in `program-public-apply`; removed `showLoaderOnConfirm` without `preConfirm` in `growth-matrics`).
- Resolved as noise/no-fix: FRONTEND-1 (local env), EX, F2, 7T, ET, 6E (= BACKEND-9).

## SAN-1758 — open, needs product owner / dev lead
Frontend `PitchDocumentTypes` = `fundraising-pitch | sales-pitch | hiring-pitch`; backend = `fundraising-pitch | pitch-document`. Backend removed sales/hiring **on purpose** (`d4fd191b`, May 2023: enum values, every `sales_*`/`hiring_*` column of `StartupPitchDeckEntity`, repository methods). Adding the enum values would only swap a 400 for another and let a sales delete wipe the fundraising document (route ignores type), a sales video overwrite the fundraising video, and `savePitchDocument`'s switch (fundraising only) 200 with `undefined`. **Tried and reverted** — no backend change left. Decision: (A) rebuild sales/hiring in the backend (columns + repository + switch + per-tenant migration) or (B) remove them from the frontend UI (recommended). Also observed: frontend calls routes the backend doesn't serve (`PATCH startup/pitch-deck/power-pitch` commented out; pitch-deck `supporting-documents` routes; `compile/...`).

## Still open (deliberately)
SAN-455 (BACKEND-X) and SAN-1152 (BACKEND-4F): only diagnostics in code (`fe33f96e` axios tags; `d254dc94` `failed_table`) — need a post-deploy event naming the call site/table. TENANTS-5 / -6: shared MySQL `max_connections` / refused connections (infra: `max_connections`, RDS Proxy). ~30 minor groups untouched (perf flags, handled "not found" faults, dev-tenant SES/SMTP config, stale singles).

## Contract impact
None. No controller/DTO/flag/auth change; tenant scoping untouched. (An additive backend enum change was explored for SAN-1758 and reverted.)

## Commits
sc-saas-backend, sc-saas-frontend, sanchiconnect-saas-tenants-admin, sc-saas-admin (spec line), and this record in the workspace repo — all on `ai_native_setup_aman` / `ai_native_setup` per repo convention. Not deployed.
