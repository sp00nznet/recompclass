"""
Lab 11: CFG to Mermaid Diagram Converter

Takes a control flow graph represented as basic blocks with an adjacency list
and produces a Mermaid flowchart diagram.

Supports:
  - Basic block nodes with instruction listings
  - Labeled edges (taken, fall-through)
  - Path highlighting via CSS classes
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple


# ---------------------------------------------------------------------------
# CFG Input Representation
# ---------------------------------------------------------------------------

@dataclass
class BlockInfo:
    """
    Information about a basic block for visualization purposes.

    This is a simplified representation that can come from Lab 10's CFG
    or any other source.
    """
    address: int
    instructions: List[str] = field(default_factory=list)  # Human-readable instruction text
    successors: List[int] = field(default_factory=list)     # Successor block addresses
    # For conditional branches, the first successor is the fall-through
    # and the second is the taken branch. For unconditional jumps, there
    # is only one successor.
    is_conditional_exit: bool = False   # True if the block ends with a conditional branch
    label: str = ""                     # Optional custom label


# ---------------------------------------------------------------------------
# Mermaid Generator
# ---------------------------------------------------------------------------

def _sanitize_node_id(address: int) -> str:
    """Create a valid Mermaid node ID from a block address."""
    return f"blk_{address:04X}"


def _escape_mermaid_text(text: str) -> str:
    """Escape special characters for Mermaid labels."""
    # Mermaid uses quotes to delimit labels; escape internal quotes
    return text.replace('"', "'")


def generate_mermaid(
    blocks: Dict[int, BlockInfo],
    title: str = "Control Flow Graph",
    direction: str = "TD",
    highlight_path: Optional[List[int]] = None,
    show_instructions: bool = True,
) -> str:
    """
    Generate a Mermaid flowchart from a set of basic blocks.

    Args:
        blocks: Dict mapping block addresses to BlockInfo objects.
        title: Title comment for the diagram.
        direction: Flow direction -- "TD" (top-down) or "LR" (left-right).
        highlight_path: Optional list of block addresses to highlight.
        show_instructions: If True, include instruction text in node labels.

    Returns:
        A string containing the complete Mermaid diagram.
    """
    if highlight_path is None:
        highlight_path = []
    highlight_set: Set[int] = set(highlight_path)

    lines: List[str] = []
    lines.append(f"---")
    lines.append(f"title: {title}")
    lines.append(f"---")
    lines.append(f"graph {direction}")

    # -- Define nodes --
    for addr in sorted(blocks.keys()):
        block = blocks[addr]
        node_id = _sanitize_node_id(addr)
        label = _build_node_label(block, show_instructions)
        escaped = _escape_mermaid_text(label)

        # Use a stadium shape for highlighted nodes, rectangles for normal
        if addr in highlight_set:
            lines.append(f'    {node_id}(["{escaped}"])')
        else:
            lines.append(f'    {node_id}["{escaped}"]')

    lines.append("")

    # -- Define edges --
    for addr in sorted(blocks.keys()):
        block = blocks[addr]
        src_id = _sanitize_node_id(addr)

        if block.is_conditional_exit and len(block.successors) == 2:
            # First successor: fall-through, second: taken
            fall_through_addr = block.successors[0]
            taken_addr = block.successors[1]

            ft_id = _sanitize_node_id(fall_through_addr)
            tk_id = _sanitize_node_id(taken_addr)

            lines.append(f'    {src_id} -->|"fall-through"| {ft_id}')
            lines.append(f'    {src_id} -->|"taken"| {tk_id}')
        else:
            for succ_addr in block.successors:
                dst_id = _sanitize_node_id(succ_addr)
                lines.append(f'    {src_id} --> {dst_id}')

    # -- Highlight styling --
    if highlight_set:
        lines.append("")
        lines.append("    %% Highlight styling")
        lines.append("    classDef highlighted fill:#f9f,stroke:#333,stroke-width:2px")
        highlighted_ids = " ".join(_sanitize_node_id(a) for a in sorted(highlight_set) if a in blocks)
        if highlighted_ids:
            lines.append(f"    class {highlighted_ids} highlighted")

    return "\n".join(lines)


def _build_node_label(block: BlockInfo, show_instructions: bool) -> str:
    """Build the text label for a basic block node."""
    if block.label:
        header = f"{block.label} (0x{block.address:04X})"
    else:
        header = f"Block 0x{block.address:04X}"

    if show_instructions and block.instructions:
        # Show instructions, separated by newlines (Mermaid uses <br/> in labels)
        instr_text = "<br/>".join(block.instructions)
        return f"{header}<br/>---<br/>{instr_text}"
    else:
        return header


# ---------------------------------------------------------------------------
# Convenience: convert from adjacency list
# ---------------------------------------------------------------------------

def adjacency_list_to_mermaid(
    adj: Dict[int, List[int]],
    title: str = "Control Flow Graph",
    direction: str = "TD",
    conditional_blocks: Optional[Set[int]] = None,
) -> str:
    """
    Generate a Mermaid diagram from a simple adjacency list.

    This is useful when you do not have full BlockInfo objects -- just
    addresses and edges.

    Args:
        adj: Dict mapping block address -> list of successor addresses.
        title: Diagram title.
        direction: Flow direction.
        conditional_blocks: Set of block addresses that end with conditional branches.

    Returns:
        Mermaid diagram string.
    """
    if conditional_blocks is None:
        conditional_blocks = set()

    blocks: Dict[int, BlockInfo] = {}
    for addr, successors in adj.items():
        blocks[addr] = BlockInfo(
            address=addr,
            successors=list(successors),
            is_conditional_exit=(addr in conditional_blocks and len(successors) == 2),
        )

    return generate_mermaid(blocks, title=title, direction=direction, show_instructions=False)


# ---------------------------------------------------------------------------
# TODO: Dominator tree visualization
# ---------------------------------------------------------------------------

def compute_dominators(adj: Dict[int, List[int]], entry: int) -> Dict[int, int]:
    """
    Compute the immediate dominator for each block in the CFG.

    TODO: Implement this using the iterative dominator algorithm:
          1. Initialize dom(entry) = entry, dom(n) = all_nodes for all other n.
          2. Repeat until stable:
             For each node n (except entry), in reverse postorder:
               dom(n) = intersect(dom(p) for p in predecessors(n))
          3. Return a dict mapping each node to its immediate dominator.

    This is needed for structured code recovery (identifying if-then-else,
    loops, etc.) in static recompilation.
    """
    raise NotImplementedError("Dominator computation not yet implemented")


def generate_dominator_tree_mermaid(dominators: Dict[int, int], entry: int) -> str:
    """
    Generate a Mermaid diagram showing the dominator tree.

    TODO: Implement this once compute_dominators is available.
          The dominator tree has an edge from idom(n) to n for each node.
    """
    raise NotImplementedError("Dominator tree visualization not yet implemented")


# ---------------------------------------------------------------------------
# TODO: Loop detection
# ---------------------------------------------------------------------------

def detect_natural_loops(adj: Dict[int, List[int]], entry: int) -> List[Set[int]]:
    """
    Detect natural loops in the CFG.

    TODO: Implement this:
          1. Compute a DFS tree from the entry point.
          2. Identify back edges (edges where the target dominates the source).
          3. For each back edge (n -> h), compute the natural loop:
             the set of nodes that can reach n without going through h,
             plus h itself.
          4. Return a list of loops, each as a set of block addresses.
    """
    raise NotImplementedError("Loop detection not yet implemented")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== Lab 11: CFG Visualizer ===\n")

    # Example: a small CFG with a conditional branch and a loop
    blocks = {
        0x0000: BlockInfo(
            address=0x0000,
            instructions=["LOAD 10"],
            successors=[0x0002],
        ),
        0x0002: BlockInfo(
            address=0x0002,
            instructions=["SUB 1", "CMP 0", "JZ 0x000C"],
            successors=[0x0008, 0x000C],
            is_conditional_exit=True,
            label="Loop Header",
        ),
        0x0008: BlockInfo(
            address=0x0008,
            instructions=["JMP 0x0002"],
            successors=[0x0002],
            label="Loop Back",
        ),
        0x000C: BlockInfo(
            address=0x000C,
            instructions=["HALT"],
            successors=[],
            label="Exit",
        ),
    }

    # Generate with instruction details
    mermaid = generate_mermaid(
        blocks,
        title="Example Loop CFG",
        highlight_path=[0x0002, 0x0008],
    )

    print("Generated Mermaid diagram:\n")
    print(mermaid)
    print()

    # Also demonstrate the adjacency-list shorthand
    print("--- From adjacency list ---\n")
    adj = {
        0x0000: [0x0004, 0x0008],
        0x0004: [0x000C],
        0x0008: [0x000C],
        0x000C: [],
    }
    simple_mermaid = adjacency_list_to_mermaid(
        adj,
        title="Diamond CFG",
        conditional_blocks={0x0000},
    )
    print(simple_mermaid)
