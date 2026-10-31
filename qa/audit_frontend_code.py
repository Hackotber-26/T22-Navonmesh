#!/usr/bin/env python3
"""
Section 6: Frontend Static & Architecture Audit
Inspects:
- Touch target sizes (< 48px buttons/links)
- PWA manifest.json and sw.js
- QR Scanner Modal & jsQR integration
- Dead ends, placeholder text, fake data, TODOs
- Navigation links across pages
"""

import os
import re
import json

def audit_frontend():
    print("=== Section 6: Frontend Code & Asset Audit ===")
    fe_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

    # 1. Inspect manifest.json and sw.js
    print("\n--- 1. PWA Manifest & Service Worker ---")
    manifest_path = os.path.join(fe_dir, "public", "manifest.json")
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    print(f"Manifest name: {manifest.get('name')}")
    print(f"Manifest short_name: {manifest.get('short_name')}")
    print(f"Manifest display: {manifest.get('display')}")
    print(f"Manifest icons: {len(manifest.get('icons', []))} icons defined")
    for ic in manifest.get("icons", []):
        icon_path = os.path.join(fe_dir, "public", ic.get("src", "").lstrip("/"))
        exists = os.path.exists(icon_path)
        sz = os.path.getsize(icon_path) if exists else 0
        print(f"  Icon {ic.get('src')}: exists={exists}, size={sz} bytes")

    # Check Web Share Target in manifest.json
    share_target = manifest.get("share_target")
    print(f"Web Share Target defined: {share_target is not None}")
    if share_target:
        print(f"  Action: {share_target.get('action')}, params: {share_target.get('params')}")

    # Check sw.js
    sw_path = os.path.join(fe_dir, "public", "sw.js")
    with open(sw_path, "r", encoding="utf-8") as f:
        sw_content = f.read()
    print(f"Service Worker size: {len(sw_content)} bytes")
    print(f"  Has fetch listener: {'addEventListener(\"fetch\"' in sw_content or 'addEventListener(\'fetch\'' in sw_content}")
    print(f"  Has install listener: {'addEventListener(\"install\"' in sw_content or 'addEventListener(\'install\'' in sw_content}")

    # 2. Touch targets < 48px
    print("\n--- 2. Touch Targets Inspection ---")
    small_targets = []
    button_regex = re.compile(r'<button[^>]*class(?:Name)?=["\']([^"\']+)["\']', re.IGNORECASE)
    for root, _, files in os.walk(os.path.join(fe_dir, "src")):
        for f in files:
            if f.endswith((".tsx", ".jsx")):
                path = os.path.join(root, f)
                with open(path, "r", encoding="utf-8") as pf:
                    content = pf.read()
                    for m in button_regex.finditer(content):
                        cls = m.group(1)
                        # Look for h- or p- that indicates small size (e.g. h-6, h-8, p-1) without min-h-[48px]
                        if any(s in cls for s in ["h-6", "h-7", "h-8", "w-6", "w-7", "w-8", "p-1"]) and "min-h-[48px]" not in cls and "p-3" not in cls and "p-4" not in cls:
                            small_targets.append((f, cls[:60]))

    print(f"Found {len(small_targets)} potentially sub-48px button touch targets:")
    for st in small_targets[:5]:
        print(f"  In {st[0]}: class='{st[1]}'")

    # 3. QR Scanner Modal & Image decoding
    print("\n--- 3. QR Scanner Implementation ---")
    qr_component = os.path.join(fe_dir, "src", "components", "QRScannerModal.tsx")
    with open(qr_component, "r", encoding="utf-8") as f:
        qr_code = f.read()
    print(f"QR Scanner uses jsQR: {'jsqr' in qr_code.lower()}")
    print(f"QR Scanner handles camera access: {'navigator.mediaDevices.getUserMedia' in qr_code}")
    print(f"QR Scanner handles file upload fallback: {'<input type=\"file\"' in qr_code or 'type=\"file\"' in qr_code}")

    # 4. Search for TODO, FIXME, mock, sample, lorem ipsum
    print("\n--- 4. Codebase Placeholders & TODOs Audit ---")
    todos = []
    placeholder_pattern = re.compile(r'\b(TODO|FIXME|XXX|lorem\s*ipsum|mock_data|fake_data)\b', re.IGNORECASE)
    for root, dirs, files in os.walk(fe_dir):
        dirs[:] = [d for d in dirs if d not in ("node_modules", ".next")]
        for f in files:
            if f.endswith((".tsx", ".ts", ".js", ".mjs", ".json", ".css")):
                path = os.path.join(root, f)
                with open(path, "r", encoding="utf-8", errors="ignore") as pf:
                    for lno, line in enumerate(pf, 1):
                        m = placeholder_pattern.search(line)
                        if m:
                            todos.append((f, lno, m.group(0), line.strip()[:70]))

    print(f"Found {len(todos)} placeholder/TODO occurrences:")
    for td in todos:
        print(f"  {td[0]}:{td[1]} [{td[2]}] -> {td[3]}")

if __name__ == "__main__":
    audit_frontend()
