#!/usr/bin/env python3
"""Map code changes to the AI docs that may now be stale.

For every doc with frontmatter `covers:` globs and `verified_at: <sha>`, list the
covered files that changed since that commit (committed, staged, unstaged and
untracked). Also list changed code files that no doc covers.

Usage: python3 affected_docs.py [repo_root] [--since SHA] [--json]
  --since  compare every doc against this commit instead of its own verified_at
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    CODE_EXTS, LOCK_FILES, default_doc_paths, git, in_skipped_dir, is_git_repo, list_files,
    load_manifest, match_any, parse_frontmatter, read_text,
)

CONFIG_EXTS = {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".env", ".example", ".sql", ".prisma"}


def changes_since(root: Path, sha: str) -> dict[str, str]:
    """Return {path: status} for changes from sha to the working tree."""
    out: dict[str, str] = {}
    diff = git(root, "diff", "--name-status", "-M", sha)
    for line in diff.splitlines():
        parts = line.split("\t")
        if not parts or not parts[0]:
            continue
        status = parts[0][0]
        if status == "R" and len(parts) == 3:
            out[parts[1]] = "D"  # old path is gone
            out[parts[2]] = "R"
        elif len(parts) >= 2:
            out[parts[1]] = status
    for path in git(root, "ls-files", "--others", "--exclude-standard").splitlines():
        if path:
            out.setdefault(path, "A")
    return out


def is_code_or_config(path: str) -> bool:
    name = path.rsplit("/", 1)[-1]
    if name in LOCK_FILES or in_skipped_dir(path):
        return False
    ext = os.path.splitext(name)[1].lower()
    return ext in CODE_EXTS or ext in CONFIG_EXTS or name.startswith(("Dockerfile", ".env")) \
        or name in {"Makefile", "Procfile", "package.json", "req.txt", "requirements.txt", "go.mod"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--since", help="override: compare against this commit")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if not is_git_repo(root):
        print("not a git repository; update mode needs git history", file=sys.stderr)
        return 2
    files = list_files(root)
    docs = default_doc_paths(root, files)
    manifest = load_manifest(root)
    fallback = args.since or (manifest.get("last_run") or {}).get("commit")

    cache: dict[str, dict[str, str]] = {}
    result_docs = []
    unmapped_docs = []
    covered_changed: set[str] = set()
    all_changed: dict[str, str] = {}

    all_covers: list[str] = []
    for doc in docs:
        fm, _ = parse_frontmatter(read_text(root, doc) or "")
        covers = fm.get("covers") or []
        all_covers.extend(covers)
        sha = args.since or fm.get("verified_at") or fallback
        if not covers:
            STRATEGIC_DOCS = {
                "docs/README.md", "docs/VISION.md", "docs/DECISIONS.md", "docs/OPEN_QUESTIONS.md",
                "docs/readme.md", "docs/vision.md", "docs/decisions.md", "docs/open_questions.md",
            }
            if doc.startswith("docs/") and doc not in STRATEGIC_DOCS:
                unmapped_docs.append(doc)
            continue
        if not sha:
            result_docs.append({"doc": doc, "verified_at": None, "changed": [], "note": "no verified_at"})
            continue
        if sha not in cache:
            if not git(root, "rev-parse", "--verify", "--quiet", f"{sha}^{{commit}}").strip():
                result_docs.append({"doc": doc, "verified_at": sha, "changed": [],
                                    "note": "verified_at is not a known commit; re-verify the whole doc"})
                continue
            cache[sha] = changes_since(root, sha)
        changes = cache[sha]
        all_changed.update(changes)
        hits = sorted(f"{st} {p}" for p, st in changes.items() if match_any(p, covers))
        covered_changed.update(p for p, _ in changes.items() if match_any(p, covers))
        result_docs.append({"doc": doc, "verified_at": sha, "changed": hits})

    if fallback and fallback not in cache and git(root, "rev-parse", "--verify", "--quiet", f"{fallback}^{{commit}}").strip():
        all_changed.update(changes_since(root, fallback))

    # A change is "uncovered" only when no doc's `covers` matches it at all,
    # whether or not that doc is currently stale.
    uncovered = sorted(
        f"{st} {p}" for p, st in all_changed.items()
        if not match_any(p, all_covers) and is_code_or_config(p) and not p.startswith("docs/")
    )
    stale = [d for d in result_docs if d["changed"] or d.get("note")]

    if args.json:
        print(json.dumps({"stale_docs": stale, "fresh_docs": [d["doc"] for d in result_docs if d not in stale],
                          "uncovered_changes": uncovered, "unmapped_docs": unmapped_docs,
                          "head": git(root, "rev-parse", "HEAD").strip()}, indent=1))
        return 0

    print(f"HEAD {git(root, 'rev-parse', '--short', 'HEAD').strip()}")
    if stale:
        print("\nDocs to refresh:")
        for d in stale:
            print(f"- {d['doc']} (verified_at {d['verified_at']})" + (f" — {d['note']}" if d.get("note") else ""))
            for c in d["changed"][:25]:
                print(f"    {c}")
            if len(d["changed"]) > 25:
                print(f"    … {len(d['changed']) - 25} more")
    else:
        print("\nNo mapped doc has changed sources since it was verified.")
    if uncovered:
        print("\nChanged code that no doc covers (assign to a doc or add a new one):")
        for c in uncovered[:60]:
            print(f"    {c}")
    if unmapped_docs:
        print("\nDocs without `covers:` frontmatter (cannot be tracked):")
        for d in unmapped_docs:
            print(f"- {d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
