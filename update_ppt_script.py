import re

with open("generate_ppt.py", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Update TOTAL
text = re.sub(r'TOTAL = 10', 'TOTAL = 12', text)

# 2. Update TOC items
old_toc = """items = [
    ("01", "Definition & Problem Statement"),
    ("02", "Objectives"),
    ("03", "Novelty of the Approach"),
    ("04", "System Architecture"),
    ("05", "Error Taxonomy (5 Categories)"),
    ("06", "Dataset Design  (Week 8)"),
    ("07", "AST Analysis  (Week 7)"),
    ("08", "AI Tutor Pipeline  (Week 9 — Code)"),
    ("09", "Sample Output  (Week 9 — Run)"),
    ("10", "Progress Summary  (Weeks 1 – 9)"),
]"""

new_toc = """items = [
    ("01", "Definition & Problem Statement"),
    ("02", "Objectives"),
    ("03", "Novelty of the Approach"),
    ("04", "System Architecture"),
    ("05", "Error Taxonomy"),
    ("06", "Dataset Design"),
    ("07", "AST Analysis"),
    ("08", "AI Tutor Pipeline"),
    ("09", "Sample Output"),
    ("10", "Progress Summary"),
    ("11", "Security Rules"),
    ("12", "Model Training (Flan-T5)"),
]"""
text = text.replace(old_toc, new_toc)

# 3. Modify Novelties (Remove Icons)
old_novelty = """novelties = [
    ("🔗", "Compiler-Integrated",
     "Sits between GCC and the student — not a separate checker. Uses actual GCC output, so accuracy is 100% real."),
    ("🧠", "Hybrid AI",
     "Rule-based matching (instant, offline) + fine-tuned Flan-T5 Transformer (handles novel/unseen errors). Best of both worlds."),
    ("🔒", "Security-Aware Fixes",
     "Unlike Stack Overflow or generic tutors, every suggested fix is checked against a blocklist of unsafe C functions."),
    ("🌲", "AST-Level Explanation",
     "Maps each error back to its Abstract Syntax Tree node (VarDecl, CallExpr, etc.) for a deeper, compiler-theory explanation."),
    ("📊", "Quantitative Evaluation",
     "Scores AI Tutor vs GCC on 4 rubrics across all 10 error types. Proves improvement with data, not just anecdote."),
    ("🖥️", "Full GUI Demo",
     "Dedicated dark-themed Tkinter GUI with 4 tabs: AI Tutor, AST View, Security Scan, Evaluation — all usable live."),
]

for i, (icon, title, desc) in enumerate(novelties):
    col = i % 3
    row = i // 3
    x = 0.4 + col * 4.27
    y = 1.5 + row * 2.7
    add_rect(sl, x, y, 4.0, 2.4, BOX_BG)
    add_line(sl, x, y+2.33, 4.0, 0.07, ACCENT2)
    add_text(sl, icon, x+0.1, y+0.1, 0.55, 0.6, size=22, color=WHITE)
    add_text(sl, title, x+0.7, y+0.12, 3.2, 0.5, size=15, bold=True, color=ACCENT2)
    add_text(sl, desc,  x+0.1, y+0.7,  3.8, 1.6, size=12, color=LIGHT_GRAY)"""

new_novelty = """novelties = [
    ("Compiler-Integrated",
     "Sits between GCC and the student — not a separate checker. Uses actual GCC output, so accuracy is 100% real."),
    ("Hybrid AI",
     "Rule-based matching (instant, offline) + fine-tuned Flan-T5 Transformer (handles novel/unseen errors). Best of both worlds."),
    ("Security-Aware Fixes",
     "Unlike Stack Overflow or generic tutors, every suggested fix is checked against a blocklist of unsafe C functions."),
    ("AST-Level Explanation",
     "Maps each error back to its Abstract Syntax Tree node (VarDecl, CallExpr, etc.) for a deeper, compiler-theory explanation."),
    ("Quantitative Evaluation",
     "Scores AI Tutor vs GCC on 4 rubrics across all 10 error types. Proves improvement with data, not just anecdote."),
    ("Full GUI Demo",
     "Dedicated dark-themed Tkinter GUI with 4 tabs: AI Tutor, AST View, Security Scan, Evaluation — all usable live."),
]

for i, (title, desc) in enumerate(novelties):
    col = i % 3
    row = i // 3
    x = 0.4 + col * 4.27
    y = 1.5 + row * 2.7
    add_rect(sl, x, y, 4.0, 2.4, BOX_BG)
    add_line(sl, x, y+2.33, 4.0, 0.07, ACCENT2)
    add_text(sl, title, x+0.2, y+0.15, 3.6, 0.5, size=17, bold=True, color=ACCENT2)
    add_text(sl, desc,  x+0.2, y+0.65, 3.6, 1.6, size=12, color=LIGHT_GRAY)"""
text = text.replace(old_novelty, new_novelty)

# 4. Insert New Slides before "# ── Save ──────────────────────────────────────────────────"
save_marker = "# ── Save ──────────────────────────────────────────────────"

new_slides = """# =============================================================
# SLIDE 11 — SECURITY
# =============================================================
sl = blank_slide(prs)
set_bg(sl)
accent_line(sl)

add_text(sl, "Security Blocklist & Enforcement",
         0.5, 0.3, 12, 0.75, size=34, bold=True, color=WHITE)

add_rect(sl, 0.4, 1.5, 12.5, 5.2, BOX_BG)
add_line(sl, 0.4, 1.5, 12.5, 0.08, RED)

add_text(sl, "Safe Code Guardrails", 0.6, 1.7, 5.0, 0.5, size=24, bold=True, color=RED)
add_text_multi(sl, [
    "The AI restricts usage of inherently unsafe C functions prone to memory corruption.",
    "If an unsafe function is typed by the student—or predicted by the model—the engine highlights it and blocks it.",
    "",
    "Rules Enforced:",
    "  • gets()                 → Reject (Use fgets instead)",
    "  • strcpy() / strcat()    → Reject (Use strncpy / strncat instead)",
    "  • scanf(\\\"%s\\\")           → Reject (Enforce width like scanf(\\\"%49s\\\"))",
    "  • system()               → Reject (Shell Injection risk)",
], 0.6, 2.5, 12.0, 4.0, size=18, color=LIGHT_GRAY, line_spacing=1.5)

slide_num(sl, 11, TOTAL)

# =============================================================
# SLIDE 12 — MODEL TRAINING
# =============================================================
sl = blank_slide(prs)
set_bg(sl)
accent_line(sl)

add_text(sl, "Model Training (Flan-T5)",
         0.5, 0.3, 12, 0.75, size=34, bold=True, color=WHITE)

add_rect(sl, 0.4, 1.5, 5.8, 5.2, BOX_BG)
add_line(sl, 0.4, 1.5, 5.8, 0.07, ACCENT)
add_text(sl, "Training Pipeline & Setup", 0.6, 1.7, 5.4, 0.5, size=20, bold=True, color=ACCENT)
add_text_multi(sl, [
    "Google Flan-T5 was fine-tuned locally using PyTorch and Hugging Face Transformers.",
    "",
    "Dataset Augmentation:",
    "Expanded 33 base errors into ~11,550 variations.",
    "Prompt Formats:",
    "  • 'Explain this C compiler error...'",
    "  • 'Fix this GCC warning...'",
    "",
    "Framework: Seq2Seq Trainer (Epochs: 3, LR: 3e-4)"
], 0.6, 2.3, 5.4, 4.0, size=15, color=LIGHT_GRAY)

add_rect(sl, 6.5, 1.5, 6.4, 5.2, BOX_BG)
add_line(sl, 6.5, 1.5, 6.4, 0.07, ACCENT2)
add_text(sl, "Inference Architecture", 6.7, 1.7, 6.0, 0.5, size=20, bold=True, color=ACCENT2)
add_text_multi(sl, [
    "Fallback Method:",
    "The neural model is only invoked when regex heuristics yield zero algorithmic matches.",
    "",
    "Performance Stats:",
    "  • Inference Time: < 15 seconds (Local CPU)",
    "  • Memory Footprint: ~300MB",
    "  • Environment: Completely offline (Private execution).",
], 6.7, 2.3, 6.0, 4.0, size=15, color=LIGHT_GRAY)

slide_num(sl, 12, TOTAL)

"""
text = text.replace(save_marker, new_slides + save_marker)

with open("generate_ppt.py", "w", encoding="utf-8") as f:
    f.write(text)

print("generate_ppt.py successfully updated!")
