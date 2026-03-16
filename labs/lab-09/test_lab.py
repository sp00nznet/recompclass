"""
Lab 9 Tests: Dispatch Table Generator

Verifies that the generated C code is structurally correct for all three
dispatch strategies.
"""

import re
import unittest
from dispatch_gen import (
    generate_switch_dispatch,
    generate_bsearch_dispatch,
    generate_hash_dispatch,
    generate_all_dispatchers,
    JumpTarget,
)

# A small set of test targets
TEST_TARGETS: list = [
    (0x00401000, "func_00401000"),
    (0x00401050, "func_00401050"),
    (0x004010A0, "func_004010A0"),
    (0x00401100, "func_00401100"),
]


class TestSwitchDispatch(unittest.TestCase):
    """Test the switch/case dispatch generator."""

    def test_contains_switch_statement(self):
        code = generate_switch_dispatch(TEST_TARGETS)
        self.assertIn("switch (addr)", code)

    def test_contains_all_cases(self):
        code = generate_switch_dispatch(TEST_TARGETS)
        for addr, func_name in TEST_TARGETS:
            self.assertIn(f"case 0x{addr:08X}:", code)
            self.assertIn(f"return {func_name};", code)

    def test_contains_default_case(self):
        code = generate_switch_dispatch(TEST_TARGETS)
        self.assertIn("default:", code)

    def test_contains_function_signature(self):
        code = generate_switch_dispatch(TEST_TARGETS)
        self.assertIn("recomp_func_t dispatch_switch(uint32_t addr)", code)

    def test_forward_declarations(self):
        code = generate_switch_dispatch(TEST_TARGETS)
        for _, func_name in TEST_TARGETS:
            self.assertIn(f"void {func_name}(cpu_state_t *ctx);", code)

    def test_balanced_braces(self):
        code = generate_switch_dispatch(TEST_TARGETS)
        self.assertEqual(code.count("{"), code.count("}"))

    def test_includes_header(self):
        code = generate_switch_dispatch(TEST_TARGETS)
        self.assertIn('#include "dispatch.h"', code)


class TestBsearchDispatch(unittest.TestCase):
    """Test the binary search dispatch generator."""

    def test_contains_sorted_table(self):
        code = generate_bsearch_dispatch(TEST_TARGETS)
        self.assertIn("dispatch_entry_t dispatch_table", code)

    def test_table_entries_are_sorted(self):
        code = generate_bsearch_dispatch(TEST_TARGETS)
        # Extract addresses from the table entries
        addresses = re.findall(r"0x([0-9A-Fa-f]{8}),", code)
        addr_values = [int(a, 16) for a in addresses if int(a, 16) != 0]
        # Verify they are in ascending order
        self.assertEqual(addr_values, sorted(addr_values))

    def test_contains_binary_search_logic(self):
        code = generate_bsearch_dispatch(TEST_TARGETS)
        self.assertIn("while (lo <= hi)", code)
        self.assertIn("mid = lo + (hi - lo) / 2", code)

    def test_contains_function_signature(self):
        code = generate_bsearch_dispatch(TEST_TARGETS)
        self.assertIn("recomp_func_t dispatch_bsearch(uint32_t addr)", code)

    def test_balanced_braces(self):
        code = generate_bsearch_dispatch(TEST_TARGETS)
        self.assertEqual(code.count("{"), code.count("}"))

    def test_table_size_matches(self):
        code = generate_bsearch_dispatch(TEST_TARGETS)
        self.assertIn(f"#define DISPATCH_TABLE_SIZE {len(TEST_TARGETS)}", code)


class TestHashDispatch(unittest.TestCase):
    """Test the hash table dispatch generator."""

    def test_contains_hash_table(self):
        code = generate_hash_dispatch(TEST_TARGETS)
        self.assertIn("hash_table[HASH_TABLE_SIZE]", code)

    def test_table_size_is_power_of_2(self):
        code = generate_hash_dispatch(TEST_TARGETS)
        match = re.search(r"#define HASH_TABLE_SIZE (\d+)", code)
        self.assertIsNotNone(match)
        size = int(match.group(1))
        # Check power of 2: size & (size - 1) == 0
        self.assertEqual(size & (size - 1), 0)
        # Table should be at least 2x the number of entries
        self.assertGreaterEqual(size, len(TEST_TARGETS) * 2)

    def test_contains_linear_probing(self):
        code = generate_hash_dispatch(TEST_TARGETS)
        self.assertIn("(slot + 1) & HASH_MASK", code)

    def test_contains_function_signature(self):
        code = generate_hash_dispatch(TEST_TARGETS)
        self.assertIn("recomp_func_t dispatch_hash(uint32_t addr)", code)

    def test_all_targets_in_table(self):
        code = generate_hash_dispatch(TEST_TARGETS)
        for addr, func_name in TEST_TARGETS:
            self.assertIn(f"0x{addr:08X}", code)
            self.assertIn(func_name, code)

    def test_balanced_braces(self):
        code = generate_hash_dispatch(TEST_TARGETS)
        self.assertEqual(code.count("{"), code.count("}"))


class TestGenerateAll(unittest.TestCase):
    """Test the convenience function that generates all strategies."""

    def test_returns_all_three(self):
        result = generate_all_dispatchers(TEST_TARGETS)
        self.assertIn("switch", result)
        self.assertIn("bsearch", result)
        self.assertIn("hash", result)

    def test_single_target(self):
        """Should work with just one target."""
        targets = [(0x00400000, "func_main")]
        result = generate_all_dispatchers(targets)
        for strategy_name, code in result.items():
            self.assertIn("func_main", code)

    def test_empty_targets(self):
        """Should handle empty target list without crashing."""
        result = generate_all_dispatchers([])
        self.assertIn("switch", result)


if __name__ == "__main__":
    unittest.main()
