# Contributing to recompclass

Thank you for your interest in contributing to the Static Recompilation open course. This project aims to grow the static recompilation community by making knowledge accessible to everyone.

## Ways to Contribute

### Content Improvements
- Fix typos, grammar, or unclear explanations
- Improve diagrams or add new ones
- Add cross-references between modules
- Expand glossary definitions

### Lab Contributions
- Fix bugs in lab starter code or solutions
- Add test cases for existing labs
- Propose new lab exercises (open an issue first)

### New Material
- Architecture reference sheets for ISAs not yet covered
- Cheat sheets for tools used in the course
- Translations to other languages

### Capstone Contributions (Module 16)
- HLE module implementations
- Toy recompiler examples
- Documentation of your own recompilation projects

## Guidelines

### Before You Start
1. Check existing [issues](../../issues) to avoid duplicate work
2. For non-trivial changes, open an issue to discuss your approach first
3. Read the [Syllabus](SYLLABUS.md) to understand how modules connect

### Content Standards
- Write in clear, technical English
- Use Mermaid for diagrams where possible (renders natively on GitHub)
- Use SVG only for complex hardware diagrams that exceed Mermaid's capabilities
- Follow the existing color scheme: blue=pipeline stages, green=hardware, orange=decisions, red=challenges
- All code examples must compile/run as shown
- No copyrighted ROMs or binaries -- homebrew and open-source test programs only

### Code Standards
- Lab code should be in C (recompiler code) or Python (analysis tools)
- Include comments explaining non-obvious logic
- Starter code must compile without errors
- Solutions must produce the expected output

### Commit Messages
- Use imperative mood: "Add MIPS reference sheet" not "Added MIPS reference sheet"
- Reference module numbers where relevant: "Fix diagram in Module 8"

## Submitting Changes

1. Fork the repository
2. Create a feature branch: `git checkout -b add-sh4-reference`
3. Make your changes
4. Test that all Mermaid diagrams render (preview on GitHub or use mermaid-cli)
5. Test that lab code compiles and runs
6. Submit a pull request with a clear description of what and why

## Code of Conduct

Be respectful, constructive, and focused on growing the community. We are all here because we think static recompilation is fascinating and worth preserving knowledge about.

## Questions?

Open an issue with the "question" label.

---

## Labs and Reference Solutions

Each lab ships a stub whose unimplemented functions end in a `# TODO:` block.
**The stub's tests are supposed to fail** until you fill them in -- that is the
exercise, not a bug.

Reference solutions live in `labs/lab-NN/solution/`. Try the lab first; the
solution is there so you can check your work and so CI has something real to
gate on.

### Working on labs

```bash
pytest labs/lab-01                 # run one lab's tests against your work
python tools/check_solutions.py    # run every lab's tests against its solution
python tools/check_solutions.py lab-04   # just one
```

`check_solutions.py` swaps the solution into the lab directory, runs pytest, and
swaps the stub back. The lab tests do a plain `import <module>` and rely on
pytest putting the test file's own directory on `sys.path`, so swapping is the
only reliable way to exercise the solution.

### Changing a lab

Solutions are **generated**, not hand-maintained:

```bash
python tools/make_solutions.py           # regenerate all solutions
python tools/make_solutions.py --check   # verify they are current (CI does this)
```

The implementations live in the patch table in `tools/make_solutions.py`. If you
change a stub's shape, regenerate -- and if the generator can no longer find a
function's TODO block it fails loudly rather than emitting a solution that no
longer matches the exercise.

Bodies in that table are raw strings, so a backslash in a body is a backslash in
the generated file.

### What CI checks

CI cannot run the labs to completion (that needs the stubs filled in), so it
gates on what is always true: every lab module imports, every test file
collects, the solutions are current, and every solution passes its own tests.
