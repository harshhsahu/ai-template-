---
covers: ["*"]
verified_at: {{HEAD_SHORT}}
verified_on: {{TODAY}}
---
# Product Vision & Strategic Direction

<!-- fill: 2-3 sentences summarizing the product's ultimate purpose and reason for being. -->

## Authoritative Sources & Status

<!-- fill: List trusted sources where product context was recovered (e.g. README, PRD, founder notes, package.json).
     Clearly distinguish what is approved direction vs current implementation vs proposals vs unknowns. -->
- **Approved Direction:** {{Document or explicit executive direction establishing the intended product vision}}
- **Current Implementation:** {{What is currently shipped in code as of verified_at}}
- **Proposals & Roadmaps:** {{Known planned features or future initiatives currently under discussion}}
- **Unknowns & Ambiguities:** See [docs/OPEN_QUESTIONS.md](OPEN_QUESTIONS.md)

## Target Audience & Ideal Customer Profile (ICP)

<!-- fill: Whom does this product serve? Personas, user roles, skills, and organizational contexts. -->
- **Primary Persona:** {{Role, workflow, key responsibilities, technical level}}
- **Secondary Personas:** {{Other roles who touch the system, e.g. admins, auditors, collaborators}}

## Problems Solved & Value Proposition

<!-- fill: What critical customer friction, pain points, or inefficiencies does this product solve? -->
| Customer Problem | How We Solve It | Unique Value / Differentiator |
|---|---|---|
| {{Problem description}} | {{Feature / workflow solution}} | {{Why our approach is superior}} |

## Core Principles & Design Philosophy

<!-- fill: 4-6 guiding principles that govern UX, architecture, and feature trade-offs. -->
1. **{{Principle 1}}:** {{Explanation of trade-off: e.g. "Clarity over cleverness: prefer explicit controls to magical hidden automation."}}
2. **{{Principle 2}}:** {{Explanation}}

## Strategic Priorities & Success Measures

- **Top Priorities:**
  1. {{Current focus area}}
  2. {{Secondary focus area}}
- **Key Success Metrics:**
  - {{Metric 1: e.g., Task completion time < 30s}}
  - {{Metric 2: e.g., Zero-churn onboarding conversion}}

## Boundaries & Non-Goals

<!-- fill: What is explicitly outside the product scope? What will we NOT build? -->
- **Explicit Non-Goal:** {{What we do not do, e.g., "Not a general-purpose CMS; strictly optimized for checkout flows."}}
- **Anti-Patterns:** {{Behaviors or patterns that violate the product vision}}

## How Future Agents Must Evaluate Requests

When evaluating any user or feature request, follow this protocol:
1. **Align with Approved Direction:** Compare the request against the principles, ICP, and non-goals above.
2. **Improve Unclear Requests:** If a request is ambiguous or underspecified, clarify the problem it solves and suggest improvements aligned with this vision before writing code.
3. **Flag Conflicts:** If a request directly contradicts an approved principle or non-goal, explain the conflict clearly and recommend declining or modifying the change.
4. **Explicit Direction Changes:** If the user intentionally wishes to change product direction, make that decision explicit, confirm the strategic shift, and update this document alongside code changes.
5. **Contract Boundaries (No Fabricated Integrations):** If a requested frontend feature requires unavailable backend capabilities, describe the required backend API or contract clearly in [docs/CONTRACTS.md](CONTRACTS.md). **Never fabricate mock endpoints or fake working integrations that give a false impression of backend readiness.**
