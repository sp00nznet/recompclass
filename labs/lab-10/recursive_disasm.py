"""
Lab 10: Recursive Descent Disassembler

Implements recursive descent disassembly for the simple ISA defined in
simple_isa.py. Builds basic blocks and constructs a control flow graph (CFG).

Algorithm:
  1. Start with entry point(s) on a worklist.
  2. Pop an address from the worklist.
  3. Decode instructions sequentially, adding them to the current basic block.
  4. When a terminator is reached (branch, jump, halt):
     - End the current basic block.
     - Add successor addresses to the worklist (if not already visited).
     - Record CFG edges.
  5. Repeat until the worklist is empty.
"""

from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from simple_isa import (
    DecodedInstruction,
    decode_instruction,
    is_terminator,
    is_unconditional_jump,
    is_conditional_branch,
    is_halt,
    INSTRUCTION_WIDTH,
)


# ---------------------------------------------------------------------------
# Basic Block
# ---------------------------------------------------------------------------

@dataclass
class BasicBlock:
    """
    A basic block: a maximal sequence of instructions with
    exactly one entry point (the first instruction) and one exit point
    (the last instruction, which is a terminator).
    """
    start_address: int
    instructions: List[DecodedInstruction] = field(default_factory=list)
    successors: List[int] = field(default_factory=list)  # Addresses of successor blocks

    @property
    def end_address(self) -> int:
        """Address just past the last instruction in this block."""
        if not self.instructions:
            return self.start_address
        last = self.instructions[-1]
        return last.address + last.size

    @property
    def last_instruction(self) -> Optional[DecodedInstruction]:
        if self.instructions:
            return self.instructions[-1]
        return None

    def __str__(self) -> str:
        lines = [f"Block 0x{self.start_address:04X}:"]
        for instr in self.instructions:
            lines.append(f"    {instr}")
        if self.successors:
            succ_text = ", ".join(f"0x{s:04X}" for s in self.successors)
            lines.append(f"  -> successors: {succ_text}")
        else:
            lines.append("  -> (no successors)")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Control Flow Graph
# ---------------------------------------------------------------------------

@dataclass
class CFG:
    """
    A control flow graph represented as:
      - A dict of basic blocks keyed by start address
      - An adjacency list (edges as successor lists on each block)
    """
    blocks: Dict[int, BasicBlock] = field(default_factory=OrderedDict)
    entry_point: int = 0

    def add_block(self, block: BasicBlock) -> None:
        """Add a basic block to the CFG."""
        self.blocks[block.start_address] = block

    def get_block_at(self, address: int) -> Optional[BasicBlock]:
        """Get the block starting at the given address."""
        return self.blocks.get(address)

    def get_adjacency_list(self) -> Dict[int, List[int]]:
        """Return the CFG as a simple adjacency list (address -> [successor addresses])."""
        adj = {}
        for addr, block in self.blocks.items():
            adj[addr] = list(block.successors)
        return adj

    def get_predecessor_map(self) -> Dict[int, List[int]]:
        """Return a map from block address to list of predecessor block addresses."""
        preds: Dict[int, List[int]] = {addr: [] for addr in self.blocks}
        for addr, block in self.blocks.items():
            for succ in block.successors:
                if succ in preds:
                    preds[succ].append(addr)
        return preds

    def __str__(self) -> str:
        lines = [f"=== CFG (entry: 0x{self.entry_point:04X}, {len(self.blocks)} blocks) ==="]
        for block in self.blocks.values():
            lines.append(str(block))
            lines.append("")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Recursive Descent Disassembler
# ---------------------------------------------------------------------------

class RecursiveDescentDisassembler:
    """
    Recursive descent disassembler for the simple ISA.

    Builds a CFG by following control flow from a set of entry points.
    """

    def __init__(self, data: bytes):
        self.data = data
        self.cfg = CFG()
        self._visited: Set[int] = set()         # Addresses we have already decoded
        self._block_starts: Set[int] = set()     # Known block start addresses

    def disassemble(self, entry_point: int = 0) -> CFG:
        """
        Perform recursive descent disassembly starting from the entry point.

        Args:
            entry_point: Starting address (byte offset) in the binary.

        Returns:
            The constructed CFG.
        """
        self.cfg = CFG(entry_point=entry_point)
        self._visited.clear()
        self._block_starts.clear()

        # Worklist algorithm: addresses to explore
        worklist: List[int] = [entry_point]
        self._block_starts.add(entry_point)

        while worklist:
            address = worklist.pop()

            # Skip if we have already built a block starting at this address
            if address in self.cfg.blocks:
                continue

            # Build a basic block starting at this address
            block = self._build_basic_block(address)
            if block is None:
                continue

            self.cfg.add_block(block)

            # Add successor addresses to the worklist
            for succ_addr in block.successors:
                if succ_addr not in self.cfg.blocks:
                    self._block_starts.add(succ_addr)
                    worklist.append(succ_addr)

        # After building all blocks, we may need to split blocks where a branch
        # target lands in the middle of an existing block.
        self._split_blocks_at_targets()

        return self.cfg

    def _build_basic_block(self, start_address: int) -> Optional[BasicBlock]:
        """
        Decode instructions starting at start_address until a terminator is found.

        Returns a BasicBlock, or None if the address is out of bounds.
        """
        block = BasicBlock(start_address=start_address)
        address = start_address

        while True:
            # Bounds check
            if address >= len(self.data):
                break

            # If we have already visited this address AND it is not the start
            # of our current block, then we are running into another block.
            if address != start_address and address in self._block_starts:
                # This address is the start of a different block.
                # End the current block and add a fall-through edge.
                block.successors.append(address)
                break

            # Decode the instruction
            instr = decode_instruction(self.data, address)
            if instr is None:
                break

            self._visited.add(address)
            block.instructions.append(instr)

            # Check if this instruction is a terminator
            if is_terminator(instr.opcode):
                if is_unconditional_jump(instr.opcode):
                    # Unconditional jump: one successor (the target)
                    target = instr.branch_target
                    if target is not None and target < len(self.data):
                        block.successors.append(target)

                elif is_conditional_branch(instr.opcode):
                    # Conditional branch: two successors
                    # 1) Fall-through (next sequential instruction)
                    fall_through = instr.next_address
                    if fall_through < len(self.data):
                        block.successors.append(fall_through)
                    # 2) Branch target
                    target = instr.branch_target
                    if target is not None and target < len(self.data):
                        block.successors.append(target)

                elif is_halt(instr.opcode):
                    # HALT: no successors
                    pass

                break  # Terminator ends the basic block

            # Move to the next instruction
            address += INSTRUCTION_WIDTH

        return block if block.instructions else None

    def _split_blocks_at_targets(self) -> None:
        """
        Split basic blocks where a branch target lands in the middle of
        an existing block. This ensures every branch target is the start
        of its own basic block.

        TODO: Implement block splitting.
              For each block in the CFG:
                - Check if any known branch target falls within the block
                  (between start_address exclusive and end_address exclusive).
                - If so, split the block at that address:
                  1. The first half keeps instructions before the split point.
                  2. The second half starts at the split point.
                  3. The first half's successors become [split_address].
                  4. The second half inherits the original successors.
                - Update the CFG accordingly.
        """
        # This is left as an exercise. For the simple ISA with fixed-width
        # instructions, this situation arises when a branch targets an
        # instruction that is not the first in an already-built block.
        pass

    def detect_unreachable_code(self) -> List[Tuple[int, int]]:
        """
        Detect regions of the binary that were not visited during disassembly.

        TODO: Implement this method.
              - Walk through the binary in INSTRUCTION_WIDTH steps.
              - Identify contiguous ranges of addresses not in self._visited.
              - Return a list of (start_address, length) tuples for each
                unreachable region.
        """
        raise NotImplementedError("Unreachable code detection not yet implemented")


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------

def print_cfg_adjacency(cfg: CFG) -> None:
    """Print the CFG as an adjacency list."""
    adj = cfg.get_adjacency_list()
    print("CFG Adjacency List:")
    for addr in sorted(adj.keys()):
        successors = adj[addr]
        if successors:
            succ_text = ", ".join(f"0x{s:04X}" for s in successors)
        else:
            succ_text = "(terminal)"
        print(f"  0x{addr:04X} -> {succ_text}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from simple_isa import Opcode, assemble

    print("=== Lab 10: Recursive Descent Disassembler ===\n")

    # Build a small example program:
    #
    #   0x00: LOAD 10       ; acc = 10
    #   0x02: SUB 1         ; acc = acc - 1
    #   0x04: CMP 0         ; compare acc with 0
    #   0x06: JZ 0x0C       ; if zero, jump to HALT at 0x0C
    #   0x08: JMP 0x02      ; otherwise loop back to SUB
    #   0x0A: NOP 0         ; unreachable (data or dead code)
    #   0x0C: HALT 0        ; program end
    #
    program = assemble([
        (Opcode.LOAD, 10),      # 0x00
        (Opcode.SUB, 1),        # 0x02
        (Opcode.CMP, 0),        # 0x04
        (Opcode.JZ, 0x0C),      # 0x06
        (Opcode.JMP, 0x02),     # 0x08
        (Opcode.NOP, 0),        # 0x0A (unreachable)
        (Opcode.HALT, 0),       # 0x0C
    ])

    print(f"Program binary ({len(program)} bytes): {program.hex()}\n")

    disasm = RecursiveDescentDisassembler(program)
    cfg = disasm.disassemble(entry_point=0)

    print(cfg)
    print_cfg_adjacency(cfg)
