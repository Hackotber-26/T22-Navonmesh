# Open Source AI Compliance & Licensing Manifest

**Project:** ScamShield India  
**Commitment:** 100% Free, Permissively Licensed, and Compliant with the OSI Open Source AI Definition.

---

## 1. Core AI & ML Components

| Component | Model / Technology | Origin & Provider | License | OSI Open Source AI Status |
| :--- | :--- | :--- | :--- | :--- |
| **Text Scam Classifier** | IndicBERT v2 (`ai4bharat/indic-bert`) | AI4Bharat / IIT Madras | MIT License | **Fully Open Source** (Public code, public weights, documented Indian language corpora) |
| **URL Risk Classifier** | LightGBM Lexical Model | Microsoft / Open Source Community | MIT License | **Fully Open Source** (Trained on public feeds and lexical features) |
| **Client-Side QR Scanner**| `jsQR` / `zxing-wasm` | Open Source Web Community | Apache-2.0 / MIT | **Fully Open Source** |
| **Offline Translation** | IndicTrans2 (`ai4bharat/indictrans2`) | AI4Bharat / IIT Madras | MIT License | **Fully Open Source** (Offline pre-translation script only) |
| **Offline Text-to-Speech** | Indic Parler-TTS | AI4Bharat & Hugging Face | Apache-2.0 | **Fully Open Source** (Static MP3 asset pre-generation only) |
| **Threat Feeds** | URLhaus & OpenPhish Community Feed | abuse.ch & OpenPhish | CC0 1.0 Public Domain / Open Community | **Open Threat Data** |

> [!NOTE]
> **No Proprietary AI APIs:** ScamShield India operates with zero proprietary inference APIs (no OpenAI, Google Gemini, Anthropic, or proprietary cloud vision endpoints). All inference executes locally on CPU via ONNX Runtime and LightGBM.

---

## 2. Software Stack Licenses

| Layer | Technology | License |
| :--- | :--- | :--- |
| **Application Repo** | ScamShield India | MIT License |
| **Frontend Framework** | Next.js (React) | MIT License |
| **Styling** | Tailwind CSS | MIT License |
| **Typography** | Noto Sans (Devanagari, Bengali, Kannada) | SIL Open Font License (OFL 1.1) |
| **Backend Framework** | FastAPI (Python) | MIT License |
| **Database ORM** | SQLAlchemy & Alembic | MIT License |
| **Database Engine** | PostgreSQL / SQLite | PostgreSQL License / Public Domain |
| **Caching & Rate Limiting**| Redis | BSD-3-Clause / RSALv2 / SSPL (Community CE) |
