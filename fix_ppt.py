import re

with open("generate_ppt.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Remove Table of Contents Slide
toc_pattern = re.compile(r"# ={61}\n# SLIDE 2 — TABLE OF CONTENTS\n# ={61}.*?slide_num\(sl,\s*2,\s*TOTAL\)\n", re.DOTALL)
content = toc_pattern.sub("", content)

# 2. Re-write the Progress Summary to Implementation
progress_pattern = re.compile(r"# ={61}\n# SLIDE 10 — PROGRESS SUMMARY \(Weeks 1-9\)\n# ={61}.*?slide_num\(sl,\s*10,\s*TOTAL\)\n", re.DOTALL)

implementation_slide = """# =============================================================
# SLIDE — IMPLEMENTATION DETAILS
# =============================================================
sl = blank_slide(prs)
set_bg(sl)
accent_line(sl)

add_text(sl, "Implementation Details",
         0.5, 0.3, 12, 0.75, size=34, bold=True, color=WHITE)

add_rect(sl, 0.4, 1.5, 5.8, 5.2, BOX_BG)
add_line(sl, 0.4, 1.5, 5.8, 0.07, ACCENT)
add_text(sl, "Core Implementation", 0.6, 1.7, 5.4, 0.5, size=20, bold=True, color=ACCENT)
add_text_multi(sl, [
    "Fully working AI Tutor Implemented.",
    "Pipeline successfully bridges GCC and AI fallback.",
    "",
    "Quantitative Improvements:",
    "  • +222% Clarity improvement over raw GCC",
    "  • +245% Actionability improvement",
    "  • Average score +2.25 points (+82%)",
], 0.6, 2.3, 5.4, 4.0, size=15, color=LIGHT_GRAY)

add_rect(sl, 6.5, 1.5, 6.4, 5.2, BOX_BG)
add_line(sl, 6.5, 1.5, 6.4, 0.07, ACCENT2)
add_text(sl, "System Integration", 6.7, 1.7, 6.0, 0.5, size=20, bold=True, color=ACCENT2)
add_text_multi(sl, [
    "Web Interface (Flask):",
    "  • Beautiful dark-mode UI for live interaction",
    "  • AST viewpoint and Security tabs enabled",
    "",
    "Performance Check:",
    "  • Security safeguards block 100% of unsafe code injections",
    "  • AST parser covers 100% of tested Beginner constructs"
], 6.7, 2.3, 6.0, 4.0, size=15, color=LIGHT_GRAY)

slide_num(sl, __SLIDE_NUM__, TOTAL)
"""

content = progress_pattern.sub(implementation_slide, content)

# 3. Add dynamic slide numbering
# We will replace TOTAL = 12 with a dynamic count
blocks = content.split("slide_num(sl,")
for i in range(1, len(blocks)):
    # replace the number with the new sequenced number ` i, TOTAL)`
    blocks[i] = re.sub(r"^\s*.*?,\s*TOTAL\)", f" {i}, TOTAL)", blocks[i])
    # replace __SLIDE_NUM__ if any
    blocks[i] = blocks[i].replace("__SLIDE_NUM__", str(i))

content = "slide_num(sl,".join(blocks)

# update TOTAL variable
content = re.sub(r"TOTAL\s*=\s*\d+", f"TOTAL = {len(blocks)-1}", content)

with open("generate_ppt.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Done!")
