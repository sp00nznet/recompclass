"""
Lab 9: Dispatch Table Generator

Generates C code implementing three dispatch strategies for handling
indirect jumps in statically recompiled code:
  1. Switch/case dispatch
  2. Binary search dispatch
  3. Hash table dispatch

Each strategy maps original binary addresses to recompiled function pointers.
"""

from typing import List, Tuple


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

# A jump target is a (original_address, recompiled_function_name) pair.
JumpTarget = Tuple[int, str]


# ---------------------------------------------------------------------------
# Strategy 1: Switch/Case Dispatch
# ---------------------------------------------------------------------------

def generate_switch_dispatch(targets: List[JumpTarget]) -> str:
    """
    Generate a C switch/case dispatch function.

    This is the simplest strategy. The compiler may optimize the switch into
    a jump table if the addresses are dense, or a binary search if sparse.

    Args:
        targets: List of (address, function_name) pairs.

    Returns:
        A string containing the C function definition.
    """
    lines = []
    lines.append("/* Strategy 1: Switch/case dispatch */")
    lines.append("#include \"dispatch.h\"")
    lines.append("")

    # Forward declarations for all recompiled functions
    for addr, func_name in targets:
        lines.append(f"void {func_name}(cpu_state_t *ctx);")
    lines.append("")

    lines.append("recomp_func_t dispatch_switch(uint32_t addr) {")
    lines.append("    switch (addr) {")

    for addr, func_name in sorted(targets, key=lambda t: t[0]):
        lines.append(f"    case 0x{addr:08X}:")
        lines.append(f"        return {func_name};")

    lines.append("    default:")
    lines.append("        return (recomp_func_t)0;  /* Not found */")
    lines.append("    }")
    lines.append("}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Strategy 2: Binary Search Dispatch
# ---------------------------------------------------------------------------

def generate_bsearch_dispatch(targets: List[JumpTarget]) -> str:
    """
    Generate a C binary search dispatch function.

    Uses a sorted table of dispatch entries and a manual binary search.
    Guarantees O(log n) lookup time.

    Args:
        targets: List of (address, function_name) pairs.

    Returns:
        A string containing the C function definition.
    """
    sorted_targets = sorted(targets, key=lambda t: t[0])

    lines = []
    lines.append("/* Strategy 2: Binary search dispatch */")
    lines.append("#include \"dispatch.h\"")
    lines.append("")

    # Forward declarations
    for addr, func_name in sorted_targets:
        lines.append(f"void {func_name}(cpu_state_t *ctx);")
    lines.append("")

    # Sorted dispatch table
    lines.append(f"static const dispatch_entry_t dispatch_table[{len(sorted_targets)}] = {{")
    for addr, func_name in sorted_targets:
        lines.append(f"    {{ 0x{addr:08X}, {func_name} }},")
    lines.append("};")
    lines.append("")

    lines.append(f"#define DISPATCH_TABLE_SIZE {len(sorted_targets)}")
    lines.append("")

    # Binary search function
    lines.append("recomp_func_t dispatch_bsearch(uint32_t addr) {")
    lines.append("    int lo = 0;")
    lines.append("    int hi = DISPATCH_TABLE_SIZE - 1;")
    lines.append("")
    lines.append("    while (lo <= hi) {")
    lines.append("        int mid = lo + (hi - lo) / 2;")
    lines.append("        uint32_t mid_addr = dispatch_table[mid].original_addr;")
    lines.append("")
    lines.append("        if (mid_addr == addr) {")
    lines.append("            return dispatch_table[mid].func;")
    lines.append("        } else if (mid_addr < addr) {")
    lines.append("            lo = mid + 1;")
    lines.append("        } else {")
    lines.append("            hi = mid - 1;")
    lines.append("        }")
    lines.append("    }")
    lines.append("")
    lines.append("    return (recomp_func_t)0;  /* Not found */")
    lines.append("}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Strategy 3: Hash Table Dispatch
# ---------------------------------------------------------------------------

def generate_hash_dispatch(targets: List[JumpTarget],
                           table_size_multiplier: int = 2) -> str:
    """
    Generate a C hash table dispatch function.

    Uses open addressing with linear probing. The table size is chosen to be
    at least 2x the number of entries for reasonable load factor.

    Args:
        targets: List of (address, function_name) pairs.
        table_size_multiplier: Multiplier for table size vs entry count.

    Returns:
        A string containing the C function definition.
    """
    # Choose a table size (next power of 2 >= entries * multiplier)
    min_size = len(targets) * table_size_multiplier
    table_size = 1
    while table_size < min_size:
        table_size <<= 1

    # Build the hash table using linear probing
    # Hash function: addr & (table_size - 1)
    hash_table: list = [None] * table_size
    for addr, func_name in targets:
        slot = addr & (table_size - 1)
        while hash_table[slot] is not None:
            slot = (slot + 1) & (table_size - 1)
        hash_table[slot] = (addr, func_name)

    lines = []
    lines.append("/* Strategy 3: Hash table dispatch */")
    lines.append("#include \"dispatch.h\"")
    lines.append("")

    # Forward declarations
    for addr, func_name in targets:
        lines.append(f"void {func_name}(cpu_state_t *ctx);")
    lines.append("")

    lines.append(f"#define HASH_TABLE_SIZE {table_size}")
    lines.append(f"#define HASH_MASK       0x{table_size - 1:08X}")
    lines.append("")

    # Emit the pre-built hash table
    lines.append(f"static const dispatch_entry_t hash_table[HASH_TABLE_SIZE] = {{")
    for i, entry in enumerate(hash_table):
        if entry is not None:
            addr, func_name = entry
            lines.append(f"    /* [{i:3d}] */ {{ 0x{addr:08X}, {func_name} }},")
        else:
            lines.append(f"    /* [{i:3d}] */ {{ 0x00000000, (recomp_func_t)0 }},")
    lines.append("};")
    lines.append("")

    # Lookup function with linear probing
    lines.append("recomp_func_t dispatch_hash(uint32_t addr) {")
    lines.append("    uint32_t slot = addr & HASH_MASK;")
    lines.append("    uint32_t start = slot;")
    lines.append("")
    lines.append("    do {")
    lines.append("        if (hash_table[slot].func == (recomp_func_t)0) {")
    lines.append("            return (recomp_func_t)0;  /* Empty slot, not found */")
    lines.append("        }")
    lines.append("        if (hash_table[slot].original_addr == addr) {")
    lines.append("            return hash_table[slot].func;")
    lines.append("        }")
    lines.append("        slot = (slot + 1) & HASH_MASK;")
    lines.append("    } while (slot != start);")
    lines.append("")
    lines.append("    return (recomp_func_t)0;  /* Table full, not found */")
    lines.append("}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Convenience: generate all three strategies
# ---------------------------------------------------------------------------

def generate_all_dispatchers(targets: List[JumpTarget]) -> dict:
    """
    Generate all three dispatch strategies.

    Returns:
        A dict mapping strategy name to generated C code.
    """
    return {
        "switch": generate_switch_dispatch(targets),
        "bsearch": generate_bsearch_dispatch(targets),
        "hash": generate_hash_dispatch(targets),
    }


# TODO: Add a performance comparison generator that emits a C main() function
#       benchmarking all three strategies with a set of lookup addresses.

# TODO: Add a fallback-to-interpreter option for each strategy. When a target
#       address is not found, instead of returning NULL, call an interpreter
#       function that can execute the original instructions.


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== Lab 9: Dispatch Table Generator ===\n")

    # Example: known indirect jump targets from a hypothetical recompiled binary
    example_targets: List[JumpTarget] = [
        (0x00401000, "func_00401000"),
        (0x00401050, "func_00401050"),
        (0x004010A0, "func_004010A0"),
        (0x00401100, "func_00401100"),
        (0x00401200, "func_00401200"),
        (0x00401300, "func_00401300"),
        (0x00401400, "func_00401400"),
        (0x00402000, "func_00402000"),
    ]

    dispatchers = generate_all_dispatchers(example_targets)

    for strategy_name, code in dispatchers.items():
        print(f"--- {strategy_name.upper()} strategy ---")
        print(code)
        print()
