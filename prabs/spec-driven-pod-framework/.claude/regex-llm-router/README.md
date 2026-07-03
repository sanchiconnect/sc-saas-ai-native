# RegexLLMRouter

**Deterministic-vs-LLM parse decision for customer service chatbots**

---

## What This Does

Before an agent calls an LLM to extract structured data, RegexLLMRouter
scores the parsing task on five dimensions of structural regularity and routes
it to the cheapest correct implementation: a regex/parser, a hybrid pipeline,
or a full LLM call. For the sample customer service chatbot, this eliminates
~73% of extraction LLM calls.

---

## Decision Framework (Quick Reference)

Score each dimension 1–5, then sum:

| Dimension | 5 (most regular) | 1 (least regular) |
|-----------|-----------------|-------------------|
| Schema consistency | All samples identical | Every sample different |
| Delimiter reliability | Fixed unambiguous separator | No reliable separator |
| Ambiguity level | No interpretation needed | Subjective/requires world knowledge |
| Error tolerance | Cosmetic failure OK | Wrong parse triggers irreversible action |
| Volume | 1,000+ operations/day | One-off task |

| Total | Route |
|-------|-------|
| 20–25 | Regex / deterministic parser |
| 13–19 | Hybrid (regex first, LLM for unmatched) |
| 0–12 | LLM unconditionally |

When `prefer_deterministic: true` is set in routing-config.json, ties at the
20-point boundary promote to regex.

---

## Customer Service Common Patterns

### Order ID

```python
import re

ORDER_ID = re.compile(r'ORD-\d{5}', re.IGNORECASE)

def find_order_ids(text: str) -> list[str]:
    return [m.upper() for m in ORDER_ID.findall(text)]
```

Handles multiple IDs per message. Normalize to uppercase after extraction.

### Billing Amount

```python
import re

AMOUNT = re.compile(r'\$\d{1,6}(?:\.\d{2})?')

def find_amounts(text: str) -> list[float]:
    return [float(m.lstrip('$')) for m in AMOUNT.findall(text)]
```

Known gap: does not handle thousands separators (`$1,200.00`). Strip commas
from input first if large amounts appear in your data.

### Account Status (CRM JSON)

```python
import json

def get_account_status(crm_json: str) -> str:
    data = json.loads(crm_json)
    return data['account_status']  # 'active' | 'suspended' | 'pending_cancellation' | 'closed'
```

Use `json.loads()`, not a regex. Regex on JSON breaks when key order or
whitespace changes.

### Phone Number (E.164 normalization)

```python
import re

_PHONE = re.compile(
    r'(?:\+1[\s.\-]?)?(?:\(?\d{3}\)?[\s.\-]?)\d{3}[\s.\-]?\d{4}'
)

def extract_phone_e164(text: str) -> str | None:
    m = _PHONE.search(text)
    if not m:
        return None
    digits = re.sub(r'\D', '', m.group(0))
    if len(digits) == 11 and digits.startswith('1'):
        digits = digits[1:]
    return f'+1{digits}' if len(digits) == 10 else None
```

Handles all NANP formats. Returns `None` (not a partial result) on length
mismatch.

---

## Testing Regex Patterns Before Deploying

### 1. Unit test with known inputs

Create a test file alongside your extraction module:

```python
# test_extractors.py
import pytest
from extractors import find_order_ids, extract_phone_e164

@pytest.mark.parametrize("text,expected", [
    ("order ORD-48291 is late", ["ORD-48291"]),
    ("orders ORD-10034 and ORD-10035", ["ORD-10034", "ORD-10035"]),
    ("no order here", []),
    ("ref REF-48291 is not an order", []),
])
def test_order_id_extraction(text, expected):
    assert find_order_ids(text) == expected

@pytest.mark.parametrize("text,expected", [
    ("(555) 123-4567", "+15551234567"),
    ("555-123-4567", "+15551234567"),
    ("+1 555 123 4567", "+15551234567"),
    ("5551234567", "+15551234567"),
    ("no phone here", None),
])
def test_phone_normalization(text, expected):
    assert extract_phone_e164(text) == expected
```

### 2. Run against a sample of real production logs

Before switching a task from LLM to regex in production, sample 500 recent
messages that went through the LLM path and verify the regex produces the
same output:

```python
mismatches = []
for msg, llm_result in production_sample:
    regex_result = find_order_ids(msg)
    if set(regex_result) != set(llm_result):
        mismatches.append({'msg': msg, 'regex': regex_result, 'llm': llm_result})

print(f"Mismatch rate: {len(mismatches)/len(production_sample):.1%}")
# Target: < 1% before switching
```

### 3. Monitor parse failure rate post-deployment

Log every failed parse (regex returns None/empty for a message that should
have contained a value). Alert if the 7-day rolling failure rate exceeds 2%.
This is your early warning for data drift.

```python
import logging

def find_order_ids_instrumented(text: str, expected_has_order: bool = True) -> list[str]:
    results = find_order_ids(text)
    if expected_has_order and not results:
        logging.warning("regex_parse_failure", extra={"task": "T01", "text_preview": text[:80]})
    return results
```

---

## When to Revisit Routing Decisions

### Data drift

If customers start using a new order format (e.g., `ORD-A1234` with a letter
prefix) after a system migration, the `ORD-\d{5}` pattern will silently miss
those IDs. Monitor the parse-failure alert (2% threshold) and update the
pattern within one sprint.

### Volume change

A task that was low-volume (Dimension 5 score 1–2) and accepted as LLM may
become high-volume after a product launch. Re-score when daily volume crosses
100 calls — the ROI on building a regex changes significantly.

### Business rule change

If a field that was cosmetic (score 4–5 on error tolerance) is now used in
financial workflows (score 1–2), re-evaluate even if the pattern itself is
unchanged. A field with low error tolerance should have higher confidence
before accepting a regex route.

### Hybrid fallthrough rate

Check hybrid task fallthrough rates quarterly against the thresholds in
routing-config.json:

- Fallthrough < 10% for 7 days: promote to full regex (stop calling LLM)
- Fallthrough > 60% for 7 days: demote to full LLM and re-score the task

### Quarterly scheduled review

Even without any alerts, re-run the scoring rubric on all tasks every 90 days.
Natural language patterns shift over time — a borderline task that scored 16
(hybrid) may drift toward 12 (LLM) as customers adopt more informal phrasing.

---

## File Layout

```
skills/RegexLLMRouter/
├── SKILL.md                        # Full routing framework and scoring rubric
├── README.md                       # This file
├── input/
│   ├── parsing-tasks.json          # 8 parsing tasks with sample inputs
│   └── routing-config.json         # Thresholds, cost model, volume settings
└── output/
    ├── routing-decisions.json      # Per-task decisions + economic analysis
    ├── regex-patterns.json         # Working Python patterns for regex tasks
    └── hybrid-strategy.json        # Pipeline specs for hybrid tasks
```
