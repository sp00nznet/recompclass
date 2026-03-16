# Recompilation Project Plan

## Target Binary

[TODO: Describe the binary you plan to recompile. Include the game/program
name, platform, file format, and approximate size. If it is a commercial
ROM, note the region and version.]

## Architecture

[TODO: Describe the CPU architecture. Include:
- CPU name and type (e.g., Z80, 6502, MIPS R4300i, ARM7TDMI)
- Word size (8-bit, 16-bit, 32-bit, 64-bit)
- Endianness (big or little)
- Key architectural features relevant to recompilation (e.g., delay slots,
  banked registers, multiple instruction sets)]

## Tool Selection

[TODO: List the tools you plan to use. Include at least:
- Disassembler / reverse-engineering tool (e.g., Ghidra, IDA, radare2)
- C compiler for the host platform (e.g., GCC, Clang, MSVC)
- Build system (e.g., CMake, Make, Ninja)
- Any platform-specific libraries or SDKs (e.g., SDL2 for graphics)]

## Milestones

[TODO: List at least 3 milestones. Number them and include a brief
description of what "done" looks like for each. Example:

1. **ROM loads and parses** -- Header is read, sections are identified,
   entry point is located.
2. **First function lifts** -- At least one function compiles and produces
   correct output when tested in isolation.
3. **Boot sequence runs** -- The program initializes and reaches the main
   loop without crashing.]

## Risk Assessment

[TODO: Identify at least 2 risks that could block or slow your project.
For each risk, describe:
- What the risk is
- How likely it is (low/medium/high)
- What you would do to mitigate it

Example:
- **Self-modifying code**: The target may modify its own instructions at
  runtime. Likelihood: medium. Mitigation: add a memory-write hook that
  invalidates the recompiled cache for modified regions.]

## Success Criteria

[TODO: Describe how you will know the project is "done enough." What does
the recompiled binary need to do? Examples:
- Boots to the title screen
- Plays through the first level
- Passes the original test suite
- Matches a reference trace with zero divergences]
