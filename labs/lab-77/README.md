# Lab 77: Endianness Two Ways

## Objective

Implement both endianness strategies from Module 43 section 3 and find out
which suits your access mix.

## Background

A big-endian guest on a little-endian host needs a swap on every access.
Two ways to make it nearly free:

**Swap on access**, using the host's byte-swap intrinsic -- a single
instruction. Never hand-roll shifts and masks.

**Do not swap at all.** Store guest memory byte-swapped in units of the
guest's word size. Aligned word accesses then need no swap; only sub-word
accesses do, and those are handled by XOR-ing the low address bits. N64Recomp
uses exactly this -- the common case costs nothing and the uncommon case
costs one `xor`.

## Your Task

Implement in `endian.py`:

- `swap32(value)` -- the reference swap.
- `SwapOnAccess` -- strategy one, counting swaps.
- `SwappedStorage` -- strategy two, counting XORs.
- `compare(...)` -- run both over a workload.

Both must produce identical results for every access. A test asserts it.
