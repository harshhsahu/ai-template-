---
covers: [{{route files}}, {{schema files}}]
verified_at: {{HEAD_SHORT}}
verified_on: {{TODAY}}
---
# API

<!-- fill: base URL/prefix composition, auth schemes and where they are enforced, response envelope (if any), error shape. -->

## {{Router / group}}
Mounted at `{{prefix}}` in `{{path:line}}`.

| Method | Path | Auth | Handler | Request | Notes |
|---|---|---|---|---|---|
| POST | `{{/full/path}}` | {{jwt}} | `{{path:function}}` | `{{Schema}}` | {{errors, streaming, side effects}} |

### `{{METHOD /full/path}}`
<!-- fill: only for the important routes: request shape (required fields), response shape, error cases. -->
