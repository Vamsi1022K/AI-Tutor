# RUNNING COMMAND: python src/collect_errors.py
# =============================================================
# FILE: src/collect_errors.py
# WEEK 6 — Error Collection (EXPANDED: 25 errors)
# =============================================================
# WHAT THIS FILE DOES:
#   Runs GCC on each of our 25 error C programs.
#   Captures the error message GCC prints.
#   Saves everything to a JSON file.
#
# HOW TO RUN:
#   python src/collect_errors.py
# =============================================================

import subprocess  # lets Python run external programs like GCC
import os          # file and folder operations
import json        # read/write JSON files

# ── Paths ─────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ERRORS_DIR  = os.path.join(BASE_DIR, 'errors')
OUTPUT_FILE = os.path.join(BASE_DIR, 'raw_gcc_output.json')

# ── List of all 25 error programs ─────────────────────────────
# (filename, error_id, category)
ERROR_FILES = [
    # ── Original 10 ──────────────────────────────────────────
    ("err_001_missing_semicolon.c",    "E001", "Syntax"),
    ("err_002_undeclared_variable.c",  "E002", "Declaration"),
    ("err_003_incompatible_types.c",   "E003", "Type"),
    ("err_004_implicit_declaration.c", "E004", "Declaration"),
    ("err_005_missing_paren.c",        "E005", "Syntax"),
    ("err_006_too_few_args.c",         "E006", "Syntax"),
    ("err_007_redefinition.c",         "E009", "Declaration"),
    ("err_008_void_return.c",          "E010", "Scope"),
    ("err_009_format_mismatch.c",      "E011", "Type"),
    ("err_010_missing_brace.c",        "E015", "Syntax"),
    # ── New 15 ───────────────────────────────────────────────
    ("err_011_array_bounds.c",         "E016", "Memory"),
    ("err_012_null_pointer.c",         "E017", "Pointer"),
    ("err_013_division_zero.c",        "E018", "Logic"),
    ("err_014_uninit_variable.c",      "E019", "Logic"),
    ("err_015_wrong_format_float.c",   "E020", "Type"),
    ("err_016_missing_return.c",       "E021", "Scope"),
    ("err_017_pointer_mismatch.c",     "E022", "Pointer"),
    ("err_018_forgot_malloc.c",        "E023", "Memory"),
    ("err_019_wrong_include.c",        "E024", "Declaration"),
    ("err_020_integer_overflow.c",     "E025", "Overflow"),
    ("err_021_char_as_int.c",          "E026", "Type"),
    ("err_022_missing_break.c",        "E027", "Logic"),
    ("err_023_scope_error.c",          "E028", "Scope"),
    ("err_024_wrong_array_init.c",     "E029", "Syntax"),
    ("err_025_struct_field.c",         "E030", "Struct"),
]

def compile_and_capture(filepath):
    """Run GCC on one C file. Return what GCC printed."""
    # 'NUL' on Windows, '/dev/null' on Linux — we don't want an output exe
    null = 'NUL' if os.name == 'nt' else '/dev/null'

    result = subprocess.run(
        ['gcc', '-Wall', filepath, '-o', null],
        stderr=subprocess.PIPE,   # capture error output
        stdout=subprocess.PIPE,
        text=True                 # give us a string, not bytes
    )
    return result.stderr          # GCC errors go to stderr

def main():
    print("=" * 55)
    print("  WEEK 6 — GCC Error Collection (25 Errors)")
    print("=" * 55)

    results = []

    for filename, error_id, category in ERROR_FILES:
        filepath = os.path.join(ERRORS_DIR, filename)

        # Skip if file doesn't exist
        if not os.path.isfile(filepath):
            print(f"  MISSING: {filename}")
            continue

        # Compile and get GCC output
        stderr = compile_and_capture(filepath)

        # Get first line of the error (most important one)
        first_line = stderr.strip().splitlines()[0] if stderr.strip() else "No error"

        print(f"  [{error_id}] {filename}")
        print(f"       GCC: {first_line[:65]}")
        print()

        results.append({
            "id"         : error_id,
            "category"   : category,
            "filename"   : filename,
            "gcc_error"  : first_line,
            "full_output": stderr.strip()
        })

    # Save to JSON file
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"  Done! Saved {len(results)} entries to raw_gcc_output.json")
    print("=" * 55)

if __name__ == '__main__':
    main()
