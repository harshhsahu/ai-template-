#!/usr/bin/env python3
"""Copy selected documentation templates into a target project.

Copies from the skill's assets/templates/ so filenames, numbering, and template
wording stay exactly as the house template ships them. Refuses to overwrite
existing files unless --force, because an existing docs/ file may be
hand-written by a human.

Usage:
    python3 scaffold_docs.py <project-root>
        --files 00,06,07,08,09,12,13,15,18,19,20,22,23,ARCHITECTURE,AGENTS,ROOT_AGENTS
        [--all-numbered]
        [--domains api:payments,api:tenants]
        [--modules 01-billing,02-tenancy]
        [--database entities,relationships]
        [--ui shared/data-table,shared/modal]
        [--infra postgres,redis]
        [--docs-dir docs] [--dry-run] [--force] [--list]

Standard library only; Python 3.8+.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATES = SKILL_DIR / "assets" / "templates"

NUMBERED = {
    "00": "00-project-overview.md",
    "01": "01-product-vision.md",
    "02": "02-business-goals.md",
    "03": "03-user-personas.md",
    "04": "04-user-journeys.md",
    "05": "05-navigation.md",
    "06": "06-tech-stack.md",
    "07": "07-system-architecture.md",
    "08": "08-folder-structure.md",
    "09": "09-coding-guidelines.md",
    "10": "10-design-system.md",
    "11": "11-state-management.md",
    "12": "12-api-guidelines.md",
    "13": "13-security.md",
    "14": "14-performance.md",
    "15": "15-environment-setup.md",
    "16": "16-analytics.md",
    "17": "17-notifications.md",
    "18": "18-error-handling.md",
    "19": "19-testing.md",
    "20": "20-deployment.md",
    "21": "21-roadmap.md",
    "22": "22-definition-of-done.md",
    "23": "23-git-workflow.md",
    "24": "24-feature-flags.md",
}

SPECIAL = {
    "ARCHITECTURE": ("docs/ARCHITECTURE.md", "docs/ARCHITECTURE.md"),
    "AGENTS": ("docs/AGENTS.md", "docs/AGENTS.md"),
    "ROOT_AGENTS": ("AGENTS.md", "AGENTS.md"),
}

SUBFOLDERS = {
    "api": "docs/api/_TEMPLATE.md",
    "database": "docs/database/_TEMPLATE.md",
    "modules": "docs/modules/_TEMPLATE.md",
    "ui": "docs/ui/_TEMPLATE.md",
    "current-infrastructure": "docs/current-infrastructure/_TEMPLATE.md",
    "plans": "docs/plans/_TEMPLATE.md",
    "brainstorms": "docs/brainstorms/_TEMPLATE.md",
}


def csv(value):
    return [v.strip() for v in (value or "").split(",") if v.strip()]


def slugify(name: str) -> str:
    keep = "".join(c if (c.isalnum() or c in "-_/") else "-" for c in name.strip().lower())
    while "--" in keep:
        keep = keep.replace("--", "-")
    return keep.strip("-")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", nargs="?", help="target project root")
    ap.add_argument("--files", default="",
                    help="comma list of numbered keys (00-24) and/or "
                         "ARCHITECTURE, AGENTS, ROOT_AGENTS")
    ap.add_argument("--all-numbered", action="store_true",
                    help="include every 00-24 guide (use only if the user asked for the full set)")
    ap.add_argument("--domains", default="",
                    help="api domain docs, e.g. api:payments,api:tenants (or just payments,tenants)")
    ap.add_argument("--modules", default="",
                    help="module docs, e.g. 01-billing,02-tenancy")
    ap.add_argument("--database", default="",
                    help="database docs, e.g. entities,relationships")
    ap.add_argument("--ui", default="", help="ui component docs, e.g. shared/data-table")
    ap.add_argument("--infra", default="",
                    help="current-infrastructure docs, e.g. postgres,redis")
    ap.add_argument("--keep-templates", dest="keep_templates", action="store_true", default=True,
                    help="keep each subfolder's _TEMPLATE.md (default: on)")
    ap.add_argument("--no-claude-md", action="store_true",
                    help="do not create CLAUDE.md containing @AGENTS.md")
    ap.add_argument("--docs-dir", default="docs", help="docs directory name (default: docs)")
    ap.add_argument("--dry-run", action="store_true", help="print planned writes, change nothing")
    ap.add_argument("--force", action="store_true", help="overwrite existing files")
    ap.add_argument("--list", action="store_true", help="list available template keys and exit")
    args = ap.parse_args()

    if args.list:
        print("Numbered guides (--files):")
        for k, v in NUMBERED.items():
            print(f"  {k}  -> {args.docs_dir}/{v}")
        print("\nSpecial (--files):")
        for k, (src, dst) in SPECIAL.items():
            print(f"  {k}  -> {dst}")
        print("\nSubfolder templates:")
        for k in SUBFOLDERS:
            print(f"  {k}")
        return 0

    if not args.root:
        ap.error("the following arguments are required: root")

    if not TEMPLATES.is_dir():
        print(f"error: templates not found at {TEMPLATES}", file=sys.stderr)
        return 2

    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 2

    docs = args.docs_dir.strip("/")
    plan = []  # (template_relpath, dest_relpath)
    unknown = []

    keys = csv(args.files)
    if args.all_numbered:
        keys = sorted(set(keys) | set(NUMBERED))
    for key in keys:
        k = key.strip()
        if k in NUMBERED:
            plan.append((f"docs/{NUMBERED[k]}", f"{docs}/{NUMBERED[k]}"))
        elif k.upper() in SPECIAL:
            src, dst = SPECIAL[k.upper()]
            dst = dst.replace("docs/", f"{docs}/", 1) if dst.startswith("docs/") else dst
            plan.append((src, dst))
        elif k in NUMBERED.values():
            plan.append((f"docs/{k}", f"{docs}/{k}"))
        else:
            unknown.append(k)

    def add_clones(raw, folder, transform=slugify):
        for item in csv(raw):
            name = item.split(":", 1)[1] if ":" in item else item
            name = transform(name)
            if not name:
                continue
            if not name.endswith(".md"):
                name += ".md"
            plan.append((SUBFOLDERS[folder], f"{docs}/{folder}/{name}"))

    add_clones(args.domains, "api")
    add_clones(args.modules, "modules")
    add_clones(args.database, "database")
    add_clones(args.ui, "ui")
    add_clones(args.infra, "current-infrastructure")

    # Keep the _TEMPLATE.md pattern file in every subfolder we touch, plus
    # plans/ and brainstorms/, which are written per-change rather than generated.
    if args.keep_templates:
        touched = {p.split("/")[1] for _, p in plan
                   if p.startswith(f"{docs}/") and len(p.split("/")) > 2}
        for folder in sorted(touched | {"plans", "brainstorms"}):
            if folder in SUBFOLDERS:
                plan.append((SUBFOLDERS[folder], f"{docs}/{folder}/_TEMPLATE.md"))

    if unknown:
        print(f"error: unknown template key(s): {', '.join(unknown)}\n"
              f"run with --list to see valid keys", file=sys.stderr)
        return 2
    if not plan:
        print("error: nothing to do — pass --files and/or the subfolder options",
              file=sys.stderr)
        return 2

    # de-duplicate, preserving order
    seen, ordered = set(), []
    for src, dst in plan:
        if dst not in seen:
            seen.add(dst)
            ordered.append((src, dst))

    written, skipped, missing = [], [], []
    for src, dst in ordered:
        src_path = TEMPLATES / src
        dst_path = root / dst
        if not src_path.is_file():
            missing.append(src)
            continue
        if dst_path.exists() and not args.force:
            skipped.append(dst)
            continue
        if not args.dry_run:
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src_path, dst_path)
        written.append(dst)

    claude_md = root / "CLAUDE.md"
    created_claude = False
    wants_root_agents = any(d == "AGENTS.md" for _, d in ordered)
    if wants_root_agents and not args.no_claude_md:
        if claude_md.exists() and not args.force:
            skipped.append("CLAUDE.md")
        else:
            if not args.dry_run:
                claude_md.write_text("@AGENTS.md\n", encoding="utf-8")
            written.append("CLAUDE.md")
            created_claude = True

    tag = "[dry-run] would create" if args.dry_run else "created"
    print(f"{tag} {len(written)} file(s) under {root}:")
    for w in written:
        print(f"  + {w}" + ("   (mirror of AGENTS.md)" if w == "CLAUDE.md" and created_claude else ""))
    if skipped:
        print(f"\nskipped {len(skipped)} existing file(s) — read them before changing "
              f"anything, or re-run with --force:")
        for s in skipped:
            print(f"  = {s}")
    if missing:
        print(f"\nWARNING: missing template source(s): {', '.join(missing)}", file=sys.stderr)
    print("\nNext: fill each file from the evidence ledger. Resolve every {{TOKEN}} you have "
          "evidence for; leave the rest verbatim with a > [!TODO] callout explaining what "
          "evidence was missing.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
