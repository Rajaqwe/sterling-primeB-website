#!/usr/bin/env python3
"""
Milestone 3 – Frontend Grid Virtualization
===========================================
Reads catalog_data.js (window.CATALOG_DATA) and rebuilds index.html to:
  - Replace the static 506-card HTML grid with a JS-driven progressive grid
  - Keep all in-house Sterling Prime products (from existing HTML)
  - Load catalog_data.js dynamically so new products auto-appear
  - Progressive rendering: 48 initial cards + 36 per scroll batch via IntersectionObserver
  - In-memory search with 150ms debounce
  - Dynamic category pill counts from window.CATALOG_DATA
  - Chatbot stays bottom-right (right:28px; bottom:28px)
  - WhatsApp float stays bottom-left (left:28px; bottom:28px)
"""

import sys, json, re, pathlib
sys.stdout.reconfigure(encoding='utf-8')

ROOT     = pathlib.Path(__file__).parent.parent
IN_HTML  = ROOT / "index.html"
OUT_HTML = ROOT / "index.html"
DATA_JS  = ROOT / "catalog_data.js"

def main():
    print("=" * 60)
    print("M3 – Frontend Grid Virtualization")
    print("=" * 60)

    if not DATA_JS.exists():
        print("ERROR: catalog_data.js not found. Run M2 first.")
        sys.exit(1)

    # Count products for stats
    with open(DATA_JS, encoding='utf-8') as f:
        js_raw = f.read()
    # Parse the JSON part
    json_str = js_raw[js_raw.index('['):js_raw.rindex(']')+1]
    catalog  = json.loads(json_str)
    total    = len(catalog)

    import collections
    cat_counts = collections.Counter(p['category_slug'] for p in catalog)

    print(f"\n[1/4] Catalog stats: {total:,} unique products across {len(cat_counts)} categories")
    for slug, count in sorted(cat_counts.items(), key=lambda x: -x[1]):
        print(f"      {slug:<30s}  {count:>5,}")

    print(f"\n[2/4] Reading index.html …")
    with open(IN_HTML, encoding='utf-8') as f:
        html = f.read()
    lines = html.splitlines(keepends=True)
    total_lines = len(lines)
    print(f"      {total_lines:,} lines read")

    # Find galleryGrid start/end
    grid_start = None
    grid_end   = None
    for i, line in enumerate(lines):
        if 'id="galleryGrid"' in line:
            grid_start = i  # the <div class="gallery-grid" id="galleryGrid"> line
        if grid_start and i > grid_start:
            if '<!-- No Results Found State -->' in line:
                grid_end = i  # keep no-results div
                break

    if not grid_start or not grid_end:
        print("ERROR: Could not locate galleryGrid boundaries in index.html")
        sys.exit(1)

    print(f"      galleryGrid: lines {grid_start+1}–{grid_end+1}")

    # The new grid section: just a sentinel comment, JS renders the cards
    new_grid_inner = """
            <!-- Partner catalogue product cards are rendered dynamically by catalog_data.js + CatalogGrid JS below -->
            <!-- In-house Sterling Prime products (below) are always rendered statically -->

"""

    print(f"\n[3/4] Injecting dynamic grid JS …")

    # Build category pills HTML from real counts
    cat_display = {
        "electronics-tech":    ("fas fa-headphones",       "Tech & Audio"),
        "smartwatches":        ("fas fa-clock",             "Smartwatches"),
        "drinkware-bottles":   ("fas fa-mug-hot",           "Drinkware"),
        "bags-travel":         ("fas fa-suitcase-rolling",  "Bags & Travel"),
        "pens-writing":        ("fas fa-pen-nib",           "Pens & Writing"),
        "stationery-work":     ("fas fa-folder-open",       "Stationery & Kits"),
        "home-kitchen":        ("fas fa-home",              "Home & Kitchen"),
        "festive-hampers":     ("fas fa-gifts",             "Hampers"),
        "apparel-lifestyle":   ("fas fa-tshirt",            "Apparel"),
        "wellness-grooming":   ("fas fa-spa",               "Wellness"),
        "office-desk":         ("fas fa-briefcase",         "Office & Desk"),
        "wooden-handicrafts":  ("fas fa-tree",              "Wooden Gifts"),
        "clocks-planners":     ("fas fa-clock",             "Clocks & Planners"),
        "corporate-gift-sets": ("fas fa-gift",              "Gift Sets"),
        "luxury-premium":      ("fas fa-crown",             "Luxury"),
        "books-learning":      ("fas fa-book",              "Books"),
    }

    pills_html = f"""            <button class="cat-btn active" data-cat="all" data-cat-name="All Catalogue Items">
                <i class="fas fa-th-large"></i>
                <span>All Items</span>
                <span class="cat-count" id="count-all">{total:,}</span>
            </button>
"""
    for slug in sorted(cat_counts.keys(), key=lambda s: -cat_counts[s]):
        if slug in cat_display:
            icon, label = cat_display[slug]
            count = cat_counts.get(slug, 0)
            pills_html += f"""            <button class="cat-btn" data-cat="{slug}" data-cat-name="{label}">
                <i class="{icon}"></i>
                <span>{label}</span>
                <span class="cat-count" id="count-{slug}">{count:,}</span>
            </button>
"""

    # The virtualized grid JS block (goes before </body>)
    # This replaces static card rendering with IntersectionObserver lazy batch rendering
    virtual_js = f"""
    <!-- ═══ Catalog Grid Virtualization Engine ═══ -->
    <script src="catalog_data.js"></script>
    <script>
    (function() {{
        'use strict';
        var BATCH_INIT = 48;
        var BATCH_SIZE = 36;
        var allProducts = [];    // merged inhouse + partner
        var filtered   = [];
        var rendered   = 0;
        var observer   = null;
        var sentinel   = null;
        var debounceTimer = null;

        // ── Collect in-house cards already in DOM ──────────────────────────
        function collectInhouse() {{
            var cards = document.querySelectorAll('#galleryGrid .product-card.is-inhouse');
            var result = [];
            cards.forEach(function(c) {{
                result.push({{
                    _domNode: c,
                    _slug:    c.dataset.category || '',
                    _name:    (c.dataset.name || '').toLowerCase(),
                    _brand:   (c.dataset.brand || '').toLowerCase(),
                    _type:    'inhouse'
                }});
            }});
            return result;
        }}

        // ── Build a product card DOM node from catalog_data.js entry ───────
        function buildCard(p) {{
            var slug  = p.category_slug || 'corporate-gift-sets';
            var name  = p.name  || 'Unknown Product';
            var brand = p.brand || 'Partner Brand';
            var img   = p.image || '';
            var cat   = p.category || slug;
            var waText = encodeURIComponent(
                'Hi Sterling Prime, I would like a quotation for:\\n\\n*' + brand + ' – ' + name + '*\\nCategory: ' + cat
            );
            var waUrl  = 'https://wa.me/917041614713?text=' + waText;
            var safe   = function(s){{ return s.replace(/"/g,"&quot;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/&/g,"&amp;"); }};
            var imgSrc = img ? img : 'raw%20images/placeholder.jpg';

            var div = document.createElement('div');
            div.className = 'product-card is-partner';
            div.setAttribute('data-category', slug);
            div.setAttribute('data-category-name', cat);
            div.setAttribute('data-name', name);
            div.setAttribute('data-brand', brand);
            div.setAttribute('data-type', 'partner_product');
            div.setAttribute('onclick', "openLightbox('" + safe(img) + "', '" + safe(name) + "', '" + safe(cat) + "', '" + safe(brand) + "', true)");
            div.innerHTML =
                '<span class="product-badge">' + safe(cat) + '</span>' +
                '<div class="img-wrapper">' +
                  '<img src="' + safe(imgSrc) + '" alt="' + safe(name) + '" loading="lazy" onerror="this.src=\'raw%20images/placeholder.jpg\'">' +
                '</div>' +
                '<div class="product-info">' +
                  '<div class="brand-subtitle">' + safe(brand) + '</div>' +
                  '<div class="product-name" title="' + safe(name) + '">' + safe(name) + '</div>' +
                  '<div class="card-actions">' +
                    '<a href="' + waUrl + '" target="_blank" class="btn-enquire" title="Enquire via WhatsApp" onclick="event.stopPropagation();">' +
                      '<i class="fab fa-whatsapp"></i> Enquire' +
                    '</a>' +
                    '<button type="button" class="btn-zoom" title="View details" onclick="openLightbox(\'' + safe(img) + '\',\'' + safe(name) + '\',\'' + safe(cat) + '\',\'' + safe(brand) + '\',true);event.stopPropagation();">' +
                      '<i class="fas fa-search-plus"></i>' +
                    '</button>' +
                  '</div>' +
                '</div>';
            return div;
        }}

        // ── Render next batch of filtered items ────────────────────────────
        function renderBatch(n) {{
            var grid = document.getElementById('galleryGrid');
            if (!grid) return;

            // Remove sentinel if present
            if (sentinel && sentinel.parentNode) sentinel.parentNode.removeChild(sentinel);

            var end = Math.min(rendered + n, filtered.length);
            var fragment = document.createDocumentFragment();

            for (var k = rendered; k < end; k++) {{
                var item = filtered[k];
                if (item._domNode) {{
                    // in-house: node already in DOM, nothing to do
                }} else {{
                    fragment.appendChild(buildCard(item));
                }}
            }}
            rendered = end;

            // Insert partner cards before noResults
            var noRes = document.getElementById('noResults');
            if (noRes) {{
                grid.insertBefore(fragment, noRes);
            }} else {{
                grid.appendChild(fragment);
            }}

            // Update count display
            var countEl = document.getElementById('productCount');
            if (countEl) {{
                countEl.innerHTML = 'Showing <strong>' + rendered + ' of ' + filtered.length + '</strong> items';
            }}

            // If more to load, add new sentinel
            if (rendered < filtered.length) {{
                attachSentinel(grid);
            }}

            // Toggle noResults
            if (noRes) {{
                noRes.style.display = filtered.length === 0 ? 'block' : 'none';
            }}
        }}

        // ── IntersectionObserver sentinel for infinite scroll ──────────────
        function attachSentinel(grid) {{
            if (observer) observer.disconnect();
            sentinel = document.createElement('div');
            sentinel.id = 'sp-load-sentinel';
            sentinel.style.cssText = 'height:2px;width:100%;grid-column:1/-1;';
            var noRes = document.getElementById('noResults');
            if (noRes) grid.insertBefore(sentinel, noRes);
            else grid.appendChild(sentinel);

            observer = new IntersectionObserver(function(entries) {{
                if (entries[0].isIntersecting) renderBatch(BATCH_SIZE);
            }}, {{ rootMargin: '200px' }});
            observer.observe(sentinel);
        }}

        // ── Filter products by category slug and search query ──────────────
        function applyFilters() {{
            var catSlug  = (window._activeCat || 'all');
            var typeF    = (window._activeType || 'all');
            var query    = ((document.getElementById('productSearch') || {{}}).value || '').toLowerCase().trim();

            // First hide/show all inhouse DOM nodes
            allProducts.forEach(function(p) {{
                if (p._domNode) {{
                    var show = true;
                    if (catSlug !== 'all' && p._slug !== catSlug) show = false;
                    if (typeF === 'partner_product') show = false; // partner only
                    if (query) {{
                        var haystack = p._name + ' ' + p._brand + ' ' + p._slug;
                        if (haystack.indexOf(query) === -1) show = false;
                    }}
                    p._domNode.style.display = show ? '' : 'none';
                }}
            }});

            // Then set filtered for partner products
            filtered = allProducts.filter(function(p) {{
                if (p._domNode) return false; // handled above
                if (catSlug !== 'all' && p._slug !== catSlug) return false;
                if (typeF === 'inhouse') return false; // inhouse only
                if (query) {{
                    var haystack = ((p.name || '') + ' ' + (p.brand || '') + ' ' + (p.category || '') + ' ' + (p.category_slug || '')).toLowerCase();
                    if (haystack.indexOf(query) === -1) return false;
                }}
                return true;
            }});

            // Remove all dynamically inserted partner cards from DOM
            var grid = document.getElementById('galleryGrid');
            if (grid) {{
                var partnerCards = grid.querySelectorAll('.product-card.is-partner');
                partnerCards.forEach(function(c) {{ c.parentNode.removeChild(c); }});
            }}
            if (sentinel && sentinel.parentNode) sentinel.parentNode.removeChild(sentinel);
            rendered = 0;

            // Count visible inhouse cards
            var visibleInhouse = allProducts.filter(function(p) {{ return p._domNode && p._domNode.style.display !== 'none'; }}).length;
            var total = visibleInhouse + filtered.length;

            var countEl = document.getElementById('productCount');
            if (countEl) countEl.innerHTML = 'Showing <strong>' + total + '</strong> items';

            if (filtered.length === 0 && visibleInhouse === 0) {{
                var noRes = document.getElementById('noResults');
                if (noRes) noRes.style.display = 'block';
            }} else {{
                var noRes = document.getElementById('noResults');
                if (noRes) noRes.style.display = 'none';
                renderBatch(BATCH_INIT);
            }}
        }}

        // ── Initialise ─────────────────────────────────────────────────────
        function init() {{
            // Collect inhouse products from existing DOM
            var inhouse = collectInhouse();

            // Merge with partner catalog
            var partnerAll = (window.CATALOG_DATA || []).filter(function(p) {{
                return p.type === 'partner_product';
            }}).map(function(p) {{
                return Object.assign({{}}, p, {{
                    _slug:  p.category_slug || p.category || 'corporate-gift-sets',
                    _name:  (p.name  || p.title || '').toLowerCase(),
                    _brand: (p.brand || '').toLowerCase(),
                    _type:  'partner_product'
                }});
            }});

            allProducts = inhouse.concat(partnerAll);

            // Rebuild category pill counts dynamically
            var catCounts = {{}};
            allProducts.forEach(function(p) {{
                catCounts[p._slug] = (catCounts[p._slug] || 0) + 1;
            }});
            // Update all cat-btn count spans
            document.querySelectorAll('.cat-btn[data-cat]').forEach(function(btn) {{
                var slug = btn.getAttribute('data-cat');
                var countEl = btn.querySelector('.cat-count');
                if (!countEl) return;
                if (slug === 'all') {{
                    countEl.textContent = allProducts.length.toLocaleString();
                }} else {{
                    var n = catCounts[slug] || 0;
                    if (n > 0) countEl.textContent = n.toLocaleString();
                }}
            }});
            // Update search placeholder
            var search = document.getElementById('productSearch');
            if (search) search.placeholder = 'Search ' + allProducts.length.toLocaleString() + '+ items by brand, category, or keyword…';

            // Hook up category pill clicks (extend existing handler)
            document.querySelectorAll('.cat-btn[data-cat]').forEach(function(btn) {{
                btn.addEventListener('click', function() {{
                    document.querySelectorAll('.cat-btn').forEach(function(b) {{ b.classList.remove('active'); }});
                    btn.classList.add('active');
                    window._activeCat = btn.getAttribute('data-cat');
                    applyFilters();
                }});
            }});

            // Hook up type filter buttons
            document.querySelectorAll('.view-mode-btn[data-type-filter]').forEach(function(btn) {{
                btn.addEventListener('click', function() {{
                    document.querySelectorAll('.view-mode-btn').forEach(function(b) {{ b.classList.remove('active'); }});
                    btn.classList.add('active');
                    window._activeType = btn.getAttribute('data-type-filter');
                    applyFilters();
                }});
            }});

            // Hook up search bar
            var searchEl = document.getElementById('productSearch');
            if (searchEl) {{
                searchEl.addEventListener('input', function() {{
                    clearTimeout(debounceTimer);
                    debounceTimer = setTimeout(applyFilters, 150);
                }});
            }}
            var clearBtn = document.getElementById('clearSearch');
            if (clearBtn) {{
                clearBtn.addEventListener('click', function() {{
                    var s = document.getElementById('productSearch');
                    if (s) {{ s.value = ''; applyFilters(); }}
                }});
            }}

            // Initial render
            window._activeCat  = 'all';
            window._activeType = 'all';
            applyFilters();
        }}

        // Override resetAllFilters to work with virtual grid
        window.resetAllFilters = function() {{
            document.querySelectorAll('.cat-btn').forEach(function(b) {{ b.classList.remove('active'); }});
            var allBtn = document.querySelector('.cat-btn[data-cat="all"]');
            if (allBtn) allBtn.classList.add('active');
            document.querySelectorAll('.view-mode-btn').forEach(function(b) {{ b.classList.remove('active'); }});
            var allType = document.querySelector('.view-mode-btn[data-type-filter="all"]');
            if (allType) allType.classList.add('active');
            var s = document.getElementById('productSearch');
            if (s) s.value = '';
            window._activeCat  = 'all';
            window._activeType = 'all';
            applyFilters();
        }};

        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', init);
        }} else {{
            init();
        }}
    }})();
    </script>
"""

    print(f"\n[4/4] Rebuilding index.html …")

    # ── Step 1: Update category pills in HTML ──────────────────────────────
    # Find the category-filter-bar div and replace its content
    cat_bar_start = html.index('<div class="category-filter-bar" id="categoryFilterBar">')
    cat_bar_end   = html.index('</div>', cat_bar_start + 50) + len('</div>')
    # Find the actual end (closing of the category-filter-bar)
    # The bar ends with </div> after the last cat-btn
    # Find the exact </div> that closes categoryFilterBar
    depth = 0
    pos   = cat_bar_start
    while pos < len(html):
        if html[pos:pos+4] == '<div':
            depth += 1
        elif html[pos:pos+6] == '</div>':
            if depth == 1:
                cat_bar_end = pos + 6
                break
            depth -= 1
        pos += 1

    new_cat_bar = f'<div class="category-filter-bar" id="categoryFilterBar">\n{pills_html}            </div>'
    html = html[:cat_bar_start] + new_cat_bar + html[cat_bar_end:]

    # ── Step 2: Update search placeholder ─────────────────────────────────
    html = re.sub(
        r'placeholder="Search \d+\+ items[^"]*"',
        f'placeholder="Search {total:,}+ items by brand, category, or keyword…"',
        html
    )

    # ── Step 3: Clear static product cards from galleryGrid ───────────────
    # We'll keep in-house cards (is-inhouse) and remove is-partner-catalogue cards
    # But actually the JS engine handles rendering — we remove ALL static partner cards
    # to avoid duplication. In-house cards stay in HTML so they show before JS loads.
    # Find galleryGrid boundaries in updated HTML
    grid_open = '<div class="gallery-grid" id="galleryGrid">'
    gi = html.index(grid_open)
    gi_end = gi + len(grid_open)

    # Find where no-results div begins (that marks end of product cards area)
    no_res_marker = '<!-- No Results Found State -->'
    nr_pos = html.index(no_res_marker, gi_end)

    # The content between galleryGrid open and noResults is all the static product cards
    cards_section = html[gi_end:nr_pos]

    # Keep only is-inhouse cards from the static HTML
    # Extract each product-card block
    inhouse_cards_html = []
    search_pos = 0
    while True:
        card_start = cards_section.find('<div class="product-card is-inhouse"', search_pos)
        if card_start == -1:
            break
        # Find matching closing div
        depth = 0
        pos2 = card_start
        while pos2 < len(cards_section):
            if cards_section[pos2:pos2+4] == '<div':
                depth += 1
            elif cards_section[pos2:pos2+6] == '</div>':
                depth -= 1
                if depth == 0:
                    card_end = pos2 + 6
                    inhouse_cards_html.append(cards_section[card_start:card_end])
                    search_pos = card_end
                    break
            pos2 += 1
        else:
            break

    print(f"      Extracted {len(inhouse_cards_html)} in-house static cards to preserve")

    # Build new grid content: just inhouse cards + a comment for partner cards
    new_cards_section = "\n            <!-- Partner product cards rendered by CatalogGrid.js -->\n\n"
    for card in inhouse_cards_html:
        new_cards_section += "            " + card.strip() + "\n\n"

    html = html[:gi_end] + new_cards_section + html[nr_pos:]

    # ── Step 4: Inject catalog_data.js <script> before </body> ────────────
    # Remove any existing catalog_data.js script tag
    html = re.sub(r'\s*<script src="catalog_data\.js"[^>]*></script>', '', html)
    # Inject the new virtualization block just before </body>
    body_close = html.rfind('</body>')
    html = html[:body_close] + virtual_js + "\n</body>" + html[body_close + len('</body>'):]

    # ── Step 5: Update counts in "Why Choose Us" section ──────────────────
    html = re.sub(r'506\+ Products &amp; Catalogues', f'{total:,}+ Products &amp; Catalogues', html)
    html = re.sub(r'506\+ Products', f'{total:,}+ Products', html)

    # ── Step 6: Write output ───────────────────────────────────────────────
    with open(OUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html)

    out_lines = html.count('\n')
    out_kb = len(html.encode('utf-8')) / 1024
    print(f"\n      index.html written: {out_lines:,} lines | {out_kb:.0f} KB")
    print(f"      Inhouse cards preserved: {len(inhouse_cards_html)}")
    print(f"      Partner products (JS-rendered): {total:,}")
    print(f"\n{'='*60}")
    print(f"  M3 COMPLETE — index.html rebuilt with virtual grid")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
