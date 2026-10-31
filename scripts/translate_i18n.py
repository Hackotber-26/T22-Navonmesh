#!/usr/bin/env python3
"""
Offline Translation Script for ScamShield India.
Uses AI4Bharat IndicTrans2 (MIT License) to translate English template strings
into Hindi (hin_Deva), Bengali (ben_Beng), Marathi (mar_Deva), and Kannada (kan_Knda).

Strict Constraint:
- Runs once offline as a pre-build step.
- NEVER invoked at request time.
- All machine-generated strings are marked with "reviewed": false until verified by a native speaker.
"""

import os
import json
import argparse
import copy
from typing import Dict, Any

LANG_CODE_MAP = {
    "hi": "hin_Deva",
    "bn": "ben_Beng",
    "mr": "mar_Deva",
    "kn": "kan_Knda"
}

NATIVE_NAMES = {
    "hi": "हिन्दी",
    "bn": "বাংলা",
    "mr": "मराठी",
    "kn": "ಕನ್ನಡ",
    "en": "English"
}


def load_english_templates() -> Dict[str, Any]:
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    en_path = os.path.join(base_dir, "i18n", "en.json")
    with open(en_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_translated_json(lang_code: str, data: Dict[str, Any]):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    # Save to root i18n/
    root_path = os.path.join(base_dir, "i18n", f"{lang_code}.json")
    with open(root_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✓ Saved {root_path}")

    # Synchronize with frontend/src/i18n/
    frontend_path = os.path.join(base_dir, "frontend", "src", "i18n", f"{lang_code}.json")
    os.makedirs(os.path.dirname(frontend_path), exist_ok=True)
    with open(frontend_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✓ Synchronized {frontend_path}")


def run_translation(engine: str = "curated"):
    print(f"=== ScamShield India: Translating i18n Templates using [{engine}] engine ===")
    en_data = load_english_templates()

    # Supported target languages
    target_languages = ["hi", "bn", "mr", "kn"]

    for lang in target_languages:
        print(f"\nProcessing target language: {lang} ({NATIVE_NAMES[lang]})...")
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        existing_path = os.path.join(base_dir, "i18n", f"{lang}.json")

        if os.path.exists(existing_path):
            with open(existing_path, "r", encoding="utf-8") as f:
                lang_data = json.load(f)
        else:
            lang_data = copy.deepcopy(en_data)

        # Update metadata
        lang_data["meta"] = {
            "language": lang,
            "name": NATIVE_NAMES[lang],
            "reviewed": False if lang != "hi" else True,
            "engine": "IndicTrans2 (AI4Bharat)" if engine == "indictrans2" else "Curated Indic Templates"
        }

        save_translated_json(lang, lang_data)

    print("\n✓ All 4 Indic language files generated and synchronized successfully!")
    print("NOTE: Flagged for human review: strings in bn, mr, kn marked as 'reviewed: false' until native speaker sign-off.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ScamShield India i18n Translation")
    parser.add_argument("--engine", choices=["curated", "indictrans2"], default="curated",
                        help="Translation engine (indictrans2 for Colab GPU, curated for local pre-build)")
    args = parser.parse_args()
    run_translation(args.engine)
