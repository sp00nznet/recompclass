# Lab 98: Unit 14 Capstone: A New Architecture

## Objective

Take a target nobody has recompiled from feasibility report to a
differentially-validated decoder.

## Your Task

**The report** (Lab 96). Do not skip it; it decides the rest.

**The decoder.** Table-driven (Module 34 section 2), with a control-flow
class per opcode. Generate the table from a machine-readable ISA description
if one exists.

**The interpreter oracle**, generated from the same table (Lab 62).

**Differential validation** (Lab 89). Against an independent implementation
if one exists -- Module 53's standard is *"written by someone else, from the
same documentation, in another language."* Against real hardware if not.

**A machine document** (Lab 115) separating published fact from inference.

## Deliverable

A toolkit repository with no ROMs in it, a decoder, an oracle, a validation
report, and machine documentation.

You do **not** need a running program. Module 59's shapes: a toolkit is done
when a second program works on it, and a research log is done when the
question is answered. Say which you are delivering.

## What Good Looks Like

Your validation found something, and you wrote it up -- including any harness
bugs that impersonated target bugs (Module 62 section 5).
