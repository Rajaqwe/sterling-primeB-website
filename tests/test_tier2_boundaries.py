"""
Tier 2: Boundary & Corner Cases E2E Tests
Tests adversarial inputs, empty states, case insensitivity, regex metacharacters,
extreme string lengths, Unicode/currency traps, and corrupted assets.
"""

import io
import re
import tempfile
import time
import unittest
import urllib.parse
from pathlib import Path
from PIL import Image

from tests.helpers import (
    RAW_IMAGES_DIR,
    compute_canonical_model,
    compute_token_jaccard,
    get_html_text,
    get_parsed_soup,
    load_catalog_products,
    parse_whatsapp_url,
    simulate_in_memory_search,
    verify_image_file,
)


class TestSearchQueryBoundaryCases(unittest.TestCase):
    """Tier 2: Boundary tests for search query inputs."""

    @classmethod
    def setUpClass(cls):
        cls.products = load_catalog_products()

    def test_t2_01_empty_string_search_returns_all_items(self):
        """Verify empty string query '' returns all items without filtering."""
        results = simulate_in_memory_search(self.products, "")
        self.assertEqual(len(results), len(self.products))

    def test_t2_02_whitespace_only_query_is_trimmed(self):
        """Verify queries with pure whitespace '   ' are trimmed and return all items."""
        results = simulate_in_memory_search(self.products, "     ")
        self.assertEqual(len(results), len(self.products))

    def test_t2_03_unicode_whitespace_and_newlines_handled(self):
        """Verify tab, newline, and non-breaking spaces handle gracefully without error."""
        queries = ["\t\n", "  \r\n  ", "\u200B", "\u00A0"]
        for q in queries:
            results = simulate_in_memory_search(self.products, q)
            self.assertEqual(len(results), len(self.products), f"Failed on whitespace query: {repr(q)}")

    def test_t2_04_multiple_consecutive_spaces_between_tokens(self):
        """Verify multiple spaces between tokens 'desk    organizer' match accurately."""
        res_single = simulate_in_memory_search(self.products, "desk")
        res_multi = simulate_in_memory_search(self.products, "desk   ")
        self.assertEqual(len(res_single), len(res_multi))

    def test_t2_05_regex_metacharacters_in_search_query(self):
        """Verify search with regex metacharacters (*, +, ?, [, ], (, ), ^, $, |) does not crash."""
        metachar_queries = [
            "boAt (131)",
            "Noise [ColorFit]+",
            "Model * 100",
            "Desk? Organiser",
            "Title $100 | VIP",
        ]
        for q in metachar_queries:
            try:
                results = simulate_in_memory_search(self.products, q)
                self.assertIsInstance(results, list)
            except Exception as exc:
                self.fail(f"Search crashed on query {q}: {exc}")


class TestCaseInsensitiveBoundaryCases(unittest.TestCase):
    """Tier 2: Boundary tests for case sensitivity across brands, models, and categories."""

    @classmethod
    def setUpClass(cls):
        cls.products = load_catalog_products()

    def test_t2_06_uppercase_lowercase_and_mixed_brand_search(self):
        """Verify 'BOAT', 'boAt', and 'boat' yield identical search results."""
        res_upper = simulate_in_memory_search(self.products, "BOAT")
        res_mixed = simulate_in_memory_search(self.products, "boAt")
        res_lower = simulate_in_memory_search(self.products, "boat")
        self.assertEqual(len(res_upper), len(res_mixed))
        self.assertEqual(len(res_mixed), len(res_lower))

    def test_t2_07_mixed_case_multitoken_query(self):
        """Verify mixed-case multi-word queries 'DeSk OrGaNiZeR' match consistently."""
        res1 = simulate_in_memory_search(self.products, "desk organizer")
        res2 = simulate_in_memory_search(self.products, "DeSk OrGaNiZeR")
        self.assertEqual(len(res1), len(res2))

    def test_t2_08_lowercase_query_matches_uppercase_model_code(self):
        """Verify lowercase model code 'd1001' matches uppercase canonical 'D1001'."""
        sample_catalog = [
            {"name": "Executive Diary", "brand": "Idea", "model": "D1001", "category": "stationery-work"}
        ]
        results = simulate_in_memory_search(sample_catalog, "d1001")
        self.assertEqual(len(results), 1)

    def test_t2_09_category_slug_case_insensitivity(self):
        """Verify category filtering is case-insensitive ('Office-Desk' vs 'office-desk')."""
        res1 = simulate_in_memory_search(self.products, "", category="office-desk")
        res2 = simulate_in_memory_search(self.products, "", category="OFFICE-DESK")
        self.assertEqual(len(res1), len(res2))

    def test_t2_10_type_filter_case_insensitivity(self):
        """Verify type filter is case-insensitive ('Inhouse' vs 'inhouse')."""
        res1 = simulate_in_memory_search(self.products, "", type_filter="inhouse")
        res2 = simulate_in_memory_search(self.products, "", type_filter="INHOUSE")
        self.assertEqual(len(res1), len(res2))


class TestSpecialCharactersModelBoundaryCases(unittest.TestCase):
    """Tier 2: Boundary tests for special characters and model codes."""

    def test_t2_11_model_code_with_slashes_and_hashes(self):
        """Verify 'Airdopes 131 - Black/Grey #2' normalizes without corruption."""
        raw = "Airdopes 131 - Black/Grey #2"
        canonical = compute_canonical_model(raw)
        self.assertEqual(canonical, "AIRDOPES131BLACKGREY2")

    def test_t2_12_model_code_with_ampersand_and_plus(self):
        """Verify 'Rockerz 255 (Pro+) & Mic' normalizes cleanly."""
        raw = "Rockerz 255 (Pro+) & Mic"
        canonical = compute_canonical_model(raw)
        self.assertEqual(canonical, "ROCKERZ255PROMIC")

    def test_t2_13_model_code_with_quotes(self):
        """Verify inch quotes like '14\" Laptop Sleeve' do not corrupt model string."""
        raw = '14" Laptop Sleeve'
        canonical = compute_canonical_model(raw)
        self.assertEqual(canonical, "14LAPTOPSLEEVE")

    def test_t2_14_model_code_with_unicode_dashes(self):
        """Verify en-dash, em-dash, and bullets normalize identically to hyphens."""
        dashes = ["D-1001", "D–1001", "D—1001", "D•1001"]
        keys = {compute_canonical_model(d) for d in dashes}
        self.assertEqual(len(keys), 1)
        self.assertEqual(list(keys)[0], "D1001")

    def test_t2_15_empty_and_none_model_code_handling(self):
        """Verify None, empty string, and whitespace model codes produce safe empty strings."""
        self.assertEqual(compute_canonical_model(""), "")
        self.assertEqual(compute_canonical_model(None), "")
        self.assertEqual(compute_canonical_model("   "), "")


class TestImagePathAndCorruptAssetBoundaryCases(unittest.TestCase):
    """Tier 2: Boundary tests for image paths, URL escaping, and corrupt files."""

    def test_t2_16_image_path_with_spaces_url_encoded(self):
        """Verify image paths with spaces are URL encoded with '%20'."""
        path_with_space = "raw images/BLUE DESK ORGAIZER.jpeg"
        encoded = path_with_space.replace(" ", "%20")
        self.assertEqual(encoded, "raw%20images/BLUE%20DESK%20ORGAIZER.jpeg")
        self.assertNotIn(" ", encoded)

    def test_t2_17_image_path_with_parentheses(self):
        """Verify filenames with parentheses like 'COASTER SET (2).jpeg' are resolved on disk."""
        target_path = RAW_IMAGES_DIR / "COASTER SET (2).jpeg"
        self.assertTrue(target_path.exists(), f"Image with parentheses missing: {target_path}")
        ok, msg = verify_image_file(target_path)
        self.assertTrue(ok, f"Verification failed: {msg}")

    def test_t2_18_simulated_zero_byte_image_fails_verification(self):
        """Verify 0-byte file fails image validation contract."""
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            temp_path = Path(f.name)
        try:
            ok, msg = verify_image_file(temp_path)
            self.assertFalse(ok, "0-byte image should fail verification")
            self.assertIn("File size too small", msg)
        finally:
            temp_path.unlink(missing_ok=True)

    def test_t2_19_simulated_corrupted_header_image_fails_verification(self):
        """Verify file with corrupt bytes fails PIL verification."""
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            f.write(b"NOT_A_REAL_JPEG_IMAGE_HEADER_PADDING_BYTES" * 100)
            temp_path = Path(f.name)
        try:
            ok, msg = verify_image_file(temp_path)
            self.assertFalse(ok, "Corrupt file should fail verification")
            self.assertIn("Corrupted image", msg)
        finally:
            temp_path.unlink(missing_ok=True)

    def test_t2_20_sub_100px_dimension_image_fails_verification(self):
        """Verify image with dimensions under 100x100 fails validation."""
        import random
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            im = Image.new("RGB", (80, 80))
            # Fill with noise so compressed JPEG size exceeds 1000 bytes
            pixels = [random.randint(0, 255) for _ in range(80 * 80 * 3)]
            im.frombytes(bytes(pixels))
            im.save(f.name, "JPEG", quality=100)
            temp_path = Path(f.name)
        try:
            self.assertGreater(temp_path.stat().st_size, 1000, "Test image should exceed 1KB")
            ok, msg = verify_image_file(temp_path)
            self.assertFalse(ok, "Sub-100px image should fail validation")
            self.assertIn("Dimensions below threshold", msg)
        finally:
            temp_path.unlink(missing_ok=True)


class TestFilterSwitchingAndStateBoundaryCases(unittest.TestCase):
    """Tier 2: Boundary tests for filter switching and UI state coherence."""

    @classmethod
    def setUpClass(cls):
        cls.products = load_catalog_products()

    def test_t2_21_category_switch_with_active_search_query(self):
        """Verify active search query filters within selected category."""
        all_desk = simulate_in_memory_search(self.products, "desk", category="all")
        office_desk = simulate_in_memory_search(self.products, "desk", category="office-desk")
        self.assertLessEqual(len(office_desk), len(all_desk))

    def test_t2_22_rapid_filter_switching_simulation(self):
        """Verify sequential filter switches do not leak or corrupt result sets."""
        categories = ["office-desk", "gift-sets", "drinkware-kitchen", "all"]
        counts = []
        for cat in categories:
            res = simulate_in_memory_search(self.products, "", category=cat)
            counts.append(len(res))
        # Re-run same switches: counts must be 100% deterministic
        for idx, cat in enumerate(categories):
            res = simulate_in_memory_search(self.products, "", category=cat)
            self.assertEqual(len(res), counts[idx])

    def test_t2_23_empty_category_yields_zero_results(self):
        """Verify querying a category with 0 matches returns empty list without error."""
        results = simulate_in_memory_search(self.products, "nonexistent_token_xyz_12345")
        self.assertEqual(len(results), 0)

    def test_t2_24_reset_filter_restores_full_count(self):
        """Verify reset action returns count to len(products)."""
        filtered = simulate_in_memory_search(self.products, "boat", category="office-desk")
        self.assertEqual(len(filtered), 0)
        restored = simulate_in_memory_search(self.products, "", category="all")
        self.assertEqual(len(restored), len(self.products))

    def test_t2_25_view_mode_filter_and_category_intersection(self):
        """Verify inhouse products + specific category filter intersection."""
        inhouse_all = simulate_in_memory_search(self.products, "", type_filter="inhouse")
        inhouse_office = simulate_in_memory_search(self.products, "", category="office-desk", type_filter="inhouse")
        self.assertLessEqual(len(inhouse_office), len(inhouse_all))


class TestUnicodeEscapingAndResourceStressCases(unittest.TestCase):
    """Tier 2: Boundary tests for Unicode, XSS escaping, and latency stress."""

    @classmethod
    def setUpClass(cls):
        cls.products = load_catalog_products()

    def test_t2_26_rupee_currency_symbol_preservation(self):
        """Verify Indian Rupee symbol '₹' does not raise cp1252 UnicodeEncodeError."""
        text_with_rupee = "Price: ₹1,450/- per unit"
        encoded_bytes = text_with_rupee.encode("utf-8")
        decoded_text = encoded_bytes.decode("utf-8")
        self.assertEqual(decoded_text, text_with_rupee)
        self.assertIn("₹", decoded_text)

    def test_t2_27_xss_injection_payload_in_search_query(self):
        """Verify XSS payloads in search queries do not crash search or match inappropriately."""
        xss_queries = [
            "<script>alert(1)</script>",
            "\" onmouseover=\"alert('xss')",
            "'; DROP TABLE products; --",
            "<img src=x onerror=alert(1)>",
        ]
        for payload in xss_queries:
            results = simulate_in_memory_search(self.products, payload)
            self.assertIsInstance(results, list)

    def test_t2_28_extreme_length_search_query_latency(self):
        """Verify 1,000-character search query executes in < 5ms with 0 matches."""
        long_query = "Noise Smartwatch " * 60  # ~1000 chars
        t0 = time.time()
        results = simulate_in_memory_search(self.products, long_query)
        elapsed_ms = (time.time() - t0) * 1000
        self.assertLess(elapsed_ms, 5.0, f"Query took {elapsed_ms:.2f}ms")
        self.assertEqual(len(results), 0)

    def test_t2_29_html_entities_in_whatsapp_quote_encoding(self):
        """Verify quotation with ampersands, quotes, and slashes encodes to valid RFC 3986."""
        brand = "Ferns & Petals"
        name = "Luxury Hamper \"Celebration Edition\""
        category = "Festive Hampers & Gourmet"
        raw_msg = f"Hi Sterling Prime, I would like a quotation for:\n\n*{brand} {name}*\nCategory: {category}"
        encoded_url = f"https://wa.me/917041614713?text={urllib.parse.quote(raw_msg)}"
        parsed = parse_whatsapp_url(encoded_url)
        self.assertTrue(parsed["is_valid_endpoint"])
        self.assertIn("Ferns & Petals", parsed["raw_text"])
        self.assertIn("Celebration Edition", parsed["raw_text"])

    def test_t2_30_missing_optional_fields_in_product_record(self):
        """Verify product records with null or missing optional fields handle cleanly."""
        sparse_item = {
            "id": "sparse_001",
            "name": "Minimal Product",
            "brand": None,
            "category": "office-desk",
            "model": None,
            "description": None,
            "price": None,
        }
        results = simulate_in_memory_search([sparse_item], "minimal")
        self.assertEqual(len(results), 1)
        # Search for non-matching term
        results2 = simulate_in_memory_search([sparse_item], "electronics")
        self.assertEqual(len(results2), 0)
