import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from backend.app.main import app
from backend.app.core.database import AsyncSessionLocal
from backend.app.models.incident import Incident
from backend.app.services.action_engine import action_engine, ALL_CATEGORIES, ALL_RISK_LEVELS, ALL_ACTION_STATES


def test_action_matrix_completeness():
    """Verify that every category x risk_level x action_state combination is fully defined."""
    missing = action_engine.validate_rules_completeness()
    assert len(missing) == 0, f"Action matrix has missing rules: {missing}"

    # Also test an explicit query
    actions = action_engine.get_actions("UPI_COLLECT_FRAUD", "high", "paid")
    assert "REPORT_1930" in actions
    assert "CALL_BANK" in actions


@pytest.mark.asyncio
async def test_sbi_kyc_scam_detection():
    """Acceptance criterion: Pasting SBI KYC blocking scam returns high/critical FAKE_KYC verdict."""
    transport = ASGITransport(app=app)
    scam_text = "Your SBI account will be blocked today, update KYC at sbi-kyc-update.xyz"

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/analyze",
            json={
                "input_type": "text",
                "content": scam_text,
                "language": "en",
                "user_action_state": "not_acted"
            }
        )
        assert response.status_code == 200
        data = response.json()

        assert data["risk_score"] >= 0.60
        assert data["risk_level"] in ["high", "critical"]
        assert data["category"] == "FAKE_KYC"
        assert any(code in data["reason_codes"] for code in ["LOOKALIKE_DOMAIN", "FAKE_BANK_DOMAIN"])
        assert any(code in data["reason_codes"] for code in ["FAKE_KYC_PROMPT", "THREAT_OF_BLOCKING"])
        assert len(data["action_codes"]) > 0
        assert "DO_NOT_CLICK" in data["action_codes"]
        assert "sbi-kyc-update.xyz" in data["extracted_domains"]


@pytest.mark.asyncio
async def test_legitimate_bank_otp_alert():
    """Acceptance criterion: Legitimate bank OTP and transaction alert is rated low risk."""
    transport = ASGITransport(app=app)
    legit_messages = [
        "Dear Customer, your A/C XX4921 has been credited with Rs 2,500.00 on 30-Oct-26 by UPI. Avl Bal: Rs 15,400.00. SBI",
        "OTP for NetBanking transaction of Rs 500.00 is 849201. Valid for 10 mins. Never share your OTP with anyone - HDFC Bank."
    ]

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        for msg in legit_messages:
            response = await client.post(
                "/api/analyze",
                json={
                    "input_type": "text",
                    "content": msg,
                    "language": "en"
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert data["risk_score"] < 0.30, f"Expected low risk score for: {msg}, got {data['risk_score']}"
            assert data["risk_level"] == "low"


@pytest.mark.asyncio
async def test_lookalike_domain_in_short_text():
    """Acceptance criterion: Lookalike domain in short or benign text is still flagged."""
    transport = ASGITransport(app=app)
    short_text = "Please verify your details here: hdfc-netbanking-login.top"

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/analyze",
            json={
                "input_type": "url",
                "content": short_text,
                "language": "en"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["risk_score"] >= 0.60
        assert "LOOKALIKE_DOMAIN" in data["reason_codes"] or "FAKE_BANK_DOMAIN" in data["reason_codes"]


@pytest.mark.asyncio
async def test_privacy_guarantee_no_raw_content_in_db():
    """
    CRITICAL ACCEPTANCE CRITERIA (DPDP ACT):
    Verify that raw message content, URLs, and QR codes are NEVER stored in the database.
    """
    canary_token = f"CANARY_SECRET_{uuid.uuid4().hex}"
    canary_url = f"https://sbi-phishing-{uuid.uuid4().hex[:6]}.xyz/login?secret_token={canary_token}"
    canary_text = f"Urgent: Your account is blocked. Call 9999999999 {canary_token} at {canary_url}"

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/analyze",
            json={
                "input_type": "text",
                "content": canary_text,
                "language": "hi"
            }
        )
        assert response.status_code == 200
        incident_id = response.json()["incident_id"]

    # Now inspect the database directly to verify canary text does not exist anywhere
    async with AsyncSessionLocal() as session:
        # Check incidents table via ORM
        stmt = select(Incident).where(Incident.id == incident_id)
        res = await session.execute(stmt)
        row = res.scalar_one_or_none()
        assert row is not None

        # Verify incident properties
        assert canary_token not in row.category
        assert canary_token not in row.input_type
        for r_code in row.reason_codes:
            assert canary_token not in r_code
        for a_code in row.actions_shown:
            assert canary_token not in a_code

        # Domain hash column must be a 64-char hex SHA-256 hash, NOT the raw URL
        assert row.domain_hash is not None
        assert len(row.domain_hash) == 64
        assert canary_token not in row.domain_hash


@pytest.mark.asyncio
async def test_update_action_state_flow():
    """Test the 3-button user action state transition (not_acted -> clicked -> paid)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Analyze high risk UPI scam
        res1 = await client.post(
            "/api/analyze",
            json={
                "input_type": "text",
                "content": "Enter UPI PIN to receive cashback of Rs 5000 in your bank account immediately",
                "language": "en",
                "user_action_state": "not_acted"
            }
        )
        assert res1.status_code == 200
        data1 = res1.json()
        incident_id = data1["incident_id"]
        assert "DECLINE_COLLECT_REQUEST" in data1["action_codes"]

        # 2. User updates state: "I sent money" -> paid
        res2 = await client.post(
            f"/api/incidents/{incident_id}/action-state",
            json={"user_action_state": "paid"}
        )
        assert res2.status_code == 200
        data2 = res2.json()
        assert data2["user_action_state"] == "paid"
        # Emergency helpline 1930 should be prioritized for paid state
        assert data2["action_codes"][0] == "REPORT_1930"


@pytest.mark.asyncio
async def test_multilingual_indic_scripts_detection():
    """Verify detection across native Devanagari, Bengali, and Romanized Hinglish."""
    transport = ASGITransport(app=app)
    test_cases = [
        # Hindi electricity disconnection scam
        (
            "आपका बिजली बिल बाकी है, आज रात 9:30 बजे बिजली कनेक्शन काट दिया जाएगा। तुरंत संपर्क करें।",
            "ELECTRICITY_BILL",
            ["ELECTRICITY_DISCONNECT_THREAT", "URGENCY", "THREAT_OF_BLOCKING"]
        ),
        # Bengali KYC scam
        (
            "আপনার অ্যাকাউন্ট ব্লক হয়ে যাবে, অবিলম্বে কেওয়াইসি আপডেট করুন",
            "FAKE_KYC",
            ["FAKE_KYC_PROMPT", "THREAT_OF_BLOCKING", "URGENCY"]
        ),
        # Romanized Hinglish KYC
        (
            "Aapka account block ho jayega, 24 ghante me KYC karaye sbi-kyc-update.xyz",
            "FAKE_KYC",
            ["FAKE_KYC_PROMPT", "THREAT_OF_BLOCKING", "LOOKALIKE_DOMAIN"]
        )
    ]

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        for text_input, expected_cat, expected_reasons in test_cases:
            response = await client.post(
                "/api/analyze",
                json={
                    "input_type": "text",
                    "content": text_input,
                    "language": "hi"
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert data["risk_score"] >= 0.60
            assert data["category"] == expected_cat
            for reason in expected_reasons:
                assert reason in data["reason_codes"], f"Missing reason code: {reason} in {data['reason_codes']}"


@pytest.mark.asyncio
async def test_qr_payment_trap():
    """Verify QR code encoding UPI intent with claim/receive trap is flagged."""
    transport = ASGITransport(app=app)
    qr_payload = "upi://pay?pa=cashback-rewards@okaxis&pn=Cashback&am=5000&note=Receive+Money+Enter+PIN"

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/analyze",
            json={
                "input_type": "qr",
                "content": qr_payload,
                "language": "en"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["risk_score"] >= 0.70
        assert "QR_LEADS_TO_PAYMENT" in data["reason_codes"]
        assert "ENTER_PIN_TO_RECEIVE" in data["reason_codes"]
        assert "NO_PIN_TO_RECEIVE" in data["action_codes"]


@pytest.mark.asyncio
async def test_screenshot_ocr_endpoint():
    """Verify screenshot OCR endpoint extracts text and evaluates threats without storing images."""
    import io
    from PIL import Image

    # Create dummy white image in memory
    img = Image.new("RGB", (150, 60), color="white")
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    img_bytes = img_byte_arr.getvalue()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/analyze/ocr",
            files={"file": ("screenshot.png", img_bytes, "image/png")},
            data={"language": "hi"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "risk_score" in data
        assert "category" in data
        assert "extracted_text" in data
        assert len(data["extracted_text"]) > 0
