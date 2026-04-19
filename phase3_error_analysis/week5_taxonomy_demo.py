# =====================================================
# WEEK 5 — Error Taxonomy
# Shows the 10 GCC error types with category and cause
# Run: python phase3_error_analysis/week5_taxonomy_demo.py
# =====================================================

# All 10 error types stored as a list of dictionaries
ERRORS = [
    {"id":"E001","category":"Syntax",      "name":"Missing Semicolon",           "cause":"Statement not ended with ;"},
    {"id":"E002","category":"Declaration", "name":"Undeclared Variable",          "cause":"Variable used without declaring first"},
    {"id":"E003","category":"Type",        "name":"Incompatible Types",           "cause":"Assigning string to int, etc."},
    {"id":"E004","category":"Declaration", "name":"Implicit Function Declaration","cause":"Missing #include for function"},
    {"id":"E005","category":"Syntax",      "name":"Missing Closing Parenthesis",  "cause":"( not matched with )"},
    {"id":"E006","category":"Syntax",      "name":"Too Few Arguments",            "cause":"Function called with fewer args"},
    {"id":"E009","category":"Declaration", "name":"Variable Redefinition",        "cause":"Same variable declared twice"},
    {"id":"E010","category":"Scope",       "name":"Void Returns Value",           "cause":"void function has return value"},
    {"id":"E011","category":"Type",        "name":"Format Mismatch",              "cause":"%d used for double, etc."},
    {"id":"E015","category":"Syntax",      "name":"Missing Closing Brace",        "cause":"{ not matched with }"},
]

def show_taxonomy():
    print("=" * 55)
    print("  WEEK 5 — GCC Error Taxonomy (10 Error Types)")
    print("=" * 55)
    print(f"  {'ID':6} {'Category':14} {'Name':28} Cause")
    print(f"  {'─'*6} {'─'*14} {'─'*28} {'─'*25}")
    for e in ERRORS:
        print(f"  {e['id']:6} {e['category']:14} {e['name']:28} {e['cause']}")

def count_by_category():
    print("\n  Errors per category:")
    cats = {}
    for e in ERRORS:
        cats[e['category']] = cats.get(e['category'], 0) + 1
    for cat, n in sorted(cats.items()):
        print(f"  {cat:14} {'█'*n} ({n})")

if __name__ == '__main__':
    show_taxonomy()
    count_by_category()
    print(f"\n  Total: {len(ERRORS)} error types documented")
    print("=" * 55)
