#!/usr/bin/env python3
"""
Create offline distribution zip archives:
1. sterling-prime-website-complete.zip in repo root
2. sterling-primeB-website-main.zip in parent Downloads folder

Packages:
- index.html
- catalog_data.js
- products.json
- raw images/ (inhouse images + all referenced partner product images)
- scripts/
- tests/
"""

import sys, os, zipfile, json, pathlib

sys.stdout.reconfigure(encoding='utf-8')

ROOT = pathlib.Path(__file__).parent.parent
ZIP_REPO = ROOT / "sterling-prime-website-complete.zip"
ZIP_PARENT = ROOT.parent / "sterling-primeB-website-main.zip"

def create_archive(dest_path: pathlib.Path):
    print(f"Creating archive: {dest_path} …")
    
    # Load referenced images to include
    referenced_images = set()
    if (ROOT / "products.json").exists():
        with open(ROOT / "products.json", encoding="utf-8") as f:
            for p in json.load(f):
                img = p.get("image") or p.get("image_path")
                if img:
                    clean = img.replace("raw%20images/", "raw images/").replace("/", os.sep)
                    referenced_images.add(clean)

    # Core files to always include
    core_files = [
        "index.html",
        "catalog_data.js",
        "products.json",
        ".gitignore",
        "README.md",
    ]

    with zipfile.ZipFile(dest_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        # 1. Add core files
        for fname in core_files:
            fpath = ROOT / fname
            if fpath.exists():
                z.write(fpath, arcname=fname)

        # 2. Add scripts/
        scripts_dir = ROOT / "scripts"
        if scripts_dir.exists():
            for f in scripts_dir.glob("*.py"):
                z.write(f, arcname=f"scripts/{f.name}")

        # 3. Add tests/
        tests_dir = ROOT / "tests"
        if tests_dir.exists():
            for f in tests_dir.glob("*.py"):
                z.write(f, arcname=f"tests/{f.name}")

        # 4. Add raw images root (logos, inhouse images)
        raw_img_dir = ROOT / "raw images"
        if raw_img_dir.exists():
            for f in raw_img_dir.iterdir():
                if f.is_file():
                    z.write(f, arcname=f"raw images/{f.name}")
            
            # Logos subfolder
            logos_dir = raw_img_dir / "sterling company LOGOS"
            if logos_dir.exists():
                for f in logos_dir.glob("*.*"):
                    z.write(f, arcname=f"raw images/sterling company LOGOS/{f.name}")

            # Catalogue covers (Excluded per Requirement R1)
            # covers_dir = raw_img_dir / "catalogue_covers"
            # Excluded from distribution archive

            # 5. Add all referenced partner product images
            products_dir = raw_img_dir / "products"
            if products_dir.exists():
                count = 0
                for img_rel in referenced_images:
                    p = ROOT / img_rel
                    if p.exists() and p.is_file():
                        arc = img_rel.replace("\\", "/")
                        z.write(p, arcname=arc)
                        count += 1
                print(f"   Packaged {count:,} referenced product images")

    size_mb = dest_path.stat().st_size / (1024 * 1024)
    print(f"   Successfully wrote {dest_path.name} ({size_mb:.1f} MB)")

def main():
    print("=" * 60)
    print("Building Offline Complete Distribution Archives")
    print("=" * 60)
    create_archive(ZIP_REPO)
    create_archive(ZIP_PARENT)
    print("=" * 60)
    print("Offline Zip Archives Completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
