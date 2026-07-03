# program.md — Canonical Template

> This template is used by the `program-charter` skill to generate `specs/program.md`.
> All sections are required unless marked optional.
> Do NOT include a Feature Decomposition section — features are managed via `feature-brief`.

---

```markdown
# Program Charter: {Program Name}
**Program ID:** PRG-{IDENTIFIER}
**Program Lead:** {Name}
**Created:** {Month Year}
**Status:** Active

---

## Executive Summary

{2–4 sentence summary of the program: what it does, why it matters, and what success looks like.}

**Goal:** {Single sentence statement of the primary program goal.}

**Business Impact:**
- 🎯 {KPI target 1}
- 💰 {Revenue or cost impact}
- ⏱️ {Efficiency or time target}
- 📊 {Customer or quality metric}

---

## 1. Business Foundation

### Problem Statement
{Describe the current problem, pain point, or opportunity. Include quantified evidence where available
(e.g., "Cart abandonment is 2x the industry average on mobile"). Be specific and outcome-oriented.}

### Target Users
- {Segment 1 — role, behavior, or demographic}
- {Segment 2}
- {Segment 3 — include geography or device context if relevant}

### Success Metrics (KPIs)
| Metric | Baseline | Target | Measurement Method |
|--------|----------|--------|--------------------|
| {Metric 1} | {Current value} | {Target value} | {Tool or method} |
| {Metric 2} | {Current value} | {Target value} | {Tool or method} |
| {Metric 3} | {Current value} | {Target value} | {Tool or method} |

### Scope
✅ **In Scope:** {Comma-separated list of what is included}
❌ **Out of Scope:** {Comma-separated list of explicit exclusions}

---

## 2. Architecture & Systems

### System Domains
1. **{Domain 1}** — {Brief description of responsibilities}
2. **{Domain 2}** — {Brief description}
3. **{Domain 3}** — {Brief description}

### Key Architectural Decisions
- **{Decision label}:** {Rationale and choice made}
- **{Decision label}:** {Rationale and choice made}
- **{Decision label}:** {Rationale and choice made}

### Pod / Team Structure
- **{Pod Name}** ({N} eng) — {Responsibilities}
- **{Pod Name}** ({N} eng) — {Responsibilities}

### Non-Functional Requirements (NFRs)
- **Performance:** {Target — e.g., "Page load <2s on 4G"}
- **Availability:** {SLA — e.g., "99.9% uptime during peak hours"}
- **Security:** {Standard or control — e.g., "PCI-DSS Level 1"}
- **Accessibility:** {Standard — e.g., "WCAG 2.1 AA"}
- **Scalability:** {Ceiling — e.g., "10K concurrent sessions"}

---

## 3. Design Vision

### User Journey
1. **{Step name}** → {What the user does and sees}
2. **{Step name}** → {What the user does and sees}
3. **{Step name}** → {What the user does and sees}
4. **{Step name}** → {What the user does and sees}

### Design Highlights
- {Key UX pattern or interaction}
- {Key UX pattern or interaction}
- {Key UX pattern or interaction}

### Design System Integration
- {Design token reference, component library, or "None — greenfield"}
- {Accessibility and touch target notes if applicable}

---

## 4. Risks, Timeline & Stakeholders

### Risk Register
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| {Risk description} | High/Medium/Low | High/Medium/Low | {Mitigation action} |
| {Risk description} | High/Medium/Low | High/Medium/Low | {Mitigation action} |

### Timeline
- **{Phase / Quarter}:** {Goals for this phase}
- **{Phase / Quarter}:** {Goals for this phase}
- **{Phase / Quarter}:** {Goals for this phase}

### Key Milestones
- **{Date}:** {Milestone — e.g., "Design sign-off"}
- **{Date}:** {Milestone — e.g., "Beta launch to 5% users"}
- **{Date}:** {Milestone — e.g., "Full production rollout"}

### Stakeholders
| Role | Name | Involvement |
|------|------|-------------|
| {Role} | {Name} | {What decisions or approvals they own} |
| {Role} | {Name} | {What decisions or approvals they own} |

---

## Sign-Off

| Role | Name | Date | Approved |
|------|------|------|----------|
| Program Lead | {Name} | {Date} | ☐ |
| Product VP | {Name} | {Date} | ☐ |
| Architecture Lead | {Name} | {Date} | ☐ |
| UX Lead | {Name} | {Date} | ☐ |

---

**Next Step:** Feature Leads begin `/feature-brief` sessions for each feature in scope.
```
