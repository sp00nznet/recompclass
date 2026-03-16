"""
Lab 10 Tests: Recursive Descent Disassembler

Tests with hand-crafted binaries using the simple ISA.
"""

import unittest
from simple_isa import Opcode, assemble, decode_instruction, INSTRUCTION_WIDTH
from recursive_disasm import RecursiveDescentDisassembler, CFG


class TestSimpleISA(unittest.TestCase):
    """Test the simple ISA encoding and decoding."""

    def test_assemble_single_instruction(self):
        binary = assemble([(Opcode.NOP, 0)])
        self.assertEqual(binary, bytes([0x00, 0x00]))

    def test_assemble_multiple_instructions(self):
        binary = assemble([
            (Opcode.LOAD, 42),
            (Opcode.HALT, 0),
        ])
        self.assertEqual(len(binary), 4)
        self.assertEqual(binary[0], Opcode.LOAD)
        self.assertEqual(binary[1], 42)

    def test_decode_instruction(self):
        binary = assemble([(Opcode.ADD, 5)])
        instr = decode_instruction(binary, 0)
        self.assertIsNotNone(instr)
        self.assertEqual(instr.opcode, Opcode.ADD)
        self.assertEqual(instr.operand, 5)
        self.assertEqual(instr.address, 0)
        self.assertEqual(instr.mnemonic, "ADD")

    def test_decode_out_of_bounds(self):
        binary = bytes([0x00])  # Only 1 byte, need 2
        instr = decode_instruction(binary, 0)
        self.assertIsNone(instr)

    def test_branch_target(self):
        binary = assemble([(Opcode.JMP, 0x10)])
        instr = decode_instruction(binary, 0)
        self.assertEqual(instr.branch_target, 0x10)

    def test_non_branch_has_no_target(self):
        binary = assemble([(Opcode.LOAD, 42)])
        instr = decode_instruction(binary, 0)
        self.assertIsNone(instr.branch_target)


class TestLinearProgram(unittest.TestCase):
    """Test disassembly of a simple linear (no branches) program."""

    def test_linear_program_one_block(self):
        """A program with no branches should produce a single basic block."""
        program = assemble([
            (Opcode.LOAD, 1),
            (Opcode.ADD, 2),
            (Opcode.STORE, 0),
            (Opcode.HALT, 0),
        ])
        disasm = RecursiveDescentDisassembler(program)
        cfg = disasm.disassemble(0)

        self.assertEqual(len(cfg.blocks), 1)
        block = cfg.get_block_at(0)
        self.assertIsNotNone(block)
        self.assertEqual(len(block.instructions), 4)
        self.assertEqual(block.successors, [])  # HALT has no successors

    def test_linear_instruction_addresses(self):
        program = assemble([
            (Opcode.LOAD, 1),   # 0x00
            (Opcode.ADD, 2),    # 0x02
            (Opcode.HALT, 0),   # 0x04
        ])
        disasm = RecursiveDescentDisassembler(program)
        cfg = disasm.disassemble(0)

        block = cfg.get_block_at(0)
        addresses = [instr.address for instr in block.instructions]
        self.assertEqual(addresses, [0, 2, 4])


class TestUnconditionalJump(unittest.TestCase):
    """Test disassembly with unconditional jumps."""

    def test_forward_jump(self):
        """JMP forward should create two blocks."""
        program = assemble([
            (Opcode.LOAD, 1),    # 0x00
            (Opcode.JMP, 0x06),  # 0x02: jump to 0x06
            (Opcode.NOP, 0),     # 0x04: skipped (unreachable without other entry)
            (Opcode.HALT, 0),    # 0x06: target
        ])
        disasm = RecursiveDescentDisassembler(program)
        cfg = disasm.disassemble(0)

        # Should have 2 blocks: [0x00] and [0x06]
        self.assertIn(0, cfg.blocks)
        self.assertIn(0x06, cfg.blocks)
        # Block at 0 should jump to 0x06
        self.assertIn(0x06, cfg.blocks[0].successors)

    def test_backward_jump_creates_loop(self):
        """JMP backward should create a loop edge in the CFG."""
        program = assemble([
            (Opcode.LOAD, 1),    # 0x00
            (Opcode.JMP, 0x00),  # 0x02: jump back to start
        ])
        disasm = RecursiveDescentDisassembler(program)
        cfg = disasm.disassemble(0)

        block = cfg.get_block_at(0)
        self.assertIsNotNone(block)
        self.assertIn(0x00, block.successors)


class TestConditionalBranch(unittest.TestCase):
    """Test disassembly with conditional branches."""

    def test_conditional_creates_two_successors(self):
        """JZ should create two successor edges: fall-through and target."""
        program = assemble([
            (Opcode.CMP, 0),     # 0x00
            (Opcode.JZ, 0x08),   # 0x02: if zero, jump to 0x08
            (Opcode.LOAD, 42),   # 0x04: fall-through path
            (Opcode.HALT, 0),    # 0x06
            (Opcode.LOAD, 99),   # 0x08: branch target
            (Opcode.HALT, 0),    # 0x0A
        ])
        disasm = RecursiveDescentDisassembler(program)
        cfg = disasm.disassemble(0)

        block_0 = cfg.get_block_at(0)
        self.assertIsNotNone(block_0)
        # Should have 2 successors: fall-through (0x04) and target (0x08)
        self.assertEqual(len(block_0.successors), 2)
        self.assertIn(0x04, block_0.successors)
        self.assertIn(0x08, block_0.successors)

    def test_diamond_cfg(self):
        """A classic if-then-else diamond pattern."""
        program = assemble([
            (Opcode.CMP, 0),     # 0x00
            (Opcode.JZ, 0x0A),   # 0x02: branch to "else"
            # "then" path:
            (Opcode.LOAD, 1),    # 0x04
            (Opcode.JMP, 0x0C),  # 0x06: skip "else"
            # "else" path:
            (Opcode.LOAD, 2),    # 0x0A (target of JZ -- note gap at 0x08)
            (Opcode.HALT, 0),    # 0x0C: merge point
        ])
        disasm = RecursiveDescentDisassembler(program)
        cfg = disasm.disassemble(0)

        # Should have at least 3 blocks: the entry, the "then" fall-through,
        # and the "else" target / merge
        adj = cfg.get_adjacency_list()
        self.assertIn(0, adj)
        self.assertIn(0x04, adj)
        self.assertIn(0x0A, adj)


class TestLoopProgram(unittest.TestCase):
    """Test disassembly of a loop."""

    def test_counted_loop(self):
        """A loop that counts down to zero."""
        program = assemble([
            (Opcode.LOAD, 10),    # 0x00: initialize
            (Opcode.SUB, 1),      # 0x02: loop body start
            (Opcode.CMP, 0),      # 0x04
            (Opcode.JZ, 0x0C),    # 0x06: exit loop if zero
            (Opcode.JMP, 0x02),   # 0x08: loop back
            (Opcode.NOP, 0),      # 0x0A: unreachable
            (Opcode.HALT, 0),     # 0x0C: loop exit
        ])
        disasm = RecursiveDescentDisassembler(program)
        cfg = disasm.disassemble(0)

        # The loop body block (starting at 0x02) should have a back-edge
        adj = cfg.get_adjacency_list()
        self.assertIn(0x0C, adj)  # Exit block exists
        # Verify the loop back-edge exists somewhere
        has_back_edge = False
        for addr, succs in adj.items():
            if 0x02 in succs and addr >= 0x02:
                has_back_edge = True
        self.assertTrue(has_back_edge, "Expected a back-edge to the loop header")


class TestCFGProperties(unittest.TestCase):
    """Test CFG structural properties."""

    def test_adjacency_list(self):
        program = assemble([
            (Opcode.JMP, 0x04),  # 0x00
            (Opcode.NOP, 0),     # 0x02
            (Opcode.HALT, 0),    # 0x04
        ])
        disasm = RecursiveDescentDisassembler(program)
        cfg = disasm.disassemble(0)
        adj = cfg.get_adjacency_list()
        self.assertIsInstance(adj, dict)
        self.assertIn(0, adj)
        self.assertIn(0x04, adj[0])

    def test_predecessor_map(self):
        program = assemble([
            (Opcode.JMP, 0x04),  # 0x00
            (Opcode.NOP, 0),     # 0x02
            (Opcode.HALT, 0),    # 0x04
        ])
        disasm = RecursiveDescentDisassembler(program)
        cfg = disasm.disassemble(0)
        preds = cfg.get_predecessor_map()
        self.assertIn(0x04, preds)
        self.assertIn(0, preds[0x04])

    def test_entry_point_recorded(self):
        program = assemble([(Opcode.HALT, 0)])
        disasm = RecursiveDescentDisassembler(program)
        cfg = disasm.disassemble(0)
        self.assertEqual(cfg.entry_point, 0)

    def test_empty_binary(self):
        disasm = RecursiveDescentDisassembler(b"")
        cfg = disasm.disassemble(0)
        self.assertEqual(len(cfg.blocks), 0)


if __name__ == "__main__":
    unittest.main()
