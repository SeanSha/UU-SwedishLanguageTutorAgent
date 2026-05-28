import os
import json
import pandas as pd
from datasets import load_dataset
import config

DATA_DIR = config.DATA_DIR
VOCAB_FILE = os.path.join(DATA_DIR, "vocabulary.jsonl")
SENTENCE_FILE = os.path.join(DATA_DIR, "sentence_examples.jsonl")
PLAN_FILE = os.path.join(DATA_DIR, "dialogue_plans.jsonl")
SCHEMA_FILE = os.path.join(DATA_DIR, "function_schema.json")

DEFAULT_FUNCTION_SCHEMA = {
    "greeting": "Greeting the other speaker (e.g. Hej!)",
    "offer_help": "Offering help (e.g. Vad vill du köpa?)",
    "state_want": "Stating what one wants (e.g. Jag vill ha...)",
    "ask_quantity": "Asking about quantity (e.g. Hur många?)",
    "state_quantity": "Stating quantity (e.g. en, två)",
    "state_price": "Stating price (e.g. Det kostar...)",
    "ask_permission": "Asking for permission (e.g. Kan jag få...)",
    "confirm_yes": "Confirming yes (e.g. Ja, det går bra.)",
    "state_problem": "Stating a problem (e.g. Jag mår inte bra.)",
    "ask_location": "Asking for a location (e.g. Var är toaletten?)",
    "give_directions": "Giving directions (e.g. Den ligger till vänster.)",
    "state_feeling": "Stating a feeling or state (e.g. Jag har ont i huvudet.)",
    "state_origin": "Stating country of origin (e.g. Jag kommer från Kina.)",
    "ask_health": "Asking how someone is (e.g. Hur mår du?)",
    "goodbye": "Saying goodbye (e.g. Hejdå!)"
}

def load_structured_dataset():
    """
    Loads the structured Pre-A1 Swedish dataset.
    First checks local JSON/JSONL files, then attempts loading from Hugging Face configs,
    and writes local caches if loaded from Hugging Face.
    Falls back gracefully if both fail.
    """
    print("----------------------------------------------------------------")
    print("🇸🇪 LOADING STRUCTURED SWEDISH LANGUAGE BUDDY DATASET 🇸🇪")
    print("----------------------------------------------------------------")

    # 1. Attempt local file read first (for instantaneous offline starts)
    if (os.path.exists(VOCAB_FILE) and 
        os.path.exists(SENTENCE_FILE) and 
        os.path.exists(PLAN_FILE)):
        
        try:
            print("Found local cached structured dataset files! Loading...")
            
            # Read Vocabulary
            vocab_items = []
            with open(VOCAB_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        vocab_items.append(json.loads(line))
            
            # Read Sentence Examples
            sentence_examples = []
            with open(SENTENCE_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        sentence_examples.append(json.loads(line))
                        
            # Read Dialogue Plans
            dialogue_plans = []
            with open(PLAN_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        dialogue_plans.append(json.loads(line))
            
            # Read Function Schema
            function_schema = DEFAULT_FUNCTION_SCHEMA
            if os.path.exists(SCHEMA_FILE):
                try:
                    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
                        function_schema = json.load(f)
                except Exception as e:
                    print(f"Error reading function schema file: {e}. Using defaults.")

            print("🟢 Structured dataset loaded successfully from local JSONL cache!")
            print(f"- Vocabulary items: {len(vocab_items)}")
            print(f"- Sentence examples: {len(sentence_examples)}")
            print(f"- Dialogue plans: {len(dialogue_plans)}")
            print("- Fallback mode: False (Local JSONL cache)")
            print("----------------------------------------------------------------")
            return vocab_items, sentence_examples, dialogue_plans, function_schema
            
        except Exception as e:
            print(f"Failed to read local structured files: {e}. Re-fetching from Hugging Face...")

    # 2. Attempt loading from Hugging Face
    dataset_name = "SeanSha30/swedish-pre-a1-learning-agent-dataset"
    try:
        print(f"Attempting to fetch config splits from Hugging Face: '{dataset_name}'...")
        
        # Load configs individually to handle config-specific structures cleanly
        vocab_ds = load_dataset(dataset_name, "vocabulary")
        sentence_ds = load_dataset(dataset_name, "sentence_examples")
        plan_ds = load_dataset(dataset_name, "dialogue_plans")
        
        vocab_items = [row for row in vocab_ds["train"]]
        sentence_examples = [row for row in sentence_ds["train"]]
        dialogue_plans = [row for row in plan_ds["train"]]
        function_schema = DEFAULT_FUNCTION_SCHEMA

        # Cache locally to prevent redundant downloads and enable full offline compatibility
        print("Caching loaded dataset splits locally as JSON/JSONL...")
        os.makedirs(DATA_DIR, exist_ok=True)
        
        with open(VOCAB_FILE, "w", encoding="utf-8") as f:
            for item in vocab_items:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
                
        with open(SENTENCE_FILE, "w", encoding="utf-8") as f:
            for item in sentence_examples:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
                
        with open(PLAN_FILE, "w", encoding="utf-8") as f:
            for item in dialogue_plans:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
                
        with open(SCHEMA_FILE, "w", encoding="utf-8") as f:
            json.dump(function_schema, f, ensure_ascii=False, indent=2)

        print("🟢 Structured dataset loaded successfully from Hugging Face and cached locally!")
        print(f"- Vocabulary items: {len(vocab_items)}")
        print(f"- Sentence examples: {len(sentence_examples)}")
        print(f"- Dialogue plans: {len(dialogue_plans)}")
        print("- Fallback mode: False (Hugging Face API)")
        print("----------------------------------------------------------------")
        return vocab_items, sentence_examples, dialogue_plans, function_schema

    except Exception as e:
        print(f"🔴 Hugging Face structured dataset loading failed: {e}")
        print("Searching for legacy CSV caching fallback...")

    # 3. Fallback to CSV
    if os.path.exists(config.DATASET_CACHE_PATH):
        try:
            print(f"Fallback: Reading legacy CSV dataset cache from {config.DATASET_CACHE_PATH}...")
            df = pd.read_csv(config.DATASET_CACHE_PATH)
            
            # Map legacy CSV structure to vocabulary and sentence example schema
            vocab_items = []
            sentence_examples = []
            for idx, row in df.iterrows():
                # Extract sentence examples
                sentence_examples.append({
                    "id": f"sent_{idx}",
                    "sentence": row["text"],
                    "english": row["english"],
                    "chinese": row.get("chinese", ""),
                    "scenario": row["label"],
                    "function": "state_want" if row["label"] == "food_shop" else "state_problem",
                    "level": "pre-A1",
                    "slots": {},
                    "keywords": []
                })
            
            print("🟡 Fallback mode activated: Using old data/dataset_cache.csv mapping.")
            print(f"- Mapped sentence examples: {len(sentence_examples)}")
            print("- Dialogue plans: 0 (Classic hardcoded flow will be used)")
            print("- Fallback mode: True")
            print("----------------------------------------------------------------")
            return vocab_items, sentence_examples, [], DEFAULT_FUNCTION_SCHEMA
        except Exception as csv_err:
            print(f"🔴 Legacy CSV loading failed: {csv_err}")

    # 4. Ultimate Empty Fallback to prevent crash
    print("🔴 CRITICAL: All data sources failed! Initializing empty fallbacks.")
    print("- Fallback mode: True")
    print("----------------------------------------------------------------")
    return [], [], [], DEFAULT_FUNCTION_SCHEMA

if __name__ == "__main__":
    v, s, d, sch = load_structured_dataset()
    print("Validation run complete.")
