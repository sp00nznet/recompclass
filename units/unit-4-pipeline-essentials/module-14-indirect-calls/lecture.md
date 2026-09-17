# Module 14: The Indirect Call Problem

This module addresses the single most difficult problem in static recompilation. Every architecture has it. Every project must solve it. If you have followed this course through Modules 4, 5, and 6, you have already encountered it in passing -- `JP HL` on the Game Boy, computed branches on the 65816, indirect calls in x86. Now we confront it directly.

The indirect call problem is this: static recompilation translates code ahead of time, generating a C function for each known code address. But when a program computes a jump or call target at runtime, the recompiler does not know which C function to invoke. The target is a number in a register, and that number could be anything. If the recompiler guesses wrong or fails to handle the case, the program crashes. If it handles every case conservatively, performance suffers.

There is no perfect solution. There are only tradeoffs. This module presents the full landscape of solutions, from compile-time static analysis to runtime dispatch tables to interpreter fallback, and introduces the three-tier architecture that production recompilers use to balance correctness and performance.

---

## 1. The Fundamental Problem

In a statically recompiled program, every known code address maps to a C function or a label within a function. A direct call like `CALL 0x4000` becomes `func_0x4000(ctx);` in the generated code. The target is known at compile time, the function exists, and the C compiler resolves it normally.

An indirect call or jump computes its target at runtime. The target is stored in a register, loaded from memory, or calculated from an expression. At compile time, the recompiler sees an instruction like:

- **Game Boy**: `JP HL` -- jump to the address in the HL register
- **SNES**: `JMP (addr)` -- jump to the address stored at memory location `addr`
- **x86**: `CALL [BX+SI]` -- call the address stored at the memory location computed from BX+SI
- **MIPS**: `JR $t0` -- jump to the address in register $t0
- **PowerPC**: `BCTR` -- branch to the address in the Count Register

In every case, the recompiler must emit code that somehow resolves the runtime value to the correct C function. The problem is that there are potentially thousands of valid targets, and the recompiler may not know all of them.

```mermaid
flowchart LR
    subgraph "Direct Call (Easy)"
        A1["CALL 0x4000"] --> B1["func_0x4000(ctx);"]
    end

    subgraph "Indirect Call (Hard)"
        A2["CALL [BX+SI]"] --> B2["target = mem_read(BX+SI)\n??? which function ???"]
        B2 --> C2["func_0x1000?"]
        B2 --> D2["func_0x2000?"]
        B2 --> E2["func_0x3000?"]
        B2 --> F2["func_0x????"]
    end

    style A1 fill:#2f855a,stroke:#38a169,color:#fff
    style B1 fill:#2f855a,stroke:#38a169,color:#fff
    style A2 fill:#9b2c2c,stroke:#c53030,color:#fff
    style B2 fill:#9b2c2c,stroke:#c53030,color:#fff
    style C2 fill:#975a16,stroke:#b7791f,color:#fff
    style D2 fill:#975a16,stroke:#b7791f,color:#fff
    style E2 fill:#975a16,stroke:#b7791f,color:#fff
    style F2 fill:#975a16,stroke:#b7791f,color:#fff
```

---

## 2. Why This Is Hard

The difficulty of indirect calls stems from a fundamental mismatch between the original machine and the recompiled representation.

**The original machine has a flat code space.** Every address is a valid jump target. The program counter is just a number, and the hardware does not care how it got that value -- it fetches and executes whatever bytes are at that address. If a register contains `0x4000`, the CPU jumps to `0x4000` and starts executing.

**The recompiled program has discrete functions.** Each known code address is a separate C function. There is no flat code space -- there is a collection of named functions. To call one, you need to know its name (or have a function pointer to it). A raw integer `0x4000` means nothing to the C compiler.

This gap creates several specific problems:

**Missing targets.** If the recompiler does not know that address `0x5000` is a valid code entry point, it will not generate `func_0x5000`. If the program then tries to call `0x5000` at runtime, there is nothing to call. This is a crash.

**Combinatorial explosion.** An indirect call could theoretically target any address in the code space. On a system with 64KB of code, that is up to 65,536 possible targets. Most of these are not actually valid function entries, but the recompiler cannot easily prove which ones are and which are not.

**Performance cost of runtime resolution.** Even if all targets are known, resolving an indirect call at runtime requires a lookup -- a switch/case, a hash table, or a binary search. This adds overhead to what would otherwise be a single instruction. If indirect calls are frequent (as in C++ programs with virtual methods), this overhead is significant.

**Data-dependent targets.** Some indirect call targets depend on user input, file contents, or other runtime data. No amount of static analysis can predict these values. The recompiler must have a fallback for truly unpredictable targets.

---

## 3. Solution 1: Static Analysis

The first line of defense is compile-time analysis. Before generating any runtime dispatch code, try to determine the possible targets of each indirect call through analysis of the program's data flow and structure.

### Data Flow Analysis

Track the value of the register or memory location used in the indirect call backward through the control flow graph. If the value is loaded from a known address, and that address contains a constant, the target is resolved.

Example (Game Boy):

```asm
    LD HL, jump_table    ; HL = address of jump table
    LD A, [some_var]     ; A = index (0, 1, 2, ...)
    ADD A, A             ; A = index * 2 (each entry is 2 bytes)
    ADD A, L
    LD L, A              ; HL now points to jump_table + index * 2
    LD A, [HL+]          ; Low byte of target
    LD H, [HL]           ; High byte of target
    LD L, A
    JP HL                ; Jump to target
```

By analyzing this sequence, the recompiler can determine that `JP HL` targets an entry in `jump_table`. If the jump table is in ROM (constant data), all possible targets are known. The recompiler reads the jump table, extracts every target address, and either resolves the indirect jump to a switch/case over the known targets or, if possible, to a computed goto.

### Switch Table Pattern Recognition

Jump tables (switch/case implementations) are the most common source of indirect jumps. They follow recognizable patterns on every architecture:

1. Load an index value
2. Bounds-check the index (optional but common)
3. Use the index to look up an address from a table in memory
4. Jump to that address

The recompiler can recognize these patterns through structural analysis of the code surrounding the indirect jump. Once the table is identified, all entries are known targets.

### Vtable Reconstruction

In C++ programs (common on Xbox and Xbox 360), indirect calls often go through virtual method tables (vtables). The pattern is:

1. Load the object pointer
2. Load the vtable pointer from the first field of the object
3. Load the method pointer from a fixed offset in the vtable
4. Call the method

If the recompiler can identify all vtables in the binary (usually by finding the constructors that initialize them), it can determine all possible targets for each vtable slot.

### Limits of Static Analysis

Static analysis works well for deterministic patterns -- jump tables with constant entries, vtables initialized by known constructors, function pointer arrays in read-only data. It fails for:

- **Runtime-computed addresses**: When the target depends on user input or external data.
- **Obfuscated code**: When the jump table is encrypted, compressed, or constructed at runtime.
- **Highly dynamic dispatch**: When the program uses a general-purpose dispatch mechanism that can call any function.

Static analysis is always the preferred solution when it works, because it has zero runtime cost -- the indirect call is resolved at compile time and becomes a direct call (or a small switch over known targets).

---

## 4. Solution 2: Dispatch Tables

When static analysis narrows the targets but cannot resolve a single one, or when the set of possible targets is known but the specific target varies at runtime, a **dispatch table** bridges the gap.

The idea: collect all known function addresses, generate a lookup mechanism, and emit code that maps the runtime address value to the correct C function.

### Implementation

The recompiler generates a dispatch function that takes an address and calls the corresponding recompiled function:

```c
void dispatch_call(CPUContext *ctx, uint32_t target_addr) {
    switch (target_addr) {
        case 0x0150: func_0x0150(ctx); break;
        case 0x0800: func_0x0800(ctx); break;
        case 0x1A00: func_0x1A00(ctx); break;
        case 0x1B00: func_0x1B00(ctx); break;
        case 0x2000: func_0x2000(ctx); break;
        case 0x4000: func_0x4000(ctx); break;
        // ... every known function entry point
        default:
            fprintf(stderr, "Unknown call target: 0x%04X\n", target_addr);
            abort();
    }
}
```

Every indirect call in the generated code becomes:

```c
// Original: CALL [BX+SI]
uint16_t target = mem_read_16((ctx->ds << 4) + ctx->bx + ctx->si);
dispatch_call(ctx, target);
```

### Optimization: Binary Search or Hash Table

For programs with thousands of known function entries, a linear switch/case is not ideal. The C compiler will often optimize small switch statements into jump tables, but for very large ones, an explicit binary search or hash table may be faster:

```c
// Binary search dispatch (sorted by address)
typedef struct { uint32_t addr; void (*func)(CPUContext*); } DispatchEntry;

static const DispatchEntry dispatch_table[] = {
    { 0x0150, func_0x0150 },
    { 0x0800, func_0x0800 },
    { 0x1A00, func_0x1A00 },
    // ... sorted by address
};

void dispatch_call(CPUContext *ctx, uint32_t target) {
    int lo = 0, hi = DISPATCH_TABLE_SIZE - 1;
    while (lo <= hi) {
        int mid = (lo + hi) / 2;
        if (dispatch_table[mid].addr == target) {
            dispatch_table[mid].func(ctx);
            return;
        } else if (dispatch_table[mid].addr < target) {
            lo = mid + 1;
        } else {
            hi = mid - 1;
        }
    }
    // Target not found -- fall through to interpreter
    interpreter_fallback(ctx, target);
}
```

### Populating the Dispatch Table

The dispatch table must contain every address that could be a valid indirect call target. Sources include:

- Every function entry point found by the disassembler
- Every target found in jump tables and switch tables
- Every address stored in vtables
- Every address stored in function pointer arrays in the data sections
- Addresses provided by manual annotation

Missing an entry means a potential crash at runtime. Including too many entries wastes a small amount of memory but is otherwise harmless. It is better to over-include than under-include.

---

## 5. Solution 3: Interpreter Fallback

For truly unknown targets -- addresses that no static analysis can predict and that are not in the dispatch table -- the last resort is an interpreter. The recompiled program includes a simple interpreter for the original architecture that can execute instructions one at a time starting from any address.

When the dispatch table fails to find a target, it invokes the interpreter:

```c
void interpreter_fallback(CPUContext *ctx, uint32_t start_addr) {
    ctx->pc = start_addr;
    while (1) {
        // Check if we have returned to a known address
        if (is_known_function(ctx->pc)) {
            dispatch_call(ctx, ctx->pc);
            return;
        }
        // Interpret one instruction
        interpret_single(ctx);
    }
}
```

The interpreter runs until the program counter reaches a known address (one that has a corresponding recompiled function), at which point control returns to the recompiled code. This hybrid approach guarantees correctness: if the recompiled code cannot handle a target, the interpreter can, and it hands control back to the recompiled code as soon as possible.

The performance cost is significant -- interpreted execution is 10-100x slower than recompiled code. But if the fallback is rarely triggered, the overall impact is negligible. The key insight is that most programs spend the vast majority of their time in a small number of hot loops and functions, all of which are statically resolved. The interpreter handles the rare edge cases.

---

## 6. The Three-Tier Dispatch Architecture

Production recompilers combine all three solutions into a layered architecture:

```mermaid
flowchart TD
    CALL["Indirect Call\n(runtime target address)"] --> T1{"Tier 1:\nStatically Resolved?"}
    T1 -->|Yes| DIRECT["Direct Call\n(zero overhead)"]
    T1 -->|No| T2{"Tier 2:\nIn Dispatch Table?"}
    T2 -->|Yes| DISPATCH["Dispatch Table Call\n(small overhead:\nswitch/binary search)"]
    T2 -->|No| T3["Tier 3:\nInterpreter Fallback\n(high overhead,\nguarantees correctness)"]

    T3 --> RETURN{"Interpreter reaches\nknown address?"}
    RETURN -->|Yes| REENTER["Re-enter Recompiled Code"]

    style CALL fill:#2d3748,stroke:#4a5568,color:#fff
    style T1 fill:#2f855a,stroke:#38a169,color:#fff
    style DIRECT fill:#2f855a,stroke:#38a169,color:#fff
    style T2 fill:#975a16,stroke:#b7791f,color:#fff
    style DISPATCH fill:#975a16,stroke:#b7791f,color:#fff
    style T3 fill:#9b2c2c,stroke:#c53030,color:#fff
    style RETURN fill:#2b6cb0,stroke:#3182ce,color:#fff
    style REENTER fill:#2f855a,stroke:#38a169,color:#fff
```

**Tier 1: Static Resolution** is applied at compile time. If the recompiler can determine the target through data flow analysis, pattern recognition, or annotation, it emits a direct call. This is the best case -- zero runtime overhead, the indirect call becomes indistinguishable from a direct call in the generated code.

**Tier 2: Dispatch Table** handles calls where the target is one of several known possibilities but the specific choice is determined at runtime. The dispatch table lookup adds a small overhead (a switch/case or binary search), but it is predictable and fast. Most indirect calls that escape Tier 1 are caught by Tier 2.

**Tier 3: Interpreter Fallback** is the safety net. It handles any target that the recompiler did not anticipate. It is slow but correct. In a well-analyzed program, Tier 3 should be triggered rarely or never. When it is triggered during testing, it is a signal that the recompiler's analysis should be improved -- the target should be added to the dispatch table or resolved statically.

### The Development Workflow

In practice, the three-tier architecture drives an iterative development workflow:

1. **Initial recompilation**: Many indirect calls fall to Tier 3. The interpreter logs every unknown target it encounters.
2. **Analysis pass**: Review the logged targets. Determine which ones are reachable through static analysis (add to Tier 1), which are valid function entries (add to Tier 2), and which are bugs in the recompiler's analysis.
3. **Iterate**: Re-run the recompilation with improved analysis. Fewer calls reach Tier 3.
4. **Release quality**: All calls are handled by Tier 1 or Tier 2 in normal execution. Tier 3 remains as a safety net for edge cases.

This workflow transforms the indirect call problem from a blocking issue ("the recompiler crashes on unknown targets") into a quality metric ("what percentage of indirect calls are statically resolved?"). A mature recompilation project typically achieves 95-100% static resolution.

---

## 7. Architecture-Specific Challenges

The indirect call problem manifests differently on each architecture, because each architecture has different mechanisms for computed control flow.

| Architecture | Indirect Mechanisms | Typical Count | Difficulty |
|---|---|---|---|
| **Game Boy (SM83)** | JP HL | Very few (1-10 per game) | Low |
| **SNES (65816)** | JMP (addr), JML [addr], JSR (addr,X) | Few to moderate (10-50) | Low-Medium |
| **DOS (x86-16)** | CALL [mem], JMP [mem], INT with modified IVT | Moderate (20-100) | Medium |
| **N64 (MIPS)** | JR $reg, JALR $reg | Moderate (50-200) | Medium |
| **Xbox (x86-32)** | CALL [EAX+offset] (vtables), JMP [table+reg*4] | Many (500-5000) | High |
| **Xbox 360 (PPC)** | BCTR, BCTRL | Many (500-5000) | High |
| **PS3 (Cell PPU)** | BCTR, BCTRL, plus SPU indirect branches | Very many (1000-10000) | Very High |

### Game Boy: JP HL

On the Game Boy, `JP HL` is the only indirect jump mechanism. It appears rarely -- typically in jump table dispatchers (which are easy to analyze) and occasionally in callback systems. Most Game Boy games have fewer than 10 indirect jumps total, and most of those can be fully resolved through data flow analysis of the jump table.

The low count and simple patterns make the Game Boy an ideal first target for practicing indirect call resolution. If you can resolve all `JP HL` instances in a Game Boy game, you have the skills to tackle the harder cases.

### Xbox: Vtables in C++ Code

Xbox games are compiled from C++, which means extensive use of virtual method calls. A single `CALL [EAX+0x1C]` instruction might dispatch to any class that inherits from a given base class. A game with 200 classes might have 50 vtable slots each, producing thousands of potential indirect call targets.

The saving grace is that vtables are structured. Each vtable is a constant array of function pointers stored in the read-only data section. The recompiler can:

1. Find all vtables by scanning for arrays of valid code pointers in the data sections.
2. Determine which vtable slot each indirect call accesses (from the offset in `CALL [EAX+offset]`).
3. Collect all functions that appear at that slot across all vtables.
4. Generate a dispatch table containing only the valid targets for that specific slot.

This per-slot approach dramatically reduces the dispatch table size and can sometimes reduce it to a single target (when only one class implements a given virtual method), enabling full static resolution.

### Xbox 360: CTR-Based Branches

The PowerPC architecture used in the Xbox 360 (Xenon) uses the Count Register (CTR) for indirect branches. The `BCTR` instruction branches to the address in CTR, and `BCTRL` calls the address in CTR.

The CTR is loaded by `MTCTR` (Move To Count Register), which copies a general-purpose register into CTR. The recompiler must trace the value in that general-purpose register backward to determine the target. This often leads through load instructions from function pointer tables, vtables, or computed addresses.

Additionally, Xbox 360 games make heavy use of VMX128 (the SIMD extension) and frequently use function pointers for optimized inner loops, increasing the count of indirect calls compared to scalar code.

---

## 8. Real-World Reference

The three tiers above are a teaching model. Here is what they actually look like in
shipped code, with the files to go read.

### xboxrecomp -- `RECOMP_ICALL`, and where the tiers really land

Every indirect call in xboxrecomp's generated code goes through one macro. Read
[`docs/technical/indirect-calls.md`](https://github.com/sp00nznet/xboxrecomp/blob/main/docs/technical/indirect-calls.md)
before you read anything else in this section.

Note that the shipped tiers are *not* the ones this module described:

| | This module | xboxrecomp |
|---|---|---|
| Tier 1 | static analysis (jump tables, vtables) | manual overrides (~30 hand-written replacements) |
| Tier 2 | dispatch table | dispatch table (22,097 entries, binary search) |
| Tier 3 | interpreter fallback | kernel bridge (thunks at `0xFE000000+`) |
| Miss | -- | pop the dummy return address, return 0, keep going |

There is no interpreter tier. A miss is not fatal and it is not emulated -- it
returns zero and the game keeps running. That is a deliberate choice, and it costs
something: see **the stack leak problem** in that doc. A failed `stdcall` dispatch
leaves the pushed arguments and the dummy return address on the guest stack, so
every miss leaks at least 4 bytes. At 60 FPS that is unbounded growth, which is why
`RECOMP_ICALL_SAFE` exists and takes a saved `esp`.

The static-analysis work this module calls Tier 1 still happens, but it happens
*offline*, in tools, and it does not feed the dispatch path -- it feeds the list of
addresses the recompiler agrees to lift at all. Those are different jobs, and this
module blurred them.

### The garbage pointer problem (this module did not warn you about it)

Corrupted vtable pointers, not unknown-but-valid targets, are the number one source
of dispatch failures in practice. When a constructor gets stubbed, the object's
vtable pointer is whatever happened to be in that memory. xboxrecomp handles this
with a single range check ahead of all three tiers: valid code lives in
`[0x00011000, 0x003B0000)`, kernel thunks at `0xFE000000+`, and anything in between
is garbage and is skipped.

That one check took Burnout 3 from 180 failed indirect calls per 2-second window
down to 121. It is four lines.

### tirecomp -- the whole thing in 65 lines

If the Xbox version is too much at once, read
[`tirecomp/src/recomp_rt.c`](https://github.com/sp00nznet/tirecomp/blob/main/src/recomp_rt.c).
The Z80 address space is 64KB, so the dispatch table is not a binary search -- it is
just an array:

```c
static ti_func_t g_dispatch[0x10000];                            /* line 7  */
void ti_register_func(uint16_t addr, ti_func_t fn) { g_dispatch[addr] = fn; }
ti_func_t ti_lookup_func(uint16_t addr)            { return g_dispatch[addr]; }
```

One pointer per possible address, 512KB of table, O(1) lookup, no analysis required.
Whether you can afford that is a question about your address space, not about your
recompiler.

tirecomp also shows the *other* shape of dispatch. Instead of recompiled functions
calling each other in nested C frames, every block runs to a control-transfer
boundary, writes `ti_cpu.pc`, and returns to a driver loop that dispatches the next
one (`ti_run`, same file). That makes `JP (HL)` completely uninteresting -- it is a
store to `pc` -- at the cost of a table lookup on every transfer, including the ones
a nested design would have compiled into a direct call. The interpreter fallback is
a function pointer, `ti_dispatch_fallback`, installed by
[`tools/z80recomp/interp.c`](https://github.com/sp00nznet/tirecomp/blob/main/tools/z80recomp/interp.c).

### The over-hinting trap -- more static analysis made it worse

This module told you static analysis is your first line of defense. The
[Civilization Revolution](https://github.com/sp00nznet/civrev) bring-up is a
counterexample worth sitting with.

The 360 build hit a wall of static-init thunks around `0x82E80xxx` that function
discovery had not placed, so every one of them was an unresolved indirect target.
Two ways forward:

**The static way.** Run a vtable pointer scanner over the read-only data, take
everything that looks like a code pointer, feed it back as function-entry hints. It
produced **301** candidates.

**What actually happened.** Feeding in all 301 made the build *worse*. The scanner
could not tell a vtable slot from a switch/jump-table entry, and jump-table entries
point into the *middle* of functions. Hinting those split real functions in half and
turned a loop back-edge into a fatal unresolved call -- a class of bug that did not
exist before the analysis ran.

**The runtime way.** Boot the game once with a tolerant dispatch scaffold that logs
every unregistered indirect-call target instead of dying on it. One boot produced the
complete set: **21** addresses, every one of them a guaranteed-real entry point
because the guest actually branched there.

Final hint count: 3 codegen-required plus the 21 runtime-verified, **24 total**,
down from 301. The entire bug class vanished on deletion.

The lesson is not that static analysis is useless. It is that a pointer-shaped
integer in read-only data is a *guess*, and a logged branch target is an
*observation*, and if you can afford one boot you should prefer the observation. The
tolerant-dispatch tier you build for Tier 3 is also your best target-discovery
instrument -- most treatments of this problem, including section 6 above, present it
only as a failure handler.

### What a real bring-up looks like by the numbers

Two more from the same family, for scale:

| | [You Don't Know Jack](https://github.com/sp00nznet/ydkj) (360) | [Civilization Revolution](https://github.com/sp00nznet/civrev) (360) |
|---|---|---|
| Guest image | 5 MB | 16.8 MB |
| Recompiled functions | 14,781 | 40,067 |
| Generated C++ | -- | 231 MB |
| Output executable | 21 MB | 80 MB |
| Hand-written kernel stubs | 0 | 1 bundle (`XUsbcam*`) |
| Codegen hints needed | 1 | 24 |
| Where it got to | renders its title screen | clean boot into engine init, no render |

Note the hint counts against the function counts. 14,781 functions needed **one**
hint. Indirect calls are the hardest problem in the field and they are also, on a
well-behaved binary, a rounding error. The hard part is never the average case.

Note also the honesty in that last row. Neither of these is "done," and both repos
say so in their own READMEs under a heading called **Honest scope**. When you write
up your own project, do that.

### Read these next

- xboxrecomp `docs/technical/` -- 19 files, including `rtti-recovery.md` and `register-model.md`
- xboxrecomp `docs/pipeline/03-function-id.md` -- where the target set comes from in the first place
## Lab

The following lab accompanies this module:

- **Lab 9** -- Indirect call resolution: Implement jump table recognition, dispatch table generation, and interpreter fallback for multiple architectures. Test against programs with known indirect call patterns and verify correct resolution at each tier.

---

**Next: [Module 15 -- Hardware Shims and SDL2 Integration](../module-15-hardware-shims/lecture.md)**
