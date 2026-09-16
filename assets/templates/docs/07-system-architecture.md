# 07 System Architecture

> This is the product-level architecture summary. The canonical deep dive is
> [`ARCHITECTURE.md`](ARCHITECTURE.md). Keep them consistent.

## Diagram
<!-- fill: an ASCII or mermaid diagram of client → API layer → backend systems. -->

```mermaid
flowchart LR
  UI[Client UI] --> API[API / BFF layer]
  API --> S1[(System 1)]
  API --> S2[(System 2)]
```

## Layers
- **Client:** <!-- ... -->
- **API / BFF:** <!-- ... -->
- **Backends:** <!-- list; link to current-infrastructure/ -->

## Data Flow
<!-- fill: how a typical request travels end to end. -->
