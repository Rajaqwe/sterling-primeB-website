#!/usr/bin/env python3
"""Run from repo root: python optimize_images.py   (needs: pip install pillow)
1) Converts heavy top-level PNGs in 'raw images/' to WebP and updates references in
   index.html, catalog_data.js and products.json.  2) Shrinks oversized product JPEGs in place
   (max 1000px, quality 82; same file names, nothing else to change)."""
import pathlib, glob
from urllib.parse import quote
from PIL import Image
root = pathlib.Path(__file__).parent; img = root / "raw images"
refs = [root / n for n in ("index.html", "catalog_data.js", "products.json")]
texts = {p: p.read_text(encoding="utf-8") for p in refs}
saved = 0
for f in list(img.glob("*.PNG")) + list(img.glob("*.png")):
    out = f.with_suffix(".webp"); im = Image.open(f); im.thumbnail((1000, 1000))
    im.save(out, "WEBP", quality=82); saved += f.stat().st_size - out.stat().st_size
    old, new = quote(f.name), quote(out.name)
    for p in texts: texts[p] = texts[p].replace(old, new)
for p, t in texts.items(): p.write_text(t, encoding="utf-8")
for f in glob.glob(str(img / "products" / "*")):
    f = pathlib.Path(f)
    if f.suffix.lower() in (".jpg", ".jpeg") and f.stat().st_size > 400_000:
        before = f.stat().st_size; im = Image.open(f).convert("RGB"); im.thumbnail((1000, 1000))
        im.save(f, "JPEG", quality=82, optimize=True); saved += before - f.stat().st_size
print(f"Saved about {saved/1e6:.0f} MB. Old PNGs are kept; delete them once you have checked the site.")
