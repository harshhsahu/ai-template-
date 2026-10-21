# Writing Rules for AI-First Frontend Documentation

The reader is a coding agent about to analyze, evaluate, or change this repository. It already understands programming languages, frontend frameworks, and general software engineering principles. It does NOT understand *this* product: why it exists, whom it serves, where boundaries lie, how state flows, which conventions are strictly enforced, and which mistakes were already made.

Every line written must close one of those gaps.

---

## 1. Understand & Preserve Product Purpose

Never invent product vision or assume that everything currently in the code was intentional.

- **Recover from trustworthy sources:** Gather vision from READMEs, PRDs, landing pages, marketing copy, founder notes, package descriptions, and git history.
- **Distinguish four distinct statuses:**
  1. *Approved Direction:* Confirmed strategic goals and product boundaries.
  2. *Current Implementation:* What is actually running in the codebase today.
  3. *Proposals:* Feature ideas, draft PRs, or upcoming roadmaps under consideration.
  4. *Unknowns:* Ambiguities or code without clear intent. Mark these explicitly in `docs/OPEN_QUESTIONS.md`.
- **Evaluate requests against product context:**
  - *Improve unclear requests:* Clarify user problem and propose solutions aligned with vision before touching code.
  - *Explain conflicts & decline contradictions:* If a request violates an approved principle or non-goal, explain why and recommend declining.
  - *Explicit direction changes:* If the user deliberately changes direction, make that decision explicit and update `docs/VISION.md`.
- **Unavailable backend capabilities:**
  - If a frontend feature requires backend APIs that do not exist, clearly specify the required contract in `docs/CONTRACTS.md`.
  - **NEVER fabricate working integrations or mock endpoints** that deceive future agents or users into believing the backend is complete.

---

## 2. Evidence Only

Every file path, symbol, hook, component, route, design token, env var, or storage key you cite must exist in the code at the verified commit.

- Read the source code before describing it. Never document from memory or unverified assumptions.
- If you cannot find evidence in the code or commit history, do NOT guess. Record it as an open question in `docs/OPEN_QUESTIONS.md`.
- **Bad (invented):** "`useAuth()` automatically syncs with `sessionWorker.ts`." (Neither hook nor worker exists).
- **Good (evidenced):** "`src/auth/useSession.ts:useSession` reads the JWT from `localStorage` under `TOKEN_KEY` and sets the `Authorization` header in `src/api/client.ts:apiClient`."

---

## 3. Verifier-Checkable Notation

`scripts/verify_docs.py` parses everything inside single backticks outside fenced code blocks. Use these exact citation forms:

| What you mean | How to write it |
|---|---|
| A file or directory | `` `src/components/ui/` `` (always repo-root relative) |
| A function / class / component | `` `src/components/Button.tsx:Button` `` |
| A hook / exported symbol | `` `src/hooks/useUser.ts:useUser` `` |
| A specific line or range | `` `src/config.ts:42` `` or `` `src/config.ts:40-55` `` (use sparingly; line numbers drift) |
| An identifier in context | `` `formatCurrency` `` |
| An env var | `` `VITE_API_BASE_URL` `` |
| An HTTP route | `` `POST /api/v1/auth/login` `` |
| A link to another doc | `[architecture](ARCHITECTURE.md#layers)` |

- Prefer `path:symbol` over `path:line`. Symbol names survive code edits; line numbers drift rapidly.
- Use fenced code blocks (````json ... ```` or ````typescript ... ````) for sample payloads, shapes, commands, and schemas. Verifiers skip fenced code blocks.
- If mentioning an external symbol or intentional absence that is not in the repository, add `<!-- verify:ignore -->` at the end of the line, or wrap the block in `<!-- verify:ignore-start -->` ... `<!-- verify:ignore-end -->`.

---

## 4. One Place per Fact

When the same list or table is repeated across multiple documents, they inevitably drift out of sync.

- **Env vars & setup:** Owned by `docs/DEVELOPMENT.md`.
- **API routes & schemas:** Owned by `docs/CONTRACTS.md`.
- **System modules & mental model:** Owned by `docs/ARCHITECTURE.md`.
- **User journeys & error recovery:** Owned by `docs/FLOWS.md`.
- **Tokens & reusable components:** Owned by `docs/DESIGN.md`.
- **Strategic purpose & ICP:** Owned by `docs/VISION.md`.
- **Decisions & rejected alternatives:** Owned by `docs/DECISIONS.md`.
- **Unknowns & ambiguities:** Owned by `docs/OPEN_QUESTIONS.md`.
- **`AGENTS.md` summarizes and links:** It provides a curated reading order and rules; it never duplicates large tables.

---

## 5. Project-Specific Only

Omit generic programming rules that any capable AI agent already knows. Ask yourself: *Would an agent get this wrong in this specific codebase without being told?*

- **Cut:** "Write clean code." "Handle errors gracefully." "Use semantic tags." "Follow DRY."
- **Keep:** "Never mutate `sessionStore` directly; always dispatch via `src/stores/auth.ts:updateSession` to trigger token refresh."
- **Keep:** "Modals must use `src/components/ui/Modal.tsx` and never raw `<dialog>`: raw dialogs fail our screen reader focus trap."

---

## 6. Capture the "Why" & Rejected Alternatives

A rule without a documented reason is frequently "refactored away" or broken by subsequent agents.

- Look for the rationale in commit messages (`git log -S'<symbol>'`, `git log --format=%B -n 1 <sha>`), PR comments, and code remarks.
- State the reason succinctly next to the rule.
- Document rejected alternatives and what failed when they were tried (e.g. "We previously used Redux for server state, which caused stale caching issues; migrated to TanStack Query in commit `abc123`").
- If no reason is recorded in git history or comments, document the current convention and note the missing rationale in `docs/OPEN_QUESTIONS.md`.

---

## 7. Concrete Shapes & Focused Diagrams Over Verbose Prose

Agents process structural representations far better than walls of text:
- Show real payload shapes with key fields marked optional or required.
- Use compact Mermaid diagrams (flowcharts, sequence diagrams) with ≤12 nodes.
- Do not draw exhaustive diagrams of every trivial utility function; diagram only the core request flows, routing branches, and state synchronization boundaries.

---

## 8. Footguns as Explicit Callouts

Highlight anything that causes silent failures, ordering dependency bugs, or destructive operations:

```md
> [!WARNING]
> `src/api/client.ts` intercepts 401s and retries once. If the refresh request itself returns 401, you must clear `localStorage` or an infinite redirect loop occurs.
```

Common frontend footguns:
- Missing dependency arrays in hooks causing stale closures.
- Mutating React state objects directly.
- Server vs client component hydration mismatches (Next.js).
- Unescaped user HTML or dangerous CSS injection.
- Leaking private environment variables to client bundles (`NEXT_PUBLIC_` / `VITE_`).

---

## 9. Size Budgets & Frontmatter Standard

- `AGENTS.md`: Strict limit of ≤150 lines.
- All other `docs/*.md`: Keep under ≤450 lines. If a document grows larger, extract focused sub-flows or scoped module docs.
- **Frontmatter is mandatory** on tracked documents:
  ```yaml
  ---
  covers: ["src/components/ui/**", "src/styles/**"]
  verified_at: a1b2c3d
  verified_on: 2026-10-21
  ---
  ```
  Strategic docs (`docs/VISION.md`, `docs/DECISIONS.md`, `docs/OPEN_QUESTIONS.md`) can use `covers: ["*"]` or omit `covers`.
