# =============================================================
# FILE: src/model_inference.py
# WEEK 10 — Using a Trained AI Model (Advanced / Optional)
# =============================================================
# NOTE: This is the AI fallback for errors NOT in our dataset.
# The main AI Tutor (main.py) uses rule-based matching first.
# This file is only used when no rule matches.
#
# HOW IT WORKS:
#   If GCC produces an error we haven't seen before,
#   we ask the T5 model to generate an explanation.
#
# TO USE THIS:
#   1. First run: pip install transformers torch
#   2. Then run:  python src/model_trainer.py  (to train the model)
#   3. Then this file loads the saved model automatically.
# =============================================================

import os

MODEL_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'models', 'flan-t5-compiler-tutor'
)

def explain_with_ai(gcc_error_msg):
    """
    Use the fine-tuned T5 model to explain an unknown GCC error.
    Falls back gracefully if the model / library is not installed.
    """
    # Check if model exists
    if not os.path.isdir(MODEL_DIR):
        return (
            "[AI Fallback not available — model not trained yet]\n"
            "Run: pip install transformers torch\n"
            "Then: python src/model_trainer.py"
        )

    # Try loading the model
    try:
        from transformers import T5ForConditionalGeneration, T5Tokenizer
        tokenizer = T5Tokenizer.from_pretrained(MODEL_DIR)
        model     = T5ForConditionalGeneration.from_pretrained(MODEL_DIR)
        model.eval()

        prompt = f"Explain this C compiler error to a beginner: {gcc_error_msg}"
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=128)

        import torch
        with torch.no_grad():
            out = model.generate(inputs["input_ids"], max_new_tokens=80, num_beams=4)

        return tokenizer.decode(out[0], skip_special_tokens=True)

    except ImportError:
        return (
            "[transformers library not installed]\n"
            "Install: pip install transformers torch"
        )
    except Exception as e:
        return f"[AI model error: {e}]"


def main():
    print("=" * 55)
    print("  WEEK 10 — AI Model Inference (Flan-T5 Fallback)")
    print("=" * 55)

    # Demo: try explaining a few errors
    test_errors = [
        "error: 'z' undeclared (first use in this function)",
        "error: lvalue required as left operand of assignment",
    ]

    for err in test_errors:
        print(f"\n  Input : {err}")
        result = explain_with_ai(err)
        print(f"  Output: {result}")

    print(f"\n  Note: AI output should be verified before using.")
    print("=" * 55 + "\n")


if __name__ == '__main__':
    main()
