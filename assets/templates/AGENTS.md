# {{PROJECT_NAME}}

<!-- fill: 2-3 sentences. What this product is, whom it serves, what problems it solves, and its high-level technical shape. No marketing fluff. -->

## Commands

<!-- fill: exact, verified commands. Drop rows that do not exist (e.g. no tests yet). -->
| Task | Command |
|---|---|
| Install dependencies | `{{install_cmd}}` |
| Run dev server | `{{dev_cmd}}` |
| Build for production | `{{build_cmd}}` |
| Type check | `{{typecheck_cmd}}` |
| Lint / format | `{{lint_cmd}}` |
| Run unit / integration tests | `{{test_cmd}}` |
| Run E2E / browser tests | `{{e2e_cmd}}` |
| Preview production build | `{{preview_cmd}}` |

## Reading Order Before You Change Code

Always check documentation before planning or modifying code:
1. **Product Purpose & Boundaries:** [docs/VISION.md](docs/VISION.md) — Evaluate requests against approved direction; never invent vision or fabricate backend integrations.
2. **Mental Model & Data Flow:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — Understand module boundaries, state ownership, rendering, and sources of truth.
3. **User Journey Context:** [docs/FLOWS.md](docs/FLOWS.md) — Check user paths, permissions, alternative branches, and failure recovery for affected features.
4. **Visual & UI Standards:** [docs/DESIGN.md](docs/DESIGN.md) — Component reusability, design tokens, responsiveness, accessibility, and messaging.
5. **API & Persistence Types:** [docs/CONTRACTS.md](docs/CONTRACTS.md) — Authoritative schemas, auth assumptions, analytics events, and data relationships.
6. **Environment & Verification:** [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) — Setup details, test data guidance, and how to verify your changes.
7. **Lessons & Past Choices:** [docs/DECISIONS.md](docs/DECISIONS.md) — Rationale behind architectural choices and superseded approaches.
8. **Known Ambiguities:** [docs/OPEN_QUESTIONS.md](docs/OPEN_QUESTIONS.md) — Unresolved dependencies, technical debt, and pending decisions.

## Project Rules & Boundaries

<!-- fill: 10–15 project-specific rules an agent would break without being told.
     Each rule: imperative sentence + concrete "because" / rationale or link to evidence.
     Numbered so code reviews can cite "breaks Rule 3". No generic advice like "write clean code". -->
1. {{Rule}} — {{because / link}}.

## Where Things Are

<!-- fill: 6–10 bullets mapping the top-level directories that matter and what lives there. Link, do not copy, tables. -->
- `{{path}}/` — {{role and responsibility}}

## PR & Deployment Flow

<!-- fill: the exact flow for building a PR and deploying to production.
     Always ask the human for their specific pipeline if not documented in CI workflows: e.g. feature -> PR -> testing -> stag -> main. -->
- **Branching Strategy:** `feature/<name>` or `fix/<name>` branched from `{{main / develop}}`.
- **Pre-PR Quality Gate:** Run `{{test_cmd}}`, `{{typecheck_cmd}}`, `{{lint_cmd}}`, `{{build_cmd}}`, and `python3 scripts/verify_docs.py .`.
- **Deployment Pipeline:** `{{testing -> stag -> main}}`
  1. **PR & Automated Checks:** Open PR against `{{stag / main}}`. CI runs lint, typecheck, tests, and deploys preview.
  2. **Testing Environment:** Merge to test branch triggers deployment to `{{testing / QA}}` for automated/manual acceptance.
  3. **Staging Environment (`stag`):** Promotion to staging for pre-release validation and stakeholder sign-off.
  4. **Production Deployment (`main`):** Merge to `main` deploys to production following required approvals.

## Verification & Knowledge Maintenance Expectations

- **Establish baseline before changes:** Run existing checks (`{{test_cmd}}`, `{{build_cmd}}`) and note known failures before editing.
- **Dependable application invariants:** Preserve existing routes, UI appearance, permissions, tenant boundaries, analytics, SEO metadata, and saved user preferences.
- **Evidence-based cleanup:** Never remove code merely because product rationale is unclear. Check runtime registration, dynamic imports, routing, feature flags, CSS references, build configs, and external consumers before removing.
- **Maintain project docs:** When changing behavior, schemas, routes, or design tokens, update the corresponding `docs/*.md` files in the same commit.
- **Run doc verification:** Run `python3 scripts/verify_docs.py .` and ensure 0 errors before submitting work.
