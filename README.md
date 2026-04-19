# AI-Based Compiler Error Message Rewriting — AI Tutor
## Complete Project Guide

---

## 🗂️ Project Structure

```
cd ag/
│
├── README.md                        ← This file
│
├── src/                             ← ★ ALL PYTHON SOURCE CODE
│   ├── main.py                      ← Unified CLI entry point (use this)
│   ├── collect_errors.py            ← Script 1: Auto-collect GCC errors
│   ├── dataset_builder.py           ← Script 2: Build and validate dataset
│   ├── secure_checker.py            ← Script 3: Security scanner
│   ├── ast_parser.py                ← Script 4: AST-level code analysis
│   ├── model_trainer.py             ← Script 5: Fine-tune Flan-T5 model
│   ├── model_inference.py           ← Script 6: Run AI model
│   ├── evaluate.py                  ← Script 7: Evaluation report
│   └── gui.py                       ← Script 9: Visual GUI demo (bonus!)
│
├── phase5_ai_rewriting/
│   └── rewriter.py                  ← Original standalone rewriter
│
├── errors/                          ← 10 intentional C error programs
├── phase1_understanding/            ← Weeks 1-2 documentation
├── phase2_design/                   ← Weeks 3-4 documentation
├── phase3_error_analysis/           ← Weeks 5-6 documentation
├── phase4_dataset/
│   └── annotated_errors.json        ← ★ Core dataset (10 entries)
├── phase6_evaluation/               ← Weeks 11-12 documentation
└── phase7_final/
    └── run_all_tests.bat            ← Windows demo script
```

---

## ⚡ Quick Start (Most Important Commands)

### Run the AI Tutor on any C file:
```bash
python src/main.py errors/err_001_missing_semicolon.c
```

### Check for Infinite Loops (Dynamic Timeout):
```bash
python src/main.py errors/test_infinite_loop.c
```
*Note: If the code runs for >2s, it will automatically terminate and report an "Infinite Loop".*

### Launch the visual GUI demo:
```bash
python src/gui.py
```

### Run evaluation report (shows GCC vs AI Tutor scores):
```bash
python src/evaluate.py
python src/evaluate.py --full
```

---

## 📋 All Source Files Explained

| File | Script # | What It Does |
|------|----------|--------------|
| `src/main.py` | 8 | **Main entry point** — runs all features |
| `src/augment_dataset.py` | 2.1 | **NEW: Generates 660+ variations** of errors |
| `src/executor.py` | 4.1 | **NEW: Detects Infinite Loops** (2s timeout) |
| `src/collect_errors.py` | 1 | Compiles all 10 C programs, saves raw GCC output |
| `src/dataset_builder.py` | 2 | Validates dataset, security check, add new entries |
| `src/secure_checker.py` | 3 | Scans C code for `gets()`, `strcpy()`, etc. |
| `src/ast_parser.py` | 4 | Shows AST node type + **Static Loop Check** |
| `src/model_trainer.py` | 5 | Fine-tunes Flan-T5 on **660+ entries** |
| `src/model_inference.py` | 6 | Uses the trained model to explain new errors |
| `src/evaluate.py` | 7 | Scores AI Tutor vs GCC on 4 criteria |
| `src/gui.py` | 9 | Desktop GUI app (dark-themed, 4 tabs) |

---

## 🔧 Step-by-Step Workflow

### Step 1 — Collect errors (Phase 3, Week 6):
```bash
python src/collect_errors.py
```
→ Compiles all 10 error files, saves `raw_gcc_output.json`

### Step 2 — Validate dataset (Phase 4, Week 8):
```bash
python src/main.py --dataset
```
→ Checks all 10 entries for missing fields, security violations

### Step 3 — Run the AI Tutor (Phase 5, Week 10):
```bash
python src/main.py errors/err_003_incompatible_types.c
```

### Step 4 — Security scan (Phase 6, Week 11):
```bash
python src/secure_checker.py errors/err_001_missing_semicolon.c
```

### Step 5 — Evaluate (Phase 6, Week 12):
```bash
python src/evaluate.py --full
```

### Step 1 — Augment (Generate 660+ datasets):
```bash
python src/augment_dataset.py
```
→ Creates `phase4_dataset/augmented_errors.json`.

### Step 2 — Train AI model (Phase 5, optional):
```bash
pip install transformers torch datasets sentencepiece
python src/model_trainer.py
```
→ Trains on 2,400+ prompt-response pairs.

### Step 3 — Run the GUI Demo:
```bash
python src/gui.py
```

---

## 🔒 Security Features

The AI Tutor NEVER suggests these unsafe C functions:
- ❌ `gets()` → use `fgets()` instead
- ❌ `strcpy()` → use `strncpy()` instead
- ❌ `scanf("%s")` without width → use `scanf("%49s")`
- ❌ Blind type casts → explains root cause instead

---

## 📊 Results Summary

| Metric | GCC Default | AI Tutor | Improvement |
|--------|-------------|----------|-------------|
| Clarity | 1.55 / 5 | 5.0 / 5 | **+222%** |
| Actionability | 1.45 / 5 | 5.0 / 5 | **+245%** |
| Accuracy | 5.0 / 5 | 5.0 / 5 | Same |
| Security | 3.0 / 5 | 5.0 / 5 | **+67%** |

---

## 🤖 AI Model Details

- **Primary**: Rule-based matching against `annotated_errors.json`
- **Fallback**: Fine-tuned Google Flan-T5 Transformer
- **Training**: Seq2Seq with data augmentation (4 prompt variations)
- **Offline**: Works 100% without internet after first download

---

## 📦 Requirements

**Always required:**
- Python 3.7+
- GCC (MinGW-w64 on Windows, `sudo apt install gcc` on Linux)

**Only for AI model training/inference:**
```bash
pip install transformers torch datasets sentencepiece
```

**GUI — built into Python:**
- `tkinter` (already installed with Python, no pip needed)
