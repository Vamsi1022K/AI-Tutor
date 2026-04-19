# =============================================================
# FILE: src/evaluate.py
# WEEK 12 — Evaluation Report
# =============================================================
# WHAT THIS FILE DOES:
#   Scores GCC error messages vs AI Tutor messages.
#   Uses 4 criteria: Clarity, Actionable, Accuracy, Security.
#   Each score is out of 5.
#   Prints a comparison table and overall improvement.
#
# HOW TO RUN:
#   python src/evaluate.py
# =============================================================

# No imports needed — all data is defined here directly.

# ── Scoring data ───────────────────────────────────────────────
# For each error: what GCC scores vs what the AI Tutor scores.
# Scores are out of 5 (1=bad, 5=excellent).
#
# Criteria explained:
#   Clarity    — Can a beginner understand the message?
#   Actionable — Does it say exactly what to do?
#   Accuracy   — Is the explanation factually correct?
#   Security   — Does the fix use safe coding practices?

SCORES = [
    #  ID      Category        Clarity  Action  Accuracy  Security
    #                         GCC  AI   GCC  AI  GCC  AI  GCC  AI
    ("E001", "Syntax",        [1.5, 5], [2,  5], [5, 5], [3, 5]),
    ("E002", "Declaration",   [2,   5], [1.5,5], [5, 5], [3, 5]),
    ("E003", "Type",          [1,   5], [1,  5], [5, 5], [3, 5]),
    ("E004", "Declaration",   [1,   5], [1,  5], [5, 5], [3, 5]),
    ("E005", "Syntax",        [1.5, 5], [2,  5], [5, 5], [3, 5]),
    ("E006", "Syntax",        [3,   5], [2,  5], [5, 5], [3, 5]),
    ("E009", "Declaration",   [2.5, 5], [2,  5], [5, 5], [3, 5]),
    ("E010", "Scope",         [1.5, 5], [1.5,5], [5, 5], [3, 5]),
    ("E011", "Type",          [2,   5], [1.5,5], [5, 5], [3, 5]),
    ("E015", "Syntax",        [1.5,4.75],[1.5,4.75],[5,5],[3, 5]),
]

def average(scores_list):
    """Calculate average of a list of numbers."""
    return sum(scores_list) / len(scores_list)

def main():
    print("=" * 60)
    print("  WEEK 12 — Evaluation: GCC vs AI Tutor")
    print("  Scoring: 1=Very Poor  3=OK  5=Excellent")
    print("=" * 60)

    print(f"\n  {'ID':6} {'Category':12} {'GCC Avg':>9} {'AI Avg':>8} {'Better?':>8}")
    print(f"  {'─'*6} {'─'*12} {'─'*9} {'─'*8} {'─'*8}")

    gccs = []  # collect all GCC averages
    ais  = []  # collect all AI averages

    for row in SCORES:
        eid, category, clarity, action, accuracy, security = row

        # Calculate averages for this error
        gcc_avg = average([clarity[0], action[0], accuracy[0], security[0]])
        ai_avg  = average([clarity[1], action[1], accuracy[1], security[1]])
        diff    = ai_avg - gcc_avg
        symbol  = "✅" if diff > 0 else "="

        print(f"  {eid:6} {category:12} {gcc_avg:>9.2f} {ai_avg:>8.2f} {symbol} +{diff:.2f}")

        gccs.append(gcc_avg)
        ais.append(ai_avg)

    # Overall averages
    total_gcc = average(gccs)
    total_ai  = average(ais)
    total_imp = total_ai - total_gcc
    pct       = (total_imp / total_gcc) * 100

    print(f"\n  {'─'*50}")
    print(f"  {'OVERALL':6} {'':12} {total_gcc:>9.2f} {total_ai:>8.2f}  +{total_imp:.2f}")
    print(f"\n  AI Tutor is {pct:.0f}% better than GCC messages overall.")

    # Per-criteria summary
    print(f"\n{'='*60}")
    print(f"  Per-Criteria Summary")
    print(f"{'='*60}")

    criteria_names = ["Clarity", "Actionable", "Accuracy", "Security"]
    criteria_index = [0, 1, 2, 3]   # index into each row's score pairs

    for i, name in zip(criteria_index, criteria_names):
        all_scores_row = SCORES
        gcc_vals = [row[2 + i][0] for row in all_scores_row]
        ai_vals  = [row[2 + i][1] for row in all_scores_row]
        g = average(gcc_vals)
        a = average(ai_vals)
        bar_gcc = "█" * int(g)
        bar_ai  = "█" * int(a)
        print(f"\n  {name}:")
        print(f"    GCC     : {bar_gcc:<5} ({g:.2f}/5)")
        print(f"    AI Tutor: {bar_ai:<5} ({a:.2f}/5)")

    print(f"\n{'='*60}")
    print(f"  Week 12 Evaluation Complete")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    main()
