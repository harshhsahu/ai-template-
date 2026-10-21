---
verified_at: {{HEAD_SHORT}}
verified_on: {{TODAY}}
---
# Open Questions & Known Ambiguities

<!-- fill: Track genuine uncertainties, conflicting evidence, known limitations, and unresolved dependencies.
     Distinguish verified facts from inference.
     RULE: Never invent answers to product vision or architectural intent. Record unknowns here with affected code and what would resolve each issue. -->

## Active Questions Table

| ID | Topic / Question | Affected Code | Conflicting Evidence / Current Status | What Would Resolve It |
|---|---|---|---|---|
| Q-001 | {{Short topic}} | `{{src/path/file.ts:symbol}}` | {{Evidence A vs Evidence B}} | {{Human confirmation or backend spec}} |

---

## Detailed Issue Records

### Q-001: {{Question Title: e.g. Intentionality of Dual Auth Tokens in Session Handler}}

- **The Ambiguity:**
  {{Describe the contradiction or missing rationale clearly. E.g., "`src/auth/session.ts` checks for both `token` and `legacy_jwt`, but nowhere in the repository is `legacy_jwt` written or refreshed."}}
- **Affected Code & Paths:**
  - `{{src/auth/session.ts:checkSession}}`
  - `{{src/api/client.ts:injectAuth}}`
- **Current Evidence:**
  - `git log` shows `legacy_jwt` was introduced in commit `{{sha}}` during migration from Service X.
  - No active backend endpoint consumes or returns `legacy_jwt`.
- **Potential Risk:**
  - If removed without verification, users on older sessions might be logged out, OR it might be completely dead code.
- **What Resolves This:**
  - Human confirmation from backend team whether `legacy_jwt` is still accepted by any production microservice.
  - Safe removal path: Deprecate over 1 release cycle with telemetry logging before full deletion.

---

## Known Technical Limitations & Verification Gaps

<!-- fill: Record unavailable services, credentials, or tooling that prevented 100% verification during preparation. -->
- **Unavailable Service / Tooling:**
  - Service: `{{e.g. Payment Gateway Webhook Sandbox / Staging Auth Provider}}`
  - Verification Gap: `{{e.g. End-to-end payment confirmation flow could not be verified in live browser without sandbox credentials}}`
  - Mitigation / Safe Handling: `{{e.g. Unit tests mocked; changes paused on payment webhook handlers until credentials provided}}`
