#!/usr/bin/env python3
"""
verify_live_http_assets.py
Programmatic Live HTTP Asset Verification on GitHub Pages Deployment.

Target: https://rajaqwe.github.io/sterling-primeB-website/
Validates that:
1. Core website assets (index.html, catalog_data.js, scripts/app.js) return HTTP 200.
2. Product image URLs from products.json resolve to HTTP 200 on live GitHub Pages.
"""

import sys
import os
import json
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

LIVE_BASE_URL = "https://rajaqwe.github.io/sterling-primeB-website/"
REPO_ROOT = Path(__file__).parent.parent
PRODUCTS_JSON = REPO_ROOT / "products.json"


def check_url(url: str, timeout: int = 15, retries: int = 3):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) SterlingPrimeVerifier/1.0"
    }
    req = urllib.request.Request(url, headers=headers, method="HEAD")
    last_err = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return url, resp.status, None
        except urllib.error.HTTPError as e:
            if e.code == 405:  # Method Not Allowed for HEAD, fallback to GET
                try:
                    get_req = urllib.request.Request(url, headers=headers, method="GET")
                    with urllib.request.urlopen(get_req, timeout=timeout) as g_resp:
                        return url, g_resp.status, None
                except Exception as g_err:
                    last_err = g_err
            else:
                last_err = e
        except Exception as e:
            last_err = e
        if attempt < retries - 1:
            time.sleep(1.5)
    
    code = getattr(last_err, "code", 0) if hasattr(last_err, "code") else 0
    return url, code, str(last_err)


def main():
    print("=" * 65)
    print("Programmatic Live GitHub Pages Asset Verification")
    print("=" * 65)
    print(f"Target Base URL: {LIVE_BASE_URL}")

    # 1. Verify Core Site Assets
    core_assets = [
        "",
        "catalog_data.js",
        "scripts/app.js",
    ]
    print("\n[1/3] Verifying Core Application Assets...")
    core_failures = 0
    for rel in core_assets:
        target = LIVE_BASE_URL + rel
        url, status, err = check_url(target)
        if status == 200:
            print(f"  [PASS] HTTP 200: {target}")
        else:
            print(f"  [FAIL] HTTP {status}: {target} -> {err}")
            core_failures += 1

    # 2. Load products.json
    print("\n[2/3] Loading Product Dataset from products.json...")
    if not PRODUCTS_JSON.exists():
        print(f"ERROR: {PRODUCTS_JSON} does not exist.")
        return 1

    with open(PRODUCTS_JSON, "r", encoding="utf-8") as f:
        products = json.load(f)
    print(f"  Loaded {len(products):,} active products.")

    # Collect unique image URLs
    image_urls = []
    seen = set()
    for p in products:
        img = p.get("image") or p.get("image_path") or ""
        if img and img not in seen:
            seen.add(img)
            # Ensure relative URL formatting
            clean_url = img.replace("\\", "/")
            full_live_url = LIVE_BASE_URL + clean_url
            image_urls.append(full_live_url)

    print(f"  Identified {len(image_urls):,} unique product image URLs.")

    # 3. Concurrently Verify Product Image URLs
    # If '--all' is in sys.argv, test all; otherwise test a representative sample of 250 items
    test_all = "--all" in sys.argv
    sample_urls = image_urls if test_all else image_urls[:250]
    print(f"\n[3/3] Concurrently Checking {len(sample_urls):,} Product Image URLs (threads=20)...")

    passes = 0
    fails = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(check_url, u): u for u in sample_urls}
        for future in as_completed(futures):
            url, status, err = future.result()
            if status == 200:
                passes += 1
            else:
                fails.append((url, status, err))

    print(f"\nResults for Product Images:")
    print(f"  Total Checked : {len(sample_urls):,}")
    print(f"  Passed (200)  : {passes:,} ({passes/len(sample_urls)*100:.1f}%)")
    print(f"  Failed        : {len(fails)}")

    if fails:
        print("\nSample Failures:")
        for url, status, err in fails[:10]:
            print(f"  [FAIL] HTTP {status}: {url} -> {err}")

    print("\n" + "=" * 65)
    total_violations = core_failures + len(fails)
    if total_violations == 0:
        print(f"VERIFICATION RESULT: 100% PASS - All {len(sample_urls):,} tested live URLs returned HTTP 200!")
        print("=" * 65)
        return 0
    else:
        print(f"VERIFICATION RESULT: FAILED - {total_violations} asset URLs failed HTTP 200 check.")
        print("=" * 65)
        return 1


if __name__ == "__main__":
    sys.exit(main())
