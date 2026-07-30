# System Architecture — {{PRODUCT_NAME}}

## Overview

<!-- fill: 2–3 sentences. What does this product do, and what shape is it? e.g.
     "read-only aggregation layer over N isolated backends", or
     "transactional CRUD app over a single relational DB". -->

---

## Integration Strategy

<!-- fill: How do you get from zero to integrated? Document the seam that lets UI evolve
     independently of backends (mock layer, adapter, feature flags, ...). State the phases. -->

1. **Phase 1:** <!-- ... -->
2. **Phase 2:** <!-- ... -->

Key invariant: <!-- e.g. "UI components never change during backend swaps — they stay
ignorant of the underlying data architecture." -->

---

## Client Layer

- **Framework:** {{FRAMEWORK}}
- **Styling:** {{STYLING}}
- **UI Library:** {{UI_LIB}}
- **Data Fetching:** <!-- fill: pattern -->

---

## Backend / Aggregation Layer

<!-- fill: If you have a BFF/API gateway, describe it. List every system you read/write,
     its role, and how it authenticates. Repeat the block per system. -->

### Core Systems

1. **{{SYSTEM_1}}** (`{{CLIENT_PATH_1}}`)
   - **Role:** <!-- ... -->
   - **Auth:** <!-- ... -->
2. **{{SYSTEM_2}}** (`{{CLIENT_PATH_2}}`)
   - **Role:** <!-- ... -->
   - **Auth:** <!-- ... -->

See [`current-infrastructure/`](current-infrastructure/) for the deep detail on each system.

---

## Security Model

1. **Access control:** <!-- how is the app gated? -->
2. **Secrets never leak:** all credentials live in env (`{{SECRET_ENV_NAMES}}`), never sent to the browser.
3. **Least privilege:** <!-- e.g. read-only DB pools; write isolation through explicit endpoints. -->
4. **Write isolation:** <!-- which operations mutate, and how they're routed/authorized. -->
