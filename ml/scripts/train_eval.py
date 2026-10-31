#!/usr/bin/env python3
"""
Model Evaluation & Benchmark Script for ScamShield India.
Evaluates scam classification performance across:
1. Overall Precision, Recall, F1 score
2. Per-language breakdown (hi, bn, mr, kn, en, romanized)
3. Per-category metrics for all 9 categories
4. False Positive Rate (FPR) on authentic bank transactional and OTP messages.

Output: Formatted terminal tables & updates to MODEL_CARD.md
"""

import os
import sys
import json
from collections import defaultdict

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.services.detector import detector


def evaluate_dataset(dataset_path: str = None):
    if dataset_path is None:
        dataset_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../datasets/indic_scam_synthetic.jsonl")
        )

    print(f"=== ScamShield India: Model Evaluation & Benchmark ===")
    print(f"Dataset: {dataset_path}\n")

    if not os.path.exists(dataset_path):
        print(f"Error: Dataset not found at {dataset_path}")
        return

    samples = []
    with open(dataset_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                samples.append(json.loads(line))

    print(f"Loaded {len(samples)} evaluation samples.")

    # Counters
    tp = 0  # True Positives: Scam correctly flagged as medium/high/critical
    fp = 0  # False Positives: Legitimate message wrongly flagged as scam
    tn = 0  # True Negatives: Legitimate message classified as low risk
    fn = 0  # False Negatives: Scam missed as low risk

    by_lang = defaultdict(lambda: {"tp": 0, "fp": 0, "tn": 0, "fn": 0})
    by_cat = defaultdict(lambda: {"total": 0, "correct": 0})

    for s in samples:
        text = s["text"]
        actual_is_scam = s["is_scam"]
        expected_cat = s["category"]
        lang = s.get("lang", "en")
        if s.get("script") == "romanized":
            lang = f"{lang}_rom"

        # Run inference
        res = detector.analyze(
            input_type="text",
            content=text,
            language=s.get("lang", "en")
        )

        pred_score = res["risk_score"]
        pred_is_scam = 1 if pred_score >= 0.30 else 0
        pred_cat = res["category"]

        # Track binary classification
        if actual_is_scam == 1:
            if pred_is_scam == 1:
                tp += 1
                by_lang[lang]["tp"] += 1
            else:
                fn += 1
                by_lang[lang]["fn"] += 1

            # Category tracking
            by_cat[expected_cat]["total"] += 1
            if pred_cat == expected_cat:
                by_cat[expected_cat]["correct"] += 1
        else:
            if pred_is_scam == 1:
                fp += 1
                by_lang[lang]["fp"] += 1
            else:
                tn += 1
                by_lang[lang]["tn"] += 1

    # Calculate overall metrics
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    accuracy = (tp + tn) / len(samples) if samples else 0.0

    print("\n" + "=" * 50)
    print("           OVERALL PERFORMANCE BENCHMARK          ")
    print("=" * 50)
    print(f"Accuracy:                 {accuracy * 100:.2f}%")
    print(f"Precision:                {precision * 100:.2f}%")
    print(f"Recall:                   {recall * 100:.2f}%")
    print(f"F1 Score:                 {f1 * 100:.2f}%")
    print(f"False Positive Rate (FPR): {fpr * 100:.2f}%  (Target: < 2%)")
    print(f"Total True Positives:     {tp}")
    print(f"Total True Negatives:     {tn}")
    print(f"Total False Positives:    {fp}")
    print(f"Total False Negatives:    {fn}")

    print("\n" + "-" * 50)
    print("        PER-LANGUAGE BREAKDOWN (NATIVE & ROMANIZED) ")
    print("-" * 50)
    print(f"{'Language':<12} | {'Precision':<10} | {'Recall':<10} | {'F1':<10}")
    print("-" * 50)

    for lang, counts in sorted(by_lang.items()):
        l_tp = counts["tp"]
        l_fp = counts["fp"]
        l_fn = counts["fn"]
        l_p = l_tp / (l_tp + l_fp) if (l_tp + l_fp) > 0 else 1.0
        l_r = l_tp / (l_tp + l_fn) if (l_tp + l_fn) > 0 else 1.0
        l_f1 = (2 * l_p * l_r) / (l_p + l_r) if (l_p + l_r) > 0 else 1.0
        print(f"{lang:<12} | {l_p*100:>8.1f}% | {l_r*100:>8.1f}% | {l_f1*100:>8.1f}%")

    print("\n" + "-" * 50)
    print("            PER-CATEGORY CLASSIFICATION ACCURACY   ")
    print("-" * 50)
    print(f"{'Category':<24} | {'Accuracy':<10} | {'Samples'}")
    print("-" * 50)

    for cat, data in sorted(by_cat.items()):
        acc = (data["correct"] / data["total"]) * 100 if data["total"] > 0 else 0.0
        print(f"{cat:<24} | {acc:>8.1f}% | {data['total']}")

    print("=" * 50)


if __name__ == "__main__":
    evaluate_dataset()
