# Ghidra Quick Reference for Recompiler Authors

## What Ghidra Provides

- **Disassembly** -- machine code to assembly for dozens of architectures
- **Decompilation** -- assembly to pseudo-C (invaluable for understanding semantics)
- **Control Flow Graphs** -- visual and programmatic access to basic blocks and edges
- **Cross-references (xrefs)** -- who calls what, who reads/writes what address
- **Symbol and type management** -- rename functions, define structs, apply signatures

## Key Views

| View              | Shortcut       | Use in Recompiler Work                         |
|-------------------|----------------|------------------------------------------------|
| Listing           | (default)      | Raw disassembly with labels and xrefs          |
| Decompiler        | `Ctrl+E`       | Pseudo-C output to guide your C translation    |
| Function Graph    | `Ctrl+Shift+G` | Visualize basic blocks and branch structure    |
| Symbol Table      | (Window menu)  | Browse all functions, labels, imports, exports |
| Defined Strings   | (Window menu)  | Find string literals referenced by code        |
| Bytes View        | (Window menu)  | Raw hex for header/format analysis             |

## Useful Scripts for Recompiler Work

### Export Function List

```python
# Ghidra Python (Jython) -- run via Script Manager
import csv
f = open("/tmp/functions.csv", "w")
writer = csv.writer(f)
writer.writerow(["Name", "Address", "Size"])
fm = currentProgram.getFunctionManager()
for func in fm.getFunctions(True):
    writer.writerow([func.getName(), func.getEntryPoint(), func.getBody().getNumAddresses()])
f.close()
print("Exported %d functions" % fm.getFunctionCount())
```

### Export Cross-References

```python
from ghidra.program.model.symbol import ReferenceManager
rm = currentProgram.getReferenceManager()
fm = currentProgram.getFunctionManager()
for func in fm.getFunctions(True):
    entry = func.getEntryPoint()
    refs = rm.getReferencesTo(entry)
    for ref in refs:
        print("%s -> %s (from %s)" % (ref.getFromAddress(), func.getName(), ref.getReferenceType()))
```

### Find Indirect Calls

```python
# Finds call/jump through register or memory -- important for vtables, function pointers
from ghidra.program.model.listing import CodeUnit
listing = currentProgram.getListing()
fm = currentProgram.getFunctionManager()
for func in fm.getFunctions(True):
    body = func.getBody()
    inst_iter = listing.getInstructions(body, True)
    while inst_iter.hasNext():
        inst = inst_iter.next()
        flow = inst.getFlowType()
        if flow.isCall() and flow.isComputed():
            print("Indirect call at %s in %s: %s" % (inst.getAddress(), func.getName(), inst))
```

### Dump Disassembly to Text

```python
listing = currentProgram.getListing()
fm = currentProgram.getFunctionManager()
f = open("/tmp/disasm.txt", "w")
for func in fm.getFunctions(True):
    f.write("\n; === %s (0x%s) ===\n" % (func.getName(), func.getEntryPoint()))
    inst_iter = listing.getInstructions(func.getBody(), True)
    while inst_iter.hasNext():
        inst = inst_iter.next()
        f.write("  0x%s:  %s %s\n" % (inst.getAddress(), inst.getMnemonicString(), inst.getDefaultOperandRepresentation(0)))
f.close()
```

## Ghidra Scripting Basics

| Feature          | Python (Jython)            | Java                          |
|------------------|----------------------------|-------------------------------|
| Script location  | `ghidra_scripts/` folder   | `ghidra_scripts/` folder      |
| Entry object     | `currentProgram`           | `currentProgram`              |
| Run from         | Script Manager or headless | Script Manager or headless    |
| Pros             | Quick prototyping          | Full API access, faster       |
| Key imports      | `from ghidra.program.model.*` | `import ghidra.program.model.*` |

Common entry points: `currentProgram`, `currentAddress`, `currentSelection`, `monitor` (for progress).

## Headless Analysis

```bash
# Analyze a binary and run a script without opening the GUI
<GHIDRA_INSTALL>/support/analyzeHeadless \
    /path/to/project ProjectName \
    -import /path/to/binary \
    -postScript MyExportScript.py \
    -processor <PROCESSOR_ID> \
    -scriptPath /path/to/scripts
```

Common processor IDs: `x86:LE:32:default`, `PowerPC:BE:32:default`, `MIPS:BE:64:default`, `ARM:LE:32:v7`

## Keyboard Shortcuts (Top 15)

| Shortcut          | Action                                |
|-------------------|---------------------------------------|
| `G`               | Go to address                         |
| `L`               | Rename label / function               |
| `Ctrl+E`          | Open Decompiler view                  |
| `Ctrl+Shift+G`    | Open Function Graph                   |
| `X`               | Show cross-references to selection    |
| `Ctrl+Shift+F`    | Search for text in all fields         |
| `D`               | Disassemble at cursor                 |
| `C`               | Clear code at cursor                  |
| `T`               | Set data type at cursor               |
| `F`               | Create function at cursor             |
| `;`               | Add comment                           |
| `Ctrl+L`          | Retype variable (in Decompiler)       |
| `N`               | Rename variable (in Decompiler)       |
| `Space`           | Toggle Listing / Function Graph       |
| `Alt+Left`        | Navigate back                         |
