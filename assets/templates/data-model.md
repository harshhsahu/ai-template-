---
covers: [{{model/schema/migration files}}, {{cache/queue modules}}]
verified_at: {{HEAD_SHORT}}
verified_on: {{TODAY}}
---
# Data model

<!-- fill: one line per store: what it is used for and the connection code. -->

## {{Database name}}
Connection: `{{ENV_VAR}}` → `{{path:symbol}}`. Schema owned by: {{this repo | other repo}}.

### `{{table_or_collection}}`
{{Purpose.}} Written by `{{path:symbol}}`, read by `{{path:symbol}}`.

| Field | Type | Notes |
|---|---|---|

## Cache
<!-- fill: key pattern | TTL | written by | invalidated by. Explain any prefix convention. -->

## Queues
<!-- fill: queue | producer | consumer | message shape | failure handling. Drop if none. -->
