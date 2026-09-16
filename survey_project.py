#!/usr/bin/env python3
"""Survey a project tree: inventory, stack detection, and candidate files to read.

Deterministic and read-only. Writes survey.md (for a human/agent to read) and
survey.json (machine-readable) so the analysis phase starts from facts instead of
a dozen exploratory `ls` calls.

Usage:
    python3 survey_project.py <project-root> [--out DIR] [--max-depth N]
                              [--include-vendor] [--top N]

Standard library only; Python 3.8+.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

# Directories that are never the project's own source.
VENDOR_DIRS = {
    "node_modules", ".git", ".hg", ".svn", "dist", "build", "out", ".next", ".nuxt",
    ".svelte-kit", "venv", ".venv", "env", "__pycache__", ".pytest_cache", ".mypy_cache",
    ".ruff_cache", "target", "vendor", "bin", "obj", ".gradle", ".idea", ".vscode",
    "coverage", ".coverage", "htmlcov", ".tox", ".expo", ".turbo", ".parcel-cache",
    "Pods", ".terraform", "site-packages", ".cache", ".yarn", "bower_components",
}

MANIFESTS = {
    "package.json": "node", "pnpm-lock.yaml": "node", "yarn.lock": "node",
    "package-lock.json": "node", "bun.lockb": "node",
    "requirements.txt": "python", "pyproject.toml": "python", "Pipfile": "python",
    "setup.py": "python", "setup.cfg": "python", "environment.yml": "python",
    "go.mod": "go", "Cargo.toml": "rust", "Gemfile": "ruby",
    "composer.json": "php", "pom.xml": "java", "build.gradle": "java",
    "build.gradle.kts": "java", "build.sbt": "scala", "mix.exs": "elixir",
    "pubspec.yaml": "dart", "Package.swift": "swift", "CMakeLists.txt": "c/c++",
}

CONFIG_FILES = {
    # build / tooling
    "tsconfig.json", "jsconfig.json", "vite.config.js", "vite.config.ts",
    "next.config.js", "next.config.mjs", "next.config.ts", "webpack.config.js",
    "rollup.config.js", "babel.config.js", ".babelrc", "svelte.config.js",
    "nuxt.config.ts", "angular.json", "tailwind.config.js", "tailwind.config.ts",
    "postcss.config.js", "eslint.config.js", ".eslintrc", ".eslintrc.js",
    ".eslintrc.json", ".prettierrc", ".prettierrc.json", ".editorconfig",
    "ruff.toml", ".flake8", "mypy.ini", "tox.ini", "manage.py", "artisan",
    # test
    "jest.config.js", "jest.config.ts", "vitest.config.js", "vitest.config.ts",
    "pytest.ini", "playwright.config.ts", "cypress.config.js", "karma.conf.js",
    "phpunit.xml",
    # deploy / infra
    "Dockerfile", "docker-compose.yml", "docker-compose.yaml", "compose.yaml",
    "Procfile", "vercel.json", "netlify.toml", "fly.toml", "railway.json",
    "app.yaml", "nginx.conf", "entrypoint.sh", "Makefile", "Justfile",
    "serverless.yml", "template.yaml", "skaffold.yaml",
    # env / docs
    ".env.example", ".env.sample", ".env.template", ".env.local.example",
    "README.md", "readme.md", "README.rst", "CHANGELOG.md", "CONTRIBUTING.md",
    "AGENTS.md", "CLAUDE.md", "LICENSE", "CODEOWNERS", ".gitignore",
    ".dockerignore", "openapi.json", "openapi.yaml", "swagger.json",
    "schema.prisma", "schema.sql", "schema.rb",
}

LANG_BY_EXT = {
    ".py": "Python", ".js": "JavaScript", ".jsx": "JavaScript (JSX)",
    ".mjs": "JavaScript", ".cjs": "JavaScript", ".ts": "TypeScript",
    ".tsx": "TypeScript (TSX)", ".go": "Go", ".rs": "Rust", ".rb": "Ruby",
    ".php": "PHP", ".java": "Java", ".kt": "Kotlin", ".swift": "Swift",
    ".cs": "C#", ".c": "C", ".h": "C/C++ header", ".cpp": "C++", ".cc": "C++",
    ".scala": "Scala", ".ex": "Elixir", ".exs": "Elixir", ".dart": "Dart",
    ".vue": "Vue", ".svelte": "Svelte", ".html": "HTML", ".css": "CSS",
    ".scss": "SCSS", ".sass": "Sass", ".less": "Less", ".sql": "SQL",
    ".sh": "Shell", ".ps1": "PowerShell", ".md": "Markdown", ".json": "JSON",
    ".yml": "YAML", ".yaml": "YAML", ".toml": "TOML", ".xml": "XML",
    ".graphql": "GraphQL", ".proto": "Protobuf", ".tf": "Terraform",
    ".ipynb": "Jupyter",
}

# name-pattern -> role. Order matters: first match wins.
ROLE_PATTERNS = [
    ("routes", re.compile(r"(^|[/\\])(urls?|routes?|router|routing)\.[a-z]+$", re.I)),
    ("routes", re.compile(r"(^|[/\\])route\.(t|j)sx?$", re.I)),
    ("routes", re.compile(r"(^|[/\\])routes[/\\].*\.(py|js|ts|rb|php)$", re.I)),
    ("models", re.compile(r"(^|[/\\])(models?|schema|schemas|entities|entity)\.[a-z]+$", re.I)),
    ("models", re.compile(r"(^|[/\\])(models|entities|schemas)[/\\].+\.[a-z]+$", re.I)),
    ("models", re.compile(r"schema\.prisma$|schema\.rb$", re.I)),
    ("migrations", re.compile(r"(^|[/\\])(migrations?|migrate|alembic[/\\]versions)[/\\].+", re.I)),
    ("serializers", re.compile(r"(^|[/\\])(serializers?|dto|dtos|schemas?)\.[a-z]+$", re.I)),
    ("views", re.compile(r"(^|[/\\])(views?|viewsets?|controllers?|handlers?|resolvers?)(\.[a-z]+|[/\\].+)$", re.I)),
    ("auth", re.compile(r"(auth|permission|guard|middleware|jwt|session|oauth|rbac)", re.I)),
    ("settings", re.compile(r"(^|[/\\])(settings|config|configuration|conf)(\.[a-z]+|[/\\].+)$", re.I)),
    ("tests", re.compile(r"(^|[/\\])(tests?|__tests__|spec|specs|e2e|cypress)[/\\].+|(test_.+|.+_test|.+\.test|.+\.spec)\.[a-z]+$", re.I)),
    ("components", re.compile(r"(^|[/\\])components?[/\\].+", re.I)),
    ("pages", re.compile(r"(^|[/\\])(pages?|screens?|views|app)[/\\].+\.(jsx?|tsx?|vue|svelte)$", re.I)),
    ("state", re.compile(r"(^|[/\\])(store|stores|reducers?|slices?|context|contexts|atoms)(\.[a-z]+|[/\\].+)$", re.I)),
    ("hooks", re.compile(r"(^|[/\\])hooks?[/\\].+|use[A-Z]\w+\.(jsx?|tsx?)$", re.I)),
    ("api_client", re.compile(r"(^|[/\\])(api|services?|clients?|lib[/\\]api)[/\\].+\.(jsx?|tsx?)$", re.I)),
    ("tasks", re.compile(r"(celery|tasks?|jobs?|workers?|queue|cron|scheduler|management[/\\]commands)", re.I)),
    ("ci", re.compile(r"\.github[/\\]workflows[/\\].+|\.gitlab-ci\.yml$|Jenkinsfile$|azure-pipelines\.yml$|bitbucket-pipelines\.yml$|\.circleci[/\\]config\.yml$", re.I)),
    ("infra", re.compile(r"\.tf$|k8s[/\\].+|kubernetes[/\\].+|helm[/\\].+|charts[/\\].+", re.I)),
]

ENV_READ_RE = re.compile(
    r"""(?:process\.env\.([A-Z][A-Z0-9_]{2,})"""
    r"""|process\.env\[['"]([A-Z][A-Z0-9_]{2,})['"]\]"""
    r"""|import\.meta\.env\.([A-Z][A-Z0-9_]{2,})"""
    r"""|os\.environ(?:\.get)?[\(\[]\s*['"]([A-Z][A-Z0-9_]{2,})['"]"""
    r"""|os\.getenv\(\s*['"]([A-Z][A-Z0-9_]{2,})['"]"""
    r"""|env\(\s*['"]([A-Z][A-Z0-9_]{2,})['"]"""
    r"""|ENV\[['"]([A-Z][A-Z0-9_]{2,})['"]\]"""
    r"""|getenv\(\s*['"]([A-Z][A-Z0-9_]{2,})['"]"""
    r""")"""
)

SOURCE_EXTS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".go", ".rb", ".php",
    ".java", ".kt", ".cs", ".rs", ".vue", ".svelte", ".scala", ".ex", ".exs",
}

# dependency name -> concern, for the tech-stack table
DEP_CONCERNS = [
    ("framework", ["react", "next", "vue", "nuxt", "svelte", "@angular/core", "solid-js",
                   "django", "flask", "fastapi", "express", "@nestjs/core", "fastify",
                   "koa", "rails", "laravel/framework", "spring-boot", "gin-gonic/gin",
                   "actix-web", "phoenix", "hapi", "starlette", "tornado", "sanic"]),
    ("api_layer", ["djangorestframework", "graphql", "@apollo/server", "strawberry-graphql",
                   "trpc", "@trpc/server", "grpc", "drf-spectacular", "flask-restful"]),
    ("styling", ["tailwindcss", "styled-components", "@emotion/react", "sass", "less",
                 "bootstrap", "bulma", "@stitches/react", "unocss", "vanilla-extract"]),
    ("ui_components", ["@mui/material", "antd", "@chakra-ui/react", "@radix-ui/react-dialog",
                       "shadcn", "@headlessui/react", "primevue", "vuetify", "@mantine/core",
                       "react-bootstrap", "@radix-ui/themes"]),
    ("icons", ["lucide-react", "react-icons", "@heroicons/react", "@tabler/icons-react",
               "font-awesome", "@fortawesome/react-fontawesome", "feather-icons",
               "@mui/icons-material", "phosphor-react"]),
    ("charts", ["recharts", "chart.js", "react-chartjs-2", "d3", "victory", "apexcharts",
                "echarts", "plotly.js", "nivo", "@nivo/core", "highcharts", "visx"]),
    ("animation", ["framer-motion", "motion", "react-spring", "@react-spring/web", "gsap",
                   "animejs", "lottie-react", "auto-animate", "@formkit/auto-animate"]),
    ("state", ["redux", "@reduxjs/toolkit", "zustand", "mobx", "recoil", "jotai", "pinia",
               "vuex", "xstate", "valtio", "effector"]),
    ("data_fetching", ["axios", "@tanstack/react-query", "react-query", "swr", "apollo-client",
                       "@apollo/client", "urql", "ky", "got", "requests", "httpx", "aiohttp"]),
    ("forms_validation", ["react-hook-form", "formik", "yup", "zod", "joi", "vee-validate",
                          "pydantic", "marshmallow", "class-validator", "valibot"]),
    ("orm_data", ["prisma", "@prisma/client", "typeorm", "sequelize", "mongoose", "drizzle-orm",
                  "knex", "sqlalchemy", "alembic", "django", "peewee", "tortoise-orm",
                  "gorm.io/gorm", "activerecord", "mikro-orm", "@mikro-orm/core"]),
    ("db_driver", ["pg", "mysql2", "psycopg2", "psycopg2-binary", "psycopg", "mysqlclient",
                   "sqlite3", "redis", "ioredis", "pymongo", "mongodb", "cassandra-driver",
                   "asyncpg", "mssql"]),
    ("auth", ["next-auth", "@auth/core", "passport", "jsonwebtoken", "djangorestframework-simplejwt",
              "pyjwt", "bcrypt", "argon2", "@clerk/nextjs", "firebase-auth", "authlib",
              "devise", "jose", "oauthlib", "django-allauth"]),
    ("testing", ["jest", "vitest", "mocha", "@playwright/test", "cypress", "pytest",
                 "unittest2", "@testing-library/react", "supertest", "rspec", "phpunit",
                 "selenium", "puppeteer", "factory-boy", "faker"]),
    ("build", ["vite", "webpack", "rollup", "esbuild", "parcel", "turbopack", "gulp", "swc"]),
    ("queue_tasks", ["celery", "bullmq", "bull", "agenda", "rq", "sidekiq", "dramatiq",
                     "apscheduler", "django-celery-beat", "node-cron", "temporalio"]),
    ("observability", ["sentry-sdk", "@sentry/react", "@sentry/node", "datadog", "dd-trace",
                       "newrelic", "opentelemetry", "@opentelemetry/api", "prometheus-client",
                       "winston", "pino", "structlog", "loguru"]),
    ("analytics", ["posthog-js", "mixpanel-browser", "@amplitude/analytics-browser",
                   "@segment/analytics-next", "@vercel/analytics", "react-ga4",
                   "google-analytics", "plausible-tracker", "heap-api"]),
    ("notifications", ["nodemailer", "@sendgrid/mail", "twilio", "resend", "postmark",
                       "firebase-admin", "web-push", "react-hot-toast", "react-toastify",
                       "sonner", "django-anymail", "mailgun", "expo-notifications"]),
    ("feature_flags", ["launchdarkly-js-client-sdk", "@unleash/proxy-client-react",
                       "unleash-client", "flagsmith", "@growthbook/growthbook",
                       "django-waffle", "flipper"]),
    ("storage_cloud", ["@aws-sdk/client-s3", "boto3", "aws-sdk", "@google-cloud/storage",
                       "@azure/storage-blob", "cloudinary", "multer", "django-storages",
                       "minio"]),
    ("payments", ["stripe", "@stripe/stripe-js", "razorpay", "braintree", "paypal-rest-sdk",
                  "square", "paddle-sdk"]),
]


def is_vendor(parts) -> bool:
    return any(p in VENDOR_DIRS for p in parts)


def classify_role(rel: str):
    for role, pat in ROLE_PATTERNS:
        if pat.search(rel):
            return role
    return None


def read_text(path: Path, limit: int = 400_000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:limit]
    except Exception:
        return ""


def parse_node_deps(path: Path):
    out = {}
    try:
        data = json.loads(read_text(path))
    except Exception:
        return out, {}
    meta = {k: data.get(k) for k in ("name", "version", "description", "private", "type")
            if data.get(k) is not None}
    if isinstance(data.get("scripts"), dict):
        meta["scripts"] = data["scripts"]
    if isinstance(data.get("workspaces"), (list, dict)):
        meta["workspaces"] = data["workspaces"]
    if isinstance(data.get("engines"), dict):
        meta["engines"] = data["engines"]
    for key in ("dependencies", "devDependencies", "peerDependencies"):
        for name, ver in (data.get(key) or {}).items():
            out[name] = str(ver)
    return out, meta


def parse_requirements(path: Path):
    out = {}
    for line in read_text(path).splitlines():
        line = line.split("#")[0].strip()
        if not line or line.startswith("-"):
            continue
        m = re.match(r"^([A-Za-z0-9._\-\[\]]+)\s*([=<>!~]+.*)?$", line)
        if m:
            out[m.group(1).lower()] = (m.group(2) or "").strip()
    return out


def parse_pyproject(path: Path):
    out, meta = {}, {}
    txt = read_text(path)
    m = re.search(r'^name\s*=\s*["\']([^"\']+)', txt, re.M)
    if m:
        meta["name"] = m.group(1)
    m = re.search(r'^description\s*=\s*["\']([^"\']+)', txt, re.M)
    if m:
        meta["description"] = m.group(1)
    m = re.search(r"dependencies\s*=\s*\[(.*?)\]", txt, re.S)
    if m:
        for dep in re.findall(r'["\']([^"\']+)["\']', m.group(1)):
            d = re.match(r"^([A-Za-z0-9._\-\[\]]+)\s*(.*)$", dep)
            if d:
                out[d.group(1).lower()] = d.group(2).strip()
    for dep, ver in re.findall(r'^([A-Za-z0-9._\-]+)\s*=\s*["\']([^"\']+)["\']\s*$',
                               txt.split("[tool.poetry.dependencies]")[-1], re.M) \
            if "[tool.poetry.dependencies]" in txt else []:
        out.setdefault(dep.lower(), ver)
    return out, meta


def parse_go_mod(path: Path):
    out, meta = {}, {}
    txt = read_text(path)
    m = re.search(r"^module\s+(\S+)", txt, re.M)
    if m:
        meta["name"] = m.group(1)
    m = re.search(r"^go\s+(\S+)", txt, re.M)
    if m:
        meta["go_version"] = m.group(1)
    for name, ver in re.findall(r"^\s*([\w./\-]+)\s+(v\S+)", txt, re.M):
        out[name] = ver
    return out, meta


def parse_generic_deps(path: Path, name: str):
    """Gemfile / composer.json / pom.xml / Cargo.toml — light extraction."""
    out, meta = {}, {}
    txt = read_text(path)
    if name == "composer.json":
        try:
            data = json.loads(txt)
            meta = {k: data[k] for k in ("name", "description") if k in data}
            for key in ("require", "require-dev"):
                for n, v in (data.get(key) or {}).items():
                    out[n] = str(v)
        except Exception:
            pass
    elif name == "Gemfile":
        for n, v in re.findall(r"gem\s+['\"]([^'\"]+)['\"](?:\s*,\s*['\"]([^'\"]+)['\"])?", txt):
            out[n] = v
    elif name == "Cargo.toml":
        m = re.search(r'^name\s*=\s*["\']([^"\']+)', txt, re.M)
        if m:
            meta["name"] = m.group(1)
        block = txt.split("[dependencies]")[-1].split("\n[")[0] if "[dependencies]" in txt else ""
        for n, v in re.findall(r'^([A-Za-z0-9_\-]+)\s*=\s*["\']([^"\']+)["\']', block, re.M):
            out[n] = v
    elif name == "pom.xml":
        m = re.search(r"<artifactId>([^<]+)</artifactId>", txt)
        if m:
            meta["name"] = m.group(1)
        for g, a, v in re.findall(
                r"<dependency>\s*<groupId>([^<]+)</groupId>\s*<artifactId>([^<]+)</artifactId>"
                r"(?:\s*<version>([^<]+)</version>)?", txt):
            out[f"{g}:{a}"] = v or ""
    elif name in ("build.gradle", "build.gradle.kts"):
        for dep in re.findall(r"""(?:implementation|api|compile)\s*[\("']+([^\s"')]+)""", txt):
            out[dep] = ""
    return out, meta


def lockfile_versions(root: Path):
    """Resolved versions, which are what the code actually runs against."""
    resolved = {}
    pl = root / "package-lock.json"
    if pl.exists():
        try:
            data = json.loads(read_text(pl, 8_000_000))
            for pkg, info in (data.get("packages") or {}).items():
                if pkg.startswith("node_modules/") and isinstance(info, dict) and info.get("version"):
                    name = pkg.split("node_modules/")[-1]
                    if "/node_modules/" not in pkg:
                        resolved[name] = info["version"]
            for name, info in (data.get("dependencies") or {}).items():
                if isinstance(info, dict) and info.get("version"):
                    resolved.setdefault(name, info["version"])
        except Exception:
            pass
    for lock, pat in (("yarn.lock", r'^"?([^@\s"]+(?:@[^@\s"]+)?)@[^:\n]+:\n\s+version:? "?([^"\n]+)'),
                      ("pnpm-lock.yaml", r"^\s{2}/?([^@\s/][^:@\n]*)@([\d][^:\s(]*)")):
        p = root / lock
        if p.exists():
            for name, ver in re.findall(pat, read_text(p, 4_000_000), re.M):
                resolved.setdefault(name.strip(), ver.strip())
    for lock, pat in (("poetry.lock", r'name = "([^"]+)"\nversion = "([^"]+)"'),
                      ("uv.lock", r'name = "([^"]+)"\nversion = "([^"]+)"'),
                      ("Gemfile.lock", r"^\s{4}([a-z0-9_\-]+) \(([^)]+)\)"),
                      ("composer.lock", r'"name": "([^"]+)",\s*\n\s*"version": "([^"]+)"')):
        p = root / lock
        if p.exists():
            for name, ver in re.findall(pat, read_text(p, 4_000_000), re.M):
                resolved.setdefault(name.strip(), ver.strip())
    return resolved


def concern_map(deps):
    """Group dependencies by concern; flags concerns covered by 2+ libraries."""
    found = defaultdict(list)
    lower = {k.lower(): k for k in deps}
    for concern, names in DEP_CONCERNS:
        for n in names:
            nl = n.lower()
            for dep_lower, dep_orig in lower.items():
                if dep_lower == nl or dep_lower.endswith("/" + nl) or dep_lower.startswith(nl + "/"):
                    if dep_orig not in found[concern]:
                        found[concern].append(dep_orig)
    return dict(found)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", help="project root to survey")
    ap.add_argument("--out", default="survey", help="output prefix/dir (default: ./survey)")
    ap.add_argument("--max-depth", type=int, default=4, help="tree depth to render (default 4)")
    ap.add_argument("--include-vendor", action="store_true",
                    help="do not skip node_modules/venv/etc (rarely useful)")
    ap.add_argument("--top", type=int, default=40,
                    help="how many candidate files to list per role (default 40)")
    args = ap.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 2

    files, dirs = [], []
    skipped_vendor = Counter()
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = Path(dirpath).relative_to(root)
        parts = rel_dir.parts
        if not args.include_vendor:
            for d in list(dirnames):
                if d in VENDOR_DIRS:
                    skipped_vendor[d] += 1
                    dirnames.remove(d)
            if is_vendor(parts):
                continue
        dirnames.sort()
        if parts:
            dirs.append(rel_dir.as_posix())
        for fn in sorted(filenames):
            p = Path(dirpath) / fn
            rel = (rel_dir / fn).as_posix()
            try:
                size = p.stat().st_size
            except OSError:
                size = 0
            files.append({"path": rel, "name": fn, "ext": p.suffix.lower(), "size": size})

    # languages
    lang_counts, lang_bytes = Counter(), Counter()
    for f in files:
        lang = LANG_BY_EXT.get(f["ext"])
        if lang:
            lang_counts[lang] += 1
            lang_bytes[lang] += f["size"]

    # manifests, configs, roles
    manifests, configs = [], []
    roles = defaultdict(list)
    for f in files:
        if f["name"] in MANIFESTS:
            manifests.append({"path": f["path"], "ecosystem": MANIFESTS[f["name"]]})
        if f["name"] in CONFIG_FILES or f["name"].startswith(".env"):
            configs.append(f["path"])
        role = classify_role(f["path"])
        if role:
            roles[role].append(f["path"])
        elif f["path"].startswith(".github/workflows/"):
            roles["ci"].append(f["path"])

    # dependencies
    deps, meta_all = {}, {}
    for m in manifests:
        p = root / m["path"]
        name = p.name
        if name == "package.json":
            d, meta = parse_node_deps(p)
        elif name in ("requirements.txt",):
            d, meta = parse_requirements(p), {}
        elif name == "pyproject.toml":
            d, meta = parse_pyproject(p)
        elif name == "go.mod":
            d, meta = parse_go_mod(p)
        elif name in ("composer.json", "Gemfile", "Cargo.toml", "pom.xml",
                      "build.gradle", "build.gradle.kts"):
            d, meta = parse_generic_deps(p, name)
        else:
            continue
        if d:
            deps[m["path"]] = d
        if meta:
            meta_all[m["path"]] = meta

    resolved = lockfile_versions(root)
    for sub in {Path(m["path"]).parent for m in manifests}:
        if str(sub) != ".":
            resolved.update(lockfile_versions(root / sub))

    all_deps = {}
    for d in deps.values():
        all_deps.update(d)
    concerns = concern_map(all_deps)

    # "One library per concern" is a rule *within* one app. In a repo with a separate
    # backend and frontend, react + django both landing in "framework" is the normal
    # shape, not a violation — so only flag a concern covered twice inside a single
    # manifest's own dependency set.
    ONE_PER_CONCERN = {"framework", "styling", "ui_components", "icons", "charts",
                       "animation", "state", "analytics", "feature_flags"}
    conflicts = {}
    for manifest_path, d in deps.items():
        for concern, libs in concern_map(d).items():
            if concern in ONE_PER_CONCERN and len(libs) > 1:
                conflicts.setdefault(concern, {"libraries": [], "manifests": []})
                for lib in libs:
                    if lib not in conflicts[concern]["libraries"]:
                        conflicts[concern]["libraries"].append(lib)
                if manifest_path not in conflicts[concern]["manifests"]:
                    conflicts[concern]["manifests"].append(manifest_path)

    # env vars: declared in .env* examples and read from source
    env_declared, env_read = {}, Counter()
    for f in files:
        if f["name"].startswith(".env"):
            for line in read_text(root / f["path"], 100_000).splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key = line.split("=", 1)[0].strip()
                    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key or ""):
                        env_declared.setdefault(key, []).append(f["path"])
    source_files = [f for f in files if f["ext"] in SOURCE_EXTS and f["size"] < 2_000_000]
    for f in source_files[:4000]:
        for groups in ENV_READ_RE.findall(read_text(root / f["path"], 300_000)):
            for g in groups:
                if g:
                    env_read[g] += 1

    # entry points
    ENTRY_HINTS = ["manage.py", "main.py", "app.py", "wsgi.py", "asgi.py", "server.py",
                   "index.js", "index.ts", "main.js", "main.ts", "main.jsx", "main.tsx",
                   "server.js", "app.js", "app.jsx", "App.jsx", "App.tsx", "main.go",
                   "index.html", "artisan", "Program.cs", "main.rs"]
    entries = [f["path"] for f in files if f["name"] in ENTRY_HINTS and f["path"].count("/") <= 3]

    # directory tree
    tree_lines = []

    def walk_tree(d: Path, prefix: str, depth: int):
        if depth > args.max_depth:
            return
        try:
            kids = sorted(d.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
        except OSError:
            return
        kids = [k for k in kids if args.include_vendor or k.name not in VENDOR_DIRS]
        shown = [k for k in kids if k.is_dir()] + [k for k in kids if k.is_file()][:12]
        hidden = len(kids) - len(shown)
        for i, k in enumerate(shown):
            last = i == len(shown) - 1 and hidden == 0
            tree_lines.append(f"{prefix}{'└── ' if last else '├── '}{k.name}{'/' if k.is_dir() else ''}")
            if k.is_dir():
                walk_tree(k, prefix + ("    " if last else "│   "), depth + 1)
        if hidden > 0:
            tree_lines.append(f"{prefix}└── … {hidden} more entr{'y' if hidden == 1 else 'ies'}")

    tree_lines.append(f"{root.name}/")
    walk_tree(root, "", 1)

    biggest = sorted((f for f in files if f["ext"] in SOURCE_EXTS),
                     key=lambda f: -f["size"])[:20]

    survey = {
        "root": str(root),
        "project_dir_name": root.name,
        "counts": {"files": len(files), "dirs": len(dirs),
                   "skipped_vendor_dirs": dict(skipped_vendor)},
        "languages": [{"language": k, "files": v, "bytes": lang_bytes[k]}
                      for k, v in lang_counts.most_common()],
        "manifests": manifests,
        "manifest_metadata": meta_all,
        "dependencies_declared": deps,
        "dependencies_resolved": {k: resolved[k] for k in sorted(set(all_deps) & set(resolved))},
        "concerns": concerns,
        "concern_conflicts": conflicts,
        "config_files": sorted(configs),
        "entry_points": sorted(entries),
        "candidates_by_role": {k: sorted(v)[:args.top] for k, v in sorted(roles.items())},
        "candidates_by_role_counts": {k: len(v) for k, v in sorted(roles.items())},
        "env_vars_declared": env_declared,
        "env_vars_read_in_source": dict(env_read.most_common()),
        "largest_source_files": [{"path": f["path"], "size": f["size"]} for f in biggest],
        "tree": tree_lines,
    }

    out = Path(args.out).expanduser()
    out.mkdir(parents=True, exist_ok=True) if out.suffix == "" else out.parent.mkdir(parents=True, exist_ok=True)
    base = out / "survey" if out.suffix == "" else out
    json_path, md_path = base.with_suffix(".json"), base.with_suffix(".md")
    json_path.write_text(json.dumps(survey, indent=2), encoding="utf-8")

    L = []
    a = L.append
    a(f"# Project survey — `{root.name}`\n")
    a(f"Root: `{root}`  ")
    a(f"{len(files)} files in {len(dirs)} directories (vendor/build dirs excluded)\n")

    a("## Languages\n")
    a("| Language | Files | Bytes |")
    a("|---|---:|---:|")
    for row in survey["languages"][:15]:
        a(f"| {row['language']} | {row['files']} | {row['bytes']:,} |")
    a("")

    a("## Manifests and metadata\n")
    if manifests:
        for m in manifests:
            meta = meta_all.get(m["path"], {})
            bits = ", ".join(f"{k}={v}" for k, v in meta.items()
                             if k in ("name", "version", "description", "go_version"))
            a(f"- `{m['path']}` ({m['ecosystem']}){' — ' + bits if bits else ''}")
        for path, meta in meta_all.items():
            if meta.get("scripts"):
                a(f"\n  Scripts in `{path}`:")
                for k, v in meta["scripts"].items():
                    a(f"  - `{k}`: `{v}`")
    else:
        a("- none found (check for an unusual build system)")
    a("")

    a("## Dependencies by concern\n")
    a("Resolved versions come from lockfiles and are what the code actually runs against.\n")
    a("| Concern | Libraries (resolved version) |")
    a("|---|---|")
    for concern, names in sorted(concerns.items()):
        rendered = ", ".join(f"`{n}`" + (f" {resolved.get(n, all_deps.get(n, ''))}"
                                        if (resolved.get(n) or all_deps.get(n)) else "")
                             for n in names)
        a(f"| {concern} | {rendered} |")
    a("")
    if conflicts:
        a("> **Two or more libraries for one concern inside the same app** — the template "
          "treats this as review-blocking. Verify by reading the imports (one may be dead "
          "weight), then record it in `docs/AGENTS.md` rather than listing both as approved:\n")
        for c, info in conflicts.items():
            libs = ", ".join("`" + x + "`" for x in info["libraries"])
            where = ", ".join("`" + m + "`" for m in info["manifests"])
            a(f"> - **{c}**: {libs} — declared in {where}")
        a("")

    a("## Entry points\n")
    for e in entries or ["(none detected)"]:
        a(f"- `{e}`")
    a("")

    a("## Config / infra / docs files\n")
    for c in configs or ["(none detected)"]:
        a(f"- `{c}`")
    a("")

    a("## Candidate files to read, by role\n")
    a("These are name-pattern matches, not verified facts. Read them to confirm.\n")
    for role, paths in survey["candidates_by_role"].items():
        total = survey["candidates_by_role_counts"][role]
        a(f"### {role} ({total})\n")
        for p in paths:
            a(f"- `{p}`")
        if total > len(paths):
            a(f"- … {total - len(paths)} more")
        a("")

    a("## Environment variables\n")
    if env_declared:
        a("Declared in `.env*` files (names only — never copy values into docs):\n")
        for k, where in sorted(env_declared.items()):
            a(f"- `{k}` — in {', '.join('`' + w + '`' for w in sorted(set(where)))}")
        a("")
    if env_read:
        a("Read from source:\n")
        for k, n in sorted(env_read.items()):
            a(f"- `{k}` ({n} reference{'s' if n != 1 else ''})")
        a("")
    undeclared = sorted(set(env_read) - set(env_declared))
    if undeclared:
        a(f"Read in source but **not** in any `.env*` example: "
          f"{', '.join('`' + u + '`' for u in undeclared)} — worth a note in "
          f"`15-environment-setup.md`.\n")

    a("## Largest source files\n")
    a("Usually where the real logic lives — read these early.\n")
    for f in biggest:
        a(f"- `{f['path']}` ({f['size']:,} bytes)")
    a("")

    a("## Directory tree\n")
    a("```")
    L.extend(tree_lines)
    a("```")

    md_path.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"wrote {md_path}\nwrote {json_path}")
    print(f"\n{len(files)} files · "
          f"{', '.join(r['language'] for r in survey['languages'][:4])} · "
          f"{len(manifests)} manifest(s) · {len(concerns)} concern(s) detected")
    if conflicts:
        print(f"NOTE: multiple libraries for: {', '.join(conflicts)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
