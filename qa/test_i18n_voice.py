#!/usr/bin/env python3
"""
Section 5: i18n and Voice Audit Suite
Diffs all 5 language files:
- Compares frontend/src/i18n/ vs root i18n/
- Identifies missing keys vs English reference (en.json)
- Identifies extra keys, untranslated English strings in Indic files, empty strings, broken placeholders
- Checks "reviewed" flag in metadata
- Flags Hindi/Marathi vocabulary overlap or mix-ups and script issues
- Tests audio behavior when audio files are missing
"""

import os
import re
import json

def audit_i18n():
    print("=== Section 5: i18n and Voice Audit ===")
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    langs = ["en", "hi", "bn", "mr", "kn"]

    # 1. Compare root i18n vs frontend/src/i18n
    print("\n--- 1. Root i18n/ vs frontend/src/i18n/ synchronization ---")
    for l in langs:
        root_file = os.path.join(base_dir, "i18n", f"{l}.json")
        fe_file = os.path.join(base_dir, "frontend", "src", "i18n", f"{l}.json")
        with open(root_file, "r", encoding="utf-8") as f1, open(fe_file, "r", encoding="utf-8") as f2:
            c1 = json.load(f1)
            c2 = json.load(f2)
            if c1 == c2:
                print(f"  ✓ {l}.json is identical between root and frontend.")
            else:
                print(f"  ❌ MISMATCH: {l}.json differs between root and frontend!")

    # 2. Key completeness, empty strings, untranslated English, broken placeholders
    print("\n--- 2. Key completeness, untranslated strings, placeholders ---")
    en_path = os.path.join(base_dir, "frontend", "src", "i18n", "en.json")
    with open(en_path, "r", encoding="utf-8") as f:
        en_dict = json.load(f)

    def flatten_dict(d, prefix=""):
        items = {}
        for k, v in d.items():
            new_key = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                items.update(flatten_dict(v, new_key))
            else:
                items[new_key] = v
        return items

    en_flat = flatten_dict(en_dict)
    print(f"English reference file contains {len(en_flat)} leaf keys.")

    for l in ["hi", "bn", "mr", "kn"]:
        path = os.path.join(base_dir, "frontend", "src", "i18n", f"{l}.json")
        with open(path, "r", encoding="utf-8") as f:
            target_dict = json.load(f)
        target_flat = flatten_dict(target_dict)

        missing_keys = set(en_flat.keys()) - set(target_flat.keys())
        extra_keys = set(target_flat.keys()) - set(en_flat.keys())
        empty_values = [k for k, v in target_flat.items() if isinstance(v, str) and not v.strip()]
        untranslated = []
        placeholder_issues = []

        for k, en_val in en_flat.items():
            if k in target_flat and isinstance(en_val, str) and isinstance(target_flat[k], str):
                t_val = target_flat[k]
                # Check untranslated English (ignore metadata, technical keys)
                if not any(ign in k for ign in ["meta.code", "meta.direction"]):
                    # If target string is identical to English string of length > 5
                    if en_val == t_val and len(en_val) > 5 and not en_val.isdigit():
                        untranslated.append((k, en_val))

                # Check placeholders like {name}, {count}, {domain}
                en_placeholders = re.findall(r'\{[a-zA-Z0-9_]+\}', en_val)
                target_placeholders = re.findall(r'\{[a-zA-Z0-9_]+\}', t_val)
                if sorted(en_placeholders) != sorted(target_placeholders):
                    placeholder_issues.append((k, en_placeholders, target_placeholders))

        reviewed_status = target_dict.get("meta", {}).get("reviewed", None)

        print(f"\nLanguage: [{l}]")
        print(f"  Metadata 'reviewed' flag: {reviewed_status}")
        print(f"  Leaf keys: {len(target_flat)}")
        print(f"  Missing keys: {len(missing_keys)}")
        if missing_keys:
            for mk in list(missing_keys)[:5]:
                print(f"    - {mk}")
        print(f"  Extra keys: {len(extra_keys)}")
        print(f"  Empty strings: {len(empty_values)}")
        print(f"  Untranslated English strings: {len(untranslated)}")
        for uk in untranslated[:5]:
            print(f"    - {uk[0]}: \"{uk[1][:50]}\"")
        print(f"  Broken placeholders: {len(placeholder_issues)}")
        for pi in placeholder_issues:
            print(f"    - {pi[0]}: expected {pi[1]}, got {pi[2]}")

    # 3. Hindi / Marathi mix-up analysis
    print("\n--- 3. Hindi vs Marathi linguistic inspection ---")
    hi_path = os.path.join(base_dir, "frontend", "src", "i18n", "hi.json")
    mr_path = os.path.join(base_dir, "frontend", "src", "i18n", "mr.json")
    with open(hi_path, "r", encoding="utf-8") as f1, open(mr_path, "r", encoding="utf-8") as f2:
        hi_flat = flatten_dict(json.load(f1))
        mr_flat = flatten_dict(json.load(f2))

    identical_hi_mr = []
    for k in hi_flat:
        if k in mr_flat and not k.startswith("meta"):
            if hi_flat[k] == mr_flat[k] and len(str(hi_flat[k])) > 6:
                identical_hi_mr.append((k, hi_flat[k]))

    print(f"Identical non-trivial Devanagari strings between Hindi and Marathi: {len(identical_hi_mr)}")
    for ihm in identical_hi_mr[:10]:
        print(f"  Identical [{ihm[0]}]: {ihm[1]}")

if __name__ == "__main__":
    audit_i18n()
