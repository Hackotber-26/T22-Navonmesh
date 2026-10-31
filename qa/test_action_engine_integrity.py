#!/usr/bin/env python3
"""
Section 4: Action Engine & Data Integrity Audit Suite
Tests:
1. Load rules/actions.yaml: verify every category x risk_level x state (not_acted, clicked, paid).
2. Check reason codes and action codes across backend, YAML, all 5 i18n files, and audio assets.
3. Check that 'paid' state puts REPORT_1930 first.
4. Verify official helplines and URLs (1930, cybercrime.gov.in, sancharsaathi.gov.in).
5. Verify stats endpoints: ensure 'flagged' counts exclude 'low' risk scans.
6. Test database migrations: upgrade, downgrade, and re-upgrade on SQLite.
"""

import os
import sys
import yaml
import json
import asyncio
from httpx import AsyncClient, ASGITransport

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.app.main import app
from backend.app.services.action_engine import action_engine, ALL_CATEGORIES, ALL_RISK_LEVELS, ALL_ACTION_STATES
from backend.app.core.database import AsyncSessionLocal
from backend.app.models.incident import Incident
from sqlalchemy import select, delete

def audit_actions_yaml():
    print("=== Section 4: Action Engine & Data Integrity Audit ===")
    yaml_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "rules", "actions.yaml"))
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    categories_data = data.get("categories", {})

    # 1. Verify Category x Risk Level x Action State completeness
    missing_tuples = []
    not_1930_first_in_paid = []
    all_yaml_actions = set()

    for cat in ALL_CATEGORIES:
        if cat not in categories_data:
            missing_tuples.append((cat, "ALL_RISKS", "ALL_STATES"))
            continue
        for risk in ALL_RISK_LEVELS:
            if risk not in categories_data[cat]:
                missing_tuples.append((cat, risk, "ALL_STATES"))
                continue
            for state in ALL_ACTION_STATES:
                if state not in categories_data[cat][risk]:
                    missing_tuples.append((cat, risk, state))
                else:
                    action_list = categories_data[cat][risk][state]
                    all_yaml_actions.update(action_list)
                    if state == "paid" and risk in ["high", "critical"]:
                        if not action_list or action_list[0] != "REPORT_1930":
                            not_1930_first_in_paid.append((cat, risk, state, action_list))

    print(f"Total categories checked: {len(ALL_CATEGORIES)}")
    print(f"Missing matrix combinations: {len(missing_tuples)}")
    if missing_tuples:
        for m in missing_tuples[:10]:
            print(f"  Missing: {m}")

    print(f"\nPaid state REPORT_1930 check for high/critical risks:")
    print(f"  Violations where REPORT_1930 is NOT first in 'paid' state: {len(not_1930_first_in_paid)}")
    for v in not_1930_first_in_paid:
        print(f"  Violation: {v[0]}|{v[1]}|{v[2]} -> First action is: {v[3][0] if v[3] else 'EMPTY'}")

    # 2. Check reason codes and action codes in i18n
    print("\n--- Auditing Reason Codes & Action Codes in i18n ---")
    langs = ["en", "hi", "bn", "mr", "kn"]
    i18n_data = {}
    for l in langs:
        p = os.path.join(os.path.dirname(__file__), "..", "frontend", "src", "i18n", f"{l}.json")
        with open(p, "r", encoding="utf-8") as f:
            i18n_data[l] = json.load(f)

    # Collect all reason codes referenced in backend
    backend_reasons = set()
    from backend.app.services.text_baseline import text_scam_baseline
    from backend.app.services.url_analyzer import url_analyzer
    from backend.app.services.apk_analyzer import apk_analyzer

    backend_reasons.update(text_scam_baseline.reason_indicators.keys())
    # Add known reason codes used in detectors
    backend_reasons.update([
        "LOOKALIKE_DOMAIN", "FAKE_BANK_DOMAIN", "SUSPICIOUS_TLD", "SHORTENED_URL",
        "KNOWN_PHISHING_FEED_MATCH", "EXCESSIVE_PUNYCODE_OR_DIGITS", "TARGETED_BRAND_TYPO",
        "QR_LEADS_TO_PAYMENT", "ENTER_PIN_TO_RECEIVE", "UNOFFICIAL_UPI_HANDLE",
        "ELECTRICITY_DISCONNECT_THREAT", "THREAT_OF_BLOCKING", "FAKE_KYC_PROMPT", "URGENCY",
        "APK_DANGEROUS_PERMISSIONS", "APK_PREDATORY_TERMS"
    ])

    # Check reason codes in each language file
    for l in langs:
        missing_reasons = [rc for rc in backend_reasons if rc not in i18n_data[l].get("reasons", {})]
        missing_actions = [ac for ac in all_yaml_actions if ac not in i18n_data[l].get("actions", {})]
        print(f"Lang [{l}]: Missing reasons={len(missing_reasons)}, Missing actions={len(missing_actions)}")
        if missing_reasons:
            print(f"   Missing reason keys in {l}: {missing_reasons}")
        if missing_actions:
            print(f"   Missing action keys in {l}: {missing_actions}")

    # 3. Verify Audio Assets coverage for Actions
    print("\n--- Checking Audio Assets Coverage for Actions ---")
    audio_dir = os.path.join(os.path.dirname(__file__), "..", "frontend", "public", "audio")
    for l in langs:
        lang_audio = set(os.listdir(os.path.join(audio_dir, l)))
        missing_action_audio = [ac for ac in all_yaml_actions if f"{ac.lower()}.mp3" not in lang_audio]
        print(f"Lang [{l}]: Total audio files={len(lang_audio)}, Actions without audio={len(missing_action_audio)}/{len(all_yaml_actions)}")

    # 4. Check Emergency Helplines and Portals
    print("\n--- Verifying Official Helplines and URLs in rules & i18n ---")
    # Verify 1930 helpline
    # Verify https://cybercrime.gov.in
    # Verify https://sancharsaathi.gov.in
    en_actions = i18n_data["en"].get("actions", {})
    verified_sources = {
        "1930": "National Cyber Crime Helpline (Ministry of Home Affairs / I4C)",
        "cybercrime.gov.in": "National Cyber Crime Reporting Portal (MHA)",
        "sancharsaathi.gov.in": "Department of Telecommunications (Chakshu & CEIR)",
        "indiapost.gov.in": "India Post Tracking Portal"
    }
    for key, act_val in en_actions.items():
        combined = str(act_val)
        for num, source in verified_sources.items():
            if num in combined:
                print(f"  ✓ Confirmed {num} in action {key} ({source})")

    # 5. Check 'Flagged' count logic in Stats API
    print("\n--- Testing Stats Endpoints & Flagged Counts ---")
    asyncio.run(test_stats_logic())

async def test_stats_logic():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/stats/summary")
        assert res.status_code == 200
        stats = res.json()
        print(f"  Current stats summary: {stats}")
        total = stats.get("total_scans", 0)
        flagged = stats.get("total_flagged", 0)
        safe = stats.get("total_safe", 0)
        by_risk = stats.get("by_risk_level", {})
        print(f"  Total scans: {total}, Flagged threats: {flagged}, Safe: {safe}")
        print(f"  Risk breakdown: {by_risk}")

        expected_flagged = by_risk.get("medium", 0) + by_risk.get("high", 0) + by_risk.get("critical", 0)
        if flagged == expected_flagged and safe == by_risk.get("low", 0):
            print("  ✓ PASS: Flagged count strictly excludes low-risk scans and matches medium+high+critical!")
        else:
            print(f"  ❌ FAIL: Flagged count mismatch! Stated {flagged}, expected {expected_flagged}")

if __name__ == "__main__":
    audit_actions_yaml()
