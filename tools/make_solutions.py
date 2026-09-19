#!/usr/bin/env python3
"""
Generate reference solutions for the labs.

Each lab ships a stub whose unimplemented functions end in a `# TODO:` comment
block followed by `pass` (or `raise NotImplementedError(...)`). The reference
solution is the same file with those bodies filled in, written to
`labs/lab-NN/solution/`.

Generating rather than hand-maintaining means a solution cannot silently drift
from its stub: if a stub's tables, imports or signatures change, regenerating
picks that up, and a stub whose shape changed fails loudly here instead of
producing a solution that no longer matches the exercise.

    python tools/make_solutions.py           # write all solutions
    python tools/make_solutions.py --check   # verify they are current (CI)

Add work with `impl("lab-NN", "file.py", "function_name", r'''body''')`.
Bodies are RAW strings: a backslash in a body is a backslash in the generated
solution. Without that, a body containing a newline escape turns into a real
newline here and silently wrecks the generated file's indentation. The
script locates that function, finds the trailing TODO block, and swaps in the
body. Bodies are written at one indent level (4 spaces) unless the function is
a method, in which case the script re-indents to match.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys
import textwrap

REPO = pathlib.Path(__file__).resolve().parent.parent
LABS = REPO / "labs"
NEWLINE = chr(10)

# (lab, filename) -> list of (function_name, body)
IMPLS: dict[tuple[str, str], list[tuple[str, str]]] = {}


def impl(lab: str, filename: str, func: str, body: str) -> None:
    """Register a solution body.

    The body is de-indented by the indentation of its *first* line rather than
    by textwrap.dedent's common prefix. dedent gives up silently -- returning
    the text unchanged -- if any line sits at column zero, which happens
    whenever a body contains an escaped newline that got un-escaped on the way
    in. That produced valid-looking Python indented one level too deep, which
    is a tedious thing to debug twice.
    """
    lines = body.strip(NEWLINE).splitlines()
    if not lines:
        raise SystemExit(f"{lab}/{filename}: empty body for {func!r}")

    pad = len(lines[0]) - len(lines[0].lstrip())
    prefix = lines[0][:pad]
    out = []
    for line in lines:
        if line.strip() and not line.startswith(prefix):
            raise SystemExit(
                f"{lab}/{filename}: inconsistent indentation in {func!r}. "
                f"Every line must begin with {pad} spaces; this one does not:"
                f"{NEWLINE}  {line!r}"
            )
        out.append(line[pad:] if line.strip() else "")
    IMPLS.setdefault((lab, filename), []).append((func, NEWLINE.join(out)))


# ==========================================================================
# Solutions
# ==========================================================================

# ------------------------------------------------------------------ lab-01
impl("lab-01", "rom_inspector.py", "parse_title", r"""
    raw = rom_data[0x134:0x144]
    return raw.decode("ascii", errors="replace").rstrip("\x00").strip()
""")
impl("lab-01", "rom_inspector.py", "parse_cartridge_type", r"""
    value = read_u8(rom_data, 0x147)
    return value, CARTRIDGE_TYPES.get(value, "UNKNOWN")
""")
impl("lab-01", "rom_inspector.py", "parse_rom_size", r"""
    value = read_u8(rom_data, 0x148)
    return value, ROM_SIZES.get(value, "UNKNOWN")
""")
impl("lab-01", "rom_inspector.py", "parse_ram_size", r"""
    value = read_u8(rom_data, 0x149)
    return value, RAM_SIZES.get(value, "UNKNOWN")
""")
impl("lab-01", "rom_inspector.py", "compute_header_checksum", r"""
    x = 0
    for addr in range(0x134, 0x14D):
        x = (x - read_u8(rom_data, addr) - 1) & 0xFF
    return x
""")

# ------------------------------------------------------------------ lab-08
impl("lab-08", "mz_parser.py", "apply_relocations", r"""
    image = bytearray(self.get_code_image())
    for entry in self.relocations:
        position = entry.segment * 16 + entry.offset
        if position + 2 > len(image):
            print(f"Warning: relocation at {position:#x} is outside the image")
            continue
        value = struct.unpack_from("<H", image, position)[0]
        struct.pack_into("<H", image, position, (value + load_segment) & 0xFFFF)
    return image
""")
impl("lab-08", "mz_parser.py", "detect_overlays", r"""
    expected = self.header.file_size
    if expected and len(self.data) > expected:
        return expected
    return None
""")


# ------------------------------------------------------------------ lab-21
impl("lab-21", "decoder_6502.py", "decode_instruction", r"""
    if offset >= len(data):
        return None

    opcode = data[offset]
    entry = OPCODE_TABLE.get(opcode)
    if entry is None:
        return None

    mnemonic, mode, length = entry
    if offset + length > len(data):
        return None

    if length == 1:
        operand = None
    elif length == 2:
        operand = data[offset + 1]
    else:
        operand = data[offset + 1] | (data[offset + 2] << 8)

    return {
        "address": base_address + offset,
        "opcode": opcode,
        "mnemonic": mnemonic,
        "mode": mode,
        "length": length,
        "operand": operand,
        "raw": bytes(data[offset:offset + length]),
    }
""")

impl("lab-21", "decoder_6502.py", "format_instruction", r"""
    if decoded is None:
        return None

    address = decoded["address"]
    mnemonic = decoded["mnemonic"]
    mode = decoded["mode"]
    operand = decoded["operand"]
    head = f"${address:04X}: {mnemonic}"

    if mode == "imp":
        return head
    if mode == "acc":
        return f"{head} A"

    if mode == "rel":
        # The offset is signed and measured from the *next* instruction.
        signed = operand if operand < 0x80 else operand - 0x100
        target = (address + decoded["length"] + signed) & 0xFFFF
        return f"{head} ${target:04X}"

    one_byte = {
        "imm": "#${:02X}",
        "zp":  "${:02X}",
        "zpx": "${:02X},X",
        "zpy": "${:02X},Y",
        "izx": "(${:02X},X)",
        "izy": "(${:02X}),Y",
    }
    two_byte = {
        "abs": "${:04X}",
        "abx": "${:04X},X",
        "aby": "${:04X},Y",
        "ind": "(${:04X})",
    }

    if mode in one_byte:
        return f"{head} " + one_byte[mode].format(operand)
    if mode in two_byte:
        return f"{head} " + two_byte[mode].format(operand)

    # Unknown mode: show the raw operand rather than silently dropping it.
    return f"{head} ${operand:04X}" if operand is not None else head
""")

impl("lab-21", "decoder_6502.py", "disassemble", r"""
    lines = []
    offset = 0
    while offset < len(data):
        if count is not None and len(lines) >= count:
            break

        decoded = decode_instruction(data, offset, base_address)
        if decoded is None:
            # Unknown opcode: skip one byte and resynchronise.
            offset += 1
            continue

        lines.append(format_instruction(decoded))
        offset += decoded["length"]

    return lines
""")


# ------------------------------------------------------------------ lab-22
impl("lab-22", "export_functions.py", "get_all_functions", r"""
    fm = program.getFunctionManager()
    functions = []
    for func in fm.getFunctions(True):
        functions.append({
            "name": func.getName(),
            "address": "0x" + format(int(str(func.getEntryPoint()), 16), "08x"),
            "size": func.getBody().getNumAddresses(),
        })
    return functions
""")

impl("lab-22", "export_functions.py", "export_to_json", r"""
    functions = get_all_functions(program)
    result = {
        "binary": program.getName(),
        "function_count": len(functions),
        "functions": functions,
    }
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    return result
""")

# ------------------------------------------------------------------ lab-23
impl("lab-23", "cfg_builder.py", "build_cfg", r"""
    cfg = {}
    worklist = [entry_point]

    while worklist:
        addr = worklist.pop()
        if addr in cfg:
            continue

        block = BasicBlock(addr)
        cursor = addr
        last = None

        while True:
            instr = decode_one(data, cursor)
            if instr is None:
                break
            block.instructions.append(instr)
            cursor += instr["length"]
            last = instr
            if instr["opcode"] in BRANCH_OPCODES:
                break

        if last is not None:
            opcode = last["opcode"]
            if opcode in JUMP_OPCODES and last["operand"] is not None:
                target = last["operand"]
                block.successors.append((target, "taken"))
                worklist.append(target)
            if opcode in FALLTHROUGH_OPCODES:
                block.successors.append((cursor, "fall"))
                worklist.append(cursor)

        cfg[addr] = block

    return cfg
""")

impl("lab-23", "cfg_builder.py", "cfg_to_dot", r"""
    lines = ["digraph CFG {"]
    lines.append('  node [shape=box, fontname="Courier"];')

    for addr in sorted(cfg):
        block = cfg[addr]
        body = "\n".join(format_instruction(i) for i in block.instructions)
        lines.append(f'  "{block.label()}" [label="{body}"];')

    for addr in sorted(cfg):
        block = cfg[addr]
        for target, edge in block.successors:
            target_label = cfg[target].label() if target in cfg else f"blk_{target:04X}"
            lines.append(f'  "{block.label()}" -> "{target_label}" [label="{edge}"];')

    lines.append("}")
    return "\n".join(lines) + "\n"
""")


# ------------------------------------------------------------------ lab-24
impl("lab-24", "flags.py", "compute_add_flags", r"""
    result = (a + b) & 0xFF
    return {
        "Z": result == 0,
        "N": False,
        "H": (a & 0x0F) + (b & 0x0F) > 0x0F,
        "C": a + b > 0xFF,
    }
""")
impl("lab-24", "flags.py", "compute_sub_flags", r"""
    result = (a - b) & 0xFF
    return {
        "Z": result == 0,
        "N": True,
        "H": (a & 0x0F) < (b & 0x0F),
        "C": a < b,
    }
""")
impl("lab-24", "flags.py", "compute_and_flags", r"""
    result = a & b
    return {
        "Z": result == 0,
        "N": False,
        # AND is the odd one out: it always sets H and always clears C.
        "H": True,
        "C": False,
    }
""")
impl("lab-24", "flags.py", "compute_inc_flags", r"""
    result = (a + 1) & 0xFF
    return {
        "Z": result == 0,
        "N": False,
        "H": (a & 0x0F) + 1 > 0x0F,
        "C": old_carry,     # INC leaves carry alone
    }
""")
impl("lab-24", "flags.py", "compute_dec_flags", r"""
    result = (a - 1) & 0xFF
    return {
        "Z": result == 0,
        "N": True,
        "H": (a & 0x0F) < 1,
        "C": old_carry,     # DEC leaves carry alone
    }
""")

# ------------------------------------------------------------------ lab-26
impl("lab-26", "nes_inspector.py", "validate_magic", r"""
    return rom_data[0:4] == INES_MAGIC
""")
impl("lab-26", "nes_inspector.py", "parse_prg_rom_size", r"""
    return rom_data[4] * 16384
""")
impl("lab-26", "nes_inspector.py", "parse_chr_rom_size", r"""
    return rom_data[5] * 8192
""")
impl("lab-26", "nes_inspector.py", "parse_mapper", r"""
    flags6 = rom_data[6]
    flags7 = rom_data[7]
    # Low nibble of the mapper lives in the high nibble of flags 6,
    # the high nibble in the high nibble of flags 7.
    mapper = (flags7 & 0xF0) | (flags6 >> 4)
    return mapper, MAPPER_NAMES.get(mapper, "Unknown")
""")
impl("lab-26", "nes_inspector.py", "parse_mirroring", r"""
    flags6 = rom_data[6]
    if flags6 & 0x08:          # bit 3 overrides bit 0
        return "Four-Screen"
    if flags6 & 0x01:
        return "Vertical"
    return "Horizontal"
""")
impl("lab-26", "nes_inspector.py", "parse_flags", r"""
    flags6 = rom_data[6]
    return {
        "battery": bool(flags6 & 0x02),
        "trainer": bool(flags6 & 0x04),
    }
""")


# ------------------------------------------------------------------ lab-27
impl("lab-27", "arm_disasm.py", "disasm_arm", r"""
    cs = Cs(CS_ARCH_ARM, CS_MODE_ARM)
    return [
        (insn.address, insn.mnemonic, insn.op_str, insn.bytes)
        for insn in cs.disasm(data, base_address)
    ]
""")
impl("lab-27", "arm_disasm.py", "disasm_thumb", r"""
    cs = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    return [
        (insn.address, insn.mnemonic, insn.op_str, insn.bytes)
        for insn in cs.disasm(data, base_address)
    ]
""")
impl("lab-27", "arm_disasm.py", "format_disasm", r"""
    return [
        f"[{mode_label:5s}] 0x{addr:08X}: {mnemonic:6s} {op_str}"
        for addr, mnemonic, op_str, _raw in instructions
    ]
""")
impl("lab-27", "arm_disasm.py", "detect_mode_switches", r"""
    return [
        {"address": addr, "register": op_str.strip()}
        for addr, mnemonic, op_str, _raw in instructions
        if mnemonic.lower() == "bx"
    ]
""")
impl("lab-27", "arm_disasm.py", "disasm_auto", r"""
    lines = []
    for section in sections:
        addr = base_address + section["offset"]
        if section["mode"] == "thumb":
            decoded = disasm_thumb(section["data"], addr)
            label = "THUMB"
        else:
            decoded = disasm_arm(section["data"], addr)
            label = "ARM"
        lines.extend(format_disasm(decoded, label))
    return lines
""")

# ------------------------------------------------------------------ lab-28
impl("lab-28", "gba_inspector.py", "parse_entry_point", r"""
    entry_word = struct.unpack_from("<I", rom_data, 0)[0]
    offset = entry_word & 0x00FFFFFF
    if offset & 0x00800000:          # sign-extend the 24-bit field
        offset |= 0xFF000000
        offset -= 0x100000000
    # The ARM pipeline means a branch is relative to PC+8.
    return 8 + (offset << 2)
""")
impl("lab-28", "gba_inspector.py", "parse_game_title", r"""
    return rom_data[0xA0:0xAC].decode("ascii", errors="replace").rstrip("\x00").strip()
""")
impl("lab-28", "gba_inspector.py", "parse_game_code", r"""
    return rom_data[0xAC:0xB0].decode("ascii", errors="replace")
""")
impl("lab-28", "gba_inspector.py", "parse_maker_code", r"""
    return rom_data[0xB0:0xB2].decode("ascii", errors="replace")
""")
impl("lab-28", "gba_inspector.py", "compute_complement", r"""
    checksum = 0
    for byte in rom_data[0xA0:0xBD]:
        checksum = (checksum - byte) & 0xFF
    return (checksum - 0x19) & 0xFF
""")
impl("lab-28", "gba_inspector.py", "validate_header", r"""
    stored = rom_data[0xBD]
    computed = compute_complement(rom_data)
    return stored, computed, stored == computed
""")


# ------------------------------------------------------------------ lab-29
impl("lab-29", "analysis_checklist.py", "parse_sections", r"""
    sections = {}
    title = None
    body = []
    for line in text.splitlines():
        if line.startswith("## "):
            if title is not None:
                sections[title] = "\n".join(body)
            title = line[3:].strip()
            body = []
        elif title is not None:
            body.append(line)
    if title is not None:
        sections[title] = "\n".join(body)
    return sections
""")
impl("lab-29", "analysis_checklist.py", "check_section_present", r"""
    if title not in sections:
        return False, False
    # Strip the [TODO: ...] placeholders and see whether anything real is left.
    remainder = re.sub(r"\[TODO:.*?\]", "", sections[title], flags=re.S)
    return True, bool(remainder.strip())
""")
impl("lab-29", "analysis_checklist.py", "count_list_items", r"""
    body = sections.get(title)
    if not body:
        return 0
    return sum(
        1 for line in body.splitlines()
        if re.match(r"^\s*(\d+\.|[-*])\s", line)
    )
""")

# ------------------------------------------------------------------ lab-31
impl("lab-31", "trace_compare.py", "load_trace", r"""
    with open(filepath, newline="") as f:
        return [
            {key: int(value, 16) for key, value in row.items()}
            for row in csv.DictReader(f)
        ]
""")
impl("lab-31", "trace_compare.py", "load_trace_from_string", r"""
    return [
        {key: int(value, 16) for key, value in row.items()}
        for row in csv.DictReader(text.splitlines())
    ]
""")
impl("lab-31", "trace_compare.py", "compare_traces", r"""
    for step, (expected, got) in enumerate(zip(trace_a, trace_b)):
        differs = [
            key for key in expected
            if key in got and expected[key] != got[key]
        ]
        if differs:
            return {
                "step": step,
                "expected": expected,
                "got": got,
                "differs": differs,
            }
    return None
""")

# ------------------------------------------------------------------ lab-32
impl("lab-32", "dead_code.py", "find_reachable", r"""
    visited = set()
    worklist = [entry]
    while worklist:
        name = worklist.pop()
        if name in visited:
            continue
        visited.add(name)
        for callee in graph.get(name, []):
            if callee not in visited:
                worklist.append(callee)
    return visited
""")
impl("lab-32", "dead_code.py", "find_dead_code", r"""
    reachable = find_reachable(entry, graph)
    return set(graph) - reachable
""")

impl("lab-31", "trace_compare.py", "format_divergence", r"""
    if div is None:
        return "Traces match."

    step = div["step"]
    expected = div["expected"]
    got = div["got"]

    lines = [
        f"Traces diverge at step {step} (CSV line {step + 2}):",
        "",
    ]
    for key in div["differs"]:
        lines.append(
            f"  {key}: expected 0x{expected[key]:X}, got 0x{got[key]:X}"
        )
    lines.append("")
    lines.append("  expected row: " + ", ".join(
        f"{k}=0x{v:X}" for k, v in expected.items()))
    lines.append("  actual row:   " + ", ".join(
        f"{k}=0x{v:X}" for k, v in got.items()))
    return "\n".join(lines)
""")


# ------------------------------------------------------------------ lab-33
impl("lab-33", "dlist_parser.py", "parse_command", r"""
    if offset + 8 > len(data):
        return None

    raw = bytes(data[offset:offset + 8])
    cmd_id = raw[0]
    cmd_name = COMMAND_NAMES.get(cmd_id, "UNKNOWN")

    if cmd_id == 0x04:          # G_VTX
        params = {
            "count": (data[offset + 1] >> 4) & 0x0F,
            "addr": struct.unpack_from(">I", data, offset + 4)[0],
        }
    elif cmd_id == 0x06:        # G_TRI1 -- indices are stored pre-multiplied by 2
        params = {
            "v0": data[offset + 5] // 2,
            "v1": data[offset + 6] // 2,
            "v2": data[offset + 7] // 2,
        }
    elif cmd_id in (0x05, 0xFD):    # G_DL, G_SETTIMG
        params = {"addr": struct.unpack_from(">I", data, offset + 4)[0]}
    else:
        params = {
            "word0": struct.unpack_from(">I", data, offset)[0],
            "word1": struct.unpack_from(">I", data, offset + 4)[0],
        }

    return {
        "offset": offset,
        "cmd_id": cmd_id,
        "cmd_name": cmd_name,
        "raw": raw,
        "params": params,
    }
""")
impl("lab-33", "dlist_parser.py", "parse_display_list", r"""
    commands = []
    offset = 0
    while offset + 8 <= len(data):
        cmd = parse_command(data, offset)
        if cmd is None:
            break
        commands.append(cmd)
        offset += 8
        if cmd["cmd_id"] == 0xB8:       # G_ENDDL terminates the list
            break
    return commands
""")
impl("lab-33", "dlist_parser.py", "format_command", r"""
    prefix = f"{cmd['offset']:04X}: {cmd['cmd_name']:20s}"
    params = cmd["params"]
    name = cmd["cmd_name"]

    if name == "G_VTX":
        return prefix + f"count={params['count']}, addr=0x{params['addr']:08X}"
    if name == "G_TRI1":
        return prefix + f"v0={params['v0']}, v1={params['v1']}, v2={params['v2']}"
    if "addr" in params:
        return prefix + f"addr=0x{params['addr']:08X}"
    return prefix + f"word0=0x{params['word0']:08X}, word1=0x{params['word1']:08X}"
""")
impl("lab-33", "dlist_parser.py", "summarize", r"""
    counts = {}
    for cmd in commands:
        counts[cmd["cmd_name"]] = counts.get(cmd["cmd_name"], 0) + 1
    return counts
""")


# ------------------------------------------------------------------ lab-34
impl("lab-34", "wii_dol_parser.py", "parse_dol_header", r"""
    def words(start, count):
        return [_read_u32_be(data, start + i * 4) for i in range(count)]

    text_offsets = words(TEXT_OFFSETS_START, 7)
    data_offsets = words(DATA_OFFSETS_START, 11)
    text_addrs = words(TEXT_ADDRS_START, 7)
    data_addrs = words(DATA_ADDRS_START, 11)
    text_sizes = words(TEXT_SIZES_START, 7)
    data_sizes = words(DATA_SIZES_START, 11)

    text_sections = [
        {"file_offset": o, "load_address": a, "size": z}
        for o, a, z in zip(text_offsets, text_addrs, text_sizes)
    ]
    data_sections = [
        {"file_offset": o, "load_address": a, "size": z}
        for o, a, z in zip(data_offsets, data_addrs, data_sizes)
    ]

    return {
        "text_sections": text_sections,
        "data_sections": data_sections,
        "bss_address": _read_u32_be(data, BSS_ADDR_OFFSET),
        "bss_size": _read_u32_be(data, BSS_SIZE_OFFSET),
        "entry_point": _read_u32_be(data, ENTRY_POINT_OFFSET),
    }
""")
impl("lab-34", "wii_dol_parser.py", "get_text_sections", r"""
    return [
        dict(section, index=i)
        for i, section in enumerate(header["text_sections"])
        if section["size"] > 0
    ]
""")
impl("lab-34", "wii_dol_parser.py", "get_data_sections", r"""
    return [
        dict(section, index=i)
        for i, section in enumerate(header["data_sections"])
        if section["size"] > 0
    ]
""")
impl("lab-34", "wii_dol_parser.py", "get_entry_point", r"""
    return header["entry_point"]
""")
impl("lab-34", "wii_dol_parser.py", "get_bss_info", r"""
    return header["bss_address"], header["bss_size"]
""")
impl("lab-34", "wii_dol_parser.py", "detect_platform", r"""
    sections = header["text_sections"] + header["data_sections"]
    for section in sections:
        if section["size"] <= 0:
            continue
        if MEM2_START <= section["load_address"] < MEM2_END:
            return "Wii"
    return "GameCube"
""")


# ------------------------------------------------------------------ lab-35
impl("lab-35", "sh2_lifter.py", "decode_sh2", r"""
    if offset + 2 > len(data):
        return None

    word = struct.unpack_from(">H", data, offset)[0]
    address = base_address + offset

    instr = {
        "address": address,
        "raw": word,
        "mnemonic": "UNKNOWN",
        "has_delay": False,
        "rn": None,
        "rm": None,
        "disp": None,
        "target": None,
    }

    if word == 0x000B:                          # RTS
        instr["mnemonic"] = "RTS"
        instr["has_delay"] = True
    elif (word & 0xF00F) == 0x6003:             # MOV Rm, Rn
        instr["mnemonic"] = "MOV"
        instr["rn"] = (word >> 8) & 0xF
        instr["rm"] = (word >> 4) & 0xF
    elif (word & 0xF00F) == 0x300C:             # ADD Rm, Rn
        instr["mnemonic"] = "ADD"
        instr["rn"] = (word >> 8) & 0xF
        instr["rm"] = (word >> 4) & 0xF
    elif (word & 0xF00F) == 0x3000:             # CMP/EQ Rm, Rn
        instr["mnemonic"] = "CMP/EQ"
        instr["rn"] = (word >> 8) & 0xF
        instr["rm"] = (word >> 4) & 0xF
    elif (word & 0xFF00) == 0x8900:             # BT disp
        instr["mnemonic"] = "BT"
        instr["has_delay"] = True
        instr["disp"] = _sign_extend_8(word & 0xFF)
        instr["target"] = address + 4 + instr["disp"] * 2
    elif (word & 0xFF00) == 0x8B00:             # BF disp
        instr["mnemonic"] = "BF"
        instr["has_delay"] = True
        instr["disp"] = _sign_extend_8(word & 0xFF)
        instr["target"] = address + 4 + instr["disp"] * 2
    elif (word & 0xF000) == 0xA000:             # BRA disp
        instr["mnemonic"] = "BRA"
        instr["has_delay"] = True
        instr["disp"] = _sign_extend_12(word & 0xFFF)
        instr["target"] = address + 4 + instr["disp"] * 2
    elif (word & 0xF0FF) == 0x400B:             # JSR @Rm
        instr["mnemonic"] = "JSR"
        instr["has_delay"] = True
        instr["rm"] = (word >> 8) & 0xF

    return instr
""")
impl("lab-35", "sh2_lifter.py", "lift_instruction", r"""
    mnemonic = instr["mnemonic"]
    rn, rm = instr["rn"], instr["rm"]
    target = instr["target"]

    if mnemonic == "MOV":
        return f"regs[{rn}] = regs[{rm}];"
    if mnemonic == "ADD":
        return f"regs[{rn}] = regs[{rn}] + regs[{rm}];"
    if mnemonic == "CMP/EQ":
        return f"T = (regs[{rn}] == regs[{rm}]);"
    if mnemonic == "BT":
        return f"if (T) goto label_{target:08X};"
    if mnemonic == "BF":
        return f"if (!T) goto label_{target:08X};"
    if mnemonic == "BRA":
        return f"goto label_{target:08X};"
    if mnemonic == "JSR":
        return f"PR = 0x{instr['address'] + 4:08X}; goto *regs[{rm}];"
    if mnemonic == "RTS":
        return "goto *PR;"
    return f"/* unknown: 0x{instr['raw']:04X} */;"
""")
impl("lab-35", "sh2_lifter.py", "lift_block", r"""
    lines = []
    offset = 0

    while offset < len(data):
        instr = decode_sh2(data, offset, base_address)
        if instr is None:
            break

        comment = f"/* {instr['address']:08X}: {instr['mnemonic']} */"

        if instr["has_delay"]:
            delay = decode_sh2(data, offset + 2, base_address)
            lines.append(comment)
            if delay is not None:
                # The delay slot executes BEFORE the branch takes effect,
                # so its C has to be emitted first.
                lines.append(lift_instruction(delay) + "   // delay slot")
            lines.append(lift_instruction(instr))
            offset += 4
        else:
            lines.append(comment)
            lines.append(lift_instruction(instr))
            offset += 2

    return lines
""")


# ------------------------------------------------------------------ lab-36
impl("lab-36", "vdp1_parser.py", "parse_cmdctrl", r"""
    end_flag = bool(cmdctrl & 0x8000)
    link_mode = (cmdctrl >> 12) & 0x7
    cmd_type = cmdctrl & 0x000F
    return end_flag, link_mode, cmd_type
""")
impl("lab-36", "vdp1_parser.py", "parse_cmdsize", r"""
    width = ((cmdsize >> 8) & 0x3F) * 8
    height = cmdsize & 0xFF
    return width, height
""")
impl("lab-36", "vdp1_parser.py", "parse_vertices", r"""
    return [
        (
            read_be16_signed(data, offset + i * 4),
            read_be16_signed(data, offset + i * 4 + 2),
        )
        for i in range(4)
    ]
""")
impl("lab-36", "vdp1_parser.py", "parse_command", r"""
    cmdctrl = read_be16(data, offset + 0x00)
    end_flag, link_mode, cmd_type = parse_cmdctrl(cmdctrl)

    cmdsize = read_be16(data, offset + 0x0A)
    width, height = parse_cmdsize(cmdsize)

    return {
        "end": end_flag,
        "link_mode": link_mode,
        "link_name": LINK_NAMES.get(link_mode, "Unknown"),
        "cmd_type": cmd_type,
        "cmd_name": COMMAND_NAMES.get(cmd_type, "Unknown"),
        "cmd_link": read_be16(data, offset + 0x02),
        "draw_mode": read_be16(data, offset + 0x04),
        "color": read_be16(data, offset + 0x06),
        # CMDSRCA holds the character address in 8-byte units.
        "tex_addr": read_be16(data, offset + 0x08) * 8,
        "width": width,
        "height": height,
        "vertices": parse_vertices(data, offset + 0x0C),
        "gouraud": read_be16(data, offset + 0x1C),
    }
""")
impl("lab-36", "vdp1_parser.py", "parse_command_table", r"""
    commands = []
    offset = 0
    while offset + 32 <= len(data):
        cmd = parse_command(data, offset)
        commands.append(cmd)
        offset += 32
        if cmd["end"]:
            break
    return commands
""")


# ------------------------------------------------------------------ lab-37
impl("lab-37", "xbe_inspector.py", "validate_magic", r"""
    return read_u32(data, 0x000) == XBE_MAGIC
""")
impl("lab-37", "xbe_inspector.py", "parse_header", r"""
    return {
        "magic": read_u32(data, 0x000),
        "base_address": read_u32(data, 0x104),
        "headers_size": read_u32(data, 0x108),
        "image_size": read_u32(data, 0x10C),
        "timestamp": read_u32(data, 0x114),
        "cert_addr": read_u32(data, 0x118),
        "num_sections": read_u32(data, 0x11C),
        "section_headers_addr": read_u32(data, 0x120),
        "entry_point_raw": read_u32(data, 0x128),
        "thunk_addr_raw": read_u32(data, 0x16C),
        "num_lib_versions": read_u32(data, 0x174),
        "lib_versions_addr": read_u32(data, 0x178),
    }
""")
impl("lab-37", "xbe_inspector.py", "decode_entry_point", r"""
    # The XBE stores the entry point XOR'd with a per-build key. There is no
    # flag saying which key was used, so the test is whether the result lands
    # inside the image.
    for key, variant in ((ENTRY_RETAIL_KEY, "retail"), (ENTRY_DEBUG_KEY, "debug")):
        decoded = (raw_entry ^ key) & 0xFFFFFFFF
        if base_address <= decoded < base_address + image_size:
            return decoded, variant
    return raw_entry, "unknown"
""")
impl("lab-37", "xbe_inspector.py", "decode_thunk_addr", r"""
    for key, variant in ((THUNK_RETAIL_KEY, "retail"), (THUNK_DEBUG_KEY, "debug")):
        decoded = (raw_thunk ^ key) & 0xFFFFFFFF
        if base_address <= decoded < base_address + image_size:
            return decoded, variant
    return raw_thunk, "unknown"
""")
impl("lab-37", "xbe_inspector.py", "parse_section_header", r"""
    return {
        "flags": read_u32(data, offset + 0x00),
        "vaddr": read_u32(data, offset + 0x04),
        "vsize": read_u32(data, offset + 0x08),
        "raw_addr": read_u32(data, offset + 0x0C),
        "raw_size": read_u32(data, offset + 0x10),
        "name_addr": read_u32(data, offset + 0x14),
    }
""")
impl("lab-37", "xbe_inspector.py", "parse_sections", r"""
    table_offset = header["section_headers_addr"] - header["base_address"]
    return [
        parse_section_header(data, table_offset + i * SECTION_HEADER_SIZE)
        for i in range(header["num_sections"])
    ]
""")
impl("lab-37", "xbe_inspector.py", "read_section_name", r"""
    offset = name_addr - base_address
    if offset < 0 or offset >= len(data):
        return ""
    end = min(offset + 32, len(data))
    raw = data[offset:end]
    terminator = raw.find(b"\x00")
    if terminator != -1:
        raw = raw[:terminator]
    return raw.decode("ascii", errors="replace")
""")
impl("lab-37", "xbe_inspector.py", "parse_kernel_thunk_table", r"""
    ordinals = []
    offset = thunk_file_offset
    while offset + 4 <= len(data):
        value = read_u32(data, offset)
        if value == 0:
            break
        ordinals.append(value & 0x7FFFFFFF)
        offset += 4
    return ordinals
""")


# ------------------------------------------------------------------ lab-39
impl("lab-39", "vmx128_lifter.py", "lift_vaddps", r"""
    return f"vr[{insn['vD']}] = _mm_add_ps(vr[{insn['vA']}], vr[{insn['vB']}]);"
""")
impl("lab-39", "vmx128_lifter.py", "lift_vmulps", r"""
    return f"vr[{insn['vD']}] = _mm_mul_ps(vr[{insn['vA']}], vr[{insn['vB']}]);"
""")
impl("lab-39", "vmx128_lifter.py", "lift_vdot3", r"""
    return f"vr[{insn['vD']}] = vdot3_sse(vr[{insn['vA']}], vr[{insn['vB']}]);"
""")
impl("lab-39", "vmx128_lifter.py", "lift_vperm", r"""
    return (
        f"vr[{insn['vD']}] = vperm_sse("
        f"vr[{insn['vA']}], vr[{insn['vB']}], vr[{insn['vC']}]);"
    )
""")
impl("lab-39", "vmx128_lifter.py", "lift_instruction", r"""
    op = insn["op"]
    lifter = LIFTERS.get(op)
    if lifter is None:
        raise ValueError(f"Unknown opcode: {op}")
    return lifter(insn)
""")
impl("lab-39", "vmx128_lifter.py", "lift_block", r"""
    return [lift_instruction(insn) for insn in instructions]
""")
impl("lab-39", "vmx128_lifter.py", "emit_function", r"""
    lines = [f"void {name}(__m128 vr[128])", "{"]
    for statement in lift_block(instructions):
        lines.append("    " + statement)
    lines.append("}")
    return "\n".join(lines)
""")

# ------------------------------------------------------------------ lab-40
impl("lab-40", "shader_translate.py", "emit_version", r"""
    return "#version 330 core"
""")
impl("lab-40", "shader_translate.py", "emit_texture_uniforms", r"""
    return [f"uniform sampler2D u_tex{i};" for i in texture_indices]
""")
impl("lab-40", "shader_translate.py", "emit_texture_samples", r"""
    return [
        f"    vec4 t{i} = texture(u_tex{i}, v_texcoord);"
        for i in texture_indices
    ]
""")
impl("lab-40", "shader_translate.py", "emit_combine", r"""
    names = [f"t{i}" for i in texture_indices]

    if not names:
        return "    vec4 combined = vec4(1.0);"

    if color_mode == "replace" or len(names) == 1:
        if color_mode == "add" and len(names) == 1:
            return f"    vec4 combined = clamp({names[0]}, 0.0, 1.0);"
        return f"    vec4 combined = {names[0]};"

    if color_mode == "modulate":
        return "    vec4 combined = " + " * ".join(names) + ";"

    if color_mode == "add":
        return "    vec4 combined = clamp(" + " + ".join(names) + ", 0.0, 1.0);"

    if color_mode == "decal":
        # Blend the first texture over the second using its own alpha.
        return f"    vec4 combined = mix({names[1]}, {names[0]}, {names[0]}.a);"

    raise ValueError(f"Unknown color mode: {color_mode}")
""")
impl("lab-40", "shader_translate.py", "emit_alpha_test", r"""
    if not alpha_test:
        return None

    func = alpha_test["func"]
    if func == "never":
        return "    discard;"
    if func == "always":
        return None

    op = ALPHA_FUNC_GLSL.get(func)
    if op is None:
        raise ValueError(f"Unknown alpha test function: {func}")

    ref = alpha_test["ref"]
    return f"    if (!(combined.a {op} {ref})) discard;"
""")
impl("lab-40", "shader_translate.py", "translate", r"""
    textures = combiner.get("textures", [])
    lines = [emit_version(), "", "in vec2 v_texcoord;"]
    lines.extend(emit_texture_uniforms(textures))
    lines.append("out vec4 frag_color;")
    lines.append("")
    lines.append("void main() {")
    lines.extend(emit_texture_samples(textures))
    lines.append(emit_combine(textures, combiner.get("color_mode", "replace")))

    alpha = emit_alpha_test(combiner.get("alpha_test"))
    if alpha is not None:
        lines.append(alpha)

    lines.append("    frag_color = combined;")
    lines.append("}")
    return "\n".join(lines)
""")


# ------------------------------------------------------------------ lab-41
impl("lab-41", "tev_compiler.py", "resolve_color_input", r"""
    if name not in COLOR_SOURCES:
        raise ValueError(f"Unknown color input: {name}")
    return COLOR_SOURCES[name]
""")
impl("lab-41", "tev_compiler.py", "resolve_alpha_input", r"""
    if name not in ALPHA_SOURCES:
        raise ValueError(f"Unknown alpha input: {name}")
    return ALPHA_SOURCES[name]
""")
impl("lab-41", "tev_compiler.py", "emit_tev_color", r"""
    a = resolve_color_input(inputs["a"])
    b = resolve_color_input(inputs["b"])
    c = resolve_color_input(inputs["c"])
    d = resolve_color_input(inputs["d"])
    # TEV computes d +/- ((1-c)*a + c*b), which is exactly GLSL mix(a, b, c).
    sign = "-" if op == "sub" else "+"
    return f"    prev.rgb = {d} {sign} mix({a}, {b}, {c});"
""")
impl("lab-41", "tev_compiler.py", "emit_tev_alpha", r"""
    a = resolve_alpha_input(inputs["a"])
    b = resolve_alpha_input(inputs["b"])
    c = resolve_alpha_input(inputs["c"])
    d = resolve_alpha_input(inputs["d"])
    sign = "-" if op == "sub" else "+"
    return f"    prev.a = {d} {sign} mix({a}, {b}, {c});"
""")
impl("lab-41", "tev_compiler.py", "emit_stage", r"""
    return [
        f"    // TEV Stage {stage_idx}",
        emit_tev_color(stage_idx, stage["color_inputs"], stage["color_op"]),
        emit_tev_alpha(stage_idx, stage["alpha_inputs"], stage["alpha_op"]),
    ]
""")
impl("lab-41", "tev_compiler.py", "compile_tev", r"""
    textures = config.get("textures", [])
    lines = [
        "#version 330 core",
        "",
        "in vec2 v_texcoord;",
        "in vec4 v_color;",
    ]
    for i in textures:
        lines.append(f"uniform sampler2D u_tex{i};")
    lines.append("out vec4 frag_color;")
    lines.append("")
    lines.append("void main() {")
    for i in textures:
        lines.append(f"    vec4 t{i} = texture(u_tex{i}, v_texcoord);")
    lines.append("    vec4 prev = vec4(0.0);")
    for idx, stage in enumerate(config.get("stages", [])):
        lines.extend(emit_stage(idx, stage))
    lines.append("    frag_color = clamp(prev, 0.0, 1.0);")
    lines.append("}")
    return "\n".join(lines)
""")


# ------------------------------------------------------------------ lab-42
impl("lab-42", "spu_scheduler.py", "submit", r"""
    task.status = "pending"
    self.pending_queue.append(task)
    self._try_dispatch()
""")
impl("lab-42", "spu_scheduler.py", "_try_dispatch", r"""
    # Lower priority number wins; ties broken by submission order (task_id).
    self.pending_queue.sort(key=lambda t: (t.priority, t.task_id))
    for slot in range(len(self.spe_slots)):
        if self.spe_slots[slot] is not None:
            continue
        if not self.pending_queue:
            break
        task = self.pending_queue.pop(0)
        task.assigned_spe = slot
        task.status = "running"
        self.spe_slots[slot] = task
""")
impl("lab-42", "spu_scheduler.py", "get_free_spe_count", r"""
    return sum(1 for slot in self.spe_slots if slot is None)
""")
impl("lab-42", "spu_scheduler.py", "get_running_tasks", r"""
    return [slot for slot in self.spe_slots if slot is not None]
""")
impl("lab-42", "spu_scheduler.py", "start_dma", r"""
    for task in self.spe_slots:
        if task is not None and task.task_id == task_id:
            if task.status != "running":
                raise ValueError(
                    f"Task {task_id} is '{task.status}', expected 'running'"
                )
            task.status = "waiting_dma"
            return
    raise ValueError(f"Task {task_id} is not assigned to an SPE")
""")
impl("lab-42", "spu_scheduler.py", "complete_dma", r"""
    for slot, task in enumerate(self.spe_slots):
        if task is not None and task.task_id == task_id:
            if task.status != "waiting_dma":
                raise ValueError(
                    f"Task {task_id} is '{task.status}', expected 'waiting_dma'"
                )
            task.status = "completed"
            task.assigned_spe = None
            self.spe_slots[slot] = None
            self.completed.append(task)
            self._try_dispatch()
            return
    raise ValueError(f"Task {task_id} is not assigned to an SPE")
""")
impl("lab-42", "spu_scheduler.py", "complete_task", r"""
    for slot, task in enumerate(self.spe_slots):
        if task is not None and task.task_id == task_id:
            if task.status != "running":
                raise ValueError(
                    f"Task {task_id} is '{task.status}', expected 'running'"
                )
            task.status = "completed"
            task.assigned_spe = None
            self.spe_slots[slot] = None
            self.completed.append(task)
            self._try_dispatch()
            return
    raise ValueError(f"Task {task_id} is not assigned to an SPE")
""")
impl("lab-42", "spu_scheduler.py", "get_task_status", r"""
    for task in self.pending_queue:
        if task.task_id == task_id:
            return task.status
    for task in self.spe_slots:
        if task is not None and task.task_id == task_id:
            return task.status
    for task in self.completed:
        if task.task_id == task_id:
            return task.status
    return None
""")
impl("lab-42", "spu_scheduler.py", "get_completed_tasks", r"""
    return self.completed
""")


# ------------------------------------------------------------------ lab-45
impl("lab-45", "interleaver.py", "run_slice", r"""
    trace = []
    while True:
        insn = cpu.current_insn()
        if insn is None:
            break

        # A SYNC yields immediately, regardless of remaining budget.
        if insn["name"] == "SYNC":
            trace.append((cpu.cpu_id, insn["name"], cpu.total_cycles))
            cpu.pc += 1
            break

        cost = insn["cycles"]
        if cpu.cycles_used + cost > budget:
            break

        cpu.pc += 1
        cpu.cycles_used += cost
        cpu.total_cycles += cost
        trace.append((cpu.cpu_id, insn["name"], cpu.total_cycles))

    return trace
""")
impl("lab-45", "interleaver.py", "interleave", r"""
    cpu_a = CpuState("A", stream_a)
    cpu_b = CpuState("B", stream_b)
    trace = []

    while not (cpu_a.finished and cpu_b.finished):
        before = len(trace)

        cpu_a.cycles_used = 0
        trace.extend(run_slice(cpu_a, budget_a))

        cpu_b.cycles_used = 0
        trace.extend(run_slice(cpu_b, budget_b))

        # Neither CPU made progress and neither is finished: the budgets are
        # too small for the next instruction, so stop rather than spin.
        if len(trace) == before:
            break

    return trace
""")


# ------------------------------------------------------------------ lab-46
impl("lab-46", "multi_arch_analyzer.py", "compute_score", r"""
    return {
        "byte_ratio": (decoded_bytes / total_bytes) if total_bytes else 0.0,
        "num_instructions": num_instructions,
        "decoded_bytes": decoded_bytes,
    }
""")
impl("lab-46", "multi_arch_analyzer.py", "try_disassemble", r"""
    md = Cs(arch, mode)
    instructions = list(md.disasm(data, 0))
    decoded_bytes = sum(insn.size for insn in instructions)
    return compute_score(decoded_bytes, len(data), len(instructions))
""")
impl("lab-46", "multi_arch_analyzer.py", "analyze", r"""
    if candidates is None:
        candidates = CANDIDATES

    results = []
    for name, arch, mode in candidates:
        score = try_disassemble(data, arch, mode)
        results.append(dict(score, name=name))

    results.sort(key=lambda r: (-r["byte_ratio"], -r["num_instructions"]))
    return results
""")
impl("lab-46", "multi_arch_analyzer.py", "best_guess", r"""
    results = analyze(data, candidates)
    return results[0] if results else None
""")
impl("lab-46", "multi_arch_analyzer.py", "rank_mock_results", r"""
    ranked = [dict(score, name=name) for name, score in results]
    ranked.sort(key=lambda r: (-r["byte_ratio"], -r["num_instructions"]))
    return ranked
""")


# ------------------------------------------------------------------ lab-50
impl("lab-50", "regression_runner.py", "load_config", r"""
    if tomllib is None:
        raise RuntimeError("TOML library not available")
    with open(path, "rb") as f:
        return tomllib.load(f)
""")
impl("lab-50", "regression_runner.py", "parse_config", r"""
    project_name = config["project"]["name"]
    tests = []
    for entry in config["tests"]:
        tests.append({
            "name": entry["name"],
            "binary": entry["binary"],
            "args": entry.get("args", []),
            "input_file": entry.get("input_file", ""),
            "expected_stdout_md5": entry.get("expected_stdout_md5", ""),
            "expected_exit_code": entry.get("expected_exit_code", 0),
        })
    return project_name, tests
""")
impl("lab-50", "regression_runner.py", "compute_md5", r"""
    return hashlib.md5(data).hexdigest()
""")
impl("lab-50", "regression_runner.py", "run_test_binary", r"""
    cmd = [binary] + list(args)
    stdin_data = None
    if input_file:
        try:
            with open(input_file, "rb") as f:
                stdin_data = f.read()
        except FileNotFoundError:
            return b"", -1

    try:
        result = subprocess.run(
            cmd, input=stdin_data, capture_output=True, timeout=timeout
        )
    except subprocess.TimeoutExpired:
        return b"", -1
    except FileNotFoundError:
        return b"", -1

    return result.stdout, result.returncode
""")
impl("lab-50", "regression_runner.py", "run_single_test", r"""
    stdout_data, exit_code = run_test_binary(
        test["binary"], test["args"], test["input_file"]
    )

    if exit_code == -1:
        return make_result(
            test["name"], "error",
            message="binary not found, or timed out",
        )

    actual_md5 = compute_md5(stdout_data)
    expected_md5 = test["expected_stdout_md5"]

    md5_match = (not expected_md5) or (actual_md5 == expected_md5)
    exit_match = exit_code == test["expected_exit_code"]

    if md5_match and exit_match:
        return make_result(
            test["name"], "pass",
            expected_md5=expected_md5, actual_md5=actual_md5,
            exit_code_match=True,
        )

    problems = []
    if not md5_match:
        problems.append(f"stdout md5 {actual_md5} != {expected_md5}")
    if not exit_match:
        problems.append(
            f"exit code {exit_code} != {test['expected_exit_code']}"
        )

    return make_result(
        test["name"], "fail",
        expected_md5=expected_md5, actual_md5=actual_md5,
        exit_code_match=exit_match,
        message="; ".join(problems),
    )
""")
impl("lab-50", "regression_runner.py", "run_all_tests", r"""
    project_name, tests = parse_config(load_config(config_path))
    results = [run_single_test(test) for test in tests]

    return {
        "project_name": project_name,
        "results": results,
        "passed": sum(1 for r in results if r["status"] == "pass"),
        "failed": sum(1 for r in results if r["status"] == "fail"),
        "errors": sum(1 for r in results if r["status"] == "error"),
    }
""")


# ------------------------------------------------------------------ lab-51
impl("lab-51", "pipeline.py", "hash_file", r"""
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()
""")
impl("lab-51", "pipeline.py", "stage_key", r"""
    parts = [stage.name, stage.version]
    # Sorted, so the same inputs in a different order give the same key.
    for path in sorted(inputs):
        parts.append(f"{path}:{hash_file(path)}")
    return hashlib.sha256("|".join(parts).encode()).hexdigest()
""")
impl("lab-51", "pipeline.py", "run", r"""
    self.ran = []
    self.skipped = []
    self._provenance = {
        "inputs": [(p, hash_file(p)) for p in inputs],
        "stages": [],
    }

    current = list(inputs)
    for stage in self.stages:
        key = stage_key(stage, current)
        cached = key in self.cache
        if cached:
            outputs = self.cache[key]
            self.skipped.append(stage.name)
        else:
            outputs = stage.func(current, self.outdir)
            self.cache[key] = outputs
            self.ran.append(stage.name)

        self._provenance["stages"].append({
            "name": stage.name,
            "version": stage.version,
            "key": key,
            "cached": cached,
            "outputs": list(outputs),
        })
        current = outputs

    return current
""")
impl("lab-51", "pipeline.py", "provenance", r"""
    return self._provenance
""")

# ------------------------------------------------------------------ lab-52
impl("lab-52", "batch.py", "run_target", r"""
    value = target
    for name, func in stages:
        try:
            value = func(value)
        except StageFailure as exc:
            return {"target": target, "category": exc.category,
                    "stage": name, "message": exc.message}
        except Timeout:
            return {"target": target, "category": "timeout",
                    "stage": name, "message": f"exceeded {timeout}s"}
        except Exception as exc:
            # An unexpected exception is itself information -- it means the
            # harness met something no stage knew how to categorise.
            return {"target": target, "category": "error",
                    "stage": name, "message": str(exc)}

    return {"target": target, "category": "ok", "stage": None, "message": ""}
""")
impl("lab-52", "batch.py", "run_batch", r"""
    return [run_target(t, stages, timeout) for t in targets]
""")
impl("lab-52", "batch.py", "summarize", r"""
    counts = {}
    for result in results:
        counts[result["category"]] = counts.get(result["category"], 0) + 1
    counts["total"] = len(results)
    return counts
""")

# ------------------------------------------------------------------ lab-54
impl("lab-54", "fallthrough.py", "ends_with_terminator", r"""
    instructions = func.get("instructions") or []
    if not instructions:
        return False
    last = instructions[-1]["mnemonic"]
    # A conditional branch is deliberately NOT a terminator: control can fall
    # through it, so a function ending in one runs off its own end.
    return last in RETURNS or last in UNCONDITIONAL_BRANCHES
""")
impl("lab-54", "fallthrough.py", "find_fallthroughs", r"""
    return [f for f in functions if not ends_with_terminator(f)]
""")
impl("lab-54", "fallthrough.py", "propose_merges", r"""
    by_addr = {f["addr"]: f for f in functions}
    merges = []
    for func in find_fallthroughs(functions):
        successor = by_addr.get(end_address(func))
        if successor is not None:
            merges.append((func["addr"], successor["addr"]))
    return sorted(merges)
""")
impl("lab-54", "fallthrough.py", "apply_merges", r"""
    by_addr = {f["addr"]: f for f in functions}
    successor_of = dict(merges)
    absorbed = set(successor_of.values())

    result = []
    for func in sorted(functions, key=lambda f: f["addr"]):
        if func["addr"] in absorbed:
            continue

        size = func["size"]
        instructions = list(func["instructions"])
        cursor = func["addr"]
        # Follow the chain: A -> B -> C becomes one function.
        while cursor in successor_of:
            nxt = by_addr[successor_of[cursor]]
            size += nxt["size"]
            instructions.extend(nxt["instructions"])
            cursor = nxt["addr"]

        result.append({"addr": func["addr"], "size": size,
                       "instructions": instructions})

    return result
""")


# ------------------------------------------------------------------ lab-53
impl("lab-53", "isagen.py", "parse_isa", r"""
    lengths = {"none": 0, "imm8": 1, "imm16": 2}
    entries = []
    seen = set()

    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        fields = [f.strip() for f in line.split("|")]
        if len(fields) != 6:
            raise ValueError(f"expected 6 fields, got {len(fields)}: {line!r}")

        opcode_s, mnemonic, operand, cls, cycles_s, semantics = fields
        opcode = int(opcode_s, 16)

        if cls not in CLASSES:
            raise ValueError(f"unknown class {cls!r} for opcode {opcode_s}")
        if operand not in lengths:
            raise ValueError(f"unknown operand kind {operand!r} for opcode {opcode_s}")
        if opcode in seen:
            raise ValueError(f"duplicate opcode {opcode_s}")
        seen.add(opcode)

        entries.append(Entry(opcode, mnemonic, operand, cls, int(cycles_s), semantics))

    return entries
""")
impl("lab-53", "isagen.py", "build_table", r"""
    table = [None] * 256
    for entry in entries:
        table[entry.opcode] = entry
    return table
""")
impl("lab-53", "isagen.py", "check_coverage", r"""
    undefined = [i for i, e in enumerate(table) if e is None]
    return {"defined": 256 - len(undefined), "undefined": undefined}
""")
impl("lab-53", "isagen.py", "emit_lifter", r"""
    lines = ["void lift(uint8_t op, cpu_t *c) {", "    switch (op) {"]
    for opcode in range(256):
        entry = table[opcode]
        if entry is None:
            continue
        lines.append(f"    case 0x{opcode:02X}: /* {entry.mnemonic} */")
        lines.append(f"        c->cycles += {entry.cycles};")
        lines.append(f"        {entry.semantics};")
        lines.append("        break;")
    lines.append("    default:")
    lines.append("        unknown_opcode(op);")
    lines.append("        break;")
    lines.append("    }")
    lines.append("}")
    return "\n".join(lines)
""")
impl("lab-53", "isagen.py", "emit_interpreter", r"""
    lines = ["def step(op, cpu):"]
    keyword = "if"
    for opcode in range(256):
        entry = table[opcode]
        if entry is None:
            continue
        lines.append(f"    {keyword} op == 0x{opcode:02X}:  # {entry.mnemonic}")
        lines.append(f"        cpu.cycles += {entry.cycles}")
        lines.append(f"        {entry.semantics}")
        keyword = "elif"
    if keyword == "if":
        # No entries at all: the function still has to be valid Python.
        lines.append("    raise ValueError(f'unknown opcode {op:#04x}')")
    else:
        lines.append("    else:")
        lines.append("        raise ValueError(f'unknown opcode {op:#04x}')")
    return "\n".join(lines)
""")

# ------------------------------------------------------------------ lab-55
impl("lab-55", "fixtures.py", "assemble", r"""
    out = bytearray()
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith(";"):
            continue

        parts = line.split()
        mnemonic = parts[0]
        if mnemonic not in OPCODES:
            raise ValueError(f"unknown mnemonic {mnemonic!r}")

        opcode, nbytes = OPCODES[mnemonic]
        operands = parts[1:]
        if nbytes == 0 and operands:
            raise ValueError(f"{mnemonic} takes no operand")
        if nbytes > 0 and not operands:
            raise ValueError(f"{mnemonic} needs an operand")

        out.append(opcode)
        if nbytes:
            value = int(operands[0], 0)
            for shift in range(nbytes):
                out.append((value >> (8 * shift)) & 0xFF)

    return bytes(out)
""")
impl("lab-55", "fixtures.py", "run_fixture", r"""
    actual = lifter(assemble(fixture.source))

    if fixture.expected is None:
        # Not a pass. An unrecorded golden is an untested fixture.
        return {"name": fixture.name, "status": "no_golden",
                "actual": actual, "diff": ""}

    if actual == fixture.expected:
        return {"name": fixture.name, "status": "pass",
                "actual": actual, "diff": ""}

    diff = "\n".join(difflib.unified_diff(
        fixture.expected.splitlines(), actual.splitlines(),
        fromfile="golden", tofile="actual", lineterm=""))
    return {"name": fixture.name, "status": "fail", "actual": actual, "diff": diff}
""")
impl("lab-55", "fixtures.py", "run_suite", r"""
    results = [run_fixture(f, lifter) for f in fixtures]
    return {
        "results": results,
        "passed": sum(1 for r in results if r["status"] == "pass"),
        "failed": sum(1 for r in results if r["status"] == "fail"),
        "no_golden": sum(1 for r in results if r["status"] == "no_golden"),
    }
""")
impl("lab-55", "fixtures.py", "regenerate", r"""
    # Deliberately returns the new goldens rather than writing them back:
    # a human reads the diff before any of this is committed.
    return {f.name: lifter(assemble(f.source)) for f in fixtures}
""")

# ------------------------------------------------------------------ lab-57
impl("lab-57", "manifest.py", "parse_manifest", r"""
    sections = {}
    current = None

    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith("[") and line.endswith("]"):
            current = line[1:-1].strip()
            sections.setdefault(current, {})
            continue

        if current is None:
            raise ManifestError(f"line {number}: key outside any section: {line!r}")
        if "=" not in line:
            raise ManifestError(f"line {number}: malformed line: {line!r}")

        key, _, value = line.partition("=")
        sections[current][key.strip()] = value.strip()

    return sections
""")
impl("lab-57", "manifest.py", "validate", r"""
    for name in manifest:
        top = name.split(".")[0]
        if top in FORBIDDEN_SECTIONS:
            raise ManifestError(
                f"section [{name}] holds derived state; it belongs in the "
                f"output directory, not the manifest")
        if top not in KNOWN_SECTIONS:
            raise ManifestError(f"unknown section [{name}]")

    project = manifest.get("project")
    if project is None:
        raise ManifestError("missing [project] section")
    if not project.get("name"):
        raise ManifestError("[project] has no name")

    return True
""")
impl("lab-57", "manifest.py", "hints", r"""
    section = manifest.get("entrypoint.functions")
    if not section:
        return []

    out = []
    for key, note in section.items():
        if not note.strip():
            raise ManifestError(
                f"hint {key} has no recorded source; a bare address cannot be "
                f"told apart from a guess six months from now")
        out.append({"addr": int(key, 16), "source": note.strip()})

    return sorted(out, key=lambda h: h["addr"])
""")
impl("lab-57", "manifest.py", "resolve_overrides", r"""
    section = manifest.get("imports")
    if not section:
        return {}

    out = {}
    for name, spec in section.items():
        fields = {}
        for item in spec.split(","):
            item = item.strip()
            if not item:
                continue
            if ":" not in item:
                raise ManifestError(f"{name}: malformed override {item!r}")
            field, _, value = item.partition(":")
            field, value = field.strip(), value.strip()
            if field == "purge":
                try:
                    value = int(value, 0)
                except ValueError:
                    raise ManifestError(f"{name}: purge must be an integer, got {value!r}")
            fields[field] = value
        out[name] = fields

    return out
""")
impl("lab-57", "manifest.py", "derived_path", r"""
    name = manifest["project"]["name"]
    return os.path.join(outdir, f"{name}.derived.json")
""")

# ------------------------------------------------------------------ lab-58
impl("lab-58", "variant.py", "load_variants", r"""
    out = []
    seen = set()
    for spec in specs:
        name = spec["name"]
        if name in seen:
            raise ValueError(f"duplicate variant name {name!r}")
        seen.add(name)
        out.append(Variant(name, spec["functions"], spec.get("hints")))
    return out
""")
impl("lab-58", "variant.py", "common_functions", r"""
    return sorted(set(a.functions) & set(b.functions))
""")
impl("lab-58", "variant.py", "compute_deltas", r"""
    return {
        name: b.functions[name] - a.functions[name]
        for name in common_functions(a, b)
    }
""")
impl("lab-58", "variant.py", "dominant_shift", r"""
    total = len(deltas)
    if total == 0:
        return {"shift": None, "count": 0, "total": 0, "coverage": 0.0}

    counts = Counter(deltas.values())
    # Most common wins; ties go to the smaller magnitude, so the report is
    # stable between runs and prefers the likelier explanation.
    shift, count = max(counts.items(), key=lambda kv: (kv[1], -abs(kv[0])))
    return {"shift": shift, "count": count, "total": total,
            "coverage": count / total}
""")
impl("lab-58", "variant.py", "port_hints", r"""
    sign = "+" if shift >= 0 else "-"
    label = f"{sign}0x{abs(shift):X}"
    return [
        {"addr": h["addr"] + shift,
         "source": f"ported {label} from {h['source']}"}
        for h in hints
    ]
""")


# ------------------------------------------------------------------ lab-61
impl("lab-61", "attribution.py", "record_draw", r"""
    if source not in SOURCES:
        raise ValueError(f"unknown draw source {source!r}")
    self.frame["draws"][source] += count
    self.session["draws"][source] += count
""")
impl("lab-61", "attribution.py", "record_dispatch", r"""
    key = "native" if native else "fallback"
    self.frame["dispatch"][key] += 1
    self.session["dispatch"][key] += 1
""")
impl("lab-61", "attribution.py", "end_frame", r"""
    snapshot = {
        "draws": dict(self.frame["draws"]),
        "dispatch": dict(self.frame["dispatch"]),
    }
    self.session["frames"] += 1
    self.frame = {"draws": {GUEST: 0, HARNESS: 0},
                  "dispatch": {"native": 0, "fallback": 0}}
    return snapshot
""")
impl("lab-61", "attribution.py", "session_summary", r"""
    draws = dict(self.session["draws"])
    dispatch = dict(self.session["dispatch"])
    total_draws = draws[GUEST] + draws[HARNESS]
    total_dispatch = dispatch["native"] + dispatch["fallback"]
    return {
        "frames": self.session["frames"],
        "draws": draws,
        "dispatch": dispatch,
        "guest_draw_ratio": (draws[GUEST] / total_draws) if total_draws else 0.0,
        "native_ratio": (dispatch["native"] / total_dispatch) if total_dispatch else 0.0,
    }
""")
impl("lab-61", "attribution.py", "honest_claim", r"""
    guest = summary["draws"][GUEST]
    harness = summary["draws"][HARNESS]
    total = guest + harness

    if total == 0:
        claim = "Nothing has been drawn."
    elif guest == 0:
        claim = (f"All {total} draws came from the harness; "
                 f"the guest has not drawn anything.")
    elif harness == 0:
        claim = f"All {total} draws came from guest code."
    else:
        pct = round(100 * guest / total)
        claim = (f"{guest} of {total} draws came from guest code "
                 f"({pct}%); the rest are harness.")

    native = summary["dispatch"]["native"]
    fallback = summary["dispatch"]["fallback"]
    dispatched = native + fallback
    if dispatched:
        if fallback == 0:
            claim += f" All {dispatched} dispatches ran native code."
        else:
            claim += f" {fallback} of {dispatched} dispatches fell back."

    return claim
""")

# ------------------------------------------------------------------ lab-62
impl("lab-62", "oracle.py", "diff_states", r"""
    return [f for f in FIELDS if getattr(a, f) != getattr(b, f)]
""")
impl("lab-62", "oracle.py", "run_differential", r"""
    # Separate states: if both implementations advanced one object, a
    # divergence could never be observed.
    state_a = State()
    state_b = State()
    steps = 0

    for step in range(limit):
        try:
            next_a = impl_a(program, step, state_a)
            next_b = impl_b(program, step, state_b)
        except StopIteration:
            break

        steps += 1
        fields = diff_states(next_a, next_b)
        if fields:
            return {"diverged": True, "step": step,
                    "expected": next_a, "actual": next_b,
                    "fields": fields, "steps_run": steps}

        state_a, state_b = next_a, next_b

    return {"diverged": False, "step": None, "expected": None,
            "actual": None, "fields": [], "steps_run": steps}
""")

# ------------------------------------------------------------------ lab-63
impl("lab-63", "bisect_lift.py", "in_range", r"""
    return lo <= addr <= hi
""")
impl("lab-63", "bisect_lift.py", "run_with_range", r"""
    return [lifted_fn(a) if in_range(a, lo, hi) else oracle_fn(a) for a in addrs]
""")
impl("lab-63", "bisect_lift.py", "bisect", r"""
    found, _log = bisect_log(addrs, test)
    return found
""")
impl("lab-63", "bisect_lift.py", "bisect_log", r"""
    log = []

    def probe(lo, hi):
        good = test(lo, hi)
        log.append({"lo": lo, "hi": hi, "good": good})
        return good

    if not addrs or probe(addrs[0], addrs[-1]):
        return None, log

    # Smallest prefix [addrs[0], addrs[i]] that is bad.
    lo_i, hi_i = 0, len(addrs) - 1
    while lo_i < hi_i:
        mid = (lo_i + hi_i) // 2
        if probe(addrs[0], addrs[mid]):
            lo_i = mid + 1
        else:
            hi_i = mid

    return addrs[lo_i], log
""")

# ------------------------------------------------------------------ lab-64
impl("lab-64", "tripwire.py", "check_stack", r"""
    if before == after:
        return None
    delta = after - before
    return f"sp moved by {delta} (0x{before:X} -> 0x{after:X})"
""")
impl("lab-64", "tripwire.py", "check_callee_saved", r"""
    clobbered = []
    for reg in saved_regs:
        if reg not in before or reg not in after:
            continue          # not observed; do not invent a failure
        if before[reg] != after[reg]:
            clobbered.append(f"{reg} 0x{before[reg]:X} -> 0x{after[reg]:X}")
    return ", ".join(clobbered) if clobbered else None
""")
impl("lab-64", "tripwire.py", "check_guards", r"""
    violations = []
    for addr in sorted(guards):
        expected = guards[addr]
        if addr not in memory:
            violations.append(f"{addr}: unmapped, expected 0x{expected:02X}")
        elif memory[addr] != expected:
            violations.append(
                f"{addr}: expected 0x{expected:02X}, got 0x{memory[addr]:02X}")
    return ", ".join(violations) if violations else None
""")
impl("lab-64", "tripwire.py", "guarded_call", r"""
    before = copy.deepcopy(ctx)
    result = fn(ctx)

    for name, check in checks:
        detail = check(before, ctx)
        if detail:
            raise TripwireFailure(name, detail, call_name)

    return result
""")

# ------------------------------------------------------------------ lab-65
impl("lab-65", "insnfuzz.py", "interesting_values", r"""
    mask = MASKS[width]
    signed = 1 << (width - 1)
    values = {
        0x00, 0x01,
        0x0F, 0x10,
        signed - 1, signed, signed + 1,
        mask - 1, mask,
    }
    return sorted(v for v in values if 0 <= v <= mask)
""")
impl("lab-65", "insnfuzz.py", "gen_operand", r"""
    if rng.random() < edge_bias:
        return rng.choice(interesting_values(width))
    return rng.randint(0, MASKS[width])
""")
impl("lab-65", "insnfuzz.py", "fuzz_instruction", r"""
    rng = random.Random(seed)
    ran = 0

    for _ in range(trials):
        operands = tuple(gen_operand(rng, width, edge_bias) for _ in range(arity))
        ran += 1
        expected = impl_a(*operands)
        actual = impl_b(*operands)
        if expected != actual:
            return {"name": name, "trials": ran, "failed": True,
                    "operands": operands, "expected": expected,
                    "actual": actual, "seed": seed}

    return {"name": name, "trials": ran, "failed": False, "operands": None,
            "expected": None, "actual": None, "seed": seed}
""")
impl("lab-65", "insnfuzz.py", "shrink_case", r"""
    current = tuple(operands)
    if not still_fails(current):
        return current

    candidates = interesting_values(width)
    changed = True
    while changed:
        changed = False
        for i in range(len(current)):
            # Only ever move to a SMALLER value. Accepting any different value
            # lets the search oscillate between equally-failing cases and never
            # terminate.
            for candidate in candidates:
                if candidate >= current[i]:
                    break
                trial = current[:i] + (candidate,) + current[i + 1:]
                if still_fails(trial):
                    current = trial
                    changed = True
                    break

    return current
""")


# ------------------------------------------------------------------ lab-66
impl("lab-66", "minimise.py", "truncate", r"""
    if index < 0:
        return []
    return list(inputs[:index + 1])
""")
impl("lab-66", "minimise.py", "shrink_prefix", r"""
    current = list(inputs)
    lo, hi = 0, len(current)      # number of leading elements to drop
    best = 0
    while lo <= hi:
        mid = (lo + hi) // 2
        if mid < len(current) and still_fails(current[mid:]):
            best = mid
            lo = mid + 1
        else:
            hi = mid - 1
    return current[best:]
""")
impl("lab-66", "minimise.py", "shrink_elements", r"""
    current = list(inputs)
    for i in range(len(current) - 1, -1, -1):
        trial = current[:i] + current[i + 1:]
        if still_fails(trial):
            current = trial
    return current
""")
impl("lab-66", "minimise.py", "minimise", r"""
    original = list(inputs)
    if not still_fails(original):
        raise ValueError("input does not reproduce the failure")

    log = []
    current = original

    if failure_index is not None:
        current = truncate(current, failure_index)
        if not still_fails(current):
            raise ValueError("truncation lost the failure")
        log.append(("truncate", len(current)))

    current = shrink_prefix(current, still_fails)
    if not still_fails(current):
        raise ValueError("prefix shrink lost the failure")
    log.append(("shrink_prefix", len(current)))

    current = shrink_elements(current, still_fails)
    if not still_fails(current):
        raise ValueError("element shrink lost the failure")
    log.append(("shrink_elements", len(current)))

    return {
        "minimal": current,
        "original": len(original),
        "final": len(current),
        "ratio": (len(current) / len(original)) if original else 0.0,
        "log": log,
    }
""")

# ------------------------------------------------------------------ lab-67
impl("lab-67", "triage.py", "fingerprint", r"""
    kind = report["kind"]
    if kind not in KINDS:
        raise ValueError(f"unknown failure kind {kind!r}")
    return (report["func"], report["insn"], kind)
""")
impl("lab-67", "triage.py", "deduplicate", r"""
    groups = {}
    for report in reports:
        key = fingerprint(report)
        group = groups.get(key)
        if group is None:
            groups[key] = {
                "fingerprint": key,
                "func": report["func"],
                "insn": report["insn"],
                "kind": report["kind"],
                "count": 1,
                "examples": [report],
            }
        else:
            group["count"] += 1
            group["examples"].append(report)
    return list(groups.values())
""")
impl("lab-67", "triage.py", "rank", r"""
    annotated = []
    for group in groups:
        g = dict(group)
        g["reach"] = trace_counts.get(g["func"], 0)
        annotated.append(g)

    # A quiet divergence outranks a loud crash at equal reach: nothing tells
    # you about a wrong answer.
    return sorted(annotated, key=lambda g: (
        -g["reach"],
        -g["count"],
        0 if g["kind"] == "divergence" else 1,
        g["func"],
    ))
""")
impl("lab-67", "triage.py", "triage", r"""
    groups = deduplicate(reports)
    return {
        "total": len(reports),
        "unique": len(groups),
        "groups": rank(groups, trace_counts),
    }
""")

# ------------------------------------------------------------------ lab-68
impl("lab-68", "framedrv.py", "tick", r"""
    self.cycles += cycles
    self._budget += cycles

    fired = 0
    while self._budget >= self.cycles_per_frame:
        self._budget -= self.cycles_per_frame
        self.frames += 1
        fired += 1
        if self.on_frame:
            self.on_frame()

    return fired
""")
impl("lab-68", "framedrv.py", "run_loop", r"""
    frames = 0
    for i in range(iterations):
        if body is not None:
            body(i)
        frames += clock.tick(cycles_per_iteration)
    return {"iterations": iterations, "frames": frames}
""")
impl("lab-68", "framedrv.py", "detect_impossible_speed", r"""
    if expected_cycles <= 0:
        return None
    ratio = actual_cycles / expected_cycles
    if ratio < tolerance:
        return (f"expected ~{expected_cycles} cycles, consumed {actual_cycles} "
                f"({ratio:.3f}x) -- nothing appears to be advancing time")
    return None
""")

# ------------------------------------------------------------------ lab-69
impl("lab-69", "audioclock.py", "write", r"""
    space = self.capacity - self.level
    stored = min(count, space)
    if stored < count:
        self.overruns += 1
    self.level += stored
    return stored
""")
impl("lab-69", "audioclock.py", "read", r"""
    got = min(count, self.level)
    if got < count:
        self.underruns += 1
    self.level -= got
    return got
""")
impl("lab-69", "audioclock.py", "correction", r"""
    error = fill - self.target_fill
    adjust = self.gain * error
    if adjust > self.max_correction:
        adjust = self.max_correction
    elif adjust < -self.max_correction:
        adjust = -self.max_correction
    return 1.0 + adjust
""")
impl("lab-69", "audioclock.py", "simulate", r"""
    buf = Buffer(capacity)
    buf.write(capacity // 2)      # start half full: slack in both directions

    fills = []
    for _ in range(frames):
        buf.write(int(round(produced_per_frame * (1.0 + drift))))

        rate = nominal_consumed
        if discipline is not None:
            rate = nominal_consumed * discipline.correction(buf.fill)
        buf.read(int(round(rate)))

        fills.append(buf.fill)

    return {
        "underruns": buf.underruns,
        "overruns": buf.overruns,
        "fills": fills,
        "final_fill": fills[-1] if fills else 0.0,
    }
""")

# ------------------------------------------------------------------ lab-70
impl("lab-70", "timingtest.py", "compare_content", r"""
    a_states, b_states = a.states(), b.states()
    missing = sorted(a_states - b_states)
    extra = sorted(b_states - a_states)
    return {"match": not missing and not extra,
            "missing": missing, "extra": extra}
""")
impl("lab-70", "timingtest.py", "compare_timeline", r"""
    missing = []
    mistimed = []

    for frame, state in a.observations:
        actual = b.frame_of(state)
        if actual is None:
            if state not in missing:
                missing.append(state)
            continue
        delta = actual - frame
        if abs(delta) > tolerance:
            mistimed.append({"state": state, "expected": frame,
                             "actual": actual, "delta": delta})

    mistimed.sort(key=lambda m: m["expected"])
    return {"match": not missing and not mistimed,
            "missing": sorted(missing), "mistimed": mistimed}
""")
impl("lab-70", "timingtest.py", "assert_reaches", r"""
    actual = timeline.frame_of(state)
    if actual is None:
        return f"{state!r} was never reached"
    delta = actual - frame
    if abs(delta) > tolerance:
        return (f"{state!r} expected at frame {frame}, reached at {actual} "
                f"(delta {delta:+d})")
    return None
""")


# ------------------------------------------------------------------ lab-73
impl("lab-73", "gprof.py", "resolve", r"""
    ordered = sorted(functions, key=lambda f: f[0])
    starts = [f[0] for f in ordered]
    i = bisect.bisect_right(starts, addr) - 1
    if i < 0:
        return None
    start, size, name = ordered[i]
    return name if addr < start + size else None
""")
impl("lab-73", "gprof.py", "sample", r"""
    name = resolve(addr, self.functions)
    if name is None:
        self.unresolved += 1
    else:
        self.samples.append((addr, name))
""")
impl("lab-73", "gprof.py", "profile", r"""
    total = len(self.samples) + self.unresolved
    counts = {}
    for _addr, name in self.samples:
        counts[name] = counts.get(name, 0) + 1

    rows = [{"name": n, "samples": c,
             "percent": (100.0 * c / total) if total else 0.0}
            for n, c in counts.items()]
    return sorted(rows, key=lambda r: (-r["samples"], r["name"]))
""")
impl("lab-73", "gprof.py", "detect_spin", r"""
    if not samples:
        return None

    counts = {}
    for addr, name in samples:
        counts[addr] = counts.get(addr, 0) + 1

    addr, count = max(counts.items(), key=lambda kv: (kv[1], -kv[0]))
    fraction = count / len(samples)
    if fraction <= threshold:
        return None

    name = next(n for a, n in samples if a == addr)
    return (f"0x{addr:08X} ({name}) holds {fraction * 100:.1f}% of samples "
            f"-- execution is not advancing")
""")

# ------------------------------------------------------------------ lab-74
impl("lab-74", "veclift.py", "saturate", r"""
    if signed:
        lo, hi = -(1 << (width - 1)), (1 << (width - 1)) - 1
    else:
        lo, hi = 0, (1 << width) - 1
    return lo if value < lo else hi if value > hi else value
""")
impl("lab-74", "veclift.py", "vadd_sat", r"""
    if len(a) != len(b):
        raise ValueError(f"length mismatch: {len(a)} vs {len(b)}")
    return [saturate(x + y, width, signed) for x, y in zip(a, b)]
""")
impl("lab-74", "veclift.py", "flush_denormals", r"""
    import sys
    if not enabled:
        return list(vec)

    out = []
    for v in vec:
        if v != 0.0 and math.isfinite(v) and abs(v) < sys.float_info.min:
            out.append(math.copysign(0.0, v))
        else:
            out.append(v)
    return out
""")
impl("lab-74", "veclift.py", "vmin", r"""
    if len(a) != len(b):
        raise ValueError(f"length mismatch: {len(a)} vs {len(b)}")

    out = []
    for x, y in zip(a, b):
        x_nan, y_nan = math.isnan(x), math.isnan(y)
        if x_nan and y_nan:
            out.append(x)
        elif x_nan:
            out.append(x if nan_wins else y)
        elif y_nan:
            out.append(y if nan_wins else x)
        else:
            out.append(x if x < y else y)
    return out
""")
impl("lab-74", "veclift.py", "differential", r"""
    def same(x, y):
        if isinstance(x, float) and isinstance(y, float):
            if math.isnan(x) and math.isnan(y):
                return True
        if isinstance(x, list) and isinstance(y, list):
            return len(x) == len(y) and all(same(i, j) for i, j in zip(x, y))
        return x == y

    failures = []
    for case in cases:
        expected = op_a(*case)
        actual = op_b(*case)
        if not same(expected, actual):
            failures.append({"case": case, "expected": expected, "actual": actual})

    return {"total": len(cases), "diverged": len(failures), "failures": failures}
""")

# ------------------------------------------------------------------ lab-75
impl("lab-75", "lanes.py", "mirror_index", r"""
    if not 0 <= i < count:
        raise ValueError(f"lane {i} outside [0, {count})")
    return count - 1 - i
""")
impl("lab-75", "lanes.py", "permute", r"""
    out = []
    for src in control:
        if not 0 <= src < len(vec):
            raise IndexError(f"control index {src} outside [0, {len(vec)})")
        out.append(vec[src])
    return out
""")
impl("lab-75", "lanes.py", "lift_permute_naive", r"""
    return list(control)
""")
impl("lab-75", "lanes.py", "lift_permute", r"""
    # Both the destination position and the selected source are expressed in
    # guest lane numbering, so both have to be mirrored.
    out = []
    for host_dst in range(count):
        guest_dst = mirror_index(host_dst, count)
        guest_src = control[guest_dst]
        out.append(mirror_index(guest_src, count))
    return out
""")
impl("lab-75", "lanes.py", "demonstrate_bug", r"""
    count = len(vec)
    naive = permute(vec, lift_permute_naive(control))
    correct = permute(vec, lift_permute(control, count))
    return {"naive": naive, "correct": correct, "differ": naive != correct}
""")

# ------------------------------------------------------------------ lab-76
impl("lab-76", "memladder.py", "SwitchBus.read", r"""
    for start, size, data in self.regions:
        self.comparisons += 1
        if start <= addr < start + size:
            return data[addr - start]

    if self.io_handler is not None:
        return self.io_handler(addr)
    raise IOTrap(f"unmapped address 0x{addr:X}")
""")
impl("lab-76", "memladder.py", "FlatBus.read", r"""
    self.checks += 1

    if self.io_range is not None and self.io_range[0] <= addr <= self.io_range[1]:
        if self.io_handler is not None:
            return self.io_handler(addr)
        # Returning RAM here would silently turn a hardware register into a
        # stale byte -- the exact failure Module 43 section 2 warns about.
        raise IOTrap(f"memory-mapped access at 0x{addr:X} with no handler")

    return self.memory[addr - self.base]
""")
impl("lab-76", "memladder.py", "classify_static", r"""
    if addr is None:
        return "dynamic"
    if io_range is not None and io_range[0] <= addr <= io_range[1]:
        return "io"
    return "fast"
""")
impl("lab-76", "memladder.py", "benchmark", r"""
    for addr in accesses:
        bus.read(addr)

    work = getattr(bus, "comparisons", None)
    if work is None:
        work = getattr(bus, "checks", 0)

    count = len(accesses)
    return {"accesses": count, "work": work,
            "work_per_access": (work / count) if count else 0.0}
""")

# ------------------------------------------------------------------ lab-77
impl("lab-77", "endian.py", "swap32", r"""
    return (((value & 0x000000FF) << 24) |
            ((value & 0x0000FF00) << 8) |
            ((value & 0x00FF0000) >> 8) |
            ((value & 0xFF000000) >> 24))
""")
impl("lab-77", "endian.py", "SwapOnAccess.read8", r"""
    return self.memory[addr]
""")
impl("lab-77", "endian.py", "SwapOnAccess.write32", r"""
    self.swaps += 1
    stored = swap32(value)
    self.memory[addr:addr + 4] = stored.to_bytes(4, "little")
""")
impl("lab-77", "endian.py", "SwapOnAccess.read32", r"""
    self.swaps += 1
    stored = int.from_bytes(self.memory[addr:addr + 4], "little")
    return swap32(stored)
""")
impl("lab-77", "endian.py", "SwappedStorage.read32", r"""
    # Already stored in host order: no swap, no XOR. This is the whole point.
    return int.from_bytes(self.memory[addr:addr + 4], "little")
""")
impl("lab-77", "endian.py", "SwappedStorage.read8", r"""
    self.xors += 1
    return self.memory[byte_xor(addr)]
""")
impl("lab-77", "endian.py", "SwappedStorage.write32", r"""
    self.memory[addr:addr + 4] = value.to_bytes(4, "little")
""")
impl("lab-77", "endian.py", "compare", r"""
    a = SwapOnAccess(size)
    b = SwappedStorage(size)
    mismatches = []

    for i, (op, addr, value) in enumerate(workload):
        if op == "w32":
            a.write32(addr, value)
            b.write32(addr, value)
        elif op == "r32":
            x, y = a.read32(addr), b.read32(addr)
            if x != y:
                mismatches.append((i, op, addr, x, y))
        elif op == "r8":
            x, y = a.read8(addr), b.read8(addr)
            if x != y:
                mismatches.append((i, op, addr, x, y))
        else:
            raise ValueError(f"unknown op {op!r}")

    return {"agree": not mismatches, "mismatches": mismatches,
            "swap_cost": a.swaps, "storage_cost": b.xors}
""")

# ------------------------------------------------------------------ lab-78
impl("lab-78", "prune.py", "reachable", r"""
    seen = set()
    worklist = [entry]
    while worklist:
        name = worklist.pop()
        if name in seen:
            continue
        seen.add(name)
        for callee in call_graph.get(name, []):
            if callee not in seen:
                worklist.append(callee)
    return seen
""")
impl("lab-78", "prune.py", "observed", r"""
    return set(trace)
""")
impl("lab-78", "prune.py", "live_set", r"""
    return reachable(entry, call_graph) | observed(trace)
""")
impl("lab-78", "prune.py", "plan", r"""
    names = list(all_functions)
    keep = sorted(n for n in names if n in live)
    trap = sorted(n for n in names if n not in live)
    total = len(names)
    return {"keep": keep, "trap": trap, "kept": len(keep),
            "trapped": len(trap),
            "reduction": (len(trap) / total) if total else 0.0}
""")
impl("lab-78", "prune.py", "call", r"""
    if name not in self.trapped:
        raise KeyError(f"{name!r} was never trapped")
    self.fired[name] = self.fired.get(name, 0) + 1
    return self.fired[name]
""")
impl("lab-78", "prune.py", "report", r"""
    return sorted(self.fired.items(), key=lambda kv: (-kv[1], kv[0]))
""")

# ------------------------------------------------------------------ lab-79
impl("lab-79", "ordering.py", "call_counts", r"""
    return dict(Counter(trace))
""")
impl("lab-79", "ordering.py", "order_by_heat", r"""
    called = [n for n in all_functions if counts.get(n, 0) > 0]
    uncalled = [n for n in all_functions if counts.get(n, 0) == 0]
    called.sort(key=lambda n: (-counts[n], n))
    uncalled.sort()
    return called + uncalled
""")
impl("lab-79", "ordering.py", "layout", r"""
    addresses = {}
    cursor = 0
    for name in order:
        addresses[name] = cursor
        cursor += sizes[name]
    return addresses
""")
impl("lab-79", "ordering.py", "estimate_cache_misses", r"""
    lines = set()
    for name in trace:
        start = addresses[name]
        end = start + sizes[name]
        for line in range(start // line_size, (end - 1) // line_size + 1):
            lines.add(line)
    return len(lines)
""")
impl("lab-79", "ordering.py", "compare_layouts", r"""
    counts = call_counts(trace)
    heat = order_by_heat(counts, all_functions)

    original_lines = estimate_cache_misses(
        trace, layout(original_order, sizes), sizes, line_size)
    ordered_lines = estimate_cache_misses(
        trace, layout(heat, sizes), sizes, line_size)

    improvement = 0.0
    if original_lines and ordered_lines < original_lines:
        improvement = (original_lines - ordered_lines) / original_lines

    return {"original_lines": original_lines, "ordered_lines": ordered_lines,
            "improvement": improvement, "order": heat}
""")


# ------------------------------------------------------------------ lab-87
impl("lab-87", "wholerom.py", "emit_label", r"""
    return f"L_{addr:04X}"
""")
impl("lab-87", "wholerom.py", "emit_instruction", r"""
    lines = [f"    c->cycles += {insn['cycles']};"]
    kind = insn["kind"]

    if kind == "jump":
        lines.append(f"    goto {emit_label(insn['target'])};")
    elif kind == "call":
        lines.append(f"    push_return(0x{insn['addr'] + 1:04X});")
        lines.append(f"    goto {emit_label(insn['target'])};")
    elif kind == "return":
        lines.append("    goto *pop_return();")

    return lines
""")
impl("lab-87", "wholerom.py", "emit_rom", r"""
    out = ["void run_rom(cpu_t *c) {"]
    for insn in program:
        out.append(f"{emit_label(insn['addr'])}: /* {insn['mnemonic']} */")
        out.extend(emit_instruction(insn))
    out.append("}")
    return "\n".join(out)
""")
impl("lab-87", "wholerom.py", "count_gotos", r"""
    return source.count("goto")
""")
impl("lab-87", "wholerom.py", "reachable_labels", r"""
    targets = {i["target"] for i in program
               if i["kind"] in ("jump", "call") and i["target"] is not None}
    return sorted(targets)
""")

# ------------------------------------------------------------------ lab-88
impl("lab-88", "paging.py", "resolve_targets", r"""
    out = []
    page = None

    for insn in program:
        resolved = dict(insn)
        if insn["op"] == "PSET":
            page = insn["page"]
            resolved["target"] = None
        elif insn["op"] in ("JP", "CALL"):
            if page is None:
                raise PagingError(
                    f"transfer at 0x{insn['addr']:04X} with no page latched")
            resolved["target"] = (page << 8) | insn["offset"]
        else:
            resolved["target"] = None
        out.append(resolved)

    return out
""")
impl("lab-88", "paging.py", "check_pset_invariant", r"""
    violations = []
    for i, insn in enumerate(program):
        if insn["op"] != "PSET":
            continue
        if i + 1 >= len(program) or program[i + 1]["op"] not in ("JP", "CALL"):
            violations.append(insn["addr"])
    return sorted(violations)
""")
impl("lab-88", "paging.py", "emit", r"""
    violations = check_pset_invariant(program)
    if violations:
        raise PagingError(
            "PSET not followed by a transfer at: "
            + ", ".join(f"0x{a:04X}" for a in violations))

    resolved = resolve_targets(program)
    lines = []
    for insn in resolved:
        lines.append(f"L_{insn['addr']:04X}: /* {insn['op']} */")
        if insn["op"] == "PSET":
            # Folded into the following transfer; nothing to emit.
            lines.append(f"    /* PSET 0x{insn['page']:02X} folded */")
        elif insn["op"] in ("JP", "CALL"):
            lines.append(f"    goto L_{insn['target']:04X};")
    return lines
""")

# ------------------------------------------------------------------ lab-89
impl("lab-89", "indoracle.py", "validate_state", r"""
    bad = []
    for field, width in REGISTER_WIDTHS.items():
        if field not in state:
            continue
        value = state[field]
        if not 0 <= value < (1 << width):
            bad.append((field, value, width))
    return sorted(bad, key=lambda t: t[0])
""")
impl("lab-89", "indoracle.py", "compare_step", r"""
    fields = sorted({f for f in set(a) | set(b) if a.get(f) != b.get(f)})

    if not fields:
        return {"agree": True, "fields": [], "kind": None, "detail": ""}

    impossible = validate_state(a) + validate_state(b)
    if impossible:
        detail = "; ".join(
            f"{f}=0x{v:X} cannot fit in {w} bits" for f, v, w in impossible)
        return {"agree": False, "fields": fields,
                "kind": "impossible_value", "detail": detail}

    if all(f in TIMING_FIELDS for f in fields):
        return {"agree": False, "fields": fields, "kind": "timing",
                "detail": "only timing-derived fields differ"}

    detail = "; ".join(f"{f}: {a.get(f)!r} vs {b.get(f)!r}" for f in fields)
    return {"agree": False, "fields": fields, "kind": "target_bug",
            "detail": detail}
""")
impl("lab-89", "indoracle.py", "run_validation", r"""
    ran = 0
    for i in range(limit):
        try:
            a = oracle_fn(steps, i)
            b = target_fn(steps, i)
        except StopIteration:
            break

        ran += 1
        result = compare_step(a, b)
        if not result["agree"]:
            return {"diverged": True, "step": i, "kind": result["kind"],
                    "fields": result["fields"], "detail": result["detail"],
                    "steps_run": ran}

    return {"diverged": False, "step": None, "kind": None,
            "fields": [], "detail": "", "steps_run": ran}
""")

# ------------------------------------------------------------------ lab-90
impl("lab-90", "bytecheck.py", "relocation_density", r"""
    code = binary.get("code_bytes", 0)
    if code <= 0:
        return 0.0
    return binary.get("relocations", 0) / (code / 1024.0)
""")
impl("lab-90", "bytecheck.py", "is_runtime_only", r"""
    system = SYSTEM_MODULES if system_modules is None else system_modules
    system = {m.upper().split(".")[0] for m in system}

    names = {m.upper().split(".")[0] for m in binary.get("imports", [])}
    if not names:
        return False        # no imports at all is a different animal
    return not (names & system)
""")
impl("lab-90", "bytecheck.py", "classify", r"""
    density = relocation_density(binary)
    reasons = []

    runtime_only = is_runtime_only(binary)
    if runtime_only:
        imports = ", ".join(binary.get("imports", [])) or "(none)"
        reasons.append(f"imports only {imports} -- no system modules, so the "
                       f"runtime is doing the work")
    else:
        reasons.append("imports system modules, as native code must")

    if reference is not None:
        ref_density = relocation_density(reference)
        threshold = ref_density * 0.1
        low = density < threshold
        reasons.append(
            f"relocation density {density:.2f}/KB versus "
            f"{ref_density:.2f}/KB for {reference.get('name', 'reference')}")
    else:
        low = density < 1.0
        reasons.append(f"relocation density {density:.2f}/KB "
                       f"(below 1.0 suggests the segments are not code)")

    if runtime_only and low:
        verdict = "bytecode"
    elif not runtime_only and not low:
        verdict = "native"
    else:
        verdict = "uncertain"
        reasons.append("only one signal fired -- a hint, not a finding")

    return {"name": binary.get("name", "?"), "verdict": verdict,
            "density": density, "reasons": reasons}
""")

# ------------------------------------------------------------------ lab-91
impl("lab-91", "stacklocals.py", "compute_depths", r"""
    depths = {}
    worklist = [(0, 0)]

    while worklist:
        pc, depth = worklist.pop()
        if pc >= len(program):
            continue

        known = depths.get(pc)
        if known is not None:
            if known != depth:
                raise StackError(
                    f"pc {pc} reached at depth {known} and {depth}")
            continue
        depths[pc] = depth

        insn = program[pc]
        after = depth - insn["pops"] + insn["pushes"]

        if insn["op"] == "return":
            continue
        if insn["op"] in ("branch", "branch_if") and insn["target"] is not None:
            worklist.append((insn["target"], after))
        if insn["op"] != "branch":
            worklist.append((pc + 1, after))

    return depths
""")
impl("lab-91", "stacklocals.py", "verify_balance", r"""
    problems = []
    try:
        depths = compute_depths(program)
    except StackError as exc:
        return [f"conflicting depths: {exc}"]

    for pc, depth in sorted(depths.items()):
        insn = program[pc]
        if depth - insn["pops"] < 0:
            problems.append(
                f"pc {pc} ({insn['op']}) pops {insn['pops']} at depth {depth} "
                f"-- stack would go negative")
        if insn["op"] == "return" and depth != 0:
            problems.append(f"pc {pc} return at depth {depth}, expected 0")

    return problems
""")
impl("lab-91", "stacklocals.py", "emit", r"""
    lines = [f"    value_t s[{max(max_depth(depths), 1)}];"]

    for pc in sorted(depths):
        insn = program[pc]
        depth = depths[pc]
        lines.append(f"    /* {pc:4d}: {insn['op']} */")
        if insn["pushes"]:
            slot = depth - insn["pops"]
            lines.append(f"    s[{slot}] = op_{insn['op'].replace('-', '_')}();")
        else:
            lines.append(f"    op_{insn['op'].replace('-', '_')}();")

    return lines
""")

# ------------------------------------------------------------------ lab-92
impl("lab-92", "encoding.py", "decode_one", r"""
    if pos >= len(data):
        raise DecodeError(f"read past end at {pos}")

    byte = data[pos]
    opcode = byte >> 3
    a = byte & 7

    if a == ESCAPE:
        if pos + 3 > len(data):
            raise DecodeError(f"truncated escape at {pos}")
        b = (data[pos + 1] << 8) | data[pos + 2]
        length = 3
    else:
        b = a
        length = 1

    if opcode not in OPCODES:
        raise DecodeError(f"unknown opcode {opcode} at {pos}")

    if opcode == 0:
        if b not in SIMPLE_OPS:
            raise DecodeError(f"unknown simple op {b} at {pos}")
        name = SIMPLE_OPS[b]
    else:
        name = OPCODES[opcode]

    return {"pos": pos, "opcode": opcode, "name": name, "b": b, "length": length}
""")
impl("lab-92", "encoding.py", "decode_all", r"""
    out = []
    pos = 0
    while pos < len(data):
        insn = decode_one(data, pos)
        out.append(insn)
        pos += insn["length"]
    return out
""")
impl("lab-92", "encoding.py", "decode_naive", r"""
    # Deliberately wrong: one byte per instruction, and it never complains.
    out = []
    for pos, byte in enumerate(data):
        opcode = byte >> 3
        b = byte & 7
        if opcode == 0:
            name = SIMPLE_OPS.get(b, "?")
        else:
            name = OPCODES.get(opcode, "?")
        out.append({"pos": pos, "opcode": opcode, "name": name,
                    "b": b, "length": 1})
    return out
""")
impl("lab-92", "encoding.py", "corpus_check", r"""
    affected = []
    errors = []
    escapes = 0

    for name in sorted(programs):
        data = programs[name]
        try:
            correct = decode_all(data)
        except DecodeError:
            errors.append(name)
            continue

        escapes += sum(1 for i in correct if i["length"] == 3)

        naive = decode_naive(data)
        if [i["name"] for i in naive] != [i["name"] for i in correct]:
            affected.append(name)

    return {"total": len(programs), "disagree": len(affected),
            "escapes": escapes, "affected": sorted(affected),
            "errors": sorted(errors)}
""")


# ------------------------------------------------------------------ lab-93
impl("lab-93", "addrspace.py", "add", r"""
    end = base + size
    for other_base, other_size, other_name in self.images:
        if base < other_base + other_size and other_base < end:
            raise Overlap(
                f"{name} [0x{base:X}, 0x{end:X}) overlaps {other_name}")
    self.images.append((base, size, name))
    self.images.sort()
""")
impl("lab-93", "addrspace.py", "contains", r"""
    return any(base <= addr < base + size for base, size, _ in self.images)
""")
impl("lab-93", "addrspace.py", "image_of", r"""
    for base, size, name in self.images:
        if base <= addr < base + size:
            return name
    return None
""")
impl("lab-93", "addrspace.py", "analyse", r"""
    outside = []
    resolved = 0
    for t in transfers:
        if space.contains(t["target"]):
            resolved += 1
        else:
            outside.append(t["target"])
    return {"total": len(transfers), "resolved": resolved,
            "unresolved": len(outside), "outside": sorted(outside)}
""")
impl("lab-93", "addrspace.py", "compare_assembly", r"""
    combined = AddressSpace()
    for name, base, size in images:
        combined.add(name, base, size)

    separate = 0
    for name, base, size in images:
        solo = AddressSpace()
        solo.add(name, base, size)
        for t in transfers:
            if solo.contains(t["site"]) and not solo.contains(t["target"]):
                separate += 1

    combined_unresolved = analyse(transfers, combined)["unresolved"]
    return {
        "separate": separate,
        "combined": combined_unresolved,
        "recovered": separate - combined_unresolved,
        "ratio": (combined_unresolved / separate) if separate else 0.0,
    }
""")

# ------------------------------------------------------------------ lab-94
impl("lab-94", "classify.py", "find_definition", r"""
    for i in range(site_index - 1, -1, -1):
        if block[i].get("dst") == register:
            return block[i]
    return None
""")
impl("lab-94", "classify.py", "classify_site", r"""
    register = block[site_index].get("reg")
    definition = find_definition(block, site_index, register)
    if definition is None or definition.get("mode") is None:
        return UNKNOWN
    return definition["mode"]
""")
impl("lab-94", "classify.py", "classify_all", r"""
    groups = {}
    for block, index in sites:
        mechanism = classify_site(block, index)
        groups[mechanism] = groups.get(mechanism, 0) + 1
    return groups
""")
impl("lab-94", "classify.py", "report", r"""
    rows = [{"mechanism": m, "count": c, "means": MECHANISMS.get(m, m)}
            for m, c in groups.items()]
    return sorted(rows, key=lambda r: (-r["count"], r["mechanism"]))
""")

# ------------------------------------------------------------------ lab-95
impl("lab-95", "harvard.py", "fetch", r"""
    if not 0 <= addr < len(self.rom):
        raise SpaceError(f"ROM fetch at 0x{addr:X} is outside the space")
    return self.rom[addr]
""")
impl("lab-95", "harvard.py", "ldc", r"""
    if not 0 <= addr < len(self.rom):
        raise SpaceError(f"LDC at 0x{addr:X} is outside ROM")
    return self.rom[addr]
""")
impl("lab-95", "harvard.py", "load", r"""
    if not 0 <= addr < len(self.ram):
        raise SpaceError(f"RAM load at 0x{addr:X} is outside the space")
    handler = self.io_handlers.get(addr)
    if handler is not None:
        return handler(None)
    return self.ram[addr]
""")
impl("lab-95", "harvard.py", "store", r"""
    if not 0 <= addr < len(self.ram):
        raise SpaceError(f"RAM store at 0x{addr:X} is outside the space")
    handler = self.io_handlers.get(addr)
    if handler is not None:
        handler(value)
        return
    self.ram[addr] = value
""")
impl("lab-95", "harvard.py", "detect_conflation", r"""
    addr = min(len(memory.rom), len(memory.ram)) // 2

    memory.rom[addr] = 0xA5
    memory.store(addr, 0x5A)

    from_rom = memory.ldc(addr)
    from_ram = memory.load(addr)

    if from_rom == from_ram:
        return (f"address 0x{addr:X} reads 0x{from_rom:02X} from both spaces "
                f"-- ROM and RAM are the same storage")
    if from_rom != 0xA5:
        return f"ROM at 0x{addr:X} was overwritten by a RAM store"
    return None
""")

# ------------------------------------------------------------------ lab-83
impl("lab-83", "verify.py", "hash_data", r"""
    return hashlib.sha256(data).hexdigest()
""")
impl("lab-83", "verify.py", "identify", r"""
    return known.get(hash_data(data))
""")
impl("lab-83", "verify.py", "check", r"""
    digest = hash_data(data)
    found = known.get(digest)
    short = digest[:16]

    if found == target:
        verdict = "match"
        message = f"Input identified as {found} (SHA-256 {short}...)."
    elif found is not None:
        verdict = "known_mismatch"
        message = (
            f"Expected: {target}\n"
            f"Found:    {found} (SHA-256 {short}...)\n"
            f"This project targets {target}. {found} has different function "
            f"addresses and the manifest hints will not apply. Proceeding "
            f"anyway -- expect unresolved calls.")
    else:
        verdict = "unknown"
        message = (
            f"Unrecognised input (SHA-256 {short}...). This project targets "
            f"{target}. Proceeding anyway; if it works, please report this "
            f"hash so it can be added.")

    return {"verdict": verdict, "found": found, "digest": digest,
            "message": message}
""")
impl("lab-83", "verify.py", "provenance", r"""
    result = check(data, known, target)
    return {
        "digest": result["digest"],
        "identified": result["found"],
        "target": target,
        "verdict": result["verdict"],
        "tools": sorted(f"{name}={version}" for name, version in tool_versions.items()),
    }
""")

# ------------------------------------------------------------------ lab-99
impl("lab-99", "hybrid.py", "dispatch", r"""
    entry = self.registry.get(addr)

    if entry is not None:
        func, instructions = entry
        try:
            func()
        except Exception:
            # Exactly what the real implementations do: roll back and let the
            # fallback cover it. The counter is the only trace it leaves.
            self.crashes += 1
        else:
            self.native_calls += 1
            self.native_instructions += instructions
            return instructions

    if self.fallback is None:
        raise RuntimeError(f"nothing registered at 0x{addr:X} and no fallback")

    instructions = self.fallback(addr)
    self.fallback_calls += 1
    self.fallback_instructions += instructions
    return instructions
""")
impl("lab-99", "hybrid.py", "crossover", r"""
    total = self.native_instructions + self.fallback_instructions
    return (self.native_instructions / total) if total else 0.0
""")
impl("lab-99", "hybrid.py", "honest_summary", r"""
    executed = stats["native_instructions"] + stats["fallback_instructions"]
    registered = stats["registered"]
    crossover = stats["crossover"]

    if executed == 0:
        claim = "Nothing has executed."
    elif crossover == 0.0:
        claim = (f"{registered} functions registered, but 0% of executed "
                 f"instructions ran native -- the fallback is running this "
                 f"program.")
    elif crossover == 1.0:
        claim = (f"All executed instructions ran native code "
                 f"({registered} functions registered).")
    else:
        claim = (f"{crossover * 100:.1f}% of executed instructions ran native "
                 f"({registered} functions registered).")

    if stats["crashes"]:
        claim += (f" {stats['crashes']} recompiled function(s) crashed and "
                  f"fell back.")

    return claim
""")

# ------------------------------------------------------------------ lab-100
impl("lab-100", "migration.py", "plan_migration", r"""
    return sorted(profile, key=lambda n: (-profile[n], n))
""")
impl("lab-100", "migration.py", "simulate_migration", r"""
    total = sum(profile.values())
    curve = [0.0]
    ported = 0
    for name in order:
        ported += profile.get(name, 0)
        curve.append((ported / total) if total else 0.0)
    return curve
""")
impl("lab-100", "migration.py", "steps_to_reach", r"""
    for i, value in enumerate(curve):
        if value >= target:
            return i
    return None
""")
impl("lab-100", "migration.py", "verify_runnable", r"""
    covered = set(ported) | set(emulated)
    return sorted(n for n in all_functions if n not in covered)
""")


# ----------------------------------------------------------------- lab-103
impl("lab-103", "symimport.py", "parse_symbols", r"""
    symbols = []
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        fields = line.split()
        if len(fields) != 3:
            raise ValueError(
                f"line {lineno}: expected 3 fields, got {len(fields)}: {line!r}")
        addr, name, size = fields
        try:
            symbols.append({"addr": int(addr, 16), "name": name,
                            "size": int(size, 16)})
        except ValueError:
            raise ValueError(f"line {lineno}: bad hex in {line!r}")
    return symbols
""")
impl("lab-103", "symimport.py", "validate_symbols", r"""
    problems = []
    seen = {}
    for sym in symbols:
        if sym["size"] <= 0:
            problems.append(f"{sym['name']}: size is {sym['size']}")
        if sym["addr"] in seen:
            problems.append(
                f"{sym['name']}: duplicate address 0x{sym['addr']:X} "
                f"(also {seen[sym['addr']]})")
        else:
            seen[sym["addr"]] = sym["name"]

    ordered = sorted(symbols, key=lambda s: s["addr"])
    for prev, cur in zip(ordered, ordered[1:]):
        end = prev["addr"] + prev["size"]
        if end > cur["addr"]:
            problems.append(
                f"{prev['name']} overlaps {cur['name']}: ends 0x{end:X}, "
                f"next starts 0x{cur['addr']:X}")
    return problems
""")
impl("lab-103", "symimport.py", "to_function_set", r"""
    functions = {}
    for sym in symbols:
        if sym["name"] in functions:
            raise ValueError(f"duplicate symbol name {sym['name']!r}")
        functions[sym["name"]] = {"addr": sym["addr"], "size": sym["size"]}
    return {"source_commit": commit, "count": len(functions),
            "functions": functions}
""")
impl("lab-103", "symimport.py", "diff_imports", r"""
    old_funcs = old["functions"] if old else {}
    new_funcs = new["functions"]

    moved, resized = [], []
    for name in sorted(set(old_funcs) & set(new_funcs)):
        before, after = old_funcs[name], new_funcs[name]
        if before["addr"] != after["addr"]:
            moved.append({"name": name, "from": before["addr"],
                          "to": after["addr"]})
        if before["size"] != after["size"]:
            resized.append({"name": name, "from": before["size"],
                            "to": after["size"]})

    return {
        "added": sorted(set(new_funcs) - set(old_funcs)),
        "removed": sorted(set(old_funcs) - set(new_funcs)),
        "moved": moved,
        "resized": resized,
        "from_commit": old["source_commit"] if old else None,
        "to_commit": new["source_commit"],
    }
""")

# ----------------------------------------------------------------- lab-104
impl("lab-104", "decomporacle.py", "compare_function", r"""
    failures = []
    try:
        for case in cases:
            expected = decomp_fn(*case)
            actual = recomp_fn(*case)
            if expected != actual:
                failures.append({"case": case, "expected": expected,
                                 "actual": actual})
    except Exception as exc:
        return {"name": name, "cases": len(cases), "status": "error",
                "failures": failures, "message": str(exc)}

    return {"name": name, "cases": len(cases),
            "status": "fail" if failures else "pass",
            "failures": failures, "message": ""}
""")
impl("lab-104", "decomporacle.py", "run_suite", r"""
    results, missing = [], []
    for name in sorted(suite):
        if name not in decomp or name not in recomp:
            missing.append(name)
            continue
        results.append(compare_function(name, suite[name], decomp[name],
                                        recomp[name]))

    return {
        "results": results,
        "passed": sum(1 for r in results if r["status"] == "pass"),
        "failed": sum(1 for r in results if r["status"] == "fail"),
        "errors": sum(1 for r in results if r["status"] == "error"),
        "missing": missing,
    }
""")
impl("lab-104", "decomporacle.py", "coverage", r"""
    tested = {r["name"] for r in suite_result["results"]}
    total = len(all_functions)
    return {
        "tested": len(tested),
        "total": total,
        "fraction": (len(tested) / total) if total else 0.0,
        "untested": sorted(n for n in all_functions if n not in tested),
    }
""")
impl("lab-104", "decomporacle.py", "honest_report", r"""
    bad = suite_result["failed"] + suite_result["errors"]
    if bad:
        return f"{bad} function(s) diverge from the decomp."

    tested = cov["tested"]
    pct = f"{cov['fraction'] * 100:.1f}%"
    if cov["fraction"] >= 0.8:
        return f"All {tested} tested functions match the decomp ({pct} coverage)."
    return (f"All {tested} tested functions match, but only {pct} of the "
            f"binary is covered -- this is not validation of the build.")
""")

# ----------------------------------------------------------------- lab-106
impl("lab-106", "proposecheck.py", "check_alignment", r"""
    addr = proposal["addr"]
    if addr % alignment:
        return f"0x{addr:X} is not {alignment}-byte aligned"
    return None
""")
impl("lab-106", "proposecheck.py", "check_in_range", r"""
    lo, hi = code_range
    addr = proposal["addr"]
    if not lo <= addr <= hi:
        return f"0x{addr:X} is outside code range [0x{lo:X}, 0x{hi:X}]"
    return None
""")
impl("lab-106", "proposecheck.py", "check_not_mid_function", r"""
    addr = proposal["addr"]
    for start, size in known:
        if start < addr < start + size:
            return (f"0x{addr:X} is inside known function at 0x{start:X} "
                    f"(+0x{addr - start:X}); hinting it would split "
                    f"that function")
    return None
""")
impl("lab-106", "proposecheck.py", "check_observed", r"""
    addr = proposal["addr"]
    if addr in set(trace):
        return None
    return f"0x{addr:X} was never reached during execution"
""")
impl("lab-106", "proposecheck.py", "evaluate", r"""
    accepted, rejected = [], []
    by_source = {}
    observed = 0

    for proposal in proposals:
        source = proposal.get("source", "unknown")
        counts = by_source.setdefault(source, {"accepted": 0, "rejected": 0})

        reasons = [reason for reason in (
            check_alignment(proposal, alignment),
            check_in_range(proposal, code_range),
            check_not_mid_function(proposal, known),
        ) if reason is not None]

        if reasons:
            rejected.append({"addr": proposal["addr"], "source": source,
                             "reasons": reasons})
            counts["rejected"] += 1
        else:
            accepted.append(proposal)
            counts["accepted"] += 1
            if check_observed(proposal, trace) is None:
                observed += 1

    return {
        "accepted": sorted(accepted, key=lambda p: p["addr"]),
        "rejected": rejected,
        "observed": observed,
        "by_source": by_source,
    }
""")

# ----------------------------------------------------------------- lab-107
impl("lab-107", "eqgate.py", "Gate.submit", r"""
    for case in self.all_cases():
        expected = self.reference(*case)
        try:
            actual = candidate(*case)
        except Exception as exc:
            self.rejected += 1
            self.reasons["raised"] = self.reasons.get("raised", 0) + 1
            return {"accepted": False, "reason": "raised",
                    "detail": f"raised on {case}: {exc}", "case": case}

        if actual != expected:
            self.rejected += 1
            self.reasons["mismatch"] = self.reasons.get("mismatch", 0) + 1
            return {"accepted": False, "reason": "mismatch",
                    "detail": f"on {case}: expected {expected!r}, "
                              f"got {actual!r}",
                    "case": case}

    self.accepted += 1
    return {"accepted": True, "reason": "", "detail": "", "case": None}
""")
impl("lab-107", "eqgate.py", "Gate.stats", r"""
    submitted = self.accepted + self.rejected
    return {
        "submitted": submitted,
        "accepted": self.accepted,
        "rejected": self.rejected,
        "rate": (self.accepted / submitted) if submitted else 0.0,
        "reasons": dict(self.reasons),
    }
""")

# ----------------------------------------------------------------- lab-112
impl("lab-112", "autoreg.py", "register", r"""
    self.history.setdefault(addr, []).append(name)
    overrode = addr in self.table
    self.table[addr] = (name, func)
    return overrode
""")
impl("lab-112", "autoreg.py", "lookup", r"""
    entry = self.table.get(addr)
    return entry[1] if entry else None
""")
impl("lab-112", "autoreg.py", "name_at", r"""
    entry = self.table.get(addr)
    return entry[0] if entry else None
""")
impl("lab-112", "autoreg.py", "overrides", r"""
    return [{"addr": addr, "active": names[-1], "shadowed": names[:-1]}
            for addr, names in sorted(self.history.items()) if len(names) > 1]
""")
impl("lab-112", "autoreg.py", "emit_registration", r"""
    return (f"void {name}(void);\n"
            f"static void __attribute__((constructor)) "
            f"register_{name}(void) {{\n"
            f"    recomp_register(0x{addr:06X}, \"{name}\", {name});\n"
            f"}}")
""")

# ----------------------------------------------------------------- lab-119
impl("lab-119", "verifylift.py", "exhaustive_verify", r"""
    checked = 0
    for operands in itertools.product(range(1 << width), repeat=arity):
        for flag in flag_states:
            checked += 1
            expected = reference(*operands, flag)
            actual = candidate(*operands, flag)
            if expected != actual:
                return {"verified": False, "checked": checked,
                        "first_bad": operands + (flag,),
                        "expected": expected, "actual": actual}
    return {"verified": True, "checked": checked, "first_bad": None,
            "expected": None, "actual": None}
""")
impl("lab-119", "verifylift.py", "sampled_verify", r"""
    rng = random.Random(seed)
    top = (1 << width) - 1
    flags = list(flag_states)
    for checked in range(1, trials + 1):
        operands = tuple(rng.randint(0, top) for _ in range(arity))
        flag = rng.choice(flags)
        expected = reference(*operands, flag)
        actual = candidate(*operands, flag)
        if expected != actual:
            return {"verified": False, "checked": checked,
                    "first_bad": operands + (flag,), "expected": expected,
                    "actual": actual, "seed": seed}
    return {"verified": True, "checked": trials, "first_bad": None,
            "expected": None, "actual": None, "seed": seed}
""")
impl("lab-119", "verifylift.py", "compare_approaches", r"""
    full = exhaustive_verify(reference, candidate, width, arity)
    sample = sampled_verify(reference, candidate, width, arity, trials, seed)
    space = (1 << width) ** arity
    return {
        "exhaustive": full,
        "sampled": sample,
        "missed": sample["verified"] and not full["verified"],
        "space_size": space,
        "sampled_fraction": min(1.0, trials / space) if space else 0.0,
    }
""")

# ----------------------------------------------------------------- lab-121
impl("lab-121", "harnessval.py", "validate_harness", r"""
    baseline = bool(harness(subject))

    results, escaped, false_alarms = [], [], []
    caught = 0

    for mutation in mutations:
        detected = not bool(harness(mutation.apply(subject)))
        if mutation.should_detect:
            outcome = "caught" if detected else "escaped"
            if detected:
                caught += 1
            else:
                escaped.append(mutation.name)
        else:
            outcome = "false_alarm" if detected else "correctly_ignored"
            if detected:
                false_alarms.append(mutation.name)

        results.append({"name": mutation.name, "detected": detected,
                        "should_detect": mutation.should_detect,
                        "outcome": outcome})

    return {"baseline": baseline, "results": results, "caught": caught,
            "escaped": sorted(escaped), "false_alarms": sorted(false_alarms)}
""")


# ==========================================================================
# Machinery
# ==========================================================================

TODO_BLOCK = re.compile(
    r"(?:^[ \t]*#[^\n]*\n)*"            # the comment block (TODO + continuation lines)
    r"^[ \t]*(?:pass|raise NotImplementedError\([^\n]*\))[ \t]*\n",
    re.MULTILINE,
)


def find_function(text: str, name: str) -> tuple[int, int, str]:
    """Return (start, end, indent) of `def name(...)`'s body.

    A name of the form "ClassName.method" is scoped to that class. Two classes
    defining the same method -- two bus implementations each with `read`, say --
    would otherwise both resolve to the first one, leaving the second silently
    unpatched.
    """
    offset, limit = 0, len(text)

    if "." in name:
        cls, _, name = name.partition(".")
        cm = re.search(r"^([ \t]*)class " + re.escape(cls) + r"\b", text, re.MULTILINE)
        if not cm:
            raise SystemExit(f"class {cls!r} not found")
        offset = cm.end()
        nxt = re.search(r"^(?:class |def )", text[offset:], re.MULTILINE)
        limit = offset + nxt.start() if nxt else len(text)

    window = text[offset:limit]
    m = re.search(r"^([ \t]*)def " + re.escape(name) + r"\s*\(", window, re.MULTILINE)
    if not m:
        raise SystemExit(f"function {name!r} not found")

    indent = m.group(1)
    start = offset + m.end()

    # The body ends at the next non-blank line indented no further than the def.
    rest = text[start:]
    end = len(text)
    for line in re.finditer(r"^(?![ \t]*$)([ \t]*)\S", rest, re.MULTILINE):
        if line.start() == 0:
            continue
        if len(line.group(1)) <= len(indent):
            end = start + line.start()
            break

    return start, end, indent


def build(stub_path: pathlib.Path, impls: list[tuple[str, str]]) -> str:
    text = stub_path.read_text(encoding="utf-8")

    for func, body in impls:
        start, end, indent = find_function(text, func)
        segment = text[start:end]
        # A docstring may legitimately contain an example ending in `pass`, so
        # only accept a block that actually marks unimplemented work.
        m = None
        for candidate in TODO_BLOCK.finditer(segment):
            if "TODO" in candidate.group(0) or "NotImplementedError" in candidate.group(0):
                m = candidate
                break
        if not m:
            raise SystemExit(
                f"{stub_path.relative_to(REPO)}: no TODO block found in {func!r}.\n"
                f"The stub changed shape -- update tools/make_solutions.py."
            )
        indented = textwrap.indent(body, indent + "    ") + "\n"
        text = text[:start] + segment[:m.start()] + indented + segment[m.end():] + text[end:]

    header = (
        '"""REFERENCE SOLUTION -- generated by tools/make_solutions.py.\n'
        "\n"
        "Do not edit by hand: edit the implementation in that script and regenerate.\n"
        "Try the exercise before reading this one.\n"
        '"""\n\n'
    )
    return header + text


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="verify solutions are current instead of writing them")
    args = ap.parse_args()

    stale, written = [], 0
    for (lab_name, filename), impls in sorted(IMPLS.items()):
        stub = LABS / lab_name / filename
        if not stub.exists():
            raise SystemExit(f"missing stub: {stub.relative_to(REPO)}")

        out = LABS / lab_name / "solution" / filename
        content = build(stub, impls)

        if args.check:
            if not out.exists() or out.read_text(encoding="utf-8") != content:
                stale.append(str(out.relative_to(REPO)))
        else:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(content, encoding="utf-8", newline="\n")
            written += 1

    if args.check:
        for s in stale:
            print(f"STALE: {s}")
        print(f"{len(IMPLS) - len(stale)}/{len(IMPLS)} solution files current")
        return 1 if stale else 0

    print(f"wrote {written} solution file(s) covering {len(IMPLS)} lab module(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
