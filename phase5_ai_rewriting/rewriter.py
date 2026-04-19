#!/usr/bin/env python3
"""
============================================================
 AI-BASED COMPILER ERROR MESSAGE REWRITING — AI TUTOR
 Week 10 Deliverable: Error Rewriting Module (rewriter.py)
 Phase 5: AI-Based Error Rewriting
============================================================
Project   : AI-Based Compiler Error Message Rewriting (AI Tutor)
Language  : C (target) | Python 3 (this module)
Compiler  : GCC
Dataset   : ../phase4_dataset/annotated_errors.json

Usage:
  python rewriter.py <your_c_file.c>
  python rewriter.py errors/err_001_missing_semicolon.c

Requirements:
  - Python 3.7+
  - GCC installed and accessible from command line
    Windows: Install MinGW-w64 and add gcc to PATH
    Linux  : sudo apt install gcc
    macOS  : xcode-select --install
============================================================
"""

import re
import json
import subprocess
import sys
import os

# ═══════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════

# Path to the annotated errors dataset (relative to this script)
DATASET_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', 'phase4_dataset', 'annotated_errors.json'
)

# GCC output line pattern:
# Matches: filename.c:LINE:COL: error/warning: message
GCC_LINE_PATTERN = re.compile(
    r'^(?P<file>[^:]+):(?P<line>\d+):(?P<col>\d+):\s*'
    r'(?P<type>error|warning|note):\s*(?P<msg>.+)$'
)

# ═══════════════════════════════════════════════════════════
# ERROR MATCHING PATTERNS
# Maps regex pattern → dataset Error ID
# Order matters: more specific patterns should come first
# ═══════════════════════════════════════════════════════════

ERROR_PATTERNS = [
    (re.compile(r"incompatible types when assigning", re.IGNORECASE), "E003"),
    (re.compile(r"implicit declaration of function",  re.IGNORECASE), "E004"),
    (re.compile(r"return with a value.*void|void.*return with a value",
                re.IGNORECASE), "E010"),
    (re.compile(r"too few arguments",                 re.IGNORECASE), "E006"),
    (re.compile(r"too many arguments",                re.IGNORECASE), "E006"),
    (re.compile(r"redefinition of",                   re.IGNORECASE), "E009"),
    (re.compile(r"format '%.+' expects",              re.IGNORECASE), "E011"),
    (re.compile(r"undeclared",                        re.IGNORECASE), "E002"),
    (re.compile(r"expected\s*';'",                    re.IGNORECASE), "E001"),
    (re.compile(r"expected\s*'\)'",                   re.IGNORECASE), "E005"),
    (re.compile(r"expected\s*'\}'",                   re.IGNORECASE), "E015"),
    (re.compile(r"expected '\}' at end",              re.IGNORECASE), "E015"),
]

# ═══════════════════════════════════════════════════════════
# MODULE 1: DATASET LOADER
# ═══════════════════════════════════════════════════════════

def load_dataset():
    """
    Load the annotated errors dataset from JSON file.
    Returns a dictionary keyed by error ID for fast lookup.
    """
    try:
        with open(DATASET_PATH, 'r', encoding='utf-8') as f:
            entries = json.load(f)
        # Build a lookup dict: { "E001": {...}, "E002": {...}, ... }
        return {entry['id']: entry for entry in entries}
    except FileNotFoundError:
        print(f"[ERROR] Dataset file not found: {DATASET_PATH}")
        print("  Make sure annotated_errors.json is in phase4_dataset/")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Dataset JSON is malformed: {e}")
        sys.exit(1)

# Load dataset once at module startup
DATASET = load_dataset()

# ═══════════════════════════════════════════════════════════
# MODULE 2: GCC COMPILATION MODULE
# ═══════════════════════════════════════════════════════════

def compile_with_gcc(c_file_path):
    """
    Compile the given C file using GCC and capture stderr output.

    Args:
        c_file_path (str): Absolute or relative path to the .c file

    Returns:
        tuple: (stderr_text: str, return_code: int)
               stderr_text contains all GCC error/warning messages
               return_code: 0 = success, non-zero = errors found
    """
    # Determine null device for this platform (discard binary output)
    null_device = 'NUL' if os.name == 'nt' else '/dev/null'

    # Run GCC — use list form (NOT shell=True) to prevent shell injection
    result = subprocess.run(
        ['gcc', '-Wall', '-Wextra', c_file_path, '-o', null_device],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True
    )
    return result.stderr, result.returncode

# ═══════════════════════════════════════════════════════════
# MODULE 3: ERROR PARSER MODULE
# ═══════════════════════════════════════════════════════════

def parse_gcc_output(gcc_stderr):
    """
    Parse raw GCC stderr output into a list of structured error dicts.

    Args:
        gcc_stderr (str): Full raw stderr string from GCC

    Returns:
        list of dicts, each with keys:
            file, line, col, type, msg, raw
    """
    errors = []
    for line in gcc_stderr.splitlines():
        line = line.strip()
        if not line:
            continue
        m = GCC_LINE_PATTERN.match(line)
        if m:
            errors.append({
                'file': m.group('file'),
                'line': int(m.group('line')),
                'col':  int(m.group('col')),
                'type': m.group('type'),
                'msg':  m.group('msg').strip(),
                'raw':  line
            })
    return errors

# ═══════════════════════════════════════════════════════════
# MODULE 4: AI REWRITING MODULE (Rule-Based Lookup)
# ═══════════════════════════════════════════════════════════

def find_matching_entry(gcc_msg):
    """
    Match a GCC error message against known error patterns.

    Args:
        gcc_msg (str): The core GCC error message text

    Returns:
        dict: Matching dataset entry, or None if no match found
    """
    for pattern, error_id in ERROR_PATTERNS:
        if pattern.search(gcc_msg):
            return DATASET.get(error_id, None)
    return None

def rewrite_error(error_dict):
    """
    Rewrite a single parsed GCC error into a beginner-friendly result.

    Args:
        error_dict (dict): Parsed error with file, line, col, type, msg, raw

    Returns:
        dict with: original_error, file, line, category,
                   explanation, fix, secure
    """
    msg   = error_dict['msg']
    entry = find_matching_entry(msg)

    if entry:
        return {
            'original_error': error_dict['raw'],
            'file':           error_dict['file'],
            'line':           error_dict['line'],
            'category':       entry['category'],
            'explanation':    entry['plain_explanation'],
            'fix':            entry['fix'],
            'secure':         entry['secure']
        }
    else:
        # Fallback for unknown errors
        return {
            'original_error': error_dict['raw'],
            'file':           error_dict['file'],
            'line':           error_dict['line'],
            'category':       'Unknown',
            'explanation':    (
                f"The compiler reported: {msg}\n"
                "This error is not yet in the AI Tutor database.\n"
                "Tip: Read the error message carefully, look at the "
                "indicated line number, and compare with a working example."
            ),
            'fix': (
                "Check the line number shown above.\n"
                "Compare your code carefully with a correct version.\n"
                "Search the error message online for more guidance."
            ),
            'secure': True
        }

# ═══════════════════════════════════════════════════════════
# MODULE 5 + 6: COMBINED — OUTPUT FORMATTER
# (Secure Fix validation is embedded in the dataset entries)
# ═══════════════════════════════════════════════════════════

def print_results(rewritten_errors, source_file):
    """
    Pretty-print all rewritten error results to the terminal.

    Args:
        rewritten_errors (list): List of rewrite result dicts
        source_file      (str):  Name of the C source file compiled
    """
    divider     = '═' * 62
    sub_divider = '─' * 62

    print(f"\n{divider}")
    print(f"  🤖  AI COMPILER TUTOR")
    print(f"  📄  File: {source_file}")

    if not rewritten_errors:
        print(f"  ✅  No errors! Your program compiled successfully.")
        print(f"{divider}\n")
        return

    count = len(rewritten_errors)
    print(f"  ⚠️   Found {count} issue{'s' if count > 1 else ''}  "
          f"— fix from the top down")
    print(f"{divider}")

    for i, err in enumerate(rewritten_errors, start=1):
        secure_label = "✅ Safe Fix" if err['secure'] else "⚠️  Review this fix carefully"

        print(f"\n  ❌  Issue #{i}  —  {err['category']} Error")
        print(f"  📁  File : {err['file']},  Line {err['line']}")
        print(f"  🔴  Original GCC output:")
        print(f"         {err['original_error']}")
        print(f"  {sub_divider}")

        print(f"  💡  What it means:")
        for line in err['explanation'].splitlines():
            print(f"       {line}")

        print(f"\n  🔧  How to fix it:")
        for line in err['fix'].splitlines():
            print(f"       {line}")

        print(f"\n  🔒  {secure_label}")
        print()

    if count > 1:
        print(f"  💬  Tip: Fix Issue #1 first — some later errors may")
        print(f"      disappear once the first mistake is corrected.")
    print(f"{divider}\n")

# ═══════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════

def compile_and_rewrite(c_file_path):
    """
    Full pipeline: compile → parse → rewrite → return results.

    Args:
        c_file_path (str): Path to the C source file

    Returns:
        tuple: (list of rewrite result dicts, raw gcc stderr str)
    """
    gcc_stderr, _ = compile_with_gcc(c_file_path)
    parsed_errors  = parse_gcc_output(gcc_stderr)
    # Skip 'note' lines (they are continuation notes, not standalone errors)
    parsed_errors  = [e for e in parsed_errors if e['type'] != 'note']
    rewritten      = [rewrite_error(e) for e in parsed_errors]
    return rewritten, gcc_stderr


if __name__ == '__main__':
    # ── Argument Validation ──────────────────────────────────────
    if len(sys.argv) < 2:
        print("\nUsage: python rewriter.py <your_c_file.c>")
        print("Example: python rewriter.py errors/err_001_missing_semicolon.c\n")
        sys.exit(1)

    input_file = sys.argv[1]

    if not os.path.isfile(input_file):
        print(f"\n[ERROR] File not found: {input_file}")
        print("  Please check the file path and try again.\n")
        sys.exit(1)

    # ── Run Pipeline ─────────────────────────────────────────────
    rewritten_errors, raw_gcc_output = compile_and_rewrite(input_file)

    # ── Display Results ───────────────────────────────────────────
    print_results(rewritten_errors, os.path.basename(input_file))
