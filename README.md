# Product Template

A reusable scaffold for spinning up a **new product** with the same documentation
structure, conventions, and agent guardrails that power ViaSocket Mission Control.

The goal: a new team should be able to copy this folder, do a find-and-replace on the
placeholders, fill in the sections, and immediately have a docs-driven codebase that
AI agents and humans can both navigate.

## What's in here

```
product-template/
├── README.md              # you are here
├── AGENTS.md              # common, product-agnostic agent guardrails (copy to repo root)
└── docs/
    ├── AGENTS.md          # how to write & maintain the docs (project-specific rules go here)
    ├── ARCHITECTURE.md    # high-level system architecture template
    ├── 00..24-*.md        # the numbered product/engineering guide set (one concern each)
    ├── api/_TEMPLATE.md            # one file per API domain
    ├── database/_TEMPLATE.md       # entities + relationships per data store
    ├── modules/_TEMPLATE.md        # one file per product module/feature area
    ├── ui/_TEMPLATE.md             # one file per shared/reusable component
    ├── current-infrastructure/_TEMPLATE.md  # one file per backend system you integrate
    ├── plans/_TEMPLATE.md          # dated implementation plans
    └── brainstorms/_TEMPLATE.md    # dated requirement/brainstorm docs
```

## How to use it

1. **Copy the folder** into your new product repo as `docs/` and copy `AGENTS.md` to the repo root.
   ```bash
   cp -R product-template/docs ../my-new-product/docs
   cp product-template/AGENTS.md ../my-new-product/AGENTS.md
   echo "@AGENTS.md" > ../my-new-product/CLAUDE.md
   ```
2. **Replace the placeholders.** Every template uses `{{DOUBLE_BRACE}}` tokens and
   `<!-- fill: ... -->` hints. Search for `{{` and resolve each one. Common tokens:
   - `{{PRODUCT_NAME}}` — human name of the product
   - `{{PRODUCT_SLUG}}` — repo/package slug
   - `{{ONE_LINE_SUMMARY}}` — the elevator pitch
   - `{{FRAMEWORK}}`, `{{LANGUAGE}}`, `{{STYLING}}`, `{{DB}}` — tech-stack choices
3. **Delete what you don't need.** Not every product has feature flags or notifications.
   Delete the file rather than leaving a stub — but renumber consciously.
4. **Rename `_TEMPLATE.md` files.** In `api/`, `modules/`, `ui/`, etc., copy the
   `_TEMPLATE.md` once per real thing (`api/orders.md`, `modules/01-checkout.md`) and
   keep the `_TEMPLATE.md` around as the pattern to clone.
5. **Fill `docs/AGENTS.md` last.** That file is where product-specific hard rules live
   (ID mapping, server/client boundaries, degradation policy). It is the single most
   important file for keeping agents on the rails.

## The doc numbering convention

The `00–24` guides are ordered from **product** → **architecture** → **engineering
practice**. Keep the numbers stable so links and muscle memory survive across products:

| Range | Concern |
|---|---|
| 00–05 | Product: overview, vision, goals, personas, journeys, navigation |
| 06–08 | Shape: tech stack, system architecture, folder structure |
| 09–14 | Engineering: coding, design system, state, API, security, performance |
| 15–20 | Operate: environment, analytics, notifications, error handling, testing, deployment |
| 21–24 | Govern: roadmap, definition of done, git workflow, feature flags |

## Golden rule

**The docs are the source of truth.** When code and docs disagree, that's a bug in one
of them. Every contract change ships with its doc change in the same commit.
