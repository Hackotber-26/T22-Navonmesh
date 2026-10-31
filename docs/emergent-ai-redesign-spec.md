# Project Brief & Design Specification for Emergent AI
**Project Name:** ScamShield India (स्कैमशील्ड इंडिया)  
**Target Platform:** Mobile-First Progressive Web App (PWA)  
**Primary Users:** Elderly & first-time digital citizens across India on budget Android devices (320px–412px viewports) with low tech literacy.  
**Mission:** Instant, panic-free detection of SMS phishing, fake UPI payment requests, malicious APK apps, and predatory terms & conditions fine print in native Indian languages.

---

## 1. Executive Summary & Problem Space
In India, cyber fraud (fake electricity bill disconnections, lottery/task scams, fake KYC updates, APK loan shark malware, UPI reverse charges) targets non-tech-savvy users who often panic under artificial urgency.
Current security tools fail because they are:
1. Cluttered with technical jargon (SSL, CVE, hashes, heuristic scores).
2. Designed for English-only desktop power users.
3. Overwhelming during a live scam incident when the victim is anxious.

**ScamShield India's UI/UX Principle:** "Clarity under panic, zero jargon, voice-first explanation, high tactile confidence."

---

## 2. Core User Personas & Context of Use
### Persona A: Ramesh (Age 64, Retired Clerk)
- **Device:** Budget Android phone (Redmi / Samsung Galaxy M-series), cracked screen, large system font scale enabled.
- **Languages:** Hindi & Bengali (limited English).
- **Trigger Scenario:** Receives an SMS: *"Urgent: Electricity bill unpaid. Power cut at 9:30 PM. Call officer at 98xxxx or install Suvidha.apk"*.
- **Need:** Paste the message or upload the APK, get an unmistakable **RED / GREEN / AMBER** status, hear an audio explanation in Hindi, and know exactly what to do in 3 bullet points.

### Persona B: Priya (Age 22, College Student)
- **Device:** Android smartphone.
- **Trigger Scenario:** Instant loan app asks for full contacts and gallery permissions; wants to know if the APK terms hide predatory auto-debit or blackmail clauses.
- **Need:** Upload `.apk`, get an instant breakdown of dangerous permissions and predatory legal loopholes in plain words.

---

## 3. Design System & Accessibility Constraints (Crucial for AI Redesign)
1. **Touch Target Size:** Minimum `48px x 48px` (ideally `56px` for primary actions) with generous thumb reachability on bottom half of the screen.
2. **Color Palette:**
   - **Background:** Deep dark mode (`#0B0F19` / `#0F172A`) to reduce battery drain on AMOLED budget phones and minimize glare.
   - **Verdict RED (Danger/Critical):** `#EF4444` / Crimson with high-contrast badge styling.
   - **Verdict AMBER (Suspicious/Warning):** `#F59E0B` / Indian Marigold Amber.
   - **Verdict GREEN (Safe/Verified):** `#10B981` / Emerald.
   - **Accent / Trust:** `#6366F1` (Indigo) / `#3B82F6` (Electric Blue).
   - *Rule:* Traffic-light colors must NEVER be used for general decorative buttons—only for actual risk verdicts and danger warnings.
3. **Typography:**
   - Large, legible sans-serif (Inter / Outfit / Noto Sans Devanagari).
   - Base text size `>= 16px` to prevent automatic iOS/Android zoom on input focus.
4. **Multilingual Architecture:**
   - One-tap global language switcher prominently pinned in header (Supports English, हिन्दी, বাংলা, मराठी, ಕನ್ನಡ).
5. **Zero Friction:**
   - No login wall, no signup, no phone number required. The user lands directly on the scanner.

---

## 4. Key Screens & UX Flows to Redesign

### Screen 1: Primary Scanner (Home View)
- **Header:**
  - App Logo with trust shield badge.
  - Quick Language Switcher button (e.g. `🌐 हिंदी`).
  - Subtle links: "Privacy (DPDP Act)" and "Terms".
- **Hero & Trust Affirmation:**
  - Clear heading: *"Check any message, link, QR or Android APK"*.
  - Subtext badge: *"100% Private • Zero Data Stored • Govt 1930 Integrated"*.
- **Multi-Input Unified Container:**
  - Textarea: Prominent placeholder with real Indian scam examples (*"Paste SMS, WhatsApp message, or website link here..."*).
  - Quick action toolbar underneath input:
    - `📋 Paste from Clipboard` (1-click paste).
    - `📷 Scan QR Code` (opens camera modal).
    - `🖼️ Upload Screenshot` (OCR scanner for WhatsApp / SMS screenshots).
    - `📦 Check APK File` (inspects Android `.apk` files for malware & fine-print loopholes).
    - `Clear` button.
- **Primary CTA:**
  - Big, tactile button: `🔍 Check Now (तुरंत जांचें)` (minimum 56px height, vibrant gradient, active press feedback).
- **Loading & Timeout UX States:**
  - Multi-stage spinner ("Checking threat feeds...", "Reading package...", "Analyzing fine print...").
  - Gentle fallback warning after 8s: *"Still checking with threat intelligence feeds..."* with `Cancel` option.
  - Clear `Retry` button if connection times out.
- **Emergency Pinned Banner:**
  - National Cyber Crime Helpline card: **Dial 1930 (Toll Free 24x7)** + link to `cybercrime.gov.in`.

---

### Screen 2: Verdict & Explanation View (The Moment of Truth)
When an analysis completes, the UI transforms into a clear, reassuring result card:
1. **Traffic Light Verdict Header:**
   - Gigantic status card:
     - 🔴 **DANGER: Scam Detected (सावधान! यह धोखाधड़ी है)**
     - 🟡 **CAUTION: Suspicious Indicator Found (चेतावनी! संदिग्ध)**
     - 🟢 **SAFE: Verified Legitimate Entity (सुरक्षित)**
   - Plain-language summary (1 sentence max, 0 jargon).
2. **Voice Explanation Module (High Priority):**
   - Floating/prominent audio player with speaker wave animation.
   - Button: `🔊 Listen in Hindi / हिंदी में सुनें` (One tap plays pre-rendered native voice guidance explaining why it's a scam).
3. **Why It's Dangerous (Expandable Reason Pills):**
   - Tag badges: *"Fake Electricity Bill"*, *"Lookalike Banking Domain"*, *"Urgency Pressure Tactics"*.
4. **Immediate Action Checklist ("What you should do right now"):**
   - Step 1: 🛑 Do not click or reply.
   - Step 2: 🚫 Block sender on WhatsApp/SMS.
   - Step 3: 📞 If money was lost, call **1930** within golden hour.
   - Step 4: Link to Safety Confirmation / `/thank-you` route.

---

### Screen 3: APK Package & Fine-Print Terms Loophole Inspector
Specialized verdict layout when a user uploads an Android `.apk` file:
1. **App Identity Card:**
   - Package Name, Version, App Label, and Total Permissions Count.
2. **Dangerous Permissions Grid:**
   - Visual risk badges for sensitive accesses:
     - ⚠️ `RECEIVE_SMS / READ_SMS` (Steals bank OTPs).
     - ⚠️ `BIND_ACCESSIBILITY_SERVICE` (Screen overlay / keylogger banking trojan).
     - ⚠️ `READ_CONTACTS` (Used by illegal loan sharks to harass family/friends).
     - ⚠️ `SYSTEM_ALERT_WINDOW` (Fake lockscreen or fake payment overlay).
3. **Fine-Print Loophole Warnings (Predatory Terms Reader):**
   - Cards warning the user about predatory clauses hidden in the app's user agreement:
     - **Contact Harassment Waiver:** *"App reserves right to call all phone contacts in case of dispute"*. Shows direct quoted excerpt.
     - **Hidden Recurring Auto-Debit:** Auto-renewal fee buried in clause 14.
     - **Legal Dispute Waiver:** Forced arbitration waiving Indian consumer court rights.
     - **Gallery & Storage Scraping:** Grants access to scan personal photos.
4. **Recommended Action:**
   - Prominent red action: `🗑️ Uninstall or Delete File Immediately`.

---

### Screen 4: Supporting Pages & PWA Modals
1. **Camera QR Scanner Modal:** Fullscreen mobile viewfinder with flashlight toggle, scan box outline, and back button.
2. **Language Picker Modal:** Clean 2-column grid with native scripts (`English`, `हिन्दी`, `বাংলা`, `मराठी`, `ಕನ್ನಡ`).
3. **Privacy Policy Page (`/privacy`):** Plain-language DPDP Act 2023 zero-retention guarantee diagram.
4. **Terms & Conditions Page (`/terms`):** Clear disclaimers and emergency 1930 escalation protocols.
5. **Thank You Page (`/thank-you`):** Positive reinforcement screen celebrating safe cyber hygiene with share buttons for family WhatsApp groups.
6. **Custom 404 Page (`/not-found`):** Reassuring lost-page screen directing back to the scanner.

---

## 5. UI/UX Redesign Deliverables Expected from Emergent AI
1. **High-Fidelity Component Wireframes / Mockups:**
   - Modern glassmorphism / tactile neumorphic dark-theme aesthetics.
   - Mobile-first layouts (360px × 800px standard viewport).
2. **Design Tokens & Theme Guide:**
   - Color hex codes (Backgrounds, Borders, Verdict Surfaces, Text hierarchy).
   - Component spacing, border-radii (`16px–24px` rounded friendly look), shadow elevation.
3. **Interactive Micro-Interactions:**
   - Tap feedback animations for the big Scan button.
   - Visual audio wave pulsating effect for the Voice Guidance player.
   - Smooth accordion transitions for predatory loophole cards.
4. **Family-Shareable Safety Cards:**
   - An eye-catching "Warning Card" graphic layout that a user can screenshot or share directly to WhatsApp to protect their parents/relatives.
