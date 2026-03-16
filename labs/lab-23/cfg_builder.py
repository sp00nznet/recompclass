"""
Lab 23: CFG Builder (Recursive Descent)

Build a control-flow graph from SimpleISA bytecode using recursive
descent disassembly.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

from simple_isa import (
    decode_one, format_instruction,
    BRANCH_OPCODES, JUMP_OPCODES, FALLTHROUGH_OPCODES, TERMINATOR_OPCODES,
)


# ---------------------------------------------------------------------------
# Basic Block
# ---------------------------------------------------------------------------

class BasicBlock:
    """A straight-line sequence of instructions with edges to successors.

    Attributes:
        start_addr: int, address of the first instruction.
        instructions: list of decoded instruction dicts.
        successors: list of (target_addr, edge_label) tuples.
                    edge_label is "fall" for fall-through, "taken" for
                    branch/jump targets.
    """

    def __init__(self, start_addr):
        self.start_addr = start_addr
        self.instructions = []
        self.successors = []

    def end_addr(self):
        """Address just past the last instruction in this block."""
        if not self.instructions:
            return self.start_addr
        last = self.instructions[-1]
        return last["address"] + last["length"]

    def label(self):
        return f"blk_{self.start_addr:04X}"

    def __repr__(self):
        return f"BasicBlock(0x{self.start_addr:04X}, {len(self.instructions)} instrs)"


# ---------------------------------------------------------------------------
# CFG Construction
# ---------------------------------------------------------------------------

def build_cfg(data, entry_point=0):
    """Build a control-flow graph via recursive descent disassembly.

    Starting at *entry_point*, decode instructions sequentially until
    a branch/jump/return is hit, forming a basic block. Then recursively
    follow branch targets and fall-through addresses to discover more
    blocks.

    Args:
        data: bytes, the program image.
        entry_point: int, address to start disassembly.

    Returns:
        A dict mapping start_address (int) -> BasicBlock.
    """
    # TODO: 1. Create a work-list (a list or set of addresses to visit),
    #          starting with [entry_point].
    #       2. Create an empty dict for the CFG blocks.
    #       3. While the work-list is not empty:
    #          a. Pop an address from the work-list.
    #          b. If a block already exists at this address, skip it.
    #          c. Create a new BasicBlock at this address.
    #          d. Decode instructions sequentially:
    #             - Call decode_one(data, addr) for each instruction.
    #             - Append to the block's instructions list.
    #             - If the instruction's opcode is in BRANCH_OPCODES,
    #               stop the sequential decode (end of basic block).
    #             - If decode_one returns None, stop (invalid code).
    #          e. After the block ends, determine successors:
    #             - If the last opcode is in JUMP_OPCODES, add the
    #               jump target with label "taken" to successors,
    #               and add the target address to the work-list.
    #             - If the last opcode is in FALLTHROUGH_OPCODES,
    #               add the fall-through address with label "fall",
    #               and add it to the work-list.
    #             - If the last opcode is JMP (0x05), it also has a
    #               "taken" successor but no fall-through.
    #             - RET (0x08) has no successors.
    #          f. Store the block in the CFG dict.
    #       4. Return the CFG dict.
    #
    # Watch out for: blocks that start in the middle of an existing block.
    # For simplicity, this lab does not require splitting blocks.
    pass


def cfg_to_dot(cfg):
    """Convert a CFG dict to Graphviz DOT format.

    Args:
        cfg: dict of start_address -> BasicBlock.

    Returns:
        A string containing valid DOT source.
    """
    # TODO: 1. Start with 'digraph CFG {\n'
    #       2. Add a node shape declaration:
    #          '  node [shape=box, fontname="Courier"];\n'
    #       3. For each block (sorted by start_addr):
    #          - Build a label string from the formatted instructions
    #            (use format_instruction()), joined by "\\n".
    #          - Emit: '  "{label}" [label="{instr_text}"];\n'
    #       4. For each block, for each successor:
    #          - Emit: '  "{src_label}" -> "{dst_label}" [label="{edge}"];\n'
    #       5. End with '}\n'
    #       6. Return the string.
    pass


def print_cfg(cfg):
    """Print a textual summary of the CFG."""
    for addr in sorted(cfg):
        block = cfg[addr]
        print(f"--- Block 0x{addr:04X} ---")
        for instr in block.instructions:
            print(f"  {format_instruction(instr)}")
        if block.successors:
            targets = ", ".join(
                f"0x{t:04X} ({lbl})" for t, lbl in block.successors
            )
            print(f"  -> {targets}")
        else:
            print("  -> (end)")
        print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    # Example program:
    #   0000: LOAD r0
    #   0002: BEQ 0006
    #   0005: STORE r1    (fall-through from BEQ)
    #   0007: JMP 0009    (skip to end -- note: this is 3 bytes, target 0x0009)
    #   0009: RET         (branch target and jump target merge here)
    #
    # Note: BEQ target 0x0006 is actually a STORE at 0x0005?
    # Let's fix the addresses to be consistent:
    program = bytes([
        0x02, 0x00,             # 0000: LOAD r0
        0x06, 0x07, 0x00,       # 0002: BEQ 0007
        0x03, 0x01,             # 0005: STORE r1
        0x08,                   # 0007: RET
    ])

    cfg = build_cfg(program, entry_point=0)
    if cfg is None:
        print("build_cfg() returned None -- implement the TODO sections.")
        return

    print_cfg(cfg)
    print("=== DOT Output ===")
    dot = cfg_to_dot(cfg)
    if dot:
        print(dot)
    else:
        print("cfg_to_dot() returned None -- implement it.")


if __name__ == "__main__":
    main()
