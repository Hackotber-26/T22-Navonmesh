import re
from typing import Dict, Any, List, Tuple


class TextScamBaseline:
    """Rules-based text scam analyzer covering native Indic scripts and romanized Hinglish/Benglish."""

    def __init__(self):
        # 1. Category patterns with regexes across Hindi, Bengali, Marathi, Kannada, English, and Romanized
        self.category_patterns = {
            "FAKE_KYC": [
                r'(?i)\b(kyc\s*(update|pending|block|expire|deactivat|verif)|pan\s*card\s*link|aadhaar\s*link)\b',
                r'(?i)\b(account\s*(will\s*be\s*)?(blocked|suspended|deactivated|closed)\s*(today|within\s*\d+\s*(hours?|hrs?)))\b',
                r'(?i)\b(khata\s*(band|block)\s*(ho\s*jayega|hoga)|kyc\s*karaye|kyc\s*nahi\s*kiya)\b',
                # Devanagari (Hindi / Marathi)
                r'(केवाईसी\s*(अपडेट|पेंडिंग|सत्यापन|ब्लॉक))',
                r'(खाता\s*(ब्लॉक|बंद)\s*(हो\s*जाएगा|किया\s*जाएगा|होईल))',
                r'(पैन\s*कार्ड\s*(लिंक|अपडेट))',
                # Bengali
                r'(কেওয়াইসি\s*(আপডেট|পেন্ডিং|ব্লক))',
                r'(অ্যাকাউন্ট\s*(ব্লক|বন্ধ)\s*হয়ে\s*যাবে)',
                # Kannada
                r'(ಕೆವೈಸಿ\s*(ನವೀಕರಿಸಿ|ಬಾಕಿ|ನಿರ್ಬಂಧಿಸಲಾಗಿದೆ))',
                r'(ಖಾತೆ\s*(ನಿರ್ಬಂಧಿಸಲಾಗಿದೆ|ಮುಚ್ಚಲಾಗುತ್ತದೆ))',
            ],
            "ELECTRICITY_BILL": [
                r'(?i)\b(electricity\s*(bill|power|connection)?\s*.*(disconnect|cutoff|suspend|cut\s*off))\b',
                r'(?i)\b(power\s*will\s*be\s*disconnected\s*(tonight|today|at\s*\d+))\b',
                r'(?i)\b(bijli\s*(bill|connection|power)?\s*.*(kat\s*jayegi|band\s*hogi|kat\s*di\s*jayegi|cut))\b',
                r'(?i)\b(call\s*electricity\s*officer|contact\s*power\s*officer)\b',
                # Devanagari (Hindi / Marathi)
                r'(बिजली\s*(?:बिल|कनेक्शन|पावर)?\s*.*(?:काट|कट|बंद|डिस्कनेक्ट))',
                r'(विद्युत\s*(?:पुरवठा|कनेक्शन|बिल)?\s*.*(?:खंडित|कापला|बंद))',
                # Bengali
                r'(বিদ্যুৎ\s*(?:সংযোগ|বিল)?\s*.*(?:বিচ্ছিন্ন|কেটে\s*দেওয়া|কাটা))',
                # Kannada
                r'(ವಿದ್ಯುತ್\s*(?:ಸಂಪರ್ಕ|ಬಿಲ್)?\s*.*(?:ಕಡಿತ|ರದ್ದು|ಸ್ಥಗಿತ))',
            ],
            "UPI_COLLECT_FRAUD": [
                r'(?i)\b(enter\s*(upi)?\s*pin\s*to\s*(receive|credit|claim|get)|pin\s*daal\s*kar\s*(paise|cash))\b',
                r'(?i)\b(collect\s*request\s*of\s*rs|accept\s*collect\s*request|claim\s*refund\s*of\s*rs)\b',
                r'(?i)\b(scan\s*(this)?\s*qr\s*to\s*(receive|get|credit)\s*(money|cash|payment))\b',
                # Devanagari
                r'((पैसे|रुपये)\s*(प्राप्त\s*करने|पाने)\s*के\s*लिए\s*पिन\s*(दर्ज\s*करें|डालें))',
                r'(कलेक्ट\s*रिक्वेस्ट\s*(स्वीकार|accept)\s*करें)',
                # Bengali
                r'(টাকা\s*পাওয়ার\s*জন্য\s*ইউপিআই\s*পিন\s*দিন)',
                # Kannada
                r'(ಹಣ\s*ಪಡೆಯಲು\s*ಯುಪಿಐ\s*ಪಿನ್\s*(ನಮೂದಿಸಿ|ಹಾಕಿ))',
            ],
            "PARCEL_DELIVERY": [
                r'(?i)\b(package|parcel|shipment|courier)\s*(on\s*hold|pending|undelivered|held\s*at\s*customs)\b',
                r'(?i)\b(india\s*post|speed\s*post|delhivery|bluedart)\s*(package|address\s*incomplete|fee\s*due)\b',
                r'(?i)\b(pay\s*(rs\.?|inr)?\s*\d+\s*(redelivery|customs?|clearance)\s*fee)\b',
                # Devanagari
                r'(पार्सल\s*(अटका\s*हुआ|होल्ड\s*पर|डिलीवर\s*नहीं\s*हो\s*सका))',
                r'(डाक\s*घर|इंडिया\s*पोस्ट\s*पार्सल)',
                # Bengali
                r'(পার্সেল\s*(আটকে\s*গেছে|ডেলিভারি\s*ব্যর্থ))',
                # Kannada
                r'(ಪಾರ್ಸೆಲ್\s*(ತಡೆಹಿಡಿಯಲಾಗಿದೆ|ವಿತರಣೆ\s*ವಿಫಲವಾಗಿದೆ))',
            ],
            "LOTTERY_PRIZE": [
                r'(?i)\b(congratulations|congrats|lucky\s*winner|won\s*(rs\.?|inr)?\s*[\d,]+|kbc\s*(lottery|lucky\s*draw))\b',
                r'(?i)\b(lottery\s*winner|claim\s*your\s*(car|prize|cashback|cash\s*reward))\b',
                r'(?i)\b(25\s*lakh\s*(lottery|kbc)|claim\s*free\s*recharge)\b',
                # Devanagari
                r'(बधाई\s*हो|लॉटरी\s*जीत\s*गए|केबीसी\s*लकी\s*ड्रॉ|इनाम\s*मिला\s*है)',
                # Bengali
                r'(অভিনন্দন|লটারি\s*জিতেছেন|পুরস্কার\s*পেয়েছেন)',
                # Kannada
                r'(ಅಭಿನಂದನೆಗಳು|ಲಾಟರಿ\s*ಗೆದ್ದಿದ್ದೀರಿ|ಬಹುಮಾನ\s*ಗೆದ್ದಿದ್ದೀರಿ)',
            ],
            "JOB_SCAM": [
                r'(?i)\b(work\s*from\s*home|part\s*time\s*job|earn\s*(rs\.?|inr)?\s*\d+[\d,-]*\s*(daily|per\s*day))\b',
                r'(?i)\b(like\s*youtube\s*videos\s*(and\s*earn|job)|telegram\s*(task|job|income))\b',
                r'(?i)\b(ghar\s*baithe\s*(paise\s*kamaye|kamaye\s*daily))\b',
                # Devanagari
                r'(घर\s*बैठे\s*(पैसे\s*कमाएं|कमाई)|पार्ट\s*टाइम\s*जॉब)',
                # Bengali
                r'(ঘরে\s*বসে\s*(টাকা\s*আয়|পার্ট\s*টাইম\s*কাজ))',
                # Kannada
                r'(ಮನೆಯಲ್ಲೇ\s*ಕುಳಿತು\s*(ಗಳಿಸಿ|ಉದ್ಯೋಗ))',
            ],
        }

        # 2. Specific Reason Code triggers
        self.reason_indicators = {
            "URGENCY": [
                r'(?i)\b(immediately|urgent|within\s*\d+\s*(hours?|mins?|minutes?)|today\s*itself|tonight|last\s*warning)\b',
                r'(?i)\b(turant|aaj\s*hi|aakhri\s*chetavani|24\s*ghante)\b',
                r'(तुरंत|आज\s*ही|अंतिम\s*चेतावनी|तातडीने|অবিলম্বে|ತಕ್ಷಣ)',
            ],
            "THREAT_OF_BLOCKING": [
                r'(?i)\b(will\s*be\s*(blocked|suspended|stopped|deactivated|closed|disconnected))\b',
                r'(?i)\b(band\s*kar\s*diya\s*jayega|block\s*(?:hoga|ho\s*jayega)|kat\s*jayega)\b',
                r'(ब्लॉक\s*हो\s*जाएगा|बंद\s*किया\s*जाएगा|काट\s*दिया\s*जाएगा|खंडित|বিচ্ছিন্ন|(?:ব্লক|বন্ধ)\s*(?:হয়ে\s*যাবে|করা\s*হবে)|(?:ನಿರ್ಬಂಧಿಸಲಾಗಿದೆ|ಮುಚ್ಚಲಾಗುತ್ತದೆ))',
            ],
            "ENTER_PIN_TO_RECEIVE": [
                r'(?i)\b(enter\s*(upi)?\s*pin\s*to\s*(receive|get|claim)|pin\s*daal\s*kar\s*paise)\b',
                r'(पैसे\s*पाने\s*के\s*लिए\s*पिन|पिन\s*डालकर\s*पैसे|টাকা\s*পেতে\s*পিন)',
            ],
            "ASKS_FOR_OTP": [
                r'(?i)\b(send\s*(your\s*)?otp|share\s*(your\s*)?otp|forward\s*otp|tell\s*otp|verify\s*otp\s*over\s*call)\b',
                r'(?i)\b(otp\s*share\s*kare|otp\s*bhejo|otp\s*bataye)\b',
                r'(ओटीपी\s*(शेयर\s*करें|बताएं|भेजें)|ওটিপি\s*(দিন|পাঠান))',
            ],
            "FAKE_KYC_PROMPT": [
                r'(?i)\b(update\s*kyc|kyc\s*(?:update|verification|pending|karaye|kare|link)|pan\s*update|aadhaar\s*link)\b',
                r'(केवाईसी\s*(?:अपडेट|सत्यापन|कराएं|करें)|কেওয়াইসি\s*(?:আপডেট|পেন্ডিং)|ಕೆವೈಸಿ\s*ನವೀಕರಿಸಿ)',
            ],
            "ELECTRICITY_DISCONNECT_THREAT": [
                r'(?i)\b(electricity|power|bijli)\s*(?:bill|connection)?\s*.*(disconnect|cut\s*off|kat\s*jayegi)\b',
                r'(बिजली\s*.*(?:काट|कट|बंद)|विद्युत\s*.*(?:खंडित|कापला)|বিদ্যুৎ\s*.*(?:বিচ্ছিন্ন|কাটা)|ವಿದ್ಯುತ್\s*.*(?:ಕಡಿತ|ರದ್ದು))',
            ],
            "PRIZE_OR_LOTTERY": [
                r'(?i)\b(lottery|lucky\s*draw|won\s*prize|kbc\s*winner|cashback\s*reward)\b',
                r'(लॉटरी|इनाम|लकी\s*ड्रॉ|লটারি)',
            ],
            "PARCEL_FEE_REQUEST": [
                r'(?i)\b(redelivery\s*fee|customs?\s*fee|package\s*on\s*hold|courier\s*fee)\b',
                r'(पार्सल\s*शुल्क|কাস্টমস\s*ফি)',
            ],
            "UPI_COLLECT_REQUEST": [
                r'(?i)\b(collect\s*request|upi\s*collect|approve\s*request\s*to\s*receive)\b',
                r'(कलेक्ट\s*रिक्वेस्ट)',
            ],
            "UNKNOWN_SENDER_IMPERSONATION": [
                r'(?i)\b(dear\s*customer|bank\s*officer|electricity\s*officer|courier\s*executive)\b',
            ],
        }

        # 3. Legitimate Transactional Signals (False Positive Mitigators)
        self.legitimate_indicators = [
            # Standard bank credit/debit alerts
            r'(?i)\b(credited\s*with\s*(inr|rs\.?)|debited\s*(by|for)\s*(inr|rs\.?))\b',
            r'(?i)\b(available\s*bal(ance)?\s*:\s*(inr|rs\.?)|avl\s*bal\s*:)\b',
            r'(?i)\b(spent\s*on\s*your\s*card|at\s*pos\s*\d+|txn\s*id\s*:)\b',
            r'(?i)\b(ref\s*no\.?\s*:?\s*\d+|utr\s*no\.?\s*:?\s*\d+)\b',
            # Authentic OTP protective warnings
            r'(?i)\b(never\s*share\s*(your\s*)?otp|do\s*not\s*share\s*(this\s*)?otp\s*with\s*anyone)\b',
            r'(?i)\b(valid\s*for\s*\d+\s*(mins?|minutes?)|otp\s*is\s*confidential)\b',
            r'(?i)\b(bank\s*never\s*asks\s*for\s*(your\s*)?otp|kisi\s*ke\s*saath\s*share\s*na\s*kare)\b',
            r'(ओटीपी\s*किसी\s*के\s*साथ\s*साझा\s*ना\s*करें|কাউকে\s*ওটিপি\s*দেবেন\s*না)'
        ]

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze text content for fraud patterns and return raw score, category, and reasons."""
        matched_categories: Dict[str, int] = {}
        matched_reasons: List[str] = []

        # Check categories
        for cat, patterns in self.category_patterns.items():
            count = 0
            for pat in patterns:
                if re.search(pat, text):
                    count += 1
            if count > 0:
                matched_categories[cat] = count

        # Check reason codes
        for reason, patterns in self.reason_indicators.items():
            for pat in patterns:
                if re.search(pat, text):
                    if reason not in matched_reasons:
                        matched_reasons.append(reason)
                    break

        # Check legitimate indicators
        legit_matches = 0
        for pat in self.legitimate_indicators:
            if re.search(pat, text):
                legit_matches += 1

        # Calculate base text risk score
        base_score = 0.0
        primary_category = "OTHER"

        if matched_categories:
            # Pick highest matched category
            primary_category = max(matched_categories, key=matched_categories.get)
            match_count = matched_categories[primary_category]

            if match_count >= 2:
                base_score = 0.78
            else:
                base_score = 0.62

            # Additional severity if urgency or blocking is explicitly threatened
            if "THREAT_OF_BLOCKING" in matched_reasons:
                base_score += 0.12
            if "URGENCY" in matched_reasons:
                base_score += 0.08
            if "ENTER_PIN_TO_RECEIVE" in matched_reasons:
                base_score += 0.15
        elif matched_reasons:
            base_score = 0.35 + (0.1 * min(len(matched_reasons), 3))

        # Legitimate dampener:
        # If strong transactional keywords or bank safety warnings are present,
        # AND no direct fraud demands (like enter pin or fake kyc) exist:
        if legit_matches > 0:
            if not matched_categories:
                # Completely legitimate message
                base_score = max(0.05, base_score - 0.45)
            else:
                # Has some keywords (e.g. OTP warning), but if it's a defensive warning
                if "never share" in text.lower() and primary_category not in {"UPI_COLLECT_FRAUD", "FAKE_KYC"}:
                    base_score = max(0.10, base_score - 0.35)

        base_score = min(1.0, max(0.0, base_score))

        return {
            "category": primary_category,
            "score": round(base_score, 2),
            "reasons": matched_reasons,
            "legitimate_matches": legit_matches,
            "has_threats": len(matched_categories) > 0 or len(matched_reasons) > 0
        }


text_scam_baseline = TextScamBaseline()
