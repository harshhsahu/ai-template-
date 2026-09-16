# Agent Guide — {{PRODUCT_NAME}}

> This file (mirrored to `CLAUDE.md` via `@AGENTS.md`) is the first thing an AI agent or
> new engineer reads. Keep it short and imperative. Deep detail lives in `docs/`.

## Read before you write

You MUST read the relevant guide in [`docs/`](docs/) before writing code or changing
structure. Start with:

- [`docs/AGENTS.md`](docs/AGENTS.md) — the hard rules for this codebase (read this first)
- [`docs/00-project-overview.md`](docs/00-project-overview.md) — what this product is
- [`docs/07-system-architecture.md`](docs/07-system-architecture.md) — how it fits together
- [`docs/08-folder-structure.md`](docs/08-folder-structure.md) — where things go

If your framework/library has vendored docs (e.g. `node_modules/<pkg>/dist/docs/`),
read those instead of relying on training data — versions drift and APIs break.

## Quick reference

- **Architecture:** <!-- fill: one-line description, e.g. "Mock-first V1 → real backend integration; UI calls `/api/**`, never raw databases." -->
- **Tech stack:** {{FRAMEWORK}}, {{LANGUAGE}}, {{STYLING}}, {{DB}} <!-- keep in sync with docs/06-tech-stack.md -->
- **Security:** Secrets stay server-side. Never import server-only clients into client code.
- **ID mapping:** <!-- fill: how identifiers map across your systems -->
- **Graceful degradation:** If a backend fails, return `null` for that data block — don't 500 the whole page.
- **Documentation:** Update `docs/**` in the same commit as any contract change.

## The ten rules

1. **Docs are the source of truth.** Disagreement between code and docs is a bug. Fix both.
2. **Read the guide for the area you're touching** before editing (`docs/api`, `docs/modules`, `docs/database`, ...).
3. **Respect server/client boundaries.** Secrets and DB clients never reach the browser bundle.
4. **Go through the API layer.** UI never talks to a database or external service directly.
5. **Fail soft.** Catch backend errors and degrade to `null`/empty/mock — keep the app navigable.
6. **Map IDs deliberately.** Never assume one ID type works everywhere; pass the type each source needs.
7. **Stay inside the sanctioned stack.** Don't add a second charting/icon/animation library.
8. **Prefer the platform's defaults.** Server components / SSR / built-in routing over bespoke abstractions.
9. **Small, reviewable changes.** One concern per PR; follow `docs/23-git-workflow.md`.
10. **Update docs when you learn something.** New infra fact or changed contract → update `docs/` now, not later.

## When something isn't documented

If you discover a fact about infrastructure, an API contract, or a data model that isn't
written down: **write it down** in the right `docs/` file as part of your change. The next
agent depends on it.
