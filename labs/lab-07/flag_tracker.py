"""
Lab 7: M/X Flag Tracker for the WDC 65816 Processor

Tracks the M and X flags through a sequence of 65816 instructions to determine
register widths (8-bit vs 16-bit) at each point in the code.

The M flag (bit 5 of the status register) controls accumulator width:
  - M=1 -> 8-bit accumulator
  - M=0 -> 16-bit accumulator

The X flag (bit 4 of the status register) controls index register width:
  - X=1 -> 8-bit index registers (X, Y)
  - X=0 -> 16-bit index registers (X, Y)
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


# ---------------------------------------------------------------------------
# Flag state representation
# ---------------------------------------------------------------------------

class FlagValue(Enum):
    """Represents the known state of a single flag bit."""
    CLEAR = 0       # Flag is known to be 0
    SET = 1         # Flag is known to be 1
    UNKNOWN = 2     # Flag state is not known (e.g., after a merge of divergent paths)


@dataclass
class RegisterState:
    """Tracks the M and X flag states at a given point."""
    m_flag: FlagValue = FlagValue.SET      # Default: 8-bit accumulator (emulation mode)
    x_flag: FlagValue = FlagValue.SET      # Default: 8-bit index registers (emulation mode)

    @property
    def acc_width(self) -> str:
        """Return a human-readable accumulator width."""
        if self.m_flag == FlagValue.SET:
            return "8-bit"
        elif self.m_flag == FlagValue.CLEAR:
            return "16-bit"
        else:
            return "unknown"

    @property
    def index_width(self) -> str:
        """Return a human-readable index register width."""
        if self.x_flag == FlagValue.SET:
            return "8-bit"
        elif self.x_flag == FlagValue.CLEAR:
            return "16-bit"
        else:
            return "unknown"

    def copy(self) -> "RegisterState":
        """Return an independent copy of this state."""
        return RegisterState(m_flag=self.m_flag, x_flag=self.x_flag)

    def __str__(self) -> str:
        return f"ACC={self.acc_width}, IDX={self.index_width}"


# ---------------------------------------------------------------------------
# Instruction representation
# ---------------------------------------------------------------------------

@dataclass
class Instruction:
    """A parsed 65816 instruction."""
    address: int
    mnemonic: str
    operand: Optional[int] = None   # Immediate value for SEP/REP, target for branches
    raw_text: str = ""


# ---------------------------------------------------------------------------
# Instruction parser
# ---------------------------------------------------------------------------

def parse_instructions(text: str) -> List[Instruction]:
    """
    Parse a sequence of 65816 instructions from text.

    Expected format (one instruction per line):
        ADDR: MNEMONIC [#$OPERAND]

    Examples:
        0000: SEP #$30
        0002: LDA #$42
        0004: REP #$20
        0006: LDA #$1234

    Lines starting with ';' are treated as comments and skipped.
    Blank lines are skipped.
    """
    instructions = []
    for line in text.strip().splitlines():
        line = line.strip()
        if not line or line.startswith(";"):
            continue

        # Split address from the rest
        if ":" not in line:
            continue
        addr_str, rest = line.split(":", 1)
        addr = int(addr_str.strip(), 16)
        rest = rest.strip()

        # Split mnemonic and optional operand
        parts = rest.split()
        mnemonic = parts[0].upper()
        operand = None

        if len(parts) > 1:
            op_str = parts[1]
            # Handle #$XX (immediate hex) format
            if op_str.startswith("#$"):
                operand = int(op_str[2:], 16)
            elif op_str.startswith("$"):
                operand = int(op_str[1:], 16)

        instructions.append(Instruction(
            address=addr,
            mnemonic=mnemonic,
            operand=operand,
            raw_text=line,
        ))

    return instructions


# ---------------------------------------------------------------------------
# Flag tracker (linear / single basic block)
# ---------------------------------------------------------------------------

M_BIT = 0x20   # Bit 5 in the status register
X_BIT = 0x10   # Bit 4 in the status register


def apply_sep(state: RegisterState, imm: int) -> RegisterState:
    """
    Apply a SEP (Set Processor Status) instruction.
    SEP sets the bits indicated by the immediate value.
    """
    new_state = state.copy()
    if imm & M_BIT:
        new_state.m_flag = FlagValue.SET
    if imm & X_BIT:
        new_state.x_flag = FlagValue.SET
    return new_state


def apply_rep(state: RegisterState, imm: int) -> RegisterState:
    """
    Apply a REP (Reset Processor Status) instruction.
    REP clears the bits indicated by the immediate value.
    """
    new_state = state.copy()
    if imm & M_BIT:
        new_state.m_flag = FlagValue.CLEAR
    if imm & X_BIT:
        new_state.x_flag = FlagValue.CLEAR
    return new_state


def merge_states(a: RegisterState, b: RegisterState) -> RegisterState:
    """
    Merge two register states at a control flow join point.
    If both paths agree on a flag value, keep it; otherwise mark as UNKNOWN.

    TODO: This is used when two branches converge. Integrate this into the
    branching logic once you implement branch handling.
    """
    merged = RegisterState()

    if a.m_flag == b.m_flag:
        merged.m_flag = a.m_flag
    else:
        merged.m_flag = FlagValue.UNKNOWN

    if a.x_flag == b.x_flag:
        merged.x_flag = a.x_flag
    else:
        merged.x_flag = FlagValue.UNKNOWN

    return merged


def track_flags_linear(instructions: List[Instruction],
                       initial_state: Optional[RegisterState] = None
                       ) -> List[Tuple[Instruction, RegisterState]]:
    """
    Track M/X flag state through a linear sequence of instructions (no branches).

    Returns a list of (instruction, state_before_instruction) pairs.

    Args:
        instructions: List of parsed instructions.
        initial_state: Starting register state. Defaults to 8-bit mode (M=1, X=1).
    """
    if initial_state is None:
        initial_state = RegisterState()  # M=SET, X=SET -> 8-bit mode

    results = []
    current_state = initial_state.copy()

    for instr in instructions:
        # Record the state BEFORE this instruction executes
        results.append((instr, current_state.copy()))

        # Update state based on this instruction
        if instr.mnemonic == "SEP" and instr.operand is not None:
            current_state = apply_sep(current_state, instr.operand)
        elif instr.mnemonic == "REP" and instr.operand is not None:
            current_state = apply_rep(current_state, instr.operand)
        # All other instructions do not change M/X flags in our simplified model.

        # TODO: Handle branch instructions (BRA, BNE, BEQ, etc.)
        #   - When a branch is encountered, you need to track flag state
        #     along both the taken and not-taken paths.
        #   - At the branch target, if it has already been visited with a
        #     different state, merge the states using merge_states().

        # TODO: Handle JSR/RTS and interrupt-related instructions
        #   - PLP (Pull Processor Status) sets flags from the stack -- the
        #     state becomes UNKNOWN unless you can track what was pushed.
        #   - XCE (Exchange Carry and Emulation) can switch modes entirely.

    return results


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------

def display_results(results: List[Tuple[Instruction, RegisterState]]) -> None:
    """Pretty-print the flag tracking results."""
    print(f"{'Address':<10} {'Instruction':<20} {'Accumulator':<14} {'Index Regs':<14}")
    print("-" * 58)
    for instr, state in results:
        # Format the instruction text
        if instr.operand is not None:
            instr_text = f"{instr.mnemonic} #${instr.operand:02X}"
        else:
            instr_text = instr.mnemonic
        print(f"${instr.address:04X}      {instr_text:<20} {state.acc_width:<14} {state.index_width:<14}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

EXAMPLE_PROGRAM = """\
; Example 65816 program showing M/X flag changes
; Starting in 8-bit mode (emulation mode default)
0000: SEP #$30    ; Set M and X -> 8-bit accumulator and index
0002: LDA #$42    ; 8-bit load
0004: REP #$20    ; Clear M -> 16-bit accumulator, index stays 8-bit
0006: LDA #$1234  ; 16-bit load
0009: REP #$10    ; Clear X -> 16-bit index registers
000B: LDX #$ABCD  ; 16-bit index load
000E: SEP #$30    ; Set M and X -> back to 8-bit everything
0010: LDA #$FF    ; 8-bit load
"""

if __name__ == "__main__":
    print("=== Lab 7: M/X Flag Tracker (65816) ===\n")

    instructions = parse_instructions(EXAMPLE_PROGRAM)
    results = track_flags_linear(instructions)
    display_results(results)

    print()
    print("Note: This tracker handles linear code only.")
    print("TODO: Add branch handling and state merging for full CFG support.")
