---
id: SAN-564
title: VideoSDK "Could not fetch token" crash joining a meeting
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-564
sentry:
  - SC-SAAS-FRONTEND-BQ
repos: [frontend]
commit: sc-saas-frontend@8ad52561 (branch ai_native_setup_vishali, not pushed)
created: 2026-09-03
updated: 2026-09-03
---

# SAN-564 — VideoSDK could-not-fetch-token crash

## Root cause
`meeting.component.ts`'s `initMeeting()` builds `config.apiKey` from `this.globalSettings?.videoSDK?.apiKey` and unconditionally calls `new VideoSDKMeeting(); meeting.init(config)`. If `apiKey` (or `meetingId`) is missing/empty — tenant videoSDK settings not configured, or global settings not yet loaded — the third-party `@videosdk.live/rtc-js-prebuilt` bundle fails deep inside its own internal token-fetch logic as an uncaught promise rejection (`_temp2` in the minified vendor bundle), entirely outside this app's try/catch reach since `init()` is synchronous and the async failure happens inside the mounted iframe's own JS context.

## Fix
Added a guard at the top of `initMeeting()`: if `apiKey` or `meetingId` is falsy, show a toast ("Unable to start the meeting — video settings are not configured for this workspace...") and return, instead of handing off to VideoSDK and letting it fail internally and unrecoverably.

## Blast radius
None — only short-circuits the already-broken case; normal meeting join (valid apiKey/meetingId) is unchanged.

## Verification
`npx tsc -p tsconfig.json --noEmit` clean. No automated test exists for this flow; verification is static/type-check only, per workspace-wide `guardian`-skill blocker.

## Related
Root cause of *why* apiKey/meetingId might be missing may involve `sc-saas-3rdparty-webservices`'s videoSDK module / `video-sdk.service.ts` (backend) — not investigated here, out of scope for this repo.
