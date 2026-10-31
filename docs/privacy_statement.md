# Privacy Statement & DPDP Act 2023 Compliance

**Project:** ScamShield India ("The Fake App That Looks Real")  
**Effective Date:** Hacktoberfest Hack Day 2026  
**License:** MIT License  

---

## 1. Zero-Retention Architecture
ScamShield India is designed from the ground up on the principle of **Zero-Knowledge Inference & Privacy by Default**:

1. **No Raw Content Storage:**
   - Message text, pasted URLs, SMS contents, and QR code raw payloads are **NEVER** stored in any database or persistent log.
   - All analysis is performed entirely in volatile memory during the request lifecycle and discarded immediately upon response generation.

2. **Domain-Only One-Way Hashing:**
   - When URLs are analyzed, only a one-way cryptographic SHA-256 hash of the sanitized domain name (e.g. `sha256("sbi-kyc-update.xyz")`) is retained for threat intelligence aggregation.
   - Paths, query parameters, tokens, phone numbers, and VPA identifiers are stripped client-side or during parsing and never recorded.

3. **Client-Side QR Code Processing:**
   - QR scanning runs entirely inside the user's web browser via WebAssembly/pure JavaScript (`jsQR`).
   - Camera video frames never leave the device. Only the decoded URL or text string is submitted for risk analysis.

4. **Self-Hosted AI Inference:**
   - All machine learning models (IndicBERT v2 ONNX, LightGBM lexical analyzer) run locally on our own backend server.
   - **No user data is ever forwarded to third-party proprietary AI APIs** (such as OpenAI, Google Gemini, or external cloud vision/LLM APIs).

---

## 2. Compliance with India's DPDP Act 2023
ScamShield India adheres to the principles of the **Digital Personal Data Protection Act, 2023 (DPDP Act)**:

- **Purpose Limitation (Section 4):** Data processed during an active scan session is strictly used to evaluate threat indicators and provide defensive guidance.
- **Data Minimization (Section 6):** Only anonymous telemetry metadata (timestamp, risk category, risk score level, language code, user action state) is retained in the `incidents` table.
- **Right to Erasure & Anonymity:** Guests can scan without creating an account or providing an email address. For signed-in users (via Google OAuth), only `openid email profile` scopes are requested, and users can delete their incident history at any time.
- **Children and Vulnerable Users:** Specifically designed for elderly and first-time digital citizens with protective, non-deceptive interfaces, clear local-language audio guidance, and no tracking cookies or commercial ad trackers.

---

## 3. Telemetry Logged vs. Never Logged

| Logged (Metadata Only) | NEVER Stored in Database |
| :--- | :--- |
| Scan Timestamp (UTC) | Raw SMS / WhatsApp message text |
| Threat Category (e.g. `FAKE_KYC`) | Full URLs, paths, or query parameters |
| Risk Score & Level (`high`, `0.92`) | UPI IDs, phone numbers, or account numbers |
| Reason Codes (e.g. `LOOKALIKE_DOMAIN`) | Camera images or screenshot bitmaps |
| UI Language (`hi`, `bn`, `mr`, `kn`, `en`) | Personal Names, OTPs, or Passwords |
| SHA-256 Hash of Domain Only | User GPS or Precise Geolocation |

