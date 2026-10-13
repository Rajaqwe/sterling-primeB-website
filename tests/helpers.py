"""
Test infrastructure helpers, contract definitions, and reference oracles
for Sterling Prime E2E Test Suite.
"""

import hashlib
import json
import os
import re
import sys
import urllib.parse
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import bs4
from PIL import Image

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Directory and File Paths
REPO_ROOT = Path(r"c:\Users\Krishana\Downloads\sterling-primeB-website")
CATALOGUES_DIR = Path(r"c:\Users\Krishana\Downloads\catalogues")
RAW_IMAGES_DIR = REPO_ROOT / "raw images"
INDEX_HTML_PATH = REPO_ROOT / "index.html"
PRODUCTS_JSON_PATH = REPO_ROOT / "products.json"
CATALOG_DATA_JS_PATH = REPO_ROOT / "catalog_data.js"
EXTRACTED_RAW_PATH = REPO_ROOT / "extracted_products_raw.json"
ZIP_ARCHIVE_PATH = REPO_ROOT / "sterling-prime-website-complete.zip"
ZIP_ARCHIVE_FALLBACK = REPO_ROOT / "sterling-primeB-website.zip"

# Master Taxonomy Definitions from PROJECT.md and Company Profile
EXPECTED_CATEGORIES = [
    "all",
    "gift-sets",
    "festive-hampers",
    "office-desk",
    "bags-travel",
    "pens-writing",
    "healthcare-medical",
    "stationery-work",
    "drinkware-kitchen",
    "wooden-gifts",
    "electronics-tech",
    "acrylic-displays",
    "wellness-care",
    "apparel-lifestyle",
    "clocks-planners",
    "promotional-merch",
    "packaging-storage",
]

# Authoritative Partner Catalogue Folders
CATALOGUE_BRAND_FOLDERS = [
    "gift desk",
    "idea corporate gifts",
    "procter",
    "tapwell",
    "fnp catalogue",
    "melamine",
    "New folder",
    "salido",
    "the bombay store",
]

# Cached DOM and Text
_CACHED_SOUP: Optional[bs4.BeautifulSoup] = None
_CACHED_HTML_TEXT: Optional[str] = None


def get_html_text() -> str:
    """Read raw HTML content of index.html with caching."""
    global _CACHED_HTML_TEXT
    if _CACHED_HTML_TEXT is None:
        if not INDEX_HTML_PATH.exists():
            raise FileNotFoundError(f"index.html not found at {INDEX_HTML_PATH}")
        with open(INDEX_HTML_PATH, "r", encoding="utf-8", errors="replace") as f:
            _CACHED_HTML_TEXT = f.read()
    return _CACHED_HTML_TEXT


def get_parsed_soup() -> bs4.BeautifulSoup:
    """Parse index.html with BeautifulSoup, memoized for high-speed test execution."""
    global _CACHED_SOUP
    if _CACHED_SOUP is None:
        raw_text = get_html_text()
        _CACHED_SOUP = bs4.BeautifulSoup(raw_text, "html.parser")
    return _CACHED_SOUP


def extract_css_text() -> str:
    """Extract all text contained in inline <style> tags from index.html."""
    soup = get_parsed_soup()
    styles = soup.find_all("style")
    return "\n".join(s.get_text() for s in styles)


def compute_sha256(filepath_or_bytes: Any) -> str:
    """Compute cryptographic SHA-256 hex digest for a file or raw bytes."""
    hasher = hashlib.sha256()
    if isinstance(filepath_or_bytes, (str, Path)):
        with open(filepath_or_bytes, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
    elif isinstance(filepath_or_bytes, (bytes, bytearray)):
        hasher.update(filepath_or_bytes)
    else:
        raise TypeError("Expected file path or bytes")
    return hasher.hexdigest()


def compute_canonical_model(code: str) -> str:
    """
    Tier 1 Deduplication Algorithm: Canonical Model Normalization.
    Strips all non-alphanumeric characters and converts to uppercase.
    Contract defined in PROJECT.md and survey tooling report.
    """
    if not code:
        return ""
    return re.sub(r"[^A-Z0-9]", "", str(code).upper())


def compute_token_jaccard(title1: str, title2: str) -> float:
    """
    Tier 2 Deduplication Algorithm: Token-Set Jaccard Similarity.
    Tokenizes titles, computes |intersection| / |union|.
    """
    def tokenize(text: str) -> set:
        if not text:
            return set()
        tokens = re.findall(r"[a-zA-Z0-9]+", str(text).lower())
        return set(tokens)

    set1 = tokenize(title1)
    set2 = tokenize(title2)
    if not set1 and not set2:
        return 1.0
    if not set1 or not set2:
        return 0.0
    return len(set1 & set2) / len(set1 | set2)


def compute_dhash(img_input: Any, hash_size: int = 8) -> int:
    """
    Tier 3 Deduplication Algorithm: Pure-Pillow 64-bit Difference Hash (dHash).
    Resizes image to (hash_size + 1, hash_size) in grayscale using Bilinear interpolation.
    Compares adjacent horizontal pixels to generate a 64-bit integer hash.
    Zero external dependencies (pure Pillow).
    """
    if isinstance(img_input, (str, Path)):
        with Image.open(img_input) as im:
            resized = im.convert("L").resize(
                (hash_size + 1, hash_size), Image.Resampling.BILINEAR
            )
            try:
                pixels = list(resized.get_flattened_data())
            except AttributeError:
                pixels = list(resized.getdata())
    elif isinstance(img_input, Image.Image):
        resized = img_input.convert("L").resize(
            (hash_size + 1, hash_size), Image.Resampling.BILINEAR
        )
        try:
            pixels = list(resized.get_flattened_data())
        except AttributeError:
            pixels = list(resized.getdata())
    else:
        raise TypeError("Expected filepath or PIL Image object")

    diff = 0
    for row in range(hash_size):
        for col in range(hash_size):
            p_left = pixels[row * (hash_size + 1) + col]
            p_right = pixels[row * (hash_size + 1) + col + 1]
            diff = (diff << 1) | (1 if p_left > p_right else 0)
    return diff


def hamming_distance(hash1: int, hash2: int) -> int:
    """Compute bitwise Hamming distance between two 64-bit integer hashes."""
    return (hash1 ^ hash2).bit_count()


def verify_image_file(image_path: Path) -> Tuple[bool, str]:
    """
    Strict image verification contract:
    - File exists and has size > 1000 bytes.
    - PIL verify() succeeds without corruption.
    - PIL load() successfully unpacks pixel buffer.
    - Dimensions >= 100x100 pixels.
    """
    if not image_path.exists():
        return False, f"File does not exist: {image_path}"
    if image_path.stat().st_size < 1000:
        return False, f"File size too small (<1KB): {image_path.stat().st_size} bytes"

    try:
        with Image.open(image_path) as im:
            im.verify()
        with Image.open(image_path) as im:
            im.load()
            w, h = im.size
            if w < 100 or h < 100:
                return False, f"Dimensions below threshold: {w}x{h} (minimum 100x100)"
    except Exception as exc:
        return False, f"Corrupted image ({type(exc).__name__}): {exc}"

    return True, "OK"


def parse_whatsapp_url(url: str) -> Dict[str, Any]:
    """
    Parses a WhatsApp B2B quotation URL and verifies parameters.
    Expected format: https://wa.me/917041614713?text=...
    """
    parsed = urllib.parse.urlparse(url)
    phone = parsed.path.strip("/")
    query_params = urllib.parse.parse_qs(parsed.query)
    text = query_params.get("text", [""])[0]

    return {
        "scheme": parsed.scheme,
        "netloc": parsed.netloc,
        "phone": phone,
        "raw_text": text,
        "is_valid_endpoint": (
            parsed.scheme in ("https", "http")
            and parsed.netloc == "wa.me"
            and phone == "917041614713"
        ),
    }


def load_catalog_products() -> List[Dict[str, Any]]:
    """
    Loads catalog product records according to the contract in PROJECT.md:
    1. First attempts to load products.json if it exists.
    2. Then attempts catalog_data.js.
    3. Fallback: extracts DOM cards from index.html.
    """
    if PRODUCTS_JSON_PATH.exists():
        with open(PRODUCTS_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    if CATALOG_DATA_JS_PATH.exists():
        with open(CATALOG_DATA_JS_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        match = re.search(r"window\.CATALOG_DATA\s*=\s*(\[.*?\]);", content, re.DOTALL)
        if match:
            return json.loads(match.group(1))

    # Extract static items from index.html as fallback representation
    soup = get_parsed_soup()
    cards = soup.select(".product-card")
    items = []
    for idx, card in enumerate(cards):
        name = card.get("data-name", "")
        brand = card.get("data-brand", "")
        category = card.get("data-category", "")
        cat_name = card.get("data-category-name", "")
        card_type = card.get("data-type", "")
        img_elem = card.select_one("img")
        img_src = img_elem.get("src", "") if img_elem else ""

        items.append({
            "id": f"card_{idx}",
            "name": name,
            "title": name,
            "brand": brand,
            "category": category,
            "category_slug": category,
            "category_name": cat_name,
            "type": card_type,
            "image": img_src,
            "image_path": img_src,
            "description": name,
        })
    return items


def simulate_in_memory_search(
    products: List[Dict[str, Any]],
    query: str,
    category: str = "all",
    type_filter: str = "all",
) -> List[Dict[str, Any]]:
    """
    Reference in-memory search implementation matching catalog.js contract.
    Filters across brand, model/name, category, keywords with case-insensitivity.
    """
    q = re.sub(r"[\s\u200b\u200c\u200d\ufeff]+", " ", (query or "")).strip().lower()
    cat_filter = (category or "all").strip().lower()
    t_filter = (type_filter or "all").strip().lower()

    results = []
    for item in products:
        # Category match
        if cat_filter != "all":
            item_cat = item.get("_cat_lower")
            if item_cat is None:
                item_cat = (item.get("category") or item.get("category_slug") or "").lower()
                item["_cat_lower"] = item_cat
            if item_cat != cat_filter:
                continue

        # Type filter match
        if t_filter != "all":
            item_type = item.get("_type_lower")
            if item_type is None:
                item_type = (item.get("type") or "").lower()
                item["_type_lower"] = item_type
            if item_type != t_filter:
                continue

        # Search query match
        if q:
            searchable = item.get("_searchable")
            if searchable is None:
                name = (item.get("name") or item.get("title") or "").lower()
                brand = (item.get("brand") or "").lower()
                model = (item.get("model") or item.get("model_number") or "").lower()
                desc = (item.get("description") or "").lower()
                cat = (item.get("category") or item.get("category_slug") or "").lower()
                cat_name = (item.get("category_name") or "").lower()
                searchable = f"{name} {brand} {model} {cat} {cat_name} {desc}"
                item["_searchable"] = searchable
            if q not in searchable:
                continue

        results.append(item)

    return results
