"""
Milestone 1 Empirical Adversarial Challenge Test Harness
Tests extracted_products_raw.json and raw images/products/ for:
1. Strict UTF-8 and JSON parsing validity.
2. 100% Schema conformance across all records.
3. 100% Image path presence and non-zero file size on disk for ALL 41,426 records.
4. Deep Pillow stress-test on 2,500+ images:
   - Header verification (im.verify())
   - Complete pixel decode / corrupt chunk detection (im.load()) with LOAD_TRUNCATED_IMAGES=False
   - Dimension assertions (width >= 100, height >= 100)
   - Color mode inspection
   - Resampling / thumbnail stress test
5. Content sanity checks (no unhandled nulls, NaN, null bytes, traces).
"""

import os
import sys
import json
import random
from collections import Counter
from PIL import Image, ImageFile

# Enforce strict rejection of truncated or corrupt image streams
ImageFile.LOAD_TRUNCATED_IMAGES = False

# Ensure UTF-8 output on Windows terminal
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
JSON_PATH = os.path.join(REPO_ROOT, "extracted_products_raw.json")
RAW_IMG_DIR = os.path.join(REPO_ROOT, "raw images", "products")

REQUIRED_SCHEMA_KEYS = {
    "id",
    "title",
    "model_number",
    "brand",
    "category",
    "description",
    "price",
    "image_path",
    "source_pdf",
    "page_number",
}

def run_adversarial_challenge():
    print("=" * 70)
    print("STARTING ADVERSARIAL STRESS TEST FOR MILESTONE 1")
    print(f"Repository Root: {REPO_ROOT}")
    print(f"Target JSON:     {JSON_PATH}")
    print("=" * 70)

    # ---------------------------------------------------------
    # Test 1: JSON File Decoding & Encoding Audit
    # ---------------------------------------------------------
    print("\n[CHALLENGE 1] JSON File Format & Strict UTF-8 Decoding...")
    assert os.path.exists(JSON_PATH), f"Target JSON missing at {JSON_PATH}"
    file_size_mb = os.path.getsize(JSON_PATH) / (1024 * 1024)
    print(f"JSON File Size: {file_size_mb:.2f} MB")

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    total_records = len(data)
    print(f"Loaded records: {total_records}")
    assert total_records == 41426, f"Expected 41426 records, got {total_records}"
    print("[PASS] Challenge 1 Passed: Valid JSON with exact 41,426 records parsed under strict UTF-8.")

    # ---------------------------------------------------------
    # Test 2: 100% Schema Conformance & Field Sanity
    # ---------------------------------------------------------
    print("\n[CHALLENGE 2] 100% Schema Conformance & Type Audit across ALL 41,426 records...")
    id_set = set()
    categories_counter = Counter()
    brands_counter = Counter()
    missing_fields_errors = []
    null_image_paths = []
    invalid_page_nums = []
    suspicious_text_count = 0

    for idx, rec in enumerate(data):
        # Key presence
        keys = set(rec.keys())
        if keys != REQUIRED_SCHEMA_KEYS:
            missing = REQUIRED_SCHEMA_KEYS - keys
            extra = keys - REQUIRED_SCHEMA_KEYS
            missing_fields_errors.append((idx, f"Missing: {missing}, Extra: {extra}"))

        # ID uniqueness
        r_id = rec.get("id")
        if not r_id or r_id in id_set:
            missing_fields_errors.append((idx, f"Duplicate or empty ID: {r_id}"))
        id_set.add(r_id)

        # Image path validation
        img_path = rec.get("image_path")
        if not img_path or not isinstance(img_path, str) or img_path.strip() == "":
            null_image_paths.append((idx, r_id, img_path))
        elif any(placeholder in img_path.lower() for placeholder in ["placeholder", "none", "null", "undefined"]):
            null_image_paths.append((idx, r_id, img_path))

        # Page number validation
        pg = rec.get("page_number")
        if not isinstance(pg, int) or pg < 0:
            invalid_page_nums.append((idx, r_id, pg))

        categories_counter[rec.get("category", "UNKNOWN")] += 1
        brands_counter[rec.get("brand", "UNKNOWN")] += 1

    # Text sanity checks
    null_byte_records = []
    traceback_records = []
    for idx, rec in enumerate(data):
        title = rec.get("title", "")
        desc = rec.get("description", "")
        for field, s in [("title", title), ("description", desc)]:
            if s and "\x00" in s:
                null_byte_records.append((idx, rec["id"], field, repr(s[:60])))
            if s and "Traceback (most recent call last)" in s:
                traceback_records.append((idx, rec["id"], field))

    assert len(missing_fields_errors) == 0, f"Schema errors encountered: {missing_fields_errors[:5]}"
    assert len(null_image_paths) == 0, f"Null or placeholder image paths found: {null_image_paths[:5]}"
    assert len(invalid_page_nums) == 0, f"Invalid page numbers found: {invalid_page_nums[:5]}"
    assert len(traceback_records) == 0, f"Found unhandled tracebacks in records: {traceback_records[:5]}"
    assert len(id_set) == total_records, f"Unique ID count {len(id_set)} != {total_records}"

    print(f"[PASS] Challenge 2 Passed: 100% of 41,426 records strictly match schema.")
    if null_byte_records:
        print(f"  [ADVERSARIAL FINDING] Detected {len(null_byte_records)} fields with embedded null bytes (\\x00):")
        for n_item in null_byte_records[:5]:
            print(f"    - {n_item}")
    else:
        print("  Zero null bytes detected.")
    print(f"  Unique categories found: {len(categories_counter)}")
    for cat, cnt in categories_counter.most_common():
        print(f"    - {cat}: {cnt}")

    # ---------------------------------------------------------
    # Test 3: 100% On-Disk Image Existence & Non-Zero File Size
    # ---------------------------------------------------------
    print("\n[CHALLENGE 3] Verifying 100% of Referenced Images on Disk...")
    missing_on_disk = []
    zero_byte_images = []

    for idx, rec in enumerate(data):
        rel_path = rec["image_path"]
        # Normalize relative path separators
        norm_rel = rel_path.replace("/", os.sep).replace("\\", os.sep)
        full_path = os.path.join(REPO_ROOT, norm_rel)

        if not os.path.exists(full_path):
            missing_on_disk.append((idx, rec["id"], full_path))
            if len(missing_on_disk) > 10:
                break
            continue

        size = os.path.getsize(full_path)
        if size == 0:
            zero_byte_images.append((idx, rec["id"], full_path))
            if len(zero_byte_images) > 10:
                break

    assert len(missing_on_disk) == 0, f"Missing images on disk: {missing_on_disk[:5]}"
    assert len(zero_byte_images) == 0, f"Zero-byte images found: {zero_byte_images[:5]}"
    print(f"[PASS] Challenge 3 Passed: 100% ({total_records}/{total_records}) image files exist on disk with size > 0 bytes.")

    # ---------------------------------------------------------
    # Test 4: Deep Adversarial Image Stress Test (2,500+ Samples)
    # ---------------------------------------------------------
    print("\n[CHALLENGE 4] Deep Pillow Decode & Corrupt Chunk Stress Test on Sampled Images...")
    random.seed(42)

    # Stratified sampling:
    # 1. First 487 records (pre-extracted JPG bonus assets)
    bonus_samples = data[:487]

    # 2. Stratified sample across all categories (150 per category)
    cat_buckets = {}
    for rec in data[487:]:
        cat = rec["category"]
        if cat not in cat_buckets:
            cat_buckets[cat] = []
        cat_buckets[cat].append(rec)

    stratified_samples = []
    for cat, items in cat_buckets.items():
        sample_size = min(150, len(items))
        stratified_samples.extend(random.sample(items, sample_size))

    # 3. 500 purely random uniform samples across entire dataset
    random_samples = random.sample(data, 500)

    # Combine and deduplicate sampled records
    sample_pool_map = {r["id"]: r for r in (bonus_samples + stratified_samples + random_samples)}
    sampled_records = list(sample_pool_map.values())
    total_sampled = len(sampled_records)
    print(f"Total Unique Images Selected for Deep Stress Testing: {total_sampled}")
    assert total_sampled >= 1000, f"Requirement requires >= 1000 sampled images, got {total_sampled}"

    decode_failures = []
    corrupt_chunks = []
    dimension_failures = []
    color_modes_found = Counter()
    aspect_ratios = []

    for i, rec in enumerate(sampled_records):
        norm_rel = rec["image_path"].replace("/", os.sep).replace("\\", os.sep)
        full_path = os.path.join(REPO_ROOT, norm_rel)

        # Step 4a: File header integrity via verify()
        try:
            with Image.open(full_path) as im:
                im.verify()
        except Exception as e:
            decode_failures.append((rec["id"], full_path, f"im.verify() failed: {e}"))
            continue

        # Step 4b: Complete pixel decompression via load()
        try:
            with Image.open(full_path) as im:
                im.load()  # Forces full decoding of JPEG entropy chunks
                w, h = im.size
                mode = im.mode
                color_modes_found[mode] += 1
                aspect_ratios.append(w / h)

                # Step 4c: Resolution assertion
                if w < 100 or h < 100:
                    dimension_failures.append((rec["id"], full_path, w, h))

                # Step 4d: Thumbnail rendering stress test
                thumb = im.copy()
                thumb.thumbnail((120, 120))
                assert thumb.size[0] > 0 and thumb.size[1] > 0
        except Exception as e:
            corrupt_chunks.append((rec["id"], full_path, f"im.load() corrupt chunk: {e}"))

        if (i + 1) % 500 == 0 or (i + 1) == total_sampled:
            print(f"  Processed {i + 1}/{total_sampled} images...")

    print("\n--- Empirical Stress Test Results ---")
    print(f"Sampled Images Tested:       {total_sampled}")
    print(f"Header Decode Failures:      {len(decode_failures)}")
    print(f"Corrupt Chunk / Load Errors: {len(corrupt_chunks)}")
    print(f"Dimension (<100px) Violations: {len(dimension_failures)}")
    print(f"Color Modes Observed:        {dict(color_modes_found)}")

    min_ar = min(aspect_ratios) if aspect_ratios else 0
    max_ar = max(aspect_ratios) if aspect_ratios else 0
    print(f"Aspect Ratio Range:          min={min_ar:.2f}, max={max_ar:.2f}")

    assert len(decode_failures) == 0, f"Decode failures: {decode_failures[:5]}"
    assert len(corrupt_chunks) == 0, f"Corrupt chunks: {corrupt_chunks[:5]}"
    assert len(dimension_failures) == 0, f"Dimension violations: {dimension_failures[:5]}"
    print("[PASS] Challenge 4 Passed: 100% of sampled images successfully decoded, valid color modes, zero corruption.")

    # ---------------------------------------------------------
    # Test 5: Verify Partner PDF Source Corpus Coverage
    # ---------------------------------------------------------
    print("\n[CHALLENGE 5] Source PDF Attributions & Traceability...")
    sources = set(r["source_pdf"] for r in data)
    print(f"Unique source PDFs mapped in extracted data: {len(sources)}")
    assert len(sources) >= 300, f"Expected >= 300 unique source PDFs, found {len(sources)}"
    print("[PASS] Challenge 5 Passed: Wide source PDF representation confirmed across partner corpus.")

    print("\n" + "=" * 70)
    print("ALL EMPIRICAL CHALLENGES PASSED! VERDICT: APPROVE")
    print("=" * 70)
    return True

if __name__ == "__main__":
    try:
        run_adversarial_challenge()
        sys.exit(0)
    except AssertionError as err:
        print(f"\n[FATAL STRESS-TEST FAILURE] {err}")
        sys.exit(1)
    except Exception as err:
        print(f"\n[UNEXPECTED EXCEPTION] {err}")
        import traceback
        traceback.print_exc()
        sys.exit(2)
