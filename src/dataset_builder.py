# =============================================================
# FILE: src/dataset_builder.py
# WEEK 8 — Dataset Validation
# =============================================================
# WHAT THIS FILE DOES:
#   Loads annotated_errors.json (our dataset).
#   Checks every entry has all required fields.
#   Checks that no fix uses dangerous functions like gets().
#   Prints a summary of the dataset.
#
# HOW TO RUN:
#   python src/dataset_builder.py
# =============================================================

import os    # file paths
import json  # read JSON file
import re    # pattern matching (for security check)

# ── Paths ─────────────────────────────────────────────────────
BASE_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, 'phase4_dataset', 'annotated_errors.json')

# ── Fields every dataset entry must have ─────────────────────
REQUIRED_FIELDS = ['id', 'category', 'gcc_error',
                   'plain_explanation', 'fix', 'secure']

# ── Unsafe functions we never want in any fix ─────────────────
UNSAFE = [r'\bgets\s*\(', r'\bstrcpy\s*\(', r'scanf\s*\(\s*"%s"']

def check_security(text):
    """Return True if fix text contains any unsafe function."""
    for pattern in UNSAFE:
        if re.search(pattern, text, re.IGNORECASE):
            return True   # unsafe found
    return False          # all safe

def main():
    print("=" * 50)
    print("  WEEK 8 — Dataset Validation Report")
    print("=" * 50)

    # Load dataset
    if not os.path.isfile(DATASET_PATH):
        print("  ERROR: annotated_errors.json not found!")
        return

    with open(DATASET_PATH, 'r') as f:
        dataset = json.load(f)

    print(f"\n  Total entries in dataset: {len(dataset)}\n")

    passed = 0
    failed = 0

    for entry in dataset:
        eid    = entry.get('id', '???')
        errors = []

        # Check all required fields exist
        for field in REQUIRED_FIELDS:
            if field not in entry or not str(entry[field]).strip():
                errors.append(f"Missing field: {field}")

        # Check fix text for unsafe functions
        fix_text = entry.get('fix', '') + entry.get('fixed_code', '')
        if check_security(fix_text):
            errors.append("Fix uses unsafe function (gets/strcpy/scanf %s)!")

        # Print result for this entry
        if errors:
            print(f"  FAIL [{eid}]")
            for e in errors:
                print(f"       ⚠ {e}")
            failed += 1
        else:
            cat    = entry.get('category', '?')
            secure = "[OK]" if entry.get('secure') else "[!!]"
            print(f"  PASS [{eid}] {cat:12s} {secure}")
            passed += 1

    # Summary
    print(f"\n  Results: {passed} passed, {failed} failed")

    # Show category counts
    print(f"\n  Errors by category:")
    cats = {}
    for entry in dataset:
        c = entry.get('category', 'Unknown')
        cats[c] = cats.get(c, 0) + 1
    for cat, count in sorted(cats.items()):
        bar = '#' * count
        print(f"  {cat:15s} {bar} ({count})")

    print("\n" + "=" * 50)

if __name__ == '__main__':
    main()
