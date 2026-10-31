# Model Card: IndicBERT v2 Scam & Category Classifier

## Model Details
- **Architecture:** `ai4bharat/indic-bert` fine-tuned for sequence classification and exported to ONNX Runtime.
- **Provider:** AI4Bharat / IIT Madras (Base Model), fine-tuned by the ScamShield India team.
- **Base Model License:** MIT License.
- **Target Platform:** ONNX Runtime on CPU (low-latency, zero-cost, self-hosted).

---

## Intended Use
- **Primary Domain:** Detecting digital scam messages (SMS, WhatsApp, Telegram, email, and UPI payment remarks) targeting users in India.
- **Supported Languages:**
  - Hindi (`hi`)
  - Bengali (`bn`)
  - Marathi (`mr`)
  - Kannada (`kn`)
  - English (`en`)
  - Code-mixed / Romanized scripts (e.g. Hinglish: *"Aapka electricity connection kat jayega..."*).

---

## Limitations & Edge Cases
- **Code-Mixed Text:** Highly non-standard phonetic romanization may produce lower confidence scores than native scripts. A lexical fallback rule engine supplements the neural classifier.
- **Contextual Legitimacy:** Messages asking for genuine bill payments that look urgent may be flagged as `medium` risk; softer advisory warnings are presented to prevent user panic.
- **Translations:** Guidance templates were generated via IndicTrans2 and reviewed by native speakers. Offline static MP3 clips ensure no run-time latency or translation drift.

---

## Performance Targets
- **Target Precision:** >= 95% on high/critical verdicts to avoid alarming users unnecessarily.
- **False Positive Rate:** < 2% on legitimate bank transaction and OTP notifications.
