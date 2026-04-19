# AI Compiler Tutor — Professor's Evaluation Guide

This folder contains the complete AI Compiler Tutor system (Weeks 1-14). 
Below are the commands to run each component during the evaluation.

### 1. Main AI Tutor (Unified Interface)
Run the tutor on any C file to see the rewritten error and safety fix:
```powershell
python src/main.py errors/err_001_missing_semicolon.c
```

### 2. Infinite Loop Detection (Logic Analyzer)
Test the dynamic timeout and static analysis features:
```powershell
python src/main.py errors/test_infinite_loop.c
```

### 3. Visual GUI (Bonus Implementation)
Open the professional dark-themed interface:
```powershell
python src/gui.py
```

### 4. Data Augmentation (Big Dataset)
Generate 660 entry variations for model training:
```powershell
python src/augment_dataset.py
```

### 5. AI Training (Fine-tuning)
Fine-tune the Flan-T5 model on the augmented dataset:
```powershell
py -3.12 src/model_trainer.py
```

### 6. Security Scanner
Scan for unsafe C functions:
```powershell
python src/secure_checker.py errors/err_001_missing_semicolon.c
```

---
*Note: Each .py file also has its own running command in the very first line of code.*
