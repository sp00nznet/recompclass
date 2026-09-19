# Lab 93: Assemble the Address Space

## Objective

Reproduce the single cheapest win in Module 55: analysing the whole machine
instead of half of it.

## Background

From `cybikorecomp`'s `INDIRECT.md`:

> CyOS and the boot ROM are separate files but **not separate worlds** --
> CyOS calls down into the boot ROM constantly, for `memcpy` and `memset`
> among others. Analysed apart, every such call is a "target outside the
> image". `tools/cyimage.py` glues them into one space (`0x000000` boot ROM,
> `0x200000` SRAM), and that alone took unresolved transfers from **2,533 to
> 227**.

And the second-order effect:

> It also removed all 12 "undecodable opcodes", which were **never decoder
> gaps** -- they were misaligned decodes caused by tracing into a region the
> other half owned.

## Your Task

Implement in `addrspace.py`:

- `AddressSpace` -- several images mapped at their own bases.
- `contains(addr)` / `image_of(addr)`.
- `analyse(transfers, space)` -- resolved versus unresolved.
- `compare_assembly(images, transfers)` -- per-image versus combined.

## The Number to Report

`compare_assembly` returns the unresolved count both ways. That ratio is
the finding, and it costs an afternoon to produce.
