# =============================================================
# FILE: src/model_trainer.py
# WEEK 9 — AI Model Training (Fine-tune Flan-T5)
# =============================================================
# WHAT THIS FILE DOES:
#   Reads our augmented_errors.json (600+ error entries).
#   Creates 4 training prompt variations per entry = 100 pairs.
#   Fine-tunes Google's Flan-T5-small model on these pairs.
#   Saves the trained model to models/flan-t5-compiler-tutor/
#
# WHERE TRAINING HAPPENS:
#   ✅ On YOUR OWN PC (locally) — no cloud, no internet needed
#      after the first download of the Flan-T5 base model.
#
# HOW TO RUN:
#   Step 1:  pip install transformers torch datasets sentencepiece
#   Step 2:  python src/model_trainer.py
#   Output:  models/flan-t5-compiler-tutor/  (saved trained model)
#
# HARDWARE:
#   CPU:  works fine, takes ~5-10 minutes for 25 examples
#   GPU:  much faster if you have one (automatic detection)
# =============================================================

import os
import json

BASE_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, 'phase4_dataset', 'augmented_errors.json')
MODEL_DIR    = os.path.join(BASE_DIR, 'models', 'flan-t5-compiler-tutor')

# ─────────────────────────────────────────────────────────────
# STEP 1: Build training pairs from the dataset
# ─────────────────────────────────────────────────────────────
def build_training_pairs(dataset):
    """
    Convert each dataset entry into 4 training examples.
    This is called DATA AUGMENTATION — more examples = better model.

    For each error entry we create 4 variations:
      Pair 1: Explain the error
      Pair 2: How to fix
      Pair 3: What does this mean?
      Pair 4: C error help
    """
    pairs = []  # list of (input_text, output_text)

    for entry in dataset:
        gcc_err = entry['gcc_error']
        expl    = entry['plain_explanation']
        fix     = entry['fix']

        # 4 prompt variations for the same entry
        pairs.append((
            f"Explain this C compiler error to a beginner: {gcc_err}",
            expl
        ))
        pairs.append((
            f"How do I fix this C error: {gcc_err}",
            fix
        ))
        pairs.append((
            f"What does this C error mean: {gcc_err}",
            expl
        ))
        pairs.append((
            f"C error help for beginner: {gcc_err}",
            fix
        ))

    return pairs   # entries × 4 prompts

# ─────────────────────────────────────────────────────────────
# STEP 2: Tokenize for T5 (convert text to numbers)
# ─────────────────────────────────────────────────────────────
def tokenize_pairs(pairs, tokenizer, max_input=128, max_output=128):
    """
    Tokenization = converting text into number sequences.
    The T5 model cannot read text directly — it reads lists of integers.
    This function converts all our training pairs into that format.
    """
    encodings = []
    for input_text, output_text in pairs:
        # Tokenize input
        input_enc = tokenizer(
            input_text,
            max_length=max_input,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        # Tokenize output (called labels in seq2seq)
        label_enc = tokenizer(
            output_text,
            max_length=max_output,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        encodings.append({
            'input_ids'      : input_enc['input_ids'].squeeze(),
            'attention_mask' : input_enc['attention_mask'].squeeze(),
            'labels'         : label_enc['input_ids'].squeeze()
        })
    return encodings

# ─────────────────────────────────────────────────────────────
# STEP 3: Create a PyTorch Dataset wrapper
# ─────────────────────────────────────────────────────────────
def make_torch_dataset(encodings):
    """
    Wraps our encodings into a PyTorch Dataset so the
    Trainer can iterate over batches during training.
    """
    try:
        import torch
        class CompilerErrorDataset(torch.utils.data.Dataset):
            def __init__(self, data):
                self.data = data
            def __len__(self):
                return len(self.data)
            def __getitem__(self, idx):
                return self.data[idx]
        return CompilerErrorDataset(encodings)
    except ImportError:
        raise ImportError("torch not found. Run: pip install torch")

# ─────────────────────────────────────────────────────────────
# STEP 4: Main training function
# ─────────────────────────────────────────────────────────────
def train():
    print("=" * 60)
    print("  WEEK 9 — AI Model Training (Flan-T5)")
    print("  Training runs on: YOUR PC (locally)")
    print("=" * 60)

    # ── Load dataset ──────────────────────────────────────────
    if not os.path.isfile(DATASET_PATH):
        print("  ERROR: annotated_errors.json not found!")
        print("  Run: python src/collect_errors.py first.")
        return

    with open(DATASET_PATH, 'r') as f:
        dataset = json.load(f)
        
    # [OPTIMIZATION] Processing the full massive scale 11k+ dataset
    # We will let the script load it entirely to prove it handles the huge JSON

    print(f"\n  Dataset loaded: {len(dataset)} entries (massive scale)")

    # ── Build training pairs ──────────────────────────────────
    pairs = build_training_pairs(dataset)
    print(f"  Training pairs (4 per entry): {len(pairs)}")

    # ── Load Flan-T5 model and tokenizer ─────────────────────
    print("\n  Loading Flan-T5 model from HuggingFace...")
    print("  (Downloads ~300 MB on first run, cached after)")
    try:
        from transformers import (
            T5ForConditionalGeneration,
            T5Tokenizer,
            Seq2SeqTrainer,
            Seq2SeqTrainingArguments,
            DataCollatorForSeq2Seq
        )
    except ImportError:
        print("\n  ERROR: transformers library not installed!")
        print("  Run:   pip install transformers torch datasets sentencepiece")
        return

    MODEL_NAME = "google/flan-t5-small"   # small model: ~300MB
    tokenizer  = T5Tokenizer.from_pretrained(MODEL_NAME)
    model      = T5ForConditionalGeneration.from_pretrained(MODEL_NAME)

    print(f"  Model loaded: {MODEL_NAME}")

    # ── Tokenize all pairs ────────────────────────────────────
    print("\n  Tokenizing training pairs...")
    encodings   = tokenize_pairs(pairs, tokenizer)
    train_data  = make_torch_dataset(encodings)

    # ── Configure training ────────────────────────────────────
    # These settings are for small local training.
    # EPOCHS = how many full rounds through the data.
    # BATCH_SIZE = how many examples per step (lower = less RAM).
    # Using max_steps safely limits the compute time during live presentations 
    # without crashing local CPUs doing 40,000 batches.
    training_args = Seq2SeqTrainingArguments(
        output_dir               = MODEL_DIR,
        num_train_epochs         = 1,          
        max_steps                = 150,        # Process a targeted burst of the 11k to complete quickly
        per_device_train_batch_size = 8,       
        save_strategy            = "epoch",    # save checkpoint each epoch
        logging_steps            = 10,         # print loss every 10 steps
        predict_with_generate    = True,
        fp16                     = False,      # use True only if GPU+CUDA
        report_to                = "none",     # no wandb / mlflow
    )

    trainer = Seq2SeqTrainer(
        model            = model,
        args             = training_args,
        train_dataset    = train_data,
        processing_class = tokenizer,            # newer transformers: use processing_class
    )

    # ── TRAIN ─────────────────────────────────────────────────
    print("\n  Starting training...")
    print("  (This takes ~5-10 min on CPU, faster on GPU)")
    print()
    trainer.train()

    # ── Save trained model ────────────────────────────────────
    os.makedirs(MODEL_DIR, exist_ok=True)
    trainer.save_model(MODEL_DIR)
    tokenizer.save_pretrained(MODEL_DIR)

    print(f"\n  ✅ Training complete!")
    print(f"  Model saved to: models/flan-t5-compiler-tutor/")
    print(f"\n  Next step — use the model:")
    print(f"  python src/model_inference.py")
    print("=" * 60)

# ─────────────────────────────────────────────────────────────
# EXPLAIN CONCEPT (no libraries needed)
# ─────────────────────────────────────────────────────────────
def explain_concept():
    """Print a clear explanation of what training does."""
    print("""
  WHAT IS TRAINING?
  -----------------
  Training = showing the AI thousands of examples so it learns
  the pattern between inputs and correct outputs.

  HOW T5 LEARNS:
  --------------
  Step 1: Model reads input:  "Explain C error: expected ';'"
  Step 2: Model GUESSES the output (wrong at first)
  Step 3: We measure how WRONG the guess was (called 'loss')
  Step 4: Adjust model weights to reduce that error
  Step 5: Repeat for all 100 pairs x 3 epochs = 300 steps

  WHERE TRAINING RUNS:
  --------------------
  [LOCAL] YOUR OWN MACHINE
  - Downloads flan-t5-small (~300MB) from HuggingFace once
  - All training happens on your CPU (or GPU if available)
  - No internet required after first download
  - Model saved in: models/flan-t5-compiler-tutor/

  DATASET SIZE:
  -------------
  600+ entries x 4 prompts = 2400+ training pairs
""")

def main():
    explain_concept()
    train()

if __name__ == '__main__':
    main()
