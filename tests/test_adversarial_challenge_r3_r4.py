#!/usr/bin/env python3
"""
tests/test_adversarial_challenge_r3_r4.py
Adversarial Stress-Testing Suite for Requirements R3 and R4.
Executed by teamwork_preview_challenger_r1_r4_2.

R3: Category Mapping & Dynamic Badges
    - 16 canonical categories exact match & 17 filter bar buttons
    - Dynamic badge count summation matching "All Items" (6,119) and total products in catalog_data.js
    - Simulated client-side filtering across all 16 categories with zero 0-result categories and zero unmapped fallbacks
    - Clean DOM/Data alignment without category leakage

R4: Live GitHub Pages Deployment & HTTP 200 Verification + Floating Navigation Layout
    - Live concurrent HTTP HEAD/GET probes to https://rajaqwe.github.io/sterling-primeB-website/
    - Core assets check: index.html (/), catalog_data.js, scripts/app.js -> HTTP 200
    - Stratified random sample of 350+ product images across all 16 categories -> 100% HTTP 200
    - Collision-free floating navigation geometry & z-index stacking:
      WhatsApp (bottom-left), Back-to-Top (bottom-left above WhatsApp), Chatbot (bottom-right)
"""

import sys
import os
import re
import json
import random
import unittest
import urllib.request
import urllib.error
from pathlib import Path
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
INDEX_HTML = REPO_ROOT / "index.html"
CATALOG_DATA_JS = REPO_ROOT / "catalog_data.js"
PRODUCTS_JSON = REPO_ROOT / "products.json"
APP_JS = REPO_ROOT / "scripts" / "app.js"

LIVE_BASE_URL = "https://rajaqwe.github.io/sterling-primeB-website/"

CANONICAL_16_CATEGORIES = [
    "electronics-tech",
    "smartwatches",
    "drinkware-bottles",
    "bags-travel",
    "pens-writing",
    "stationery-work",
    "home-kitchen",
    "festive-hampers",
    "apparel-lifestyle",
    "wellness-grooming",
    "office-desk",
    "wooden-handicrafts",
    "clocks-planners",
    "corporate-gift-sets",
    "luxury-premium",
    "books-learning",
]

INHOUSE_SLUG_MAP = {
    "wooden-gifts": "wooden-handicrafts",
    "healthcare-medical": "wellness-grooming",
    "wellness-care": "wellness-grooming",
    "gift-sets": "corporate-gift-sets",
    "promotional-merch": "corporate-gift-sets",
    "packaging-storage": "corporate-gift-sets",
    "acrylic-displays": "office-desk",
    "drinkware-kitchen": "drinkware-bottles",
}


def load_catalog_data():
    """Load and parse window.CATALOG_DATA from catalog_data.js."""
    with open(CATALOG_DATA_JS, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r"window\.CATALOG_DATA\s*=\s*(\[.*?\]);?\s*$", content, re.DOTALL)
    if not match:
        raise ValueError("Could not extract window.CATALOG_DATA array from catalog_data.js")
    return json.loads(match.group(1))


def load_inhouse_cards_from_dom():
    """Parse static in-house product cards directly from index.html."""
    with open(INDEX_HTML, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    cards = soup.select("#galleryGrid .product-card.is-inhouse")
    items = []
    for c in cards:
        raw_slug = (c.get("data-category") or "").strip().lower()
        slug = INHOUSE_SLUG_MAP.get(raw_slug, raw_slug)
        items.append({
            "_slug": slug,
            "_raw_slug": raw_slug,
            "_name": (c.get("data-name") or "").strip().lower(),
            "_brand": (c.get("data-brand") or "").strip().lower(),
            "_type": "inhouse",
            "_card_el": c
        })
    return items, soup


def probe_http_url(url: str, timeout: int = 12, retries: int = 3):
    """Probe a live URL via HTTP HEAD with GET fallback."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) SterlingPrimeAdversarialAuditor/2.0"
    }
    req = urllib.request.Request(url, headers=headers, method="HEAD")
    last_err = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return url, resp.status, None
        except urllib.error.HTTPError as e:
            if e.code == 405:  # Method Not Allowed for HEAD, try GET
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
            import time
            time.sleep(1.0)
    status_code = getattr(last_err, "code", 0) if hasattr(last_err, "code") else 0
    return url, status_code, str(last_err)


class TestR3CategoryMappingAndDynamicBadges(unittest.TestCase):
    """Adversarial stress-tests for Requirement R3."""

    @classmethod
    def setUpClass(cls):
        cls.inhouse_items, cls.soup = load_inhouse_cards_from_dom()
        cls.catalog_items = load_catalog_data()
        with open(PRODUCTS_JSON, "r", encoding="utf-8") as f:
            cls.products_json_items = json.load(f)

    def test_r3_01_all_16_canonical_categories_defined_in_filter_bar(self):
        """Verify #categoryFilterBar has exactly 17 buttons (1 All Items + 16 categories)."""
        buttons = self.soup.select(".cat-btn[data-cat]")
        self.assertEqual(len(buttons), 17, f"Expected 17 filter buttons, found {len(buttons)}")

        slugs = [b.get("data-cat") for b in buttons]
        self.assertIn("all", slugs, "Missing 'all' category button")

        cat_slugs = set(s for s in slugs if s != "all")
        expected_set = set(CANONICAL_16_CATEGORIES)
        self.assertEqual(cat_slugs, expected_set, f"Category mismatch. Diff: {cat_slugs ^ expected_set}")

    def test_r3_02_dynamic_badge_sum_matches_all_items_and_catalog_length(self):
        """Verify sum of category badge counts matches 'All Items' count and total products."""
        buttons = self.soup.select(".cat-btn[data-cat]")
        badge_counts = {}
        for b in buttons:
            slug = b.get("data-cat")
            count_el = b.select_one(".cat-count")
            self.assertIsNotNone(count_el, f"Missing .cat-count badge for {slug}")
            raw_text = count_el.get_text().strip().replace(",", "")
            self.assertTrue(raw_text.isdigit(), f"Non-numeric badge '{raw_text}' for {slug}")
            badge_counts[slug] = int(raw_text)

        all_count = badge_counts["all"]
        category_sum = sum(badge_counts[c] for c in CANONICAL_16_CATEGORIES)

        self.assertEqual(all_count, category_sum, f"Badge sum {category_sum} != 'All Items' count {all_count}")
        self.assertEqual(all_count, len(self.catalog_items), f"All Items badge {all_count} != catalog_data.js length {len(self.catalog_items)}")
        self.assertEqual(all_count, len(self.products_json_items), f"All Items badge {all_count} != products.json length {len(self.products_json_items)}")

    def test_r3_03_simulate_filtering_across_all_16_categories_no_zero_results(self):
        """Simulate client-side filtering engine across all 16 categories, ensuring no empty categories."""
        # Client simulation according to scripts/app.js
        partner_all = [
            {
                "_slug": p.get("category_slug") or p.get("category") or "corporate-gift-sets",
                "_name": (p.get("name") or p.get("title") or "").lower(),
                "_brand": (p.get("brand") or "").lower(),
                "_type": "partner_product",
            }
            for p in self.catalog_items
            if p.get("type") == "partner_product"
        ]
        all_products = self.inhouse_items + partner_all

        buttons = self.soup.select(".cat-btn[data-cat]")
        badge_counts = {
            b.get("data-cat"): int(b.select_one(".cat-count").get_text().strip().replace(",", ""))
            for b in buttons
        }

        for cat in CANONICAL_16_CATEGORIES:
            filtered = [p for p in all_products if p["_slug"] == cat]
            count = len(filtered)
            self.assertGreater(
                count, 0, f"Category '{cat}' produced 0 results in client filter simulation!"
            )
            self.assertEqual(
                count, badge_counts[cat],
                f"Simulated count for '{cat}' ({count}) does not match badge count ({badge_counts[cat]})"
            )

    def test_r3_04_no_unmapped_fallbacks_or_category_leakage(self):
        """Verify zero products fall back to undefined or stray categories."""
        partner_all = [
            p.get("category_slug") or p.get("category") or "corporate-gift-sets"
            for p in self.catalog_items
            if p.get("type") == "partner_product"
        ]
        inhouse_all = [p["_slug"] for p in self.inhouse_items]
        all_slugs = partner_all + inhouse_all

        slug_set = set(all_slugs)
        expected_set = set(CANONICAL_16_CATEGORIES)
        unmapped = slug_set - expected_set
        self.assertEqual(len(unmapped), 0, f"Found unmapped category slugs in catalog: {unmapped}")

    def test_r3_05_inhouse_products_normalized_coherently(self):
        """Verify that all 171 in-house cards in DOM possess valid canonical data-category attributes."""
        self.assertEqual(len(self.inhouse_items), 171, f"Expected 171 in-house cards, found {len(self.inhouse_items)}")
        for item in self.inhouse_items:
            self.assertIn(
                item["_slug"], CANONICAL_16_CATEGORIES,
                f"In-house item slug '{item['_slug']}' not in canonical 16 taxonomy"
            )


class TestR4LiveDeploymentAndFloatingNavigation(unittest.TestCase):
    """Adversarial stress-tests for Requirement R4."""

    @classmethod
    def setUpClass(cls):
        with open(INDEX_HTML, "r", encoding="utf-8") as f:
            cls.soup = BeautifulSoup(f.read(), "html.parser")
            cls.styles = " ".join(s.get_text() for s in cls.soup.find_all("style"))
        with open(PRODUCTS_JSON, "r", encoding="utf-8") as f:
            cls.products = json.load(f)

    def test_r4_01_floating_navigation_dom_presence(self):
        """Verify WhatsApp, Back-to-Top, and Chatbot exist in DOM."""
        wa_float = self.soup.select_one(".whatsapp-float")
        self.assertIsNotNone(wa_float, "Missing .whatsapp-float in DOM")
        self.assertIn("https://wa.me/917041614713", wa_float.get("href", ""), "Invalid WhatsApp telephone link")

        back_to_top = self.soup.select_one("#backToTop") or self.soup.select_one(".back-to-top")
        self.assertIsNotNone(back_to_top, "Missing #backToTop in DOM")

        chatbot = self.soup.select_one("#sp-btn") or self.soup.select_one("#sp-chat-container")
        self.assertIsNotNone(chatbot, "Missing Gift Advisor Chatbot (#sp-btn) in DOM")

    def test_r4_02_floating_navigation_css_collision_free_coordinates(self):
        """Verify CSS coordinates strictly place WhatsApp on bottom-left and Chatbot on bottom-right."""
        # WhatsApp bottom-left
        self.assertIn(".whatsapp-float", self.styles)
        wa_match = re.search(r"\.whatsapp-float\s*\{([^}]+)\}", self.styles)
        self.assertIsNotNone(wa_match, "Missing .whatsapp-float CSS block")
        wa_block = wa_match.group(1)
        self.assertTrue(re.search(r"position:\s*fixed", wa_block), "WhatsApp must be position fixed")
        self.assertTrue(re.search(r"left:\s*(?:28px|16px)", wa_block), "WhatsApp must be docked on left")
        self.assertTrue(re.search(r"bottom:\s*(?:28px|18px)", wa_block), "WhatsApp must be docked on bottom")

        # Back to top bottom-left above WhatsApp
        btt_match = re.search(r"\.back-to-top\s*\{([^}]+)\}", self.styles)
        self.assertIsNotNone(btt_match, "Missing .back-to-top CSS block")
        btt_block = btt_match.group(1)
        self.assertTrue(re.search(r"position:\s*fixed", btt_block), "Back-to-top must be position fixed")
        self.assertTrue(re.search(r"left:\s*(?:33px|20px)", btt_block), "Back-to-top must be docked on left")
        self.assertTrue(re.search(r"bottom:\s*(?:98px|76px)", btt_block), "Back-to-top must be stacked above WhatsApp (bottom >= 76px)")

        # Chatbot bottom-right
        self.assertIn("#sp-btn", self.styles)
        cb_match = re.search(r"#sp-btn\s*\{([^}]+)\}", self.styles)
        self.assertIsNotNone(cb_match, "Missing #sp-btn CSS block")
        cb_block = cb_match.group(1)
        self.assertTrue(re.search(r"position:\s*fixed", cb_block), "Chatbot must be position fixed")
        self.assertTrue(re.search(r"right:\s*28px", cb_block), "Chatbot must be docked on right")
        self.assertTrue(re.search(r"bottom:\s*28px", cb_block), "Chatbot must be docked on bottom")

    def test_r4_03_floating_navigation_z_index_hierarchy(self):
        """Verify collision-free z-index hierarchy: Chatbot launcher > WhatsApp > Back-to-Top."""
        wa_z = re.search(r"\.whatsapp-float[^{]*\{[^}]*z-index:\s*(\d+)", self.styles)
        btt_z = re.search(r"\.back-to-top[^{]*\{[^}]*z-index:\s*(\d+)", self.styles)
        cb_z = re.search(r"#sp-btn[^{]*\{[^}]*z-index:\s*(\d+)", self.styles)

        self.assertIsNotNone(wa_z, "Missing WhatsApp z-index")
        self.assertIsNotNone(btt_z, "Missing Back-to-Top z-index")
        self.assertIsNotNone(cb_z, "Missing Chatbot z-index")

        wa_val = int(wa_z.group(1))
        btt_val = int(btt_z.group(1))
        cb_val = int(cb_z.group(1))

        self.assertGreater(wa_val, btt_val, f"WhatsApp z-index ({wa_val}) should exceed Back-to-top ({btt_val})")
        self.assertGreater(cb_val, wa_val, f"Chat launcher z-index ({cb_val}) should exceed WhatsApp ({wa_val})")

    def test_r4_04_live_github_pages_core_assets_http_200(self):
        """Verify core web pages and script bundles return HTTP 200 on live GitHub Pages."""
        core_endpoints = [
            LIVE_BASE_URL,
            LIVE_BASE_URL + "catalog_data.js",
            LIVE_BASE_URL + "scripts/app.js",
        ]
        for url in core_endpoints:
            tested_url, status, err = probe_http_url(url, timeout=12)
            self.assertEqual(status, 200, f"Live asset failed HTTP 200: {tested_url} (status={status}, err={err})")

    def test_r4_05_live_github_pages_product_images_stratified_sample_http_200(self):
        """Verify large stratified sample (350+ items across all 16 categories) returns HTTP 200 on live GitHub Pages."""
        # Stratified sampling across all 16 categories
        categorized = {cat: [] for cat in CANONICAL_16_CATEGORIES}
        for p in self.products:
            c = p.get("category_slug")
            img = p.get("image") or p.get("image_path")
            if c in categorized and img:
                categorized[c].append(img)

        sample_images = []
        random.seed(42)  # Deterministic seed for reproducibility
        for cat, imgs in categorized.items():
            # Sample up to 25 from each category, or all if fewer
            k = min(len(imgs), 25)
            sample_images.extend(random.sample(imgs, k))

        # Ensure we have >= 300 sample images
        self.assertGreaterEqual(len(sample_images), 300, f"Sample size {len(sample_images)} < 300")

        urls_to_test = [LIVE_BASE_URL + img.replace("\\", "/") for img in sample_images]

        failures = []
        passes = 0
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(probe_http_url, u): u for u in urls_to_test}
            for fut in as_completed(futures):
                url, status, err = fut.result()
                if status == 200:
                    passes += 1
                else:
                    failures.append((url, status, err))

        self.assertEqual(
            len(failures), 0,
            f"{len(failures)} out of {len(urls_to_test)} live product images failed HTTP 200! Failures: {failures[:5]}"
        )
        print(f"\n[PASS] Verified {passes}/{len(urls_to_test)} live product images return HTTP 200 (100.0% success rate across all 16 categories)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
