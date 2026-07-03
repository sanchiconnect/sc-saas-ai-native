# SecretShield

A silent, mandatory gate that scans every context payload destined for a generation accelerator and redacts credentials, API keys, tokens, and secrets before they enter an LLM context window. Uses dual-method detection: regex pattern matching for known formats and semantic analysis for high-entropy unknown strings.

**Always active** — runs before every context payload injection into any LLM without explicit invocation.

---

## When to Use

Always active as a background gate. Explicit audit invocations:

- `scan this file for secrets`
- `run SecretShield on [file/content]`
- `check this config for credentials before injecting`
- `show me last week's SecretShield redaction log`

---

## Inputs

| Input | Required |
|---|---|
| Context payload (any format) | Mandatory |
| `references/secret-patterns.yaml` | Mandatory (internal) |

## Outputs

- Redacted context payload (secrets replaced with `[REDACTED:TYPE]` placeholders)
- `artifacts/secret-shield-log.md` — weekly redaction log for POD Lead audit

---

## Framework Position

Always runs before every context payload injection. No upstream or downstream dependency — it is a transparent gate between any agent and its LLM call.
