# =====================================================
# WEEK 7 — AST Context Analysis
# Reads a C file and labels each line with its AST node type
# Run: python phase4_dataset/week7_ast_mapper.py errors/err_001_missing_semicolon.c
# =====================================================

import os, re, sys

# AST Rules: (node_type, regex_pattern)
RULES = [
    ("IncludeDirective",    re.compile(r'^\s*#include')),
    ("FunctionDecl",        re.compile(r'^\s*(int|void|char|float|double)\s+\w+\s*\(')),
    ("VarDecl",             re.compile(r'^\s*(int|float|double|char|long)\s+\w+')),
    ("ReturnStmt",          re.compile(r'^\s*return\b')),
    ("IfStmt",              re.compile(r'^\s*if\s*\(')),
    ("ForStmt",             re.compile(r'^\s*for\s*\(')),
    ("WhileStmt",           re.compile(r'^\s*while\s*\(')),
    ("CallExpr[printf]",    re.compile(r'^\s*printf\s*\(')),
    ("CallExpr[scanf]",     re.compile(r'^\s*scanf\s*\(')),
    ("CallExpr",            re.compile(r'^\s*\w+\s*\([^)]*\)\s*;')),
    ("BinaryOp[=]",         re.compile(r'^\s*\w+\s*=\s*.+;')),
    ("CompoundStmt[open]",  re.compile(r'^\s*\{')),
    ("CompoundStmt[close]", re.compile(r'^\s*\}')),
]

# GCC error → responsible AST node
ERROR_MAP = {
    "expected ';'"       : "VarDecl/ExprStmt — semicolon missing at end of node",
    "undeclared"         : "DeclRefExpr — no matching VarDecl in symbol table",
    "incompatible types" : "BinaryOp[=] — left and right types don't match",
    "implicit declaration": "CallExpr — no FunctionDecl in scope (missing #include)",
    "too few arguments"  : "CallExpr — fewer args than FunctionDecl expects",
    "redefinition"       : "VarDecl — duplicate declaration in same scope",
    "return with a value": "ReturnStmt — value returned from void FunctionDecl",
    "format '%d' expects": "CallExpr[printf] — argument type ≠ format specifier",
    "expected '}'"       : "CompoundStmt — block opened with { never closed",
}

if len(sys.argv) < 2:
    print("Usage: python week7_ast_mapper.py errors/err_001_missing_semicolon.c [line]")
    sys.exit()

filepath   = sys.argv[1]
error_line = int(sys.argv[2]) if len(sys.argv) >= 3 else None

with open(filepath, 'r', errors='replace') as f:
    lines = f.readlines()

print(f"\n{'='*60}")
print(f"  WEEK 7 — AST View: {os.path.basename(filepath)}")
print(f"{'='*60}")
print(f"  {'Line':>5}  {'AST Node':28}  Code")
print(f"  {'─'*5}  {'─'*28}  {'─'*25}")

for i, line in enumerate(lines, 1):
    node  = "Stmt/Expr"
    for name, pat in RULES:
        if pat.search(line):
            node = name
            break
    arrow = "  ◄── ERROR" if i == error_line else ""
    print(f"  {i:>5}  {node:28}  {line.rstrip()[:32]}{arrow}")

if error_line:
    print(f"\n  Error at line {error_line} maps to:")
    for keyword, explanation in ERROR_MAP.items():
        # show first match found in filename hint
        print(f"  '{keyword}' → {explanation}")
        break   # just show first as example

print(f"\n{'='*60}\n")
