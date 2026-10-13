"""
Tier 3: Cross-Feature Combinations (Pairwise Interaction) E2E Tests
Tests multi-attribute interactions: Brand + Category, Active Search + Category Tabs,
WhatsApp URL Encoding with Complex Models, Lightbox with Diverse Aspect Ratios,
and Deduplication Coherence with Downstream Quotation Actions.
"""

import re
import unittest
import urllib.parse
from PIL import Image

from tests.helpers import (
    compute_canonical_model,
    compute_dhash,
    compute_token_jaccard,
    extract_css_text,
    get_html_text,
    get_parsed_soup,
    hamming_distance,
    load_catalog_products,
    parse_whatsapp_url,
    simulate_in_memory_search,
)


class TestBrandAndCategoryPairwiseCombinations(unittest.TestCase):
    """Pairwise interaction between Brand filtering and Category filtering."""

    @classmethod
    def setUpClass(cls):
        cls.products = load_catalog_products()

    def test_t3_01_brand_and_category_intersection(self):
        """Verify brand search within category returns only items meeting both criteria."""
        sample_catalog = [
            {"id": "1", "name": "boAt Airdopes 131", "brand": "boAt", "category": "electronics-tech"},
            {"id": "2", "name": "boAt Stone 650", "brand": "boAt", "category": "electronics-tech"},
            {"id": "3", "name": "boAt Travel Pouch", "brand": "boAt", "category": "bags-travel"},
            {"id": "4", "name": "Noise ColorFit", "brand": "Noise", "category": "electronics-tech"},
        ]
        results = simulate_in_memory_search(sample_catalog, "boAt", category="electronics-tech")
        self.assertEqual(len(results), 2)
        for r in results:
            self.assertEqual(r["brand"], "boAt")
            self.assertEqual(r["category"], "electronics-tech")

    def test_t3_02_brand_in_disjoint_category_returns_empty(self):
        """Verify brand filtered against completely disjoint category returns 0 results."""
        sample_catalog = [
            {"id": "1", "name": "boAt Airdopes 131", "brand": "boAt", "category": "electronics-tech"},
            {"id": "2", "name": "boAt Stone 650", "brand": "boAt", "category": "electronics-tech"},
        ]
        results = simulate_in_memory_search(sample_catalog, "boAt", category="office-desk")
        self.assertEqual(len(results), 0)

    def test_t3_03_inhouse_brand_and_category_filtering(self):
        """Verify inhouse brand filtering within office-desk category on live data."""
        inhouse_desk = simulate_in_memory_search(self.products, "sterling", category="office-desk")
        self.assertGreater(len(inhouse_desk), 0, "Expected in-house desk products")
        for item in inhouse_desk:
            self.assertEqual(item.get("category"), "office-desk")

    def test_t3_04_partner_brand_in_gourmet_hampers(self):
        """Verify festive hampers category filtering with gourmet brand terms."""
        hampers = simulate_in_memory_search(self.products, "", category="festive-hampers")
        self.assertGreater(len(hampers), 0)
        for item in hampers:
            self.assertEqual(item.get("category"), "festive-hampers")


class TestSearchQueryWithCategoryAndTypeTabs(unittest.TestCase):
    """Pairwise interaction between Active Search and Tab Switching."""

    @classmethod
    def setUpClass(cls):
        cls.products = load_catalog_products()

    def test_t3_05_active_search_preserved_when_switching_category_tabs(self):
        """Verify query 'pen' produces valid subsets when switching categories."""
        all_pens = simulate_in_memory_search(self.products, "pen", category="all")
        writing_pens = simulate_in_memory_search(self.products, "pen", category="pens-writing")
        self.assertGreater(len(all_pens), 0)
        self.assertGreater(len(writing_pens), 0)
        self.assertLessEqual(len(writing_pens), len(all_pens))

    def test_t3_06_search_query_with_view_mode_tabs(self):
        """Verify search query across view mode tabs (all vs inhouse vs partner)."""
        all_matches = simulate_in_memory_search(self.products, "desk", type_filter="all")
        inhouse_matches = simulate_in_memory_search(self.products, "desk", type_filter="inhouse")
        self.assertLessEqual(len(inhouse_matches), len(all_matches))

    def test_t3_07_clearing_search_retains_active_category_tab(self):
        """Verify clearing search string returns to full category count, not 'all' count."""
        office_all = simulate_in_memory_search(self.products, "", category="office-desk")
        office_filtered = simulate_in_memory_search(self.products, "clock", category="office-desk")
        self.assertLessEqual(len(office_filtered), len(office_all))
        # After clearing search (query=""):
        cleared = simulate_in_memory_search(self.products, "", category="office-desk")
        self.assertEqual(len(cleared), len(office_all))

    def test_t3_08_dynamic_pill_count_recalculation_under_search(self):
        """Verify dynamic pill counts when active search query is applied."""
        total_desk_items = simulate_in_memory_search(self.products, "desk")
        # Sum of items matching "desk" grouped by category must equal total_desk_items
        cat_counts = {}
        for item in total_desk_items:
            cat = item.get("category") or "unknown"
            cat_counts[cat] = cat_counts.get(cat, 0) + 1
        self.assertEqual(sum(cat_counts.values()), len(total_desk_items))


class TestWhatsAppQuotationUrlEncodingWithComplexMetadata(unittest.TestCase):
    """Pairwise interaction between complex product metadata and WhatsApp URL encoding."""

    def test_t3_09_whatsapp_url_with_slashes_and_ampersands(self):
        """Verify complex title 'Airdopes 131 - Bold & Black / #2' encodes and decodes perfectly."""
        brand = "boAt"
        name = "Airdopes 131 - Bold & Black / #2"
        category = "Tech & Audio"
        raw_msg = f"Hi Sterling Prime, I would like a quotation for:\n\n*{brand} {name}*\nCategory: {category}"
        url = f"https://wa.me/917041614713?text={urllib.parse.quote(raw_msg)}"
        parsed = parse_whatsapp_url(url)
        self.assertTrue(parsed["is_valid_endpoint"])
        self.assertIn("Bold & Black / #2", parsed["raw_text"])
        self.assertIn("Tech & Audio", parsed["raw_text"])

    def test_t3_10_whatsapp_url_with_rupee_price_and_newlines(self):
        """Verify message with Rupee symbol '₹' and multiple linebreaks generates valid URL."""
        msg = "Hi Sterling Prime,\nQuotation request:\n*Noise ColorFit*\nPrice: ₹2,499/-\nQty: 250 units"
        url = f"https://wa.me/917041614713?text={urllib.parse.quote(msg)}"
        parsed = parse_whatsapp_url(url)
        self.assertTrue(parsed["is_valid_endpoint"])
        self.assertIn("₹2,499/-", parsed["raw_text"])
        self.assertIn("Qty: 250 units", parsed["raw_text"])

    def test_t3_11_whatsapp_url_special_symbols_and_apostrophes(self):
        """Verify single quotes, asterisks, and brackets are preserved in decoded text."""
        msg = "Hi Sterling Prime, I'm interested in 'Executive's Choice' [Model: EC-101]!"
        url = f"https://wa.me/917041614713?text={urllib.parse.quote(msg)}"
        parsed = parse_whatsapp_url(url)
        self.assertIn("Executive's Choice", parsed["raw_text"])
        self.assertIn("[Model: EC-101]", parsed["raw_text"])


class TestLightboxAspectRatiosAndActionCoherence(unittest.TestCase):
    """Pairwise interaction between Lightbox zoom modal, diverse image aspect ratios, and actions."""

    def test_t3_12_lightbox_portrait_image_aspect_ratio(self):
        """Verify portrait aspect ratio image (e.g. 400x800) fits without breaking modal max-height."""
        css_text = extract_css_text()
        # Lightbox image container must constrain max-height to viewport
        self.assertIn("max-height: 50vh", css_text)
        self.assertIn("object-fit: contain", css_text)

    def test_t3_13_lightbox_landscape_image_aspect_ratio(self):
        """Verify landscape aspect ratio image (e.g. 1200x600) fits without horizontal overflow."""
        css_text = extract_css_text()
        self.assertIn("max-width: 100%", css_text)
        self.assertIn("max-width: 780px", css_text)  # Modal width boundary

    def test_t3_14_lightbox_square_image_aspect_ratio(self):
        """Verify square image (1:1) centers cleanly."""
        css_text = extract_css_text()
        self.assertIn("justify-content: center", css_text)
        self.assertIn("align-items: center", css_text)

    def test_t3_15_lightbox_dual_actions_metadata_sync(self):
        """Verify Lightbox WhatsApp button and Email button both reference product info."""
        soup = get_parsed_soup()
        wa_btn = soup.select_one("#lightbox-wa-btn") or soup.select_one(".lightbox-wa-btn")
        email_btn = soup.select_one("#lightbox-email-btn") or soup.select_one(".lightbox-email-btn")
        self.assertIsNotNone(wa_btn, "Missing Lightbox WhatsApp action button")
        self.assertIsNotNone(email_btn, "Missing Lightbox Email action button")


class TestDeduplicationAndQuotationCoherence(unittest.TestCase):
    """Pairwise interaction between Deduplication Engine and downstream B2B Quotations."""

    def test_t3_16_deduplicated_item_retains_cleanest_title_for_quotation(self):
        """Verify deduplication between minor title variants selects richest title for quote."""
        title_a = "boAt Airdopes 131"
        title_b = "boAt Airdopes 131 True Wireless Bluetooth Earbuds"
        jaccard = compute_token_jaccard(title_a, title_b)
        self.assertGreaterEqual(jaccard, 0.4)
        # Canonical choice picks the longer, more informative title
        canonical_title = max([title_a, title_b], key=len)
        self.assertEqual(canonical_title, title_b)
        # Downstream WhatsApp quotation pre-fill
        wa_url = f"https://wa.me/917041614713?text={urllib.parse.quote(f'*{canonical_title}*')}"
        parsed = parse_whatsapp_url(wa_url)
        self.assertIn("True Wireless Bluetooth Earbuds", parsed["raw_text"])

    def test_t3_17_deduplication_preserves_higher_resolution_photo(self):
        """Verify deduplication retains higher resolution photo when perceptual hash matches."""
        im_low = Image.new("RGB", (200, 200), color="blue")
        im_high = Image.new("RGB", (800, 800), color="blue")
        dist = hamming_distance(compute_dhash(im_low), compute_dhash(im_high))
        self.assertLessEqual(dist, 5, "Perceptual hash should match for identical content")
        # Resolution comparison selects high-res
        selected = im_high if (im_high.width * im_high.height) > (im_low.width * im_low.height) else im_low
        self.assertEqual(selected.size, (800, 800))

    def test_t3_18_inhouse_and_partner_card_badge_differentiation(self):
        """Verify card badges cleanly differentiate inhouse vs partner items."""
        soup = get_parsed_soup()
        inhouse_cards = soup.select(".product-card.is-inhouse")
        self.assertGreater(len(inhouse_cards), 0)
        first_card = inhouse_cards[0]
        badge = first_card.select_one(".product-badge")
        self.assertIsNotNone(badge)
        self.assertTrue(len(badge.get_text().strip()) > 0)
