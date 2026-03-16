"""
Lab 29: Project Plan Checklist Validator

Parses a Markdown project plan and verifies that all required sections
are present and contain real content (not just the TODO placeholder).
"""

import sys
import os
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


# ---------------------------------------------------------------------------
# Required sections
# ---------------------------------------------------------------------------

REQUIRED_SECTIONS = [
    "Target Binary",
    "Architecture",
    "Tool Selection",
    "Milestones",
    "Risk Assessment",
    "Success Criteria",
]

# Sections that need numbered/bulleted items
SECTIONS_WITH_ITEMS = {
    "Milestones": 3,       # at least 3 milestones
    "Risk Assessment": 2,  # at least 2 risks
}


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def parse_sections(text):
    """Parse a Markdown document into sections.

    Args:
        text: the full Markdown text.

    Returns:
        A dict mapping section title (str) -> section body (str).
        Section titles are taken from ## headings, stripped of
        leading/trailing whitespace.
    """
    # TODO: 1. Split the text by lines.
    # TODO: 2. Walk through lines looking for lines starting with "## ".
    # TODO: 3. For each heading, collect all following lines until the next
    #          heading (or end of file) as the section body.
    # TODO: 4. Return a dict of {title: body}.
    pass


def check_section_present(sections, title):
    """Check whether a section exists and has content beyond the TODO placeholder.

    Args:
        sections: dict from parse_sections().
        title: the section title to look for.

    Returns:
        Tuple of (found, has_content):
            found: bool, True if the section heading exists.
            has_content: bool, True if the body contains text other
                         than the [TODO: ...] placeholder.
    """
    # TODO: 1. Check if title is in sections.
    # TODO: 2. If found, check whether the body contains "[TODO:" --
    #          if it does and there is no other substantial text, the
    #          student has not filled it in yet.
    #          A simple heuristic: if the body stripped of TODO blocks
    #          and whitespace is non-empty, treat it as having content.
    # TODO: 3. Return (found, has_content).
    pass


def count_list_items(sections, title):
    """Count numbered or bulleted list items in a section.

    Looks for lines starting with "- " or "N. " (where N is a digit).

    Args:
        sections: dict from parse_sections().
        title: the section title.

    Returns:
        The number of list items found (int). Returns 0 if section
        is missing.
    """
    # TODO: 1. Get the section body.
    # TODO: 2. Count lines that match r'^\s*(\d+\.|[-*])\s' (numbered
    #          or bulleted list items).
    # TODO: 3. Return the count.
    pass


def run_checklist(filepath):
    """Run the full checklist against a project plan file.

    Args:
        filepath: path to the Markdown file.

    Returns:
        Tuple of (passed, failed) where each is a list of message strings.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    sections = parse_sections(text)
    if sections is None:
        return [], ["parse_sections() returned None"]

    passed = []
    failed = []

    for title in REQUIRED_SECTIONS:
        found, has_content = check_section_present(sections, title)
        if not found:
            failed.append(f"Section missing: {title}")
        elif not has_content:
            failed.append(f"Section not filled in: {title}")
        else:
            if title in SECTIONS_WITH_ITEMS:
                min_items = SECTIONS_WITH_ITEMS[title]
                count = count_list_items(sections, title)
                if count >= min_items:
                    passed.append(
                        f"Section found: {title} ({count} items found)")
                else:
                    failed.append(
                        f"Section {title}: need {min_items} items, "
                        f"found {count}")
            else:
                passed.append(f"Section found: {title}")

    return passed, failed


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <project_plan.md>")
        sys.exit(1)

    filepath = sys.argv[1]
    if not os.path.isfile(filepath):
        print(f"Error: file not found: {filepath}")
        sys.exit(1)

    print(f"Checking {filepath}...")
    passed, failed = run_checklist(filepath)

    for msg in passed:
        print(f"[PASS] {msg}")
    for msg in failed:
        print(f"[FAIL] {msg}")

    print()
    if not failed:
        print("All checks passed! Your project plan is complete.")
    else:
        print(f"{len(failed)} check(s) failed. Fill in the missing sections.")
        sys.exit(1)


if __name__ == "__main__":
    main()
