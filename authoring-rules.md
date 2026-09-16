# Authoring rules — the style contract

Read this in Phase 5, before writing the first doc file. These conventions are what make
the generated set feel like it was written by the team rather than by a generator.

## Contents

- [Evidence discipline](#evidence-discipline)
- [Marking what you couldn't determine](#marking-what-you-couldnt-determine)
- [Placeholders and fill hints](#placeholders-and-fill-hints)
- [Citing code](#citing-code)
- [Confidence language](#confidence-language)
- [Tone and density](#tone-and-density)
- [Tables, diagrams and code blocks](#tables-diagrams-and-code-blocks)
- [Cross-linking](#cross-linking)
- [Naming and numbering](#naming-and-numbering)
- [Refreshing existing docs](#refreshing-existing-docs)
- [The final summary](#the-final-summary)

## Evidence discipline

Every factual sentence maps to a row in your evidence ledger. Before writing a sentence,
ask which file you read to learn it. If the answer is "it's how these projects usually
work," that sentence is invention — either go read the file or mark it unknown.

Three specific traps:

- **Plausible completion.** A project with `/api/tenants` and `/api/rooms` probably has
  `/api/leases`. Probably isn't evidence. Document the routes that exist.
- **Convention assumed as fact.** Django REST routers *usually* expose six endpoints, but
  `http_method_names` or a read-only viewset changes that. Read the viewset.
- **Template text left standing as a claim.** The templates contain example prose (the ten
  rules, "Mock-first V1 → real backend integration", `{{ID_A}} → Proxy company.id`). That
  text is illustrative. If you leave it in place it reads as a claim about this project.
  Either replace it with the project's reality or mark it.

## Marking what you couldn't determine

Use a GitHub-flavored callout so it renders visibly and greps easily:

```markdown
> [!TODO]
> Not determinable from the repository — <what you looked for and where>. Needs a human.
```

Good markers name the evidence that was missing, because that tells the human what to
supply:

```markdown
> [!TODO]
> Not determinable from the repository — no CI config found under `.github/workflows/`,
> `.gitlab-ci.yml`, or `Jenkinsfile`, and no branch protection settings in the repo.
> Needs a human.
```

```markdown
> [!TODO]
> Performance budgets are a product decision and aren't expressed anywhere in the code.
> The observed mitigations are documented above; the targets need a human.
```

Weak markers to avoid: a bare `TODO`, `> [!TODO] TBD`, or a marker that restates the
section heading. They tell the reader nothing they didn't already see from the empty
section.

Put the marker **immediately under the heading it applies to**, not in a lump at the end of
the file, so a reader scanning a section knows at that moment whether to trust it.

Where a section is *partly* answerable, write what you know and scope the marker to the
gap. Half-known is the normal case and is much more useful than an all-or-nothing stub.

## Placeholders and fill hints

The templates use `{{DOUBLE_BRACE}}` tokens and `<!-- fill: ... -->` hints.

- **Resolve every one you have evidence for.** Replace the token with the real value; delete
  the `<!-- fill: -->` hint and write the content it asked for.
- **Leave the rest verbatim and add a `[!TODO]` callout.** Keeping the token means
  `grep -r '{{' docs/` still enumerates every open item, which is the workflow the
  template's README describes. The callout explains why it's still open.
- Never delete an unresolved token without marking it — that hides the gap.
- Never invent a value to make a token go away. `{{CHART_LIB}}` with no charting dependency
  should stay a token with a note that the project has no charting library, or the row
  should be dropped from the table if the concern doesn't apply at all.

A table row for a concern the project genuinely doesn't have is better deleted than filled
with a placeholder — but say so in your final summary so the user knows the row is gone.

## Citing code

- Paths are **relative to the project root**, in backticks:
  `` `backend/api/views.py` ``, `` `src/components/ui/DataTable.jsx` ``.
- Never use absolute local paths, OS-specific separators, or a path that exists only in
  your working copy. A reader on another machine must be able to open what you cite.
- Add line numbers for specific claims: `` `api/views.py:412-438` ``. Skip them for
  whole-file references, since line numbers rot.
- Name real symbols — class, function, and setting names exactly as spelled in the code.
  A doc that says `TenantViewSet` when the class is `TenantsViewSet` fails its one job.
- Quote short code fragments (a settings dict, a serializer's `fields` list) rather than
  paraphrasing a contract. Two lines of real code beats a sentence about them.

## Confidence language

Three registers, used deliberately:

| Register | Use for | Phrasing |
|---|---|---|
| Observed | What the code does | "`POST /api/payments/` creates a `RentPayment` and recalculates the lease balance (`api/views.py:512`)." |
| Inferred | Pattern read from structure | "Appears to follow a thin-client pattern: all business logic sits in serializers and viewsets (inferred from `src/api/*.js` containing only HTTP calls)." |
| Unknown | Not in the repo | A `[!TODO]` callout. |

Never dress inference as observation, and don't hedge observations — "the endpoint may
create a payment" when you've read the code that creates it is just as unhelpful as a
false claim. Read it, then state it.

## Tone and density

Match the templates: short, imperative, scannable. Present tense for what the code does.
No marketing language, no filler ("this important file describes..."), no restating the
heading in the first sentence.

The templates are terse on purpose — an agent reads these before every task, so length has
a real cost. Aim for the shortest version that a new engineer could act on. If a section
runs past ~15 lines of prose, it probably wants a table or belongs in a subfolder doc.

## Tables, diagrams and code blocks

- Keep every table's column headers exactly as the template ships them. Someone
  else's tooling and muscle memory depend on those columns.
- Where a template supplies a mermaid diagram, keep mermaid — don't switch to ASCII. Edit
  the nodes to the real systems and keep the graph small enough to read (roughly under a
  dozen nodes); push detail into `current-infrastructure/`.
- Code blocks need a language tag (` ```ts `, ` ```python `, ` ```bash `).
- Response-shape blocks should show the real field names and types with nullability, and
  keep the template's habit of commenting *why* a field can be null.

## Cross-linking

Use relative markdown links exactly as the templates do:
`[09-coding-guidelines.md](09-coding-guidelines.md)` from within `docs/`,
`[../22-definition-of-done.md](../22-definition-of-done.md)` from a subfolder.

Every link must resolve to a file you actually created. A link to a Tier B doc you skipped
is a broken promise — `verify_docs.py` catches these, so fix them rather than shipping
them. When you skip a file that a template links to, either remove the link or replace it
with a one-line inline note.

Link *down* the hierarchy (overview → detail), and from detail back up only where the
template already does it.

## Naming and numbering

- Numbered guides keep their exact filenames: `00-project-overview.md` through
  `24-feature-flags.md`. Don't renumber to close gaps.
- `modules/`: `NN-slug.md` starting at `01`, lowercase, hyphenated.
- `api/`: `<domain>.md`, lowercase, plural where the resource is plural
  (`payments.md`), matching the route path.
- `database/`: `entities.md` and `relationships.md`, or `<store>.md` per store.
- `ui/`: mirror the component's source location where it helps
  (`ui/shared/data-table.md`), lowercase-hyphenated even when the component is PascalCase.
- `current-infrastructure/`: `<system>.md`, lowercase (`postgres.md`, `redis.md`).
- `plans/`: `YYYY-MM-DD-NNN-<type>-<slug>-plan.md` where type is a conventional-commit
  type (`feat`, `fix`, `chore`).
- `brainstorms/`: `YYYY-MM-DD-<slug>-requirements.md`.
- Keep each subfolder's `_TEMPLATE.md` — it is the pattern for the next clone.

## Refreshing existing docs

When `docs/` already exists, you are correcting a record someone else wrote, so the
default is conservative:

- Read every existing file before editing anything.
- Preserve human-written prose — especially Tier C content (vision, goals, personas) and
  any rationale. You cannot regenerate those, so losing them is unrecoverable.
- Fix only what the code contradicts, and say what you changed and why.
- Add newly discovered facts to the file that owns that concern.
- When code and docs disagree, the docs are wrong about the present but may record real
  intent. Update the description to match the code and note the discrepancy — don't silently
  delete the old claim, because the divergence itself is often the bug worth finding.
- Don't reformat, renumber, or restructure files you weren't asked to change. A diff full
  of cosmetic churn hides the substantive corrections.

## The final summary

End your run with a short report, not a wall of text:

1. **Created** — the file list, grouped as in the plan.
2. **Skipped and why** — the Tier B/C files you didn't create, one line each. This is how
   the user learns the project has no analytics rather than that you forgot.
3. **Open TODOs** — every `[!TODO]` you left, grouped by file. Frequently the most useful
   part of the deliverable: it's a precise list of what only a human can answer.
4. **Findings** — anything the analysis surfaced that the user should know: a committed
   secret, two libraries for one concern, a client calling a nonexistent endpoint, models
   that disagree with migrations. Keep it factual and short; recommendations are separate
   work.
