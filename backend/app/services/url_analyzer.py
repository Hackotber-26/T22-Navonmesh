import re
import hashlib
from typing import List, Dict, Any, Tuple, Set, Optional
from urllib.parse import urlparse

# Suspicious TLDs frequently abused in Indian phishing and SMS scams
SUSPICIOUS_TLDS = {
    "xyz", "top", "club", "work", "click", "buzz", "online", "site",
    "icu", "link", "rest", "cam", "live", "tk", "ml", "ga", "cf", "gq",
    "vip", "cc", "monster", "cfd", "sbs", "beauty", "hair", "skin", "quest"
}

# Known URL shorteners
SHORTENERS = {
    "bit.ly", "tinyurl.com", "t.co", "is.gd", "cutt.ly", "rb.gy",
    "shorturl.at", "ow.ly", "goo.gl", "buff.ly", "rebrand.ly", "bl.ink"
}

# Official Allowlisted Domains and TLD suffixes
OFFICIAL_SUFFIXES = [
    ".gov.in",
    ".nic.in",
    ".sbi",
    ".ac.in",
    ".res.in",
    ".mil.in"
]

OFFICIAL_DOMAINS = {
    # Government & Law Enforcement
    "cybercrime.gov.in",
    "sancharsaathi.gov.in",
    "incometax.gov.in",
    "uidai.gov.in",
    "epfindia.gov.in",
    "parivahan.gov.in",
    "indiapost.gov.in",
    "meity.gov.in",
    "rbi.org.in",
    "npci.org.in",

    # Major Indian Banks
    "sbi.co.in",
    "onlinesbi.sbi",
    "hdfcbank.com",
    "icicibank.com",
    "axisbank.com",
    "pnbindia.in",
    "bankofbaroda.in",
    "canarabank.com",
    "kotak.com",
    "indusind.com",
    "idbibank.in",
    "yesbank.in",
    "unionbankofindia.co.in",
    "bankofindia.co.in",
    "centralbankofindia.co.in",
    "punjabandbank.co.in",

    # Payment Platforms & Telecom
    "paytm.com",
    "phonepe.com",
    "bhimupi.org.in",
    "pay.google.com",
    "jio.com",
    "airtel.in",
    "myvi.in",

    # State Utilities
    "bsesdelhi.com",
    "mahadiscom.in",
    "tnebnet.org",
    "uppclonline.com",
    "wbbsdcl.in",
    "bescom.karnataka.gov.in"
}

# Targeted Brands for Lookalike / Typosquatting Analysis
INDIAN_TARGET_BRANDS = [
    "sbi", "onlinesbi", "statebank", "hdfc", "hdfcbank", "icici", "icicibank",
    "axis", "axisbank", "pnb", "pnbindia", "kotak", "canara", "bob", "baroda",
    "paytm", "phonepe", "bhim", "gpay", "googlepay", "uidai", "aadhaar",
    "aadhar", "incometax", "cybercrime", "sancharsaathi", "indiapost", "postinfo",
    "electricity", "bijli", "mahadiscom", "bses", "uppcl"
]

# URL extraction regex supporting http/https and naked domains/IPs
URL_REGEX = re.compile(
    r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,12}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))\)|[^\s`!()\[\]{};:\'\".,<>?«»“”‘’]))',
    re.IGNORECASE
)

# Naked domain pattern (e.g. "sbi-kyc-update.xyz" or "192.168.1.1:8080")
NAKED_DOMAIN_REGEX = re.compile(
    r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+(?:[a-zA-Z]{2,12})\b',
    re.IGNORECASE
)


def levenshtein_distance(s1: str, s2: str) -> int:
    """Compute standard Levenshtein edit distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


class URLAnalyzer:
    """Lexical and reputation analysis for URLs and domain names in Indian context."""

    def __init__(self):
        # Known threat blocklist (URLhaus, OpenPhish feeds)
        self.blocklist_domains: Set[str] = set()
        self.blocklist_hashes: Set[str] = set()
        self._load_default_threat_signatures()

    def _load_default_threat_signatures(self):
        """Seed initial high-risk phishing signatures and load threat_feeds.json if present."""
        import os, json
        data_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/threat_feeds.json"))
        if os.path.exists(data_file):
            try:
                with open(data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for dom in data.get("domains", []):
                        self.blocklist_domains.add(dom.lower())
                    for h in data.get("hashes", []):
                        self.blocklist_hashes.add(h)
            except Exception:
                pass

        sample_malicious = [
            "sbi-kyc-update.xyz",
            "hdfc-netbanking-login.top",
            "icici-reward-points.club",
            "electricity-bill-disconnection.site",
            "paytm-kyc-verification.online",
            "phonepe-cashback-gift.top",
            "indiaofficialpost-track.xyz",
            "bses-powerbill-pay.click"
        ]
        for dom in sample_malicious:
            self.blocklist_domains.add(dom.lower())
            self.blocklist_hashes.add(hashlib.sha256(dom.lower().encode("utf-8")).hexdigest())

    def extract_urls(self, text: str) -> List[str]:
        """Extract URLs and raw domain references from text."""
        matches = []
        for match in URL_REGEX.finditer(text):
            url_str = match.group(0).strip()
            # Clean trailing punctuation
            url_str = re.sub(r'[\'\".,;!?)]+$', '', url_str)
            if url_str not in matches:
                matches.append(url_str)

        # Fallback to naked domain extraction if no standard protocol matches found
        if not matches:
            for match in NAKED_DOMAIN_REGEX.finditer(text):
                dom_str = match.group(0).strip().lower()
                # Exclude common false positives like file extensions or version strings
                if "." in dom_str and not dom_str.endswith((".png", ".jpg", ".pdf", ".txt", ".json")):
                    if dom_str not in matches:
                        matches.append(dom_str)

        return matches

    def extract_domain(self, url: str) -> str:
        """Sanitize and extract the registered hostname/domain from a URL."""
        url_to_parse = url if "://" in url else f"http://{url}"
        try:
            parsed = urlparse(url_to_parse)
            host = parsed.netloc or parsed.path.split('/')[0]
            # Strip port and username/password if present
            host = host.split('@')[-1].split(':')[0].strip().lower()
            # Strip leading 'www.'
            if host.startswith("www."):
                host = host[4:]
            return host
        except Exception:
            return url.strip().lower()

    def compute_domain_hash(self, domain: str) -> str:
        """Generate SHA-256 hash of domain name for DPDP-compliant telemetry."""
        return hashlib.sha256(domain.strip().lower().encode("utf-8")).hexdigest()

    def is_official_allowlist(self, domain: str) -> bool:
        """Check if domain is officially registered to Indian government or banks."""
        d = domain.lower()
        if d in OFFICIAL_DOMAINS:
            return True
        for suffix in OFFICIAL_SUFFIXES:
            if d.endswith(suffix):
                return True
        return False

    def is_known_blocklist(self, domain: str) -> bool:
        """Check if domain is present in threat feeds or blocklist."""
        d = domain.lower()
        if d in self.blocklist_domains:
            return True
        h = self.compute_domain_hash(d)
        if h in self.blocklist_hashes:
            return True
        return False

    def analyze_domain(self, domain: str) -> Dict[str, Any]:
        """Perform deep lexical heuristics and brand impersonation detection on a domain."""
        reasons: List[str] = []
        score: float = 0.0
        dom = domain.lower().strip()

        # 1. Allowlist check: If verified official domain, zero risk
        if self.is_official_allowlist(dom):
            return {
                "domain": dom,
                "domain_hash": self.compute_domain_hash(dom),
                "is_allowlisted": True,
                "is_blocklisted": False,
                "score": 0.0,
                "reasons": []
            }

        # 2. Blocklist / Threat Feed match
        is_blocklisted = self.is_known_blocklist(dom)
        if is_blocklisted:
            reasons.append("KNOWN_PHISHING_FEED_MATCH")
            score = max(score, 0.95)

        # 3. Shortener check
        if dom in SHORTENERS:
            reasons.append("SHORTENED_URL")
            score = max(score, 0.65)

        # 4. TLD check
        parts = dom.split(".")
        tld = parts[-1] if len(parts) > 1 else ""
        if tld in SUSPICIOUS_TLDS:
            reasons.append("SUSPICIOUS_TLD")
            score = max(score, 0.68)

        # 5. IP Address or Punycode in host
        if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', dom):
            reasons.append("EXCESSIVE_PUNYCODE_OR_DIGITS")
            score = max(score, 0.70)
        elif dom.startswith("xn--"):
            reasons.append("EXCESSIVE_PUNYCODE_OR_DIGITS")
            score = max(score, 0.65)

        # 6. Hyphen and digit abuse (e.g. sbi-kyc-update-portal-2026.xyz)
        hyphen_count = dom.count("-")
        digit_count = sum(c.isdigit() for c in dom)
        if hyphen_count >= 2 or (hyphen_count >= 1 and digit_count >= 3):
            score = max(score, 0.50)

        # 7. Brand lookalike & typosquatting detection
        # Strip TLD and check core domain name
        core_name = ".".join(parts[:-1]) if len(parts) > 1 else dom
        tokens = re.split(r'[-._]', core_name)

        is_lookalike = False
        is_fake_bank = False

        for brand in INDIAN_TARGET_BRANDS:
            # Case A: Brand embedded with suspicious prefix/suffix (e.g. "sbi-kyc", "hdfc-alert", "paytm-cash")
            if brand in tokens or brand in core_name:
                # Brand is present in unverified domain
                is_lookalike = True
                if brand in {"sbi", "onlinesbi", "statebank", "hdfc", "hdfcbank", "icici", "axis", "pnb", "kotak", "canara"}:
                    is_fake_bank = True
                break

            # Case B: Typosquatting via Levenshtein distance on tokens
            for token in tokens:
                if len(token) >= 4 and len(brand) >= 4:
                    dist = levenshtein_distance(token, brand)
                    if dist == 1:  # Exactly one character typo (e.g. hdfcbamk, icicbank, paytmm)
                        is_lookalike = True
                        if brand in {"sbi", "hdfc", "icici", "axis", "pnb", "kotak"}:
                            is_fake_bank = True
                        break
            if is_lookalike:
                break

        if is_fake_bank:
            reasons.append("FAKE_BANK_DOMAIN")
            reasons.append("LOOKALIKE_DOMAIN")
            score = max(score, 0.88)
        elif is_lookalike:
            reasons.append("LOOKALIKE_DOMAIN")
            score = max(score, 0.75)

        # Cap score between 0.0 and 1.0
        score = min(1.0, max(0.0, score))

        return {
            "domain": dom,
            "domain_hash": self.compute_domain_hash(dom),
            "is_allowlisted": False,
            "is_blocklisted": is_blocklisted,
            "score": round(score, 2),
            "reasons": reasons
        }

    def analyze_text_for_urls(self, text: str) -> Dict[str, Any]:
        """Extract and analyze all URLs found in the text."""
        extracted = self.extract_urls(text)
        if not extracted:
            return {
                "has_urls": False,
                "urls": [],
                "domains": [],
                "primary_domain_hash": None,
                "max_url_score": 0.0,
                "reasons": []
            }

        domain_results = []
        domains_list = []
        max_score = 0.0
        all_reasons = []

        for item in extracted:
            dom = self.extract_domain(item)
            if dom and dom not in domains_list:
                domains_list.append(dom)
                analysis = self.analyze_domain(dom)

                # Check entire URL path/query for phishing or target brand keywords
                if not analysis["is_allowlisted"]:
                    item_lower = item.lower()
                    # Check for bank brand mentions anywhere in the URL (e.g. tinyurl.com/sbi-verify)
                    bank_brands = {"sbi", "onlinesbi", "statebank", "hdfc", "hdfcbank", "icici", "axis", "pnb", "kotak", "canara"}
                    phishing_keywords = {
                        "kyc", "pan", "aadhaar", "aadhar", "block", "unblock", "verify",
                        "verification", "cashback", "reward", "rewards", "prize", "gift",
                        "lottery", "claim", "free", "bonus", "refund", "cutoff", "electricity",
                        "bijli", "bill", "payme", "quickpay"
                    }

                    has_bank = any(b in item_lower for b in bank_brands)
                    has_phish = any(p in item_lower for p in phishing_keywords)

                    if has_bank:
                        if "FAKE_BANK_DOMAIN" not in analysis["reasons"]:
                            analysis["reasons"].append("FAKE_BANK_DOMAIN")
                        if "LOOKALIKE_DOMAIN" not in analysis["reasons"]:
                            analysis["reasons"].append("LOOKALIKE_DOMAIN")
                        analysis["score"] = max(analysis["score"], 0.88)
                    elif has_phish:
                        if "LOOKALIKE_DOMAIN" not in analysis["reasons"]:
                            analysis["reasons"].append("LOOKALIKE_DOMAIN")
                        analysis["score"] = max(analysis["score"], 0.75)

                domain_results.append(analysis)
                if analysis["score"] > max_score:
                    max_score = analysis["score"]
                for r in analysis["reasons"]:
                    if r not in all_reasons:
                        all_reasons.append(r)

        primary_hash = domain_results[0]["domain_hash"] if domain_results else None

        return {
            "has_urls": True,
            "urls": extracted,
            "domains": domains_list,
            "primary_domain_hash": primary_hash,
            "max_url_score": max_score,
            "reasons": all_reasons,
            "domain_results": domain_results
        }


url_analyzer = URLAnalyzer()

