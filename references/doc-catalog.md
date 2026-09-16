# Doc catalog — what each template file is for

Read this in Phase 3, when you're deciding which files to create.

## Contents

- [How the tiers work](#how-the-tiers-work)
- [Tier A — always create](#tier-a--always-create)
- [Tier B — create only with evidence](#tier-b--create-only-with-evidence)
- [Tier C — human-owned](#tier-c--human-owned)
- [Subfolder templates](#subfolder-templates)
- [Anti-duplication map](#anti-duplication-map)
- [Numbering rules](#numbering-rules)

## How the tiers work

The template ships 25 numbered guides plus 7 cloneable subfolder templates. Reproducing
all of them for every project produces a directory of stubs, and the template's own README
says to "delete what you don't need... rather than leaving a stub." So sort files into
three tiers:

- **Tier A** is the navigation spine. Without these, an agent dropped into the repo has
  nothing to orient on, so create them even if some sections end up marked TODO.
- **Tier B** documents a concern only if the concern exists in the code. The *absence* of
  `16-analytics.md` is itself information: this project doesn't do analytics. That's more
  honest than a file full of empty tables. When you skip one, list it in your Phase 3 plan
  and in your final summary with the reason, so the user can override.
- **Tier C** needs a human. Code cannot tell you the business goal or the persona. Default
  to skipping these and offer them; create the stub-plus-TODO version only if asked.

## Tier A — always create

| File | Purpose | Evidence to gather |
|---|---|---|
| `AGENTS.md` (repo root) | The first file an agent or new engineer reads. Short, imperative, points into `docs/`. Fill the Quick reference block and rewrite "The ten rules" to reflect the project's real constraints. | Everything else — write it last |
| `CLAUDE.md` (repo root) | One line: `@AGENTS.md`. The mirror the template's README prescribes so Claude Code picks up the same guardrails. | none |
| `docs/AGENTS.md` | The project-specific rulebook — the sharp constraints an agent must not violate. This is the highest-leverage file in the set; the template calls it "the single most important file for keeping agents on the rails." | Layer boundaries, real ID types and how they map, secret env var names, approved libraries (one per concern), error/degradation policy |
| `docs/00-project-overview.md` | Name, 2–3 sentence summary, current phase, key features. | Manifest name/description, README, top-level route or module names |
| `docs/06-tech-stack.md` | The choice-per-layer table with versions. | Manifests and lockfiles — cite exact pinned versions, not "latest" |
| `docs/07-system-architecture.md` | Product-level architecture summary with a mermaid diagram and the request data flow. Keep consistent with `ARCHITECTURE.md`. | Entry points, API layer, which services the API talks to |
| `docs/08-folder-structure.md` | Annotated tree plus placement rules ("where does a new X go?"). | The real directory tree — prune vendored/build dirs |
| `docs/09-coding-guidelines.md` | Style, naming, component conventions, do/don't. | Linter/formatter config (`.eslintrc`, `ruff.toml`, `.prettierrc`, `.editorconfig`), plus conventions you can observe consistently in the code |
| `docs/ARCHITECTURE.md` | The canonical deep dive: overview, integration strategy and phases, client layer, backend/aggregation layer per system, security model. | Same as 07, plus auth and secrets handling |
| `docs/22-definition-of-done.md` | A checklist. Mostly template-stable; adjust the bullets that reference things this project doesn't have. | CI checks, test setup, review config |

`docs/12-api-guidelines.md` is also Tier A whenever the project exposes any HTTP surface,
which is nearly always. Skip it only for a library or CLI with no server.

## Tier B — create only with evidence

| File | Create when you find | Skip when |
|---|---|---|
| `10-design-system.md` | A design-token file, theme config (`tailwind.config.*`, CSS custom properties), or a component library dependency | No UI in the repo |
| `11-state-management.md` | A state library (Redux, Zustand, Pinia, MobX), React Context providers, or a server-state cache (react-query, SWR) | No client app, or state is purely local `useState` with nothing worth documenting — note that in 09 instead |
| `13-security.md` | Auth middleware, permission classes, env-based secrets, CORS/CSRF config, token handling | A public static site with no auth or secrets |
| `14-performance.md` | Caching config, pagination classes, `select_related`/eager-loading, bundle analysis, CDN or index tuning | Nothing in the repo addresses performance — don't invent budgets |
| `15-environment-setup.md` | A `.env.example`, Docker/compose file, or documented run scripts | Never skip if any env var is read — this is where the graceful-degradation map lives |
| `16-analytics.md` | An analytics/telemetry SDK or event-tracking calls | No provider anywhere |
| `17-notifications.md` | Email/SMS/push/toast/webhook sending code | No notification code (the template says "Delete this file if unused") |
| `18-error-handling.md` | Exception handlers, error boundaries, a standard error envelope, retry/fallback logic | Nothing systematic exists — but if an API layer exists, document the observed behavior even if it's inconsistent, and flag the inconsistency |
| `19-testing.md` | A test runner config or any test files | No tests — then say so plainly in 22 rather than creating an empty 19 |
| `20-deployment.md` | Dockerfile, CI workflow, IaC, host config (`nginx.conf`, `Procfile`, `vercel.json`), entrypoint scripts | Nothing deploy-related |
| `23-git-workflow.md` | PR template, CODEOWNERS, branch protection config, or a legible commit-message convention in history | Only conventions you can actually observe; don't assert a branching model from nothing |
| `24-feature-flags.md` | A flag provider or a homegrown flag/toggle mechanism | No flags (the template says to delete it) |
| `05-navigation.md` | A client-side router with a route table, or server-rendered page routes | No user-facing navigation (pure API service) — the API surface belongs in `api/` instead |

## Tier C — human-owned

`01-product-vision.md`, `02-business-goals.md`, `03-user-personas.md`,
`04-user-journeys.md`, `21-roadmap.md`.

Code does not contain vision, KPIs, personas, or a roadmap. Inferring them is exactly the
invention this skill is built to prevent — a persona invented from a database table will
read as authoritative and quietly mislead product decisions.

Two honest exceptions, both evidence-backed:

- A repo with a substantial README, pitch deck, or product doc: you may summarize *that
  source* into 01/02, citing it as the source.
- `04-user-journeys.md`: an observable UI flow (route sequence, wizard steps, redirect
  chain) is a real journey. Document the flow as observed and leave the persona and
  business framing as TODO.

`21-roadmap.md` has one legitimate code-derived section: `## Done` can list shipped
milestones from git tags or a CHANGELOG. Leave Now/Next/Later to the human.

## Subfolder templates

Each subfolder keeps its `_TEMPLATE.md` in place as the pattern to clone.

| Folder | One file per | Name it | Evidence |
|---|---|---|---|
| `docs/api/` | API domain, not per endpoint | `orders.md`, `users.md` — group by resource/router | Route definitions, handler bodies, serializers/DTOs, real response shapes |
| `docs/database/` | Store or topic. Use `entities.md` for the catalog and `relationships.md` for how they connect | `entities.md`, `relationships.md`, or `postgres.md` per store | Migrations (most reliable — they are the applied truth), ORM models, raw DDL |
| `docs/modules/` | Product module / feature area, numbered | `01-checkout.md`, `02-billing.md` | A coherent feature slice: its screens, its routes, its data |
| `docs/ui/` | Reusable/shared component only | `shared/data-table.md`, or mirror the source path | Component source: prop types, variants, states |
| `docs/current-infrastructure/` | External backend system you integrate | `postgres.md`, `redis.md`, `stripe.md` | Client/connection code, env vars, the functions your code calls, failure behavior |
| `docs/plans/` | Dated implementation plan | `YYYY-MM-DD-NNN-<type>-<slug>-plan.md` | Don't generate — these are written per change |
| `docs/brainstorms/` | Dated requirements doc | `YYYY-MM-DD-<slug>-requirements.md` | Don't generate — these precede a change |

Leave `plans/` and `brainstorms/` as the bare `_TEMPLATE.md`. Generating a fake dated plan
for work that never happened corrupts the record.

**How many `modules/` files?** One per feature area a user would name, not one per source
directory. Six route groups that are all CRUD over one domain is one module; a dashboard,
a billing flow, and an admin console are three. If you can't write a distinct "Purpose" and
"Business Value" for a candidate module, it isn't one — fold it into a sibling.

**Which `ui/` components?** Only the shared, reused ones (a design-system primitive, a
`DataTable`, a `Modal`). A one-off page component belongs to its module's doc. If the repo
has thirty primitives, document the ones other code actually imports more than once and say
you scoped it that way.

## Anti-duplication map

Each concern has one home. Elsewhere, link. When two files disagree the docs stop being
citable, which defeats the "docs are the source of truth" contract.

| Concern | Lives in | Everywhere else |
|---|---|---|
| Stack + versions | `06-tech-stack.md` | Root `AGENTS.md` Quick reference gets a one-line summary only |
| Directory layout | `08-folder-structure.md` | Modules reference paths, don't re-draw the tree |
| Deep architecture | `ARCHITECTURE.md` | `07` is the short summary and links down |
| Response envelope, error conventions | `12-api-guidelines.md` | `api/<domain>.md` documents that route's specific shape |
| Per-endpoint contract | `api/<domain>.md` | `modules/*` lists endpoint names under "API Dependencies" and links |
| Table/column definitions | `database/entities.md` | `current-infrastructure/<system>.md` covers connection, role, degradation; don't restate columns |
| Shared component props | `ui/<component>.md` | `modules/*` names the component and links |
| Env vars | `15-environment-setup.md` | `13-security.md` discusses posture; infra files name their own var |
| Hard agent rules | `docs/AGENTS.md` | Root `AGENTS.md` keeps the short universal version |

## Numbering rules

The `00–24` numbers are stable across products so links and muscle memory survive. Never
renumber to close a gap left by a skipped Tier B file — a missing `17` is meaningful, and
renumbering breaks every existing cross-link.

`modules/` files use their own `NN-` sequence starting at `01`, in the order a user
encounters them (entry/dashboard first, admin last).
