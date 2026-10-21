#!/usr/bin/env python3
"""Collect facts about a repository for the ai-docs skill.

Writes the full inventory as JSON to --out and prints a short Markdown summary
to stdout. Python standard library only; works on any language.

Usage: python3 inventory.py [repo_root] --out /path/inventory.json
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    CODE_EXTS, DOC_EXTS, git, in_skipped_dir, is_git_repo, is_text_candidate,
    list_files, read_text,
)

MANIFEST_NAMES = {
    "package.json", "pyproject.toml", "requirements.txt", "req.txt", "setup.py", "setup.cfg",
    "Pipfile", "go.mod", "Cargo.toml", "pom.xml", "build.gradle", "build.gradle.kts",
    "Gemfile", "composer.json", "mix.exs", "pubspec.yaml", "deno.json", "bun.toml",
}
INFRA_NAMES = {
    "Dockerfile", "docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml",
    "Procfile", "Makefile", "justfile", "Taskfile.yml", "serverless.yml", "vercel.json",
    "netlify.toml", "fly.toml", "render.yaml", "app.yaml", "wrangler.toml", "wrangler.jsonc",
    "nest-cli.json", "manage.py", "alembic.ini", "schema.prisma", "tsconfig.json",
    "angular.json", "nx.json", "turbo.json", "lerna.json", "pnpm-workspace.yaml",
}
TOOLING_PATTERNS = [
    r"(^|/)ruff\.toml$", r"(^|/)\.flake8$", r"(^|/)mypy\.ini$", r"(^|/)\.pylintrc$",
    r"(^|/)\.eslintrc", r"(^|/)eslint\.config\.", r"(^|/)\.prettierrc", r"(^|/)prettier\.config\.",
    r"(^|/)biome\.json", r"(^|/)\.pre-commit-config\.yaml$", r"(^|/)commitlint\.config\.",
    r"(^|/)\.cz\.toml$", r"(^|/)\.editorconfig$", r"(^|/)\.golangci\.", r"(^|/)rustfmt\.toml$",
    r"(^|/)\.rubocop\.yml$", r"(^|/)phpstan\.neon", r"(^|/)jest\.config\.", r"(^|/)vitest\.config\.",
    r"(^|/)pytest\.ini$", r"(^|/)tox\.ini$", r"(^|/)playwright\.config\.", r"(^|/)cypress\.config\.",
    r"(^|/)\.husky/", r"(^|/)\.github/workflows/", r"(^|/)\.gitlab-ci\.yml$", r"(^|/)Jenkinsfile$",
    r"(^|/)\.circleci/", r"(^|/)bitbucket-pipelines\.yml$",
]
AGENT_FILES = [
    "AGENTS.md", "CLAUDE.md", "GEMINI.md", ".cursorrules", ".windsurfrules",
    ".github/copilot-instructions.md", "CONVENTIONS.md", ".clinerules",
]
ENTRY_NAMES = {
    "main.py", "app.py", "index.py", "server.py", "wsgi.py", "asgi.py", "manage.py", "__main__.py",
    "index.js", "index.ts", "main.js", "main.ts", "server.js", "server.ts", "app.js", "app.ts",
    "main.go", "main.rs", "lib.rs", "Program.cs", "Application.java", "main.dart",
    "layout.tsx", "layout.jsx", "layout.js", "_app.tsx", "_app.jsx", "_app.js", "App.tsx", "App.jsx", "App.vue", "main.tsx", "main.jsx",
}
FRAMEWORK_DEPS = {
    "fastapi": "FastAPI", "flask": "Flask", "django": "Django", "starlette": "Starlette",
    "aiohttp": "aiohttp", "tornado": "Tornado", "sanic": "Sanic", "celery": "Celery",
    "sqlalchemy": "SQLAlchemy", "pymongo": "PyMongo", "motor": "Motor (async Mongo)",
    "redis": "Redis", "pika": "RabbitMQ (pika)", "aio-pika": "RabbitMQ (aio-pika)",
    "pydantic": "Pydantic", "langchain": "LangChain",
    "express": "Express", "@nestjs/core": "NestJS", "next": "Next.js", "react": "React",
    "vue": "Vue", "nuxt": "Nuxt", "svelte": "Svelte", "@sveltejs/kit": "SvelteKit",
    "@angular/core": "Angular", "koa": "Koa", "fastify": "Fastify", "hono": "Hono",
    "mongoose": "Mongoose", "sequelize": "Sequelize", "typeorm": "TypeORM", "prisma": "Prisma",
    "@prisma/client": "Prisma", "drizzle-orm": "Drizzle", "ioredis": "Redis (ioredis)",
    "amqplib": "RabbitMQ (amqplib)", "kafkajs": "Kafka", "socket.io": "Socket.IO",
    "tailwindcss": "Tailwind CSS", "redux": "Redux", "@reduxjs/toolkit": "Redux Toolkit",
    "zustand": "Zustand", "@tanstack/react-query": "TanStack Query", "swr": "SWR",
    "jest": "Jest", "vitest": "Vitest", "pytest": "pytest", "mocha": "Mocha",
    "github.com/gin-gonic/gin": "Gin", "github.com/labstack/echo": "Echo",
    "github.com/gofiber/fiber": "Fiber", "gorm.io/gorm": "GORM",
    "rails": "Rails", "laravel/framework": "Laravel", "spring-boot": "Spring Boot",
    "actix-web": "Actix", "axum": "Axum", "tokio": "Tokio",
}

ENV_PATTERNS = [
    re.compile(r"""os\.(?:getenv|environ\.get)\(\s*["']([A-Za-z_][A-Za-z0-9_]*)["']"""),
    re.compile(r"""os\.environ\[\s*["']([A-Za-z_][A-Za-z0-9_]*)["']\s*\]"""),
    re.compile(r"""(?<![\w.])(?:getenv|env|config)\(\s*["']([A-Z][A-Z0-9_]+)["']"""),
    re.compile(r"""process\.env\.([A-Za-z_][A-Za-z0-9_]*)"""),
    re.compile(r"""process\.env\[\s*["'`]([A-Za-z_][A-Za-z0-9_]*)["'`]\s*\]"""),
    re.compile(r"""import\.meta\.env\.([A-Za-z_][A-Za-z0-9_]*)"""),
    re.compile(r"""Deno\.env\.get\(\s*["']([A-Za-z_][A-Za-z0-9_]*)["']"""),
    re.compile(r"""os\.(?:Getenv|LookupEnv)\(\s*"([A-Za-z_][A-Za-z0-9_]*)\""""),
    re.compile(r"""ENV(?:\.fetch\(|\[)\s*["']([A-Za-z_][A-Za-z0-9_]*)["']"""),
    re.compile(r"""System\.getenv\(\s*"([A-Za-z_][A-Za-z0-9_]*)\""""),
    re.compile(r"""env::var\(\s*"([A-Za-z_][A-Za-z0-9_]*)\""""),
    re.compile(r"""\$\{([A-Z][A-Z0-9_]+)(?::[^}]*)?\}"""),
]
DOTENV_RE = re.compile(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=", re.M)

HTTP = r"(get|post|put|patch|delete|head|options|all|route|api_route|websocket)"
ROUTE_PATTERNS = [
    # FastAPI / Flask / Express / Koa / Hono / Fastify / Gin / Echo style: obj.verb("path"
    ("call", re.compile(r"""(?<![\w])([A-Za-z_][\w]*)\.""" + HTTP + r"""\(\s*[frb]?["'`](/[^"'`]*|)["'`]""", re.I)),
    # NestJS / Spring decorators: @Get('path'), @PostMapping("path")
    ("decorator", re.compile(r"""@(Get|Post|Put|Patch|Delete|Head|Options|All|Sse)(?:Mapping)?\(\s*(?:value\s*=\s*)?["'`]?([^"'`)]*)["'`]?\s*\)""")),
    ("decorator", re.compile(r"""@RequestMapping\(\s*(?:value\s*=\s*)?["']([^"']*)["']""")),
    ("prefix", re.compile(r"""@Controller\(\s*["'`]([^"'`]*)["'`]""")),
    ("prefix", re.compile(r"""APIRouter\([^)]*prefix\s*=\s*["']([^"']*)["']""")),
    ("mount", re.compile(r"""include_router\(\s*([\w.]+)[^)]*?prefix\s*=\s*["']([^"']*)["']""")),
    ("mount", re.compile(r"""\.use\(\s*["'`](/[^"'`]*)["'`]\s*,\s*([\w.]+)""")),
    ("mount", re.compile(r"""register_blueprint\(\s*([\w.]+)[^)]*?url_prefix\s*=\s*["']([^"']*)["']""")),
    # Django
    ("django", re.compile(r"""(?<![\w])(?:re_)?path\(\s*r?["']([^"']*)["']\s*,\s*([\w.]+)""")),
    # Go net/http
    ("call", re.compile(r"""(?<![\w])(http|mux|r|router)\.(HandleFunc|Handle)\(\s*"([^"]*)\"""")),
]
NEXT_ROUTE_RE = re.compile(r"(?:^|/)(app|pages)/(.*?)(?:/)?(page|route|index)?\.(tsx|ts|jsx|js|mdx)$")

DATA_PATTERNS = {
    "sql_table": re.compile(r"""CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?["`]?([\w.]+)""", re.I),
    "orm_tablename": re.compile(r"""__tablename__\s*=\s*["']([\w.]+)["']"""),
    "mongo_collection": re.compile(r"""(?:db|database|client)\s*\[\s*["']([\w.-]+)["']\s*\]|\.collection\(\s*["']([\w.-]+)["']|get_collection\(\s*["']([\w.-]+)["']"""),
    "mongoose_model": re.compile(r"""mongoose\.model\(\s*["']([\w.-]+)["']|model\(\s*["']([\w.-]+)["']\s*,\s*\w+Schema"""),
    "prisma_model": re.compile(r"""^model\s+(\w+)\s*\{""", re.M),
    "typeorm_entity": re.compile(r"""@Entity\(\s*(?:["']([\w.]+)["'])?"""),
    "django_model": re.compile(r"""class\s+(\w+)\((?:models\.)?Model\)"""),
    "sequelize_define": re.compile(r"""\.define\(\s*["']([\w.]+)["']"""),
}
REDIS_KEY_RE = re.compile(r"""["'`]([a-zA-Z][\w-]*[:_][\w:{}$-]*)["'`]""")
QUEUE_RE = re.compile(r"""(?:queue|QUEUE|exchange|routing_key|topic)[\w]*\s*[=:]\s*["']([\w.:-]+)["']""")


def detect_language(path: str) -> str | None:
    return CODE_EXTS.get(os.path.splitext(path)[1].lower())


def line_count(text: str) -> int:
    return text.count("\n") + (0 if text.endswith("\n") or not text else 1)


def parse_package_json(text: str) -> dict:
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return {}
    deps = sorted({**data.get("dependencies", {}), **data.get("peerDependencies", {})})
    dev = sorted(data.get("devDependencies", {}))
    return {
        "name": data.get("name"), "main": data.get("main"), "type": data.get("type"),
        "scripts": data.get("scripts", {}), "dependencies": deps, "devDependencies": dev,
        "workspaces": data.get("workspaces"),
    }


def parse_requirements(text: str) -> list[str]:
    deps = []
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if not line or line.startswith("-"):
            continue
        name = re.split(r"[<>=!~\[; @]", line, maxsplit=1)[0].strip()
        if name:
            deps.append(name.lower())
    return deps


def parse_pyproject(text: str) -> dict:
    try:
        import tomllib  # Python 3.11+
        data = tomllib.loads(text)
    except Exception:  # noqa: BLE001 - tomllib missing or invalid toml
        names = re.findall(r'^\s*"([A-Za-z0-9_.\-]+)', text, re.M)
        return {"dependencies": sorted({n.lower() for n in names})}
    project = data.get("project", {})
    deps = [re.split(r"[<>=!~\[; ]", d, maxsplit=1)[0].lower() for d in project.get("dependencies", [])]
    poetry = data.get("tool", {}).get("poetry", {})
    deps += [d.lower() for d in poetry.get("dependencies", {}) if d.lower() != "python"]
    scripts = project.get("scripts", {}) or poetry.get("scripts", {})
    return {"name": project.get("name") or poetry.get("name"), "dependencies": sorted(set(deps)),
            "scripts": scripts, "tools": sorted(data.get("tool", {}).keys())}


def parse_go_mod(text: str) -> dict:
    module = re.search(r"^module\s+(\S+)", text, re.M)
    deps = re.findall(r"^\s*([\w.\-/]+)\s+v[\d.]+", text, re.M)
    return {"module": module.group(1) if module else None, "dependencies": sorted(set(deps))}


def parse_dockerfile(text: str) -> dict:
    cmds = re.findall(r"^\s*(?:CMD|ENTRYPOINT)\s+(.+)$", text, re.M | re.I)
    base = re.findall(r"^\s*FROM\s+(\S+)", text, re.M | re.I)
    ports = re.findall(r"^\s*EXPOSE\s+(.+)$", text, re.M | re.I)
    return {"from": base, "cmd": cmds, "expose": ports}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--out", required=True, help="where to write the full JSON inventory")
    ap.add_argument("--max-refs", type=int, default=6, help="max file:line refs kept per env var")
    ap.add_argument("--history", type=int, default=600, help="commits of git history to scan")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    all_files = list_files(root)
    files = [f for f in all_files if not in_skipped_dir(f)]

    inv: dict = {"root": str(root), "is_git": is_git_repo(root)}
    if inv["is_git"]:
        inv["git"] = {
            "head": git(root, "rev-parse", "HEAD").strip(),
            "branch": git(root, "rev-parse", "--abbrev-ref", "HEAD").strip(),
            "commit_count": int(git(root, "rev-list", "--count", "HEAD").strip() or 0),
            "first_commit": git(root, "log", "--reverse", "--format=%ad", "--date=short").split("\n", 1)[0],
            "last_commit": git(root, "log", "-1", "--format=%ad", "--date=short").strip(),
            "dirty_files": [l[3:] for l in git(root, "status", "--porcelain").splitlines() if l],
            "remotes": sorted(set(git(root, "remote", "-v").split())) [:6],
        }

    languages: dict = collections.defaultdict(lambda: {"files": 0, "lines": 0})
    dirs: dict = collections.defaultdict(lambda: {"files": 0, "lines": 0})
    sizes: list = []
    manifests, infra, tooling = {}, [], []
    entry_points: list = []
    env_refs: dict = collections.defaultdict(list)
    dotenv_vars: dict = collections.defaultdict(list)
    routes: list = []
    next_routes: list = []
    data_hits: dict = collections.defaultdict(lambda: collections.defaultdict(set))
    redis_like: collections.Counter = collections.Counter()
    queues: dict = collections.defaultdict(set)
    tests: list = []
    docs: list = []
    hashes: dict = collections.defaultdict(list)
    deps_all: set = set()

    for path in files:
        name = path.rsplit("/", 1)[-1]
        ext = os.path.splitext(name)[1].lower()
        if not is_text_candidate(path):
            continue
        text = read_text(root, path)
        if text is None:
            continue
        lines = line_count(text)
        lang = detect_language(path)
        if lang:
            languages[lang]["files"] += 1
            languages[lang]["lines"] += lines
            parts = path.split("/")
            for depth in (1, 2, 3):
                if len(parts) > depth:
                    d = "/".join(parts[:depth]) + "/"
                    dirs[d]["files"] += 1
                    dirs[d]["lines"] += lines
            sizes.append((lines, path))

        if name in MANIFEST_NAMES or (name.startswith("requirements") and ext == ".txt"):
            if name == "package.json":
                parsed = parse_package_json(text)
            elif name == "pyproject.toml":
                parsed = parse_pyproject(text)
            elif name == "go.mod":
                parsed = parse_go_mod(text)
            elif ext == ".txt":
                parsed = {"dependencies": parse_requirements(text)}
            else:
                parsed = {}
            manifests[path] = parsed
            deps_all.update(d.lower() for d in parsed.get("dependencies", []) or [])
            deps_all.update(d.lower() for d in parsed.get("devDependencies", []) or [])
            if name in {"Cargo.toml", "Gemfile", "composer.json", "pom.xml", "build.gradle", "build.gradle.kts"}:
                deps_all.update(m.lower() for m in re.findall(r"""["']?([a-z][\w.\-/]+)["']?\s*[=:(]""", text))
        if name in INFRA_NAMES or name.startswith("Dockerfile") or name.startswith("docker-compose"):
            entry = {"path": path}
            if name.startswith("Dockerfile"):
                entry.update(parse_dockerfile(text))
            if name == "Procfile":
                entry["processes"] = text.strip().splitlines()[:10]
            infra.append(entry)
        if any(re.search(p, path) for p in TOOLING_PATTERNS):
            tooling.append(path)

        if name in ENTRY_NAMES and path.count("/") <= 3:
            entry_points.append(path)
        if re.search(r"(^|/)cmd/[^/]+/main\.go$", path):
            entry_points.append(path)

        is_test = bool(re.search(r"(^|/)(tests?|__tests__|spec|e2e)/|(_test|\.test|\.spec|_spec)\.\w+$|(^|/)test_[^/]+\.py$", path))
        if is_test:
            tests.append(path)

        if ext in DOC_EXTS or name in AGENT_FILES or path in AGENT_FILES:
            first_heading = next((l.lstrip("# ").strip() for l in text.splitlines() if l.startswith("#")), "")
            docs.append({"path": path, "lines": lines, "title": first_heading[:120]})
            hashes[hashlib.md5(text.encode()).hexdigest()].append(path)
            continue

        if name.startswith(".env") or name.endswith(".env.example") or name.endswith(".env.sample"):
            for var in DOTENV_RE.findall(text):
                dotenv_vars[var].append(path)
            continue

        if not lang and ext not in {".yml", ".yaml", ".json", ".toml", ".ini", ".cfg", ".env", ".conf"}:
            continue

        for i, line in enumerate(text.splitlines(), 1):
            if len(line) > 2000:
                continue
            for pat in ENV_PATTERNS:
                for m in pat.finditer(line):
                    var = m.group(1)
                    if pat.pattern.startswith(r"\$\{") and ext not in {".yml", ".yaml", ".toml", ".properties", ".conf"}:
                        continue
                    if len(env_refs[var]) < args.max_refs:
                        env_refs[var].append(f"{path}:{i}")
                    elif not env_refs[var][-1].startswith("+"):
                        env_refs[var].append("+more")
            if lang:
                for kind, pat in ROUTE_PATTERNS:
                    for m in pat.finditer(line):
                        g = [x for x in m.groups()]
                        if kind == "call" and len(g) == 3:
                            obj, verb, rpath = g
                            if obj in {"os", "self", "dict", "data", "request", "req", "res", "response", "json",
                                       "params", "headers", "cache", "redis", "client", "session", "kwargs",
                                       "body", "config", "settings", "map", "query", "args", "axios", "http_client",
                                       "requests", "httpx", "fetch", "context", "ctx", "localStorage", "store", "env"}:
                                continue
                            routes.append({"kind": "handler", "method": verb.upper(), "path": rpath,
                                           "via": obj, "at": f"{path}:{i}"})
                        elif kind == "decorator":
                            routes.append({"kind": "handler", "method": g[0].upper(), "path": g[-1] or "",
                                           "at": f"{path}:{i}"})
                        elif kind == "prefix":
                            routes.append({"kind": "prefix", "path": g[0], "at": f"{path}:{i}"})
                        elif kind == "mount":
                            a, b = g
                            prefix, target = (a, b) if a.startswith("/") else (b, a)
                            routes.append({"kind": "mount", "path": prefix, "target": target, "at": f"{path}:{i}"})
                        elif kind == "django" and (path.endswith("urls.py")):
                            routes.append({"kind": "handler", "method": "ANY", "path": "/" + g[0], "view": g[1],
                                           "at": f"{path}:{i}"})
                for qm in QUEUE_RE.finditer(line):
                    queues[qm.group(1)].add(path)
                for rk in REDIS_KEY_RE.finditer(line):
                    key = rk.group(1)
                    looks_like_key = ":" in key or key.endswith("_") or "{" in key or "$" in key
                    if looks_like_key and 2 < len(key) < 60 and "/" not in key and not key.startswith("http"):
                        if re.search(r"redis|cache|key", line, re.I):
                            redis_like[key] += 1
            for kind, pat in DATA_PATTERNS.items():
                for m in pat.finditer(line):
                    val = next((x for x in m.groups() if x), None)
                    if val:
                        data_hits[kind][val].add(path)

        m = NEXT_ROUTE_RE.search(path)
        if m and lang in {"TypeScript", "JavaScript"} and ("/app/" in "/" + path or "/pages/" in "/" + path):
            seg = "/" + m.group(2) if m.group(2) else "/"
            if m.group(1) == "app" and m.group(3) in {"page", "route"}:
                next_routes.append({"route": seg, "kind": m.group(3), "file": path})
            elif m.group(1) == "pages" and not name.startswith("_"):
                next_routes.append({"route": seg if m.group(3) != "index" else seg, "kind": "page", "file": path})

    frameworks = sorted({label for dep, label in FRAMEWORK_DEPS.items() if dep.lower() in deps_all})

    history: dict = {}
    if inv["is_git"]:
        log = git(root, "log", f"-{args.history}", "--no-merges", "--name-only",
                  "--format=@@%h|%ad|%s", "--date=short")
        churn: collections.Counter = collections.Counter()
        pairs: collections.Counter = collections.Counter()
        feature_commits = []
        current = None
        commits = []
        for line in log.splitlines():
            if line.startswith("@@"):
                sha, date, subject = (line[2:].split("|", 2) + ["", ""])[:3]
                current = {"sha": sha, "date": date, "subject": subject, "files": []}
                commits.append(current)
            elif line.strip() and current is not None:
                current["files"].append(line.strip())
        file_set = set(files)
        for c in commits:
            live = [f for f in c["files"] if f in file_set and detect_language(f)]
            churn.update(live)
            if 2 <= len(live) <= 12:
                for a in live:
                    for b in live:
                        if a < b:
                            pairs[(a, b)] += 1
            if re.match(r"(feat|feature|add|implement|introduce|support|new)\b", c["subject"], re.I) and live:
                feature_commits.append({"sha": c["sha"], "date": c["date"], "subject": c["subject"][:120],
                                        "files": live[:15], "file_count": len(live)})
        history = {
            "commits_scanned": len(commits),
            "top_churn": [{"file": f, "commits": n} for f, n in churn.most_common(40)],
            "co_change": [{"a": a, "b": b, "together": n} for (a, b), n in pairs.most_common(40) if n >= 3],
            "feature_commits": feature_commits[:60],
        }

    dup_docs = [paths for paths in hashes.values() if len(paths) > 1]

    env_all = sorted(set(env_refs) | set(dotenv_vars))
    inv.update({
        "file_count": len(files),
        "languages": dict(sorted(languages.items(), key=lambda kv: -kv[1]["lines"])),
        "dirs": {d: v for d, v in sorted(dirs.items()) if v["files"] >= 2},
        "largest_files": [{"file": p, "lines": n} for n, p in sorted(sizes, reverse=True)[:30]],
        "manifests": manifests,
        "frameworks": frameworks,
        "infra": infra,
        "tooling": sorted(tooling),
        "entry_points": sorted(set(entry_points)),
        "env_vars": {v: {"read_at": env_refs.get(v, []), "in_env_files": sorted(set(dotenv_vars.get(v, [])))}
                     for v in env_all},
        "routes": routes,
        "file_routes": next_routes,
        "data": {k: {name: sorted(paths)[:5] for name, paths in sorted(v.items())} for k, v in data_hits.items()},
        "cache_key_candidates": [k for k, _ in redis_like.most_common(60)],
        "queue_candidates": {q: sorted(p)[:5] for q, p in sorted(queues.items())},
        "tests": {"count": len(tests), "sample": tests[:30]},
        "docs": sorted(docs, key=lambda d: d["path"]),
        "agent_files": [f for f in AGENT_FILES if (root / f).is_file()],
        "duplicate_docs": dup_docs,
        "history": history,
    })

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(inv, indent=1, default=sorted))

    # Short human summary for the orchestrating agent.
    p = print
    p(f"# Inventory: {root.name}\n")
    if inv.get("git"):
        g = inv["git"]
        p(f"- git: {g['branch']} @ {g['head'][:10]}, {g['commit_count']} commits, {g['first_commit']} → {g['last_commit']}"
          + (f", **{len(g['dirty_files'])} uncommitted files**" if g["dirty_files"] else ""))
    total_lines = sum(v["lines"] for v in inv["languages"].values())
    p(f"- {inv['file_count']} files, {total_lines:,} lines of code")
    p("- languages: " + ", ".join(f"{k} {v['lines']:,}" for k, v in list(inv["languages"].items())[:6]))
    p("- frameworks/libs: " + (", ".join(frameworks) or "none detected"))
    p("- manifests: " + (", ".join(manifests) or "none"))
    p("- entry point candidates: " + (", ".join(inv["entry_points"][:12]) or "none"))
    p("- tooling: " + (", ".join(inv["tooling"][:12]) or "none"))
    p(f"- tests: {len(tests)} files" + (f" (e.g. {', '.join(tests[:3])})" if tests else ""))
    p(f"- env vars: {len(env_all)} ({sum(1 for v in env_all if v in env_refs)} read in code, "
      f"{sum(1 for v in env_all if v in dotenv_vars)} in .env files)")
    handlers = [r for r in routes if r["kind"] == "handler"]
    p(f"- routes: {len(handlers)} handler declarations, {sum(1 for r in routes if r['kind'] != 'handler')} prefixes/mounts, "
      f"{len(next_routes)} file-based routes")
    p("- data hints: " + (", ".join(f"{k} ×{len(v)}" for k, v in inv["data"].items()) or "none"))
    p(f"- docs: {len(docs)} markdown/agent files; agent files present: {', '.join(inv['agent_files']) or 'none'}")
    if dup_docs:
        p("- duplicate doc files (identical content): " + "; ".join(", ".join(d) for d in dup_docs))
    p("\n## Biggest folders (code lines)\n")
    top_dirs = sorted(((v["lines"], d) for d, v in inv["dirs"].items() if d.count("/") <= 3), reverse=True)[:25]
    for n, d in top_dirs:
        p(f"- {d} — {n:,} lines, {inv['dirs'][d]['files']} files")
    if history:
        p("\n## Hot files (most commits)\n")
        for item in history["top_churn"][:12]:
            p(f"- {item['file']} ({item['commits']})")
    p(f"\nFull JSON: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
