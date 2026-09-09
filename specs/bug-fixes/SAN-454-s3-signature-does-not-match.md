---
id: SAN-454
title: AWS S3 SignatureDoesNotMatch — production credentials/infra issue (45 events)
type: bug-fix
status: in-progress
linear: https://linear.app/sanchiconnect/issue/SAN-454
sentry:
  - SC-SAAS-BACKEND-9
repos: [backend]
commit: n/a — infrastructure fix required, no code change
created: 2026-08-20
updated: 2026-08-21
---

# SAN-454 — S3 SignatureDoesNotMatch (production infra)

## Root cause
`app.module.ts:89-102` configures the S3 client correctly (`signatureVersion: 'v4'`, `s3ForcePathStyle: true`, custom MinIO endpoint). The `SignatureDoesNotMatch` error is a production infrastructure/credentials issue, not a code bug.

## Action required (Aman)
1. Verify `AMAZON_ACCESS_KEY_ID` and `AMAZON_SECRET_ACCESS_KEY` in the production ECS task definition match the actual MinIO storage credentials — key may have been rotated.
2. Check NTP sync on the ECS instance (`ip-10-0-21-185.ap-south-1.compute.internal`) — SigV4 rejects requests where the timestamp differs >5 min from the server clock.
3. Confirm `AMAZON_S3_ENDPOINT` points to the correct storage instance and the credentials belong to that instance.

## Blast radius
None until infra fix — current uploads are failing.

## Verification
Once credentials are corrected in production, SC-SAAS-BACKEND-9 will stop automatically.
