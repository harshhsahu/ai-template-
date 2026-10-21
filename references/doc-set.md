# The Canonical AI-Ready Doc Set

This doc set is designed for 100% AI-driven development. It equips any capable AI coding agent to enter the repository, understand the product's purpose and architecture, evaluate incoming requests intelligently, make reliable changes, perform safe refactorings, and maintain project knowledge without needing humans to repeatedly explain the system.

Combine small documents when that improves clarity; avoid duplicate sources of truth. Use additional documents only when they solve a genuine navigation or knowledge problem (e.g. scoped instructions for distinct apps in a monorepo).

## The Canonical Suite

| Document | Primary Purpose & Scope | When to Write | Main Inputs |
|---|---|---|---|
| `AGENTS.md` (root) | Concise starting point (<150 lines): project scope, essential boundaries, commands, reading order, 10–15 numbered project rules, PR & deployment pipeline (`testing -> stag -> main`), and verification expectations. | Always (Root Entry) | Summary of all docs below |
| `docs/VISION.md` | Product purpose, ICP, customer problems, value proposition, principles, priorities, success measures, non-goals, future direction, and request evaluation protocol. | Always | README, PRDs, founder notes, package.json, user Q&A |
| `docs/ARCHITECTURE.md` | System mental model: major modules, responsibilities, entry points, dependencies, state ownership, sources of truth, rendering strategy, and compact Mermaid data-flow diagram. | Always | Entry points, router configs, state stores, services |
| `docs/FLOWS.md` | Important user journeys: happy paths, alternative branches, permissions, failures, and recovery. Connects user actions to routes, components, state changes, and APIs. | Always (Core user flows) | Page views, event handlers, router configs, API calls |
| `docs/DESIGN.md` | Visual & interaction principles, reusable component catalog, design tokens, responsive breakpoints, accessibility (a11y), website messaging, and SEO expectations. | Always (Frontend projects) | Theme configs, CSS tokens, shared components, metadata |
| `docs/CONTRACTS.md` | Authoritative API schemas, TypeScript types, data relationships, auth assumptions, error handling, analytics events, persistence contracts, and unavailable backend API specs. | Always | API client, TypeScript types/interfaces, auth interceptors |
| `docs/DEVELOPMENT.md` | Verified local setup, run, build, test, and preview instructions; environment variables without secrets; safe test-data guidance; PR workflow & deployment pipeline (`testing -> stag -> main`); and agent verification checklist. | Always | `package.json` scripts, config files, `.env.example`, Dockerfile |
| `docs/DECISIONS.md` | Significant architectural and design decisions (ADRs), rationale, supporting evidence, superseded choices, and lessons learned from past incidents. | Always | Git history (`git log -S`), PR discussions, comments |
| `docs/OPEN_QUESTIONS.md` | Ambiguities, conflicting evidence, known limitations, and unresolved dependencies, with affected code and what would resolve each issue. | Always | Code contradictions, uncertain dead code, verification gaps |

## Secondary & Scoped Documents (Use Sparingly)

Use additional documents only when they solve a real navigation or knowledge problem:
- **`docs/modules/<slug>.md`**: For very large repositories with distinct isolated subsystems or modular monoliths where a single architecture doc would exceed size budgets (>450 lines).
- **`docs/<app>/`**: In monorepos with multiple deployable applications (e.g., `apps/web`, `apps/admin`), replicate the canonical set under `docs/<app>/`, mapped by a root `AGENTS.md`.
- **`docs/README.md`**: Optional navigation index when the doc set spans multiple subfolders or legacy docs are preserved.

## Canonical Manifest: `docs/.ai-docs.json`

Tracks the verification baseline, skill version, and superseded documents.

```json
{
  "skill": "ai-docs",
  "skill_version": "2.0.0",
  "created": "2026-10-21",
  "last_run": {
    "mode": "init",
    "commit": "a1b2c3d",
    "date": "2026-10-21"
  },
  "canonical_docs": [
    "AGENTS.md",
    "docs/VISION.md",
    "docs/ARCHITECTURE.md",
    "docs/FLOWS.md",
    "docs/DESIGN.md",
    "docs/CONTRACTS.md",
    "docs/DEVELOPMENT.md",
    "docs/DECISIONS.md",
    "docs/OPEN_QUESTIONS.md"
  ],
  "superseded": [
    "docs/old_notes.md"
  ]
}
```

## Frontmatter Standard on All `docs/*.md`

```yaml
---
covers: ["src/components/**", "src/styles/**"]
verified_at: a1b2c3d
verified_on: 2026-10-21
---
```
- `covers`: Repo-relative globs for code files this doc tracks. Update mode checks changes against these globs.
- Note: Strategic/governance documents (`docs/VISION.md`, `docs/DECISIONS.md`, `docs/OPEN_QUESTIONS.md`) may specify `covers: ["*"]` or omit `covers` when documenting product-wide decisions rather than specific code files.
- `verified_at`: Short commit SHA against which the claims in the doc were verified.
- `verified_on`: ISO date (YYYY-MM-DD) of the verification.
