# Stack hints

Where to look first in each ecosystem. These are starting points only: confirm everything in the code. If the stack isn't listed, use the method at the end.

## Python

| Thing | FastAPI / Starlette | Flask | Django |
|---|---|---|---|
| Entry / app object | `app = FastAPI(...)`, often in `main.py`, `index.py`, `app/main.py`; `lifespan=` or `@app.on_event` holds startup | `Flask(__name__)`, `create_app()` factory | `manage.py`, `<proj>/settings.py`, `wsgi.py` / `asgi.py` |
| Routes | `APIRouter(prefix=…)`, `@router.get/post`, `app.include_router(x, prefix=…)`; full path = mount prefix + router prefix + route | `@app.route`, `Blueprint`, `register_blueprint(url_prefix=…)` | `urls.py` (`path`, `re_path`, `include`), views, DRF `ViewSet` + `router.register` |
| Request validation | Pydantic models in signatures, `Depends(...)` | marshmallow / manual | forms, DRF serializers |
| Middleware / auth | `Depends` chains, `app.add_middleware`, `@app.middleware("http")` | `before_request`, decorators | `MIDDLEWARE` in settings, permission classes |
| Data | SQLAlchemy (`__tablename__`, Alembic `migrations/versions`), Motor/PyMongo (`db["coll"]`), Redis (`redis.asyncio`) | Flask-SQLAlchemy | `models.py`, `migrations/` |
| Background work | `BackgroundTasks`, Celery (`@shared_task`), aio-pika / pika consumers, APScheduler | Celery, RQ | Celery, management commands |
| Config | `os.getenv`, pydantic `BaseSettings`, a `config.py` / `Config` class, python-dotenv | `app.config` | `settings.py`, django-environ |
| Tests / lint | `pytest`, `tests/`, `conftest.py`; `ruff.toml`, `pyproject [tool.*]`, `.pre-commit-config.yaml` | same | `manage.py test` |

## Node / TypeScript backends

| Thing | Express / Koa / Fastify / Hono | NestJS |
|---|---|---|
| Entry | `package.json` `main` / `scripts.start`, `src/index.(js|ts)`, `server.(js|ts)`, `app.(js|ts)` | `src/main.ts` → `NestFactory.create(AppModule)` |
| Routes | `router.get('/x', …)`, `app.use('/prefix', router)`; the full path is composed across files | `@Controller('prefix')` + `@Get('x')`; modules list controllers and providers |
| Validation | Joi / zod / celebrate / express-validator middleware | `class-validator` DTOs, `ValidationPipe` |
| Middleware / auth | `app.use(...)` order matters; error handler is the 4-argument `(err, req, res, next)` | Guards, interceptors, pipes, exception filters |
| Data | Mongoose (`mongoose.model`, `Schema`), Sequelize, Prisma (`schema.prisma`), Knex/TypeORM migrations, ioredis | TypeORM `@Entity`, Prisma, Mongoose module |
| Background work | node-cron, BullMQ, amqplib consumers, `setInterval` jobs registered at startup | `@nestjs/schedule`, Bull queues |
| Config | `process.env`, `dotenv`, a `config/` folder | `ConfigModule` or plain `process.env` |
| Tests / lint | jest / vitest / mocha, `eslint.config.*`, `.prettierrc`, husky, commitlint | jest with `Test.createTestingModule` |

## Frontends

| Thing | Next.js | React (Vite / CRA) | Vue / Nuxt | SvelteKit / Angular |
|---|---|---|---|---|
| Routes | `app/**/page.tsx`, `app/**/route.ts` (API), `layout.tsx`; or `pages/**` | `react-router` route config | `pages/**` (Nuxt), `vue-router` | `src/routes/**/+page.svelte`; Angular `Routes` arrays |
| Server/client boundary | `"use client"`, server components, server actions, `middleware.ts` | everything is client side | `server/` folder in Nuxt | `+page.server.ts`; Angular SSR |
| State | React Query / SWR, Redux Toolkit / Zustand / Context | same | Pinia / Vuex | Svelte stores; NgRx / services |
| Components | `components/`, `components/ui/` (often shadcn), `@/` path alias in `tsconfig.json` | same | `components/` | `lib/components` |
| Styling / design system | Tailwind (`tailwind.config.*`, CSS variables in `globals.css`), CSS modules, a theme file | same | same | same |
| API calls | `lib/api`, `services/`, fetch wrappers, env vars `NEXT_PUBLIC_*` (sent to the browser!) | `VITE_*` env vars (sent to the browser) | `runtimeConfig` | |

For a frontend, also document:
- which env vars reach the browser
- the API base URL and auth token handling
- loading, empty and error state conventions
- the component inventory, as one table: name → file → purpose → key props

## Go

- **Entry:** `cmd/<name>/main.go`, `main.go`.
- **Packages:** `internal/` (private), `pkg/` (shared).
- **Routes:** `http.HandleFunc`, `mux.HandleFunc`; gin `r.GET`, echo `e.GET`, chi `r.Get`, fiber `app.Get`.
- **Data:** `database/sql`, sqlc, GORM; migrations in `migrations/` or `db/`.
- **Config:** `os.Getenv`, envconfig, viper.
- **Tests:** `*_test.go`, `go test ./...`. Lint: `.golangci.yml`.

## Java / Kotlin (Spring)

- **Entry:** the `@SpringBootApplication` class.
- **Routes:** `@RestController` + `@GetMapping` / `@RequestMapping`.
- **Data:** JPA `@Entity` + `JpaRepository`; Flyway or Liquibase in `src/main/resources/db/migration`.
- **Config:** `application.yml` / `.properties` with `${ENV_VAR}`.
- **Tests:** `src/test/java`.

## Ruby on Rails

- **Routes:** `config/routes.rb`.
- **Code:** `app/controllers`, `app/models`.
- **Data:** `db/schema.rb`, `db/migrate/`.
- **Background work:** `app/jobs` (Sidekiq / ActiveJob).
- **Config:** `config/credentials`, `ENV[...]`.
- **Tests:** `spec/` or `test/`.

## PHP (Laravel)

- **Routes:** `routes/web.php`, `routes/api.php`.
- **Code:** `app/Http/Controllers`, `app/Models`.
- **Data:** `database/migrations`.
- **Config:** `config/*.php` calling `env()`.
- **Background work:** `app/Jobs`.

## Rust

- **Entry:** `src/main.rs` / `src/lib.rs`; workspace members in `Cargo.toml`.
- **Routes:** axum `Router::new().route(...)`, actix `#[get("/x")]`.
- **Data:** sqlx / diesel migrations.
- **Config:** `env::var`.

## Unknown stack: the general method

1. **Build manifest:** read it to learn the language, dependencies and scripts.
2. **Entry point:** find what the Dockerfile `CMD`, `Procfile` or CI deploy step actually runs. That is the real entry point.
3. **Inbound surface:** grep for how the system receives work: a listening port, route registration, queue consumers, a cron scheduler, CLI argument parsing.
4. **Outbound surface:** grep for how it reaches the outside world: HTTP clients, DB drivers, SDK imports, env var reads.
5. **Trace:** follow one real input from entry to output and write down every file it passes through.
6. **Rank:** use git churn (the inventory's `top_churn`) to decide which areas matter most.
