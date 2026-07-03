---
name: secret-shield
description: "SecretShield is a silent, mandatory gate that scans every context payload destined for a generation accelerator (DevCopilot, KnowledgeMesh, PromptBench, ExperienceStudio) and redacts credentials, API keys, tokens, and secrets before they enter an LLM context window. One credential leak through an LLM context window can cause a security..."
---

# SecretShield — SKILL.md
## SpecPod Build Phase · Agent B-07
**Version:** 2.1.0 | **Model:** claude-haiku-4-5-20251001 | **Token Budget:** ~15K

---

## Purpose
SecretShield is a **silent, mandatory gate** that scans every context payload destined for a generation accelerator (DevCopilot, KnowledgeMesh, PromptBench, ExperienceStudio) and redacts credentials, API keys, tokens, and secrets before they enter an LLM context window.

One credential leak through an LLM context window can cause a security incident that costs days to remediate — rotations, audit trails, potential breach notifications. SecretShield makes this impossible by default with near-zero latency overhead.

SecretShield operates on a **dual-method approach**: regex pattern matching for known credential formats, supplemented by semantic analysis for high-entropy strings that don't match known patterns.

---

## Activation Triggers
SecretShield is **always active** — it must run before **every** context payload injection into any LLM. It does not require explicit invocation.

Explicit audit invocations:
- *"scan this file for secrets"*
- *"run SecretShield on [file/content]"*
- *"check this config for credentials before injecting"*
- POD Lead weekly log review: *"show me last week's SecretShield redaction log"*

---

## Inputs

| Input | Source | Role |
|-------|--------|------|
| Context payload (any format) | Requesting agent or AI Builder | Content to be scanned before LLM injection |
| `references/secret-patterns.yaml` | SecretShield internal | Regex pattern library for known credential formats |
| Environment: multi-provider (Claude + OpenAI + others) | Configuration | Determines which provider-specific token formats to scan |

**Scope of scanning:**
- File contents passed as context (`.env`, `.yaml`, `.json`, `.py`, `.ts`, `.sql`, config files)
- Code snippets from builder sessions
- API response payloads being passed as context
- Database connection strings
- Shell command outputs
- Inline text messages containing what appears to be configuration

---

## Processing Logic

### Step 1 — Pattern Matching (Regex)
Scan for all patterns in `references/secret-patterns.yaml`:

| Pattern Category | Example Format | Redaction Placeholder |
|-----------------|---------------|----------------------|
| Anthropic API Key | `sk-ant-api[0-9]{2}-[A-Za-z0-9]{86}` | `[REDACTED:ANTHROPIC_API_KEY]` |
| OpenAI API Key | `sk-[A-Za-z0-9]{48}` or `sk-proj-[...]` | `[REDACTED:OPENAI_API_KEY]` |
| AWS Access Key | `AKIA[0-9A-Z]{16}` | `[REDACTED:AWS_ACCESS_KEY]` |
| AWS Secret Key | 40-char base64 following AKIA | `[REDACTED:AWS_SECRET_KEY]` |
| JWT Token | `eyJ[A-Za-z0-9_-]{20,}\.eyJ[A-Za-z0-9_-]{20,}` | `[REDACTED:JWT_TOKEN]` |
| PostgreSQL Connection String | `postgresql://[user]:[pass]@` | `[REDACTED:DB_CONNECTION_STRING]` |
| Generic Secret/Password | `(?i)(password\|secret\|api_key\|token\|private_key)\s*[=:]\s*["']?[^\s"']{8,}` | `[REDACTED:GENERIC_SECRET]` |
| Private Key Block | `-----BEGIN (RSA\|EC\|PRIVATE) KEY-----` | `[REDACTED:PRIVATE_KEY_BLOCK]` |
| GitHub Token | `gh[pousr]_[A-Za-z0-9]{36}` | `[REDACTED:GITHUB_TOKEN]` |
| Slack Token | `xox[baprs]-[0-9A-Za-z-]{10,}` | `[REDACTED:SLACK_TOKEN]` |
| Google API Key | `AIza[0-9A-Za-z\-_]{35}` | `[REDACTED:GOOGLE_API_KEY]` |
| Bearer Token | `(?i)bearer\s+[A-Za-z0-9\-._~+/]{20,}` | `[REDACTED:BEARER_TOKEN]` |

### Step 2 — Semantic / Entropy Analysis
For strings that don't match known patterns but exhibit high-entropy characteristics:
- Calculate Shannon entropy of candidate string
- If entropy > 3.5 bits/char AND length ≥ 20 characters AND not in whitelist: flag as `[POSSIBLE_SECRET:HIGH_ENTROPY]`
- High-entropy flags are advisory (do not block payload) but are logged and reported to POD Lead

### Step 3 — Disposition Decision
| Detection | Action |
|-----------|--------|
| High-confidence pattern match | **Redact silently** — replace value, continue payload delivery |
| High-confidence pattern match, context-critical | **Redact and alert POD Lead** — payload delivered with redaction; POD Lead informed |
| Multiple high-confidence matches in one payload | **Block payload** — do not deliver; alert POD Lead immediately |
| High-entropy string (semantic flag) | **Redact as possible secret** — log, continue delivery with placeholder |
| False positive whitelist match | **Pass through** — log as whitelisted |

### Step 4 — Logging
Every redaction event is logged to `secret-shield-redaction.log`:
```
[TIMESTAMP] [SEVERITY] [FILE_PATH_OR_CONTEXT_ID] [PATTERN_TYPE] [ACTION_TAKEN]
```
**Never log the secret value itself** — only the file path, pattern type, and character position.

---

## Elicitation Protocol
SecretShield operates silently and does not ask questions during normal operation.

If invoked explicitly for an audit scan:
1. *"Please paste or describe the content you want scanned."*
2. *"Is this content from a file? If so, what is the file path? (for logging purposes)"*
3. *"Is this a `.env` file or config file? If so, I will apply stricter scanning thresholds."*

---

## Outputs

### Sanitised Context Payload
The input payload with all detected secrets replaced by typed placeholder tokens:
```
# Original:
OPENAI_API_KEY=sk-proj-abc123...xyz789

# Sanitised:
OPENAI_API_KEY=[REDACTED:OPENAI_API_KEY]
```

### `secret-shield-redaction.log` (continuous, append-only)
```
2025-09-16T09:14:33Z | HIGH | src/config/settings.py | OPENAI_API_KEY | REDACTED
2025-09-16T09:22:11Z | MEDIUM | inline-context/task-042 | HIGH_ENTROPY_STRING | REDACTED_POSSIBLE
2025-09-16T10:05:44Z | HIGH | .env | ANTHROPIC_API_KEY | BLOCKED_PAYLOAD_ALERT_SENT
```

### POD Lead Alert (on block or multi-secret detection)
Immediate alert with:
- Context ID or file path
- Number and types of secrets detected
- Action taken (blocked/redacted)
- Recommended remediation (rotate the credential)

---

## Whitelist Management
Some strings that match secret patterns are legitimate non-secrets (e.g. test API keys in documentation, placeholder values in templates). Add to `references/secret-whitelist.yaml`:
```yaml
whitelist:
  - value_prefix: "sk-test-"
    reason: "Stripe test mode key prefix — not a real credential"
  - value_exact: "your-api-key-here"
    reason: "Placeholder template string"
  - pattern: "EXAMPLE_.*_KEY"
    reason: "Documentation placeholder pattern"
```

---

## Limitations & Escalation
- **Pattern matching produces false positives** on high-entropy strings (base64-encoded config values, UUIDs, hashed content). Weekly POD Lead log review is required to tune the whitelist and reduce noise.
- Does not scan **binary files** (images, PDFs, compiled artifacts). If a binary file is being injected as context, SecretShield cannot analyse it — DevCopilot must flag this condition.
- Does not validate whether a redacted credential is still valid (i.e., whether rotation is needed). Rotation is a human decision.

---

## Integration Points
| Agent | Direction | Data Exchanged |
|-------|-----------|----------------|
| DevCopilot | Gate (all payloads) | Every context payload passes through SecretShield before injection |
| KnowledgeMesh | Gate (all payloads) | Chunk delivery payloads scanned |
| PromptBench | Gate (prompts + samples) | Prompt and query payloads scanned |
| ExperienceStudio | Gate (UI artefacts) | Design file contents scanned |

---

## References
- `references/secret-patterns.yaml` — Full regex pattern library (all provider formats)
- `references/secret-whitelist.yaml` — Whitelisted false-positive patterns
- `references/entropy-scoring.md` — Shannon entropy calculation and thresholds
- `sample_input/sample-payload-with-secrets.txt` — Example input with embedded secrets
- `sample_output/sample-sanitised-payload.txt` — Corresponding sanitised output
