#!/usr/bin/env python3
"""Recursive-descent listing of BOOT.bin, linked at 0x00700000 (CL-BOOT-REC-113).

    python3 tools/scripts/boot_listing.py [--out DIR] [--roles FILE]

Own decoder over the raw file, independent of Ghidra: capstone with
skipdata=True (CL-TOOL-REC-127), ARM/Thumb followed through BX/BLX instead of
a fixed window (CL-BOOT-REC-117). Seeds: the reset entry 0x700000 and the
three scatter helpers named by the scatter table (scatter_base.py).

Writes into DIR (default research/phase_a_sd_analysis/artifacts/boot_2026-10-18):
  listing.txt    every reached instruction; pool values, register values known
                 from straight-line propagation, MMIO register names
  functions.txt  one line per function: entry, mode, extent, size, callers,
                 callees, MMIO registers touched, role (from --roles)
  coverage.txt   file ranges not reached as code, with what they hold
  unresolved.txt indirect branches/calls whose target the propagation missed

--roles reads a tab-separated file "0xADDR<TAB>name<TAB>role" written by hand
(default: roles.tsv in DIR); without it the role column stays empty.
"""
import argparse, json, os, struct, sys
from collections import defaultdict
import capstone
from capstone import arm

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BIN = os.path.join(ROOT, "firmware", "bin", "ZK-INKJET-NANO-BOOT.bin")
REGS = os.path.join(ROOT, "research", "findings", "n32903_registers.json")
OUT = os.path.join(ROOT, "research", "phase_a_sd_analysis", "artifacts", "boot_2026-10-18")
BASE = 0x00700000

D = open(BIN, "rb").read()
END = BASE + len(D)

CS = {}
for mode, flag in (("A", capstone.CS_MODE_ARM), ("T", capstone.CS_MODE_THUMB)):
    c = capstone.Cs(capstone.CS_ARCH_ARM, flag)
    c.detail = True
    c.skipdata = True
    CS[mode] = c

PC, LR, SP = arm.ARM_REG_PC, arm.ARM_REG_LR, arm.ARM_REG_SP


def inimg(a):
    return BASE <= a < END


def w32(a):
    return struct.unpack_from("<I", D, a - BASE)[0]


def ror(v, r):
    r &= 31
    return ((v >> r) | (v << (32 - r))) & 0xFFFFFFFF if r else v


def mmio_names():
    d = json.load(open(REGS))
    names = {}
    for e in d["entries"]:
        names.setdefault(int(e["address"], 16), e["register_name"])
    bases = {}
    for e in d["base_addresses"]:
        bases.setdefault(int(e["address"], 16), e["register_name"])
    return names, bases


MMIO, MMIO_BASE = mmio_names()


def mmio_label(a):
    if a in MMIO:
        return MMIO[a]
    if a in MMIO_BASE:
        return MMIO_BASE[a]
    if 0xB0000000 <= a <= 0xBFFFFFFF:
        best = max((b for b in MMIO_BASE if b <= a), default=None)
        if best is not None and a - best < 0x1000:
            return "%s+0x%X" % (MMIO_BASE[best], a - best)
        return "MMIO"
    return None


def decode(addr, mode):
    """One instruction at addr, or None if it does not decode."""
    n = 4 if mode == "A" else 4  # Thumb BL pairs are 4 bytes; capstone takes what it needs
    off = addr - BASE
    for ins in CS[mode].disasm(D[off:off + n], addr, 1):
        if ins.id == 0:  # skipdata
            return None
        return ins
    return None


def reg_name(r):
    return CS["A"].reg_name(r)


class Insn:
    __slots__ = ("addr", "mode", "size", "mn", "ops", "raw", "note", "func", "ins")


def pool_load(ins, mode):
    """(pool address, value) if this is a PC-relative literal load, else None."""
    if mode == "A":
        x = w32(ins.address)
        # LDR (imm), Rn = PC, I = 0, L = 1, B = 0: cond 010P U0W1 1111 Rd imm12
        if (x & 0x0E5F0000) == 0x041F0000 and (x >> 28) != 0xF:
            imm = x & 0xFFF
            base = ins.address + 8
            pa = base + imm if (x >> 23) & 1 else base - imm
            return pa, (w32(pa) if inimg(pa) and pa + 4 <= END else None)
    else:
        h = struct.unpack_from("<H", D, ins.address - BASE)[0]
        if (h & 0xF800) == 0x4800:
            pa = ((ins.address + 4) & ~3) + (h & 0xFF) * 4
            return pa, (w32(pa) if inimg(pa) and pa + 4 <= END else None)
    return None


def adr_value(ins, mode):
    if mode == "A":
        x = w32(ins.address)
        if (x >> 28) == 0xF:
            return None
        if (x & 0x0FFF0000) == 0x028F0000:   # add rd, pc, #imm
            return ins.address + 8 + ror(x & 0xFF, 2 * ((x >> 8) & 0xF))
        if (x & 0x0FFF0000) == 0x024F0000:   # sub rd, pc, #imm
            return ins.address + 8 - ror(x & 0xFF, 2 * ((x >> 8) & 0xF))
    else:
        h = struct.unpack_from("<H", D, ins.address - BASE)[0]
        if (h & 0xF800) == 0xA000:
            return ((ins.address + 4) & ~3) + (h & 0xFF) * 4
    return None


def written_regs(ins):
    try:
        _, wr = ins.regs_access()
        return set(wr)
    except capstone.CsError:
        return set()


def is_cond(ins):
    return ins.cc not in (arm.ARM_CC_AL, arm.ARM_CC_INVALID)


def propagate(ins, mode, known):
    """Update known register values after ins; return a note string."""
    notes = []
    pl = pool_load(ins, mode)
    av = adr_value(ins, mode)
    ops = ins.operands
    wr = written_regs(ins)
    newval = None
    dst = None
    mn = ins.mnemonic.split(".")[0]
    base_mn = mn[:-2] if ins.cc not in (arm.ARM_CC_AL, arm.ARM_CC_INVALID) and len(mn) > 3 else mn
    if pl:
        pa, val = pl
        dst = ops[0].reg
        newval = val
        if val is not None:
            lab = mmio_label(val)
            notes.append("=[0x%X] 0x%08X%s" % (pa, val, " (%s)" % lab if lab else ""))
    elif av is not None:
        dst = ops[0].reg
        newval = av
        notes.append("adr 0x%08X" % av)
    elif base_mn.rstrip("s") in ("mov", "mvn") and len(ops) == 2 and ops[0].type == arm.ARM_OP_REG:
        dst = ops[0].reg
        if ops[1].type == arm.ARM_OP_IMM:
            v = ops[1].imm & 0xFFFFFFFF
            newval = v if base_mn.startswith("mov") else (~v) & 0xFFFFFFFF
        elif ops[1].type == arm.ARM_OP_REG and ops[1].reg in known and ops[1].shift.type == 0:
            newval = known[ops[1].reg]
            if base_mn.startswith("mvn"):
                newval = (~newval) & 0xFFFFFFFF
    elif base_mn.rstrip("s") in ("add", "sub", "orr", "bic", "eor", "and", "lsl", "lsr") and \
            len(ops) in (2, 3) and ops[0].type == arm.ARM_OP_REG:
        dst = ops[0].reg
        if len(ops) == 3:
            src, opd = ops[1], ops[2]
        else:
            src, opd = ops[0], ops[1]
        pcval = ins.address + 8 if mode == "A" else (ins.address + 4) & ~3
        a = known.get(src.reg) if src.type == arm.ARM_OP_REG else None
        if src.type == arm.ARM_OP_REG and src.reg == PC:
            a = pcval
        if opd.type == arm.ARM_OP_IMM:
            b = opd.imm & 0xFFFFFFFF
        elif opd.type == arm.ARM_OP_REG and opd.shift.type == 0:
            b = pcval if opd.reg == PC else known.get(opd.reg)
        else:
            b = None
        if a is not None and b is not None:
            op = base_mn.rstrip("s")
            newval = {"add": (a + b), "sub": (a - b), "orr": a | b, "bic": a & ~b,
                      "eor": a ^ b, "and": a & b, "lsl": a << (b & 31),
                      "lsr": a >> (b & 31)}[op] & 0xFFFFFFFF
    # memory access with known base
    for o in ops:
        if o.type == arm.ARM_OP_MEM and o.mem.base != PC and o.mem.base in known \
                and o.mem.index == 0:
            disp = o.mem.disp
            if getattr(o, "subtracted", False) and disp > 0:
                disp = -disp
            ea = (known[o.mem.base] + disp) & 0xFFFFFFFF
            lab = mmio_label(ea)
            notes.append("@0x%08X%s" % (ea, " (%s)" % lab if lab else ""))
    # kill written registers, then set dst if known and unconditional
    for r in wr:
        known.pop(r, None)
    if LR in wr and base_mn not in ("bl", "blx"):
        known["lr_set"] = True
    if base_mn in ("bl", "blx"):
        for r in (arm.ARM_REG_R0, arm.ARM_REG_R1, arm.ARM_REG_R2, arm.ARM_REG_R3,
                  arm.ARM_REG_R12, LR, "lr_set"):
            known.pop(r, None)
    if dst is not None and newval is not None and not is_cond(ins) and dst != PC:
        known[dst] = newval
        if not pl and av is None:
            lab = mmio_label(newval)
            notes.append("%s=0x%X%s" % (reg_name(dst), newval, " (%s)" % lab if lab else ""))
    return "; ".join(notes)


def branch_info(ins, mode, known):
    """Return (kind, target, target_mode, conditional).

    kind: 'call', 'jump', 'ret', 'indirect_call', 'indirect_jump', None.
    """
    mn = ins.mnemonic
    ops = ins.operands
    cond = is_cond(ins)
    gid = set(ins.groups)
    m0 = mn
    for cc in ("eq", "ne", "hs", "lo", "cs", "cc", "mi", "pl", "vs", "vc", "hi", "ls",
               "ge", "lt", "gt", "le"):
        if cond and mn.endswith(cc):
            m0 = mn[:-2]
            break
    m0 = m0.split(".")[0]
    if m0 in ("b", "bl", "blx") and ops and ops[0].type == arm.ARM_OP_IMM:
        t = ops[0].imm & 0xFFFFFFFF
        if m0 == "blx":
            tm = "T" if mode == "A" else "A"
            if tm == "A":
                t &= ~3
        else:
            tm = mode
        return ("jump" if m0 == "b" else "call"), t, tm, cond
    if m0 in ("bx", "blx") and ops and ops[0].type == arm.ARM_OP_REG:
        r = ops[0].reg
        if r == LR and m0 == "bx":
            return "ret", None, None, cond
        v = known.get(r)
        kind = "call" if m0 == "blx" or known.get("lr_set") else "jump"
        if v is not None:
            return kind, v & ~1, ("T" if v & 1 else "A"), cond
        return "indirect_" + kind, None, None, cond
    # writes to pc
    if PC in written_regs(ins) or (ops and ops[0].type == arm.ARM_OP_REG and ops[0].reg == PC
                                   and m0 in ("mov", "ldr", "add", "sub")):
        if m0 in ("pop", "ldm", "ldmia", "ldmfd", "ldmib", "ldmda", "ldmdb"):
            return "ret", None, None, cond
        if m0 == "mov" and len(ops) == 2 and ops[1].type == arm.ARM_OP_REG and ops[1].reg == LR:
            return "ret", None, None, cond
        pl = pool_load(ins, mode)
        if pl and pl[1] is not None:
            v = pl[1]
            return "jump", v & ~1, ("T" if v & 1 else "A"), cond
        return "indirect_jump", None, None, cond
    return None, None, None, cond


def jump_table(ins, mode, prev):
    """Entry count of an armcc switch (cmp rX,#N; add<cc> pc,pc,rX,lsl #2), else 0."""
    if mode != "A" or not ins.mnemonic.startswith("add") or len(ins.operands) != 3:
        return 0
    o0, o1, o2 = ins.operands
    if not (o0.reg == PC and o1.reg == PC and o2.type == arm.ARM_OP_REG
            and o2.shift.type == arm.ARM_SFT_LSL and o2.shift.value == 2):
        return 0
    for p in reversed(prev[-3:]):
        if p.mnemonic == "cmp" and p.operands[0].reg == o2.reg and \
                p.operands[1].type == arm.ARM_OP_IMM:
            return p.operands[1].imm
    return 0


def walk(seeds, stop=frozenset()):
    """stop: literal-pool addresses from an earlier pass; a linear run ends there
    (the instruction before was a call that does not return, like exit)."""
    code = {}           # addr -> Insn
    funcs = {}          # entry -> mode
    data_refs = {}      # pool addr -> (value, user)
    unresolved = []
    edges = defaultdict(set)        # caller-insn -> targets (call)
    queue = []
    seen_block = set()
    for a, m in seeds:
        funcs[a] = m
        queue.append((a, m))
    while queue:
        a, m = queue.pop()
        if (a, m) in seen_block:
            continue
        seen_block.add((a, m))
        known = {}
        prev = []
        start = a
        while inimg(a):
            if a in code:
                break
            if a != start and (a in stop or a in data_refs):
                break
            ins = decode(a, m)
            if ins is None:
                unresolved.append((a, m, "undecodable"))
                break
            it = Insn()
            it.addr, it.mode, it.size, it.mn, it.ops = a, m, ins.size, ins.mnemonic, ins.op_str
            it.raw = D[a - BASE:a - BASE + ins.size]
            it.ins = ins
            pl = pool_load(ins, m)
            if pl:
                data_refs.setdefault(pl[0], (pl[1], a))
            kind, t, tm, cond = branch_info(ins, m, known)
            it.note = propagate(ins, m, known)
            code[a] = it
            if kind == "call" and ins.mnemonic.startswith("bx"):
                known.pop("lr_set", None)   # the lr set up for this call is used up
            if kind == "call":
                if inimg(t):
                    funcs.setdefault(t, tm)
                    queue.append((t, tm))
                    edges[a].add(t)
                else:
                    edges[a].add(t)
                    it.note = (it.note + "; " if it.note else "") + "call outside image 0x%X" % t
            elif kind == "jump":
                if inimg(t):
                    queue.append((t, tm))
                    if tm != m:
                        it.note = (it.note + "; " if it.note else "") + "mode switch -> %s" % tm
                    if not cond and a in funcs:
                        funcs.setdefault(t, tm)   # a function that is only a branch: its target is one too
                if not cond:
                    break
            elif kind == "ret":
                if not cond:
                    break
            elif kind in ("indirect_call", "indirect_jump"):
                n = jump_table(ins, m, prev)
                if n:
                    # armcc switch: add<cc> pc, pc, rX, lsl #2; b default; b case0 ...
                    for i in range(n):
                        queue.append((a + 8 + 4 * i, m))
                    it.note = (it.note + "; " if it.note else "") + \
                        "jump table, %d entries at 0x%X" % (n, a + 8)
                else:
                    unresolved.append((a, m, "%s %s %s" % (kind, ins.mnemonic, ins.op_str)))
                if kind == "indirect_jump" and not cond:
                    break
            prev.append(ins)
            a += ins.size
    return code, funcs, data_refs, unresolved, edges


def func_bodies(code, funcs):
    """Assign each instruction to the function whose entry reaches it by non-call flow."""
    owner = {}
    body = defaultdict(set)
    for f, m in sorted(funcs.items()):
        stack = [f]
        while stack:
            a = stack.pop()
            if a in body[f] or a not in code:
                continue
            if a != f and a in funcs:
                continue  # tail call / other function
            body[f].add(a)
            owner.setdefault(a, f)
            it = code[a]
            kind, t, tm, cond = branch_info(it.ins, it.mode, {})
            nxt = a + it.size
            if kind == "jump":
                if t is not None and inimg(t):
                    stack.append(t)
                if cond:
                    stack.append(nxt)
                continue
            if kind in ("ret", "indirect_jump") and not cond:
                continue
            # pool-relative bx with known value was resolved in walk(); follow its target
            stack.append(nxt)
    # jumps resolved only through propagation (bx rN with known value)
    return owner, body


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--roles", default=None)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    roles_path = args.roles or os.path.join(args.out, "roles.tsv")
    roles = {}
    if os.path.exists(roles_path):
        for line in open(roles_path, encoding="utf-8"):
            if not line.strip() or line.startswith("#"):
                continue
            p = line.rstrip("\n").split("\t")
            roles[int(p[0], 16)] = (p[1] if len(p) > 1 else "", p[2] if len(p) > 2 else "")

    # Seeds: reset entry, scatter helpers (fn words of the scatter table)
    seeds = [(BASE, "A")]
    tab_lo = BASE + 0x94 + w32(BASE + 0x94)
    tab_hi = BASE + 0x94 + w32(BASE + 0x98)
    for e in range(tab_lo, tab_hi, 16):
        fn = w32(e + 12)
        seeds.append((fn & ~1, "T" if fn & 1 else "A"))
    code, funcs, data_refs, unresolved, edges = walk(seeds)
    # Pointer seeds: literal words that point into the image and are not used
    # as a load base within the next six instructions (that would be a data
    # table, like the PLL divider table at 0x7030EC). ISRs and the routine
    # copied to SRAM are reached only this way.
    ptr_seeds = []
    for pa, (val, user) in sorted(data_refs.items()):
        if val is None or not inimg(val & ~1) or (val & ~1) in code:
            continue
        reg = code[user].ins.operands[0].reg
        as_base = False
        a = user + code[user].size
        for _ in range(6):
            if a not in code:
                break
            ins = code[a].ins
            if ins.mnemonic.startswith(("ldr", "ldm")) and any(
                    o.type == arm.ARM_OP_MEM and o.mem.base == reg for o in ins.operands):
                as_base = True
            if ins.mnemonic.startswith("ldm") and ins.operands[0].reg == reg:
                as_base = True
            a += code[a].size
        if not as_base:
            ptr_seeds.append((val & ~1, "T" if val & 1 else "A", pa))
    if ptr_seeds:
        code, funcs, data_refs, unresolved, edges = walk(
            seeds + [(v, m) for v, m, _ in ptr_seeds], stop=frozenset(data_refs))
    via_ptr = {v: pa for v, m, pa in ptr_seeds}
    # The exception handlers live in the copied vector block (VA 0, not in the
    # image); report them, they are not code in this file.
    vec_src = w32(tab_lo)
    vectors = [w32(vec_src + 0x20 + 4 * i) for i in range(8)]
    owner, body = func_bodies(code, funcs)

    callers = defaultdict(set)
    callees = defaultdict(set)
    for a, ts in edges.items():
        f = owner.get(a)
        for t in ts:
            callers[t].add(a)
            if f is not None:
                callees[f].add(t)

    # ---- listing
    covered = set()
    for a, it in code.items():
        covered.update(range(a, a + it.size))
    for pa in data_refs:
        covered.update(range(pa, pa + 4))
    with open(os.path.join(args.out, "listing.txt"), "w", encoding="utf-8") as fh:
        fh.write("BOOT.bin listing, base 0x%08X, %d bytes; generated by tools/scripts/boot_listing.py\n"
                 % (BASE, len(D)))
        fh.write("Columns: VA  mode  bytes  instruction  ; notes (pool value, known register value, MMIO)\n\n")
        a = BASE
        while a < END:
            if a in funcs:
                name, role = roles.get(a, ("", ""))
                fh.write("\n; ---- function 0x%08X %s %s%s\n" % (
                    a, funcs[a], name or "sub_%06X" % (a - BASE),
                    ("  -- " + role) if role else ""))
                if a in via_ptr:
                    fh.write(";      reached through the literal word at 0x%X\n" % via_ptr[a])
                cl = sorted(callers.get(a, ()))
                if cl:
                    fh.write(";      called from %s\n" % ", ".join("0x%X" % c for c in cl))
            if a in code:
                it = code[a]
                fh.write("%08X  %s  %-8s  %-8s %-32s%s\n" % (
                    a, it.mode, it.raw.hex(), it.mn, it.ops, ("; " + it.note) if it.note else ""))
                a += it.size
            elif a in data_refs:
                v, user = data_refs[a]
                lab = mmio_label(v) if v is not None else None
                fh.write("%08X  D  %08X  .word 0x%08X%s  ; pool, loaded at 0x%X\n" % (
                    a, v, v, (" (%s)" % lab) if lab else "", user))
                a += 4
            else:
                b = a
                while b < END and b not in code and b not in data_refs and b not in funcs:
                    b += 1
                chunk = D[a - BASE:b - BASE]
                for k in range(0, len(chunk), 16):
                    seg = chunk[k:k + 16]
                    asc = "".join(chr(c) if 32 <= c < 127 else "." for c in seg)
                    fh.write("%08X  ?  %-32s  %s\n" % (a + k, seg.hex(), asc))
                a = b

    # ---- functions
    with open(os.path.join(args.out, "functions.txt"), "w", encoding="utf-8") as fh:
        fh.write("entry       mode  extent                 insns  callers  name  role\n")
        for f in sorted(funcs):
            bs = body.get(f, set())
            lo = min(bs) if bs else f
            hi = max(a + code[a].size for a in bs) if bs else f
            mm = set()
            for a in bs:
                n = code[a].note or ""
                for part in n.split("; "):
                    if "(" in part and ("0xB" in part):
                        mm.add(part[part.index("(") + 1:part.rindex(")")])
            name, role = roles.get(f, ("", ""))
            fh.write("0x%08X  %s  0x%08X-0x%08X  %5d  %-7s  %s  %s\n" % (
                f, funcs[f], lo, hi, len(bs),
                "%d%s" % (len(callers.get(f, ())), "+p" if f in via_ptr else ""),
                name or "sub_%06X" % (f - BASE), role))
            cs = sorted(callees.get(f, ()))
            if cs:
                fh.write("      calls: %s\n" % ", ".join(
                    "0x%X%s" % (c, (" " + roles[c][0]) if c in roles and roles[c][0] else "")
                    for c in cs))
            if mm:
                fh.write("      mmio:  %s\n" % ", ".join(sorted(mm)))

    # ---- coverage
    with open(os.path.join(args.out, "coverage.txt"), "w", encoding="utf-8") as fh:
        n_code = sum(it.size for it in code.values())
        fh.write("bytes reached as code: %d of %d; pool words: %d; functions: %d\n" % (
            n_code, len(D), len(data_refs), len(funcs)))
        fh.write("vector block copied to VA 0 from 0x%X; handler words: %s\n" % (
            vec_src, ", ".join("0x%X" % v for v in vectors)))
        fh.write("Thumb instructions: %d, ARM instructions: %d\n" % (
            sum(1 for it in code.values() if it.mode == "T"),
            sum(1 for it in code.values() if it.mode == "A")))
        fh.write("\nRanges neither code nor referenced pool word:\n")
        a = BASE
        while a < END:
            if a in covered:
                a += 1
                continue
            b = a
            while b < END and b not in covered:
                b += 1
            seg = D[a - BASE:b - BASE]
            zero = seg.count(0)
            fh.write("  0x%08X-0x%08X  %5d bytes  zero %d\n" % (a, b, b - a, zero))
            a = b

    with open(os.path.join(args.out, "unresolved.txt"), "w", encoding="utf-8") as fh:
        for a, m, why in sorted(unresolved):
            fh.write("0x%08X %s  %s\n" % (a, m, why))

    print("code bytes %d, functions %d, pool words %d, unresolved %d -> %s" % (
        sum(it.size for it in code.values()), len(funcs), len(data_refs), len(unresolved), args.out))


if __name__ == "__main__":
    main()
