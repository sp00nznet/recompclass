"""
Tests for Lab 29: Mini-Project Planner

Tests the analysis_checklist.py validation functions using
synthetic Markdown documents.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import analysis_checklist


# ---------------------------------------------------------------------------
# Test documents
# ---------------------------------------------------------------------------

COMPLETE_DOC = """\
# Recompilation Project Plan

## Target Binary

Super Plumber Bros. for the NES (NTSC-U, PRG1 revision).
File: super_plumber.nes, 256 KB.

## Architecture

6502 (Ricoh 2A03), 8-bit, little-endian. No delay slots.
Banked ROM via MMC3 mapper.

## Tool Selection

- Ghidra with 6502 processor module
- GCC 13 for host compilation
- CMake for build system
- SDL2 for graphics/audio output

## Milestones

1. ROM loads and header parses correctly
2. First function (reset vector) lifts and runs
3. Title screen renders

## Risk Assessment

- **Self-modifying code**: Medium likelihood. Mitigate with memory hooks.
- **Cycle-accurate timing**: High likelihood for audio. Mitigate with
  timer-based scheduling.

## Success Criteria

The recompiled binary boots to the title screen and plays the first
level to completion with correct graphics and audio.
"""

INCOMPLETE_DOC = """\
# Recompilation Project Plan

## Target Binary

[TODO: describe your target]

## Architecture

6502, 8-bit.

## Tool Selection

Ghidra, GCC, CMake.
"""

EMPTY_DOC = "# Nothing here\n"


# ---------------------------------------------------------------------------
# parse_sections
# ---------------------------------------------------------------------------

class TestParseSections:
    def test_returns_dict(self):
        result = analysis_checklist.parse_sections(COMPLETE_DOC)
        assert result is not None, "parse_sections() returned None"
        assert isinstance(result, dict)

    def test_finds_all_sections(self):
        sections = analysis_checklist.parse_sections(COMPLETE_DOC)
        for title in analysis_checklist.REQUIRED_SECTIONS:
            assert title in sections, f"Missing section: {title}"

    def test_section_bodies_nonempty(self):
        sections = analysis_checklist.parse_sections(COMPLETE_DOC)
        for title, body in sections.items():
            assert len(body.strip()) > 0, f"Empty body for: {title}"

    def test_empty_doc(self):
        sections = analysis_checklist.parse_sections(EMPTY_DOC)
        assert len(sections) == 0


# ---------------------------------------------------------------------------
# check_section_present
# ---------------------------------------------------------------------------

class TestCheckSectionPresent:
    def test_present_with_content(self):
        sections = analysis_checklist.parse_sections(COMPLETE_DOC)
        found, has_content = analysis_checklist.check_section_present(
            sections, "Target Binary")
        assert found is True
        assert has_content is True

    def test_present_but_todo(self):
        sections = analysis_checklist.parse_sections(INCOMPLETE_DOC)
        found, has_content = analysis_checklist.check_section_present(
            sections, "Target Binary")
        assert found is True
        assert has_content is False

    def test_missing(self):
        sections = analysis_checklist.parse_sections(INCOMPLETE_DOC)
        found, has_content = analysis_checklist.check_section_present(
            sections, "Milestones")
        assert found is False


# ---------------------------------------------------------------------------
# count_list_items
# ---------------------------------------------------------------------------

class TestCountListItems:
    def test_milestones_count(self):
        sections = analysis_checklist.parse_sections(COMPLETE_DOC)
        count = analysis_checklist.count_list_items(sections, "Milestones")
        assert count >= 3

    def test_risks_count(self):
        sections = analysis_checklist.parse_sections(COMPLETE_DOC)
        count = analysis_checklist.count_list_items(sections, "Risk Assessment")
        assert count >= 2

    def test_missing_section(self):
        sections = analysis_checklist.parse_sections(INCOMPLETE_DOC)
        count = analysis_checklist.count_list_items(sections, "Milestones")
        assert count == 0


# ---------------------------------------------------------------------------
# Full checklist
# ---------------------------------------------------------------------------

class TestRunChecklist:
    def test_complete_plan(self):
        # Write to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md",
                                         delete=False, encoding="utf-8") as f:
            f.write(COMPLETE_DOC)
            path = f.name
        try:
            passed, failed = analysis_checklist.run_checklist(path)
            assert len(failed) == 0, f"Unexpected failures: {failed}"
            assert len(passed) == len(analysis_checklist.REQUIRED_SECTIONS)
        finally:
            os.unlink(path)

    def test_incomplete_plan(self):
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md",
                                         delete=False, encoding="utf-8") as f:
            f.write(INCOMPLETE_DOC)
            path = f.name
        try:
            passed, failed = analysis_checklist.run_checklist(path)
            assert len(failed) > 0, "Should have failures for incomplete plan"
        finally:
            os.unlink(path)
