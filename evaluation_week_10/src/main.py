# RUNNING COMMAND: python src/main.py errors/your_file.c
# =============================================================
# FILE: src/main.py
# WEEK 9-10 — Main AI Tutor (Rule-Based Rewriter)
# =============================================================
# WHAT THIS FILE DOES:
#   This is the core of the project — the AI Tutor.
#   It does these steps in order:
#     1. Take a .c file as input
#     2. Compile it with GCC and capture the error
#     3. Match the error against patterns in the dataset
#     4. Show the beginner-friendly explanation and fix
#
# HOW TO RUN:
#   python src/main.py errors/err_001_missing_semicolon.c
#   python src/main.py errors/err_002_undeclared_variable.c
#
# HOW TO RUN SUB-TOOLS:
#   python src/main.py --collect    (Week 6: collect all errors)
#   python src/main.py --dataset    (Week 8: validate dataset)
#   python src/main.py --security errors/err_001.c  (Week 11)
#   python src/main.py --evaluate   (Week 12: score report)
# =============================================================

import subprocess  # run GCC from Python
import os          # file paths
import re          # pattern matching
import json        # read dataset
import sys         # command-line arguments

# Ensure src/ is in path for internal imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from executor import run_with_timeout
from ast_parser import annotate_file, check_infinite_loops
from model_inference import explain_with_ai

# ── Paths ──────────────────────────────────────────────────────
BASE_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, 'phase4_dataset', 'annotated_errors.json')

# ── Error matching patterns ────────────────────────────────────
# GCC error text → error ID in our dataset
# We use re.compile() for fast, reusable regex patterns.
# Order matters: more specific patterns come first.

PATTERNS = [
    # ── Original 10 patterns ───────────────────────────────────
    (re.compile(r"incompatible types when assigning",        re.I), "E003"),
    (re.compile(r"implicit declaration of function 'printf'",re.I), "E004"),
    (re.compile(r"return with a value",                      re.I), "E010"),
    (re.compile(r"too few arguments",                        re.I), "E006"),
    (re.compile(r"redefinition of",                          re.I), "E009"),
    (re.compile(r"format '%d'.+double",                      re.I), "E011"),
    (re.compile(r"expected.*';'",                           re.I), "E001"),
    (re.compile(r"expected.*'\)'",                          re.I), "E005"),
    (re.compile(r"expected.*'\}'",                          re.I), "E015"),
    # ── New 15 patterns ───────────────────────────────────────
    (re.compile(r"array subscript.+above array bounds",      re.I), "E016"),
    (re.compile(r"null pointer dereference",                 re.I), "E017"),
    (re.compile(r"division by zero",                         re.I), "E018"),
    (re.compile(r"used uninitialized",                       re.I), "E019"),
    (re.compile(r"format '%d'.+float",                       re.I), "E020"),
    (re.compile(r"control reaches end of non-void",          re.I), "E021"),
    (re.compile(r"incompatible pointer type",                re.I), "E022"),
    (re.compile(r"implicit declaration of function 'sqrt'",  re.I), "E024"),
    (re.compile(r"integer overflow",                         re.I), "E025"),
    (re.compile(r"overflow in conversion.+char",             re.I), "E026"),
    (re.compile(r"may fall through",                         re.I), "E027"),
    (re.compile(r"has no member named",                      re.I), "E030"),
    (re.compile(r"excess elements in array",                 re.I), "E029"),
    # ── Broad fallback patterns (must be LAST) ─────────────────
    (re.compile(r"undeclared",                               re.I), "E002"),
    (re.compile(r"format '%.+' expects",                     re.I), "E011"),
]

# ── GCC output line pattern ────────────────────────────────────
# GCC error lines look like: filename.c:LINE:COL: error: message
# This regex captures each part.
GCC_RE = re.compile(
    r'^([^:]+):(\d+):(\d+):\s*(error|warning):\s*(.+)$'
)

# ─────────────────────────────────────────────────────────────
# STEP 1: Load the dataset
# ─────────────────────────────────────────────────────────────
def load_dataset():
    """Read annotated_errors.json into a dict keyed by error ID."""
    if not os.path.isfile(DATASET_PATH):
        print("ERROR: annotated_errors.json not found!")
        sys.exit(1)
    with open(DATASET_PATH, 'r', encoding='utf-8') as f:
        entries = json.load(f)
    return {e['id']: e for e in entries}   # {'E001': {...}, 'E002': {...}, ...}

# ─────────────────────────────────────────────────────────────
# STEP 2: Compile the C file with GCC
# ─────────────────────────────────────────────────────────────
def compile_file(filepath):
    """Run GCC on a C file. Return (stderr text, return code)."""
    null = 'NUL' if os.name == 'nt' else '/dev/null'
    result = subprocess.run(
        ['gcc', '-Wall', filepath, '-o', null],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True
    )
    return result.stderr, result.returncode

# ─────────────────────────────────────────────────────────────
# STEP 3: Parse GCC stderr into structured list
# ─────────────────────────────────────────────────────────────
def parse_errors(stderr):
    """Convert raw GCC text into a list of error dicts."""
    errors = []
    for line in stderr.splitlines():
        m = GCC_RE.match(line.strip())
        if m:
            errors.append({
                'file': m.group(1),
                'line': int(m.group(2)),
                'col' : int(m.group(3)),
                'type': m.group(4),
                'msg' : m.group(5).strip(),
                'raw' : line.strip()
            })
    return errors  # could be empty if no errors

# ─────────────────────────────────────────────────────────────
# STEP 4: Match error message to dataset entry
# ─────────────────────────────────────────────────────────────
def match_error(msg, dataset):
    """Find which dataset entry matches this GCC message."""
    for pattern, eid in PATTERNS:
        if pattern.search(msg):
            return dataset.get(eid)   # return the full entry or None
    return None

# ─────────────────────────────────────────────────────────────
# STEP 5: Print the AI Tutor output
# ─────────────────────────────────────────────────────────────
def print_output(errors, dataset, filename):
    """Display beginner-friendly results for all found errors."""
    div = "=" * 55

    print(f"\n{div}")
    print(f"  AI COMPILER TUTOR")
    print(f"  File: {filename}")

    if not errors:
        print(f"  [OK] No errors -- compiled successfully!")
        print(f"{div}\n")
        return

    print(f"  Found {len(errors)} issue(s)")
    print(f"{div}")

    for i, err in enumerate(errors, 1):
        entry = match_error(err['msg'], dataset)

        if entry:
            explanation = entry['plain_explanation']
            fix         = entry['fix']
            secure_flag = "[SAFE FIX]" if entry['secure'] else "[REVIEW FIX]"
        else:
            # AI Fallback: Use the T5 Model when no rule-based entry is found
            explanation = explain_with_ai(err['msg'])
            fix         = "Check the suggested AI fix carefully."
            secure_flag = "[AI MODEL GENERATED]"

        print(f"\n  -- Issue #{i} " + "-" * 38)
        print(f"  File: {err['file']}, Line {err['line']}")
        print(f"  GCC : {err['raw']}")
        print(f"\n  What it means:")
        print(f"     {explanation}")
        print(f"\n  How to fix it:")
        print(f"     {fix}")
        print(f"\n  Security: {secure_flag}")

    if len(errors) > 1:
        print(f"\n  Tip: Fix Issue #1 first -- it often causes the others.")
    print(f"\n{div}\n")

# ─────────────────────────────────────────────────────────────
# MAIN: Parse arguments and run the right tool
# ─────────────────────────────────────────────────────────────
def main():
    args = sys.argv[1:]

    if not args:
        print("\n  AI Compiler Tutor — Usage:")
        print("  python src/main.py errors/err_001_missing_semicolon.c")
        print("  python src/main.py --collect")
        print("  python src/main.py --dataset")
        print("  python src/main.py --evaluate")
        print("  python src/main.py --security errors/err_001.c\n")
        return

    # ── Sub-tool: collect errors (Week 6) ─────────────────────
    if args[0] == '--collect':
        from collect_errors import main as collect_main
        sys.path.insert(0, os.path.join(BASE_DIR, 'src'))
        collect_main()

    # ── Sub-tool: dataset validation (Week 8) ─────────────────
    elif args[0] == '--dataset':
        sys.path.insert(0, os.path.join(BASE_DIR, 'src'))
        from dataset_builder import main as ds_main
        ds_main()

    # ── Sub-tool: security scan (Week 11) ─────────────────────
    elif args[0] == '--security':
        sys.path.insert(0, os.path.join(BASE_DIR, 'src'))
        from secure_checker import scan_file, print_report
        target = args[1] if len(args) > 1 else None
        if not target:
            print("  Usage: python src/main.py --security errors/err_001.c")
            return
        issues = scan_file(target)
        print_report(target, issues)

    # ── Sub-tool: evaluation (Week 12) ────────────────────────
    elif args[0] == '--evaluate':
        sys.path.insert(0, os.path.join(BASE_DIR, 'src'))
        from evaluate import main as eval_main
        eval_main()

    # ── Main: analyze a C file (Week 9-10) ────────────────────
    else:
        filepath = args[0]

        if not os.path.isfile(filepath):
            print(f"\n  ERROR: File not found: {filepath}\n")
            return

        dataset = load_dataset()
        stderr, retcode = compile_file(filepath)
        errors    = parse_errors(stderr)
        
        # New: If compilation succeeds, check for infinite loops (Dynamic)
        exec_status = "N/A"
        exec_output = ""
        if not errors:
            exec_status, exec_output = run_with_timeout(filepath)
            if exec_status == "TIMEOUT":
                # Add a pseudo-error for infinite loop
                errors.append({
                    'file': os.path.basename(filepath),
                    'line': 0,
                    'col': 0,
                    'type': 'error',
                    'msg': "Potential Infinite Loop detected during execution!",
                    'raw': "Runtime Timeout: Execution exceeded 2.0s"
                })

        # New: Static analysis for logic errors
        annotated = annotate_file(filepath)
        logic_errors = check_infinite_loops(annotated)
        for le in logic_errors:
            # Check if we already have a runtime timeout for this
            if not any(e['msg'] == "Potential Infinite Loop detected during execution!" for e in errors):
                errors.append({
                    'file': os.path.basename(filepath),
                    'line': le['line_num'],
                    'col': 0,
                    'type': 'warning',
                    'msg': f"Static Analysis: {le['type']} - {le['explanation']}",
                    'raw': f"Line {le['line_num']}: {le['type']}"
                })

        # New: Add E031 pattern for Infinite Loop if detected
        if any("Infinite Loop" in e['msg'] for e in errors):
            if "E031" not in [p[1] for p in PATTERNS]:
                PATTERNS.append((re.compile(r"Infinite Loop", re.I), "E031"))

        print_output(errors, dataset, os.path.basename(filepath))

if __name__ == '__main__':
    main()
