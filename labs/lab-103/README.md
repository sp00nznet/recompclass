# Lab 103: Symbol Importer

## Objective

Build the importer from Module 51 section 3 -- and make it an importer, not
a copy.

## Background

Decompilation projects improve continuously. A symbol file you pasted into
your repository in March is stale in April, and you will not notice.

```
decomp repo --> import script --> your function-set file --> recompiler
  (upstream)      (yours)          (committed)
```

Module 33's provenance rule applies: **record which upstream commit you
imported from**, or you cannot tell whether an upstream fix has reached you.

And Module 51 section 7's caution: symbol files are human work in progress.
A misnamed or mis-sized function propagates straight into your discovery, so
imported boundaries deserve the same checks as discovered ones.

## Your Task

Implement in `symimport.py`:

- `parse_symbols(text)` -- the upstream format.
- `to_function_set(symbols, commit)` -- your format, with provenance.
- `diff_imports(old, new)` -- what changed since last time.
- `validate_symbols(symbols)` -- overlaps and zero sizes.

## What the Diff Is For

Running the importer should tell you *what moved*, not just succeed.
Upstream renaming a function or correcting a size is exactly the kind of
change that silently invalidates your hints.
