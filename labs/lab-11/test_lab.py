"""
Lab 11 Tests: CFG to Mermaid Diagram Converter

Verifies that the output is valid Mermaid syntax by checking for required
structural elements.
"""

import unittest
from cfg_to_mermaid import (
    BlockInfo,
    generate_mermaid,
    adjacency_list_to_mermaid,
    _sanitize_node_id,
)


def make_simple_cfg():
    """Build a simple 3-block CFG for testing."""
    return {
        0x0000: BlockInfo(
            address=0x0000,
            instructions=["LOAD 10", "CMP 0", "JZ 0x0008"],
            successors=[0x0004, 0x0008],
            is_conditional_exit=True,
        ),
        0x0004: BlockInfo(
            address=0x0004,
            instructions=["STORE 0"],
            successors=[0x0008],
        ),
        0x0008: BlockInfo(
            address=0x0008,
            instructions=["HALT"],
            successors=[],
        ),
    }


class TestMermaidStructure(unittest.TestCase):
    """Test that generated Mermaid has correct structural elements."""

    def test_starts_with_graph_directive(self):
        blocks = make_simple_cfg()
        output = generate_mermaid(blocks)
        self.assertIn("graph TD", output)

    def test_custom_direction(self):
        blocks = make_simple_cfg()
        output = generate_mermaid(blocks, direction="LR")
        self.assertIn("graph LR", output)

    def test_contains_title(self):
        blocks = make_simple_cfg()
        output = generate_mermaid(blocks, title="My Test CFG")
        self.assertIn("title: My Test CFG", output)

    def test_contains_node_definitions(self):
        blocks = make_simple_cfg()
        output = generate_mermaid(blocks)
        # Each block should appear as a node
        self.assertIn("blk_0000", output)
        self.assertIn("blk_0004", output)
        self.assertIn("blk_0008", output)

    def test_contains_edges(self):
        blocks = make_simple_cfg()
        output = generate_mermaid(blocks)
        # The conditional block should have labeled edges
        self.assertIn("fall-through", output)
        self.assertIn("taken", output)

    def test_unconditional_edge_no_label(self):
        blocks = {
            0x0000: BlockInfo(address=0x0000, successors=[0x0004]),
            0x0004: BlockInfo(address=0x0004, successors=[]),
        }
        output = generate_mermaid(blocks)
        self.assertIn("blk_0000 --> blk_0004", output)
        # Should NOT have conditional labels
        self.assertNotIn("fall-through", output)
        self.assertNotIn("taken", output)

    def test_no_edges_for_terminal_block(self):
        blocks = {
            0x0000: BlockInfo(address=0x0000, instructions=["HALT"], successors=[]),
        }
        output = generate_mermaid(blocks)
        # Should contain the node but no arrow
        self.assertIn("blk_0000", output)
        self.assertNotIn("-->", output)


class TestNodeLabels(unittest.TestCase):
    """Test node label content."""

    def test_shows_instructions_by_default(self):
        blocks = {
            0x0000: BlockInfo(
                address=0x0000,
                instructions=["LOAD 42", "HALT"],
                successors=[],
            ),
        }
        output = generate_mermaid(blocks, show_instructions=True)
        self.assertIn("LOAD 42", output)
        self.assertIn("HALT", output)

    def test_hides_instructions_when_disabled(self):
        blocks = {
            0x0000: BlockInfo(
                address=0x0000,
                instructions=["LOAD 42", "HALT"],
                successors=[],
            ),
        }
        output = generate_mermaid(blocks, show_instructions=False)
        self.assertNotIn("LOAD 42", output)
        self.assertIn("Block 0x0000", output)

    def test_custom_label(self):
        blocks = {
            0x0000: BlockInfo(
                address=0x0000,
                label="Entry Point",
                successors=[],
            ),
        }
        output = generate_mermaid(blocks)
        self.assertIn("Entry Point", output)


class TestHighlighting(unittest.TestCase):
    """Test path highlighting."""

    def test_highlight_adds_class_def(self):
        blocks = make_simple_cfg()
        output = generate_mermaid(blocks, highlight_path=[0x0000, 0x0004])
        self.assertIn("classDef highlighted", output)

    def test_highlight_applies_class(self):
        blocks = make_simple_cfg()
        output = generate_mermaid(blocks, highlight_path=[0x0000])
        self.assertIn("class blk_0000 highlighted", output)

    def test_highlighted_node_uses_stadium_shape(self):
        blocks = make_simple_cfg()
        output = generate_mermaid(blocks, highlight_path=[0x0000])
        # Stadium shape uses ([" ... "])
        self.assertIn('(["', output)

    def test_no_highlight_no_class_def(self):
        blocks = make_simple_cfg()
        output = generate_mermaid(blocks)
        self.assertNotIn("classDef highlighted", output)


class TestAdjacencyListShorthand(unittest.TestCase):
    """Test the adjacency-list convenience function."""

    def test_basic_adjacency_list(self):
        adj = {
            0x0000: [0x0004],
            0x0004: [],
        }
        output = adjacency_list_to_mermaid(adj)
        self.assertIn("graph TD", output)
        self.assertIn("blk_0000 --> blk_0004", output)

    def test_conditional_blocks(self):
        adj = {
            0x0000: [0x0004, 0x0008],
            0x0004: [],
            0x0008: [],
        }
        output = adjacency_list_to_mermaid(adj, conditional_blocks={0x0000})
        self.assertIn("fall-through", output)
        self.assertIn("taken", output)

    def test_empty_cfg(self):
        output = adjacency_list_to_mermaid({})
        self.assertIn("graph TD", output)


class TestSanitizeNodeId(unittest.TestCase):
    """Test node ID generation."""

    def test_format(self):
        self.assertEqual(_sanitize_node_id(0), "blk_0000")
        self.assertEqual(_sanitize_node_id(0x1234), "blk_1234")
        self.assertEqual(_sanitize_node_id(0xABCD), "blk_ABCD")


if __name__ == "__main__":
    unittest.main()
