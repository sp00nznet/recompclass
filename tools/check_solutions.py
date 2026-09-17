#!/usr/bin/env python3
"""
Run each lab's tests against its reference solution.

The lab tests do a plain `import <module>` and rely on pytest putting the test
file's own directory on sys.path, so the only reliable way to exercise the
solution is to swap it into place, run, and swap the stub back. Anything
cleverer (PYTHONPATH, importlib mode, a temp tree) breaks either the sibling
import or the `from labs.lib import ...` that the tests also do.

    python tools/check_solutions.py          # test every lab that has a solution
    python tools/check_solutions.py lab-04   # just one

Exit code is non-zero if any solution fails its own tests.
"""

import pathlib
import shutil
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
LABS = REPO / "labs"


def run_lab(lab_dir: pathlib.Path) -> tuple[str, str]:
    """Swap in the solution, run pytest, restore. Returns (status, detail)."""
    solution_dir = lab_dir / "solution"
    if not solution_dir.is_dir():
        return "skip", "no solution yet"
    if not (lab_dir / "test_lab.py").exists():
        return "skip", "no test_lab.py"

    swapped: list[tuple[pathlib.Path, pathlib.Path]] = []
    try:
        for sol in sorted(solution_dir.glob("*.py")):
            target = lab_dir / sol.name
            backup = lab_dir / (sol.name + ".stub-backup")
            if target.exists():
                shutil.copy2(target, backup)
                swapped.append((target, backup))
            shutil.copy2(sol, target)

        proc = subprocess.run(
            [sys.executable, "-m", "pytest", str(lab_dir), "-q", "-p", "no:cacheprovider"],
            capture_output=True, text=True, cwd=REPO,
        )
    finally:
        for target, backup in swapped:
            shutil.copy2(backup, target)
            backup.unlink()
        for pycache in lab_dir.rglob("__pycache__"):
            shutil.rmtree(pycache, ignore_errors=True)

    tail = [ln for ln in proc.stdout.strip().splitlines() if ln.strip()]
    summary = tail[-1] if tail else "(no output)"
    return ("pass" if proc.returncode == 0 else "FAIL"), summary


def main() -> int:
    wanted = sys.argv[1:]
    labs = sorted(d for d in LABS.glob("lab-*") if d.is_dir())
    if wanted:
        labs = [d for d in labs if d.name in wanted]

    failures, tested = [], 0
    for lab_dir in labs:
        status, detail = run_lab(lab_dir)
        if status == "skip":
            continue
        tested += 1
        print(f"{status:4}  {lab_dir.name}  {detail}")
        if status == "FAIL":
            failures.append(lab_dir.name)

    print(f"\n{tested - len(failures)}/{tested} solutions pass their own tests")
    if failures:
        print("failing: " + ", ".join(failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
