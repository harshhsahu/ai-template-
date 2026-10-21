---
covers: [{{config files}}, ".env.example", "Dockerfile"]
verified_at: {{HEAD_SHORT}}
verified_on: {{TODAY}}
---
# Environment

## Run it locally
<!-- fill: numbered, verified steps: prerequisites (versions), install, required services (docker compose?), env file, start command, how to know it is up. -->

## Variables
<!-- fill: one row per var, grouped by concern (Core, Database, Auth, Integrations...).
     Required = the process crashes or a core path fails without it.
     Mark secrets. Mark vars that reach the browser. -->
| Var | Required | Default | Read in | Purpose / effect if missing |
|---|---|---|---|---|
| `{{VAR}}` | yes | — | `{{path:symbol}}` | {{...}} |

## Must match other services
<!-- fill: vars whose values must be identical elsewhere, and what breaks if they differ. Drop if none. -->
