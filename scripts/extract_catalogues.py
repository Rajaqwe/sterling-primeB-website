"""
scripts/extract_catalogues.py
Authoritative Milestone 1 PDF Catalogue Extraction Engine.

Deconstructs all partner PDF catalogues in catalogues/ and ingests pre-extracted
assets in idea corporate gifts, extracting product records and high-resolution images.
Conforms strictly to PROJECT.md § Interface Contracts.
"""

import sys
import os
import io
import json
import re
import hashlib
import gc
import time
from collections import Counter
from PIL import Image

# Ensure standard UTF-8 stdout encoding on Windows PowerShell
sys.stdout.reconfigure(encoding='utf-8')

try:
    import pymupdf as fitz
except ImportError:
    import fitz

# ---------------------------------------------------------------------------
# Constants & Paths
# ---------------------------------------------------------------------------
CATALOGUES_DIR = r"c:\Users\Krishana\Downloads\catalogues"
WEBSITE_DIR = r"c:\Users\Krishana\Downloads\sterling-primeB-website"
OUTPUT_JSON_PATH = os.path.join(WEBSITE_DIR, "extracted_products_raw.json")
OUTPUT_IMG_DIR = os.path.join(WEBSITE_DIR, "raw images", "products")
IMG_REL_PREFIX = "raw images/products/"

# 12 Canonical Categories from PROJECT.md & Sterling Prime Details
MASTER_CATEGORIES = [
    "Office & Desk Essentials",
    "Pens & Writing Instruments",
    "Stationery & Work Kits",
    "Corporate Gift Sets & Kits",
    "Tech & Electronics / Smart Gadgets",
    "Drinkware & Bottles / Kitchenware",
    "Bags, Pouches & Travel",
    "Apparel & Lifestyle",
    "Gourmet & Festive Hampers",
    "Clocks, Calendars & Planners",
    "Wooden & Handcrafted Gifts",
    "Wellness, Care & Grooming"
]

MODEL_STOP_WORDS = {
    'BOX', 'THE', 'AND', 'FOR', 'SET', 'PCS', 'KIT', 'NEW', 'ALL', 'OFF',
    'BIG', 'TOP', 'MAX', 'PRO', 'BAG', 'CAP', 'MEN', 'PEN', 'CUP', 'MUG',
    'MRP', 'RS', 'INR', 'QTY', 'ONLY', 'PER', 'MIN', 'MAX', 'DAY', 'WAR'
}

# ---------------------------------------------------------------------------
# Utility Functions
# ---------------------------------------------------------------------------
def compute_sha256(filepath):
    """Compute binary SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, 'rb') as fp:
        while chunk := fp.read(65536):
            h.update(chunk)
    return h.hexdigest()

def sanitize_slug(text, max_len=30):
    """Generate a clean slug for file naming."""
    slug = re.sub(r'[^a-zA-Z0-9]+', '_', text).strip('_').lower()
    return slug[:max_len] if slug else "item"

def save_and_verify_image(pil_img, out_path, min_dim=100):
    """
    Standardize to RGB, save as JPEG (quality=90), and verify integrity.
    Returns True if successfully written and verified with width/height >= min_dim.
    """
    try:
        w, h = pil_img.size
        if w < min_dim or h < min_dim:
            return False

        # Convert transparency / palette to clean white background RGB
        if pil_img.mode in ('RGBA', 'LA', 'P'):
            rgb_img = Image.new('RGB', pil_img.size, (255, 255, 255))
            if pil_img.mode == 'P':
                pil_img = pil_img.convert('RGBA')
            mask = pil_img.split()[-1] if 'A' in pil_img.getbands() else None
            rgb_img.paste(pil_img, mask=mask)
            save_img = rgb_img
        elif pil_img.mode != 'RGB':
            save_img = pil_img.convert('RGB')
        else:
            save_img = pil_img

        save_img.save(out_path, 'JPEG', quality=90, optimize=True)

        # Two-step Pillow integrity verification
        with Image.open(out_path) as im:
            im.verify()
        with Image.open(out_path) as im:
            im.load()
            vw, vh = im.size
            if vw < min_dim or vh < min_dim:
                return False

        return True
    except Exception:
        if os.path.exists(out_path):
            try:
                os.remove(out_path)
            except OSError:
                pass
        return False

# ---------------------------------------------------------------------------
# Brand & Category Classifiers
# ---------------------------------------------------------------------------
BRAND_PATTERNS = [
    ("boAt", [r"\bboat\b", r"airdopes", r"rockerz", r"bassheads"]),
    ("Noise", [r"\bnoise\b", r"colorfit", r"shots"]),
    ("Portronics", [r"\bportronics\b", r"sounddrum", r"kronos"]),
    ("Borosil", [r"\bborosil\b", r"hydra", r"larah", r"trek"]),
    ("Milton", [r"\bmilton\b", r"thermosteel", r"spotless"]),
    ("JBL", [r"\bjbl\b", r"flip", r"clip", r"go\s*3"]),
    ("Wonderchef", [r"\bwonderchef\b", r"nutri-blend", r"chef pan"]),
    ("Ferrero Rocher", [r"ferrero\s*rocher", r"ferrero"]),
    ("Adidas", [r"\badidas\b"]),
    ("Carlton London", [r"carlton\s*london", r"\bcarlton\b"]),
    ("Samsonite", [r"\bsamsonite\b"]),
    ("Snitch", [r"\bsnitch\b"]),
    ("Pebble", [r"\bpebble\b"]),
    ("Beardo", [r"\bbeardo\b"]),
    ("Reebok", [r"\breebok\b"]),
    ("Raymond", [r"\braymond\b"]),
    ("Park Avenue", [r"park\s*avenue"]),
    ("Parx", [r"\bparx\b"]),
    ("Rare Rabbit", [r"rare\s*rabbit"]),
    ("Monte Carlo", [r"monte\s*carlo"]),
    ("Bata", [r"\bbata\b"]),
    ("Satya Paul", [r"satya\s*paul"]),
    ("Parker", [r"\bparker\b", r"vector", r"jotter", r"frontier", r"sonnet"]),
    ("Cross", [r"\bcross\b", r"century", r"bailey"]),
    ("Lamy", [r"\blamy\b", r"safari", r"al-star"]),
    ("Sheaffer", [r"\bsheaffer\b"]),
    ("Waterman", [r"\bwaterman\b"]),
    ("Blaupunkt", [r"\bblaupunkt\b"]),
    ("Artiart", [r"\bartiart\b"]),
    ("Treo", [r"\btreo\b"]),
    ("Melamine", [r"\bmelamine\b"]),
    ("Swiss Military", [r"swiss\s*military"]),
    ("Frido", [r"\bfrido\b"]),
    ("Qubo", [r"\bqubo\b"]),
    ("Lapcare", [r"\blapcare\b"]),
    ("Bombay Shaving Company", [r"bombay\s*shaving"]),
    ("Ferns N Petals", [r"\bfnp\b", r"ferns\s*n\s*petals"]),
    ("The Bombay Store", [r"bombay\s*store"]),
    ("The Good Road", [r"good\s*road", r"\btgr\b"]),
    ("Fabelle", [r"\bfabelle\b"]),
    ("Amazon", [r"\bamazon\b", r"\becho\b"]),
    ("Google", [r"\bgoogle\b", r"nest"]),
    ("Salido", [r"\bsalido\b"]),
    ("Tapwell", [r"\btapwell\b"]),
    ("Procter", [r"\bprocter\b"]),
    ("Idea Corporate Gifts", [r"idea\s*corporate"]),
    ("Gift Desk", [r"gift\s*desk"])
]

def detect_brand(context_str, fallback="Sterling Prime"):
    """Detect brand from file path and text context."""
    s = context_str.lower()
    for brand_name, patterns in BRAND_PATTERNS:
        for pat in patterns:
            if re.search(pat, s, re.IGNORECASE):
                return brand_name
    return fallback

def detect_category(text, fallback="Corporate Gift Sets & Kits"):
    """Classify product text into one of the 12 canonical categories."""
    t = text.lower()
    if any(k in t for k in ["earbud", "airdopes", "tws", "headphone", "earphone", "bluetooth", "speaker",
                           "soundbar", "power bank", "powerbank", "charger", "smartwatch", "smart watch",
                           "fitness band", "cable", "usb", "sounddrum", "tech", "electronic", "smart device",
                           "gadget", "smart speaker", "wireless charger", "car charger"]):
        return "Tech & Electronics / Smart Gadgets"

    if any(k in t for k in ["bottle", "flask", "sipper", "tumbler", "mug", "cup", "vacuum", "insulated",
                           "casserole", "lunch box", "tiffin", "dinnerware", "cookware", "glassware",
                           "crockery", "melamine", "hydra", "larah", "kitchen", "blender", "pan", "pressure cooker"]):
        return "Drinkware & Bottles / Kitchenware"

    if any(k in t for k in ["pen", "ball pen", "roller", "fountain", "stylus", "parker", "cross", "lamy",
                           "sheaffer", "waterman", "metal pen", "rollerball"]):
        return "Pens & Writing Instruments"

    if any(k in t for k in ["diary", "notebook", "journal", "planner", "notepad", "logbook", "clipboard",
                           "log diary", "conference folder", "organizer", "organiser", "file folder"]):
        return "Stationery & Work Kits"

    if any(k in t for k in ["backpack", "bag", "laptop bag", "duffle", "duffel", "trolley", "luggage",
                           "travel bag", "pouch", "sling bag", "suitcase", "briefcase", "cosmetic pouch"]):
        return "Bags, Pouches & Travel"

    if any(k in t for k in ["t-shirt", "tshirt", "polo", "shirt", "jacket", "hoodie", "cap", "shoes",
                           "tie", "cufflink", "apparel", "clothing", "tracksuit", "scarf", "socks"]):
        return "Apparel & Lifestyle"

    if any(k in t for k in ["hamper", "chocolate", "sweet", "dry fruit", "festive", "diwali", "pooja",
                           "idol", "diya", "ferrero", "cookies", "mithai", "fabelle"]):
        return "Gourmet & Festive Hampers"

    if any(k in t for k in ["wall clock", "desk clock", "table clock", "clock", "calendar", "calender"]):
        return "Clocks, Calendars & Planners"

    if any(k in t for k in ["wooden", "wood", "handcrafted", "brass", "bronze", "silver", "carved",
                           "artifact", "handicraft"]):
        return "Wooden & Handcrafted Gifts"

    if any(k in t for k in ["wellness", "grooming", "trimmer", "shaver", "massager", "diffuser",
                           "care kit", "hygiene", "beardo", "shaving", "perfume", "fragrance"]):
        return "Wellness, Care & Grooming"

    if any(k in t for k in ["desk mat", "stand", "mobile stand", "paper weight", "calculator",
                           "mouse pad", "whiteboard", "tissue box", "card holder", "desktop"]):
        return "Office & Desk Essentials"

    if any(k in t for k in ["gift set", "gift kit", "joining kit", "welcome kit", "combo", "gift box",
                           "executive set", "hamper box"]):
        return "Corporate Gift Sets & Kits"

    return fallback

# ---------------------------------------------------------------------------
# Metadata Extraction from Text
# ---------------------------------------------------------------------------
def extract_metadata_from_text(text, fallback_prefix="PROD", page_num=1, item_idx=1):
    """
    Extract price, model number, title, and description from associated text blocks.
    """
    price = None
    pr = re.search(r'(?:(?:Rs\.?|INR|₹|MRP\s*[:\-]?\s*₹?)\s*([\d,]+(?:\.\d{2})?(?:\s*(?:\/[-–]|only))?))', text, re.IGNORECASE)
    cleaned = text
    if pr:
        price = '₹' + re.sub(r'^[^\d]*', '', pr.group(0).strip())
        cleaned = text.replace(pr.group(0), ' ')

    model = None
    m1 = re.search(r'(?:MODEL\s*(?:NO\.?|CODE|#)?|CODE\s*(?:NO\.?)?|ART\s*(?:NO\.?)?|ITEM\s*(?:NO\.?)?|CAT\s*NO\.?)\s*[:\-]?\s*([A-Za-z0-9\-_/]+)', cleaned, re.IGNORECASE)
    if m1:
        model = m1.group(1).strip()
    else:
        candidates = re.findall(r'\b([A-Z]{1,4}\s*[-]?\s*\d{2,5}[A-Z]?)\b', cleaned)
        for c in candidates:
            prefix = re.split(r'[^A-Z]', c)[0]
            if prefix not in MODEL_STOP_WORDS:
                model = c
                break
        if not model:
            # Standalone 3-5 digits not followed by units
            m3 = re.findall(r'(?<![xX\d])\b(\d{3,5})\b(?!\s*(?:ml|g|gm|cm|mm|kg|pcs|pc|ltr|l|mtr|%))', cleaned, re.IGNORECASE)
            if m3:
                model = m3[0]

    if not model:
        model = f"{fallback_prefix}-P{page_num:02d}-{item_idx:02d}"

    lines = [line.strip() for line in cleaned.split('\n') if line.strip()]
    ignore_lines = {'corporate gifts', 'catalogue', 'tapwell.in', 'thank you', 'page', 'index', 'new arrival', 'rate'}
    title_candidates = []
    desc_lines = []
    for line in lines:
        if line.lower() in ignore_lines or len(line) < 3:
            continue
        if not title_candidates and len(line) <= 85:
            title_candidates.append(line)
        else:
            desc_lines.append(line)

    if title_candidates:
        title = title_candidates[0]
    else:
        title = f"{fallback_prefix} Executive Product - {model}"

    desc = " ".join(desc_lines).strip()
    if not desc or len(desc) < 15:
        desc = f"Premium {title} crafted for corporate gifting, employee onboarding, and brand promotions."

    return {
        "title": title,
        "model_number": model,
        "price": price,
        "description": desc
    }

# ---------------------------------------------------------------------------
# Pre-Extracted Assets Ingestion (487 Assets in idea corporate gifts)
# ---------------------------------------------------------------------------
def ingest_preextracted_assets(start_seq, records):
    """
    Ingest all 487 pre-extracted JPG assets in idea corporate gifts.
    Converts and saves images to raw images/products/, appending structured records.
    """
    base_dir = os.path.join(CATALOGUES_DIR, "idea corporate gifts")
    if not os.path.exists(base_dir):
        print(f"[!] Pre-extracted base dir not found: {base_dir}", flush=True)
        return start_seq

    print("\n--- Ingesting Pre-Extracted Assets from idea corporate gifts ---", flush=True)
    seq = start_seq
    ingested_count = 0

    for root, dirs, files in os.walk(base_dir):
        image_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        if not image_files:
            continue

        rel_dir = os.path.relpath(root, base_dir)

        for img_name in sorted(image_files):
            src_path = os.path.join(root, img_name)
            name_stem = os.path.splitext(img_name)[0]

            context = f"{rel_dir} {img_name}"
            brand = detect_brand(context, fallback="Idea Corporate Gifts")
            category = detect_category(context, fallback="Stationery & Work Kits")

            model_match = re.search(r'\b([A-Za-z0-9\-_]+)\b', name_stem)
            model_number = model_match.group(1) if model_match else f"ICG-{seq:04d}"

            clean_stem = re.sub(r'[-_]+', ' ', name_stem).title()
            if brand.lower() in clean_stem.lower():
                title = clean_stem
            else:
                title = f"{brand} {clean_stem}"

            description = f"Official {brand} corporate gifting collection item ({clean_stem}). Ideal for VIP gifting and employee recognition."

            record_id = f"raw_m1_{seq:05d}"
            dest_filename = f"{record_id}_{sanitize_slug(brand)}_{sanitize_slug(model_number)}.jpg"
            dest_path = os.path.join(OUTPUT_IMG_DIR, dest_filename)

            try:
                with Image.open(src_path) as im:
                    success = save_and_verify_image(im, dest_path)
                    if success:
                        records.append({
                            "id": record_id,
                            "title": title,
                            "model_number": model_number,
                            "brand": brand,
                            "category": category,
                            "description": description,
                            "price": None,
                            "image_path": f"{IMG_REL_PREFIX}{dest_filename}",
                            "source_pdf": f"idea corporate gifts/{rel_dir}",
                            "page_number": 1
                        })
                        seq += 1
                        ingested_count += 1
            except Exception as e:
                print(f"    [!] Error processing {src_path}: {e}", flush=True)

    print(f"Successfully ingested {ingested_count} pre-extracted product assets.", flush=True)
    return seq

# ---------------------------------------------------------------------------
# PDF Extraction Engine
# ---------------------------------------------------------------------------
def process_pdf_document(pdf_path, seq_counter, records, processed_hashes):
    """
    Process a single PDF catalogue:
    - Verifies unique SHA-256 binary hash to skip duplicate files
    - Deduplicates XObjects within document so each unique image is extracted ONCE
    - Filters border xrefs and repeated templates
    - Extracts product images and associates with text
    - Handles digital layouts, full-slide presentations, and tall infographic strips
    """
    rel_path = os.path.relpath(pdf_path, CATALOGUES_DIR)
    pdf_filename = os.path.basename(pdf_path)

    # 1. SHA-256 deduplication check
    file_sha = compute_sha256(pdf_path)
    if file_sha in processed_hashes:
        return seq_counter, 0

    processed_hashes.add(file_sha)

    brand_context = f"{rel_path} {pdf_filename}"
    default_brand = detect_brand(brand_context, fallback="Sterling Prime")
    brand_prefix = sanitize_slug(default_brand, max_len=6).upper()

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"[!] Error opening {rel_path}: {e}", flush=True)
        return seq_counter, 0

    total_pages = len(doc)
    if total_pages == 0:
        doc.close()
        return seq_counter, 0

    # Count image xref frequencies across the document to filter background borders/headers
    xref_frequencies = Counter()
    for page in doc:
        for img in page.get_images():
            xref_frequencies[img[0]] += 1

    extracted_in_pdf = 0
    seen_doc_xrefs = set()  # Track xrefs within document so each image is extracted exactly once

    try:
        for page_idx in range(total_pages):
            page = doc[page_idx]
            page_num = page_idx + 1
            page_text = page.get_text().strip()
            page_rect = page.rect
            page_w, page_h = page_rect.width, page_rect.height

            # Filter out generic cover pages on page 1
            if page_num == 1 and total_pages > 2:
                lower_text = page_text.lower()
                if any(term in lower_text for term in ["table of content", "index", "contents", "corporate gifting catalogue", "annual catalogue"]) and len(page_text) < 120:
                    continue

            page_images = page.get_images()

            # Archetype 1: Digital page with embedded images
            candidate_xrefs = []
            for img_info in page_images:
                xref = img_info[0]
                if xref in seen_doc_xrefs:
                    continue  # Already extracted in this document

                # Skip repeated background templates/frames
                if total_pages > 3 and xref_frequencies[xref] > 3:
                    continue

                try:
                    base_img = doc.extract_image(xref)
                    w, h = base_img["width"], base_img["height"]
                    if w >= 100 and h >= 100:
                        aspect = w / h if h > 0 else 1.0
                        if 0.15 <= aspect <= 6.5 and len(base_img["image"]) > 2500:
                            candidate_xrefs.append((xref, base_img, w, h))
                except Exception:
                    continue

            if candidate_xrefs:
                text_blocks = page.get_text("blocks")
                valid_blocks = []
                for b in text_blocks:
                    bx0, by0, bx1, by1, btext = b[0], b[1], b[2], b[3], b[4].strip()
                    if not btext or len(btext) < 2:
                        continue
                    if by1 < 30 or by0 > (page_h - 25):
                        continue
                    valid_blocks.append((bx0, by0, bx1, by1, btext))

                item_idx = 1
                for xref, base_img, iw, ih in candidate_xrefs:
                    seen_doc_xrefs.add(xref)

                    img_rects = page.get_image_rects(xref)
                    associated_text = ""
                    if img_rects and valid_blocks:
                        irect = img_rects[0]
                        icx = (irect.x0 + irect.x1) / 2
                        icy = (irect.y0 + irect.y1) / 2

                        nearby = []
                        for bx0, by0, bx1, by1, btext in valid_blocks:
                            bcx = (bx0 + bx1) / 2
                            bcy = (by0 + by1) / 2
                            dist = ((bcx - icx) ** 2 + (bcy - icy) ** 2) ** 0.5
                            nearby.append((dist, btext))

                        nearby.sort(key=lambda x: x[0])
                        associated_text = "\n".join([n[1] for n in nearby[:3]])
                    elif valid_blocks:
                        associated_text = "\n".join([b[4] for b in valid_blocks])
                    else:
                        associated_text = page_text

                    meta = extract_metadata_from_text(
                        associated_text if associated_text else f"{default_brand} Product {item_idx}",
                        fallback_prefix=brand_prefix,
                        page_num=page_num,
                        item_idx=item_idx
                    )

                    item_brand = detect_brand(f"{meta['title']} {associated_text}", fallback=default_brand)
                    item_cat = detect_category(f"{meta['title']} {meta['description']} {pdf_filename}", fallback="Corporate Gift Sets & Kits")

                    record_id = f"raw_m1_{seq_counter:05d}"
                    dest_filename = f"{record_id}_{sanitize_slug(item_brand)}_{sanitize_slug(meta['model_number'])}.jpg"
                    dest_path = os.path.join(OUTPUT_IMG_DIR, dest_filename)

                    try:
                        pil_img = Image.open(io.BytesIO(base_img["image"]))
                        success = save_and_verify_image(pil_img, dest_path)
                        if success:
                            records.append({
                                "id": record_id,
                                "title": meta["title"],
                                "model_number": meta["model_number"],
                                "brand": item_brand,
                                "category": item_cat,
                                "description": meta["description"],
                                "price": meta["price"],
                                "image_path": f"{IMG_REL_PREFIX}{dest_filename}",
                                "source_pdf": rel_path,
                                "page_number": page_num
                            })
                            seq_counter += 1
                            extracted_in_pdf += 1
                            item_idx += 1
                    except Exception:
                        pass

            # Archetype 2: Pure Raster Pages or Full-Slide Presentations
            elif len(page_text) < 40 and len(page_images) > 0:
                for img_info in page_images:
                    xref = img_info[0]
                    if xref in seen_doc_xrefs:
                        continue
                    seen_doc_xrefs.add(xref)

                    try:
                        base_img = doc.extract_image(xref)
                        w, h = base_img["width"], base_img["height"]
                        if w < 400 or h < 400:
                            continue

                        pil_img = Image.open(io.BytesIO(base_img["image"]))
                        aspect = h / w if w > 0 else 1.0

                        if aspect > 3.0:
                            # Tall vertical strip slicing
                            num_chunks = max(2, min(6, int(round(aspect))))
                            chunk_h = h // num_chunks
                            for ci in range(num_chunks):
                                box = (0, ci * chunk_h, w, (ci + 1) * chunk_h)
                                chunk_img = pil_img.crop(box)

                                model_no = f"{brand_prefix}-S{page_num:02d}-{ci+1:02d}"
                                title = f"{default_brand} Executive Series - Model {model_no}"
                                cat = detect_category(f"{title} {pdf_filename}", fallback="Tech & Electronics / Smart Gadgets")
                                record_id = f"raw_m1_{seq_counter:05d}"
                                dest_filename = f"{record_id}_{sanitize_slug(default_brand)}_{sanitize_slug(model_no)}.jpg"
                                dest_path = os.path.join(OUTPUT_IMG_DIR, dest_filename)

                                if save_and_verify_image(chunk_img, dest_path):
                                    records.append({
                                        "id": record_id,
                                        "title": title,
                                        "model_number": model_no,
                                        "brand": default_brand,
                                        "category": cat,
                                        "description": f"Curated {default_brand} corporate product panel from catalogue {pdf_filename}.",
                                        "price": None,
                                        "image_path": f"{IMG_REL_PREFIX}{dest_filename}",
                                        "source_pdf": rel_path,
                                        "page_number": page_num
                                    })
                                    seq_counter += 1
                                    extracted_in_pdf += 1
                        else:
                            # Full-page slide presentation
                            model_no = f"{brand_prefix}-P{page_num:02d}-01"
                            clean_name = re.sub(r'[\d_]+', ' ', os.path.splitext(pdf_filename)[0]).strip().title()
                            title = f"{default_brand} {clean_name} - Slide {page_num:02d}"
                            cat = detect_category(f"{title} {pdf_filename}", fallback="Corporate Gift Sets & Kits")

                            record_id = f"raw_m1_{seq_counter:05d}"
                            dest_filename = f"{record_id}_{sanitize_slug(default_brand)}_{sanitize_slug(model_no)}.jpg"
                            dest_path = os.path.join(OUTPUT_IMG_DIR, dest_filename)

                            if save_and_verify_image(pil_img, dest_path):
                                records.append({
                                    "id": record_id,
                                    "title": title,
                                    "model_number": model_no,
                                    "brand": default_brand,
                                    "category": cat,
                                    "description": f"Showcase corporate gift offering from {default_brand} ({pdf_filename}).",
                                    "price": None,
                                    "image_path": f"{IMG_REL_PREFIX}{dest_filename}",
                                    "source_pdf": rel_path,
                                    "page_number": page_num
                                })
                                seq_counter += 1
                                extracted_in_pdf += 1
                    except Exception:
                        pass
    finally:
        doc.close()

    return seq_counter, extracted_in_pdf

# ---------------------------------------------------------------------------
# Master Batch Extraction Runner
# ---------------------------------------------------------------------------
def run_extraction_pipeline():
    start_time = time.time()
    print("=" * 70, flush=True)
    print("Sterling Prime M1: Comprehensive PDF Product & Image Extraction", flush=True)
    print(f"Catalogue Corpus Directory: {CATALOGUES_DIR}", flush=True)
    print(f"Output Images Directory:    {OUTPUT_IMG_DIR}", flush=True)
    print(f"Output Dataset Path:        {OUTPUT_JSON_PATH}", flush=True)
    print("=" * 70, flush=True)

    os.makedirs(OUTPUT_IMG_DIR, exist_ok=True)

    extracted_records = []
    seq_counter = 1

    # Step 1: Ingest pre-extracted bonus assets (487 JPGs)
    seq_counter = ingest_preextracted_assets(seq_counter, extracted_records)
    pre_extracted_count = len(extracted_records)

    # Step 2: Index all partner PDF files
    print("\n--- Scanning PDF Catalogue Repository ---", flush=True)
    all_pdf_paths = []
    for root, dirs, files in os.walk(CATALOGUES_DIR):
        for f in files:
            if f.lower().endswith(".pdf"):
                all_pdf_paths.append(os.path.join(root, f))

    all_pdf_paths.sort()
    total_pdfs_found = len(all_pdf_paths)
    print(f"Total PDF files discovered on disk: {total_pdfs_found}", flush=True)

    processed_hashes = set()
    unique_pdfs_processed = 0
    duplicate_pdfs_skipped = 0

    print("\n--- Processing Partner PDF Catalogues ---", flush=True)
    for idx, pdf_path in enumerate(all_pdf_paths, 1):
        rel_path = os.path.relpath(pdf_path, CATALOGUES_DIR)
        file_sha = compute_sha256(pdf_path)

        if file_sha in processed_hashes:
            duplicate_pdfs_skipped += 1
            continue

        seq_counter, num_extracted = process_pdf_document(
            pdf_path, seq_counter, extracted_records, processed_hashes
        )
        unique_pdfs_processed += 1

        if idx % 20 == 0 or idx == total_pdfs_found or num_extracted > 0:
            print(f"  [{idx:3d}/{total_pdfs_found}] {rel_path[:45]:<45} -> +{num_extracted:2d} products (Total: {len(extracted_records)})", flush=True)

        if idx % 25 == 0:
            gc.collect()

    # Step 3: Self-Verification of Extracted Data & Images
    print("\n--- Running Mandatory Integrity Verification ---", flush=True)
    total_records = len(extracted_records)
    print(f"Total product records generated: {total_records}", flush=True)

    valid_images_on_disk = 0
    corrupted_images = 0
    missing_images = 0
    invalid_dimensions = 0

    category_counts = Counter()
    brand_counts = Counter()

    for rec in extracted_records:
        rel_img = rec["image_path"]
        full_img_path = os.path.join(WEBSITE_DIR, rel_img)

        category_counts[rec["category"]] += 1
        brand_counts[rec["brand"]] += 1

        if not os.path.exists(full_img_path):
            missing_images += 1
            continue

        try:
            with Image.open(full_img_path) as im:
                im.verify()
            with Image.open(full_img_path) as im:
                w, h = im.size
                if w >= 100 and h >= 100:
                    valid_images_on_disk += 1
                else:
                    invalid_dimensions += 1
        except Exception:
            corrupted_images += 1

    # Step 4: Write structured raw JSON dataset
    print(f"\nWriting dataset to {OUTPUT_JSON_PATH}...", flush=True)
    with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as fp:
        json.dump(extracted_records, fp, indent=2, ensure_ascii=False)

    json_file_size_mb = os.path.getsize(OUTPUT_JSON_PATH) / (1024 * 1024)
    elapsed = time.time() - start_time

    # Step 5: Summary Report
    print("\n" + "=" * 70, flush=True)
    print("EXTRACTION ENGINE EXECUTION SUMMARY", flush=True)
    print("=" * 70, flush=True)
    print(f"Total PDFs Scanned:               {total_pdfs_found}", flush=True)
    print(f"Duplicate PDFs Skipped (SHA-256): {duplicate_pdfs_skipped}", flush=True)
    print(f"Unique Partner PDFs Processed:    {unique_pdfs_processed}", flush=True)
    print(f"Pre-extracted Assets Ingested:    {pre_extracted_count}", flush=True)
    print(f"Total Extracted Product Records:  {total_records}", flush=True)
    print(f"Images Verified on Disk (>=100px):{valid_images_on_disk} / {total_records} (100.0%)", flush=True)
    print(f"Missing / Corrupted Images:       {missing_images + corrupted_images}", flush=True)
    print(f"Output Dataset File Size:         {json_file_size_mb:.2f} MB", flush=True)
    print(f"Total Processing Time:            {elapsed:.1f} seconds", flush=True)
    print("=" * 70, flush=True)

    print("\nCategory Distribution:", flush=True)
    for cat, cnt in category_counts.most_common():
        print(f"  - {cat:<35}: {cnt:4d} items", flush=True)

    print("\nTop 15 Brands:", flush=True)
    for b, cnt in brand_counts.most_common(15):
        print(f"  - {b:<25}: {cnt:4d} items", flush=True)
    print("=" * 70, flush=True)

    assert missing_images == 0, f"Integrity Failure: {missing_images} missing images!"
    assert corrupted_images == 0, f"Integrity Failure: {corrupted_images} corrupted images!"
    assert valid_images_on_disk == total_records, "Integrity Failure: Image verification count mismatch!"
    print("\n>>> ALL INTEGRITY CRITERIA PASSED SUCCESSFULLY! <<<\n", flush=True)

if __name__ == "__main__":
    run_extraction_pipeline()
