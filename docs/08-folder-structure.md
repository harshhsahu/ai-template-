# 08 Folder Structure

```
{{PRODUCT_SLUG}}/
├── app/ (or src/)        # <!-- routes / pages -->
│   ├── api/              # API route handlers (BFF layer) — the only place touching servers
│   └── ...
├── components/
│   ├── shared/           # reusable UI (PageHeader, DataTable, ...)
│   └── <feature>/        # feature-scoped components
├── docs/                 # source of truth for architecture (YOU ARE HERE)
├── lib/
│   ├── server/           # server-only clients (DB pools, admin tokens) — never imported client-side
│   └── ...
└── public/               # static assets
```

## Placement Rules
<!-- fill: where does new X go? e.g. "one API domain = one folder under app/api",
     "shared components go in components/shared, feature ones in components/<feature>". -->
