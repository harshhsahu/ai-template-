# Refactoring & Cleanup Playbook: Evidence-Based Frontend Preparation

This playbook defines the exact process for cleaning and refactoring an existing frontend to make it 100% AI-ready.
**Do useful cleanup now. Do not stop after writing an audit or documentation.**

---

## 1. Establishing the Baseline Before Any Changes

Before modifying a single line of code, you must establish and record the current baseline:

1. **Run All Available Checks:**
   - Package install / lockfile integrity: `npm/pnpm/yarn install`
   - Typechecking: `npm run typecheck` (or `tsc --noEmit`)
   - Linting & formatting: `npm run lint`
   - Test suites: `npm test`
   - Production build: `npm run build`
   - Record existing failures, warnings, and error counts in your session notes so pre-existing defects are never confused with new regressions.
2. **Representative User Journeys & Visual State:**
   - Launch the local development server or preview build.
   - Trace core user journeys (e.g., login, primary view, core interaction, settings).
   - Capture visual state / screenshots of representative screens using browser tools or subagents.
   - Note key interactive behaviors, network requests, and console output.
3. **Establish a Clean, Recoverable Starting Point:**
   - Check `git status`. Ensure unrelated work in progress is preserved and stashed or committed.
   - Work in small, isolated, atomic steps. Never batch dozens of speculative deletions into one massive unrevertible change.

---

## 2. Evidence Checklist Before Removing Any Code

Dead-code removal must be backed by **conclusive evidence**. Never declare a file or export "unused" simply because a single grep search returned no direct static import.

Before removing any file, function, asset, or export, check all seven dimensions:

| Dimension | What to Check & Verify | Grep / Search Guidance |
|---|---|---|
| **1. Runtime Registration** | Dynamic component lookups, plugin maps, component registries, string-based dispatchers (e.g. `const Component = registry[type]`). | Search for the component/function name as a string literal or object key across the codebase. |
| **2. Dynamic Imports** | `React.lazy(() => import(...))`, `import(...)`, Next.js `dynamic(() => import(...))`, dynamic route segments. | Search for path segments or base filenames in `import(` calls. |
| **3. Routing Configurations** | File-based routing (e.g. `app/`, `pages/`, `routes/`), catch-all routes (`[...slug]`), route configuration tables, redirect mappings. | Check if file location is a route convention in the framework (Next.js, Remix, SvelteKit, Vite router). |
| **4. Feature Flags & Config Toggles** | Features toggled via remote flags, environment variables, or rollout experiments (e.g. `flags.enableNewCheckout ? <NewCheckout /> : <OldCheckout />`). | Check if the symbol is referenced behind a flag check or conditional toggle. |
| **5. CSS & Style References** | Class names referenced dynamically in Tailwind config `safelist`, CSS modules, template strings (`bg-${color}`), SVG symbol sprites, global stylesheets. | Search CSS/SCSS files and config files for class names and asset filenames. |
| **6. Build Config & Static Assets** | Assets copied by build plugins (e.g. `public/`, `static/`, Vite `assetsInclude`, Webpack `CopyWebpackPlugin`, favicons, manifest files). | Check HTML `<head>`, `manifest.json`, build configs, and server endpoints. |
| **7. External Consumers** | Components exported as npm packages, microfrontend remotes, Web Components, iframe embed targets, analytics script hooks (`window.analyticsHandler`). | Check `package.json:exports`, `main`, module federation configs, and public APIs. |

### Strict Safety Rules
- **Do NOT confuse rarely used functionality, compatibility shims, or permission-specific admin screens with dead code.**
- **If removal is uncertain:** Preserve the code and record the question in `docs/OPEN_QUESTIONS.md`.
- **Do NOT remove existing features merely because their product rationale is unclear.** Human vision takes precedence; clarify before removing.
- **Record every significant removal:** Note the file/symbol, the evidence proving it was dead, and how verification was performed.

---

## 3. Dependency Cleanup & Pruning

1. **Inspect `package.json` Dependencies:**
   - Run inventory to list all declared dependencies against imports in code.
   - Identify packages with zero imports across `src/`, `app/`, `components/`, etc.
   - Check build and tooling dependencies: ensure dependencies used only at build/test time are in `devDependencies`, not production `dependencies`.
2. **Check for Redundant / Duplicate Utility Libraries:**
   - Look for overlapping libraries (e.g., both `lodash` and `lodash-es`, or both `axios` and native `fetch`, or multiple date libraries like `moment`, `date-fns`, and `dayjs`).
   - If consolidating, choose the single standard approved library and migrate imports step-by-step.
3. **Verify Lockfile & Build:**
   - After pruning a dependency, run `npm/pnpm install`, then run `npm run typecheck`, `npm test`, and `npm run build`.

---

## 4. Module Boundary Simplification & Refactoring

Refactoring is meant to make rendering, state, API access, and business rules cleanly separated and easy to locate:

1. **Locate and Separate Responsibilities:**
   - **Rendering (Presentation):** Pure UI components that receive props and emit events. No direct database or raw network calls inside JSX.
   - **Application State:** Explicit stores (Zustand, Redux) or query caches (TanStack Query) owning state transitions.
   - **API Access:** Dedicated client functions in `src/services/` or `src/api/` with typed requests and responses.
   - **Business Rules:** Pure domain functions in `src/lib/` or `src/utils/` that can be tested in isolation.
2. **Improve Naming & Consistency:**
   - Rename ambiguous, misleading, or legacy identifiers to match domain terms documented in `docs/VISION.md`.
   - Standardize file naming (e.g., PascalCase for React components, camelCase/kebab-case for utilities).
3. **Consolidate Genuine Duplication Without Forcing Bad Abstractions:**
   - Consolidate identical code paths (e.g. identical API error handling or identical date formatting).
   - **Do NOT force unrelated behaviors into brittle generic abstractions** just because they happen to look similar today. Maintain clear module boundaries.
4. **Preserve Useful Existing Conventions:**
   - Avoid framework migrations (e.g. do not convert React Router to Next.js or Vite to Webpack unless requested).
   - Avoid broad major dependency upgrades unless specifically justified by security or blocking defects.
   - Judge "lightweight" by **reduced complexity and measured overhead**—not raw file count or deleted lines.

---

## 5. Keeping the Application Dependable (Verification Invariants)

Every step of refactoring must protect application stability:

1. **Preserve Essential Invariants:**
   - **Routes & URLs:** All existing public routes, query parameters, redirects, and anchor links must continue to function.
   - **UI Appearance & Styling:** Colors, layouts, spacing, responsive behavior, and dark mode must match the baseline.
   - **API Contracts:** Request payloads, headers, query parameters, and response interpretations must remain identical.
   - **Permissions & Tenant Boundaries:** Role checks, auth guards, and multi-tenant scoping must never be bypassed.
   - **Analytics & Tracking:** Telemetry events, tracking tags, and user flow metrics must remain intact.
   - **Saved User Preferences:** LocalStorage keys, cookie names, and user settings must not be broken or wiped.
   - **SEO & Metadata:** Title tags, meta descriptions, OpenGraph tags, semantic headings (`<h1>`), and canonical URLs must be preserved.
2. **Regression Testing & Browser Checks:**
   - Add focused unit or component tests if an important refactored component lacked coverage.
   - Compare affected screens against the pre-refactoring baseline screenshots.
   - Check the browser console for new warnings, unhandled promise rejections, or hydration errors.
3. **Never Weaken Verification:**
   - Do NOT weaken tests, suppress lint rules, or delete test assertions merely to make verification pass.
   - Fix the implementation so that tests pass truthfully.
4. **Performance Verification:**
   - When claiming performance improvements, measure before and after (bundle size via `npm run build`, render count, or lighthouse scores).

---

## 6. Documenting Removals & Changes in the Report

All refactoring and cleanup actions must be recorded for the final deliverable report:
- **What became simpler and why:** Document the architectural improvements and clarity gained.
- **Significant code and dependencies removed:** Provide the list with concrete evidence (zero references across all 7 dimensions).
- **Verification performed:** Report test suite results, build outcomes, and browser verification findings.
- **Remaining verification gaps:** Note any third-party services, sandboxes, or credentials that were unavailable.
