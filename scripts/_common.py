"""Shared helpers for the ai-docs scripts. Python standard library only."""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

SKIP_DIRS = {
    ".git", "node_modules", ".venv", "venv", "env", "__pycache__", "dist", "build",
    ".next", ".nuxt", "out", "coverage", ".mypy_cache", ".pytest_cache", ".ruff_cache",
    "vendor", "target", ".idea", ".vscode", ".turbo", ".cache", ".claude",
}

LOCK_FILES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock", "Pipfile.lock",
    "Cargo.lock", "go.sum", "composer.lock", "Gemfile.lock", "uv.lock", "bun.lockb",
}

BINARY_EXTS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".svg", ".pdf", ".zip", ".gz",
    ".tar", ".woff", ".woff2", ".ttf", ".otf", ".eot", ".mp3", ".mp4", ".mov", ".wav",
    ".jar", ".class", ".so", ".dylib", ".dll", ".exe", ".pyc", ".rdb", ".db", ".sqlite",
    ".lockb", ".bin", ".pkl", ".parquet",
}

CODE_EXTS = {
    ".py": "Python", ".js": "JavaScript", ".jsx": "JavaScript", ".mjs": "JavaScript",
    ".cjs": "JavaScript", ".ts": "TypeScript", ".tsx": "TypeScript", ".go": "Go",
    ".rs": "Rust", ".java": "Java", ".kt": "Kotlin", ".kts": "Kotlin", ".rb": "Ruby",
    ".php": "PHP", ".cs": "C#", ".swift": "Swift", ".m": "Objective-C", ".scala": "Scala",
    ".ex": "Elixir", ".exs": "Elixir", ".dart": "Dart", ".vue": "Vue", ".svelte": "Svelte",
    ".c": "C", ".h": "C", ".cpp": "C++", ".hpp": "C++", ".sql": "SQL", ".sh": "Shell",
    ".graphql": "GraphQL", ".proto": "Protobuf", ".prisma": "Prisma",
}

DOC_EXTS = {".md", ".mdx", ".rst", ".txt", ".adoc"}

MAX_TEXT_BYTES = 1_500_000


def git(root: Path, *args: str, check: bool = False) -> str:
    """Run a git command in root and return stdout ('' on failure unless check)."""
    try:
        out = subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True, text=True, check=check,
        )
    except (OSError, subprocess.CalledProcessError):
        if check:
            raise
        return ""
    return out.stdout if out.returncode == 0 else ""


def is_git_repo(root: Path) -> bool:
    return git(root, "rev-parse", "--is-inside-work-tree").strip() == "true"


def list_files(root: Path) -> list[str]:
    """Repo-relative POSIX paths of tracked + untracked-not-ignored files."""
    if is_git_repo(root):
        out = git(root, "ls-files", "--cached", "--others", "--exclude-standard")
        files = [f for f in out.splitlines() if f]
        # Drop files deleted in the working tree but still in the index.
        return sorted({f for f in files if (root / f).is_file()})
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            rel = os.path.relpath(os.path.join(dirpath, name), root)
            files.append(Path(rel).as_posix())
    return sorted(files)


def in_skipped_dir(path: str) -> bool:
    return any(part in SKIP_DIRS for part in path.split("/")[:-1])


def is_text_candidate(path: str) -> bool:
    name = path.rsplit("/", 1)[-1]
    if name in LOCK_FILES:
        return False
    ext = os.path.splitext(name)[1].lower()
    return ext not in BINARY_EXTS and not name.endswith(".min.js")


def read_text(root: Path, path: str) -> str | None:
    full = root / path
    try:
        if full.stat().st_size > MAX_TEXT_BYTES:
            return None
        data = full.read_bytes()
    except OSError:
        return None
    if b"\x00" in data[:4096]:
        return None
    return data.decode("utf-8", errors="replace")


def glob_to_regex(pattern: str) -> re.Pattern[str]:
    """Translate a gitignore-style glob (supports **) to a full-match regex."""
    i, out = 0, []
    while i < len(pattern):
        c = pattern[i]
        if pattern.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif pattern.startswith("**", i):
            out.append(".*")
            i += 2
        elif c == "*":
            out.append("[^/]*")
            i += 1
        elif c == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(c))
            i += 1
    return re.compile("".join(out) + r"\Z")


def match_any(path: str, patterns: list[str]) -> bool:
    for pat in patterns:
        pat = pat.strip()
        if not pat:
            continue
        if pat.endswith("/"):
            pat += "**"
        if glob_to_regex(pat).match(path):
            return True
    return False


FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", re.S)


def parse_frontmatter(text: str) -> tuple[dict, int]:
    """Parse the small YAML subset the docs use. Returns (data, body_start_line).

    Supports `key: value`, `key: [a, "b"]` and block lists (`key:` then `  - item`).
    """
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, 0
    data: dict = {}
    current_list_key = None
    for raw in m.group(1).splitlines():
        line = raw.split(" #", 1)[0].rstrip()
        if not line.strip():
            continue
        stripped = line.strip()
        if stripped.startswith("- ") and current_list_key:
            data[current_list_key].append(_unquote(stripped[2:].strip()))
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key, value = key.strip(), value.strip()
        if value == "":
            data[key] = []
            current_list_key = key
            continue
        current_list_key = None
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            data[key] = [_unquote(v.strip()) for v in inner.split(",") if v.strip()] if inner else []
        else:
            data[key] = _unquote(value)
    body_start = text[: m.end()].count("\n")
    return data, body_start


def _unquote(v: str) -> str:
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    return v


def default_doc_paths(root: Path, files: list[str]) -> list[str]:
    """The doc set ai-docs owns: AGENTS.md, CLAUDE.md and docs/**/*.md.

    Skips in-repo templates and the docs the manifest lists as `superseded`
    (older docs the user chose to keep; they are not maintained).
    """
    superseded = set(load_manifest(root).get("superseded") or [])
    docs = [f for f in ("AGENTS.md", "CLAUDE.md") if (root / f).is_file()]
    docs += [f for f in files if f.startswith("docs/") and f.endswith(".md")
             and not f.rsplit("/", 1)[-1].upper().startswith("_TEMPLATE")]
    return sorted(set(docs) - superseded)


def load_manifest(root: Path) -> dict:
    path = root / "docs" / ".ai-docs.json"
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def github_slug(heading: str) -> str:
    """GitHub-style heading anchor."""
    s = heading.strip().lower()
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"[`*_~\[\]()]", lambda m: "_" if m.group(0) == "_" else "", s)
    s = re.sub(r"[^\w\- ]", "", s)
    return s.replace(" ", "-")
