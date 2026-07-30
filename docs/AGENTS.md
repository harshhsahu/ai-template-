# AI Agent Guidelines ({{PRODUCT_NAME}})

Rules and heuristics for AI coding agents working in the `{{PRODUCT_SLUG}}` repository.
Read this carefully before generating or modifying any code. These rules override
default agent behavior.

> This is the **project-specific** rulebook. The repo-root `AGENTS.md` is the short
> universal version; this file is where the sharp, product-specific constraints live.

## 1. Architecture / Integration Phase

<!-- fill: What phase is the project in? Mock-first? Fully integrated? Which systems are
     real vs simulated? State clearly what an agent MAY and MAY NOT do. Example below. -->

- <!-- e.g. "UI components MAY call real `/api/**` routes when the endpoint exists." -->
- <!-- e.g. "If no real API exists, define types + fixtures in `lib/mock/`." -->
- **Do NOT** write raw DB queries or hit external endpoints directly from UI components.
  Always go through the API layer.

## 2. Server vs Client Boundaries

<!-- fill for your framework. Example for Next.js App Router: -->
- Default to Server Components; use client components only for hooks/interactivity/events.
- The API layer (`app/api/**` / equivalent) is the only place that touches server-only clients.
- **NEVER** import server-only clients (DB pools, admin tokens) into client components —
  it leaks secrets (`{{SECRET_ENV_NAMES}}`) into the browser bundle.

## 3. Tech Stack Restrictions

- **Styling:** {{STYLING}} — no custom CSS unless unavoidable (put it in the global stylesheet).
- **Icons:** {{ICON_LIB}} only.
- **Charts:** {{CHART_LIB}} only.
- **Animations:** {{ANIMATION_LIB}}.
<!-- One approved library per concern. Adding a second is a review-blocking change. -->

## 4. ID Handling & Cross-System References

<!-- fill: IDs are the #1 source of cross-system bugs. Document every ID type and its
     canonical home + how it maps. Example: -->
- `{{ID_A}}`: <!-- source of truth + what it maps to -->
- `{{ID_B}}`: <!-- ... -->

Never assume an ID is universally available. Pass the specific ID type each data source needs.

## 5. Fallback & Graceful Degradation

- If a backend service is unconfigured or fails, the API route catches the error and
  returns `null` for that data block — never a 500 for the whole page.
- The UI handles `null` gracefully (empty state or mock fallback) so the app stays navigable.

## 6. Modifying Documentation

If you learn something new about infrastructure, or change an API/data contract, you
**must** update the corresponding file in `docs/api/`, `docs/database/`, `docs/modules/`,
or `docs/current-infrastructure/` in the same change. The docs are the source of truth.
