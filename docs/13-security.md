# 13 Security

## Access Control
<!-- fill: how the app is gated (auth provider, roles, edge gating). -->

## Secrets
- All credentials live in env vars (`{{SECRET_ENV_NAMES}}`), never sent to the browser.
- Server-only clients are never imported into client components.

## Data Access
<!-- fill: least-privilege posture, e.g. read-only DB pools; write isolation. -->

## Input Handling
<!-- fill: validation, sanitization, injection prevention. -->

## Threat Model Notes
<!-- fill: what's the sensitive surface? impersonation, PII, mutations? -->
