# 12 API Guidelines

## Layer Rules
- The API layer is the **only** place that touches server-only clients / databases.
- UI never calls a database or external service directly.

## Route Conventions
<!-- fill: naming, HTTP methods, path params vs query params, versioning. -->

## Response Shape
<!-- fill: standard success/error envelope; how nulls signal degraded backends. -->

```ts
// success
{ data: ... }
// degraded backend
{ data: null }   // NOT a 500
```

## Error Handling
- Catch backend failures; return `null` for that data block. See 18-error-handling.md.

## Documenting a Route
Every route domain gets a file in [`api/`](api/). Clone [`api/_TEMPLATE.md`](api/_TEMPLATE.md).
