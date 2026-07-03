# spec.md — Consolidated Specification (excerpt)

> READ-ONLY oracle source for AxiomTestGen. Only the section relevant to the
> target task is shown.

## §4 Message Rate Limiting (EP-03)

The chat backend must protect downstream services by limiting how frequently a
single client may send messages.

### Acceptance Criteria — TASK-03.2 (Fixed-Window Rate Limiter)

- **AC-03.2.1** — A client MAY make up to `limit` requests within a rolling
  `window_seconds`. Every request at or below the limit returns `allowed = True`
  and a `remaining` count of how many further requests are permitted in the window.
- **AC-03.2.2** — The first request that would exceed `limit` within the window
  returns `allowed = False` and a positive `retry_after` (seconds until the window
  resets). `remaining` is `0` when throttled.
- **AC-03.2.3** — Construction with `limit < 1` or `window_seconds <= 0` is invalid
  and MUST raise an error; no limiter is created.
- **AC-03.2.4** — When the window elapses (current time advances past
  `window_start + window_seconds`), the counter resets and the next request is
  allowed again.
- **AC-03.2.5** — *(criticality: critical)* Behaviour when the supplied clock moves
  **backward** (e.g. NTP correction) is required to be safe. *[Spec note: exact
  expected behaviour TBD — pending architecture decision.]*
- **AC-03.2.6** — Distinct client keys are tracked independently; one client hitting
  its limit MUST NOT affect another client.

### Constraints
- §4.2 The limiter operates per-process and is **single-threaded**; concurrent
  access is out of scope for this task.
- Time is supplied via an injected `clock` callable (no direct wall-clock reads).

criticality: critical
