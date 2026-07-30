# 18 Error Handling

## Principle: Fail Soft
A single backend failure must not take down the whole page. Catch, log, degrade.

## API Layer
- Wrap each backend call; on failure return `null` for that data block (not a 500).
- Log the error server-side with enough context to debug.

## UI Layer
- Handle `null`/empty gracefully: skeletons, empty states, mock fallback.
- Reserve hard error pages for genuinely unrecoverable states (e.g. not-found).

## States to Design For
| State | UI |
|---|---|
| Loading | <!-- skeleton --> |
| Empty | <!-- "no data yet" --> |
| Partial (one backend down) | <!-- degraded block --> |
| Not found | <!-- not-found page --> |
