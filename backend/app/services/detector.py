import re
from typing import Dict, Any, List

from backend.app.core.config import settings
from backend.app.services.url_analyzer import url_analyzer
from backend.app.services.onnx_classifier import onnx_classifier
from backend.app.services.action_engine import action_engine


def calculate_risk_level(score: float) -> str:
    """Map continuous risk score to categorical risk level based on configured thresholds."""
    if score < 0.30:
        return "low"
    elif score < 0.60:
        return "medium"
    elif score < 0.85:
        return "high"
    else:
        return "critical"


class ScamDetector:
    """Central risk fusion engine combining text neural/rule signals with URL lexical indicators."""

    def __init__(self):
        self.model_version = settings.MODEL_VERSION
        self.rules_version = action_engine.rules_version

    def analyze(
        self,
        input_type: str,
        content: str,
        language: str = "en",
        user_action_state: str = "not_acted"
    ) -> Dict[str, Any]:
        """Perform zero-retention in-memory scan of text, URLs, or QR payloads."""
        sanitized_content = content.strip()

        # 1. URL & Domain Analysis
        url_analysis = url_analyzer.analyze_text_for_urls(sanitized_content)

        # 2. Text Analysis via IndicBERT / Baseline Engine
        text_analysis = onnx_classifier.predict(sanitized_content)

        # 3. Special handling for QR inputs
        qr_reasons = []
        qr_score_boost = 0.0
        if input_type == "qr":
            if sanitized_content.startswith("upi://pay"):
                qr_reasons.append("QR_LEADS_TO_PAYMENT")
                # Scammers often trick victims into scanning QR codes to "receive money"
                if "receive" in sanitized_content.lower() or "credit" in sanitized_content.lower():
                    qr_reasons.append("ENTER_PIN_TO_RECEIVE")
                    qr_score_boost = 0.80
                else:
                    qr_score_boost = 0.40

        # 4. Signal Fusion & Risk Scoring
        url_score = url_analysis["max_url_score"]
        text_score = text_analysis["score"]

        # If a harmful lookalike or blocklist domain is present, ensure verdict is high/critical
        # even if text is benign or short (e.g. "Hi click here sbi-kyc-update.xyz")
        if url_score >= 0.70:
            if text_score > 0.50:
                # Compound risk: both suspicious text and malicious link
                combined_score = min(1.0, max(url_score, text_score) + 0.08)
            else:
                combined_score = url_score
        else:
            # Predominantly text-driven or low-risk URL
            combined_score = text_score

        if qr_score_boost > 0:
            combined_score = max(combined_score, qr_score_boost)

        # Allowlist Dampener: If message contains verified official domain (e.g. *.gov.in, sbi.co.in)
        # and no malicious demands (PIN entry, OTP sharing) exist, classify as legitimate/low risk
        has_allowlisted_domain = any(d.get("is_allowlisted") for d in url_analysis.get("domain_results", []))
        if has_allowlisted_domain and not ("ENTER_PIN_TO_RECEIVE" in text_analysis["reasons"] or "ASKS_FOR_OTP" in text_analysis["reasons"]):
            combined_score = min(combined_score, 0.15)

        # Round to 2 decimal places
        combined_score = round(min(1.0, max(0.0, combined_score)), 2)
        risk_level = calculate_risk_level(combined_score)

        # 5. Determine Primary Category
        primary_category = text_analysis["category"]
        if primary_category == "OTHER":
            if "FAKE_BANK_DOMAIN" in url_analysis["reasons"]:
                primary_category = "FAKE_BANK_LINK"
            elif "QR_LEADS_TO_PAYMENT" in qr_reasons:
                primary_category = "MALICIOUS_QR"
            elif url_score >= 0.70:
                primary_category = "FAKE_BANK_LINK"

        # If text explicitly mentions KYC alongside a fake bank link
        if primary_category in ["OTHER", "FAKE_BANK_LINK"] and "FAKE_KYC_PROMPT" in text_analysis["reasons"]:
            primary_category = "FAKE_KYC"

        # 6. Aggregate Reason Codes (Order of significance, deduplicated)
        reason_codes: List[str] = []
        for r in (
            url_analysis["reasons"] +
            qr_reasons +
            text_analysis["reasons"]
        ):
            if r not in reason_codes:
                reason_codes.append(r)

        # If high risk but no explicit reason code found, assign generic threat code
        if combined_score >= 0.60 and not reason_codes:
            reason_codes.append("UNKNOWN_SENDER_IMPERSONATION")

        # 7. Action Engine Lookup
        action_codes = action_engine.get_actions(
            category=primary_category,
            risk_level=risk_level,
            user_action_state=user_action_state
        )

        return {
            "risk_score": combined_score,
            "risk_level": risk_level,
            "category": primary_category,
            "reason_codes": reason_codes,
            "action_codes": action_codes,
            "model_version": self.model_version,
            "rules_version": action_engine.rules_version,
            "extracted_domains": url_analysis["domains"],
            "primary_domain_hash": url_analysis["primary_domain_hash"]
        }


detector = ScamDetector()
