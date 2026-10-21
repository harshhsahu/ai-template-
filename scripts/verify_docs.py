#!/usr/bin/env python3
"""Check every verifiable claim in a repo's AI docs against the code.

What it checks (outside fenced code blocks and HTML comments):
  `path`               file or folder exists (repo-root relative); globs must match
  `path:42` `path:3-9` file exists and has that many lines
  `path:symbol`        file exists and contains the symbol (also `path::symbol`)
  `snake_case_name`    identifier appears somewhere in the code (catches made-up names)
  `camelCase` / `PascalCaseName` / `obj.method()`  same (dotted names only warn)
  `UPPER_SNAKE`        env var / constant appears in code or .env files
  `GET /x/{id}` `/x/y` route appears in code (warning only: prefixes are composed)
  [text](rel.md#anchor) link target and heading anchor exist
  frontmatter `covers` globs match files; `verified_at` is a known commit
  size budgets (AGENTS.md <= 150 lines, other docs <= 450) and [!TODO] count
  coverage (default doc set only): every env var the code reads appears in
    docs/environment.md, and every route path it declares appears in docs/api.md

Add `<!-- verify:ignore -->` to a line to skip it, or wrap a block in
`<!-- verify:ignore-start -->` ... `<!-- verify:ignore-end -->` (for rejected
alternatives, scope tables of another repo, or fields of an external API).

Usage: python3 verify_docs.py [repo_root] [--docs a.md b.md] [--json]
Exit code 1 when any ERROR is found.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    default_doc_paths, git, github_slug, glob_to_regex, in_skipped_dir, is_git_repo,
    is_text_candidate, list_files, parse_frontmatter, read_text,
)

FILE_EXTS = {
    "py", "js", "jsx", "mjs", "cjs", "ts", "tsx", "go", "rs", "java", "kt", "rb", "php", "cs",
    "swift", "scala", "ex", "exs", "dart", "vue", "svelte", "c", "h", "cpp", "hpp", "sql", "sh",
    "json", "jsonc", "yaml", "yml", "toml", "ini", "cfg", "md", "mdx", "txt", "html", "css",
    "scss", "prisma", "graphql", "proto", "lock", "xml", "gradle", "example", "sample", "conf",
}
ABS_FS_PREFIXES = ("/usr/", "/etc/", "/tmp/", "/var/", "/Users/", "/home/", "/opt/", "/bin/", "/dev/", "/private/")
HTTP_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS", "ANY", "ALL", "WS", "SSE"}

SPAN_RE = re.compile(r"(`+)(.+?)\1")
LINK_RE = re.compile(r"(?<!!)\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
PATH_LINE_RE = re.compile(r"^([^\s:`]+\.[A-Za-z0-9]+|[^\s:`]*/[^\s:`]*):(\d+)(?:-(\d+))?$")
PATH_SYMBOL_RE = re.compile(r"^([^\s:`]+\.[A-Za-z0-9]+)::?([A-Za-z_][\w.]*)(?:\(\))?$")
IDENTIFIER_SPAN_RE = re.compile(r"^[A-Za-z_][\w]*(?:\.[A-Za-z_]\w*)*(?:\(\))?$")
ROUTE_WITH_METHOD_RE = re.compile(r"^([A-Z]+)\s+(/\S*)$")
CONST_RE = re.compile(r"^[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+_?$")
# Names that belong to the language or runtime, not to the repo.
BUILTINS = {
    "TypeError", "ValueError", "KeyError", "RuntimeError", "AttributeError", "IndexError",
    "NotImplementedError", "StopIteration", "TimeoutError", "ConnectionError", "PermissionError",
    "FileNotFoundError", "OSError", "IOError", "ImportError", "SyntaxError", "ReferenceError",
    "RangeError", "AssertionError", "ZeroDivisionError", "UnicodeDecodeError", "CancelledError",
    "AbortController", "AbortSignal", "ReadableStream", "WritableStream", "TextDecoder", "TextEncoder",
    "FormData", "URLSearchParams", "EventSource", "WebSocket", "localStorage", "sessionStorage",
    "setTimeout", "setInterval", "clearTimeout", "clearInterval", "structuredClone", "BigInt",
    "ArrayBuffer", "Uint8Array", "DataView", "MutationObserver", "IntersectionObserver",
    "ResizeObserver", "requestAnimationFrame", "getElementById", "querySelector", "addEventListener",
    "isinstance", "getattr", "setattr", "hasattr", "staticmethod", "classmethod", "NoneType",
    "asyncio", "await", "async_generator", "__init__", "__name__", "__main__", "__dict__",
}
RUNTIME_ENV = {
    "NODE_OPTIONS", "NODE_ENV", "PYTHONPATH", "PYTHONUNBUFFERED", "PYTHONDONTWRITEBYTECODE", "PATH",
    "HOME", "TZ", "LANG", "LC_ALL", "CI", "DEBUG", "GOOGLE_APPLICATION_CREDENTIALS", "GOPATH",
    "GOOS", "GOARCH", "JAVA_HOME", "VIRTUAL_ENV", "XDG_CONFIG_HOME", "TMPDIR", "SHELL", "USER",
}
STRATEGIC_DOCS = {
    "docs/README.md", "docs/VISION.md", "docs/DECISIONS.md", "docs/OPEN_QUESTIONS.md",
    "docs/readme.md", "docs/vision.md", "docs/decisions.md", "docs/open_questions.md",
}


class Report:
    def __init__(self) -> None:
        self.items: list[dict] = []
        self.checked = 0

    def add(self, level: str, doc: str, line: int, msg: str) -> None:
        self.items.append({"level": level, "doc": doc, "line": line, "msg": msg})


class Repo:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.files = list_files(root)
        self.file_set = set(self.files)
        self.dir_set = set()
        for f in self.files:
            parts = f.split("/")
            for i in range(1, len(parts)):
                self.dir_set.add("/".join(parts[:i]))
        self.top_level = {f.split("/", 1)[0] for f in self.files}
        self.basenames: dict[str, list[str]] = {}
        for f in self.files:
            self.basenames.setdefault(f.rsplit("/", 1)[-1], []).append(f)
        self._text_cache: dict[str, str | None] = {}
        self.tokens: set[str] = set()
        chunks = []
        for f in self.files:
            if in_skipped_dir(f) or not is_text_candidate(f):
                continue
            if f.endswith((".md", ".mdx", ".rst", ".adoc")):
                continue
            text = self.text(f)
            if text is None:
                continue
            self.tokens.update(IDENT_RE.findall(text))
            chunks.append(text)
        self.corpus = "\n".join(chunks)
        self.is_git = is_git_repo(root)

    def text(self, path: str) -> str | None:
        if path not in self._text_cache:
            self._text_cache[path] = read_text(self.root, path)
        return self._text_cache[path]

    def exists(self, path: str) -> bool:
        p = path.rstrip("/")
        return p in self.file_set or p in self.dir_set or (self.root / p).exists()

    def glob_matches(self, pattern: str) -> list[str]:
        if pattern.endswith("/"):
            pattern += "**"
        rx = glob_to_regex(pattern)
        return [f for f in self.files if rx.match(f)]

    def suffix_match(self, path: str) -> list[str]:
        p = path.rstrip("/")
        hits = [f for f in self.files if f.endswith("/" + p)]
        hits += [d for d in self.dir_set if d.endswith("/" + p)]
        return sorted(set(hits))[:3]


def resolve_path(repo: Repo, doc: str, raw: str) -> tuple[str | None, list[str]]:
    """Return (repo-relative path if found, suggestions)."""
    p = raw.strip().lstrip("./") if raw.startswith("./") else raw.strip()
    if repo.exists(p):
        return p.rstrip("/"), []
    rel = os.path.normpath(os.path.join(os.path.dirname(doc), p))
    if not rel.startswith("..") and repo.exists(rel):
        return rel, []
    return None, repo.suffix_match(p)


def looks_like_path(span: str, repo: Repo) -> bool:
    if " " in span or span.startswith(("@", "http://", "https://", "-", "$", "~")):
        return False
    if any(ch in span for ch in "{}<>$|=,;()'\"\\"):
        return False
    if "/" in span:
        first = span.lstrip("./").split("/", 1)[0]
        last = span.rstrip("/").rsplit("/", 1)[-1]
        has_ext = "." in last and last.rsplit(".", 1)[-1].lower() in FILE_EXTS
        return first in repo.top_level or has_ext or span.endswith("/") or first in {"src", "app", "lib", "docs"}
    name = span.rsplit("/", 1)[-1]
    if name.startswith(".env") or name in {"Dockerfile", "Makefile", "Procfile"}:
        return True
    return "." in name and name.rsplit(".", 1)[-1].lower() in FILE_EXTS and not name[0].isupper() or name in repo.basenames


def route_found(repo: Repo, route: str) -> bool:
    segs = [s for s in route.split("?")[0].split("/") if s]
    static = []
    for s in segs:
        if re.match(r"^(\{.*\}|:.+|<.*>|\[.*\]|\*.*)$", s) or "," in s:
            static.append(None)
        else:
            static.append(s)
    # Try the longest run of trailing static segments first, down to one segment.
    candidates = []
    for start in range(len(static)):
        run = static[start:]
        if any(x is None for x in run) or not run:
            continue
        candidates.append("/" + "/".join(run))
    lone = [s for s in static if s]
    if not lone:
        return True
    for cand in candidates:
        if cand in repo.corpus or any(cand.strip("/") in f for f in repo.files):
            return True
    # Route segments separated by params: require every static segment to appear.
    return all(("/" + s) in repo.corpus or ("'" + s) in repo.corpus or ('"' + s) in repo.corpus for s in lone)


def check_identifier(repo: Repo, span: str) -> tuple[str, str] | None:
    """Return (level, message) when the identifier cannot be found, else None."""
    name = span[:-2] if span.endswith("()") else span
    parts = name.split(".")
    if name in BUILTINS or name in RUNTIME_ENV:
        return None
    if CONST_RE.match(name):
        if name not in repo.tokens:
            return "ERROR", f"env var / constant not found in code: `{span}`"
        return None
    if len(parts) > 1:
        missing = [p for p in parts if len(p) > 2 and p not in repo.tokens]
        if missing:
            return "WARN", f"dotted name not found in code ({', '.join(missing)}): `{span}`"
        return None
    looks_code = (
        ("_" in name.strip("_") and any(c.islower() for c in name))
        or re.search(r"[a-z][A-Z]", name)
        or re.match(r"^[A-Z][a-z0-9]+[A-Z][a-zA-Z0-9]*$", name)
    )
    if looks_code and len(name) >= 4 and name not in repo.tokens:
        return "ERROR", f"identifier not found anywhere in code: `{span}`"
    return None


def collect_headings(text: str) -> set[str]:
    slugs: dict[str, int] = {}
    out = set()
    in_fence = False
    for line in text.splitlines():
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = HEADING_RE.match(line)
        if m:
            slug = github_slug(m.group(2))
            n = slugs.get(slug, 0)
            out.add(slug if n == 0 else f"{slug}-{n}")
            slugs[slug] = n + 1
    return out


def verify_doc(repo: Repo, doc: str, report: Report, heading_cache: dict) -> None:
    text = repo.text(doc) or ""
    lines = text.splitlines()
    fm, body_start = parse_frontmatter(text)

    if doc != "CLAUDE.md":
        limit = 150 if doc == "AGENTS.md" else 450
        if len(lines) > limit:
            report.add("WARN", doc, 1, f"{len(lines)} lines; budget is {limit}. Split or trim it.")
    todos = text.count("[!TODO]")
    if todos:
        report.add("INFO", doc, 1, f"{todos} [!TODO] callout(s) need a human")

    if fm:
        covers = fm.get("covers", []) or []
        if isinstance(covers, str):
            covers = [covers]
        for pat in covers:
            report.checked += 1
            if "{{" in pat:
                report.add("ERROR", doc, 1, f"template placeholder left in frontmatter covers: `{pat}`")
            elif not repo.glob_matches(pat):
                report.add("ERROR", doc, 1, f"frontmatter covers glob matches no files: `{pat}`")
        sha = fm.get("verified_at")
        if sha and repo.is_git and not git(repo.root, "rev-parse", "--verify", "--quiet", f"{sha}^{{commit}}").strip():
            report.add("WARN", doc, 1, f"verified_at `{sha}` is not a known commit")
    elif doc.startswith("docs/") and doc not in STRATEGIC_DOCS:
        report.add("WARN", doc, 1, "no frontmatter `covers:` — update mode cannot tell when this doc goes stale")

    in_fence = False
    in_comment = False
    ignoring = False
    for idx, line in enumerate(lines, 1):
        if idx <= body_start:
            continue
        if "<!-- fill:" in line:
            report.add("ERROR", doc, idx, "template guidance comment left in the doc (`<!-- fill: ... -->`)")
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if "verify:ignore-start" in line:
            ignoring = True
            continue
        if "verify:ignore-end" in line:
            ignoring = False
            continue
        if ignoring or "verify:ignore" in line:
            continue
        scan = line
        if in_comment:
            if "-->" in scan:
                scan = scan.split("-->", 1)[1]
                in_comment = False
            else:
                continue
        scan = re.sub(r"<!--.*?-->", "", scan)
        if "<!--" in scan:
            scan = scan.split("<!--", 1)[0]
            in_comment = True
        if "{{" in scan and "}}" in scan:
            report.add("ERROR", doc, idx, "template placeholder left in the doc (`{{...}}`)")

        for m in LINK_RE.finditer(scan):
            target = m.group(2)
            if target.startswith(("http://", "https://", "mailto:", "tel:")):
                continue
            report.checked += 1
            path_part, _, anchor = target.partition("#")
            if path_part:
                resolved = os.path.normpath(os.path.join(os.path.dirname(doc), path_part))
                if resolved.startswith(".."):
                    report.add("WARN", doc, idx, f"link leaves the repo: {target}")
                    continue
                if not repo.exists(resolved):
                    report.add("ERROR", doc, idx, f"broken link: {target}")
                    continue
            else:
                resolved = doc
            if anchor and resolved.endswith(".md"):
                if resolved not in heading_cache:
                    heading_cache[resolved] = collect_headings(repo.text(resolved) or "")
                if anchor.lower() not in heading_cache[resolved]:
                    report.add("ERROR", doc, idx, f"broken anchor: {target}")

        for m in SPAN_RE.finditer(scan):
            span = m.group(2).strip()
            if not span or len(span) > 200:
                continue
            check_span(repo, doc, idx, span, report)


def check_span(repo: Repo, doc: str, idx: int, span: str, report: Report) -> None:
    if span.startswith(("http://", "https://")):
        return

    rm = ROUTE_WITH_METHOD_RE.match(span)
    if rm and rm.group(1) in HTTP_METHODS:
        report.checked += 1
        if not route_found(repo, rm.group(2)):
            report.add("WARN", doc, idx, f"route not found in code: `{span}`")
        return
    if span == "/":
        return
    if span.startswith("/") and " " not in span and not span.startswith(ABS_FS_PREFIXES):
        if re.match(r"^/[\w{}:.\-/\[\]<>*]+$", span):
            report.checked += 1
            if not route_found(repo, span):
                report.add("WARN", doc, idx, f"route not found in code: `{span}`")
        return

    pl = PATH_LINE_RE.match(span)
    if pl:
        report.checked += 1
        path, start, end = pl.group(1), int(pl.group(2)), int(pl.group(3) or pl.group(2))
        found, hints = resolve_path(repo, doc, path)
        if not found:
            report.add("ERROR", doc, idx, f"file not found: `{span}`" + (f" (did you mean {', '.join(hints)}?)" if hints else ""))
            return
        text = repo.text(found)
        if text is not None and end > text.count("\n") + 1:
            report.add("ERROR", doc, idx, f"line {end} is past the end of {found} ({text.count(chr(10)) + 1} lines): `{span}`")
        return

    ps = PATH_SYMBOL_RE.match(span)
    if ps and ps.group(1).rsplit(".", 1)[-1].lower() in FILE_EXTS:
        report.checked += 1
        path, symbol = ps.group(1), ps.group(2)
        found, hints = resolve_path(repo, doc, path)
        if not found:
            report.add("ERROR", doc, idx, f"file not found: `{span}`" + (f" (did you mean {', '.join(hints)}?)" if hints else ""))
            return
        text = repo.text(found) or ""
        missing = [p for p in symbol.split(".") if not re.search(r"\b" + re.escape(p) + r"\b", text)]
        if missing:
            report.add("ERROR", doc, idx, f"`{symbol}` not found in {found}: `{span}`")
        return

    if looks_like_path(span, repo):
        report.checked += 1
        if any(ch in span for ch in "*?"):
            if not repo.glob_matches(span):
                report.add("ERROR", doc, idx, f"glob matches no files: `{span}`")
            return
        found, hints = resolve_path(repo, doc, span)
        if found:
            return
        if "/" not in span:
            if span in repo.basenames or span.lstrip(".") in repo.basenames:
                return
            report.add("WARN", doc, idx, f"file not found: `{span}`")
            return
        if hints:
            report.add("WARN", doc, idx, f"path is not repo-root relative: `{span}` (did you mean {', '.join(hints)}?)")
        else:
            report.add("ERROR", doc, idx, f"path not found: `{span}`")
        return

    if IDENTIFIER_SPAN_RE.match(span):
        report.checked += 1
        res = check_identifier(repo, span)
        if res:
            report.add(res[0], doc, idx, res[1])


def check_coverage(repo: Repo, report: Report) -> None:
    """New env vars and routes must reach their canonical home docs (DEVELOPMENT.md, CONTRACTS.md)."""
    from inventory import ENV_PATTERNS, ROUTE_PATTERNS  # same detection rules as the inventory

    env_candidates = ["docs/DEVELOPMENT.md", "docs/development.md", "docs/environment.md"]
    api_candidates = ["docs/CONTRACTS.md", "docs/contracts.md", "docs/api.md"]
    env_doc = next((d for d in env_candidates if (repo.root / d).is_file()), None)
    api_doc = next((d for d in api_candidates if (repo.root / d).is_file()), None)
    env_text = repo.text(env_doc) if env_doc else None
    api_text = repo.text(api_doc) if api_doc else None
    if env_text is None and api_text is None:
        return
    seen_env: dict[str, str] = {}
    seen_routes: dict[str, str] = {}
    for f in repo.files:
        if in_skipped_dir(f) or not is_text_candidate(f) or f.endswith((".md", ".mdx")):
            continue
        if not re.search(r"\.(py|js|jsx|mjs|cjs|ts|tsx|go|rb|php|java|kt|rs)$", f):
            continue
        text = repo.text(f) or ""
        for i, line in enumerate(text.splitlines(), 1):
            if env_text is not None:
                for pat in ENV_PATTERNS:
                    if pat.pattern.startswith(r"\$\{"):
                        continue
                    for m in pat.finditer(line):
                        seen_env.setdefault(m.group(1), f"{f}:{i}")
            if api_text is not None:
                for kind, pat in ROUTE_PATTERNS:
                    if kind not in {"call", "decorator"}:
                        continue
                    for m in pat.finditer(line):
                        path = m.groups()[-1] or ""
                        if kind == "call" and m.group(1) in {"os", "self", "dict", "data", "request", "req", "res",
                                                             "response", "json", "params", "headers", "cache", "redis",
                                                             "client", "session", "requests", "httpx", "axios", "config"}:
                            continue
                        static = [s for s in path.split("/") if s and not re.match(r"^(\{.*\}|:.+|<.*>|\[.*\])$", s)]
                        if static:
                            seen_routes.setdefault("/" + "/".join(static), f"{f}:{i}")
    if env_text is not None:
        documented = set(re.findall(r"`([A-Za-z_][A-Za-z0-9_]*)`", env_text))
        for var, where in sorted(seen_env.items()):
            report.checked += 1
            if var not in documented and var not in RUNTIME_ENV:
                report.add("WARN", env_doc, 0, f"env var `{var}` is read at {where} but not documented here")
    if api_text is not None:
        for route, where in sorted(seen_routes.items()):
            report.checked += 1
            if route not in api_text:
                report.add("WARN", api_doc, 0, f"route `{route}` is declared at {where} but not documented here")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--docs", nargs="*", help="docs to check (default: AGENTS.md, CLAUDE.md, docs/**/*.md)")
    ap.add_argument("--json", action="store_true", help="print JSON instead of text")
    ap.add_argument("--quiet", action="store_true", help="only print errors and the summary")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    repo = Repo(root)
    docs = args.docs or default_doc_paths(root, repo.files)
    docs = [Path(d).resolve().relative_to(root).as_posix() if Path(d).is_absolute() else d for d in docs]
    report = Report()
    heading_cache: dict = {}
    for doc in docs:
        if not (root / doc).is_file():
            report.add("ERROR", doc, 0, "doc file does not exist")
            continue
        verify_doc(repo, doc, report, heading_cache)
    if not args.docs:
        check_coverage(repo, report)

    errors =[i for i in report.items if i["level"] == "ERROR"]
    warns = [i for i in report.items if i["level"] == "WARN"]
    if args.json:
        print(json.dumps({"docs": docs, "checked": report.checked, "errors": len(errors),
                          "warnings": len(warns), "items": report.items}, indent=1))
        return 1 if errors else 0

    by_doc: dict[str, list[dict]] = {}
    for item in report.items:
        if args.quiet and item["level"] != "ERROR":
            continue
        by_doc.setdefault(item["doc"], []).append(item)
    for doc in docs:
        items = by_doc.get(doc)
        if not items:
            continue
        print(doc)
        for it in sorted(items, key=lambda i: (i["line"], i["level"])):
            print(f"  {it['level']:<5} L{it['line']:<4} {it['msg']}")
    todos = sum(int(i["msg"].split()[0]) for i in report.items if i["level"] == "INFO" and "[!TODO]" in i["msg"])
    print(f"\n{len(docs)} docs, {report.checked} claims checked: {len(errors)} errors, {len(warns)} warnings, {todos} TODOs")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
