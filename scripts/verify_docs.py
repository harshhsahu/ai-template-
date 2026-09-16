#!/usr/bin/env python3
"""Check a generated documentation set for the mechanical failure modes.

Three checks, in order of how much they matter:

1. **Cited paths that don't exist** — the invention detector. A doc that references
   `api/views.py:412` when no such file exists is making things up, and that is the
   failure this whole skill is built to prevent.
2. **Unmarked gaps** — an unresolved {{TOKEN}} or <!-- fill: --> hint with no
   nearby [!TODO] callout reads as finished documentation but says nothing.
3. **Broken relative links** — a link to a doc that was skipped is a broken promise.

Exit status is 0 when nothing is found, 1 when any finding is reported, so this can
gate a commit.

Usage:
    python3 verify_docs.py <project-root> [--docs-dir docs] [--quiet]
                           [--no-path-check] [--json]

Standard library only; Python 3.8+.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

TOKEN_RE = re.compile(r"\{\{([A-Za-z0-9_.\-]{1,60})\}\}")
FILL_RE = re.compile(r"<!--\s*fill\s*:", re.I)
TODO_RE = re.compile(r">\s*\[!(TODO|NOTE|WARNING|IMPORTANT|CAUTION|TIP)\]", re.I)
LINK_RE = re.compile(r"\[([^\]]{0,200}?)\]\(([^)\s]+?)(?:\s+\"[^\"]*\")?\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")

# `path/to/file.ext` or `path/to/file.ext:12-40` inside backticks
CITED_RE = re.compile(
    r"`([A-Za-z0-9_.][A-Za-z0-9_./\-]*\.[A-Za-z0-9]{1,12})(?::\d+(?:-\d+)?)?`"
)

# Things that look like paths but aren't repo files.
CITE_IGNORE = re.compile(
    r"^(https?:|//|\.{1,2}$)"
    r"|^(package|module|lib|app|api|www|node|npm|pip|e\.g|i\.e|vs|etc|min|max)\.[a-z]{1,4}$"
    r"|^\*|\{\{|\$\{|<|>",
    re.I,
)
# Extensions that are real files worth checking. Anything else (e.g. `orders.md`
# as prose, `foo.bar` as a dotted name) is skipped to keep noise down.
CHECK_EXTS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".go", ".rb", ".php", ".java",
    ".kt", ".cs", ".rs", ".vue", ".svelte", ".json", ".yml", ".yaml", ".toml", ".ini",
    ".cfg", ".sql", ".sh", ".ps1", ".conf", ".html", ".css", ".scss", ".prisma", ".env",
    ".example", ".lock", ".txt", ".xml", ".tf", ".dockerfile", ".proto", ".graphql",
}

VENDOR = {"node_modules", ".git", "dist", "build", ".next", "venv", ".venv",
          "__pycache__", "target", "vendor", "coverage", ".tox", ".turbo"}


def find_heading(lines, idx: int) -> str:
    for i in range(idx, -1, -1):
        m = HEADING_RE.match(lines[i])
        if m:
            return m.group(2).strip()
    return "(top of file)"


def has_nearby_todo(lines, idx: int, window: int = 12) -> bool:
    """A gap counts as marked if a callout sits in the same section nearby."""
    lo, hi = max(0, idx - window), min(len(lines), idx + window + 1)
    for i in range(lo, hi):
        if TODO_RE.search(lines[i]):
            return True
    return False


def build_repo_index(root: Path):
    """Lowercased set of every relative path and every basename in the repo."""
    rel_paths, basenames = set(), set()
    for p in root.rglob("*"):
        parts = p.relative_to(root).parts
        if any(part in VENDOR for part in parts):
            continue
        if p.is_file():
            rel = "/".join(parts)
            rel_paths.add(rel.lower())
            basenames.add(p.name.lower())
        elif p.is_dir():
            rel_paths.add(("/".join(parts) + "/").lower())
    return rel_paths, basenames


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", help="project root containing the docs directory")
    ap.add_argument("--docs-dir", default="docs", help="docs directory name (default: docs)")
    ap.add_argument("--no-path-check", action="store_true",
                    help="skip the cited-path existence check")
    ap.add_argument("--quiet", action="store_true", help="summary only")
    ap.add_argument("--json", dest="as_json", action="store_true",
                    help="emit findings as JSON")
    args = ap.parse_args()

    root = Path(args.root).expanduser().resolve()
    docs_dir = root / args.docs_dir
    if not docs_dir.is_dir():
        print(f"error: no docs directory at {docs_dir}", file=sys.stderr)
        return 2

    doc_files = sorted(docs_dir.rglob("*.md"))
    for extra in ("AGENTS.md", "CLAUDE.md", "README.md"):
        p = root / extra
        if p.is_file():
            doc_files.append(p)
    if not doc_files:
        print(f"error: no markdown files found under {docs_dir}", file=sys.stderr)
        return 2

    rel_paths, basenames = (set(), set()) if args.no_path_check else build_repo_index(root)

    findings = {"unmarked_tokens": [], "unmarked_fills": [], "broken_links": [],
                "missing_cited_paths": [], "empty_sections": []}
    stats = {"files": len(doc_files), "todos": 0, "tokens_total": 0,
             "fills_total": 0, "links_total": 0, "citations_checked": 0}

    for f in doc_files:
        rel_doc = f.relative_to(root).as_posix()
        text = f.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        in_fence = False

        for i, line in enumerate(lines):
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue

            if TODO_RE.search(line):
                stats["todos"] += 1

            for m in TOKEN_RE.finditer(line):
                stats["tokens_total"] += 1
                if not has_nearby_todo(lines, i):
                    findings["unmarked_tokens"].append({
                        "file": rel_doc, "line": i + 1, "token": m.group(0),
                        "section": find_heading(lines, i),
                    })

            if FILL_RE.search(line):
                stats["fills_total"] += 1
                if not has_nearby_todo(lines, i):
                    findings["unmarked_fills"].append({
                        "file": rel_doc, "line": i + 1,
                        "section": find_heading(lines, i),
                        "text": line.strip()[:120],
                    })

            if in_fence:
                continue

            for m in LINK_RE.finditer(line):
                target = m.group(2)
                stats["links_total"] += 1
                if target.startswith(("http://", "https://", "mailto:", "#")) or "{{" in target:
                    continue
                path_part = target.split("#", 1)[0]
                if not path_part:
                    continue
                resolved = (f.parent / path_part).resolve()
                if not resolved.exists():
                    findings["broken_links"].append({
                        "file": rel_doc, "line": i + 1, "target": target,
                        "text": m.group(1)[:60],
                    })

            if args.no_path_check:
                continue
            for m in CITED_RE.finditer(line):
                cited = m.group(1)
                if CITE_IGNORE.search(cited) or "/" not in cited and "." not in cited:
                    continue
                ext = "." + cited.rsplit(".", 1)[-1].lower()
                if ext not in CHECK_EXTS:
                    continue
                if cited.startswith("."):  # .env.example etc
                    pass
                stats["citations_checked"] += 1
                low = cited.lower()
                base = cited.rsplit("/", 1)[-1].lower()
                if low in rel_paths:
                    continue
                # tolerate a leading ./ or a citation relative to a subdir
                if any(p.endswith("/" + low) for p in rel_paths):
                    continue
                if base in basenames:
                    findings["missing_cited_paths"].append({
                        "file": rel_doc, "line": i + 1, "cited": cited,
                        "severity": "path-mismatch",
                        "note": f"`{base}` exists in the repo but not at this path",
                    })
                else:
                    findings["missing_cited_paths"].append({
                        "file": rel_doc, "line": i + 1, "cited": cited,
                        "severity": "not-found",
                        "note": "no file with this name anywhere in the repo",
                    })

        # a heading with no content under it at all
        for i, line in enumerate(lines):
            m = HEADING_RE.match(line)
            if not m or m.group(1) == "#":
                continue
            body = []
            for j in range(i + 1, len(lines)):
                if HEADING_RE.match(lines[j]):
                    break
                body.append(lines[j].strip())
            if not any(body):
                findings["empty_sections"].append({
                    "file": rel_doc, "line": i + 1, "section": m.group(2).strip(),
                })

    total = sum(len(v) for v in findings.values())

    if args.as_json:
        print(json.dumps({"stats": stats, "findings": findings, "total": total}, indent=2))
        return 1 if total else 0

    print(f"Verified {stats['files']} doc file(s) under {docs_dir}")
    print(f"  {stats['todos']} TODO callout(s) · {stats['tokens_total']} template token(s) · "
          f"{stats['links_total']} link(s) · {stats['citations_checked']} path citation(s) checked")
    print()

    def report(key, title, fmt, explain):
        items = findings[key]
        if not items:
            print(f"OK   {title}: none")
            return
        print(f"FAIL {title}: {len(items)}")
        print(f"     {explain}")
        if not args.quiet:
            for it in items[:60]:
                print("       " + fmt(it))
            if len(items) > 60:
                print(f"       … {len(items) - 60} more")
        print()

    report("missing_cited_paths", "Cited paths that don't exist",
           lambda it: f"{it['file']}:{it['line']} — `{it['cited']}` ({it['note']})",
           "Each of these is a factual claim about a file that isn't there. "
           "Fix the docs, not this script — this is the invention detector.")

    report("unmarked_tokens", "Unresolved {{TOKEN}} with no TODO callout",
           lambda it: f"{it['file']}:{it['line']} — {it['token']} under \"{it['section']}\"",
           "Either resolve the token from code, or add a > [!TODO] callout saying "
           "what evidence was missing.")

    report("unmarked_fills", "<!-- fill: --> hints with no TODO callout",
           lambda it: f"{it['file']}:{it['line']} — under \"{it['section']}\"",
           "The template asked for content here and none was written. Fill it or mark it.")

    report("broken_links", "Broken relative links",
           lambda it: f"{it['file']}:{it['line']} — [{it['text']}]({it['target']})",
           "Usually a link to a Tier B doc that was deliberately skipped. Remove the "
           "link or replace it with an inline note.")

    report("empty_sections", "Headings with no content",
           lambda it: f"{it['file']}:{it['line']} — \"{it['section']}\"",
           "An empty section is indistinguishable from a forgotten one. Write it, "
           "mark it, or delete the heading.")

    if total == 0:
        print("No mechanical findings. Now do the pass a script can't: re-read each file "
              "and confirm every factual sentence has an evidence-ledger row behind it.")
    else:
        print(f"{total} finding(s) total.")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
