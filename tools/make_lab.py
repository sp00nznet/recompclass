#!/usr/bin/env python3
"""
Helper for scaffolding a lab directory.

Labs are three files plus an optional reference solution:

    labs/lab-NN/README.md       what to build and why
    labs/lab-NN/<module>.py     the stub, with `# TODO:` bodies
    labs/lab-NN/test_lab.py     tests that fail until the TODOs are filled in

Some labs are project or writing exercises with nothing to unit-test. Those get
a README only, and `tools/check_solutions.py` skips them.

This module is imported by the per-unit build scripts in `tools/labs/`; it is
not run directly. Keeping the boilerplate here means every lab gets the same
import preamble, so a lab can `import` its sibling module and `labs.lib`
helpers without each file re-deriving the path dance.
"""

from __future__ import annotations

import pathlib
import textwrap

REPO = pathlib.Path(__file__).resolve().parent.parent
LABS = REPO / "labs"

STUB_PREAMBLE = '''"""
Lab {num}: {title}

{summary}
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
'''

TEST_PREAMBLE = '''"""
Tests for Lab {num}: {title}
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import {module}
'''


def write(path: pathlib.Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip("\n") + "\n", encoding="utf-8", newline="\n")


def lab(num: int, title: str, readme: str, *, module: str = "",
        summary: str = "", stub: str = "", test: str = "",
        extra_imports: str = "") -> None:
    """Create one lab. Omit module/stub/test for a README-only exercise."""
    d = LABS / f"lab-{num}"
    write(d / "README.md", f"# Lab {num}: {title}\n\n" + textwrap.dedent(readme).strip())

    if not module:
        return

    body = STUB_PREAMBLE.format(num=num, title=title, summary=textwrap.dedent(summary).strip())
    if extra_imports:
        body += extra_imports.rstrip() + "\n"
    body += "\n\n" + textwrap.dedent(stub).strip() + "\n"
    write(d / f"{module}.py", body)

    write(d / "test_lab.py",
          TEST_PREAMBLE.format(num=num, title=title, module=module)
          + "\n\n" + textwrap.dedent(test).strip() + "\n")


def report() -> None:
    labs = sorted(LABS.glob("lab-*"), key=lambda p: int(p.name.split("-")[1]))
    code = [l for l in labs if (l / "test_lab.py").exists()]
    print(f"{len(labs)} labs, {len(code)} with tests")
