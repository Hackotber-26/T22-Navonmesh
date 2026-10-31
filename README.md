# ScamShield India

**A mobile-first scam detection and incident-response PWA for Indian digital users.**

ScamShield India helps people examine suspicious SMS and WhatsApp messages, URLs, QR codes, screenshots, and Android APK files. It combines heuristic threat analysis with clear, category-specific safety steps so users know what to do before clicking, sharing credentials, or transferring money.

> **Project status: Hackathon prototype — not production-ready.** The repository's own security/QA audit records critical security and reliability findings. Do not deploy this application with real user data or rely on its verdicts as the sole basis for a safety decision until those findings have been fixed and independently retested. See [the QA/security audit commit](https://github.com/Hackotber-26/T22-Navonmesh/commit/5107098d02830844a1f409113c8d3cb942170d5b).

---

## What it does

### Multi-input scam checks

- **Text and SMS analysis:** Submit suspicious messages, including common Indian scam patterns such as fake KYC alerts, UPI collect requests, courier-fee messages, electricity disconnection threats, lottery claims, and job/task offers.
- **URL and domain checks:** Extracts links and applies local heuristics for suspicious top-level domains, URL shorteners, known sample indicators, and lookalike names targeting Indian banks and public services.
- **QR scanning:** Decodes QR codes in the browser with `jsQR`; the decoded content can then be analyzed.
- **Screenshot text extraction:** Uses Tesseract.js in the browser (English language data) to extract text from an uploaded image. A backend OCR endpoint is also present and uses Tesseract language packs when installed.
- **Android APK inspection:** Examines an APK archive for selected permission strings and readable embedded terms/policy text. It flags patterns associated with invasive permissions and predatory lending clauses.

**Important:** These are prototype heuristics, not a complete malware scanner, forensic APK parser, or guaranteed phishing reputation service. A “safe” result does not prove that a message, website, QR code, or APK is safe.

### Contextual response guidance

- Risk levels: **Low, Medium, High, Critical**.
- Reason codes explain the indicators that contributed to a result.
- The action engine reads ordered response steps from [`rules/actions.yaml`](rules/actions.yaml).
- Users can select whether they have not acted, clicked/entered details, or transferred money to receive a more relevant checklist.
- Guidance includes official reporting resources, bank escalation reminders, evidence preservation, and family-warning actions.
- The frontend includes complaint-summary/download and WhatsApp-sharing helpers.

### Accessibility and languages

The frontend includes a language selector for English, Hindi, Bengali, Marathi, and Kannada, responsive layouts, large primary controls, voice-verdict assets, and a high-contrast risk presentation. Translation review status is not uniform across all languages; please verify critical safety wording with fluent speakers before public use.

### Guest access and accounts

Scanning is available in guest mode. The backend also contains optional Google sign-in and account-linked scan history. For signed-in users, the API exposes history retrieval and history deletion. Do not describe the application as “no data is ever stored”: incident metadata is persisted, and authenticated history can be associated with a user account.

---

## How analysis currently works

1. The frontend sends text or decoded QR content to the FastAPI analysis endpoint.
2. The backend extracts URLs and evaluates domain indicators using a local lexical/rule-based analyzer.
3. Text is evaluated by the baseline rule engine unless a functioning ONNX model and tokenizer are configured.
4. The detector combines the text and URL signals, assigns a risk level, and maps the result to action codes.
5. The backend stores incident metadata such as category, risk level, score, reason codes, language, model/rules version, and a domain hash. Raw submitted message text is not a field in the incident model.
6. The frontend displays the verdict and the recommended next steps.

### Model and threat-intelligence status

The repository contains an IndicBERT/ONNX integration scaffold and model-training documentation. However, the current classifier code falls back to the text baseline when the ONNX session or tokenizer is unavailable; the tokenizer is not initialized in the current implementation. The backend requirements file also does not currently install ONNX Runtime or LightGBM. Therefore, **do not claim that the deployed detector is currently powered by a working IndicBERT model or LightGBM model**.

The URL analyzer currently uses local heuristics, allowlists, and locally loaded threat signatures (plus seeded sample indicators). The implementation does not establish a guaranteed live connection to URLhaus or OpenPhish. Do not describe URL checks as live threat-feed lookups unless that integration is implemented, configured, and tested.

See [`MODEL_CARD.md`](MODEL_CARD.md) and [`docs/architecture.md`](docs/architecture.md) for the intended model and architecture documentation. The model card's benchmark figures should be treated as unverified: the repository's QA audit reports that the claimed metrics do not match its separate held-out checks.

---

## Architecture and stack

| Layer | Technologies / implementation |
|---|---|
| Frontend | Next.js 14, React 18, TypeScript, Tailwind CSS |
| Browser capabilities | PWA service worker, jsQR, Tesseract.js, Recharts |
| Backend | Python 3.10+ (Python 3.11 recommended), FastAPI, Pydantic |
| Persistence | SQLAlchemy, Alembic, SQLite for local development or PostgreSQL |
| Optional infrastructure | Redis for rate limiting/cache configuration |
| Analysis | Python heuristic text baseline, URL/domain lexical rules, YAML action engine |
| APK inspection | ZIP archive inspection, permission-string matching, readable-text pattern matching |
| OCR | Tesseract.js in the browser; optional system Tesseract in the backend |

### High-level flow

```text
Browser / PWA
  ├── Text, URL and decoded QR input
  ├── Screenshot OCR (Tesseract.js)
  └── APK upload
          |
          v
Next.js frontend / API proxy
          |
          v
FastAPI backend
  ├── Text baseline classifier (current fallback)
  ├── URL/domain heuristic analyzer
  ├── APK archive and fine-print analyzer
  └── Deterministic action engine (rules/actions.yaml)
          |
          v
SQLite or PostgreSQL
  └── Incident metadata and optional user-linked history
```

![ScamShield India interface](https://github.com/user-attachments/assets/f5b836d3-95d5-4a6a-9a4d-2350ca67613c)

![ScamShield India architecture](https://github.com/user-attachments/assets/e01a71eb-73bc-4cee-abe9-346dda979f0c)

---

## Repository layout

```text
.
├── backend/
│   ├── app/
│   │   ├── api/          # Analyze, OCR, APK, auth, stats and health routes
│   │   ├── core/         # Configuration, database, security and rate limiting
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # API request/response schemas
│   │   └── services/     # Detector, URL analyzer, baseline, APK and action engine
│   ├── alembic/          # Database migrations
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/          # Next.js routes and pages
│   │   ├── components/   # Scanner, verdict, action and APK UI
│   │   ├── context/      # Authentication context
│   │   └── i18n/         # Frontend translations
│   └── public/           # PWA assets, icons and audio
├── docs/                 # Architecture, privacy and design documents
├── i18n/                 # Shared/root translation files
├── ml/                   # Model training assets and notebooks
├── qa/                   # QA and security test scripts/reports
├── rules/
│   └── actions.yaml      # Category/risk/user-state action matrix
├── scripts/              # Translation, audio and feed-related scripts
├── .env.example
├── docker-compose.yml
├── MODEL_CARD.md
└── README.md
```

---

## Run locally

### Prerequisites

- Node.js 20 recommended (18+ may work with the current Next.js package).
- Python 3.10+ (3.11 recommended).
- Git.
- Optional for backend screenshot OCR: Tesseract OCR and the Hindi, Bengali, Marathi, and Kannada language packs.

### 1. Clone the repository

```bash
git clone https://github.com/Hackotber-26/T22-Navonmesh.git
cd T22-Navonmesh
```

### 2. Configure the backend

```bash
cp .env.example .env
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt
```

For local development, the default configuration uses SQLite. Apply the migrations and start the API:

```bash
backend/.venv/bin/alembic -c backend/alembic.ini upgrade head
PYTHONPATH=. backend/.venv/bin/uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs), and the health endpoint is [http://localhost:8000/api/health](http://localhost:8000/api/health).

### 3. Configure and start the frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

### Environment variables

See [`.env.example`](.env.example). Important settings include:

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | SQLite or PostgreSQL connection string |
| `SECRET_KEY` | JWT signing secret; replace the development value |
| `GOOGLE_CLIENT_ID` | Optional Google sign-in configuration |
| `CORS_ORIGINS` | Comma-separated allowed frontend origins |
| `REDIS_URL` / `REDIS_ENABLED` | Optional Redis configuration |
| `MAX_INPUT_CHARS` | Text input limit |
| `RATE_LIMIT_PER_MINUTE` | API rate-limit setting |
| `NEXT_PUBLIC_API_URL` | Backend URL used by the frontend |

Never commit real credentials, production secrets, OAuth client secrets, or user data.

### Docker status

A Docker Compose configuration is present, but the repository's QA audit reports that the current backend Dockerfile contains a build-breaking instruction. Treat Docker deployment as **unverified until that issue is fixed and `docker compose up --build` succeeds from a clean checkout**. The compose file also contains demo credentials; replace all secrets and passwords before any deployment.

---

## API endpoints

The following routes are implemented in the FastAPI application:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | API information |
| GET | `/api/health` | Health check |
| POST | `/api/analyze` | Analyze text, URL, or decoded QR content |
| POST | `/api/analyze/ocr` | Extract text from an uploaded screenshot and analyze it |
| POST | `/api/analyze/apk` | Inspect an uploaded APK archive |
| POST | `/api/incidents/{incident_id}/action-state` | Update the user's reported action state and return updated steps |
| GET | `/api/stats/summary` | Aggregate scan/risk counts |
| GET | `/api/stats/categories` | Aggregate flagged categories |
| GET | `/api/stats/timeline` | Daily scan timeline |
| GET | `/api/stats/by-language` | Scan counts by language |
| GET | `/api/stats/actions` | Aggregate user action-state counts |

Authentication routes are also registered under the auth router. Consult the interactive API docs for their exact paths and request schemas.

---

## Privacy and data handling

The analysis code is designed not to write raw message text into the incident database. It does persist incident metadata, including risk/category information, reason codes, timestamps, language, and a SHA-256 hash of the analyzed domain. Authenticated users can have incident records associated with their account and can access or delete their scan history.

A plain SHA-256 hash of a domain is **not irreversible anonymization**; common domains can be guessed and hashed. The application also has account, logging, and infrastructure components that require a full deployment-level privacy review. Read [`docs/privacy_statement.md`](docs/privacy_statement.md), but treat it as the project's intended policy description rather than proof of legal compliance.

**This README does not certify compliance with India's Digital Personal Data Protection Act, 2023.** Obtain a qualified legal and security review before collecting personal data or making compliance claims.

---

## Safety limitations and known issues

This is a hackathon prototype. Important limitations include:

- The text detector currently relies on a heuristic baseline unless the ONNX model and tokenizer are correctly installed and initialized.
- The URL analyzer is primarily lexical/rule-based; it is not a complete domain reputation or live threat-intelligence service.
- QR decoding identifies the encoded payload; it cannot establish that a payment request or destination is trustworthy.
- APK inspection uses archive contents and pattern matching. It does not perform full Android binary-manifest decoding, dynamic malware execution, or comprehensive reverse engineering.
- Screenshot OCR quality depends on image clarity and the OCR language data available in the selected path.
- Translation review and model evaluation need further validation on representative, independent data.
- A low-risk verdict is not a guarantee of safety. Users should independently verify sensitive requests through official bank, government, or service-provider channels.

### Security audit warning

The repository's QA/security audit commit reports multiple serious findings, including an authentication backdoor, risky CORS behavior under certain configuration, a regular-expression denial-of-service issue, a misleading OCR fallback when system Tesseract is missing, model/benchmark claims that do not match the runtime, and a Docker build problem. These findings are recorded in the repository's [QA/security audit commit](https://github.com/Hackotber-26/T22-Navonmesh/commit/5107098d02830844a1f409113c8d3cb942170d5b).

The audit is a repository-maintained report, not a substitute for an independent penetration test. Fix and retest all critical/high findings before exposing the service to the public.

---

## Emergency resources (India)

If money has been transferred in a suspected cyber fraud:

- **National Cyber Crime Helpline:** Call **1930** as soon as possible.
- **National Cyber Crime Reporting Portal:** [https://cybercrime.gov.in](https://cybercrime.gov.in)
- **Sanchar Saathi (Chakshu):** [https://sancharsaathi.gov.in](https://sancharsaathi.gov.in)

Contact your bank immediately using the number on its official website, app, or card. Preserve transaction IDs, messages, screenshots, and call details. Do not use phone numbers or links supplied by the suspected scammer.

ScamShield provides guidance only. It does not automatically contact banks, freeze accounts, or file a police complaint on the user's behalf.

---

## Contributing

Contributions are welcome. Before submitting changes:

1. Keep security and privacy claims aligned with the implementation.
2. Add or update tests for changed behavior.
3. Verify translations with fluent speakers, especially safety-critical instructions.
4. Do not commit secrets, real victim data, or unredacted incident evidence.
5. Document known limitations rather than presenting incomplete integrations as production features.

---

## License

The repository includes an [MIT License](LICENSE). Third-party libraries, datasets, model weights, and threat-intelligence sources may have separate terms; verify their licenses and attribution requirements independently.
