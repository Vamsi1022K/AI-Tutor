# RUNNING COMMAND: python src/ast_parser.py errors/your_file.c
# =============================================================
# FILE: src/ast_parser.py
# WEEK 7 — AST Context Analysis
# =============================================================
# WHAT THIS FILE DOES:
#   Reads a .c file line by line and labels each line with its
#   AST (Abstract Syntax Tree) node type.
#
#   AST = the internal tree structure GCC builds from your code.
#   Every line of C maps to a "node" in this tree:
#     int x = 5;        → VarDecl  (variable declaration node)
#     printf("hello");  → CallExpr (function call node)
#     return 0;         → ReturnStmt (return statement node)
#
# HOW TO RUN:
#   python src/ast_parser.py errors/err_001_missing_semicolon.c
# =============================================================

import os    # file paths
import re    # pattern matching
import sys   # command-line arguments

# ── Paths ──────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── AST Rules ─────────────────────────────────────────────────
# Each rule: (node_type_name, regex_pattern)
# We test each line of code against these patterns.
# The first match tells us what AST node that line is.

AST_RULES = [
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
    ("BinaryOp[assign]",    re.compile(r'^\s*\w+\s*=\s*.+;')),
    ("CompoundStmt[open]",  re.compile(r'^\s*\{')),
    ("CompoundStmt[close]", re.compile(r'^\s*\}')),
]

# ── Which GCC error → which AST node caused it ────────────────
ERROR_TO_AST = {
    "expected ';'"        : ("VarDecl / ExprStmt",  "Statement is missing its semicolon terminator"),
    "undeclared"          : ("DeclRefExpr",          "No VarDecl found for this name in the symbol table"),
    "incompatible types"  : ("BinaryOp[assign]",     "Left type ≠ right type in assignment"),
    "implicit declaration": ("CallExpr",             "No FunctionDecl in scope — missing #include"),
    "too few arguments"   : ("CallExpr",             "Call has fewer args than FunctionDecl requires"),
    "redefinition"        : ("VarDecl",              "Two VarDecl nodes with same name in same scope"),
    "return with a value" : ("ReturnStmt",           "ReturnStmt has value but FunctionDecl is void"),
    "format '%d' expects" : ("CallExpr[printf]",     "Argument type doesn't match format specifier"),
    "expected '}'"        : ("CompoundStmt",         "Block opened with { but never closed with }"),
    "expected ')'"        : ("ParenExpr",            "Parenthesis opened but never closed"),
}

def annotate_file(filepath):
    """Read C file, return list of {line_num, code, node_type}."""
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()

    annotated = []
    for lineno, line in enumerate(lines, start=1):
        node = "Stmt/Expr"   # default if nothing matches
        for node_type, pattern in AST_RULES:
            if pattern.search(line):
                node = node_type
                break
        annotated.append({
            'line_num' : lineno,
            'code'     : line.rstrip(),
            'node_type': node
        })
    return annotated

def print_ast_table(filepath, annotated, highlight=None):
    """Print the annotated AST view table."""
    fname = os.path.basename(filepath)
    print(f"\n{'='*65}")
    print(f"  AST VIEW: {fname}")
    print(f"{'='*65}")
    print(f"  {'Line':>5}  {'AST Node':28}  Code")
    print(f"  {'─'*5}  {'─'*28}  {'─'*25}")
    for item in annotated:
        arrow = "  ◄── ERROR" if item['line_num'] == highlight else ""
        code  = item['code'][:35]
        print(f"  {item['line_num']:>5}  {item['node_type']:28}  {code}{arrow}")
    print(f"{'='*65}")

def explain_error(gcc_msg, error_line, annotated):
    """Look up which AST node caused the error and explain it."""
    print(f"\n  AST Error Explanation:")
    print(f"  {'─'*45}")

    # Find the line in our annotated list
    item = next((a for a in annotated if a['line_num'] == error_line), None)
    if item:
        print(f"  Error Line  : {item['code'].strip()}")
        print(f"  AST Node    : {item['node_type']}")

    # Look up the error keyword
    gcc_lower = gcc_msg.lower()
    for keyword, (node, reason) in ERROR_TO_AST.items():
        if keyword.lower() in gcc_lower:
            print(f"  Responsible : {node}")
            print(f"  Root Cause  : {reason}")
            break
    print()

def check_infinite_loops(annotated):
    """
    Static analysis to detect characteristic infinite loops like while(1) or for(;;).
    Returns a list of potential logic errors found.
    """
    logic_errors = []
    
    # Simple patterns for infinite loops
    pattern_while_1 = re.compile(r'while\s*\(\s*(1|true)\s*\)')
    pattern_for_inf = re.compile(r'for\s*\(\s*;\s*;\s*\)')
    
    for item in annotated:
        code = item['code']
        if pattern_while_1.search(code):
            logic_errors.append({
                'line_num': item['line_num'],
                'type': 'Infinite Loop',
                'explanation': "The 'while(1)' or 'while(true)' creates a loop that runs forever unless there is a 'break' or 'return' inside."
            })
        elif pattern_for_inf.search(code):
            logic_errors.append({
                'line_num': item['line_num'],
                'type': 'Infinite Loop',
                'explanation': "The 'for(;;)' creates an empty-condition loop that runs forever. Ensure you have a 'break' condition inside the loop."
            })
            
    return logic_errors

def main():
    print("=" * 50)
    print("  WEEK 7 — AST Context Analysis")
    print("=" * 50)

    if len(sys.argv) < 2:
        print("\n  Usage:")
        print("  python src/ast_parser.py errors/err_001_missing_semicolon.c")
        print("  python src/ast_parser.py errors/err_001_missing_semicolon.c 8")
        return

    filepath    = sys.argv[1]
    error_line  = int(sys.argv[2]) if len(sys.argv) >= 3 else None

    if not os.path.isfile(filepath):
        print(f"  ERROR: File not found: {filepath}")
        return

    annotated = annotate_file(filepath)
    print_ast_table(filepath, annotated, highlight=error_line)

    if error_line:
        explain_error("expected ';'", error_line, annotated)

    # Node type count summary
    counts = {}
    for item in annotated:
        counts[item['node_type']] = counts.get(item['node_type'], 0) + 1
    print(f"  Node type counts:")
    for node, cnt in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"    {node:30s}: {cnt}")

if __name__ == '__main__':
    main()
