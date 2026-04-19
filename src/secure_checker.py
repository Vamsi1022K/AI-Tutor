# =============================================================
# FILE: src/secure_checker.py
# WEEK 11 — Security Check
# =============================================================
# WHAT THIS FILE DOES:
#   Scans any C source file for dangerous functions.
#   Tells you which line uses the unsafe function and what to
#   use instead.
#
# HOW TO RUN:
#   python src/secure_checker.py errors/err_001_missing_semicolon.c
#   python src/secure_checker.py           (scans all 10 files)
# =============================================================

import os    # file paths
import re    # pattern matching
import sys   # command-line arguments

# ── Paths ─────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ERRORS_DIR = os.path.join(BASE_DIR, 'errors')

# ── Security rules ────────────────────────────────────────────
# Each rule: (pattern, why_it_is_bad, what_to_use_instead)
RULES = [
    (
        re.compile(r'\bgets\s*\('),
        "gets() has NO limit — attacker can overflow buffer",
        "Use: fgets(buffer, sizeof(buffer), stdin)"
    ),
    (
        re.compile(r'\bstrcpy\s*\('),
        "strcpy() doesn't check destination size",
        "Use: strncpy(dest, src, sizeof(dest)-1)"
    ),
    (
        re.compile(r'scanf\s*\(\s*"%s"'),
        'scanf("%s") reads unlimited input',
        'Use: scanf("%49s", str) with a width limit'
    ),
    (
        re.compile(r'\bsprintf\s*\('),
        "sprintf() can overflow the buffer",
        "Use: snprintf(buf, sizeof(buf), format, ...)"
    ),
    (
        re.compile(r'\bstrcat\s*\('),
        "strcat() doesn't check destination size",
        "Use: strncat(dest, src, sizeof(dest)-strlen(dest)-1)"
    ),
    (
        re.compile(r'\bsystem\s*\('),
        "system() runs shell commands — injection risk",
        "Avoid system(); use proper API functions instead"
    ),
]

def scan_file(filepath):
    """Scan one C file. Return list of found issues."""
    issues = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
    except OSError:
        return []

    for lineno, line in enumerate(lines, start=1):
        # Skip comment lines
        if line.strip().startswith('//') or line.strip().startswith('*'):
            continue
        # Check each security rule
        for pattern, reason, fix in RULES:
            if pattern.search(line):
                issues.append({
                    'line'  : lineno,
                    'code'  : line.strip(),
                    'reason': reason,
                    'fix'   : fix
                })
    return issues

def print_report(filepath, issues):
    """Print security scan results for one file."""
    fname = os.path.basename(filepath)
    print(f"\n{'='*55}")
    print(f"  Security Scan: {fname}")
    print(f"{'='*55}")

    if not issues:
        print("  ✅ No security issues found.")
        return

    for i, issue in enumerate(issues, 1):
        print(f"\n  Issue #{i} on Line {issue['line']}:")
        print(f"  Code   : {issue['code'][:55]}")
        print(f"  Problem: {issue['reason']}")
        print(f"  Fix    : {issue['fix']}")

    print(f"\n  Total issues: {len(issues)}")

def main():
    print("=" * 55)
    print("  WEEK 11 — Security Checker")
    print("=" * 55)

    if len(sys.argv) >= 2:
        # Scan a specific file provided as argument
        target = sys.argv[1]
        if not os.path.isfile(target):
            print(f"  ERROR: File not found: {target}")
            sys.exit(1)
        issues = scan_file(target)
        print_report(target, issues)
    else:
        # Scan all 10 error files
        c_files = sorted(f for f in os.listdir(ERRORS_DIR) if f.endswith('.c'))
        total   = 0
        for fname in c_files:
            fpath  = os.path.join(ERRORS_DIR, fname)
            issues = scan_file(fpath)
            print_report(fpath, issues)
            total += len(issues)
        print(f"\n  Total issues across all files: {total}")

if __name__ == '__main__':
    main()
