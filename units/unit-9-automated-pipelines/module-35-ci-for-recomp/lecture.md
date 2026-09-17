# Module 35: CI/CD for Recompilation Projects

Continuous integration for a recompilation project has one hard constraint that ordinary
software does not: **you cannot ship the thing you are testing.** The game binary is
copyrighted, the recompiled output is a derived work, and neither can live in your
repository or on a public CI runner.

Everything in this module follows from that. It also covers the failure mode that
constraint encourages, which is a green badge that verifies nothing -- illustrated with a
bug found in this course's own repository.

---

## 1. The Green Badge That Tests Nothing

Start with the cautionary tale, because it is short and it was real.

`recompclass` had a CI job called **"Run Python labs"** that looked entirely reasonable:

```yaml
- name: Run Python labs
  run: |
    for dir in labs/lab-*/; do
      if [ -f "$dir/test_lab.py" ]; then
        echo "Testing $dir..."
        python "$dir/test_lab.py" || exit 1
      fi
    done
```

It passed on every commit for months. It tested nothing at all.

The test files contain pytest-style classes:

```python
class TestValidateMagic:
    def test_valid_magic(self):
        ...
```

Running such a file with `python` **defines the classes and exits 0**. Nothing invokes
them. `pytest` is what discovers and runs test classes, and `pytest` was never installed
or called.

What it cost: a genuine bug sat in `labs/lib/disasm_helpers.py`, a shared module used by
several labs.

```python
from capstone import CS_MODE_16, CS_MODE_32, CS_MODE_64, CS_MODE_MIPS32
from capstone import CS_MODE_BIG_ENDIAN, CS_MODE_LITTLE_ENDIAN
...
    "arm32":     (CS_ARCH_ARM, CS_MODE_ARM),   # never imported
```

`CS_MODE_ARM` is used and never imported, so the module raises `NameError` on import and
two labs are dead on arrival for anyone who clones the repo. A CI that imported a single
lab module would have caught it on the commit that introduced it.

### The lesson, stated generally

**A CI step that cannot fail is worse than no CI step**, because it converts "untested"
into "tested" in every reader's head, including yours.

Before trusting any CI job, break something on purpose and confirm the job goes red. If
you cannot make it fail, it is not a gate. This is the same instinct Module 37 applies to
project claims and Module 18 applies to harnesses that draw their own evidence.

---

## 2. What You Can Actually Test Without the ROM

Sort your project into what CI can see and what it cannot.

| Always testable in CI | Needs the copyrighted input |
|---|---|
| Does every tool build? | Does this game boot? |
| Does every module import? | Does it render correctly? |
| Do unit tests on decode/lift/flags pass? | Frame-hash comparison |
| Does the lifter produce identical output for a fixed synthetic input? | Full-run trace diffs |
| Do the runtime and shims compile and link? | Performance measurements |
| Does the generated build system configure? | Compatibility percentages |

The left column is most of your correctness surface, and it is entirely free of legal
problems. **Test the left column ruthlessly in public CI. Test the right column locally
and publish the method, not the artifact.**

### Synthetic fixtures are the workaround

You cannot commit a game ROM. You can commit a 64-byte blob of hand-assembled
instructions that exercises every addressing mode, and assert on the exact C your lifter
emits for it.

This is the highest-value test a recompiler can have. It is fast, it is legal, it fails
loudly on any unintended semantic change, and it doubles as documentation of what your
lifter is supposed to produce. `tirecomp` ships `tests/test_decode.c`, `tests/test_rt.c`
and `tests/test_tivar.c` for exactly this.

Build fixtures for the cases you know are hard, not the easy ones:

- Flag-setting arithmetic at every width (Module 18's `16-bit addresses wrap, they do not
  sign-extend` came from getting this wrong)
- Delay slots, on every architecture that has them
- The width-sensitive instructions on 65816 under both `M` and `X` settings
- ARM/Thumb interworking across a `BX`
- Every control-flow class from your decode table, so `JP (HL)` cannot silently become a
  plain branch

---

## 3. Structuring the Jobs

A workable shape for a recompilation toolkit:

```
build          → the tools compile on every platform you claim to support
unit           → decode, lift, flag and format tests
golden         → lifter output for synthetic fixtures matches committed expectations
runtime        → the shims and HAL compile and their own tests pass
integration    → (self-hosted / manual) real ROM, real build, real run
docs           → links resolve, diagrams render, claimed files exist
```

The first four run on every push and are fast. `integration` runs where the ROM legally
lives -- a self-hosted runner, or a developer's machine on demand.

### Golden-output tests, and their one trap

A golden test records the lifter's output for a fixed input and fails when it changes.
They are excellent and they have a specific failure mode: when output legitimately
changes, the temptation is to regenerate the goldens without reading the diff.

Make regeneration explicit and reviewable -- a separate command, output committed as a
normal change, and the diff read in review. A golden test you rubber-stamp is the CI
equivalent of the vacuous job in section 1.

---

## 4. Regression Gates at Scale

Once a project is large enough that no one holds its state in their head, "did this change
break something" needs a mechanical answer. `ps3recomp` ships a
[`docs/REGRESSION_GATE.md`](https://github.com/sp00nznet/ps3recomp/blob/main/docs/REGRESSION_GATE.md)
alongside `docs/MODULE_STATUS.md`, which tracks every HLE module as Not Started / Stubbed
/ Partial / Complete.

That pairing is the pattern worth copying:

- **A status file** that says what is claimed to work, in categories, per component.
- **A gate** that fails if something previously working stops working.

`MODULE_STATUS.md` is also a good example of why categories beat booleans. `cellVdec` is
"Partial -- open/close, start/end seq, AU submit with AUDONE+PICOUT callbacks (populated
PicItem), no actual H.264/MPEG2 decode." That is immediately actionable by a contributor
in a way "❌" is not, and Module 32's capstone suggestions are drawn straight from it.

### Categorise failures, do not count them

From Module 33's batch harness: extraction failed, codegen failed, compile failed, linked
but crashed, ran but diverged. Five numbers that move independently. A single
pass-rate percentage hides the fact that you fixed six compile failures and introduced
three crashes.

---

## 5. Build Time Is the Real Constraint

Module 34's numbers -- 114 MB of C in ~30 minutes, 231 MB, ~2 GB -- make full builds an
unusual CI problem.

**Cache by content hash, per stage.** Module 33's pipeline design pays off here directly:
if the function set did not change, extraction and disassembly do not re-run.

**Do not rebuild the world for a shim change.** The runtime and the generated code are
separate compilation domains. A change to `d3d8_device.c` must not retranslate 22,097
functions.

**Keep the translation unit split stable.** Restated from Module 34 because it is a CI
concern more than a codegen one: if adding one function reshuffles file contents, every
incremental build is a full build and your cache never hits.

**Consider building a subset in public CI.** Lifting 500 functions proves the pipeline
works end to end; lifting 40,067 proves it again, slower.

---

## 6. Documentation CI

This course's repository runs a `validate-mermaid` job, which is a better idea than it
first appears. Prose rots more quietly than code, and a recompilation project's prose is
load-bearing -- it is where all your claims live.

Cheap checks that catch real rot:

- **Every link resolves.** Repositories get renamed and deleted. This course found a
  reference pointing at a 0-star lookalike repository rather than the real 6,478-star
  project, purely because both names were plausible.
- **Every file path mentioned in docs exists.** If a module cites
  `src/recomp_rt.c`, assert it is there.
- **Diagrams render.**
- **Numbers carry a source.** Harder to automate, but a grep for bare percentages in prose
  is a start -- see Module 37.

---

## 7. What CI Cannot Tell You

Finish where Module 37 begins. Every check in this module answers "did something change?"
None of them answers "does it actually work?"

The projects in Modules 12, 22 and 27 all had builds that succeeded, binaries that ran,
and screenshots that looked right, while the thing on screen was drawn by harness code.
No CI job catches that. It is a question about *what your evidence means*, and it is the
subject of the next unit.

---

## Labs

- **Lab 55** -- Synthetic fixture suite: hand-assemble a fixture exercising every
  addressing mode and control-flow class for one ISA, and assert on the lifter's exact
  output.
- **Lab 56** -- Break your own CI: take a working pipeline, introduce a real defect at each
  stage, and confirm every stage's gate goes red. Document any defect that slipped through.

---

**Next: [Module 36 -- Configuration-Driven Recompilation](../module-36-config-driven-recomp/lecture.md)**
