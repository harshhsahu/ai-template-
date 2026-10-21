---
verified_at: {{HEAD_SHORT}}
verified_on: {{TODAY}}
---
# Architectural & Design Decisions (ADRs)

<!-- fill: Record significant architectural, technical, and UX decisions made in this repository.
     Future agents must consult these decisions so they do not repeat failed approaches or undo intentional choices. -->

## Decision Index

| Date | Decision Record | Status | Area Affected | Key Rationale |
|---|---|---|---|---|
| {{YYYY-MM-DD}} | [ADR-001: {{Title}}](#adr-001-{{slug}}) | Accepted | Routing / State / UI | {{1-line why}} |

---

## ADR-001: {{Decision Title: e.g. Adopt TanStack Query for Remote State Management}}

### Status
Accepted <!-- Accepted | Deprecated | Superseded by ADR-xxx -->

### Context & Problem Statement
<!-- fill: What problem were we solving? What pain point or architectural challenge occurred? -->
{{Description of context, e.g. "Direct useEffect fetching led to race conditions, duplicated network requests, and complex loading spinners scattered across views."}}

### Decision & Implementation
<!-- fill: What did we decide to do? Which library, pattern, or constraint was chosen? -->
{{We decided to adopt TanStack Query (`@tanstack/react-query`) as the single source of truth for all server-fetched data. All API calls are wrapped in custom hooks under `src/services/`.}}

### Supporting Evidence & Past Incidents
<!-- fill: Reference git commits, PRs, benchmarks, or incidents that drove this decision. -->
- Commit `{{sha}}`: "{{Commit message}}"
- PR #{{123}}: Refactored data fetching and reduced duplicate requests by 65%.

### Consequences & Trade-offs
- **Positive:** Automatic request deduplication, background revalidation, built-in loading and error states.
- **Negative / Constraints:** Developers must not store server payloads in local Zustand stores; cache keys must be strictly namespaced.

### Superseded / Rejected Alternatives
<!-- fill: What alternatives were tried or considered, and WHY were they rejected? -->
1. **Redux Toolkit:** Rejected because boilerplate overhead was excessive for our REST data fetching needs.
2. **Ad-hoc React Context:** Rejected because it lacked automatic caching, garbage collection, and stale-while-revalidate capabilities.

---

## Lessons Learned & Incident Log

<!-- fill: Record notable bug patterns, production issues, or regressions, and how to avoid them in the future. -->
- **Incident / Bug:** {{Description of issue}}
  - **Root Cause:** {{What caused it}}
  - **Prevention Rule:** {{Rule added to AGENTS.md or code linter}}
