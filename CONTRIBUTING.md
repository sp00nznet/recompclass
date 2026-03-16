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
