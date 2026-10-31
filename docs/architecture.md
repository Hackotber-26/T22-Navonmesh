# ScamShield India System Architecture

```mermaid
flowchart TD
    subgraph Client ["Client Device (Mobile-First PWA)"]
        User(["Elderly / First-Time User"])
        LangPicker["Language Picker (hi, bn, mr, kn, en)"]
        InputModes["Input: Paste Text / URL / Camera QR / Android Share Target"]
        QRScanner["Client-side QR Decoder (jsQR)"]
        VerdictUI["Verdict Banner (Red / Amber / Green)"]
        ActionChecklist["Action Checklist (1930 / cybercrime.gov.in)"]
        AudioPlayer["Static Voice Guidance (Pre-rendered MP3)"]
    end

    subgraph Backend ["FastAPI Backend (Zero Retention)"]
        APIEndpoint["POST /api/analyze"]
        URLAnalyzer["URL Analyzer (Lexical + Allowlist/Blocklist)"]
        TextClassifier["Text Classifier (IndicBERT v2 ONNX)"]
        SignalCombiner["Risk Fusion & Reason Code Mapper"]
        ActionEngine["Action Engine (actions.yaml)"]
    end

    subgraph Storage ["Metadata-Only Persistence"]
        DB[("PostgreSQL / SQLite")]
        RedisCache[("Redis Rate Limiter & Threat Feed Cache")]
    end

    User --> LangPicker --> InputModes
    InputModes -->|Raw text / URL| APIEndpoint
    InputModes -->|QR Code Frame| QRScanner -->|Decoded URL/Payload| APIEndpoint
    
    APIEndpoint --> URLAnalyzer
    APIEndpoint --> TextClassifier
    URLAnalyzer & TextClassifier --> SignalCombiner
    SignalCombiner --> ActionEngine
    
    ActionEngine -->|Verdict + Reason Codes + Action Codes| VerdictUI
    VerdictUI --> AudioPlayer
    VerdictUI --> ActionChecklist

    ActionEngine -.->|Metadata Only: ID, Category, Risk, Timestamp| DB
    APIEndpoint -.->|Rate limit check| RedisCache
```

## Architectural Highlights
1. **Separation of Content and Telemetry:**
   Raw text or links are processed strictly in-memory by FastAPI workers and are never persisted. Only anonymous incident metadata (category, risk score, language, domain hash) reaches the database.
2. **Deterministic Action Engine:**
   Safety-critical action advice is generated via pre-vetted rules (`actions.yaml`), completely bypassing LLMs to guarantee zero hallucinations during stressful fraud incidents.
3. **Bandwidth & Latency Optimization for Low-End Devices:**
   Instead of dynamically streaming audio via heavy TTS on each request, all voice warnings and advice snippets are pre-synthesized offline into static lightweight MP3 files served via CDN or static asset paths.
