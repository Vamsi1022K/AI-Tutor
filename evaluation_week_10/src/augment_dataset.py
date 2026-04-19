# RUNNING COMMAND: python src/augment_dataset.py
import json
import os
import random8

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, 'phase4_dataset', 'annotated_errors.json')
OUTPUT_PATH = os.path.join(BASE_DIR, 'phase4_dataset', 'augmented_errors.json')

# Lists for randomization
VAR_NAMES = ["x", "y", "z", "val", "count", "temp", "data", "result", "buffer", "ptr", "idx", "size", "limit", "total", "sum"]
FUNC_NAMES = ["main", "process", "calculate", "do_work", "update", "render", "handle_input", "save_data", "fetch", "parse"]
TYPES = ["int", "float", "double", "char", "long", "short"]

def augment_entry(entry, index):
    """Generates 10 variations of a single dataset entry."""
    variations = []
    
    for i in range(20):
        v_name = random.choice(VAR_NAMES)
        f_name = random.choice(FUNC_NAMES)
        t_name = random.choice(TYPES)
        
        # Create a new variation
        new_entry = entry.copy()
        new_entry["id"] = f"{entry['id']}_{i}"
        
        # Replace placeholders in fields
        # Note: This is a simple string replacement. In a real scenario, 
        # we'd use more sophisticated templating.
        for field in ["gcc_error", "plain_explanation", "example_code", "fix", "fixed_code"]:
            val = new_entry[field]
            # Replace common generic terms with randomized ones
            val = val.replace("'x'", f"'{v_name}'").replace("'y'", f"'{v_name}_2'")
            val = val.replace("int x", f"{t_name} {v_name}")
            val = val.replace("printf", random.choice(["printf", "puts", "fprintf"]))
            new_entry[field] = val
            
        variations.append(new_entry)
        
    return variations

def main():
    if not os.path.exists(DATASET_PATH):
        print(f"Error: {DATASET_PATH} not found.")
        return

    with open(DATASET_PATH, 'r', encoding='utf-8') as f:
        base_dataset = json.load(f)

    print(f"Loaded {len(base_dataset)} base patterns.")
    
    augmented_dataset = []
    for i, entry in enumerate(base_dataset):
        augmented_dataset.extend(augment_entry(entry, i))
        
    print(f"Generated {len(augmented_dataset)} augmented entries.")
    
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(augmented_dataset, f, indent=2)
        
    print(f"Saved augmented dataset to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
