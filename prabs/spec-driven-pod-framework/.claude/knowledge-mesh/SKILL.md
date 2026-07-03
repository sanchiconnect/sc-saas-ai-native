---
name: knowledge-mesh
description: "KnowledgeMesh is the centralised RAG context backbone for all build-phase agents. Its core function is to prevent context divergence — the failure mode where two AI Builders, or two agents, operate from different versions of the same enterprise knowledge."
---

# KnowledgeMesh — SKILL.md
## SpecPod Build Phase · Agent B-02
**Version:** 2.1.0 | **Model:** claude-haiku-4-5-20251001 | **Token Budget:** ~60K

---

## Purpose
KnowledgeMesh is the **centralised RAG context backbone** for all build-phase agents. Its core function is to prevent context divergence — the failure mode where two AI Builders, or two agents, operate from different versions of the same enterprise knowledge.

Every other build agent (DevCopilot, ExperienceStudio, ReviewPilot, TrustFabric) retrieves context through KnowledgeMesh rather than independently reading spec files. This creates a single, versioned, deduplicated knowledge plane across the entire sprint.

---

## Activation Triggers
- Any build agent requests context retrieval: *"fetch relevant context for REQ-API-003"*
- A source document changes mid-sprint (invalidation event)
- POD Lead requests a context coverage audit: *"which spec areas have low retrieval confidence?"*
- An agent reports stale context behaviour
- Explicit invocation: *"run KnowledgeMesh"*, *"build context index"*, *"retrieve context for [task]"*

---

## Inputs

| File | Source | Role |
|------|--------|------|
| `specs/knowledge.md` | Phase 2 | As-is system knowledge: existing code patterns, integrations, runbooks |
| `specs/design.md` | Phase 2 | Technical architecture: stack, patterns, component structure |
| `specs/api.md` | Phase 2 | API contracts, endpoint specs, request/response schemas |
| `specs/database.md` | Phase 2 | Schema definitions, entity relationships, query patterns |
| `specs/features.md` | Phase 2 | Feature catalogue with scope and dependencies |
| `specs/impl.md` | Phase 2 | Implementation constraints, tech debt notes, deployment assumptions |
| `artifacts/openspec.yaml` | Phase 3 | Sprint requirements — the authoritative task set |
| `artifacts/task-breakdown.yaml` | Phase 3 | Decomposed task tree with requirement IDs |
| `artifacts/ai-manifest.json` | Prior sprint | Previously generated artifacts, component index |
| `artifacts/decision-ledger.md` | Phase 3 | Architectural decisions (ADRs) — immutable design constraints |

---

## Processing Logic

### Step 1 — Index Construction
On first invocation per sprint:
1. Parse all input files listed above
2. Chunk each document into retrieval units (target: 300–500 tokens per chunk)
3. Tag each chunk with: `source_file`, `section_heading`, `requirement_ids[]`, `sprint_id`, `version_hash`
4. Build a flat index: `chunk_id → {content, metadata}`
5. Log index summary to `knowledge-mesh-index.md`

**Chunking strategy for each file type:**
- `openspec.yaml` → one chunk per requirement block
- `api.md` → one chunk per endpoint definition
- `database.md` → one chunk per table/entity definition
- `design.md` → one chunk per architectural layer section
- `knowledge.md` → one chunk per system domain section
- `decision-ledger.md` → one chunk per ADR entry

### Step 2 — Query Handling
On each retrieval request from a downstream agent:
1. Parse the query: extract `task_id`, `requirement_id`, `domain_keywords`, `requesting_agent`
2. Score all indexed chunks by relevance to the query
3. Filter to top-N chunks (default N=5; configurable by requesting agent)
4. Check each selected chunk's `version_hash` against current source file state
5. Serve chunks with metadata; flag any chunk whose source has changed since indexing

### Step 3 — Invalidation Management
When a source document changes:
1. Identify all chunks derived from the changed file
2. Mark them as `status: STALE`
3. Log the invalidation event in `knowledge-mesh-invalidation.log`
4. If a downstream agent previously received a stale chunk: emit stale context alert

### Step 4 — Coverage Assessment
On POD Lead audit request:
- Calculate retrieval confidence per spec area: ratio of spec requirements with ≥1 high-confidence chunk
- Flag areas with confidence < 60% as "low coverage" — these indicate documentation gaps
- Output to `knowledge-coverage-report.md`

---

## Elicitation Protocol
If query is ambiguous, ask:
1. *"Which task or requirement ID is this retrieval for? (e.g. TASK-042, REQ-API-003)"*
2. *"Which domain is most relevant? (Frontend / Backend API / Database / Authentication / [other])"*
3. *"Is this for code generation (DevCopilot), design validation (ExperienceStudio), or PR review (ReviewPilot)?"*

---

## Outputs

### `knowledge-mesh-index.md` (internal, generated once per sprint)
Chunk inventory: total chunks, source distribution, requirement coverage map.

### Retrieval Response (per query, delivered to requesting agent)
```yaml
retrieval_response:
  query_id: "Q-20250916-042"
  requesting_agent: "DevCopilot"
  task_id: "TASK-042"
  requirement_id: "REQ-API-003"
  chunks:
    - chunk_id: "api.md-endpoint-POST-users"
      source: "specs/api.md"
      section: "POST /users"
      relevance_score: 0.94
      status: "CURRENT"
      content: "[chunk text]"
    - chunk_id: "database.md-users-table"
      source: "specs/database.md"
      section: "users table"
      relevance_score: 0.87
      status: "STALE"
      stale_reason: "database.md updated 2025-09-16 14:32 — users table schema changed"
      content: "[chunk text — may be outdated]"
```

### `knowledge-coverage-report.md` (on audit request)
Per-spec-area retrieval confidence scores and gap list.

### `knowledge-mesh-invalidation.log` (continuous)
Timestamped log of every invalidation event and affected agents.

---

## Limitations & Escalation
- Retrieval quality is **bounded by documentation coverage**. If `api.md` doesn't document an endpoint, KnowledgeMesh cannot retrieve context for it. Undocumented system behaviour requires direct code analysis by the AI Builder.
- Does not perform semantic understanding of retrieved chunks — relevance scoring is keyword + structural. DevCopilot is responsible for applying retrieved context to code generation logic.
- Does not persist state between conversations. Index must be rebuilt each sprint session from the spec files.

---

## Integration Points
| Agent | Direction | Data Exchanged |
|-------|-----------|----------------|
| DevCopilot | Serves | Requirement + code-pattern context per task |
| ExperienceStudio | Serves | UX spec + prior sprint feedback context |
| ReviewPilot | Serves | Acceptance criteria + convention chunks per PR |
| TrustFabric | Serves | Data contract + PII classification context |
| ContextFabric (Phase 3) | Receives | Invalidation signals when platform context changes |

---

## References
- `references/chunking-strategy.md` — Detailed chunking rules per file type
- `references/relevance-scoring.md` — Scoring algorithm and tuning parameters
- `sample_input/sample-knowledge-query.yaml` — Example retrieval request
- `sample_output/sample-retrieval-response.yaml` — Example retrieval response
