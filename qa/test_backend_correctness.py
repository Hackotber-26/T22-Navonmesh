#!/usr/bin/env python3
"""
Section 2: Backend Correctness Automated Audit Suite
Tests:
- 60+ categorized inputs (scams, legitimate, edge cases, evasions) across 5 languages
- Score boundaries, determinism, harmless text with bad domain
- Response shape, validation errors, input size cap
- 50 parallel requests with p50 and p95 latency
"""

import os
import sys
import json
import time
import asyncio
import statistics

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from httpx import AsyncClient, ASGITransport
from backend.app.main import app

# Define test inputs: category, lang, expected_type ("scam", "legit", "error"), text, note
TEST_INPUTS = [
    # --- 1. Scams across 5 languages & categories ---
    # Hindi (hi)
    {"cat": "ELECTRICITY_BILL", "lang": "hi", "type": "scam", "text": "प्रिय ग्राहक, आपका बिजली बिल बकाया है। आज रात 9:30 बजे बिजली काट दी जाएगी। तुरंत 9876543210 पर संपर्क करें।"},
    {"cat": "FAKE_KYC", "lang": "hi", "type": "scam", "text": "प्रिय एसबीआई ग्राहक, आपका बैंक खाता आज निलंबित कर दिया जाएगा। तुरंत केवाईसी अपडेट करने के लिए क्लिक करें: http://sbi-kyc-verify.top"},
    {"cat": "LOTTERY_PRIZE", "lang": "hi", "type": "scam", "text": "बधाई हो! आपने कौन बनेगा करोड़पति (KBC) लॉटरी में 25 लाख रुपये जीते हैं। व्हाट्सएप पर संपर्क करें 919876543210"},
    {"cat": "JOB_SCAM", "lang": "hi", "type": "scam", "text": "घर बैठे रोजाना 3000 से 5000 रुपये कमाएं! यूट्यूब वीडियो लाइक करने का काम। टेलीग्राम जॉइन करें: t.me/easywork2026"},
    {"cat": "UPI_COLLECT_FRAUD", "lang": "hi", "type": "scam", "text": "गूगल पे पर 2000 रुपये कैशबैक प्राप्त करने के लिए अपना यूपीआई पिन दर्ज करें।"},

    # Bengali (bn)
    {"cat": "ELECTRICITY_BILL", "lang": "bn", "type": "scam", "text": "প্রিয় গ্রাহক, আপনার বিদ্যুৎ বিল বাকি রয়েছে। আজ রাত ৮ টায় বিদ্যুৎ সংযোগ বিচ্ছিন্ন করা হবে। অবিলম্বে যোগাযোগ করুন।"},
    {"cat": "FAKE_KYC", "lang": "bn", "type": "scam", "text": "আপনার ব্যাংক একাউন্ট সাময়িকভাবে বন্ধ করা হয়েছে। প্যান কার্ড আপডেট করতে লিংকে যান: http://bank-pan-update.xyz"},
    {"cat": "PARCEL_DELIVERY", "lang": "bn", "type": "scam", "text": "ইন্ডিয়া পোস্ট: আপনার পার্সেল আটকে আছে। ডেলিভারির জন্য ২৫ টাকা চার্জ দিন: http://indiapost-redelivery.club"},
    {"cat": "UPI_COLLECT_FRAUD", "lang": "bn", "type": "scam", "text": "টাকা পেতে আপনার ইউপিআই পিন দিন এবং রিকোয়েস্ট একসেপ্ট করুন।"},
    {"cat": "JOB_SCAM", "lang": "bn", "type": "scam", "text": "পার্ট টাইম জব: দিনে ২ ঘন্টা কাজ করে মাসে ৫০,০০০ টাকা আয় করুন। টেলিগ্রাম গ্রুপে যোগ দিন।"},

    # Marathi (mr)
    {"cat": "ELECTRICITY_BILL", "lang": "mr", "type": "scam", "text": "प्रिय ग्राहक, तुमचे वीज बिल भरले नाही म्हणून आज रात्री वीज पुरवठा खंडित केला जाईल. महावितरण अधिकारी 9823012345 ला संपर्क करा."},
    {"cat": "FAKE_KYC", "lang": "mr", "type": "scam", "text": "तुमचे बँक खाते ब्लॉक झाले आहे. त्वरित केवायसी अपडेट करा: http://sbi-netbanking-login.site"},
    {"cat": "LOTTERY_PRIZE", "lang": "mr", "type": "scam", "text": "अभिनंदन! तुम्ही लकी ड्रॉ मध्ये 10 लाख रुपये जिंकले आहेत. बक्षीस मिळवण्यासाठी संपर्क करा."},
    {"cat": "UPI_COLLECT_FRAUD", "lang": "mr", "type": "scam", "text": "बक्षीस रक्कम मिळवण्यासाठी यूपीआय पिन टाका आणि विनंती स्वीकारा."},
    {"cat": "PARCEL_DELIVERY", "lang": "mr", "type": "scam", "text": "तुमचे पार्सल पत्ता चुकीचा असल्यामुळे अडकले आहे. पत्ता अपडेट करा http://speedpost-update.online"},

    # Kannada (kn)
    {"cat": "ELECTRICITY_BILL", "lang": "kn", "type": "scam", "text": "ಗ್ರಾಹಕರೇ, ನಿಮ್ಮ ಬೆಸ್ಕಾಂ ವಿದ್ಯುತ್ ಬಿಲ್ ಪಾವತಿಯಾಗಿಲ್ಲ. ಇಂದು ರಾತ್ರಿ ವಿದ್ಯುತ್ ಸಂಪರ್ಕ ಕಡಿತಗೊಳಿಸಲಾಗುವುದು. ಕರೆ ಮಾಡಿ."},
    {"cat": "FAKE_KYC", "lang": "kn", "type": "scam", "text": "ನಿಮ್ಮ ಬ್ಯಾಂಕ್ ಖಾತೆಯನ್ನು ನಿರ್ಬಂಧಿಸಲಾಗಿದೆ. ತಕ್ಷಣ ಕೆವೈಸಿ ಅಪ್‌ಡೇಟ್ ಮಾಡಲು ಇಲ್ಲಿ ಕ್ಲಿಕ್ ಮಾಡಿ: http://hdfc-kyc.top"},
    {"cat": "UPI_COLLECT_FRAUD", "lang": "kn", "type": "scam", "text": "ಕ್ಯಾಶ್‌ಬ್ಯಾಕ್ 5000 ಪಡೆಯಲು ಕಲೆಕ್ಟ್ ರಿಕ್ವೆಸ್ಟ್ ಒಪ್ಪಿಕೊಳ್ಳಿ ಮತ್ತು ಯುಪಿಐ ಪಿನ್ ಹಾಕಿ."},
    {"cat": "JOB_SCAM", "lang": "kn", "type": "scam", "text": "ಮನೆಯಿಂದಲೇ ಕೆಲಸ ಮಾಡಿ ದಿನಕ್ಕೆ 2000 ಗಳಿಸಿ. ಟೆಲಿಗ್ರಾಂ ಲಿಂಕ್ ಸಂಪರ್ಕಿಸಿ."},
    {"cat": "LOTTERY_PRIZE", "lang": "kn", "type": "scam", "text": "ಅಭಿನಂದನೆಗಳು! ನೀವು 15 ಲಕ್ಷ ಲಾಟರಿ ಗೆದ್ದಿದ್ದೀರಿ. ಹಣ ಪಡೆಯಲು ಕ್ಲಿಕ್ ಮಾಡಿ."},

    # English (en)
    {"cat": "FAKE_BANK_LINK", "lang": "en", "type": "scam", "text": "Dear customer, your HDFC bank account is suspended due to invalid PAN. Click http://hdfcbank-pan-portal.xyz/verify to reactivate now."},
    {"cat": "PARCEL_DELIVERY", "lang": "en", "type": "scam", "text": "India Post: Your package IN83921 could not be delivered due to incorrect address. Please update details within 24 hours at http://indiapost-redelivery.site"},
    {"cat": "JOB_SCAM", "lang": "en", "type": "scam", "text": "Amazon Part-Time Hiring! Earn Rs 2500 - 8000 daily by reviewing products. Contact recruiter on Telegram @amazonhiring2026"},
    {"cat": "UPI_COLLECT_FRAUD", "lang": "en", "type": "scam", "text": "PhonePe Reward: You have won Rs 4,999 cashback! Approve collect request and enter UPI PIN to deposit in your bank."},
    {"cat": "MALICIOUS_QR", "lang": "en", "type": "scam", "text": "upi://pay?pa=refund-agent@axisbank&pn=Refund&am=10000&tn=Enter+PIN+to+receive+refund"},

    # Romanized / Code-mixed (Hinglish, Benglish, Marathi-Rom, Kannada-Rom)
    {"cat": "ELECTRICITY_BILL", "lang": "hi", "type": "scam", "text": "Aapka bijli bill pending hai, aaj raat 9 baje power cut ho jayega. Turant contact kare bijli vibhag."},
    {"cat": "FAKE_KYC", "lang": "hi", "type": "scam", "text": "SBI Alert: Aapka account block hone wala hai. Aaj hi KYC update kare http://sbi-kyc-update.xyz"},
    {"cat": "UPI_COLLECT_FRAUD", "lang": "hi", "type": "scam", "text": "GPay cashback 3000 paane ke liye UPI PIN enter kare aur claim kare."},
    {"cat": "FAKE_KYC", "lang": "bn", "type": "scam", "text": "Apnar bank account suspend kora hoyeche. 24 ghontay KYC na korle bondho hobe http://sbi-kyc.site"},
    {"cat": "UPI_COLLECT_FRAUD", "lang": "bn", "type": "scam", "text": "Taka pete collect request accept korun ebong UPI PIN din."},
    {"cat": "ELECTRICITY_BILL", "lang": "mr", "type": "scam", "text": "Aapla bijli connection aaj ratri kapla jail, call electricity officer 9890012345."},
    {"cat": "FAKE_KYC", "lang": "mr", "type": "scam", "text": "Aaple SBI account block honar aahe, 24 tasat KYC purna kara."},
    {"cat": "ELECTRICITY_BILL", "lang": "kn", "type": "scam", "text": "Vidyuth bill baki ide, eevathu night connection cut aaguthe. Call 9845012345."},
    {"cat": "FAKE_KYC", "lang": "kn", "type": "scam", "text": "Nimma bank account block aagide. Eegale KYC update maadi."},

    # --- 2. Legitimate Messages (False Positive Controls) ---
    {"cat": "LEGITIMATE", "lang": "en", "type": "legit", "text": "Dear Customer, your A/C XX8492 has been credited with Rs 4,500.00 on 30-Oct-26 by UPI ref 429104829104. Avl Bal: Rs 28,400.00. - State Bank of India"},
    {"cat": "LEGITIMATE", "lang": "en", "type": "legit", "text": "849201 is the OTP for transaction of Rs 1,299.00 on your HDFC Bank Card ending 4019. Valid for 10 minutes. Do not share OTP with anyone."},
    {"cat": "LEGITIMATE", "lang": "en", "type": "legit", "text": "Your Amazon order 402-8392018 has been dispatched and will arrive tomorrow by 8 PM via ATS. Track at https://www.amazon.in"},
    {"cat": "LEGITIMATE", "lang": "en", "type": "legit", "text": "URGENT BILL REMINDER: Your BSES electricity bill CA 100294819 of Rs 1,450 is overdue. Pay before 02-Nov-26 to avoid late fees. Pay at https://www.bsesdelhi.com"},
    {"cat": "LEGITIMATE", "lang": "en", "type": "legit", "text": "Airtel: Your recharge of Rs 299 is expiring in 2 days. Recharge today on Airtel Thanks App to continue unlimited 5G data."},
    {"cat": "LEGITIMATE", "lang": "en", "type": "legit", "text": "Hey Mom, I will reach home by 7 PM today. Please keep dinner ready!"},

    {"cat": "LEGITIMATE", "lang": "hi", "type": "legit", "text": "प्रिय ग्राहक, आपके खाते XX4819 में 5,000.00 रुपये जमा किए गए हैं। कुल शेष: 12,400.00 रुपये। - पंजाब नेशनल बैंक"},
    {"cat": "LEGITIMATE", "lang": "hi", "type": "legit", "text": "आपके बैंक खाते के लिए ओटीपी 492014 है। यह 5 मिनट के लिए मान्य है। किसी के साथ साझा न करें - एसबीआई।"},
    {"cat": "LEGITIMATE", "lang": "hi", "type": "legit", "text": "बिजली बिल भुगतान सूचना: आपका माह अक्टूबर का बिल 850 रुपये जमा हो चुका है। धन्यवाद - यूपीपीसीएल।"},
    {"cat": "LEGITIMATE", "lang": "hi", "type": "legit", "text": "नमस्ते भैया, क्या आप कल दोपहर घर आ रहे हैं?"},

    {"cat": "LEGITIMATE", "lang": "bn", "type": "legit", "text": "প্রিয় গ্রাহক, আপনার একাউন্টে ২০০০ টাকা জমা হয়েছে। অবশিষ্ট ব্যালেন্স: ৯৫০০ টাকা। স্টেট ব্যাংক অফ ইন্ডিয়া।"},
    {"cat": "LEGITIMATE", "lang": "bn", "type": "legit", "text": "আপনার নেট ব্যাংকিং ট্রানজ্যাকশনের ওটিপি হল ৮২৯১০৩। কাউকে ওটিপি বলবেন না। - অ্যাক্সিস ব্যাংক।"},
    {"cat": "LEGITIMATE", "lang": "bn", "type": "legit", "text": "মা, আমি কাল সকালে বাড়ি ফিরছি।"},

    {"cat": "LEGITIMATE", "lang": "mr", "type": "legit", "text": "प्रिय ग्राहक, तुमच्या खात्यात रु. ३,००० जमा झाले आहेत. उपलब्ध शिल्लक: रु. १५,२००. बँक ऑफ महाराष्ट्र."},
    {"cat": "LEGITIMATE", "lang": "mr", "type": "legit", "text": "महावितरण: ऑक्टोबर महिन्याचे वीज बिल यशस्वीपणे भरले गेले आहे. पावती महावितरण ॲपवर उपलब्ध आहे."},

    {"cat": "LEGITIMATE", "lang": "kn", "type": "legit", "text": "ಗ್ರಾಹಕರೇ, ನಿಮ್ಮ ಖಾತೆಗೆ ರೂ. ೪,೦೦೦ ಜಮೆಯಾಗಿದೆ. ಲಭ್ಯವಿರುವ ಬ್ಯಾಲೆನ್ಸ್: ರೂ. ೧೦,೮೦೦. - ಕೆನರಾ ಬ್ಯಾಂಕ್."},
    {"cat": "LEGITIMATE", "lang": "kn", "type": "legit", "text": "ಬೆಸ್ಕಾಂ: ನಿಮ್ಮ ಅಕ್ಟೋಬರ್ ತಿಂಗಳ ವಿದ್ಯುತ್ ಬಿಲ್ ರೂ ೭೫೦ ಯಶಸ್ವಿಯಾಗಿ ಪಾವತಿಯಾಗಿದೆ."},

    # --- 3. Edge Cases & Boundary Tests ---
    {"cat": "EDGE", "lang": "en", "type": "edge", "text": "", "note": "empty string"},
    {"cat": "EDGE", "lang": "en", "type": "edge", "text": "    \n\t  \r  ", "note": "whitespace only"},
    {"cat": "EDGE", "lang": "en", "type": "edge", "text": "X" * 10000, "note": "10k characters (payload limit test)"},
    {"cat": "EDGE", "lang": "en", "type": "edge", "text": "😀🎉🚀🚨💰💳🔥📲", "note": "emoji only"},
    {"cat": "EDGE", "lang": "en", "type": "edge", "text": "Dear ग्राहक, your একাউন্ট is suspended for KYC update: http://sbi-kyc.top", "note": "mixed 3 scripts"},
    {"cat": "EDGE", "lang": "en", "type": "edge", "text": "S\u200bB\u200bI K\u200bY\u200bC u\u200bp\u200bd\u200ba\u200bt\u200be http://sbi-kyc.top", "note": "zero-width space evasion"},
    {"cat": "EDGE", "lang": "en", "type": "edge", "text": "Account update\x00with null byte http://sbi-kyc.top", "note": "null byte injection"},
    {"cat": "EDGE", "lang": "en", "type": "edge", "text": "bit.ly/3xFraud", "note": "shortened URL"},
    {"cat": "EDGE", "lang": "en", "type": "edge", "text": "http://xn--sb-via.com/login", "note": "punycode IDN homograph"},
    {"cat": "EDGE", "lang": "en", "type": "edge", "text": "http://192.168.1.100:8080/sbi/update", "note": "IP address host"},
    {"cat": "EDGE", "lang": "en", "type": "edge", "text": "HTTP://SBI-KYC-UPDATE.XYZ/LOGIN", "note": "uppercase host"},
    {"cat": "EDGE", "lang": "en", "type": "edge", "text": "http://sbi-kyc-update.xyz./login", "note": "trailing dot host"},
    {"cat": "EDGE", "lang": "en", "type": "edge", "text": "https://sbi.co.in@evil-phish.xyz/login", "note": "userinfo spoofing trick"},
    {"cat": "EDGE", "lang": "en", "type": "edge", "text": "javascript:alert(1)", "note": "javascript scheme URL"},
    {"cat": "EDGE", "lang": "en", "type": "edge", "text": "data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==", "note": "data scheme URL"},
    {"cat": "EDGE", "lang": "en", "type": "edge", "text": "upi://pay?pa=scammer@okhdfcbank&pn=ElectricityOffice&am=1200&cu=INR", "note": "UPI deep link"},

    # --- 4. Evasion Patterns ---
    {"cat": "EVASION", "lang": "en", "type": "evasion", "text": "Y o u r  S B I  a c c o u n t  i s  b l o c k e d  c l i c k  s b i - k y c . t o p", "note": "spaced letters"},
    {"cat": "EVASION", "lang": "en", "type": "evasion", "text": "S.B.I K.Y.C u.p.d.a.t.e at sbi-netbanking-portal.site", "note": "dotted keywords"},
    {"cat": "EVASION", "lang": "en", "type": "evasion", "text": "Y0ur 5B1 acc0unt i5 bl0cked upd4te n0w http://sbi-kyc.top", "note": "leetspeak"},
    {"cat": "EVASION", "lang": "hi", "type": "evasion", "text": "बिजली बिल भुगतान के लिए संपर्क करें ९८७६५४३२१०", "note": "Hindi devanagari digits"},
    {"cat": "EVASION", "lang": "en", "type": "evasion", "text": "Check details at https://sbi . kyc - update . xyz/login", "note": "split URL with spaces"},
    {"cat": "EVASION", "lang": "en", "type": "evasion", "text": "Call me on 91-987-654-3210 regarding your reward", "note": "hyphenated phone"},
    {"cat": "EVASION", "lang": "en", "type": "evasion", "text": "Good morning! Here is the latest photo: http://sbi-kyc-update.xyz", "note": "harmless text with bad domain"},
]


async def run_audit():
    from backend.app.core.rate_limiter import _memory_rate_limit
    _memory_rate_limit.clear()
    print(f"=== Backend Correctness Audit: Testing {len(TEST_INPUTS)} inputs ===")
    transport = ASGITransport(app=app)
    results = []
    false_positives = []
    scams_missed = []
    edge_results = []
    latencies = []

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        for idx, item in enumerate(TEST_INPUTS):
            _memory_rate_limit.clear()  # reset rate limit to isolate functional behavior
            text = item["text"]
            lang = item["lang"]
            expected_type = item["type"]
            input_type = "url" if text.startswith("http") or text.startswith("upi:") else "text"

            t0 = time.time()
            try:
                res = await client.post(
                    "/api/analyze",
                    json={
                        "input_type": input_type,
                        "content": text,
                        "language": lang,
                        "user_action_state": "not_acted"
                    }
                )
                elapsed = time.time() - t0
                latencies.append(elapsed)

                if res.status_code == 200:
                    data = res.json()
                    score = data.get("risk_score", 0.0)
                    level = data.get("risk_level", "low")
                    cat = data.get("category", "OTHER")
                    reasons = data.get("reason_codes", [])
                    actions = data.get("action_codes", [])

                    # Verify required fields
                    assert "incident_id" in data
                    assert "risk_score" in data
                    assert "risk_level" in data
                    assert "category" in data
                    assert "reason_codes" in data
                    assert "action_codes" in data

                    is_flagged = score >= 0.30

                    if expected_type == "scam" and not is_flagged:
                        scams_missed.append((idx, text, score, level, cat, item.get("note", "")))
                    elif expected_type == "legit" and is_flagged:
                        false_positives.append((idx, text, score, level, cat, reasons))
                    elif expected_type in ("edge", "evasion"):
                        edge_results.append((idx, item.get("note", ""), score, level, cat, reasons))

                    results.append({"status": 200, "score": score, "level": level, "cat": cat})
                else:
                    results.append({"status": res.status_code, "detail": res.text})
                    if expected_type in ("edge", "evasion"):
                        edge_results.append((idx, item.get("note", ""), res.status_code, "HTTP_ERROR", "", [res.text]))
            except Exception as e:
                results.append({"status": "EXCEPTION", "error": str(e)})

    # Print summary
    print(f"\n--- Results Summary ---")
    print(f"Total inputs tested: {len(TEST_INPUTS)}")
    print(f"Total False Positives on legitimate inputs: {len(false_positives)} / 17 legitimate messages")
    for fp in false_positives:
        print(f"  [FALSE POSITIVE] Score={fp[2]}, Level={fp[3]}, Cat={fp[4]}")
        print(f"    Text: {fp[1][:80]}")
        print(f"    Reasons: {fp[5]}")

    print(f"\nTotal Scams Missed (False Negatives): {len(scams_missed)} / 29 scam messages")
    for sm in scams_missed:
        print(f"  [SCAM MISSED] Score={sm[2]}, Level={sm[3]}, Cat={sm[4]}")
        print(f"    Text: {sm[1][:80]}")

    print(f"\n--- Edge Cases & Evasions Handled ---")
    for er in edge_results:
        print(f"  Note: {er[1]:<35} | Score/Status: {er[2]} | Level: {er[3]} | Cat: {er[4]} | Reasons: {er[5][:2]}")

    # Test 50 Parallel Requests
    print("\n--- Testing 50 Concurrent Requests ---")
    _memory_rate_limit.clear()
    sample_payload = {
        "input_type": "text",
        "content": "SBI Alert: Your account is blocked. Update KYC at http://sbi-kyc-update.xyz",
        "language": "hi",
        "user_action_state": "not_acted"
    }

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        async def send_one():
            t_start = time.time()
            r = await client.post("/api/analyze", json=sample_payload)
            return r.status_code, time.time() - t_start

        tasks = [send_one() for _ in range(50)]
        t_batch_start = time.time()
        batch_results = await asyncio.gather(*tasks)
        total_batch_time = time.time() - t_batch_start

        status_codes = [r[0] for r in batch_results]
        concurrent_latencies = [r[1] * 1000 for r in batch_results] # ms

        sorted_latencies = sorted(concurrent_latencies)
        p50 = sorted_latencies[int(len(sorted_latencies) * 0.50)]
        p95 = sorted_latencies[int(len(sorted_latencies) * 0.95)]
        errors = [c for c in status_codes if c != 200]

        print(f"Batch completed in: {total_batch_time:.3f}s")
        print(f"Status codes: 200s={status_codes.count(200)}, 429s={status_codes.count(429)}, Other errors={len(errors) - status_codes.count(429)}")
        print(f"Concurrency Latency: p50={p50:.2f}ms, p95={p95:.2f}ms, min={min(concurrent_latencies):.2f}ms, max={max(concurrent_latencies):.2f}ms")

    # Test Harmless text with bad domain
    print("\n--- Testing Harmless Text with Bad Domain ---")
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/analyze", json={
            "input_type": "text",
            "content": "Good morning family! Hope everyone is doing well today. See photos here: http://sbi-kyc-update.xyz",
            "language": "en"
        })
        d = res.json()
        print(f"Result for harmless text with bad domain: Score={d.get('risk_score')}, Level={d.get('risk_level')}, Reasons={d.get('reason_codes')}")

    # Test Determinism: 5 identical requests
    print("\n--- Testing Determinism (5 identical requests) ---")
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        scores = []
        for _ in range(5):
            res = await client.post("/api/analyze", json=sample_payload)
            scores.append(res.json()["risk_score"])
        print(f"Scores for 5 identical requests: {scores} -> Deterministic: {len(set(scores)) == 1}")

    # Test Score boundaries: Low (<0.3), Medium (0.3 - 0.59), High (0.6 - 0.84), Critical (>=0.85)
    print("\n--- Testing Score Boundaries in Code ---")
    boundary_cases = [
        ("Legitimate Bank Transaction", "Dear Customer, Rs 500 credited to account XX4910. SBI", "low"),
        ("Urgent Bill Reminder without link", "Your electricity bill is due tomorrow. Please pay to avoid late fee.", "low_or_medium"),
        ("Lookalike Link alone", "http://hdfc-netbanking-login.site", "high_or_critical"),
        ("Urgent threat + lookalike phishing domain", "Your SBI account will be blocked today, update KYC at http://sbi-kyc-update.xyz", "critical")
    ]
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        for title, text_sample, expected_bracket in boundary_cases:
            res = await client.post("/api/analyze", json={"input_type": "text", "content": text_sample, "language": "en"})
            d = res.json()
            print(f"  {title:<40}: Score={d.get('risk_score'):<4} | Level={d.get('risk_level'):<8} (Expected: {expected_bracket})")


if __name__ == "__main__":
    asyncio.run(run_audit())
