# Knowledge Maintenance & Update Mode

In 100% AI-driven development, knowledge maintenance is not a separate chore—it is an integral part of making any code change.
Whenever code behavior, visual design, contracts, or architecture change, the affected documents must be updated in the **same pull request / commit**.

---

## 1. Evaluating Incoming Requests Before Making Changes

Before writing or modifying code in response to a prompt or ticket, every AI agent must evaluate the request against canonical product knowledge:

1. **Check Against Vision ([docs/VISION.md](docs/VISION.md)):**
   - Does this request align with our product purpose, ICP, and core principles?
   - Does it violate any explicit non-goals?
   - If ambiguous or underspecified, improve the request: suggest the optimal design aligned with our vision before coding.
   - If it contradicts approved direction: explain the conflict clearly and recommend declining or revising the change.
   - If the user explicitly changes strategic direction: make that decision explicit and update `docs/VISION.md`.
2. **Check Against Architecture & State ([docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)):**
   - Which module or layer owns this change?
   - What state store or query cache is affected?
   - Does it respect module boundaries (presentation vs state vs API access vs domain rules)?
3. **Check Backend Contracts ([docs/CONTRACTS.md](docs/CONTRACTS.md)):**
   - Does the required backend API exist?
   - If not, specify the required contract in `docs/CONTRACTS.md`. **Never fabricate mock endpoints or fake working integrations.**

---

## 2. Maintaining a Concise Progress Record During Substantial Work

During multi-step refactoring, feature work, or large doc updates, maintain a concise progress record in your session scratchpad (`$WORK/progress.md` or PR description):
- **Current Step / Milestone:** What has been accomplished so far.
- **Pending Tasks:** The immediate next steps.
- **Decisions Made:** Key rationale for deviations from initial plan.
- **Verification Status:** Tests run, current pass/fail state.

This ensures another AI agent or human can resume work seamlessly without needing to reconstruct the entire conversation history.

---

## 3. Automated Drift Detection & Update Workflow

When refreshing or updating documentation after code modifications:

1. **Identify Changed Code & Stale Docs:**
   ```bash
   python3 "${SKILL_DIR}/scripts/affected_docs.py" . > "$WORK/affected.txt"
   python3 "${SKILL_DIR}/scripts/verify_docs.py" . > "$WORK/verify.txt"
   ```
   - `affected_docs.py`: Lists canonical docs whose `covers` globs matched modified files since their `verified_at` commit, plus uncovered code changes.
   - `verify_docs.py`: Validates all symbol citations, file links, routes, and env vars against current code.
2. **Narrow the Scope:**
   - If updating a specific area (e.g. `/ai-docs update auth`), target the relevant canonical docs (`docs/FLOWS.md`, `docs/CONTRACTS.md`) plus any doc reporting verification ERRORs.
3. **Update Affected Canonical Documents:**
   - Run an update agent per stale doc to review the diff (`git diff <verified_at> -- <files>`).
   - Outcome options:
     - **KEEP:** No claims affected; bump `verified_at` and `verified_on`.
     - **PATCH:** Update changed props, endpoints, env vars, or state flows.
     - **REWRITE <section>:** Rewrite a specific section if a subsystem was restructured.
   - Maintain the "why", warnings, and ADR references.
4. **Synchronize Cross-Cutting Changes:**
   - If routes or types changed: update `docs/CONTRACTS.md`.
   - If setup, scripts, or env vars changed: update `docs/DEVELOPMENT.md`.
   - If UI components, tokens, or styling changed: update `docs/DESIGN.md`.
   - If user flows or recovery branches changed: update `docs/FLOWS.md`.
   - If architectural patterns or modules changed: update `docs/ARCHITECTURE.md` and `docs/DECISIONS.md`.
   - Re-check `AGENTS.md`: Update rules or commands if any fact changed.
5. **Re-Verify Everything:**
   - Run `python3 "${SKILL_DIR}/scripts/verify_docs.py" .` until **0 errors**.
   - Bump `verified_at` to the new `HEAD_SHORT` and `verified_on` to today's date.
   - Update `last_run` in `docs/.ai-docs.json`.
6. **Report Summary:**
   - State which docs changed and what was updated.
   - Note any open questions or new decisions recorded.
   - Offer to commit the changes.
