#!/usr/bin/env python3
"""Print the sections of the subagents' notes files the orchestrator needs.

The full notes are large (about 100 lines per area). The cross-cutting docs
(architecture, conventions, glossary, AGENTS.md, README) need only these sections:
Summary, Rules, Terms, External systems, Open questions. Env vars, routes and data
already went to the surface and data agents.

Usage: python3 notes_digest.py <notes_dir> [--sections "summary,rules,..."]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DEFAULT = "summary,rules,terms,external systems,open questions"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("notes_dir")
    ap.add_argument("--sections", default=DEFAULT, help=f"comma-separated, case-insensitive (default: {DEFAULT})")
    args = ap.parse_args()

    want = {s.strip().lower() for s in args.sections.split(",") if s.strip()}
    notes = sorted(Path(args.notes_dir).glob("*.md"))
    if not notes:
        print(f"no notes in {args.notes_dir}", file=sys.stderr)
        return 1
    for path in notes:
        if path.name.startswith("_"):
            continue  # e.g. _existing-docs.md: read it whole when adopting
        parts = re.split(r"^## ", path.read_text(), flags=re.M)
        print(f"\n##### {path.name}")
        for part in parts[1:]:
            heading, _, body = part.partition("\n")
            if heading.strip().lower() in want and body.strip():
                print(f"[{heading.strip().lower()}]\n{body.strip()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
