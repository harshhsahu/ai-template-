# Analysis playbook — how to find the facts

Read this in Phase 2, after `survey_project.py` has told you where things are. The survey
locates candidate files; this file tells you what to extract from them and in what order,
per ecosystem.

## Contents

- [Order of investigation](#order-of-investigation)
- [Stack identification](#stack-identification)
- [Finding routes and endpoints](#finding-routes-and-endpoints)
- [Finding data models and schemas](#finding-data-models-and-schemas)
- [Finding UI components and navigation](#finding-ui-components-and-navigation)
- [Finding auth and security](#finding-auth-and-security)
- [Finding external services and infrastructure](#finding-external-services-and-infrastructure)
- [Finding tests, CI and deployment](#finding-tests-ci-and-deployment)
- [Deriving purpose and features](#deriving-purpose-and-features)
- [Architecture: what you may and may not conclude](#architecture-what-you-may-and-may-not-conclude)
- [Multi-app repos](#multi-app-repos)

## Order of investigation

Manifest → config → entry point → routes → models → views/components → tests.

This order works because each step narrows the next. The manifest names the framework,
which tells you the routing convention, which gives you the endpoint list, which names the
models each endpoint touches. Reading components before you know the routes means reading
files without knowing why they matter.

Budget your reading: the highest information-per-token files are the manifest, the settings
or config module, the URL/route table, and the model or migration files. A 2000-line view
file can often be skimmed for its class/function signatures and decorators.

## Stack identification

Read manifests **and** lockfiles. The manifest gives the declared range (`^5.1`), the
lockfile gives the version actually installed — cite the resolved version, since that's
what the code runs against.

| File | Ecosystem | Also read |
|---|---|---|
| `package.json` | Node/JS/TS | `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `tsconfig.json`, bundler config (`vite.config.*`, `next.config.*`, `webpack.*`) |
| `requirements.txt`, `pyproject.toml`, `Pipfile` | Python | `poetry.lock`, `uv.lock`, `setup.cfg`, `manage.py` (⇒ Django) |
| `go.mod` | Go | `go.sum` |
| `pom.xml`, `build.gradle(.kts)` | Java/Kotlin | `application.yml`/`.properties` |
| `Gemfile` | Ruby | `Gemfile.lock`, `config/routes.rb` (⇒ Rails) |
| `composer.json` | PHP | `composer.lock`, `artisan` (⇒ Laravel) |
| `Cargo.toml` | Rust | `Cargo.lock` |
| `*.csproj`, `*.sln` | .NET | `appsettings.json` |

Classify each dependency by the concern it serves, because `06-tech-stack.md` and the
"one library per concern" rule are both organized that way: framework, styling, UI
components, icons, charts, animation, state, data-fetching, forms/validation, ORM/data
access, auth, testing, build. **Two libraries for one concern is a finding** — the template
treats it as review-blocking, so record it in `docs/AGENTS.md` as a conflict to resolve
rather than listing both as approved.

## Finding routes and endpoints

| Stack | Where routes live | What to extract |
|---|---|---|
| Django REST Framework | `urls.py` (project + app), `routers.DefaultRouter()` registrations, `ViewSet` classes | Router `basename`/prefix expands to the standard six endpoints; `@action(detail=…, methods=[…])` adds custom ones — these are easy to miss, so grep for `@action` |
| Django (plain) | `urlpatterns` in every `urls.py` | `path()`/`re_path()` route, view, `name=` |
| Flask / FastAPI | `@app.route`, `@router.get/post/...`, `APIRouter(prefix=)`, `include_router` | Method, path, response_model, dependencies |
| Express / Nest / Fastify | `app.use`, `router.get(...)`, `@Controller`/`@Get` decorators | Mount prefixes compose — trace `app.use('/api/x', router)` to get full paths |
| Next.js | `app/**/route.ts` (App Router), `pages/api/**` | Exported `GET`/`POST`/... names; dynamic segments `[id]` |
| Rails | `config/routes.rb` | `resources :x` expands to seven routes; run/read the resource macros carefully |
| Laravel | `routes/api.php`, `routes/web.php` | `Route::apiResource` expansion, middleware groups |
| Spring | `@RestController` + `@RequestMapping`/`@GetMapping` | Class-level prefix + method-level path compose |
| Go | `http.HandleFunc`, chi/gin/echo router setup | Mount groups |

For each endpoint the `api/_TEMPLATE.md` needs: path, method, purpose, path params, query
params, data sources (which model/service/function), the actual response shape, and
behavior notes. Get the response shape from the serializer / DTO / schema / returned
literal — **not** from the endpoint's name. `fields = "__all__"` on a serializer means you
must read the model to enumerate fields.

Also capture cross-cutting route behavior, since `12-api-guidelines.md` needs it:
pagination class and default page size, filter/search/ordering backends, auth classes,
throttles, and the error envelope.

## Finding data models and schemas

**Migrations are the most reliable source** — they are what was actually applied. Read
model definitions for intent and migrations for truth; where they differ, document the
migration state and flag the drift.

| Stack | Read |
|---|---|
| Django | `*/models.py`, `*/migrations/00*.py` (read all, in order — later ones alter earlier fields) |
| SQLAlchemy / Alembic | model classes, `alembic/versions/*` |
| Prisma | `schema.prisma` (authoritative and self-contained) |
| TypeORM / Sequelize / Mongoose | entity/model files, `migrations/` |
| Rails | `db/schema.rb` (authoritative), `db/migrate/*` |
| Raw SQL | `*.sql`, `schema.sql`, `init.sql` |

Extract per entity: table name, every column with type and null/default, PK, FKs and their
`on_delete` behavior, unique constraints and composite uniques, indexes, and enum/choice
values. Also record model-level `Meta` options (ordering, `unique_together`), computed
`@property` fields (they appear in API responses but not in the table), and signals or
hooks that write data implicitly.

The `database/_TEMPLATE.md` reserves a **Cross-System References** section for logical
references that are not foreign keys. These cause the most cross-system bugs and are only
discoverable by reading code — an `org_id` integer column with no FK, joined manually in a
service function. Look for them deliberately: columns named `*_id` with no `ForeignKey`,
and manual joins or lookups in service/repository code.

## Finding UI components and navigation

Start from the router to get the screen list, then follow imports down:

- React Router: `<Route path element>` trees, often in `App.jsx`/`routes.tsx`
- Next.js: the `app/`/`pages/` file tree *is* the route table
- Vue Router / Angular: `routes` array, `RouterModule.forRoot`
- Server-rendered: template directory plus the view that renders each template

`05-navigation.md` wants the top-level route table, the navigation model (sidebar? topbar?
command palette?), and deep-link conventions — read the sidebar/nav component for the
first two and the dynamic route segments for the third.

For `ui/` docs, extract from each shared component: import path, props with types and
defaults (TS interfaces, PropTypes, or destructured defaults), variants, and
loading/empty/disabled states. Note which components are imported in more than one place —
that's what makes them shared rather than one-off.

For `10-design-system.md`: `tailwind.config.*` theme extensions, CSS custom properties in
the global stylesheet, font imports, and the dark-mode strategy (`darkMode:` setting, a
theme context/provider, a `data-theme` attribute).

## Finding auth and security

- **Mechanism:** JWT (look for token libraries, `SIMPLE_JWT` settings, refresh endpoints),
  session cookies, OAuth provider config, API keys.
- **Where it's enforced:** middleware, decorators (`@login_required`,
  `IsAuthenticated`), permission classes, route guards, `ProtectedRoute` wrappers.
- **Roles and object-level rules:** custom permission classes and queryset filtering by
  the request user — `get_queryset` filtering is a real access-control boundary and is easy
  to overlook.
- **Client-side token storage:** `localStorage` vs `httpOnly` cookie, and the refresh
  interceptor. Worth documenting precisely because it's a common finding.
- **Secrets:** collect env var *names* from `.env.example`, `os.environ`/`process.env`
  reads, and settings modules. Never copy a value out of a committed `.env` into the docs.
  If a real secret appears committed, say so as a security note and don't reproduce it.
- **CORS/CSRF, rate limits, validation:** middleware and settings keys.

## Finding external services and infrastructure

One `current-infrastructure/<system>.md` per system you actually talk to. Find them via:
the database engine in settings/env, cache/queue clients (Redis, Celery, RabbitMQ), SDK
imports (S3, Stripe, Twilio, SendGrid, Firebase), raw HTTP calls to external hosts, and
service definitions in `docker-compose.yml`.

Per system capture: role (what it's the source of truth for), connection env var and
client module path, auth method, access posture (read-only?), the entities/endpoints you
touch, the functions your code calls, and **degradation behavior** — what happens when it's
down. If the code doesn't handle that, the honest entry is "no fallback; requests fail"
plus a TODO, and that's a genuinely useful finding.

The template's `_TEMPLATE.md` opens with a `> [!WARNING]` for the system's #1 footgun. Fill
it only with a real footgun you found (an ID that isn't a foreign key, a table that looks
authoritative but isn't). If you didn't find one, delete the warning block rather than
inventing a scary-sounding caveat.

## Finding tests, CI and deployment

- Tests: runner config (`pytest.ini`, `jest.config.*`, `vitest.config.*`), test file
  locations and naming, fixtures/factories, and roughly what layer they cover (unit /
  integration / e2e). Count test files and note obvious gaps; don't compute a coverage
  percentage you can't measure.
- CI: `.github/workflows/*`, `.gitlab-ci.yml`, `Jenkinsfile`, `azure-pipelines.yml` — the
  job steps *are* the merge gate, which feeds `22-definition-of-done.md`.
- Deployment: `Dockerfile` (base image, build stages, exposed port, entrypoint),
  `docker-compose.yml` (services and their wiring), `nginx.conf`, `Procfile`,
  `vercel.json`, `fly.toml`, k8s manifests, Terraform.
- Entrypoint scripts (`entrypoint.sh`) often reveal migration-on-boot, static collection,
  and the production server command — exactly what `20-deployment.md` needs.

## Deriving purpose and features

You can support these from code without inventing:

- **Purpose:** manifest `description`, README, the domain vocabulary of the models. Five
  models named Building/Floor/Room/Tenant/Lease tell you the domain unambiguously.
- **Features:** the route groups and screen list. Each user-facing route group is a
  feature; name it from the code's own vocabulary, not marketing language.
- **Scheduled behavior:** management commands, cron definitions, and task queues reveal
  features no route shows (e.g. a monthly billing generator). Look for them — they're the
  most commonly missed features.

You cannot support the *value* claim ("saves landlords 10 hours a month"). Describe what
the feature does; leave the value framing to the human.

## Architecture: what you may and may not conclude

**May conclude from structure:** the layer diagram and what talks to what; whether the UI
goes through an API layer or reaches data directly; where the boundary between server-only
and client code sits; whether state is server-fetched or client-held; the deployment
topology from Docker/compose; the auth flow.

**May label as inferred:** the integration phase (mock-first vs integrated) from the
presence of fixture/mock modules next to live clients; an intended pattern from consistent
naming.

**May not conclude:** why a decision was made, which alternatives were rejected, planned
phases, performance budgets, or SLAs. The `ARCHITECTURE.md` "Integration Strategy" and
phase list are frequently unanswerable from code — describe the current state and leave the
forward-looking phases as a TODO. An invented rationale is the most damaging kind of
invention, because it will be cited in future design debates.

## Multi-app repos

A separate backend and frontend directory (or several packages) is the common case.
Document them as **one docs set** describing one product, not two disconnected sets, unless
the user wants otherwise — the whole value is showing how the halves connect.

Practical approach:

- `06-tech-stack.md`: one table with a Layer column covering both.
- `08-folder-structure.md`: show both trees under one root.
- `ARCHITECTURE.md` / `07`: this is where the halves meet. Trace one real request end to
  end — client API module → HTTP call → server route → model → response — and note the base
  URL env var that binds them.
- `api/` files: document the server's contract, and note which client module consumes each
  domain (a `src/api/paymentsApi.js` next to `api/payments.md` is a strong pairing).
- `modules/`: organize by product feature, which usually spans both halves.
- Verify the two halves actually agree. A client calling an endpoint the server doesn't
  expose (or vice versa) is a real finding worth recording — and exactly the kind of thing
  docs are supposed to surface.
