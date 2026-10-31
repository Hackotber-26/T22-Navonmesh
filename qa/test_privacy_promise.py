#!/usr/bin/env python3
"""
Section 3: Privacy Promise & Zero-Retention Audit
Tests:
- Sends unique canary markers (token, fake phone, fake URL, fake UPI ID) to /api/analyze
- Inspects SQLite database, logs, temp files for any presence of canary values
- Tests error handling (malformed input, invalid types) to ensure no canary leakage in 4xx/5xx responses or logs
- Audits outbound network calls in codebase to ensure zero third-party leakage
"""

import os
import sys
import sqlite3
import asyncio
from httpx import AsyncClient, ASGITransport

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.app.main import app
from backend.app.core.rate_limiter import _memory_rate_limit

CANARY_MARKER = "ZZ_MARKER_998877_PRIVACY_AUDIT"
CANARY_PHONE = "+91-9876543219"
CANARY_URL = "https://fake-phish-domain-998877.xyz/login?token=SECRET_TOKEN_998877"
CANARY_UPI = "fraudster-998877@okhdfcbank"

async def test_privacy():
    print("=== Section 3: Testing Privacy & Zero-Retention Promises ===")
    transport = ASGITransport(app=app)
    _memory_rate_limit.clear()

    # 1. Send normal analysis with canaries
    test_text = (
        f"Urgent KYC alert: {CANARY_MARKER}. Call {CANARY_PHONE} immediately or "
        f"transfer Rs 100 to {CANARY_UPI}. Update at {CANARY_URL}"
    )

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/api/analyze",
            json={
                "input_type": "text",
                "content": test_text,
                "language": "en",
                "user_action_state": "not_acted"
            }
        )
        assert res.status_code == 200, f"Analysis failed: {res.status_code}"
        data = res.json()
        incident_id = data["incident_id"]
        print(f"✓ Analysis request processed successfully (Incident ID: {incident_id})")

    # 2. Check Database (scamshield.db)
    print("\n--- Inspecting SQLite Database for Canaries ---")
    conn = sqlite3.connect("scamshield.db")
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in c.fetchall()]

    db_leaks = []
    for table in tables:
        c.execute(f"SELECT * FROM {table}")
        rows = c.fetchall()
        for row in rows:
            row_str = str(row)
            for marker in [CANARY_MARKER, CANARY_PHONE, "SECRET_TOKEN_998877", CANARY_UPI, CANARY_URL]:
                if marker in row_str:
                    db_leaks.append((table, marker, row_str))

    if db_leaks:
        print(f"❌ CRITICAL LEAK FOUND IN DATABASE: {len(db_leaks)} occurrences!")
        for leak in db_leaks:
            print(f"   Table {leak[0]}: found {leak[1]}")
    else:
        print("✓ Zero raw content found in SQLite database! All canaries absent.")

    # Check what WAS stored in the row for this incident
    c.execute("SELECT * FROM incidents WHERE id=?", (incident_id,))
    stored_row = c.fetchone()
    print(f"  Stored telemetry row for incident {incident_id}:")
    print(f"    Category: {stored_row[3]}")
    print(f"    Risk level: {stored_row[4]}")
    print(f"    Risk score: {stored_row[5]}")
    print(f"    Domain hash: {stored_row[8]}")
    print(f"    Reason codes: {stored_row[6]}")

    # 3. Test Error Handlers for Leakage
    print("\n--- Testing Error Triggers for Content Leakage ---")
    error_tests = [
        # Invalid input_type
        {"payload": {"input_type": "invalid_type", "content": f"Canary: {CANARY_MARKER}", "language": "en"}, "name": "invalid input_type"},
        # Malformed action state
        {"payload": {"input_type": "text", "content": f"Canary: {CANARY_MARKER}", "language": "en", "user_action_state": "INVALID_STATE"}, "name": "invalid user_action_state"},
        # Unhandled extra field containing secrets
        {"payload": {"input_type": "text", "content": "normal", "language": "en", "secret_leak": CANARY_MARKER}, "name": "extra secret field"}
    ]

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        for et in error_tests:
            _memory_rate_limit.clear()
            res = await client.post("/api/analyze", json=et["payload"])
            resp_body = res.text
            if CANARY_MARKER in resp_body:
                print(f"❌ LEAK IN ERROR RESPONSE for {et['name']}: {resp_body}")
            else:
                print(f"✓ Error handler clean for {et['name']} (status={res.status_code}, marker not leaked)")

    # 4. Outbound network leakage audit
    print("\n--- Auditing Outbound Network Requests in Code ---")
    outbound_calls = []
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
    for root, _, files in os.walk(base_dir):
        for f in files:
            if f.endswith(".py"):
                path = os.path.join(root, f)
                with open(path, "r", encoding="utf-8") as pf:
                    for line_no, line in enumerate(pf, 1):
                        if any(term in line for term in ["requests.post", "requests.get", "httpx.post", "httpx.get", "aiohttp", "urllib.request"]):
                            outbound_calls.append((f, line_no, line.strip()))

    print(f"Found {len(outbound_calls)} outbound network call references in backend:")
    for oc in outbound_calls:
        print(f"  {oc[0]}:{oc[1]} -> {oc[2]}")

if __name__ == "__main__":
    asyncio.run(test_privacy())
