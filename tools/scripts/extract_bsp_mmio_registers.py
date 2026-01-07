#!/usr/bin/env python3
"""Extract MMIO register definitions from the N32901-3 NonOS BSP headers."""

from __future__ import annotations

import ast
import json
import os
import re
from datetime import datetime
from typing import Iterable, List, Tuple

ROOT = "docs/vendor/N32901-3_NonOS_BSP"
OUTPUT = ".re_kb/n32903_registers.json"
ADDR_MIN = 0xB0000000
ADDR_MAX = 0xBFFFFFFF

DEFINE_RE = re.compile(r"^\s*#\s*define\s+([A-Za-z_][A-Za-z0-9_]*)\s+(.*)$")
BLOCK_COMMENT_RE = re.compile(r"/\*.*?\*/", re.S)
LINE_COMMENT_RE = re.compile(r"//.*")
TYPE_KEYWORDS = {
    "volatile",
    "const",
    "unsigned",
    "signed",
    "struct",
    "union",
    "enum",
    "int",
    "short",
    "long",
    "char",
    "__io",
    "__iom",
    "__im",
    "__om",
    "__i",
    "__o",
    "uint",
    "uint8",
    "uint16",
    "uint32",
    "uint64",
    "int8",
    "int16",
    "int32",
    "int64",
    "uint8_t",
    "uint16_t",
    "uint32_t",
    "uint64_t",
    "int8_t",
    "int16_t",
    "int32_t",
    "int64_t",
    "bool",
    "bool_t",
    "u8",
    "u16",
    "u32",
    "u64",
    "s8",
    "s16",
    "s32",
    "s64",
    "uint8",
    "uint16",
    "uint32",
    "uint64",
    "int8",
    "int16",
    "int32",
    "int64",
    "UINT8",
    "UINT16",
    "UINT32",
    "UINT64",
    "INT8",
    "INT16",
    "INT32",
    "INT64",
}


def tokenize(expr: str) -> List[Tuple[str, str]]:
    tokens: List[Tuple[str, str]] = []
    i = 0
    n = len(expr)
    while i < n:
        ch = expr[i]
        if ch.isspace():
            i += 1
            continue
        if ch.isalpha() or ch == "_":
            start = i
            i += 1
            while i < n and (expr[i].isalnum() or expr[i] == "_"):
                i += 1
            tokens.append(("ident", expr[start:i]))
            continue
        if ch.isdigit():
            start = i
            if expr[i : i + 2].lower() == "0x":
                i += 2
                while i < n and expr[i] in "0123456789abcdefABCDEF":
                    i += 1
            else:
                i += 1
                while i < n and expr[i].isdigit():
                    i += 1
            num = expr[start:i]
            while i < n and expr[i] in "uUlL":
                i += 1
            tokens.append(("number", num))
            continue
        if expr.startswith("<<", i) or expr.startswith(">>", i):
            tokens.append(("op", expr[i : i + 2]))
            i += 2
            continue
        if ch in "+-*/|&^~()<>":
            kind = "op"
            if ch == "(":
                kind = "lparen"
            elif ch == ")":
                kind = "rparen"
            tokens.append((kind, ch))
            i += 1
            continue
        i += 1
    return tokens


def strip_empty_parens(expr: str) -> str:
    while "()" in expr:
        expr = expr.replace("()", "")
    return expr


def clean_expr(expr: str) -> str:
    expr = expr.strip().rstrip(";")
    if not expr:
        return ""
    tokens = tokenize(expr)
    filtered: List[Tuple[str, str]] = []
    for kind, value in tokens:
        if kind == "ident" and value.lower() in TYPE_KEYWORDS:
            continue
        if kind == "op" and value in ("*", "&"):
            prev = filtered[-1][0] if filtered else None
            if prev in (None, "op", "lparen"):
                continue
        filtered.append((kind, value))
    if not filtered:
        return ""
    expr = " ".join(val for _kind, val in filtered)
    expr = strip_empty_parens(expr)
    return expr.strip()


class EvalError(Exception):
    pass


def eval_ast(node: ast.AST, values: dict) -> int:
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return int(node.value)
        raise EvalError("unsupported constant")
    if isinstance(node, ast.Num):
        return int(node.n)
    if isinstance(node, ast.Name):
        if node.id in values:
            return values[node.id]
        raise EvalError(f"unresolved name: {node.id}")
    if isinstance(node, ast.BinOp):
        left = eval_ast(node.left, values)
        right = eval_ast(node.right, values)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.BitOr):
            return left | right
        if isinstance(node.op, ast.BitAnd):
            return left & right
        if isinstance(node.op, ast.BitXor):
            return left ^ right
        if isinstance(node.op, ast.LShift):
            return left << right
        if isinstance(node.op, ast.RShift):
            return left >> right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.FloorDiv):
            return left // right
        raise EvalError("unsupported operator")
    if isinstance(node, ast.UnaryOp):
        operand = eval_ast(node.operand, values)
        if isinstance(node.op, ast.UAdd):
            return +operand
        if isinstance(node.op, ast.USub):
            return -operand
        if isinstance(node.op, ast.Invert):
            return ~operand
        raise EvalError("unsupported unary")
    raise EvalError("unsupported expression")


def eval_expr(expr: str, values: dict) -> int:
    expr = clean_expr(expr)
    if not expr:
        raise EvalError("empty")
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as exc:
        raise EvalError(str(exc))
    return eval_ast(tree.body, values)


def iter_headers(root: str) -> Iterable[str]:
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            if name.lower().endswith(".h"):
                yield os.path.join(dirpath, name)


def extract_defines(path: str) -> List[Tuple[str, str]]:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            content = fh.read()
    except OSError:
        return []
    content = BLOCK_COMMENT_RE.sub("", content)
    lines = content.splitlines()
    defines: List[Tuple[str, str]] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        while line.rstrip().endswith("\\") and i + 1 < len(lines):
            line = line.rstrip()[:-1] + lines[i + 1]
            i += 1
        i += 1
        line = LINE_COMMENT_RE.sub("", line).strip()
        if not line:
            continue
        match = DEFINE_RE.match(line)
        if not match:
            continue
        name, expr = match.groups()
        expr = expr.strip()
        if not expr:
            continue
        defines.append((name, expr))
    return defines


def main() -> None:
    all_defines: List[Tuple[str, str, str]] = []
    name_to_expr: dict[str, str] = {}

    for header in iter_headers(ROOT):
        for name, expr in extract_defines(header):
            all_defines.append((name, expr, header))
            if name not in name_to_expr:
                name_to_expr[name] = expr

    values: dict[str, int] = {}
    for _ in range(12):
        changed = False
        for name, expr in name_to_expr.items():
            if name in values:
                continue
            try:
                val = eval_expr(expr, values)
            except EvalError:
                continue
            values[name] = val
            changed = True
        if not changed:
            break

    entries = []
    base_entries = []

    for name, expr, header in all_defines:
        try:
            val = eval_expr(expr, values)
        except EvalError:
            continue
        if not (ADDR_MIN <= val <= ADDR_MAX):
            continue
        rel_path = os.path.relpath(header, ROOT)
        peripheral = rel_path.split(os.sep, 1)[0] if os.sep in rel_path else "ROOT"
        entry = {
            "peripheral": peripheral,
            "register_name": name,
            "address": f"0x{val:08X}",
            "source_file": rel_path,
        }
        entries.append(entry)
        if name.endswith("_BA") or name.endswith("_BASE"):
            base_entries.append(entry)

    entries.sort(key=lambda item: (item["peripheral"], item["register_name"]))
    base_entries.sort(key=lambda item: (item["peripheral"], item["register_name"]))

    peripheral_counts = {}
    for entry in entries:
        peripheral_counts[entry["peripheral"]] = (
            peripheral_counts.get(entry["peripheral"], 0) + 1
        )

    output = {
        "generated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_root": ROOT,
        "address_range": "0xB0000000-0xBFFFFFFF",
        "total_registers": len(entries),
        "peripheral_counts": dict(sorted(peripheral_counts.items())),
        "base_addresses": base_entries,
        "entries": entries,
    }

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as fh:
        json.dump(output, fh, indent=2, sort_keys=False)

    print(f"Wrote {len(entries)} registers to {OUTPUT}")


if __name__ == "__main__":
    main()
