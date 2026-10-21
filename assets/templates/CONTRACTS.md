---
covers: [{{type_files}}, {{api_definition_files}}, {{schema_files}}]
verified_at: {{HEAD_SHORT}}
verified_on: {{TODAY}}
---
# Contracts & Data Schemas

<!-- fill: Where authoritative API schemas and TypeScript types live in the code.
     Note: Reference existing types directly (`path:Type`); do NOT copy long type definitions here. -->

## Authoritative Type Definitions

| Domain Entity | Primary TS Type / Interface | Source File | Description |
|---|---|---|---|
| `User` | `{{User}}` | `{{src/types/user.ts:User}}` | Authenticated user profile and session permissions |
| `Organization` | `{{Organization}}` | `{{src/types/org.ts:Organization}}` | Multi-tenant account boundaries and plan tiers |
| `Payload` | `{{ResourcePayload}}` | `{{src/types/resource.ts:ResourcePayload}}` | Core domain object payload |

## Backend API Endpoints & Contracts

<!-- fill: List external API routes called by the frontend. Include full paths, methods, auth, and payload types. -->
| Method | Endpoint Path | Auth Required | Request Type | Response Type | Error Statuses |
|---|---|---|---|---|---|
| POST | `{{/api/v1/auth/login}}` | Public | `{{LoginRequest}}` | `{{AuthResponse}}` | 400, 401, 429 |
| GET | `{{/api/v1/user/profile}}` | Bearer JWT | None | `{{UserProfile}}` | 401, 403, 404 |
| PUT | `{{/api/v1/items/:id}}` | Bearer JWT | `{{UpdateItemDto}}` | `{{Item}}` | 400, 401, 404, 409 |

## Authentication & Authorization Assumptions

- **Token Storage:** Token stored in `{{httpOnly cookie / memory / localStorage}}`.
- **Token Refresh Cycle:** Handled by `{{src/api/interceptor.ts:refreshToken}}` upon receiving a 401.
- **Tenant Isolation:** Multi-tenancy headers `{{X-Tenant-ID or org slug in URL}}` attached automatically.

## Standard Error Envelope

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Human-readable description of error",
    "details": [
      { "field": "email", "issue": "Invalid format" }
    ]
  }
}
```

## Persistence & Client Cache Contracts

<!-- fill: Contracts for localStorage, sessionStorage, IndexedDB, or Query cache keys. -->
| Store Name | Storage Key | Format | Owner / Invalidator |
|---|---|---|---|
| `localStorage` | `{{auth_token_key}}` | String (JWT) | `{{src/auth/tokenStorage.ts}}` |
| `Query Cache` | `{{['items', orgId]}}` | JSON array of `Item` | `{{src/services/items.ts:useItems}}` |

## Analytics & Telemetry Event Contracts

| Event Name | Trigger Location | Required Payload Properties |
|---|---|---|
| `page_viewed` | Route change in `{{src/routes/...}}` | `path`, `title`, `referrer` |
| `cta_clicked` | Button click in `{{src/components/...}}` | `button_id`, `destination`, `experiment_tag` |
| `action_completed` | Success callback in `{{src/flows/...}}` | `duration_ms`, `item_id`, `status` |

## Required / Unavailable Backend Capabilities

<!-- fill: When a desired frontend change requires backend APIs that do NOT yet exist,
     document the contract specification below.
     RULE: NEVER fabricate mock endpoints or fake working integrations in frontend code.
     Describe the exact required API contract here instead. -->

### Proposed Endpoint: `{{METHOD /api/v1/proposed/endpoint}}`
- **Purpose:** {{Why this capability is needed by the frontend}}
- **Required Query/Body Parameters:**
  ```json
  {
    "param1": "string (required)",
    "param2": "number (optional)"
  }
  ```
- **Expected Success Response (200 OK):**
  ```json
  {
    "id": "string",
    "status": "ready"
  }
  ```
- **Blocking Status:** {{Mark whether this is pending backend implementation}}
