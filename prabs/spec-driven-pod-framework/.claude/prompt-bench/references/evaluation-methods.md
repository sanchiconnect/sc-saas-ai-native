# Evaluation Methods — PromptBench

## Method 1: LLM-as-Judge (Default)

Use when: No ground truth labels available; output quality is subjective or multi-dimensional.

### Judge Prompt Template
```
You are an expert evaluator for an AI feature in a [DOMAIN] application.

Evaluate the following AI response on a scale of 1–5 using this rubric:

5 — Excellent: Completely correct, relevant, and well-structured. No improvements needed.
4 — Good: Correct and relevant with minor stylistic improvements possible.
3 — Adequate: Mostly correct with one meaningful gap or imprecision.
2 — Poor: Partially correct but missing key elements or contains errors.
1 — Failing: Incorrect, irrelevant, or harmful.

User query: {query}
AI response: {response}
Expected behaviour: {expected_behaviour_description}

Score (1–5): [SCORE]
Justification (1 sentence): [JUSTIFICATION]
```

**Important:** The judge model should be **one tier above** the model being evaluated where possible. Do not use the same model to judge its own output.

---

## Method 2: Exact Match / F1 (Classification Tasks)

Use when: The output is a classification label, entity extraction, or structured JSON with known correct answers.

### Metrics
- **Accuracy** — `correct / total` (for single-label classification)
- **F1 Macro** — for multi-label or imbalanced classes
- **JSON Schema Match** — does the output conform to the expected Pydantic/Zod schema?

### Ground Truth Format
```yaml
sample_set:
  - query_id: Q-001
    input: "Schedule a meeting with John tomorrow at 3pm"
    expected_intent: "CALENDAR_CREATE"
    expected_entities:
      attendee: "John"
      time: "tomorrow 15:00"
  - query_id: Q-002
    input: "What's the weather like?"
    expected_intent: "WEATHER_QUERY"
    expected_entities: {}
```

---

## Method 3: Human-Defined Rubric (High-Stakes Features)

Use when: The feature output has significant user-facing impact (e.g. medical, financial, legal domains) and automated scoring may miss nuance.

### Rubric Design Template
Define 2–4 dimensions for the feature. Example for a customer support assistant:

| Dimension | Weight | 1 (Failing) | 3 (Adequate) | 5 (Excellent) |
|-----------|--------|-------------|--------------|---------------|
| Correctness | 40% | Wrong information | Partially correct | Fully accurate |
| Tone | 30% | Rude/dismissive | Neutral | Empathetic, professional |
| Completeness | 20% | Ignores key part of query | Addresses main point | Addresses all aspects |
| Safety | 10% | Harmful content | No issue | Proactively safe |

**Composite score** = sum of (dimension_score × weight)

---

## Sample Set Guidance

### Minimum Sample Sizes
| Feature risk level | Minimum queries | Edge case % |
|-------------------|----------------|-------------|
| Low (internal tool) | 15 | 20% |
| Medium (user-facing) | 30 | 25% |
| High (financial/compliance) | 50 | 30% |

### Query Distribution Requirements
A good sample set includes:
- **Typical cases** (50–60%): Common, well-formed inputs
- **Edge cases** (20–30%): Boundary conditions, unusual phrasing, ambiguous inputs
- **Adversarial cases** (10–20%): Prompt injection attempts, off-topic queries, malformed inputs
- **Multilingual** (if applicable): At least 10% queries in non-primary language

### Prohibited: Auto-generated samples
Do not use LLM-generated query samples to evaluate an LLM — this creates circular evaluation bias. Samples must come from: real user data (anonymised), product owner scenario definition, or UX research outputs.
