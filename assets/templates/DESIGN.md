---
covers: [{{components_dir}}, {{styles_dir}}, {{tailwind_or_theme_configs}}]
verified_at: {{HEAD_SHORT}}
verified_on: {{TODAY}}
---
# Design System & UI Standards

<!-- fill: Overview of the UI design foundation, aesthetic goals, and styling framework (e.g. Tailwind CSS, CSS Modules, Radix UI primitives, shadcn/ui). -->

## Visual & Interaction Principles

<!-- fill: 3-5 core visual and interaction guidelines. -->
1. **Design Quality Bar:** Rich, state-of-the-art aesthetics. Cohesive palette, curated typography, subtle micro-interactions, zero generic default browser controls.
2. **Predictable Feedback:** Every interactive element must have active, hover, focused, and disabled states. Loading states use skeletons or spinners.
3. **Information Density:** Clean white space, structured cards, clear visual hierarchy.

## Design Tokens & Styling Primitives

<!-- fill: Where tokens are defined and how to reference them. -->
- **Token Source File:** `{{tailwind.config.js / globals.css / theme.ts}}`
- **Colors:**
  - Primary / Brand: `{{var(--primary) / bg-primary-600}}`
  - Neutral / Surfaces: `{{var(--background) / bg-slate-900}}`
  - Feedback: Success `{{var(--success)}}`, Error `{{var(--destructive)}}`, Warning `{{var(--warning)}}`
- **Typography:**
  - Font Families: Body `{{Inter / system}}`, Headings `{{Outfit / Inter}}`, Code `{{JetBrains Mono / monospace}}`
  - Hierarchy Scale: Display (`{{text-4xl}}`), H1 (`{{text-3xl font-bold}}`), H2 (`{{text-2xl font-semibold}}`), Body (`{{text-base}}`), Caption (`{{text-xs text-muted}}`)
- **Spacing & Elevation:** Consistent 4px/8px grid (`{{p-2, p-4, p-6}}`), shadows (`{{shadow-sm, shadow-md, shadow-xl}}`).
- **Dark Mode:** Mechanism (`{{class="dark" on <html> or data-theme}}`), default state, toggle handler in `{{src/theme/...}}`.

## Reusable Component Catalog

<!-- fill: Catalog of shared, reusable primitives. Agents must reuse these rather than writing ad-hoc buttons or modals. -->
| Component | File Path | Purpose & When to Use | Key Props / Variants |
|---|---|---|---|
| `Button` | `{{src/components/ui/Button.tsx}}` | All click triggers and CTA actions | `variant="primary|secondary|ghost|danger"`, `size="sm|md|lg"`, `isLoading` |
| `Modal` / `Dialog` | `{{src/components/ui/Modal.tsx}}` | Focused user confirmations or alerts | `isOpen`, `onClose`, `title`, `children` |
| `Input` / `TextField` | `{{src/components/ui/Input.tsx}}` | Form inputs with validation feedback | `label`, `error`, `helperText`, `icon` |
| `Card` | `{{src/components/ui/Card.tsx}}` | Content container with rounded border | `variant="elevated|outlined"`, `padding` |
| `Toast` / `Alert` | `{{src/components/ui/Toast.tsx}}` | Asynchronous feedback and status banners | `type="info|success|warning|error"`, `message` |

## Responsive Behavior & Breakpoints

- **Breakpoints:**
  - Mobile: `< 640px` (`sm`) — Single column, collapsible navigation drawer, tap-friendly touch targets (min 44px).
  - Tablet: `640px - 1024px` (`md`) — Two column layouts, condensed sidebars.
  - Desktop: `> 1024px` (`lg` / `xl`) — Full multi-pane layouts, sticky sidebars, high data density.
- **Mobile Patterns:** Bottom navigation, modal sheets, drawer menus.

## Accessibility (A11y) Standards

- **Semantic HTML:** Use native `<button>`, `<nav>`, `<main>`, `<header>`, `<footer>`, `<dialog>` elements.
- **Keyboard Navigation:** Full tab-order support, visible focus rings (`{{focus-visible:ring-2}}`), `Escape` closes modals and dropdowns.
- **ARIA Attributes:** `aria-label`, `aria-expanded`, `aria-hidden` properly toggled on custom controls.
- **Color Contrast:** All text must meet WCAG AA minimum 4.5:1 contrast against its background.

## Website Messaging & Copy Guidelines

<!-- fill: Brand voice, tone, and conventions for microcopy. -->
- **Voice & Tone:** Confident, concise, helpful, and transparent. Never robotic or verbose.
- **Error Messages:** Action-oriented microcopy (explain what happened and how to fix it, e.g. "Password must be at least 8 characters").
- **Empty States:** Provide an illustration or icon, friendly description, and a primary CTA to get started.

## SEO & Metadata Expectations

<!-- fill: SEO standards for pages and marketing routes. -->
- **Document Titles:** Descriptive format `{{Page Name}} | {{Product Name}}`.
- **Meta Descriptions:** Unique, engaging summary per route (140-160 characters).
- **Heading Hierarchy:** Strictly one `<h1>` per page view, followed by proper semantic `<h2>` and `<h3>` tags.
- **Social & OpenGraph:** `og:title`, `og:description`, `og:image`, `twitter:card` configured in root layout or page head.
- **Canonical URLs:** Configured in `{{layout.tsx or head metadata}}`.
