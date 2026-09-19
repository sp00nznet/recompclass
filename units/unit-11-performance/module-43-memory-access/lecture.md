# Module 43: Memory Access Optimization

Every guest load and store in your program goes through your memory layer. On a
sufficiently large workload that is hundreds of millions of calls per second, and it is
the single most reliable way for a recompiled build to be slow.

The good news is that there is a well-understood ladder from "a function call per access"
to "a single host instruction per access," and most targets can climb most of it.

---

## 1. The Ladder

### Rung 0: a function with a switch

Where everyone starts, and correct:

```c
uint8_t bus_read8(uint16_t addr) {
    if (addr < 0x4000) return rom[addr];
    if (addr < 0x8000) return rom_bank[addr - 0x4000];
    if (addr < 0xA000) return vram[addr - 0x8000];
    ...
}
```

A call, a chain of comparisons, and an unpredictable branch, for every access. Fine for an
8-bit target where you have a thousand times the needed headroom (Module 41 §2). Not fine
for anything modern.

### Rung 1: a flat array with a base offset

If the guest's address space is small enough to allocate outright, the translation becomes
arithmetic. `burnout3`'s harness does exactly this:

```c
extern ptrdiff_t g_xbox_mem_offset;
#define FMEM32(addr) (*(volatile uint32_t *)((uintptr_t)(addr) + g_xbox_mem_offset))
```

A guest address plus a constant offset *is* a host address. No call, no branch, no bounds
check — one `mov`. `gbarecomp`'s stated design is the same idea: *"Memory is flat
arrays."*

The cost is that you lose the ability to notice anything. Memory-mapped I/O needs §2.

### Rung 2: the guest's own addresses, via the host MMU

The strongest version, and the one that makes guest pointers Just Work. `burnout3`
reproduces the Xbox's 64 MB **using `CreateFileMapping` with mirror views** — the same
physical pages mapped at several virtual addresses, so the guest's mirrored regions behave
as they did on hardware, at the addresses the guest expects.

Once you have this, a guest pointer stored in guest memory and dereferenced later is
correct with no translation at all. Structures containing pointers, linked lists, vtables —
all of it works without your memory layer being involved.

`mmap` with `MAP_FIXED` is the POSIX equivalent. `flow` exposes
`Runtime::instance()->virtual_membase()` for the same purpose.

**The catch:** you need the guest's address range to be available in your host process.
32-bit guests on 64-bit hosts are usually fine. A guest that wants address `0x00010000`
competes with your own loader, so reserve early, before anything else allocates.

---

## 2. Keeping I/O Working When Access Is Free

The moment reads are raw pointer arithmetic, a read of a hardware register no longer calls
you — and the whole point of a hardware register is that reading it *does something*.

Three workable answers:

**Split at lift time.** If the address is a compile-time constant, the lifter knows whether
it is RAM or I/O and emits the fast path or the call accordingly. This handles the large
majority of accesses in most programs, because most addresses are constants or
constant-plus-register offsets into known regions.

**Range-check only the dynamic ones.** For computed addresses, one comparison against the
I/O window is far cheaper than a full dispatch, and predicts almost perfectly because the
answer is nearly always "not I/O."

**Let the MMU do it.** Map the I/O range with no access permission and handle the fault.
Zero cost when not touched, very expensive when touched, and fiddly across platforms — a
good fit when I/O is rare and a bad one when it is in a loop.

`xboxrecomp` shows the shape of the hybrid in practice: raw `FMEM32`-style access for
memory, with an explicit APU MMIO hook (`src/apu/apu_mmio_hook.c`) for the region that
needs it.

---

## 3. Endianness Without Branches

A big-endian guest (N64, GameCube, Xbox 360, PS3, Saturn, Neo Geo) on a little-endian host
needs a swap on every access. Done naively that is a function call and a shift-heavy
expression.

Two things make it nearly free.

**Use the host's byte-swap intrinsic.** `__builtin_bswap32`, `_byteswap_ulong` — these
compile to a single instruction. Never hand-roll shifts and masks.

**Or do not swap at all.** If you store guest memory byte-swapped in units of the guest's
word size, aligned word accesses need no swap — only sub-word accesses do, and those can be
handled by XOR-ing the low address bits. N64Recomp uses exactly this trick: an XOR on the
address selects the right byte within a stored word, so the common case costs nothing and
the uncommon case costs one `xor`.

Pick one based on your access mix, and measure. Both beat a swap function.

---

## 4. Cache Behaviour, and the Thing That Actually Bites

Module 41 §1 has the number that dominates this section: `wormsrevolution` lifted **88,816
functions** and reaches **444**.

That ratio is a cache story. Your hot 444 functions are scattered across a binary sized for
88,816, so functions that call each other constantly may sit megabytes apart, and every
call is an instruction-cache miss that the original 5 MB binary never had.

This is why Module 44's function ordering and dead-code elimination are performance work
rather than tidiness. **Your best cache optimisation is compiling less.**

For data, the guidance is simpler than it looks: the guest's memory layout is fixed and you
must not change it. What you *can* control is the layout of your own structures —
especially the CPU context. Keep the registers your generated code touches most in one
cache line, and do not put a 4 KB lookup table in the middle of a hot struct.

---

## 5. What Not to Do

**Do not add a software TLB or address cache.** It is the instinct from emulator
development, where dynamic translation makes it worthwhile. In a static recompiler it
replaces one `add` with a lookup and a branch, and is reliably slower.

**Do not make every access `volatile`.** `burnout3`'s `FMEM32` uses `volatile` because the
harness reads addresses the guest is concurrently writing. Applied to all guest memory, it
forbids the compiler from keeping *anything* in a register and will cost you more than the
memory layer ever did.

**Do not bounds-check every access in release builds.** Do it under a debug flag — where it
is genuinely valuable, as Module 38's tripwires argue — and compile it out otherwise.

**Do not optimise this before Module 41 says to.** The runtime and the graphics translation
are usually larger costs, and memory access optimisation is invasive enough that doing it
speculatively is how a working recompiler becomes a broken one.

---

## Labs

- **Lab 76** -- Memory access ladder: implement rung 0, rung 1 and (where the platform
  allows) rung 2 for one guest, and measure all three on the same workload. Report the
  speedup and what each rung gave up.
- **Lab 77** -- Endianness two ways: implement byte-swap-on-access and swapped-storage
  with address XOR for a big-endian guest, and compare them on read-heavy and write-heavy
  workloads.

---

**Next: [Module 44 -- Whole-Program Optimization](../module-44-whole-program-opt/lecture.md)**
