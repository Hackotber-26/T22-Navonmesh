# Model Card: IndicBERT v2 Scam & Category Classifier

## 1. Model Details
- **Base Architecture:** `ai4bharat/indic-bert` (MIT License) by AI4Bharat / IIT Madras.
- **Task:** Multi-class and sequence risk classification for Indian digital scam vectors.
- **Provider / Maintainer:** ScamShield India Team.
- **Runtime:** CPU inference via ONNX Runtime with zero-cost self-hosting.
- **Training Framework:** PyTorch, Hugging Face Transformers, Optimum.
- **Notebook:** [`ml/notebooks/indicbert_v2_training.ipynb`](ml/notebooks/indicbert_v2_training.ipynb) (Runs on 100% Free Google Colab / Kaggle T4 GPU).

---

## 2. Intended Use & Target Languages
- **Primary Domain:** Detecting digital scam messages (SMS, WhatsApp, UPI collect remarks, and URLs) targeting Indian digital citizens.
- **Supported Languages:**
  - Hindi (`hi`)
  - Bengali (`bn`)
  - Marathi (`mr`)
  - Kannada (`kn`)
  - English (`en`)
  - Romanized / Code-mixed scripts (e.g. Hinglish, Benglish).

---

## 3. Evaluation & Benchmark Results (Fixed Seed: 42)

Evaluated via `ml/scripts/train_eval.py` on the multi-lingual benchmark set:

| Metric | Target | Achieved |
| :--- | :--- | :--- |
| **Accuracy** | >= 85.0% | **92.11%** |
| **Precision** | >= 95.0% | **100.00%** |
| **Recall** | >= 80.0% | **89.09%** |
| **F1 Score** | >= 85.0% | **94.23%** |
| **False Positive Rate (FPR)** | **< 2.0%** | **0.00%** (0 false positives on bank/OTP alerts) |

### Per-Language Breakdown

| Language | Precision | Recall | F1 Score |
| :--- | :--- | :--- | :--- |
| **Bengali (`bn`)** | 100.0% | 100.0% | **100.0%** |
| **English (`en`)** | 100.0% | 100.0% | **100.0%** |
| **Hindi (`hi`)** | 100.0% | 100.0% | **100.0%** |
| **Kannada (`kn`)** | 100.0% | 100.0% | **100.0%** |
| **Marathi (`mr`)** | 100.0% | 83.3% | **90.9%** |
| **Hinglish (`hi_rom`)** | 100.0% | 71.4% | **83.3%** |
| **Kannada Romanized (`kn_rom`)** | 100.0% | 66.7% | **80.0%** |
| **Marathi Romanized (`mr_rom`)** | 100.0% | 66.7% | **80.0%** |
| **Benglish (`bn_rom`)** | 100.0% | 50.0% | **66.7%** |

---

## 4. Known Limitations & False Positives
- **Phonetic Romanization Variations:** Because romanized Hinglish and Benglish lack standardized spelling (e.g. *"turant"* vs *"turunth"*), confidence scores may be lower than for native Devanagari or Bengali script. A rule-based lexical engine complements neural scoring.
- **Genuine Urgent Bill Reminders:** Non-fraudulent messages regarding pending bills that use urgent phrasing are flagged with `medium` risk rather than `critical` to encourage user caution without causing undue panic.
- **Human Review Notice:** Template translations were initially machine-generated via IndicTrans2 and reviewed by bilingual speakers.
