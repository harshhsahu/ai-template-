---
name: ai-docs
description: "Prepare existing frontends and products for 100% AI-driven coding. Understand and preserve product purpose, establish mental model and architecture, remove dead code/redundant dependencies with evidence, establish a verified canonical doc set (AGENTS.md, VISION.md, ARCHITECTURE.md, FLOWS.md, DESIGN.md, CONTRACTS.md, DEVELOPMENT.md, DECISIONS.md, OPEN_QUESTIONS.md), keep applications dependable, and maintain living project knowledge. Run as /ai-docs [init|prepare|update|check] [area] [--yes]."
compatibility: "Claude Code, Antigravity, Cursor, and modern agent environments with a local git checkout, Python 3, and subagent/task execution capabilities. Run as /ai-docs [init|prepare|update|check] [area] [--yes]."
---

# 100% AI-Driven Frontend Preparation & Documentation

Prepare this frontend repository for 100% AI-driven development.
Our goal is that **any capable AI coding agent can enter the repository, understand our product and architecture, evaluate a request intelligently, and deliver reliable changes without repeatedly needing humans to explain the system.**

## Core Division of Responsibility
- **Humans provide:** Vision, strategic priorities, and business judgment.
- **AI takes responsibility for:** Deep understanding, implementation, verification, evidence-based refactoring, and maintaining project knowledge.

## Quality Bar
1. **Evidence only:** Every path, symbol, route, component, token, and env var exists in code at the verified commit.
2. **One home per fact:** Each domain truth lives in one canonical document; other files link rather than duplicate.
3. **Project-specific knowledge:** Omit generic coding platitudes; capture the unwritten rules, domain terms, and footguns.
4. **The "Why" is recorded:** Capture the reasons behind design decisions, past incidents, and rejected alternatives.
5. **Dependable application:** Refactoring and cleanup must never break existing behavior, appearance, routes, contracts, permissions, analytics, or SEO.
6. **No empty placeholders:** Every document written has real, verified substance.

Arguments: `$ARGUMENTS`. Default mode is chosen based on repository state:
- First word `init`, `prepare`, `update`, or `check` selects that mode.
- If `docs/.ai-docs.json` exists → default is `update`.
- If no manifest exists → default is `init` (prepare repository).
- Optional area name narrows `update`. `--yes` skips interactive confirmations.

---

## Phase 0: Setup & Baseline Establishment

Before modifying code or writing documentation, establish and record the current baseline:

1. **Find Repo Root & Tooling:**
   - Resolve absolute paths: `REPO` (repo root), `SKILL_DIR` (skill folder), `HEAD_SHORT`, `TODAY` (YYYY-MM-DD), and `WORK` (scratchpad directory with `notes/` subdirectory).
2. **Establish the Execution Baseline (Pre-flight Checks):**
   - Run available automated checks:
     * Package install: `npm install` / `pnpm install` / `yarn install`
     * Typechecking: `npm run typecheck` (or `tsc --noEmit`)
     * Linting: `npm run lint`
     * Test suites: `npm test`
     * Production build: `npm run build`
   - Record existing failures, warnings, and error counts in `$WORK/baseline.txt`. Pre-existing defects must be distinguished from newly introduced regressions.
3. **Capture Representative User Journeys & Visual State:**
   - Launch dev server or preview build.
   - Trace core user journeys (login, primary dashboard/view, core interaction flow).
   - Capture visual state / screenshots of representative screens.
   - Note network requests, authentication tokens, and console logs.
4. **Preserve Starting Point:**
   - Check `git status --porcelain`. Warn if uncommitted changes exist. Ensure unrelated work in progress is preserved.

---

## Phase 1: Understand & Preserve Product Purpose

1. **Recover Purpose from Trustworthy Sources:**
   - Read the `README.md`, build manifests (`package.json`), landing pages, customer-facing copy, PRDs, founder notes, and git commit history.
   - Run the repo inventory:
     ```bash
     python3 "$SKILL_DIR/scripts/inventory.py" "$REPO" --out "$WORK/inventory.json"
     ```
2. **Categorize Product Direction into Four Explicit Statuses:**
   - **Approved Direction:** Confirmed strategic goals, target audience (ICP), customer problems solved, core principles, and non-goals.
   - **Current Implementation:** Features and behavior currently functioning in the codebase.
   - **Proposals & Roadmaps:** Draft PRs, planned features, or upcoming experiments.
   - **Unknowns & Ambiguities:** Missing product rationale or contradictory behavior.
   *RULE:* Never invent our vision or assume everything in the current code is intentional.
3. **Ask the Essential Clarifying Questions (ALWAYS Ask the PR & Deployment Flow):**
   - If critical product gaps remain, ask the user a single focused question set with the few essential queries needed to fill the gaps.
   - **MANDATORY QUESTION:** You must ALWAYS ask the user for their exact flow for building PRs and deploying features to production (e.g. `feature branch -> PR & CI -> testing -> stag -> main / production deployment`). Document this flow explicitly in `AGENTS.md` and `docs/DEVELOPMENT.md`.
4. **Codify Request Evaluation Protocol for Future Agents:**
   - Future agents must evaluate all requests against this context:
     * *Improve unclear requests:* Clarify user problem and propose solutions aligned with vision before writing code.
     * *Explain conflicts & decline contradictions:* If a request violates an approved principle or non-goal, explain why and recommend declining.
     * *Explicit direction changes:* If the user deliberately changes direction, make that decision explicit and update `docs/VISION.md`.
     * *Unavailable backend capabilities:* If a requested frontend change needs unavailable backend capabilities, describe the required API contract in `docs/CONTRACTS.md`. **Never fabricate mock integrations or fake endpoints.**

---

## Phase 2: Evidence-Based Refactoring & Cleanup

**Do useful cleanup now. Do not stop after writing an audit or documentation.**

Follow `references/refactoring-playbook.md` strictly:
1. **Audit Dead Code Across All 7 Dimensions:**
   Before removing any file, component, utility, or asset, verify all 7 dimensions:
   - 1. *Runtime registration:* Dynamic component registries, string-based dispatchers (`registry[type]`).
   - 2. *Dynamic imports:* `React.lazy()`, `import()`, Next.js `dynamic()`, route code splitting.
   - 3. *Routing configurations:* File-based routes (`app/`, `pages/`, `routes/`), catch-alls (`[...slug]`), router tables.
   - 4. *Feature flags & toggles:* Environment variables, remote config flags, conditional rollout blocks.
   - 5. *CSS & style references:* Tailwind safelists, CSS modules, template classes (`bg-${color}`), SVG symbol sprites.
   - 6. *Build config & static assets:* Build plugin copies, public folder assets, HTML headers, web manifests.
   - 7. *External consumers:* Exported libraries, microfrontend remotes, Web Components, iframe embed targets.
   *Safety Invariant:* Do NOT confuse rarely used functionality, compatibility code, or permission-specific paths with dead code. If uncertain, preserve the code and record the question in `docs/OPEN_QUESTIONS.md`.
2. **Execute Evidence-Backed Removals:**
   - Remove genuinely unused files and obsolete static assets.
   - Prune redundant dependencies from `package.json` (packages with 0 imports in code, or unused devDependencies).
   - Consolidate overlapping utility libraries (e.g., duplicate date or HTTP helpers).
   - Record every removal with evidence in `$WORK/removals.md`.
3. **Simplify Module Boundaries:**
   - Ensure clear separation between:
     * *Rendering (Presentation):* UI components accepting props; no direct network calls in JSX.
     * *Application State:* Stores (Zustand, Redux) and server cache (TanStack Query) owning state transitions.
     * *API Access:* Typed client wrappers in `src/services/` or `src/api/`.
     * *Business Rules:* Pure domain helpers in `src/lib/` or `src/utils/`.
   - Consolidate genuine duplication without forcing unrelated behaviors into brittle generic abstractions.
4. **Verify Application Dependability Against Baseline:**
   - Run typecheck, linter, tests, and production build: compare results to Phase 0 baseline.
   - Launch dev server / preview build and compare screens against pre-cleanup visual captures.
   - Verify that routes, appearance, contracts, permissions, tenant boundaries, analytics, preferences, and SEO metadata are strictly preserved.

---

## Phase 3: Parallel Subagent Analysis & Deep Mapping

Dispatch deep-analysis subagents following `references/analysis-playbook.md`. Run in parallel batches (up to 4–5 at a time):

| Subagent | Role | Generates |
|---|---|---|
| **A. Vision Agent** | Recovers product purpose, ICP, value prop, principles, non-goals, request evaluation rules | `docs/VISION.md` + `$WORK/notes/vision.md` |
| **B. Architecture Agent** | Maps mental model, entry points, rendering, state ownership, Mermaid diagram | `docs/ARCHITECTURE.md` + `$WORK/notes/architecture.md` |
| **C. Flows Agent** | Traces critical user journeys, happy paths, alternatives, permissions, recovery | `docs/FLOWS.md` + `$WORK/notes/flows.md` |
| **D. Design System Agent** | Visual principles, reusable component catalog, design tokens, a11y, SEO | `docs/DESIGN.md` + `$WORK/notes/design.md` |
| **E. Contracts Agent** | Authoritative API schemas, types, auth, persistence, missing backend specs | `docs/CONTRACTS.md` + `$WORK/notes/contracts.md` |
| **F. Development Agent** | Verified setup, run, build, test, env vars without secrets, safe test-data | `docs/DEVELOPMENT.md` + `$WORK/notes/development.md` |
| **G. Decisions Agent** | Architectural decisions (ADRs), rationale, git history, rejected alternatives | `docs/DECISIONS.md` + `$WORK/notes/decisions.md` |
| **H. Existing-Docs Agent** | (If legacy docs exist) Adopts valuable rationale and incident lessons into the suite | `$WORK/notes/_existing-docs.md` |

Each subagent reads its template in `assets/templates/`, writes its doc, verifies with `scripts/verify_docs.py`, and outputs structured notes.

---

## Phase 4: Authoring the Canonical Documentation Suite

1. **Synthesize Cross-Cutting Notes:**
   - Run `python3 "$SKILL_DIR/scripts/notes_digest.py" "$WORK/notes"`.
   - Reconcile any contradictions between notes by reading source code.
2. **Finalize Canonical Suite:**
   - Review and polish the 8 canonical documents under `docs/`:
     * `docs/VISION.md`
     * `docs/ARCHITECTURE.md`
     * `docs/FLOWS.md`
     * `docs/DESIGN.md`
     * `docs/CONTRACTS.md`
     * `docs/DEVELOPMENT.md`
     * `docs/DECISIONS.md`
     * `docs/OPEN_QUESTIONS.md`
3. **Author Root `AGENTS.md` (Last):**
   - Use `assets/templates/AGENTS.md`. Keep under ≤150 lines.
   - Include:
     * Product scope and purpose summary (2–3 sentences).
     * Exact, verified commands (install, dev, build, typecheck, lint, test, preview).
     * Reading order directing agents to `docs/VISION.md` and `docs/ARCHITECTURE.md` first, then to task-relevant flows and contracts.
     * 10–15 numbered project rules an agent would break without being told (with reasons/evidence).
     * Directory map.
     * **PR & deployment flow:** The confirmed promotion pipeline (e.g. `testing -> stag -> main`) and branching rules.
     * Verification and documentation update expectations.
4. **Wire Up Tool Adapters:**
   - `CLAUDE.md`: Ensure `@AGENTS.md` is present.
   - Other agent files (`.cursorrules`, `GEMINI.md`, `.github/copilot-instructions.md`): Point to `AGENTS.md` if user approves.
   - Write `docs/.ai-docs.json` manifest.

---

## Phase 5: Verification & Fresh-Agent Simulation

1. **Automated Mechanical Verification:**
   ```bash
   python3 "$SKILL_DIR/scripts/verify_docs.py" "$REPO"
   ```
   - Fix every ERROR by aligning docs to code (never inventing code).
   - Ensure all `covers:` globs resolve and no broken links exist.
   - Re-run until **0 errors**.
2. **Fresh-Agent Simulation & Quiz:**
   - Dispatch the Fresh-Agent simulation (Playbook J) given 6–8 repo-specific questions.
   - The simulator reads ONLY `AGENTS.md` and `docs/` (no code, no git).
   - Verify that a fresh session can:
     * Locate the vision and product purpose.
     * Trace a representative user journey.
     * Identify the correct implementation area for a new feature.
     * Find relevant verification commands and rules.
   - Patch any gaps, ambiguities, or navigation friction uncovered by the simulation.

---

## Phase 6: Final Deliverable Report

Present a concise, structured report covering:
1. **What Became Simpler & Why:** Summary of architectural clarity gained, module boundary improvements, and reduced complexity.
2. **Significant Code & Dependencies Removed:** Explicit list of removed files, dead exports, unused assets, and pruned dependencies, with supporting evidence.
3. **The Documentation Map:** Overview of the canonical suite (`AGENTS.md`, `VISION.md`, `ARCHITECTURE.md`, `FLOWS.md`, `DESIGN.md`, `CONTRACTS.md`, `DEVELOPMENT.md`, `DECISIONS.md`, `OPEN_QUESTIONS.md`).
4. **Checks Performed & Verification Results:** Baseline vs final verification status (typecheck, lint, tests, build, browser checks, doc verifier).
5. **Remaining Verification Gaps:** Third-party credentials, staging services, or sandbox dependencies unavailable during preparation.
6. **Unresolved Product Questions & Technical Risks:** Key items recorded in `docs/OPEN_QUESTIONS.md`.
7. **Remaining Work & How to Resume/Revert:** Clear instructions on branching, resume checkpoints, and rollback commands.

---

## Mode: update (Knowledge Maintenance)

Follow `references/update-mode.md`:
1. **Evaluate Request:** Compare user request against `docs/VISION.md`, `docs/ARCHITECTURE.md`, and `docs/CONTRACTS.md`.
2. **Detect Drift:** Run `python3 "$SKILL_DIR/scripts/affected_docs.py" "$REPO"`.
3. **Synchronous Update:** Update affected docs, sequence diagrams, and contracts in the same commit that changes code.
4. **Maintain Progress Records:** Keep concise notes during multi-step tasks.
5. **Re-Verify:** Run `verify_docs.py` until 0 errors, bump `verified_at` and `verified_on`, update manifest.

---

## Mode: check (Read-Only Audit)

Run read-only verification:
```bash
python3 "$SKILL_DIR/scripts/verify_docs.py" "$REPO"
python3 "$SKILL_DIR/scripts/affected_docs.py" "$REPO"
```
Report error counts, stale docs, unmapped code, and broken claims. Output: "run `/ai-docs update` to fix". Writes no files.

---

## Critical Rules ("Never")

- **Never invent product vision, personas, or intent:** Unknown and important → record in `docs/OPEN_QUESTIONS.md`.
- **Never fabricate working integrations:** If a backend capability is missing, describe the required contract in `docs/CONTRACTS.md`.
- **Never remove code without conclusive evidence across all 7 dimensions:** Runtime registrations, dynamic imports, routing configs, feature flags, CSS references, build configs, and external consumers must be checked.
- **Never weaken tests, suppress lint rules, or lower verification standards** merely to make checks pass.
- **Never commit secrets or credentials:** Document variable names and defaults only.
- **Never perform unrequested major framework migrations or broad dependency rewrites.**
- **Never delete or commit files without explicit authorization.**
