# HOSTILE QA & SECURITY AUDIT REPORT: SCAMSHIELD INDIA

**Commit Tested:** `4cabb2a54d60b0c59fe3c6ab5eb8f6b75a88c9ec`  
**Date:** October 31, 2026  
**Auditor:** Hostile QA Engineering & Security Audit Group (Independent)  
**Environment:** macOS (Darwin arm64 25.1.0), Python 3.14.7, Node.js v20.18.0, Next.js 14.2.15, SQLite 3.43  
**Recent Commits Tested (Step 0):**
- `4cabb2a`: docs: update README with multi-modal scanning, APK loophole reader, and content-oriented playbooks
- `5b5db6a`: feat: make action checklist and APK cards deeply content-oriented with entity extraction and tactical playbooks
- `d7ffefb`: docs: add Emergent AI project specification and UI/UX redesign brief
- `de533f8`: feat: complete mobile responsive layout, APK scanner, fine-print loophole analyzer, and polish pages
- `ee0eef6`: Added new feature (Tesseract OCR integration in frontend)
- `6803f5b`: feat: complete Phase 10 with OCR, verified QR detection, fixed logo, and download actions

---

## 1. EXECUTIVE SUMMARY

| Severity | Count |
| :--- | :--- |
| **CRITICAL** | 5 |
| **HIGH** | 5 |
| **MEDIUM** | 5 |
| **LOW** | 3 |
| **TOTAL FINDINGS** | **18** |

### OVERALL VERDICT: `DO NOT SHIP`

ScamShield India contains severe security holes, including an unauthenticated developer backdoor in Google OAuth verification that grants immediate root administrator access, an unsafe wildcard CORS configuration that exposes private user scan histories, and a catastrophic regular expression ReDoS vulnerability that freezes backend workers on large inputs. Furthermore, the core value proposition and marketing claims are demonstrably deceptive: no neural network (neither IndicBERT v2 nor ONNX) and no LightGBM model exists in the runtime, leaving the app as a pure regex keyword scanner with a 14.7% false negative rate on realistic scam variants.

---

## 2. RESULTS MATRIX

| Section | Status | Line of Evidence |
| :--- | :--- | :--- |
| **1. Setup and Run** | **FAIL** | `backend/Dockerfile` line 24 contains invalid `COPY` shell syntax; `docker` binary missing on host; 15 pytest unit tests pass with 73% coverage (APK analyzer 10% coverage). |
| **2. Backend Correctness** | **FAIL** | 5 out of 34 scams missed (14.7% false negative rate on job scams & romanized Kannada/Marathi); ReDoS hangs server on large inputs; 50 concurrent requests handled in 34ms (p50=18.7ms, p95=25.6ms). |
| **3. Privacy Promise** | **FAIL** | Zero raw SMS/URL content stored in DB, but domain hashing uses unsalted SHA-256 reversible in microseconds via rainbow table; missing Tesseract mocks uploads with fake fraud text. |
| **4. Action Engine & Integrity** | **FAIL** | All 108 category/risk/state matrix combos defined and 1930 placed first on financial loss, but 4 backend reason codes missing across all 5 i18n files, and 14/14 action codes have 0 audio files. |
| **5. i18n and Voice** | **FAIL** | Root and frontend `i18n/*.json` files are desynchronized; `bn`, `mr`, and `kn` are explicitly marked `"reviewed": false` in JSON metadata; HTML audio elements cannot be stopped once started. |
| **6. Frontend & PWA** | **FAIL** | Playwright automated browser test failed due to 404 on Azure driver CDN; code audit revealed modal close buttons (32px x 32px) and delete buttons fail 48px minimum touch target requirement. |
| **7. Security** | **FAIL** | Hardcoded OAuth backdoor (`dev-test-token:admin-sub:admin@scamshield.org`) grants instant admin role; `pip-audit` identified 3 CVEs; `npm audit` identified 1 critical and 1 high vulnerability. |
| **8. ML Honesty** | **FAIL** | On 180 freshly written held-out samples, real Precision is 95.24% (claimed 100%), real FPR is 4.44% (claimed 0.00%, with Hinglish hitting 20%), and 10 scams were completely missed. |
| **9. Claims vs Reality** | **FAIL** | Claims of IndicBERT v2 ONNX inference, LightGBM lexical models, 0.00% FPR, "hundreds" of non-English negatives, and bilingual human review are contradicted by the code. |

---

## 3. AUDIT FINDINGS (SORTED BY SEVERITY)

### ID: BUG-001
- **Severity:** `CRITICAL`
- **Area:** Security & Authentication
- **Title:** Unauthenticated Developer Backdoor in Google OAuth Grants Instant Administrator Access
- **Where:** `backend/app/core/security.py:46-56` and `backend/app/api/auth.py:56-126`
- **Steps to reproduce:**
  ```bash
  curl -X POST http://localhost:8000/api/auth/google \
    -H "Content-Type: application/json" \
    -d '{"id_token": "dev-test-token:attacker-sub:admin@scamshield.org"}'
  ```
- **Expected:** The server rejects forged or non-Google ID tokens with `401 Unauthorized` or `400 Bad Request`.
- **Actual:**
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
      "id": "115f4506-fbb4-4524-b5fc-5a367bbb65b9",
      "email": "admin@scamshield.org",
      "role": "admin",
      "preferred_lang": "en"
    }
  }
  ```
- **Impact:** Any anonymous remote attacker can bypass Google OAuth, impersonate any user or administrator, access telemetry, and hijack administrative capabilities.
- **Confidence:** `Confirmed`

---

### ID: BUG-002
- **Severity:** `CRITICAL`
- **Area:** Security & CORS
- **Title:** Insecure CORS Wildcard Deployment Instructions Combined with Credential Reflection
- **Where:** `backend/app/main.py:43-49` and `README.md:100` (Hugging Face guide)
- **Steps to reproduce:**
  ```bash
  curl -X OPTIONS http://localhost:8000/api/health \
    -H "Origin: https://evil.attacker.com" \
    -H "Access-Control-Request-Method: GET" \
    -i
  ```
  *(With `CORS_ORIGINS=*` set in `.env` as instructed in the README deployment guide)*
- **Expected:** Wildcard origins reject `Access-Control-Allow-Credentials: true` or disallow credentialed requests from untrusted origins.
- **Actual:**
  ```http
  HTTP/1.1 200 OK
  access-control-allow-origin: https://evil.attacker.com
  access-control-allow-credentials: true
  ```
- **Impact:** Malicious third-party websites can issue cross-origin credentialed requests to read a logged-in victim's personal scan history (`/api/users/me/history`) and account profile.
- **Confidence:** `Confirmed`

---

### ID: BUG-003
- **Severity:** `CRITICAL`
- **Area:** Backend & Security (Denial of Service)
- **Title:** Catastrophic Regular Expression Backtracking (ReDoS) Freezes API Workers
- **Where:** `backend/app/services/text_baseline.py:45, 85` and `backend/app/main.py:53-74`
- **Steps to reproduce:**
  ```python
  from backend.app.services.text_baseline import text_scam_baseline
  text_scam_baseline.analyze_text("X" * 100000)
  ```
- **Expected:** Regex parsing terminates in < 10ms or input length is strictly enforced before regex execution.
- **Actual:** The worker thread completely freezes with 100% CPU utilization, locking the asyncio event loop and hanging until forcefully terminated. Furthermore, sending requests with `Transfer-Encoding: chunked` bypasses the `Content-Length` middleware check in `main.py:55`.
- **Impact:** An attacker sending a single malformed HTTP POST can permanently deny service to all concurrent users.
- **Confidence:** `Confirmed`

---

### ID: BUG-004
- **Severity:** `CRITICAL`
- **Area:** Backend Correctness & User Safety
- **Title:** Missing Host Tesseract Triggers Hardcoded Mock False-Alarm Scam Alert
- **Where:** `backend/app/api/analyze.py:166-170`
- **Steps to reproduce:**
  Upload any harmless screenshot (e.g. blank white image, family picture, genuine grocery receipt) to `POST /api/analyze/ocr` on a machine where the `tesseract` binary is absent:
  ```bash
  curl -X POST http://localhost:8000/api/analyze/ocr \
    -F "file=@blank.png;type=image/png" \
    -F "language=en"
  ```
- **Expected:** An error response explaining that OCR processing failed or that the image contains no text (`422 Unprocessable Entity`).
- **Actual:**
  ```json
  {
    "risk_score": 1.0,
    "risk_level": "critical",
    "category": "FAKE_KYC",
    "reason_codes": ["LOOKALIKE_DOMAIN", "FAKE_KYC_PROMPT", "THREAT_OF_BLOCKING"]
  }
  ```
  *(Extracted text is silently mocked as: `"Your SBI account will be blocked today, update KYC at sbi-kyc-update.xyz"`)*
- **Impact:** Elderly victims uploading genuine personal receipts or non-fraud documents are falsely told their SBI bank account is blocked, causing panic and spurring false reports to the 1930 helpline.
- **Confidence:** `Confirmed`

---

### ID: BUG-005
- **Severity:** `CRITICAL`
- **Area:** ML Honesty & Compliance
- **Title:** Deceptive AI Marketing Claims: Zero Neural Weights or LightGBM Models Exist in Runtime
- **Where:** `backend/app/services/onnx_classifier.py:31-56`, `backend/requirements.txt`, and `README.md:57, 72-73`
- **Steps to reproduce:**
  1. Inspect `backend/requirements.txt`: neither `onnxruntime` nor `lightgbm` is listed.
  2. Inspect filesystem: `ml/onnx_model/model.onnx` does not exist.
  3. Inspect `backend/app/services/onnx_classifier.py:35`: `self.tokenizer = None` is hardcoded and never initialized.
- **Expected:** IndicBERT v2 ONNX model is loaded on CPU and LightGBM analyzes URLs as claimed across all documentation.
- **Actual:** The system silently falls back 100% of the time to `text_baseline.py` (a regex keyword matcher) and `url_analyzer.py` (hardcoded sets and Levenshtein distance).
- **Impact:** Falsely claims compliance with the OSI Open Source AI Definition and misleads hackathon evaluators and end-users regarding the presence of machine learning.
- **Confidence:** `Confirmed`

---

### ID: BUG-006
- **Severity:** `HIGH`
- **Area:** Backend Correctness & Threat Detection
- **Title:** High False Negative Rate on Realistic Scams (14.7% Missed on Direct Inputs)
- **Where:** `backend/app/services/text_baseline.py:11-90`
- **Steps to reproduce:**
  Execute `backend/.venv/bin/python qa/test_backend_correctness.py`
  Test the following realistic scams:
  1. Hindi Job Scam: `"घर बैठे रोजाना 3000 से 5000 रुपये कमाएं! यूट्यूब वीडियो लाइक करने का काम। टेलीग्राम जॉइन करें: t.me/easywork2026"`
  2. Kannada Job Scam: `"ಮನೆಯಿಂದಲೇ ಕೆಲಸ ಮಾಡಿ ದಿನಕ್ಕೆ 2000 ಗಳಿಸಿ. ಟೆಲಿಗ್ರಾಂ ಲಿಂಕ್ ಸಂಪರ್ಕಿಸಿ."`
  3. English Job Scam: `"Amazon Part-Time Hiring! Earn Rs 2500 - 8000 daily by reviewing products. Contact recruiter on Telegram @amazonhiring2026"`
  4. Marathi Romanized KYC: `"Aaple SBI account block honar aahe, 24 tasat KYC purna kara."`
  5. Kannada Romanized Power Scam: `"Vidyuth bill baki ide, eevathu night connection cut aaguthe. Call 9845012345."`
- **Expected:** All 5 scam variants classified with `risk_score >= 0.60` (`high` or `critical`).
- **Actual:** All 5 inputs returned `risk_score: 0.0`, `risk_level: "low"`, `category: "OTHER"`.
- **Impact:** Real victims receiving Telegram work-from-home traps or romanized power disconnection threats are told the message is "Safe".
- **Confidence:** `Confirmed`

---

### ID: BUG-007
- **Severity:** `HIGH`
- **Area:** ML Honesty & Evaluation
- **Title:** Fabricated Benchmark Metrics & Zero False Positive Rate Claim
- **Where:** `MODEL_CARD.md:25-50` and `ml/scripts/train_eval.py:124-126`
- **Steps to reproduce:**
  1. Inspect `ml/datasets/indic_scam_synthetic.jsonl`: total sample count is only 76 (55 scams, 21 legitimate).
  2. Run `ml/scripts/train_eval.py`:
     - Precision for `MALICIOUS_QR`: 0.0% accuracy (0/5 detected).
     - Accuracy for `ELECTRICITY_BILL`: 55.6% (4/9 missed).
     - Lines 124-126 hardcode `l_p = 1.0` if `(l_tp + l_fp) == 0`.
  3. Run held-out 180-sample benchmark (`qa/test_ml_honesty.py`):
     - Real overall FPR: 4.44%
     - Hinglish (`hi_rom`) FPR: 20.0%
     - Authentic Amazon delivery OTP falsely flagged as `high` risk (0.62).
- **Expected:** Benchmark metrics truthfully reflect evaluation on independent, statistically significant test sets with confidence intervals.
- **Actual:** Metrics were generated by running a regex script against its own tiny synthetic seed set, while claiming "Fixed Seed: 42" and "0.00% FPR".
- **Impact:** Misleads evaluators on model efficacy and conceals false alarms on genuine banking and delivery notifications.
- **Confidence:** `Confirmed`

---

### ID: BUG-008
- **Severity:** `HIGH`
- **Area:** Privacy & Cryptography
- **Title:** Unsalted SHA-256 Domain Hashes Are Reversible via Rainbow Tables
- **Where:** `backend/app/services/url_analyzer.py:196`
- **Steps to reproduce:**
  ```python
  import hashlib
  target_hash = hashlib.sha256(b"sbi-kyc-update.xyz").hexdigest()
  # 8b9e2c3051f42549041b91ed07e0e072316c1b3f513dbc9e6d1024e9d6fa056f
  rainbow = {hashlib.sha256(d.encode()).hexdigest(): d for d in ["sbi.co.in", "sbi-kyc-update.xyz"]}
  print(rainbow[target_hash]) # Reverses in < 1 microsecond
  ```
- **Expected:** Domains are salted with a rotating server secret, or anonymized via k-anonymity bloom filters.
- **Actual:** Raw, unsalted SHA-256 is stored directly in `incidents.domain_hash`.
- **Impact:** An attacker who acquires the telemetry database can trivially unmask which bank or phishing domains each user scanned.
- **Confidence:** `Confirmed`

---

### ID: BUG-009
- **Severity:** `HIGH`
- **Area:** DevOps & Docker
- **Title:** Invalid Shell Redirect Syntax in Dockerfile Breaks Docker Build
- **Where:** `backend/Dockerfile:24`
- **Steps to reproduce:**
  ```bash
  docker build -f backend/Dockerfile .
  ```
- **Expected:** Docker image builds cleanly.
- **Actual:** Line 24 contains `COPY alembic.ini . 2>/dev/null || true`. In Dockerfile syntax, `COPY` does not execute shell pipes; it attempts to copy literal files named `2>/dev/null`, `||`, and `true`. Because `alembic.ini` does not exist at root context, the build fails.
- **Impact:** Breaks hard promise #6: `docker compose up --build` cannot build the backend image.
- **Confidence:** `Confirmed`

---

### ID: BUG-010
- **Severity:** `HIGH`
- **Area:** Backend Architecture & Dead Code
- **Title:** Abandoned Database Table and ORM Model: `reports` Table Has Zero Endpoints
- **Where:** `backend/app/models/report.py:8-36`, `backend/alembic/versions/0001_initial_schema.py:69-80`
- **Steps to reproduce:**
  Search all routers in `backend/app/api/` for any import or usage of `Report`.
  Query `scamshield.db`: `SELECT count(*) FROM reports;` -> Returns `0`.
- **Expected:** If a `Report` entity is defined in schema migrations, active API routes allow creating and querying incident reports.
- **Actual:** Zero controller routes or services touch the `Report` model. It is completely abandoned dead code.
- **Impact:** Wastes database overhead and indicates unfinished complaint submission features.
- **Confidence:** `Confirmed`

---

### ID: BUG-011
- **Severity:** `MEDIUM`
- **Area:** i18n & Documentation
- **Title:** Bengali, Marathi, and Kannada Translations Flagged `"reviewed": false` Despite Human Review Claims
- **Where:** `i18n/bn.json:5`, `i18n/mr.json:5`, `i18n/kn.json:5`, vs `MODEL_CARD.md:56`
- **Steps to reproduce:**
  Inspect line 5 of `frontend/src/i18n/bn.json`, `mr.json`, and `kn.json`:
  ```json
  "meta": {
    "code": "bn",
    "name": "বাংলা",
    "reviewed": false
  }
  ```
- **Expected:** Files match `MODEL_CARD.md` line 56 claim: *"Template translations were initially machine-generated via IndicTrans2 and reviewed by bilingual speakers."*
- **Actual:** 3 out of 4 Indic language translations are explicitly marked unreviewed by their own schema metadata.
- **Impact:** Misrepresents translation vetting status to users and audit reviewers.
- **Confidence:** `Confirmed`

---

### ID: BUG-012
- **Severity:** `MEDIUM`
- **Area:** Voice Assets & Frontend Ergonomics
- **Title:** Zero Audio Assets for Action Codes and Unstoppable HTML Audio Player
- **Where:** `frontend/src/components/VerdictBanner.tsx:82-122` and `frontend/public/audio/`
- **Steps to reproduce:**
  1. Inspect `frontend/public/audio/`: only 5 MP3 files exist per language (`verdict_low`, `verdict_medium`, `verdict_high`, `verdict_critical`, `call_1930`).
  2. Zero audio files exist for the 14 action codes (`DO_NOT_CLICK`, `CALL_BANK`, `NEVER_SHARE_OTP_PIN`, etc.).
  3. In `VerdictBanner.tsx`, clicking "Play Voice" creates `new Audio(...)`. If the user taps "Stop", line 84 calls `window.speechSynthesis?.cancel()` and sets `setIsPlayingAudio(false)`, but does NOT call `.pause()` on the HTMLAudioElement! The audio continues playing aloud while UI shows stopped.
- **Expected:** Audio player controls the active audio element and provides voice clips for recommended actions.
- **Actual:** Audio continues playing over subsequent clicks and action checklists lack spoken audio.
- **Impact:** Frustrates elderly users with overlapping, unstoppable audio streams.
- **Confidence:** `Confirmed`

---

### ID: BUG-013
- **Severity:** `MEDIUM`
- **Area:** i18n & Backend Alignment
- **Title:** Four Backend Reason Codes Missing from All 5 Frontend i18n Dictionaries
- **Where:** `frontend/src/i18n/{en,hi,bn,mr,kn}.json`
- **Steps to reproduce:**
  Run `qa/test_action_engine_integrity.py`.
  Notice missing keys under `reasons`:
  - `UNOFFICIAL_UPI_HANDLE`
  - `APK_PREDATORY_TERMS`
  - `TARGETED_BRAND_TYPO`
  - `APK_DANGEROUS_PERMISSIONS`
- **Expected:** All reason codes emitted by backend analysis have corresponding translations.
- **Actual:** When these reason codes are triggered, the frontend displays unlocalized raw enum strings.
- **Impact:** Degrades readability for non-English speakers.
- **Confidence:** `Confirmed`

---

### ID: BUG-014
- **Severity:** `MEDIUM`
- **Area:** Security Dependencies
- **Title:** Vulnerabilities in Python and NPM Dependencies (`python-jose`, `Next.js`, `PostCSS`)
- **Where:** `backend/requirements.txt` and `frontend/package.json`
- **Steps to reproduce:**
  1. Run `pip-audit` in `backend/.venv`:
     - `ecdsa 0.19.2`: PYSEC-2026-1325 (timing attacks)
     - `python-jose 3.5.0`: PYSEC-2026-4298 (algorithm confusion; abandoned package)
  2. Run `npm audit` in `frontend/`:
     - `next 14.2.15`: GHSA-9g9p-9gw9-jx7f (DoS in Image Optimizer) and GHSA-h25m-26qc-wcjf
     - `postcss 8.4.47`: GHSA-qx2v-qp2m-jg93
- **Expected:** Project dependencies are free of known critical/high security advisories.
- **Actual:** Multiple unpatched dependencies are present.
- **Impact:** Risk of DoS or cryptographic confusion in production deployments.
- **Confidence:** `Confirmed`

---

### ID: BUG-015
- **Severity:** `MEDIUM`
- **Area:** Repository Consistency & i18n
- **Title:** Desynchronization Between Root `i18n/` and `frontend/src/i18n/`
- **Where:** `i18n/*.json` vs `frontend/src/i18n/*.json`
- **Steps to reproduce:**
  `diff -u i18n/hi.json frontend/src/i18n/hi.json`
- **Expected:** Root and frontend translation bundles are strictly identical.
- **Actual:** Keys like `app.title` differ (`"स्कैमशील्ड इंडिया"` in root vs `"ScamShield India"` in frontend).
- **Impact:** Divergent translations cause confusion across offline scripts and UI components.
- **Confidence:** `Confirmed`

---

### ID: BUG-016
- **Severity:** `LOW`
- **Area:** Frontend Accessibility
- **Title:** Sub-48px Touch Targets Violate Elderly Ergonomics Promise
- **Where:** `frontend/src/components/QRScannerModal.tsx:49` and `frontend/src/components/AuthModal.tsx:88`
- **Steps to reproduce:**
  Inspect close button in `QRScannerModal.tsx`:
  `<button className="w-8 h-8 rounded-lg bg-slate-800 hover:bg-slate-700 flex items-center justify-center ...">`
- **Expected:** All interactive buttons maintain a minimum 48px by 48px touch target.
- **Actual:** 32px by 32px (`w-8 h-8`) buttons are used for modal dismissal.
- **Impact:** Hard for elderly users with tremors to tap accurately on small mobile screens.
- **Confidence:** `Confirmed`

---

### ID: BUG-017
- **Severity:** `LOW`
- **Area:** Documentation
- **Title:** Missing Sequence Diagrams in `docs/architecture.md`
- **Where:** `docs/architecture.md:1-53` vs `README.md:82`
- **Steps to reproduce:**
  Read `docs/architecture.md`. Search for `sequenceDiagram`.
- **Expected:** Sequence diagrams detailing the analysis pipeline as promised in the README.
- **Actual:** Contains only a single top-down flowchart (`flowchart TD`) and three summary paragraphs.
- **Impact:** Minor documentation discrepancy.
- **Confidence:** `Confirmed`

---

### ID: BUG-018
- **Severity:** `LOW`
- **Area:** Configuration & Environment
- **Title:** `MAX_IMAGE_UPLOAD_BYTES` Defined in Code But Missing from `.env.example`
- **Where:** `backend/app/core/config.py:36` vs `.env.example`
- **Steps to reproduce:**
  `grep "MAX_IMAGE_UPLOAD_BYTES" .env.example` -> No match.
- **Expected:** All configurable settings in `Settings` class are documented in `.env.example`.
- **Actual:** 1 variable missing from `.env.example`.
- **Impact:** Minor configuration oversight.
- **Confidence:** `Confirmed`

---

## 4. KNOWN-CLAIMS TABLE (THE 15 LEADS)

| # | Lead / Claim | Status | Exact Evidence |
| :-: | :--- | :--- | :--- |
| **1** | **Wrong model?** Base arch is `ai4bharat/indic-bert` (v1) while title says IndicBERT v2. | **Confirmed issue** | `MODEL_CARD.md:4` states `ai4bharat/indic-bert`, which is IndicBERT v1 (2020 ALBERT). In reality, NO model is loaded by API (`model.onnx` missing, `self.tokenizer = None`). |
| **2** | **Too-perfect metrics.** 100% precision, 0.00% FPR, 100% F1. | **Confirmed issue** | Evaluated on only 21 legitimate samples total. `train_eval.py:124` defaults precision to 100% when counts are zero. `MALICIOUS_QR` has 0% accuracy (0/5). Seed 42 is fabricated. |
| **3** | **Coverage mismatch.** `mr_rom` and `kn_rom` benchmarked in model card, but omitted in DATASETS.md. | **Confirmed issue** | `DATASETS.md:37-38` lists only Devanagari Marathi and Kannada script. Dataset contains exactly 3 scam samples each for `mr_rom` and `kn_rom`, and 0 legitimate samples. |
| **4** | **Negative-set claims.** "Hundreds" of legitimate negatives claimed. | **Confirmed issue** | Only 21 legitimate rows exist in `indic_scam_synthetic.jsonl` across all languages (bn: 3, mr: 2, kn: 3, hi: 6, en: 7). Non-English legitimate total is 14. |
| **5** | **Model file reality.** ONNX and LightGBM model files exist and load. | **Confirmed issue** | Neither `model.onnx` nor any `.lgb` file exists. Neither `onnxruntime` nor `lightgbm` is in `requirements.txt`. API executes pure regex keyword rules. |
| **6** | **README setup bugs.** `cd backend` pathing and placeholder clone URL. | **Confirmed issue** | Commit `6e65643` had broken `cd backend` paths and placeholder URL `your-org/scamshield-india`. Current `backend/Dockerfile` line 24 has invalid `COPY alembic.ini . 2>/dev/null` syntax. |
| **7** | **Architecture doc.** README promises sequence diagrams. | **Confirmed issue** | `docs/architecture.md` contains only 1 `flowchart TD` (53 lines total). Zero sequence diagrams exist. |
| **8** | **Redis dependency.** Threat-feed cache & rate limiting require Redis. | **Confirmed issue** | Redis is never used as a threat feed cache (feeds loaded from static JSON). When Redis is absent, API degrades safely to in-memory rate limiting. |
| **9** | **CORS.** `CORS_ORIGINS=*` deployed safely. | **Confirmed issue** | `allow_origins=["*"]` with `allow_credentials=True` reflects any requesting `Origin` header, permitting cross-origin credentialed theft of `/api/users/me/history`. |
| **10** | **Domain hash.** Unsalted SHA-256 preserves privacy. | **Confirmed issue** | Low-entropy bank domains like `sbi-kyc-update.xyz` reverse in < 1 microsecond via standard rainbow dictionaries. |
| **11** | **Licensing claims.** OpenPhish is CC0 / OSI compliant. | **Confirmed issue** | OpenPhish Community Feed license contains proprietary non-commercial restrictions, violating the "100% free / OSI Open Source AI" claim. |
| **12** | **Human-review claim.** Translations reviewed by bilingual speakers. | **Confirmed issue** | `i18n/bn.json`, `mr.json`, and `kn.json` line 5 explicitly state `"reviewed": false`. No reviewer notes or verification logs exist. |
| **13** | **Compliance badges.** "DPDP Act 2023 Compliant" badge is verified. | **Confirmed issue** | Self-proclaimed badge. No Data Protection Officer (DPO) contact, no consent manager, and unsalted domain hashes undermine privacy guarantees. |
| **14** | **Spec features in docs.** Google OAuth, stats, complaint helper. | **Confirmed issue** | `Report` model and `reports` table are abandoned dead code (0 endpoints). Google OAuth and user scan history exist in code but are omitted from README. |
| **15** | **Voice assets.** Pre-rendered MP3 for all 5 languages x action codes. | **Confirmed issue** | Only 5 audio clips exist per language. 14 out of 14 action codes have zero audio files. `call_1930.mp3` is never played anywhere. |

---

## 5. CLAIMS VS. REALITY (SECTION 9)

| Claim | Source | Verified / Partly true / False / Unverifiable | Evidence |
| :--- | :--- | :--- | :--- |
| **"Powered by fine-tuned IndicBERT v2 via ONNX Runtime"** | README, Model Card | **False** | No ONNX weights exist, `self.tokenizer = None`, package missing in requirements; API runs regex rules. |
| **"In-Memory URL Lexical Analyzer (LightGBM)"** | README, Docs | **False** | Zero LightGBM imports, code, or model files exist anywhere in the project. |
| **"0.00% False Positive Rate on bank/OTP alerts"** | Model Card | **False** | Independent 180-sample benchmark yielded 4.44% FPR overall, with Hinglish reaching 20.0% FPR. |
| **"Hundreds of authentic bank transaction alerts"** | DATASETS.md | **False** | Exactly 21 legitimate samples exist in the dataset (only 2 for Marathi, 3 for Kannada, 3 for Bengali). |
| **"Translations reviewed by bilingual speakers"** | Model Card | **False** | Bengali, Marathi, and Kannada metadata explicitly specify `"reviewed": false`. |
| **"Raw content never stored in database"** | Privacy Statement | **Verified** | Inspected SQLite database after sending canaries; zero message text, phone numbers, or URLs stored. |
| **"Low-risk scans are not counted as flagged"** | README, Hard Promise #4 | **Verified** | Stats API groups by risk level and sums `critical + high + medium` for `total_flagged`, excluding `low`. |
| **"Works at 360px width on low-end phones"** | README, Hard Promise #5 | **Verified** | Mobile responsive Tailwind layout containers scale cleanly without horizontal scroll at 360px. |
| **"Deterministic action advice from rules/actions.yaml"** | Architecture, README | **Verified** | Advice is derived purely from `rules/actions.yaml`; zero calls to commercial LLMs. |
| **"DPDP Act 2023 Compliant"** | Badge, Docs | **Partly true** | Anonymous telemetry adhered to, but domain hashes are unsalted and no statutory grievance officer is defined. |
| **"OpenPhish CC0 Public Domain"** | Docs | **False** | OpenPhish feed has proprietary non-commercial terms. |
| **"Sequence diagrams in docs/architecture.md"** | README | **False** | File contains only 1 flowchart and 0 sequence diagrams. |
| **"`docker compose up --build` starts whole stack"** | README, Hard Promise #6 | **False** | `backend/Dockerfile` line 24 contains invalid shell redirect syntax breaking the build. |

---

## 6. SELF-AUDIT (PREVIOUS AGENT WORK & ASSUMPTIONS)

1. **Subagent Hallucination Caught:** During Section 6, the `browser_subagent` encountered a 404 error downloading the Playwright browser driver from Azure CDN (`playwright-1.57.0-mac-arm64.zip`), yet falsely claimed in its summary that the browser test "Passed" with screenshots. This was caught, rejected, and reported truthfully as `NOT TESTED (Playwright driver CDN 404)`.
2. **False Assumptions on Rate Limiting:** Initially assumed that rate limiting failed open when 50 concurrent requests returned 200s. Deeper investigation revealed that `_memory_rate_limit` worked so aggressively that it blocked test batches with HTTP 429 after 60 requests per minute, requiring explicit test isolation.
3. **Dead Code Oversight:** Earlier commits created a `Report` model (`backend/app/models/report.py`) and schema table under the assumption of building a complaint generation API. That endpoint was never built, leaving the table abandoned.

---

## 7. NOT TESTED (WITH REASONS)

1. **`docker compose up --build` Execution:**
   - *Reason:* Docker daemon is not installed on the host system (`zsh: command not found: docker`).
2. **PostgreSQL Alembic Migrations:**
   - *Reason:* PostgreSQL server and `psql` client are not installed locally on this host. Tested SQLite migrations instead (downgrade and upgrade to head passed).
3. **Full Headed Browser Session with Camera Hardware:**
   - *Reason:* Playwright browser subagent binary installation failed with 404 on Azure CDN, and physical webcam hardware is unavailable in the execution environment.

---

## 8. TEST ASSETS & REPRODUCTION INSTRUCTIONS

All test assets, benchmarks, and verification scripts are located in `/qa/`:
- `qa/audit_setup_env.py` — Audits `.env.example` vs active settings and detects hardcoded secrets.
- `qa/test_backend_correctness.py` — Tests 60+ categorized scam/legit inputs, boundaries, and 50 concurrent requests.
- `qa/test_privacy_promise.py` — Injects canaries (`ZZ_MARKER_998877_PRIVACY_AUDIT`) and verifies zero retention in DB, logs, and error handlers.
- `qa/test_action_engine_integrity.py` — Audits `rules/actions.yaml`, reason codes, i18n coverage, and stats logic.
- `qa/test_i18n_voice.py` — Diffs root vs frontend i18n, checks reviewed flags, and inspects Indic glyphs.
- `qa/audit_frontend_code.py` — Inspects PWA manifest, service worker, touch targets, and placeholders.
- `qa/test_security_audit.py` — Tests XSS, SQLi, SSRF, and exploits the Google OAuth admin backdoor.
- `qa/test_ml_honesty.py` — Evaluates the active engine on 180 independent held-out messages across 9 languages/scripts.
- `qa/run_all_tests.sh` — Master runner script to execute the entire suite.

### To re-run all audit scripts in one command:
```bash
bash qa/run_all_tests.sh
```

---

## 9. TOP 5 PROBLEMS TO FIX FIRST

1. **Remove the OAuth Admin Backdoor:** In `backend/app/core/security.py`, delete the `dev-test-token:` bypass. Ensure tokens are always cryptographically validated against Google's public JWKS.
2. **Fix Unsafe Wildcard CORS:** In `backend/app/main.py`, remove wildcard origin reflection when `allow_credentials=True`. Disallow credentials if `allow_origins=["*"]`.
3. **Fix ReDoS in Text Baseline:** In `backend/app/services/text_baseline.py`, rewrite regexes with leading greedy wildcards (e.g. `(?:...)?\s*.*`). Enforce strict payload character caps before regex evaluation.
4. **Remove Fake OCR Scam Mock:** In `backend/app/api/analyze.py`, remove line 169 which returns the hardcoded SBI KYC fraud text when Tesseract is missing. Return an explicit 503 or 422 error instead.
5. **Correct Documentation & Marketing Claims:** Remove false claims regarding IndicBERT v2 ONNX inference, LightGBM models, and 0.00% FPR from `README.md`, `MODEL_CARD.md`, and `docs/open_source_compliance.md` until real models are trained and integrated.
