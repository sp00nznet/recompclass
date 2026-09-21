#!/usr/bin/env python3
"""Enforce the two repository rules in CONTRIBUTING.md.

  1. The root holds only README / CONTRIBUTING / LICENSE / SYLLABUS.
     Everything else goes in docs/.
  2. No reader-facing document links a repository the reader cannot open.

Both rules exist because both were broken. A project note sat at a repository
root under a tool's name, and twenty-eight repositories cited by this course
were private -- every one of those citations a 404 for anybody but their owner,
while reading like evidence.

Rule 2 needs the network. Without a token it checks anonymously, which is
exactly the reader's view. In CI the default GITHUB_TOKEN is scoped to this
repository, so a private repository elsewhere still 404s -- the same answer a
reader gets, which is the answer we want.

    python tools/check_repo_rules.py            # both rules
    python tools/check_repo_rules.py --layout   # rule 1 only, no network
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import sys
import urllib.error
import urllib.request

REPO = pathlib.Path(__file__).resolve().parent.parent

ROOT_ALLOWED = {"README.md", "CONTRIBUTING.md", "LICENSE", "LICENSE.md",
                "SYLLABUS.md"}

# Filenames that should never sit at a repository root.
TOOL_FILES = re.compile(r"(?i)^(CLAUDE|AGENTS|GEMINI|COPILOT)\.md$|"
                        r"^\.(cursorrules|clinerules|aider\.conf\.yml)$")

REPO_LINK = re.compile(r"https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)")

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "build", "dist"}


def check_layout() -> list[str]:
    """Rule 1: documentation lives in docs/, not at the root."""
    problems = []
    for p in sorted(REPO.iterdir()):
        if p.is_dir() or p.name.startswith("."):
            if p.is_file() and TOOL_FILES.match(p.name):
                problems.append(
                    f"{p.name}: tool-specific file at the repository root -- "
                    f"give it a descriptive name under docs/, or do not commit it")
            continue
        if TOOL_FILES.match(p.name):
            problems.append(
                f"{p.name}: tool-specific file at the repository root -- "
                f"give it a descriptive name under docs/, or do not commit it")
        elif p.suffix.lower() in {".md", ".rst", ".txt"} and p.name not in ROOT_ALLOWED:
            problems.append(
                f"{p.name}: documentation at the repository root -- move it to docs/")
    return problems


def iter_links():
    """Yield (file, line, owner, repo) for every GitHub repository link."""
    for md in sorted(REPO.rglob("*.md")):
        if any(part in SKIP_DIRS for part in md.parts):
            continue
        text = md.read_text(encoding="utf-8", errors="replace")
        for i, line in enumerate(text.splitlines(), 1):
            for m in REPO_LINK.finditer(line):
                owner, name = m.group(1), m.group(2)
                name = name.removesuffix(".git").rstrip(".,;:)")
                if not name:
                    continue
                # Not a repository: /owner alone, or a known non-repo path.
                if name in {"", "sponsors", "orgs", "settings"}:
                    continue
                yield md.relative_to(REPO).as_posix(), i, owner, name


def visibility(owner: str, name: str, token: str | None) -> str:
    """'public', 'unreachable', or 'error: ...' as a reader would see it."""
    req = urllib.request.Request(
        f"https://api.github.com/repos/{owner}/{name}",
        headers={"Accept": "application/vnd.github+json",
                 "User-Agent": "recompclass-link-check"})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            body = json.load(r)
        return "public" if not body.get("private") else "private"
    except urllib.error.HTTPError as e:
        if e.code in (403, 429):
            return "error: rate limited"
        return "unreachable"
    except Exception as e:  # network down, DNS, timeout
        return f"error: {type(e).__name__}"


def check_links() -> list[str]:
    """Rule 2: every cited repository is one a reader can open."""
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    seen: dict[tuple[str, str], str] = {}
    problems, errors = [], set()

    for path, line, owner, name in iter_links():
        key = (owner, name)
        if key not in seen:
            seen[key] = visibility(owner, name, token)
        state = seen[key]
        if state.startswith("error"):
            errors.add(f"{owner}/{name}")
        elif state != "public":
            problems.append(f"{path}:{line}: {owner}/{name} is {state} -- "
                            f"a reader following this link gets a 404")

    print(f"   checked {len(seen) - len(errors)} of {len(seen)} "
          f"distinct repository link(s)")
    return problems, sorted(errors)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--layout", action="store_true",
                    help="check the layout rule only (no network)")
    args = ap.parse_args()

    failures = []

    print("Rule 1: documentation lives in docs/")
    layout = check_layout()
    print(f"   {'FAIL' if layout else 'ok'}")
    failures += layout

    unverified: list[str] = []
    if not args.layout:
        print("Rule 2: no links to repositories a reader cannot open")
        links, unverified = check_links()
        print(f"   {'FAIL' if links else ('INCONCLUSIVE' if unverified else 'ok')}")
        failures += links

    if failures:
        print(f"\n{len(failures)} violation(s):")
        for f in failures:
            print("  ", f)
        return 1

    if unverified:
        # Anonymous API access allows 60 requests an hour. Printing a pass here
        # would be exactly the failure this checker exists to catch: a green
        # result from a check that never ran.
        print(f"\nINCONCLUSIVE: {len(unverified)} link(s) could not be verified "
              f"(rate limit or network).")
        print(f"   e.g. {', '.join(unverified[:4])}")
        print("   Set GITHUB_TOKEN -- CI provides one automatically -- and rerun.")
        return 2

    print("\nrepository rules hold")
    return 0


if __name__ == "__main__":
    sys.exit(main())
