#!/usr/bin/env python3
"""
Threat Feed Synchronization Script for ScamShield India.
Pulls open threat feeds from URLhaus (abuse.ch, CC0 1.0) and OpenPhish community feed.
Parses active domains, computes SHA-256 domain hashes, and writes backend/app/data/threat_feeds.json.
"""

import os
import re
import json
import hashlib
import urllib.request
from datetime import datetime, timezone
from typing import Set, Dict, Any
from urllib.parse import urlparse

URLHAUS_ONLINE_URL = "https://urlhaus.abuse.ch/downloads/text_online/"
OPENPHISH_COMMUNITY_URL = "https://openphish.com/feed.txt"


def extract_domain(url: str) -> str:
    url_to_parse = url if "://" in url else f"http://{url}"
    try:
        parsed = urlparse(url_to_parse)
        host = parsed.netloc or parsed.path.split('/')[0]
        host = host.split('@')[-1].split(':')[0].strip().lower()
        if host.startswith("www."):
            host = host[4:]
        return host
    except Exception:
        return url.strip().lower()


def fetch_urlhaus_domains() -> Set[str]:
    print("Fetching URLhaus active malicious URL feed (CC0)...")
    domains = set()
    try:
        req = urllib.request.Request(
            URLHAUS_ONLINE_URL,
            headers={"User-Agent": "ScamShield-India-ThreatIntelligence/1.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            lines = response.read().decode("utf-8", errors="ignore").splitlines()
            for line in lines:
                line = line.strip()
                if line and not line.startswith("#"):
                    dom = extract_domain(line)
                    if dom and "." in dom:
                        domains.add(dom)
        print(f"  ✓ URLhaus: fetched {len(domains)} unique threat domains.")
    except Exception as e:
        print(f"  Warning: Could not fetch URLhaus feed: {e}. Using cached/seed indicators.")
    return domains


def fetch_openphish_domains() -> Set[str]:
    print("Fetching OpenPhish community feed...")
    domains = set()
    try:
        req = urllib.request.Request(
            OPENPHISH_COMMUNITY_URL,
            headers={"User-Agent": "ScamShield-India-ThreatIntelligence/1.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            lines = response.read().decode("utf-8", errors="ignore").splitlines()
            for line in lines:
                line = line.strip()
                if line and not line.startswith("#"):
                    dom = extract_domain(line)
                    if dom and "." in dom:
                        domains.add(dom)
        print(f"  ✓ OpenPhish: fetched {len(domains)} unique threat domains.")
    except Exception as e:
        print(f"  Warning: Could not fetch OpenPhish feed: {e}. Using cached/seed indicators.")
    return domains


def refresh_threat_feeds():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    data_dir = os.path.join(base_dir, "backend", "app", "data")
    os.makedirs(data_dir, exist_ok=True)
    out_file = os.path.join(data_dir, "threat_feeds.json")

    print("=== ScamShield India: Threat Feed Refresh ===")

    all_domains = set([
        # Core Indian banking and KYC phishing honeypots
        "sbi-kyc-update.xyz",
        "hdfc-netbanking-login.top",
        "icici-reward-points.club",
        "electricity-bill-disconnection.site",
        "paytm-kyc-verification.online",
        "phonepe-cashback-gift.top",
        "indiaofficialpost-track.xyz",
        "bses-powerbill-pay.click",
        "sbicard-points-redeem.link",
        "pnb-kyc-portal.top",
        "axis-netbanking-alert.xyz"
    ])

    # Fetch live open feeds
    urlhaus_doms = fetch_urlhaus_domains()
    openphish_doms = fetch_openphish_domains()
    all_domains.update(urlhaus_doms)
    all_domains.update(openphish_doms)

    domain_list = sorted(list(all_domains))
    hash_list = [hashlib.sha256(d.encode("utf-8")).hexdigest() for d in domain_list]

    feed_payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total_domains": len(domain_list),
        "sources": ["URLhaus (abuse.ch CC0)", "OpenPhish Community", "ScamShield Honeypot Signatures"],
        "domains": domain_list,
        "hashes": hash_list
    }

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(feed_payload, f, indent=2)

    print(f"\n✓ Threat feeds updated successfully: {len(domain_list)} domains written to {out_file}")


if __name__ == "__main__":
    refresh_threat_feeds()

