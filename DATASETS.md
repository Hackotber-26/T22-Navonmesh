# Datasets & Licenses

This document catalogs all datasets and corpora used for training and evaluating ScamShield India's scam classification models.

---

## 1. External Public Datasets

### UCI SMS Spam Collection
- **Source:** [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/228/sms+spam+collection)
- **License:** Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Use:** Negative baseline (legitimate transactional, personal SMS) and classic spam message patterns.
- **Size:** 5,574 SMS messages (English).

### URLhaus Threat Feed
- **Provider:** abuse.ch
- **License:** CC0 1.0 Universal (Public Domain Dedication)
- **Use:** Active malicious URLs and payload delivery endpoints.
- **Refresh:** Synchronized via `scripts/refresh_feeds.py`.

### OpenPhish Community Feed
- **Provider:** OpenPhish
- **License:** Open Community Feed Terms
- **Use:** Confirmed active phishing domains and targeted lookalike links.

---

## 2. Indic Synthetic Scam & Legitimate Dataset (Indian Context)

To address Indian scam vectors (UPI collect fraud, electricity disconnection threats, fake KYC, WhatsApp lottery scams, job scams) across Devanagari, Bengali, Kannada, and romanized Hinglish/Benglish:

- **Location:** `ml/datasets/indic_scam_synthetic.jsonl`
- **License:** MIT License / CC0
- **Languages Covered:**
  - `hi` (Hindi in Devanagari and Romanized Hinglish)
  - `bn` (Bengali in Bengali script and Romanized Benglish)
  - `mr` (Marathi in Devanagari)
  - `kn` (Kannada in Kannada script)
  - `en` (Indian English transactional and fraud patterns)
- **Categories:**
  - `UPI_COLLECT_FRAUD`
  - `FAKE_KYC`
  - `FAKE_BANK_LINK`
  - `PARCEL_DELIVERY`
  - `ELECTRICITY_BILL`
  - `LOTTERY_PRIZE`
  - `JOB_SCAM`
  - `MALICIOUS_QR`
  - `OTHER`
- **Negative Control Set:** Hundreds of authentic bank transaction alerts, telecom expiry reminders, courier dispatch notices, and two-factor authentication (OTP) messages to rigorously minimize false positive rates.

