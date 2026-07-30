# 15 Environment Setup

## Prerequisites
<!-- fill: runtime version, package manager, system deps. -->

## Install & Run
```bash
{{PKG_INSTALL}}       # e.g. npm install
{{PKG_DEV}}           # e.g. npm run dev
```

## Environment Variables
| Var | Required | Purpose |
|---|---|---|
| `{{SECRET_ENV_1}}` | yes | <!-- --> |
| `{{SECRET_ENV_2}}` | no | <!-- unset → related feature degrades gracefully --> |

Copy `.env.example` → `.env.local` and fill in. Never commit real secrets.

## Notes
<!-- fill: which features work without which env vars (graceful degradation map). -->
