---
covers: [{{every file on the path}}]
verified_at: {{HEAD_SHORT}}
verified_on: {{TODAY}}
---
# Flow: {{name}}

<!-- fill: one sentence: what triggers it and what it produces. -->

## Steps
1. **{{What happens}}** — `{{path:function}}`
   {{One line. Branches: "if X → step N, else …".}}

## Data at key hops
```json
{{real keys only}}
```

## Errors
<!-- fill: where errors are caught, what the caller receives, what is logged/alerted. -->

## Side effects
<!-- fill: DB writes, queue messages, cache writes, external calls, background tasks started. -->
