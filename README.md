# ScamShield India (The Fake App That Looks Real)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Open Source AI](https://img.shields.io/badge/AI-Open%20Source-green.svg)](docs/open_source_compliance.md)
[![Privacy: Zero-Retention](https://img.shields.io/badge/Privacy-DPDP%202023%20Compliant-brightgreen.svg)](docs/privacy_statement.md)

A free, accessible, real-time web app and PWA that detects suspicious SMS, WhatsApp messages, URLs, and QR codes targeting Indian digital citizens (UPI collect fraud, fake electricity disconnection notices, fraudulent KYC updates, courier scams). 

Built specifically for elderly and first-time internet users with large touch targets, high-contrast traffic-light verdicts, minimal text, pre-recorded voice warnings in 5 Indian languages (Hindi, Bengali, Marathi, Kannada, English), and deterministic emergency action checklists.

---

## Key Features & Hard Constraints

1. **Zero-Retention Privacy by Default (DPDP Act 2023 Compliant):**
   - **NEVER** stores raw message text, phone numbers, full URLs, or QR contents in the database.
   - Inference runs in-memory on self-hosted servers with zero calls to third-party proprietary APIs.
   - Only a one-way SHA-256 hash of domain names is retained for threat intelligence.
2. **100% Free & Open-Source AI (OSI Compliant):**
   - Text Scam Classifier: Fine-tuned IndicBERT v2 (AI4Bharat / IIT Madras) served via ONNX Runtime on CPU.
   - URL Analyzer: LightGBM lexical model + live threat feeds (URLhaus CC0, OpenPhish Community Feed).
   - Zero proprietary AI APIs (No OpenAI, Gemini, or restrictive custom licenses).
3. **No LLM-Generated Advice:**
   - Emergency guidance and checklists are driven by deterministic, audited rule matrices (`rules/actions.yaml`). No risk of hallucinated advice during a crisis.
4. **Multilingual Voice & Text First:**
   - Hindi (`hi`), Bengali (`bn`), Marathi (`mr`), Kannada (`kn`), and English (`en`).
   - Pre-rendered static MP3 audio clips for instantaneous voice playback without network or GPU latency.
5. **Mobile-First PWA & Web Share Target:**
   - Directly receive suspicious text shared from WhatsApp or SMS messages via Android's native share menu.
   - Client-side in-browser QR scanning via `jsQR` (camera feed never leaves the browser).

---

## System Architecture

See [docs/architecture.md](docs/architecture.md) for sequence diagrams and pipeline details.

```
Client (Next.js PWA)  --->  FastAPI Backend (In-Memory Processing)
                             ├── URL Lexical Analyzer (LightGBM + Feeds)
                             ├── IndicBERT v2 Text Classifier (ONNX Runtime)
                             └── Action Engine (rules/actions.yaml)
                                    └── Incident Telemetry Metadata Only -> PostgreSQL / SQLite
```

---

## Quick Start (Local Development)

### Option 1: One-Command with Docker Compose
Ensure Docker is installed and running, then:
```bash
docker compose up --build
```
- Frontend: `http://localhost:3000`
- Backend API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/api/health`

### Option 2: Running Directly on Host (Zero Docker Required)
This setup runs directly with Python 3.11+ and Node 18+:

1. **Backend:**
   ```bash
   cd backend
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   
   # Run initial database migrations
   alembic -c backend/alembic.ini upgrade head

   # Start FastAPI dev server
   uvicorn backend.app.main:app --reload --port 8000
   ```

2. **Frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Open `http://localhost:3000`.

---

## Deployment Guide (Free VM / Hugging Face Spaces)

### Deploying on Hugging Face Spaces (Docker Space - 100% Free CPU Tier)
1. Create a new Space on [Hugging Face](https://huggingface.co/spaces) and select **Docker** SDK (Free 2 vCPU / 16GB RAM).
2. Set the repository root Dockerfile or point to `backend/Dockerfile`.
3. Add Environment Variables in Settings:
   - `ENVIRONMENT=production`
   - `DATABASE_URL=sqlite+aiosqlite:///./data/scamshield.db`
   - `SECRET_KEY=<your-generated-32-char-secret>`
   - `CORS_ORIGINS=*`
4. The backend will automatically run migrations and serve the ONNX models and API endpoints.

### Deploying on a Free Oracle Cloud / Render / Fly.io VM
1. Clone the repository onto your VM:
   ```bash
   git clone https://github.com/your-org/scamshield-india.git
   cd scamshield-india
   ```
2. Copy `.env.example` to `.env` and fill in your domain names and secrets:
   ```bash
   cp .env.example .env
   ```
3. Run with Docker Compose:
   ```bash
   docker compose up -d
   ```

---

## Open Source AI & Component Licenses

| Component | License | Origin |
| :--- | :--- | :--- |
| **ScamShield India** | MIT | Core Project |
| **IndicBERT v2** | MIT | AI4Bharat / IIT Madras |
| **IndicTrans2** | MIT | AI4Bharat / IIT Madras |
| **Indic Parler-TTS** | Apache 2.0 | AI4Bharat & Hugging Face |
| **URLhaus Feed** | CC0 1.0 (Public Domain) | abuse.ch |
| **UCI SMS Spam Dataset** | CC BY 4.0 | UCI ML Repository |
| **Noto Sans Fonts** | SIL OFL 1.1 | Google Fonts / Unicode Consortium |

---

## Important Safety Helplines
- **National Cyber Crime Helpline:** Dial `1930`
- **National Cyber Crime Reporting Portal:** [https://cybercrime.gov.in](https://cybercrime.gov.in)
- **DoT Sanchar Saathi (Chakshu):** [https://sancharsaathi.gov.in](https://sancharsaathi.gov.in)
