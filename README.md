ScamShield India (स्कैमशील्ड इंडिया)

License: MIT
Open Source AI
Privacy: Zero-Retention
PWA Ready
Supported Languages

A free, real-time, privacy-first cybersecurity web application and Progressive Web App (PWA) designed to protect Indian digital citizens—especially elderly and first-time smartphone users—from cyber fraud, SMS phishing, fake UPI payment requests, malicious Android APKs, and predatory fine-print terms & conditions.

🌟 Key Features
1. Multi-Modal Threat Detection (Zero Friction)
Text & SMS Inspection: Paste any suspicious SMS or WhatsApp message (electricity disconnection threats, fake KYC suspensions, courier fees, lottery rewards, work-from-home job traps).
Phishing URL & Domain Analyzer: Scans against live threat intelligence feeds (URLhaus, OpenPhish) and applies LightGBM lexical models to flag lookalike Indian banking domains.
Client-Side QR Code Scanner: Instant in-browser QR decoding via jsQR without uploading camera feeds to the cloud.
Screenshot AI OCR: Upload WhatsApp or SMS screenshots for automatic text extraction and threat analysis.
In-Memory APK Security Inspector (.apk): Upload Android application packages to detect banking trojans, dropper malware, and dangerous permissions (BIND_ACCESSIBILITY_SERVICE, RECEIVE_SMS, READ_CONTACTS, SYSTEM_ALERT_WINDOW, REQUEST_INSTALL_PACKAGES).
Predatory Fine-Print Loophole Reader: Inspects APK legal terms, privacy policies, and string pools for 5 exploitative clauses:
Contact List Harassment & Third-Party Shaming
Unilateral Hidden Processing Fees & Auto-Debit Traps
Dispute & Banking Ombudsman Legal Waivers
Private Media & Gallery Scraping
Third-Party Financial Data Resale
2. Content-Oriented Incident Diagnosis & Tactical Action Playbooks

The "What to do right now" card dynamically adapts to the specific message and situation:

Entity Extraction: Isolates suspect phone numbers, suspect UPI IDs/VPAs, and counterfeit URLs directly from user content, with explicit guidance not to call or approve requests.
Category-Tailored Playbooks:
Electricity Disconnection: How to verify Consumer Account (CA) numbers on official DISCOM apps (BESCOM, BSES, Mahavitaran, WBSEDCL) and warnings against installing AnyDesk/TeamViewer.
Bank & KYC Suspension: Locking NetBanking profiles, hotlisting debit/credit cards, and verifying against genuine .bank.sbi or official portals.
UPI Collect Fraud: Explains that UPI PIN is only entered to send money, instructions to decline pending requests, and checking AutoPay mandates.
Postal & Courier Traps: Official indiapost.gov.in tracking and warnings on nominal ₹5–₹25 card-harvesting fees.
Task & Job Scams: Exit guidance for Telegram/WhatsApp groups and warnings against prepaid deposits.
Targeted APK Countermeasures: Package-specific uninstall directions, accessibility revocation, and loan recovery blackmail defense.
Incident Summary Export & Sharing:
One-tap formatted .txt complaint download for cybercrime.gov.in with full incident timestamps, threat indicators, and evidence excerpts.
Pre-filled WhatsApp warning cards to alert family groups in their native language.
3. Accessible & Inclusive Design
High-Contrast Traffic Light Verdicts: Clear RED (Danger), AMBER (Suspicious), and GREEN (Safe) indicators.
Native Voice Alerts: Pre-rendered native voice guidance explaining why the message is a scam in Hindi, Bengali, Marathi, Kannada, and English.
Elderly-Friendly Ergonomics: Minimum 48px–56px touch targets, fluid typography, text size toggle (A / A+), and optimized responsiveness down to 320px–360px budget Android screens.
Zero Login Barrier: No phone numbers, passwords, or sign-ups required.
4. Zero-Retention Privacy by Default (DPDP Act 2023 Compliant)
Never Stores Personal Data: Uploaded message text, full URLs, phone numbers, and APK bytes are analyzed strictly in memory and discarded immediately.
Metadata-Only Telemetry: Only anonymous incident metadata (category, risk score, language, one-way SHA-256 domain hash) is persisted.
100% Free & Open-Source AI: Powered by fine-tuned IndicBERT v2 (AI4Bharat / IIT Madras) and deterministic rule engines (rules/actions.yaml). Zero calls to third-party proprietary LLMs.
<img width="1425" height="722" alt="image" src="https://github.com/user-attachments/assets/f5b836d3-95d5-4a6a-9a4d-2350ca67613c" />


🏛️ System Architecture
Client Device (Next.js 14 PWA)
 ├── Multi-language UI (hi, bn, mr, kn, en)
 ├── Client-side QR Scanner (jsQR)
 ├── Screenshot OCR Pipeline (Tesseract)
 └── Content-Oriented Action Playbooks & WhatsApp Share
          │
          ▼ (HTTP REST / API Proxy)
FastAPI Backend (Port 8000)
 ├── In-Memory URL Lexical Analyzer (LightGBM + Threat Feeds)
 ├── In-Memory Text Classifier (IndicBERT v2 via ONNX Runtime)
 ├── In-Memory APK Analyzer (Permission Extraction + Loophole Reader)
 └── Deterministic Action Engine (rules/actions.yaml)
          │
          ▼ (Anonymized Telemetry Only)
Storage (SQLite / PostgreSQL)
 └── Anonymous Incident Metadata (ID, Category, Risk Score, Domain Hash)

See docs/architecture.md for sequence diagrams and pipeline details.
<img width="1454" height="706" alt="image" src="https://github.com/user-attachments/assets/e01a71eb-73bc-4cee-abe9-346dda979f0c" />

🚀 Quick Start (Local Development)
Prerequisites
Node.js 18+ and npm
Python 3.10+ (Python 3.11 recommended)
1. Clone the Repository
bash
git clone https://github.com/Hackotber-26/T22-Navonmesh.git
cd T22-Navonmesh
2. Start the Backend API (FastAPI)
bash
# Setup virtual environment
python3 -m venv backend/.venv
source backend/.venv/bin/activate
# Install dependencies
pip install -r backend/requirements.txt
# Run database migrations
backend/.venv/bin/alembic -c backend/alembic.ini upgrade head
# Start FastAPI server on port 8000
PYTHONPATH=. backend/.venv/bin/uvicorn backend.app.main:app --port 8000 --reload
Interactive Swagger API Docs: http://localhost:8000/docs
Health Check: http://localhost:8000/api/health
3. Start the Frontend (Next.js 14)
bash
cd frontend
npm install
npm run dev

Open http://localhost:3000
 in your browser.

🐳 Docker Deployment
Run Everything with Docker Compose
bash
docker compose up --build
Frontend: http://localhost:3000
Backend: http://localhost:8000
📁 Repository Structure
├── backend/
│   ├── app/
│   │   ├── api/             # FastAPI endpoints (/api/analyze, /api/analyze/apk, /api/health)
│   │   ├── services/        # IndicBERT ONNX, URL analyzer, APK inspector, Action engine
│   │   └── models/          # SQLAlchemy incident telemetry models
│   ├── alembic/             # Database migrations
│   └── tests/               # Backend pytest suite
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js 14 App Router (/, /privacy, /terms, /thank-you, /stats, /_not-found)
│   │   ├── components/      # HomeScanner, ApkVerdictCard, ActionChecklist, Header, VerdictBanner
│   │   └── i18n/            # Frontend translations (en, hi, bn, mr, kn) and I18nProvider
│   └── public/              # PWA manifest, favicons, audio warnings, logo
├── docs/
│   ├── architecture.md      # Detailed system architecture & sequence diagrams
│   ├── privacy_statement.md # DPDP Act 2023 compliance breakdown
│   ├── emergent-ai-redesign-spec.md   # UX/UI redesign brief for Emergent AI
│   └── emergent-ai-project-spec.json  # Structured design token configuration
├── rules/
│   └── actions.yaml         # Deterministic rule matrix mapping scam categories to actions
└── i18n/                    # Root shared translations
📜 Legal Pages & PWA Routes
Route	Purpose	Highlights
/	Universal Scam Scanner	Text, URL, QR, Screenshot OCR, and APK Inspector
/privacy	Privacy Policy	DPDP Act 2023 zero-retention architecture disclosures
/terms	Terms & Conditions	Guidance disclaimers and emergency 1930 escalation protocols
/thank-you	Safety Confirmation	Positive reinforcement card with 1-click WhatsApp family sharing
/stats	Threat Intelligence	Anonymized threat trends and common category telemetry
/_not-found	Custom 404 Page	High-contrast return home navigation with 24x7 1930 helpline
🆘 Emergency Helplines (India)

If you or someone in your family has transferred money to a scammer:

National Cyber Crime Helpline: Dial 1930 (Toll Free 24x7)
Golden Hour Protocol: Call within the first 2 hours so cyber police can request beneficiary account freezes across Indian banks.
National Cyber Crime Reporting Portal: https://cybercrime.gov.in
DoT Sanchar Saathi (Chakshu Portal): https://sancharsaathi.gov.in
 (Report fraudulent SMS numbers and calls)
📄 License & Open-Source Compliance
Core Application: MIT License
IndicBERT v2 Model: MIT License (AI4Bharat / IIT Madras)
URLhaus Feed: CC0 1.0 Universal (Public Domain by abuse.ch)
Noto Sans Fonts: SIL Open Font License 1.1 (Google Fonts / Unicode Consortium)
