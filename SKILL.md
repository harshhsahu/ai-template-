---
name: project-documentation-generator
description: Generate a complete, evidence-based documentation set for any software project using the ViaSocket/Superheroes docs template structure (AGENTS.md + docs/00-24 numbered guides + api/, database/, modules/, ui/, current-infrastructure/ clones). Use this skill whenever the user points at a project folder, repository, zip, or source tree and asks to document it, generate docs, write an AGENTS.md or CLAUDE.md, produce architecture docs, onboard an AI agent to a codebase, backfill missing documentation, or refresh docs that have drifted from the code — even if they don't name the template by name. Also use it when the user asks "what does this codebase do" in a way that implies a written deliverable, or asks to document APIs, database schemas, modules, or components of an existing project.
---

# Project Documentation Generator

Turn a real codebase into a documentation set that matches a fixed house template — where
every sentence is traceable to code that actually exists.

Two failure modes destroy the value of generated docs, so guard against both:

1. **Invention.** A plausible-sounding endpoint that isn't in the code is worse than no
   docs at all, because a reader (human or agent) will trust it and build on it. The whole
   point of these docs is that the repo-root `AGENTS.md` tells the next agent "docs are the
   source of truth." A hallucinated doc poisons that contract.
2. **Stub sprawl.** Twenty-five files of `<!-- fill: -->` look like documentation and
   contain nothing. A reader can't tell "we don't do this" from "nobody wrote it down."

Everything below exists to keep those two out.

## Workflow

Work through these phases in order. Don't start writing docs before Phase 3 — the doc plan
is what keeps you from generating files you have no evidence for.

### Phase 1 — Locate and scope

Establish the project root (the directory holding the manifest: `package.json`,
`pyproject.toml`, `go.mod`, `pom.xml`, `Gemfile`, `composer.json`, `Cargo.toml`, `*.csproj`).
If the user handed you a zip, extract it first and find the real root inside — archives
usually add a wrapper directory.

Check whether `docs/` or `AGENTS.md` already exist. If they do, you are **refreshing**, not
creating: read what's there first, preserve human-written prose, and only correct what the
code contradicts. Silently overwriting someone's hand-written architecture notes is the
fastest way to lose their trust in this skill.

In a monorepo, ask which package to document, or document the whole workspace with one
`modules/` file per package — but say which you chose.

### Phase 2 — Survey, then read

Run the bundled survey script first. It is cheap, deterministic, and it saves you from
burning context on `ls` and `find` calls:

```bash
python3 <skill-dir>/scripts/survey_project.py <project-root> --out <scratch>/survey
```

It writes `survey.md` (read this) and `survey.json` (machine-readable), covering the
directory tree, file/language counts, detected manifests and dependencies, config files,
env var names, and candidate route/model/component/test/CI files.

The survey tells you *where to look*. It does not tell you what the code does. Now **read
the actual files** it flagged — route handlers, model/schema definitions, entry points,
config. `references/analysis-playbook.md` has the per-ecosystem search patterns for
finding routes, ORM models, components, auth middleware, external service clients, and CI
config. Read it before you start grepping; it will save you several passes.

As you read, build an **evidence ledger** at `<scratch>/evidence.md`:

```
| Claim | Source |
|---|---|
| Uses Next.js 15 App Router | package.json:14 ("next": "15.2.0"), app/layout.tsx exists |
| POST /api/orders creates an order | app/api/orders/route.ts:22-58 |
| `orders.org_id` is a logical ref to Proxy company.id | lib/server/orders.ts:41 comment |
```

This ledger is the mechanism that makes the no-invention rule enforceable rather than
aspirational. When you write a doc sentence, it comes from a ledger row. If you want to
write a sentence and there's no row, either go find the evidence or mark it unknown.

### Phase 3 — Build the doc plan and confirm it

Decide which files you will create, using the three tiers in
`references/doc-catalog.md` (read it now — it lists every template file, what it's for,
what code evidence feeds it, and the skip rule):

- **Tier A — always:** the spine an agent needs to navigate the repo at all.
- **Tier B — only with evidence:** created only if the code shows the concern exists.
  No analytics SDK anywhere → no `16-analytics.md`. Deleting the file is what the template
  itself instructs ("Delete this file if unused") and it's how a reader learns the project
  genuinely doesn't do that thing.
- **Tier C — human-owned:** product/business docs (vision, goals, personas, journeys,
  roadmap) that code cannot answer. Create these as the template stub plus a TODO only if
  the user wants the full set; default to skipping them and say so.

Show the user the planned file list before writing, grouped by tier, with one-line reasons
for notable inclusions and exclusions. This is a cheap checkpoint that catches
misunderstandings before you've written 20 files. If the session is unattended, state the
plan and proceed.

### Phase 4 — Scaffold from the bundled templates

Never retype a template from memory — the numbering, wording, and callout style are house
convention and small drifts accumulate. Copy them:

```bash
python3 <skill-dir>/scripts/scaffold_docs.py <project-root> \
  --files 00,06,07,08,09,12,13,15,18,19,20,22,23,ARCHITECTURE,AGENTS,ROOT_AGENTS \
  --domains api:orders,api:users \
  --modules 01-checkout \
  --infra postgres,redis \
  --ui shared/data-table \
  --database entities,relationships
```

Run it with `--dry-run` first if you want to see the resulting paths. It refuses to
clobber existing files unless you pass `--force`, and it always keeps each subfolder's
`_TEMPLATE.md` in place, since the template set treats those as the pattern to clone.

It also writes `CLAUDE.md` containing `@AGENTS.md` (the mirror the template's README
prescribes) unless one exists.

### Phase 5 — Fill each file from the ledger

Fill in this order, because later files reference earlier ones:
`00` → `06` → `08` → `ARCHITECTURE` → `07` → `database/` → `current-infrastructure/` →
`api/` → `ui/` → `modules/` → engineering docs (`09`–`14`, `18`–`20`, `22`–`24`) →
`docs/AGENTS.md` → root `AGENTS.md`.

Root `AGENTS.md` goes last on purpose: it is a digest of everything else, and the ten
rules have to reflect what you actually found (real ID types, the real degradation policy)
rather than the template's example text.

`references/authoring-rules.md` is the style contract — how to mark unknowns, how to cite
paths, how to keep files from duplicating each other, how to handle the `{{TOKEN}}`
placeholders. Read it before writing the first file.

The short version, because these four rules carry most of the weight:

- **Cite real paths.** Reference files as `app/api/orders/route.ts`, relative to the
  project root, so a reader can open them. Line ranges are welcome for specific claims.
- **Resolve every placeholder you have evidence for; leave the rest verbatim and mark
  them.** Keep the template's `{{TOKEN}}` / `<!-- fill: -->` where you couldn't determine
  the answer, and add a callout saying what you looked for:

  ```markdown
  > [!TODO]
  > Not determinable from the repository — no CI config found under `.github/workflows/`,
  > `.gitlab-ci.yml`, or `Jenkinsfile`. Needs a human.
  ```

  Keeping the placeholder means a `grep -r '{{' docs/` still finds every open item, which
  is exactly the workflow the template's README describes. The callout tells the human what
  evidence was missing so they know what to supply.
- **Separate observed from inferred.** State what the code does plainly. When you're
  reading intent rather than fact, say so: "Appears to follow a mock-first integration
  strategy (inferred from `lib/mock/` fixtures alongside live `app/api/**` routes)."
  Architecture *decisions* and their rationale are almost never in the code — record the
  observable structure, and leave the "why" as a TODO rather than inventing a rationale.
- **Say it once.** Each concern has exactly one home. The API response envelope lives in
  `12-api-guidelines.md`; a specific route's shape lives in `api/<domain>.md`. Elsewhere,
  link instead of restating, or the two copies will disagree within a month.

### Phase 6 — Verify before you hand it over

Run the checker, which catches the mechanical problems:

```bash
python3 <skill-dir>/scripts/verify_docs.py <project-root>
```

It reports unresolved `{{TOKEN}}`s and `<!-- fill: -->` hints that have no accompanying
TODO callout, broken relative links between docs, and file paths cited in the docs that
don't exist in the repo — that last one is the invention detector, so treat any hit as a
bug in the docs, not in the script.

Then do the pass a script can't: re-read each generated file and ask whether every factual
sentence has a ledger row behind it. Delete or mark anything that doesn't. Finally, tell
the user what you created, what you deliberately skipped and why, and the list of TODOs
they need to answer — that TODO list is often the most useful part of the deliverable.

## Reference files

Read these as you reach the phase that needs them; they're separate so this file stays
navigable.

| File | Read it when | What's in it |
|---|---|---|
| `references/doc-catalog.md` | Phase 3 | Every template file: purpose, required evidence, tier, skip rule, and which sibling docs it must link to instead of duplicating |
| `references/analysis-playbook.md` | Phase 2 | Per-ecosystem detection recipes (JS/TS, Python, Go, Java, Ruby, PHP, .NET) for stack, routes, ORM models, components, auth, external services, tests, CI, infra |
| `references/authoring-rules.md` | Phase 5 | The style contract: unknown markers, citation format, confidence language, anti-duplication map, numbering/naming conventions, dated plan/brainstorm filenames |

## Bundled assets and scripts

- `assets/templates/` — the documentation template set, verbatim. `AGENTS.md` for the repo
  root and `docs/` with the numbered guides plus the seven `_TEMPLATE.md` clones. This is
  the source of truth for structure; copy from it, don't reconstruct it.
- `scripts/survey_project.py` — deterministic project inventory and stack detection
  (Phase 2).
- `scripts/scaffold_docs.py` — copies selected templates into the target repo with the
  right names and numbering (Phase 4).
- `scripts/verify_docs.py` — post-generation checks for unmarked placeholders, broken
  doc links, and cited paths that don't exist (Phase 6).

All three scripts take `--help` and use only the Python standard library, so they run
anywhere Python 3.8+ is available.

## Scope boundaries

This skill documents what exists. It does not review code quality, propose refactors, fix
bugs, or write the product's business strategy. If the user wants those, do them as
separate work — mixing "here's what your code does" with "here's what I think you should
change" makes the docs unciteable, because a reader can no longer tell which statements
describe the repo.
