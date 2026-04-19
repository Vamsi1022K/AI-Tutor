# =====================================================
# WEEK 6 — Error Collection using subprocess
# Compiles all 10 error C programs and captures GCC output
# Run: python phase3_error_analysis/week6_collect_errors.py
# =====================================================

import subprocess, os, json

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ERRORS_DIR = os.path.join(BASE_DIR, 'errors')
OUT_FILE   = os.path.join(BASE_DIR, 'phase3_error_analysis', 'week6_output.json')

FILES = [
    ("err_001_missing_semicolon.c",    "E001"),
    ("err_002_undeclared_variable.c",  "E002"),
    ("err_003_incompatible_types.c",   "E003"),
    ("err_004_implicit_declaration.c", "E004"),
    ("err_005_missing_paren.c",        "E005"),
    ("err_006_too_few_args.c",         "E006"),
    ("err_007_redefinition.c",         "E009"),
    ("err_008_void_return.c",          "E010"),
    ("err_009_format_mismatch.c",      "E011"),
    ("err_010_missing_brace.c",        "E015"),
]

def run_gcc(filepath):
    """Run GCC and return what it printed to stderr."""
    null = 'NUL' if os.name == 'nt' else '/dev/null'
    r = subprocess.run(
        ['gcc', '-Wall', filepath, '-o', null],
        stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True
    )
    return r.stderr

print("=" * 55)
print("  WEEK 6 — GCC Error Collection")
print("=" * 55 + "\n")

results = []
for filename, eid in FILES:
    path   = os.path.join(ERRORS_DIR, filename)
    stderr = run_gcc(path)
    first  = stderr.strip().splitlines()[0] if stderr.strip() else "No error"
    print(f"  [{eid}] {filename}")
    print(f"       {first[:62]}\n")
    results.append({"id": eid, "file": filename, "gcc_error": first})

with open(OUT_FILE, 'w') as f:
    json.dump(results, f, indent=2)

print(f"  ✅ Saved to week6_output.json  ({len(results)} entries)")
print("=" * 55)
