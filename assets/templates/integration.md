---
covers: [{{client code}}]
verified_at: {{HEAD_SHORT}}
verified_on: {{TODAY}}
---
# {{System}}

<!-- fill: one line: what we use it for. -->

> [!WARNING]
> {{The #1 footgun with this system.}}

## Connection
- **Base URL / host:** `{{ENV_VAR}}` (default {{x}})
- **Client:** `{{path:symbol}}` — the only code that may call it.
- **Auth:** {{how}}

## Calls we make
| Function | Endpoint / operation | Returns |
|---|---|---|
| `{{path:symbol}}` | `{{METHOD /path}}` | {{shape}} |

## Response shapes that bite
<!-- fill: nesting, 200-with-error, pagination quirks. Drop if none. -->

## When it fails
<!-- fill: timeouts, retries, what the user sees, what is safe to retry. -->
