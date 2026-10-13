#!/usr/bin/env python3
"""
Milestone 2 – Cross-Catalogue Deduplication Engine (Authoritative)
===================================================================
Input  : extracted_products_raw.json (41,426 records from M1)
         index.html (171 in-house physical products)
Output : products.json               (All products: in-house + partner)
         catalog_data.js             (window.CATALOG_DATA = [...])

Deduplication rules:
  T1: Canonical brand + model exact match via compute_canonical_model (PROJECT.md contract)
  T2: Token-set Jaccard similarity on title >= 0.85 within same brand
  T3: Pure-Pillow 64-bit dHash Hamming distance <= 5
  T4: Exact image SHA-256 binary match

Category contract:
  - 'category': category slug (e.g. 'office-desk', 'electronics-tech', 'festive-hampers')
  - 'category_slug': category slug
  - 'category_name': human-readable display title (e.g. 'Office & Desk Essentials')
"""

import sys, os, json, re, hashlib, collections, pathlib
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

ROOT     = pathlib.Path(__file__).parent.parent
RAW_JSON = ROOT / "extracted_products_raw.json"
HTML_FILE = ROOT / "index.html"
OUT_JSON = ROOT / "products.json"
OUT_JS   = ROOT / "catalog_data.js"
IMG_DIR  = ROOT / "raw images" / "products"

SLUG_MAP = {
    "electronics-tech":     "Tech & Audio",
    "smartwatches":         "Smartwatches",
    "drinkware-bottles":    "Drinkware",
    "bags-travel":          "Bags & Travel",
    "pens-writing":         "Pens & Writing",
    "stationery-work":      "Stationery & Kits",
    "home-kitchen":         "Home & Kitchen",
    "festive-hampers":      "Hampers",
    "apparel-lifestyle":    "Apparel",
    "wellness-grooming":    "Wellness",
    "office-desk":          "Office & Desk",
    "wooden-handicrafts":   "Wooden Gifts",
    "clocks-planners":      "Clocks & Planners",
    "corporate-gift-sets":  "Gift Sets",
    "luxury-premium":       "Luxury",
    "books-learning":       "Books",
}

INHOUSE_SLUG_MAP = {
    "wooden-gifts": ("wooden-handicrafts", "Wooden Gifts"),
    "healthcare-medical": ("wellness-grooming", "Wellness"),
    "wellness-care": ("wellness-grooming", "Wellness"),
    "gift-sets": ("corporate-gift-sets", "Gift Sets"),
    "promotional-merch": ("corporate-gift-sets", "Gift Sets"),
    "packaging-storage": ("corporate-gift-sets", "Gift Sets"),
    "acrylic-displays": ("office-desk", "Office & Desk"),
    "drinkware-kitchen": ("drinkware-bottles", "Drinkware"),
}

CATEGORY_RULES = [
    (["smartwatch","smart watch","fitness band","smart band"], "smartwatches"),
    (["wall clock","table clock","desk clock","alarm clock","clock"], "clocks-planners"),
    (["luxury","exclusive","swarovski","trophy","award","memento","gold plat","silver plat"], "luxury-premium"),
    (["book","novel","education","magazine","reading"], "books-learning"),
    (["electronics","tech","gadget","laptop","computer","lenovo","speaker",
      "headphone","earphone","tws","neckband","earbuds","jbl","boat","noise",
      "blaupunkt","lapcare","bluetooth","wireless","usb","charger","powerbank",
      "power bank","dash","projector","mobile","phone","xech"], "electronics-tech"),
    (["drinkware","bottle","sipper","flask","mug","cup","glass","tumbler",
      "kitchenware","kitchen","lunch","tiffin","jar","canteen","aqua",
      "melamine","borosil","milton","aquaminder"], "drinkware-bottles"),
    (["bag","travel","trolley","luggage","backpack","sling","tote","pouch",
      "wallet","samsonite","delsey","carlton","briefcase","duffel"], "bags-travel"),
    (["pen","writing","ball pen","roller","fountain","stylus","marker",
      "parker","lamy","cross","waterman","sheaffer","artline"], "pens-writing"),
    (["stationery","notebook","diary","planner","notepad","file","folder",
      "clipboard","paper","memo","sticky","post-it","agenda",
      "year book","yearly"], "stationery-work"),
    (["home","dining","table","candle","photo frame","decor",
      "vase","showpiece","tray","plate","spoon","cutlery","coaster",
      "cushion","towel","bedsheet","linen"], "home-kitchen"),
    (["apparel","lifestyle","t-shirt","tshirt","shirt","polo","hoodie",
      "jacket","cap","hat","clothing","garment","raymond","lawman",
      "parx","snitch","park avenue"], "apparel-lifestyle"),
    (["wellness","grooming","health","massager","beardo","sanitizer",
      "care","spa","ayurved","personal care"], "wellness-grooming"),
    (["office","desk","organizer","stand","holder","paperweight","acrylic",
      "mdf","pen stand","business card","card holder","stamp","seal"], "office-desk"),
    (["wooden","wood","handicraft","handcraft","bamboo","eco","sustainable",
      "german silver","brass","metal art","idol","god","ganesh","deity",
      "statue","figurine"], "wooden-handicrafts"),
    (["corporate gift","joining kit","welcome kit","gift set","box set","gift box","combo","kit","bundle"], "corporate-gift-sets"),
    (["hamper","festive","diwali","christmas","eid","holi",
      "chocolate","gourmet","dry fruit","food","laddoo","namkeen","fnp",
      "potli","basket","mithai","sweets"], "festive-hampers"),
]

COVER_TITLE_PATTERNS = [
    r'\bcatalogue\s*\d*\b',
    r'\bcatalog\s*\d*\b',
    r'\bbrochure\b',
    r'\bdiwali\s*gifting\b',
    r'\bgifting\s*edit\b',
    r'\bcorporate\s*gifting\b',
    r'\bportfolio\b',
    r'\bcollection\s*202\d\b',
    r'\bannual\s*catalogue\b',
    r'\bprice\s*list\b',
    r'\bslide\s*01\b',
    r'\brepresentative\s*images\s*only\b',
    r'\bcall\s*or\s*whatsapp\b',
    r'\bterms\s*&\s*conditions\b',
    r'\bpowered\s*by\b'
]

def is_catalogue_cover(rec: dict, cover_dhashes: dict = None, img_dh: int = None) -> bool:
    title = (rec.get("title") or rec.get("name") or "").strip()
    model = (rec.get("model_number") or rec.get("model") or "").strip()
    brand = (rec.get("brand") or "").strip()
    page_num = rec.get("page_number", 0)
    src_pdf = rec.get("source_pdf", "")
    img_rel = (rec.get("image_path") or rec.get("image") or "").strip()

    # 1. Direct path check
    if "catalogue_covers" in img_rel.lower() or "cat_" in img_rel.lower():
        return True

    # 2. Bonus asset covers
    if not src_pdf.lower().endswith(".pdf"):
        if any(k in title.lower() for k in ["catalogue", "catalog", "mrp 01", "brochure"]):
            return True

    # 3. Title patterns
    for pat in COVER_TITLE_PATTERNS:
        if re.search(pat, title, re.IGNORECASE):
            return True

    # 4. Generic placeholder covers
    if model.endswith("-P01-01") or model.endswith("-S01-01") or "p01_01" in img_rel.lower():
        return True
    if any(title == f"{brand} Product {i}" for i in range(1, 25)):
        return True
    if title.upper() in [
        "PRODUCT", "MODEL NO.", "MRP :", "MODEL NO", "2002", "INCLUDES", "2026",
        "DURABLE", "UNBREAKABLE SHELL", "MEDIUM", "PP COLLECTION", "FREE SHOE BAG",
        "PACK OF 3", "A V A I L A B L E S I Z E S", "WOMEN’S", "MOQ -500", "SKU", "THE GIFT"
    ]:
        return True

    # 5. dHash match against the 335 covers
    if cover_dhashes and img_dh is not None:
        for cdh in cover_dhashes.values():
            if hamming(img_dh, cdh) <= 2:
                return True

    return False

def compute_canonical_model(code: str) -> str:
    """Strips all non-alphanumeric characters and converts to uppercase."""
    if not code:
        return ""
    return re.sub(r"[^A-Z0-9]", "", str(code).upper())

def raw_cat_to_slug(raw_category: str, title: str, brand: str) -> str:
    text = (raw_category + " " + title + " " + brand).lower()
    for keywords, slug in CATEGORY_RULES:
        for kw in keywords:
            if kw in text:
                return slug
    if "gourmet" in text or "hamper" in text or "festive" in text:
        return "festive-hampers"
    return "corporate-gift-sets"

def tokenize(s: str) -> set:
    return set(re.findall(r"[a-z0-9]+", s.lower()))

def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)

def file_sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return ""

def dhash(path: pathlib.Path, size=8) -> int | None:
    try:
        from PIL import Image
        with Image.open(path) as img:
            resized = img.convert("L").resize((size + 1, size))
            try:
                pixels = list(resized.get_flattened_data())
            except AttributeError:
                pixels = list(resized.getdata())
        bits = 0
        for row in range(size):
            for col in range(size):
                left  = pixels[row * (size + 1) + col]
                right = pixels[row * (size + 1) + col + 1]
                bits = (bits << 1) | (1 if left > right else 0)
        return bits
    except Exception:
        return None

def hamming(a: int, b: int) -> int:
    return bin(a ^ b).count("1")

def clean_title(raw: str) -> str:
    t = raw.strip()
    t = re.sub(r"\bpage\s*\d+\b", "", t, flags=re.I)
    t = re.sub(r"\bP\d{3,}\b", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t if t else "Corporate Gift Item"

def extract_inhouse_products() -> list[dict]:
    """Extracts original 171 in-house physical products from index.html."""
    soup = BeautifulSoup(open(HTML_FILE, encoding="utf-8"), "html.parser")
    cards = soup.select(".product-card.is-inhouse")
    items = []
    for idx, card in enumerate(cards, 1):
        name = card.get("data-name", "")
        brand = card.get("data-brand", "Sterling Prime In-House")
        raw_slug = card.get("data-category", "office-desk")
        raw_cat_name = card.get("data-category-name", "Office & Desk Essentials")
        
        if raw_slug in INHOUSE_SLUG_MAP:
            cat_slug, cat_name = INHOUSE_SLUG_MAP[raw_slug]
        else:
            cat_slug = raw_slug
            cat_name = SLUG_MAP.get(cat_slug, raw_cat_name)

        img_elem = card.select_one("img")
        img_src = img_elem.get("src", "") if img_elem else ""

        items.append({
            "id": f"inhouse_{idx:04d}",
            "name": name,
            "title": name,
            "model": name,
            "brand": brand,
            "category": cat_slug,
            "category_slug": cat_slug,
            "category_name": cat_name,
            "type": "inhouse",
            "image": img_src,
            "image_path": img_src,
            "description": f"{name} by {brand}",
            "source": "Sterling Prime In-House",
        })
    return items

def main():
    print("=" * 65)
    print("Authoritative Cross-Catalogue Deduplication Engine")
    print("=" * 65)

    # 1. In-house products
    inhouse_items = extract_inhouse_products()
    print(f"\n[1/5] Extracted {len(inhouse_items)} in-house products from index.html")

    # 2. Raw partner products
    print(f"\n[2/5] Loading {RAW_JSON.name} …")
    with open(RAW_JSON, encoding="utf-8") as f:
        raw_partner = json.load(f)
    print(f"      {len(raw_partner):,} raw partner records loaded")

    # 2.5 Pre-compute cover dhashes for 335 covers (Requirement R1)
    COVERS_DIR = ROOT / "raw images" / "catalogue_covers"
    cover_dhashes: dict[pathlib.Path, int] = {}
    if COVERS_DIR.exists():
        for f in os.listdir(COVERS_DIR):
            if f.lower().endswith((".jpg", ".jpeg", ".png")):
                fp = COVERS_DIR / f
                dh = dhash(fp)
                if dh is not None:
                    cover_dhashes[fp] = dh
    print(f"      Loaded {len(cover_dhashes)} cover dhashes from {COVERS_DIR.name}")

    # 3. Deduplicate partner products
    print(f"\n[3/5] Deduplicating partner products …")
    seen_canonical_model: set[str] = set()
    seen_sha256: dict[str, str] = {}
    seen_dhash: list[tuple[int, str]] = []
    seen_tokens: dict[str, list[tuple[set, str]]] = collections.defaultdict(list)

    unique_partner: list[dict] = []
    dup_count = 0
    img_cache: dict[str, int | None] = {}

    total = len(raw_partner)
    for idx, rec in enumerate(raw_partner, 1):
        if idx % 5000 == 0:
            pct = (idx / total) * 100
            print(f"      … {idx:,}/{total:,} ({pct:.0f}%) – kept: {len(unique_partner):,}")

        raw_id = rec.get("id", "")
        title = clean_title(rec.get("title", "") or "")
        model = (rec.get("model_number", "") or "").strip()
        brand = (rec.get("brand", "") or "").strip()
        img_rel = (rec.get("image_path", "") or "").strip()
        img_path = ROOT / img_rel if img_rel else None

        # Check image exists on disk
        if not img_path or not img_path.exists():
            dup_count += 1
            continue

        # R1: Multi-attribute Cover Purge check (Text / Model / Metadata)
        if is_catalogue_cover(rec, cover_dhashes=None, img_dh=None):
            dup_count += 1
            continue

        # T1: Canonical Brand + Model exact match (Strict Project Contract)
        b_code = compute_canonical_model(brand)
        m_code = compute_canonical_model(model)
        if b_code and m_code:
            key1 = f"{b_code}_{m_code}"
            if key1 in seen_canonical_model:
                dup_count += 1
                continue
            seen_canonical_model.add(key1)

        # T4: Exact SHA-256 of image file
        if img_path:
            sha = file_sha256(img_path)
            if sha:
                if sha in seen_sha256:
                    dup_count += 1
                    continue
                seen_sha256[sha] = raw_id

        # T3: Perceptual dHash <= 5
        if img_path:
            if img_rel not in img_cache:
                img_cache[img_rel] = dhash(img_path)
            dh = img_cache[img_rel]
            if dh is not None:
                # R1: Multi-attribute Cover Purge check (Perceptual dHash <= 2 against 335 covers)
                if is_catalogue_cover(rec, cover_dhashes=cover_dhashes, img_dh=dh):
                    dup_count += 1
                    continue

                is_dup = False
                for (existing_hash, _) in seen_dhash:
                    if hamming(dh, existing_hash) <= 5:
                        is_dup = True
                        break
                if is_dup:
                    dup_count += 1
                    continue
                seen_dhash.append((dh, raw_id))

        # T2: Title tokens Jaccard >= 0.85 within brand
        tokens = tokenize(title)
        if tokens and brand:
            is_dup = False
            for (existing_tokens, _) in seen_tokens[brand]:
                if jaccard(tokens, existing_tokens) >= 0.85:
                    is_dup = True
                    break
            if is_dup:
                dup_count += 1
                continue
            seen_tokens[brand].append((tokens, raw_id))

        # Keep record
        unique_partner.append(rec)

    print(f"\n      Partner deduplication complete:")
    print(f"      Raw: {total:,} | Redundant: {dup_count:,} | Unique: {len(unique_partner):,}")

    # 4. Standardize partner records
    partner_clean: list[dict] = []
    cat_counts: dict[str, int] = collections.defaultdict(int)

    for idx, rec in enumerate(unique_partner, 1):
        brand = (rec.get("brand", "") or "").strip() or "Partner Brand"
        title = clean_title(rec.get("title", "") or "Corporate Gift")
        raw_cat = rec.get("category", "") or ""
        img_rel = rec.get("image_path", "") or ""
        slug = raw_cat_to_slug(raw_cat, title, brand)
        img_url = img_rel.replace("raw images/", "raw%20images/").replace("\\", "/")

        entry = {
            "id": f"sp_prod_{idx:05d}",
            "name": title,
            "title": title,
            "model": (rec.get("model_number", "") or "").strip(),
            "brand": brand,
            "category": slug,
            "category_slug": slug,
            "category_name": SLUG_MAP[slug],
            "type": "partner_product",
            "image": img_url,
            "image_path": img_url,
            "description": (rec.get("description", "") or "").strip(),
            "source": rec.get("source_pdf", "") or "",
        }
        partner_clean.append(entry)
        cat_counts[slug] += 1

    # Merge: In-house + Partner
    full_catalog = inhouse_items + partner_clean
    print(f"\n[4/5] Consolidated Catalog:")
    print(f"      In-House Items   : {len(inhouse_items):,}")
    print(f"      Partner Products : {len(partner_clean):,}")
    print(f"      Total Products   : {len(full_catalog):,}")

    # 5. Output products.json and catalog_data.js
    print(f"\n[5/5] Writing deliverables …")
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(full_catalog, f, ensure_ascii=False, indent=2)
    print(f"      Saved {OUT_JSON.name} ({OUT_JSON.stat().st_size / 1024:.0f} KB)")

    js_header = "// Authoritative Sterling Prime Corporate Gifting Catalog Data\n"
    js_header += f"// Generated: {len(full_catalog):,} products ({len(inhouse_items):,} in-house + {len(partner_clean):,} partner)\n"
    js_content = js_header + "window.CATALOG_DATA = " + json.dumps(full_catalog, ensure_ascii=False, separators=(",", ":")) + ";\n"

    with open(OUT_JS, "w", encoding="utf-8") as f:
        f.write(js_content)
    print(f"      Saved {OUT_JS.name} ({OUT_JS.stat().st_size / 1024:.0f} KB)")

    print(f"\n{'='*65}")
    print(f"  DEDUPLICATION COMPLETE: {len(full_catalog):,} total products ready")
    print(f"{'='*65}\n")

if __name__ == "__main__":
    main()
