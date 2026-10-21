# Analysis Playbook: Subagent Prompts & Workflows

The orchestrator (main thread) plans the work, coordinates parallel subagents, performs evidence-based refactorings, and writes `AGENTS.md`. Subagents perform deep, focused reading across the codebase. Each subagent owns its designated output document, ensuring parallel agents never edit the same file. Every agent outputs a structured notes file to inform the orchestrator.

---

## Ground Rules for Every Subagent Prompt

- **Pass paths, not file contents:** Pass the repo root, inventory JSON path, workspace notes dir, and reference file paths.
- **Reference standards:** Subagents must read `{{SKILL_DIR}}/references/writing-rules.md` and the relevant template from `{{SKILL_DIR}}/assets/templates/` before writing.
- **Strict output boundaries:** Subagents write ONLY their assigned output document and their designated notes file. They must not alter unrelated files or git state.
- **Self-verification:** Every subagent runs the doc verifier on its output before finishing and corrects any ERRORs:
  `python3 {{SKILL_DIR}}/scripts/verify_docs.py {{REPO}} --docs {{OUTPUT_DOC}}`.
- **Concise final reply:** At most 15 lines. State the document written, verifier result, and top 5 key findings. The deep details go in the notes file to preserve orchestrator context.
- **Run in parallel batches:** Launch complementary subagents in parallel batches of up to 4–5 agents.

---

## Notes File Format

Every subagent writes `{{WORKDIR}}/notes/<name>.md` following this structure. The orchestrator uses these notes to synthesize cross-cutting insights:

```md
# Notes: <name>

## Summary
Two concise sentences: what this area is, whom it serves, and why it matters.

## Vision & Purpose
- ICP / Persona: <Target user>
- Core Problem Solved: <Pain point>
- Key Principle / Constraint: <Guiding philosophy>
- Non-goals: <Explicit out-of-scope items>

## Architecture & State
- Module / Layer: <Path> — Responsibility: <Role>
- State Ownership: <Store / Query cache / Context>
- Rendering Pattern: <SSR / SPA / Hybrid>

## Flows & Journeys
- Critical Journey: <Trigger route> → <Action> → <API call> → <Outcome>
- Guard / Permission: <Enforcement location>
- Failure Handling: <Recovery mechanism>

## Design & UI Primitives
- Reusable Components: <Name> (`path:symbol`) — Props: <props>
- Tokens & Theming: <Token file> — Dark mode: <mechanism>
- A11y & SEO: <Heading rules, meta standards>

## Contracts & APIs
- Endpoints: <METHOD /path> → Handler/Client: `path:symbol` — Auth: <auth>
- TypeScript Types: `path:Type`
- Missing Backend Needs: <Unavailable capability description>

## Development & Verification
- Commands: install, dev, build, test, preview
- Environment Variables: <VAR> (required/optional, client-exposed?)
- Safe Test Data: <Mock users or sandbox guidelines>

## Decisions & Lessons
- Decision: <Choice made> — Evidence: <Commit/PR> — Rejected alternative: <Why rejected>

## Refactoring & Dead Code Candidates (Evidence-Backed)
- Candidate: `path:symbol` — Evidence checked: <7 dimensions verified> — Recommendation: <Delete / Preserve>

## Open Questions & Ambiguities
- Question: <Genuine unknown needing human confirmation> — Affected code: `path:symbol`
```

---

## A. Product Purpose & Vision Agent

Writes `docs/VISION.md` and notes with questions for human clarification.

```text
You are analyzing the product purpose, vision, and strategic boundaries of the repository at {{REPO}} (commit {{HEAD}}).
Inventory JSON: {{INVENTORY_JSON}}. Existing docs/README: {{EXISTING_DOC_PATHS}}.

Before writing, read:
1. {{SKILL_DIR}}/references/writing-rules.md
2. {{SKILL_DIR}}/assets/templates/VISION.md

Tasks:
1. Discover the product purpose from trustworthy sources: README, package.json (description, keywords), landing pages, user-facing copy, PRDs, founder notes, and git commit history.
2. Distinguish four statuses:
   - Approved Direction: Stated purpose and confirmed boundaries.
   - Current Implementation: Features actually built in code.
   - Proposals & Roadmaps: Features in progress or planned in issues/PRs.
   - Unknowns: Unclear intent or undocumented features.
3. Define the ICP, customer problems solved, value proposition, core principles, priorities, and explicit non-goals.
4. Establish instructions for future AI agents on evaluating requests against this vision (improving unclear requests, explaining conflicts, declining contradictory changes, and describing backend contracts without fabricating mock endpoints).
5. Write {{OUTPUT_DOC}} (docs/VISION.md) and {{WORKDIR}}/notes/vision.md.
6. Verify with: python3 {{SKILL_DIR}}/scripts/verify_docs.py {{REPO}} --docs {{OUTPUT_DOC}}. Fix all ERRORs.
Reply in at most 15 lines: doc written, verifier result, top 5 strategic findings, and essential questions for the user.
```

---

## B. Architecture & State Agent

Writes `docs/ARCHITECTURE.md`.

```text
You are documenting the system mental model, modular architecture, rendering, and state ownership of {{REPO}} (commit {{HEAD}}).
Inventory JSON: {{INVENTORY_JSON}} (entry_points, frameworks, routes).

Before writing, read:
1. {{SKILL_DIR}}/references/writing-rules.md
2. {{SKILL_DIR}}/assets/templates/ARCHITECTURE.md

Tasks:
1. Identify the real entry point and startup sequence (e.g. index.html, main.tsx, app/layout.tsx, router configs).
2. Map the major modules, layers, responsibilities, and dependency rules (what may call what, what must not).
3. Document rendering patterns: SSR vs SPA vs SSG, client/server boundaries (`use client`), Suspense boundaries.
4. Document application state ownership: server cache (TanStack Query, SWR), global client stores (Zustand, Redux), URL state, and form state.
5. Trace how network requests flow through API clients, auth injection, and error interceptors.
6. Create a compact Mermaid architecture diagram (≤12 nodes).
7. Write {{OUTPUT_DOC}} (docs/ARCHITECTURE.md) and {{WORKDIR}}/notes/architecture.md.
8. Verify with: python3 {{SKILL_DIR}}/scripts/verify_docs.py {{REPO}} --docs {{OUTPUT_DOC}}. Fix all ERRORs.
Reply in at most 15 lines: doc written, verifier result, and top 5 architectural facts.
```

---

## C. User Flows Agent

Writes `docs/FLOWS.md`.

```text
You are documenting the critical user journeys and interactive flows of {{REPO}} (commit {{HEAD}}).
Inventory JSON: {{INVENTORY_JSON}} (routes, next_routes, components).

Before writing, read:
1. {{SKILL_DIR}}/references/writing-rules.md
2. {{SKILL_DIR}}/assets/templates/FLOWS.md

Tasks:
1. Map the 3–5 most critical user journeys (e.g. auth/onboarding, primary feature workflow, checkout/submission, settings).
2. For each journey, trace the complete path connecting:
   - User action & route URL
   - Entry component and UI trigger
   - State transition / optimistic update
   - API dispatch and payload
   - Response handling and storage
3. Document alternative branches and conditional paths.
4. Document role-based permissions and route guard enforcement.
5. Document failure modes: offline handling, 401 token refresh, 422 validation highlights, 500 boundary recovery.
6. Provide focused Mermaid sequence diagrams for complex flows.
7. Write {{OUTPUT_DOC}} (docs/FLOWS.md) and {{WORKDIR}}/notes/flows.md.
8. Verify with: python3 {{SKILL_DIR}}/scripts/verify_docs.py {{REPO}} --docs {{OUTPUT_DOC}}. Fix all ERRORs.
Reply in at most 15 lines: doc written, verifier result, and top flows documented.
```

---

## D. Design System & UI Agent

Writes `docs/DESIGN.md`.

```text
You are documenting the visual design system, UI components, tokens, and frontend standards of {{REPO}} (commit {{HEAD}}).
Inventory JSON: {{INVENTORY_JSON}} (components, styling configs).

Before writing, read:
1. {{SKILL_DIR}}/references/writing-rules.md
2. {{SKILL_DIR}}/assets/templates/DESIGN.md

Tasks:
1. Document visual and interaction principles (color harmony, typography, micro-interactions, dark mode).
2. Document design tokens: token sources (Tailwind, CSS vars, theme files), color palette, typography scale, spacing.
3. Build the Reusable Component Catalog: table of shared UI primitives (`Button`, `Modal`, `Input`, `Card`, `Toast`), file locations, purpose, and key props.
4. Document responsive behavior and breakpoints (mobile, tablet, desktop).
5. Document accessibility standards: semantic HTML, keyboard focus, ARIA patterns, contrast compliance.
6. Document microcopy conventions, empty states, and SEO expectations (titles, meta descriptions, headings, OpenGraph).
7. Write {{OUTPUT_DOC}} (docs/DESIGN.md) and {{WORKDIR}}/notes/design.md.
8. Verify with: python3 {{SKILL_DIR}}/scripts/verify_docs.py {{REPO}} --docs {{OUTPUT_DOC}}. Fix all ERRORs.
Reply in at most 15 lines: doc written, verifier result, and component inventory summary.
```

---

## E. Contracts & Data Agent

Writes `docs/CONTRACTS.md`.

```text
You are documenting authoritative API schemas, types, and persistence contracts of {{REPO}} (commit {{HEAD}}).
Inventory JSON: {{INVENTORY_JSON}} (routes, env_vars, data_hits).

Before writing, read:
1. {{SKILL_DIR}}/references/writing-rules.md
2. {{SKILL_DIR}}/assets/templates/CONTRACTS.md

Tasks:
1. Map authoritative TypeScript types and domain entities (reference `path:Type`; do not duplicate raw definitions).
2. Document backend API routes called by the frontend: method, full path, auth requirements, request/response types.
3. Document authentication assumptions: token storage, refresh cycle, and tenant isolation headers.
4. Document client persistence contracts: localStorage keys, sessionStorage, query cache keys.
5. Document analytics and telemetry event contracts.
6. Check for missing or incomplete backend capabilities required by frontend code. Describe required API contracts explicitly without fabricating mock implementations.
7. Write {{OUTPUT_DOC}} (docs/CONTRACTS.md) and {{WORKDIR}}/notes/contracts.md.
8. Verify with: python3 {{SKILL_DIR}}/scripts/verify_docs.py {{REPO}} --docs {{OUTPUT_DOC}}. Fix all ERRORs.
Reply in at most 15 lines: doc written, verifier result, and contracts summary.
```

---

## F. Development & Verification Agent

Writes `docs/DEVELOPMENT.md`.

```text
You are documenting the verified local setup, build, testing, and agent verification workflows for {{REPO}} (commit {{HEAD}}).
Inventory JSON: {{INVENTORY_JSON}} (manifests, infra, tooling, env_vars).

Before writing, read:
1. {{SKILL_DIR}}/references/writing-rules.md
2. {{SKILL_DIR}}/assets/templates/DEVELOPMENT.md

Tasks:
1. Extract and verify runtime prerequisites (Node.js version, package manager, system tools).
2. Document verified step-by-step setup commands (install, env file setup, dev server launch).
3. Document all environment variables read by the frontend: required vs optional, defaults, client-exposed flags (NEXT_PUBLIC_*, VITE_*). NEVER copy live secrets.
4. Document build, preview, and test commands (typecheck, lint, unit test, E2E test).
5. Document safe test-data guidance: sandbox users, mock handlers (MSW), tenant boundaries.
6. Document the PR workflow & deployment pipeline (e.g. `feature -> testing -> stag -> main/production`, branching conventions, environment triggers, and approvals). ALWAYS ask the human for their exact flow if not evident from CI configs.
7. Define the step-by-step verification checklist an AI agent must follow before submitting code changes.
8. Write {{OUTPUT_DOC}} (docs/DEVELOPMENT.md) and {{WORKDIR}}/notes/development.md.
9. Verify with: python3 {{SKILL_DIR}}/scripts/verify_docs.py {{REPO}} --docs {{OUTPUT_DOC}}. Fix all ERRORs.
Reply in at most 15 lines: doc written, verifier result, and commands verified.
```

---

## G. Decisions & History Agent

Writes `docs/DECISIONS.md`.

```text
You are discovering architectural decisions, rationale, and lessons learned from git history in {{REPO}} (commit {{HEAD}}).
Inventory JSON: {{INVENTORY_JSON}} (history.feature_commits, history.co_change).

Before writing, read:
1. {{SKILL_DIR}}/references/writing-rules.md
2. {{SKILL_DIR}}/assets/templates/DECISIONS.md

Tasks:
1. Scan git history (`git log --grep`, feature commits, revert commits, bug fix commits) to uncover significant architectural choices.
2. For each decision, document:
   - Context and problem addressed
   - Decision and implementation (`path:symbol`)
   - Supporting evidence (commit SHA or PR reference)
   - Consequences and trade-offs
   - Rejected alternatives and why they were abandoned
3. Document notable past incidents, bugs, and prevention rules.
4. Write {{OUTPUT_DOC}} (docs/DECISIONS.md) and {{WORKDIR}}/notes/decisions.md.
5. Verify with: python3 {{SKILL_DIR}}/scripts/verify_docs.py {{REPO}} --docs {{OUTPUT_DOC}}. Fix all ERRORs.
Reply in at most 15 lines: doc written, verifier result, and top decisions captured.
```

---

## H. Evidence-Based Refactoring & Dead Code Agent

Performs deep analysis for dead code, unused assets, and redundant dependencies across the 7 dimensions.

```text
You are analyzing {{REPO}} (commit {{HEAD}}) for refactoring, dead code, unused assets, and redundant dependencies.
Inventory JSON: {{INVENTORY_JSON}}.

Before analyzing, read:
1. {{SKILL_DIR}}/references/refactoring-playbook.md

Tasks:
1. Audit declared dependencies in package.json against imports in code. Identify unused dependencies.
2. Audit static assets (in public/, src/assets/): check if referenced in HTML, CSS, JS/TS, or build configs.
3. Audit unreferenced components and utility files against the 7 dimensions:
   - 1. Runtime registration (dynamic registries, dispatch maps)
   - 2. Dynamic imports (React.lazy, import(), dynamic())
   - 3. Routing configurations (file routes, catch-all routes)
   - 4. Feature flags & config toggles
   - 5. CSS references (Tailwind classes, CSS modules, SVG symbols)
   - 6. Build config & static copies
   - 7. External consumers (exports, Web Components, iframe targets)
4. Do NOT mark rarely used or permission-specific code as dead.
5. For any candidate with uncertain usage, record in notes as an Open Question.
6. Write {{WORKDIR}}/notes/refactoring.md with:
   - Verified dead code candidates (with evidence from all 7 dimensions)
   - Redundant dependencies
   - Module boundary cleanup opportunities
   - Open questions for uncertain items
Reply in at most 15 lines: confirmed dead candidates, redundant deps, and items needing human review.
```

---

## I. Existing-Docs Adopter Agent

Adopts legacy docs into the canonical AI suite.

```text
The repo {{REPO}} already contains docs: {{EXISTING_DOC_PATHS}}.
Verifier output for existing docs: {{WORKDIR}}/existing-verify.txt.

Tasks:
1. Analyze existing docs section by section.
2. Classify each section:
   - KEEP: still true and valuable (product rationale, runbooks, footguns, contracts) → assign target canonical doc (`docs/VISION.md`, `docs/ARCHITECTURE.md`, `docs/FLOWS.md`, `docs/CONTRACTS.md`, `docs/DEVELOPMENT.md`, `docs/DECISIONS.md`).
   - FIX: valuable content with stale paths or outdated symbols → target doc + required fixes.
   - DROP: obsolete, redundant, or describing deleted code.
3. Write {{WORKDIR}}/notes/_existing-docs.md with the migration map.
Reply in at most 15 lines: keepable vs fixable vs droppable content.
```

---

## J. Fresh-Agent Simulation & Quiz (Verification Phase)

Simulates a brand new AI agent entering the repository for the first time.

```text
You are a newly arrived AI agent entering {{REPO}}.
You have access ONLY to AGENTS.md and files under docs/.
Do NOT open source code, config files, or git history.
If the docs do not answer a question, reply "NOT IN DOCS" instead of guessing.

Questions to Answer:
{{NUMBERED_QUESTIONS}}

For each answer:
1. State the answer clearly.
2. Cite the exact doc and section used (`docs/DOC.md#section`).
3. Note if any two docs disagree on the same fact.
```

The orchestrator writes 6–8 repo-specific verification questions covering:
- What is the product purpose and primary ICP?
- Where does application execution start, and what is the rendering pattern?
- Where is client session state stored and how is it invalidated?
- What are the steps and files modified to add a new page or feature?
- What command runs local tests, and what is the pre-PR verification checklist?
- What is one critical rule or footgun that must never be broken in this repo?
- Are any backend capabilities missing for current frontend features?

Grading:
- **Wrong or "NOT IN DOCS":** Patch the responsible canonical document.
- **Hard to locate:** Add a direct pointer in `AGENTS.md`'s reading order.
- **Conflicting claims:** Read the code, settle the truth, and update the incorrect doc.
