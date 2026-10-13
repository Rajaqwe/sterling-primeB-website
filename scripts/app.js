// Ensure page loads at top
if ("scrollRestoration" in history) {
    history.scrollRestoration = "manual";
}
window.onload = function() {
    if (window.location.hash) {
        history.replaceState("", document.title, window.location.pathname + window.location.search);
    }
    setTimeout(function() {
        window.scrollTo(0, 0);
    }, 10);
};

// AOS Animation Init
if (typeof AOS !== "undefined") {
    AOS.init({
        once: true,
        offset: 50,
        duration: 800,
        easing: "ease-out-cubic"
    });
}

// Lightbox Modal Controls
function openLightbox(src, title, catName, brand, isPhoto) {
    var lightbox = document.getElementById("lightbox");
    var lightboxImg = document.getElementById("lightbox-img");
    var lightboxTitle = document.getElementById("lightbox-title");
    var lightboxCat = document.getElementById("lightbox-cat");
    var lightboxBrand = document.getElementById("lightbox-brand");
    var lightboxWaBtn = document.getElementById("lightbox-wa-btn");
    var lightboxEmailBtn = document.getElementById("lightbox-email-btn");

    if (!lightbox) return;
    if (lightboxImg) {
        lightboxImg.src = src;
        lightboxImg.alt = title;
    }
    if (lightboxTitle) lightboxTitle.textContent = title;
    if (lightboxCat) lightboxCat.textContent = catName || "Corporate Gift";
    if (lightboxBrand) lightboxBrand.textContent = brand || "Sterling Prime";

    var waMsg = encodeURIComponent("Hi Sterling Prime, I am interested in '" + title + "' (Brand: " + (brand || "Sterling Prime") + ", Category: " + (catName || "Corporate Gift") + "). Please share pricing, customization branding and catalogue PDF.");
    if (lightboxWaBtn) lightboxWaBtn.href = "https://wa.me/917041614713?text=" + waMsg;

    var emailSub = encodeURIComponent("Enquiry for " + title + " - Sterling Prime");
    var emailBody = encodeURIComponent("Hi Sterling Prime Team,\n\nI am interested in '" + title + "' (Brand: " + (brand || "Sterling Prime") + ", Category: " + (catName || "Corporate Gift") + ").\n\nPlease share the pricing, MOQ, customization details and catalogue PDF.\n\nThank you!");
    if (lightboxEmailBtn) lightboxEmailBtn.href = "mailto:info@mysterling.in?subject=" + emailSub + "&body=" + emailBody;

    lightbox.style.display = "flex";
    document.body.style.overflow = "hidden";
}

function closeLightbox() {
    var lightbox = document.getElementById("lightbox");
    if (lightbox) lightbox.style.display = "none";
    document.body.style.overflow = "auto";
}

function closeLightboxOnBackdrop(e) {
    var lightbox = document.getElementById("lightbox");
    if (e.target === lightbox) {
        closeLightbox();
    }
}

document.addEventListener("keydown", function(e) {
    if (e.key === "Escape") {
        closeLightbox();
    }
});

// Header scroll and Back to top button
var backToTopButton = document.getElementById("backToTop");
var header = document.querySelector("header");

window.addEventListener("scroll", function() {
    if (header) {
        if (window.scrollY > 50) header.classList.add("scrolled");
        else header.classList.remove("scrolled");
    }
    if (backToTopButton) {
        var scrollPercent = window.scrollY / (document.documentElement.scrollHeight - window.innerHeight);
        if (scrollPercent > 0.3) backToTopButton.classList.add("show");
        else backToTopButton.classList.remove("show");
    }
});

if (backToTopButton) {
    backToTopButton.addEventListener("click", function(e) {
        e.preventDefault();
        window.scrollTo({ top: 0, behavior: "smooth" });
    });
}

// ═══ Virtual Grid Engine ═══
(function() {
    "use strict";

    var BATCH_INIT = 48;
    var BATCH_SIZE = 36;
    var allProducts = [];
    var filtered = [];
    var rendered = 0;
    var observer = null;
    var sentinel = null;
    var debounceTimer = null;

    function escapeHtml(str) {
        return String(str || "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#39;");
    }

    function collectInhouse() {
        var cards = document.querySelectorAll("#galleryGrid .product-card.is-inhouse");
        var result = [];
        cards.forEach(function(c) {
            result.push({
                _domNode: c,
                _slug: (c.getAttribute("data-category") || "").toLowerCase(),
                _name: (c.getAttribute("data-name") || "").toLowerCase(),
                _brand: (c.getAttribute("data-brand") || "").toLowerCase(),
                _type: "inhouse"
            });
        });
        return result;
    }

    function buildCard(p) {
        var slug = p.category_slug || p.category || "corporate-gift-sets";
        var name = p.name || p.title || "Corporate Gift Item";
        var brand = p.brand || "Partner Brand";
        var img = p.image || p.image_path || "";
        var catName = p.category_name || p.category || "Corporate Gift";
        var waText = encodeURIComponent("Hi Sterling Prime, I would like a quotation for:\n\n*" + brand + " - " + name + "*\nCategory: " + catName);
        var waUrl = "https://wa.me/917041614713?text=" + waText;
        var imgSrc = img ? img : "raw%20images/placeholder.jpg";

        var card = document.createElement("div");
        card.className = "product-card is-partner";
        card.setAttribute("data-category", slug);
        card.setAttribute("data-category-name", catName);
        card.setAttribute("data-name", name);
        card.setAttribute("data-brand", brand);
        card.setAttribute("data-type", "partner_product");
        card.setAttribute("data-img", imgSrc);
        card.setAttribute("onclick", "openLightbox(this.getAttribute('data-img'), this.getAttribute('data-name'), this.getAttribute('data-category-name'), this.getAttribute('data-brand'), true);");

        card.innerHTML =
            "<span class=\"product-badge\">" + escapeHtml(catName) + "</span>" +
            "<div class=\"img-wrapper\">" +
                "<img src=\"" + escapeHtml(imgSrc) + "\" alt=\"" + escapeHtml(name) + "\" loading=\"lazy\">" +
            "</div>" +
            "<div class=\"product-info\">" +
                "<div class=\"brand-subtitle\">" + escapeHtml(brand) + "</div>" +
                "<div class=\"product-name\" title=\"" + escapeHtml(name) + "\">" + escapeHtml(name) + "</div>" +
                "<div class=\"card-actions\">" +
                    "<a href=\"" + waUrl + "\" target=\"_blank\" class=\"btn-enquire\" title=\"Enquire via WhatsApp\" onclick=\"event.stopPropagation();\">" +
                        "<i class=\"fab fa-whatsapp\"></i> Enquire" +
                    "</a>" +
                    "<button type=\"button\" class=\"btn-zoom\" title=\"View details\" onclick=\"openLightbox(this.closest('.product-card').getAttribute('data-img'), this.closest('.product-card').getAttribute('data-name'), this.closest('.product-card').getAttribute('data-category-name'), this.closest('.product-card').getAttribute('data-brand'), true); event.stopPropagation();\">" +
                        "<i class=\"fas fa-search-plus\"></i>" +
                    "</button>" +
                "</div>" +
            "</div>";
        return card;
    }

    function renderBatch(count) {
        var grid = document.getElementById("galleryGrid");
        if (!grid) return;

        if (sentinel && sentinel.parentNode) {
            sentinel.parentNode.removeChild(sentinel);
        }

        var end = Math.min(rendered + count, filtered.length);
        var fragment = document.createDocumentFragment();

        for (var i = rendered; i < end; i++) {
            var item = filtered[i];
            if (!item._domNode) {
                fragment.appendChild(buildCard(item));
            }
        }
        rendered = end;

        var noRes = document.getElementById("noResults");
        if (noRes) {
            grid.insertBefore(fragment, noRes);
        } else {
            grid.appendChild(fragment);
        }

        updateStatusText();

        if (rendered < filtered.length) {
            attachSentinel(grid);
        }
    }

    function attachSentinel(grid) {
        if (observer) observer.disconnect();
        sentinel = document.createElement("div");
        sentinel.id = "sp-load-sentinel";
        sentinel.style.cssText = "height:2px;width:100%;grid-column:1/-1;";

        var noRes = document.getElementById("noResults");
        if (noRes) grid.insertBefore(sentinel, noRes);
        else grid.appendChild(sentinel);

        observer = new IntersectionObserver(function(entries) {
            if (entries[0].isIntersecting) {
                renderBatch(BATCH_SIZE);
            }
        }, { rootMargin: "300px" });
        observer.observe(sentinel);
    }

    function updateStatusText() {
        var countEl = document.getElementById("productCount");
        if (!countEl) return;

        var visibleInhouse = allProducts.filter(function(p) {
            return p._domNode && p._domNode.style.display !== "none";
        }).length;
        var totalMatches = visibleInhouse + filtered.length;

        var activeBtn = document.querySelector(".cat-btn.active");
        var catLabel = activeBtn ? (activeBtn.getAttribute("data-cat-name") || "All Catalogue Items") : "All Catalogue Items";

        var query = ((document.getElementById("productSearch") || {}).value || "").trim();
        var msg = "Showing <strong>" + (visibleInhouse + rendered) + " of " + totalMatches + "</strong> items in <strong>" + catLabel + "</strong>";
        if (query) {
            msg += " matching \"<strong>" + escapeHtml(query) + "</strong>\"";
        }
        countEl.innerHTML = msg;
    }

    function applyFilters() {
        var catSlug = (window._activeCat || "all");
        var typeF = (window._activeType || "all");
        var query = ((document.getElementById("productSearch") || {}).value || "").toLowerCase().trim();

        // 1. Toggle static in-house cards
        allProducts.forEach(function(p) {
            if (p._domNode) {
                var show = true;
                if (catSlug !== "all" && p._slug !== catSlug) show = false;
                if (typeF === "partner_product" || typeF === "partner_catalogue") show = false;
                if (query) {
                    var haystack = p._name + " " + p._brand + " " + p._slug;
                    if (haystack.indexOf(query) === -1) show = false;
                }
                p._domNode.style.display = show ? "flex" : "none";
            }
        });

        // 2. Filter partner catalog items
        filtered = allProducts.filter(function(p) {
            if (p._domNode) return false;
            if (catSlug !== "all" && p._slug !== catSlug) return false;
            if (typeF === "inhouse") return false;
            if (query) {
                var haystack = ((p.name || "") + " " + (p.brand || "") + " " + (p.category || "") + " " + (p.category_slug || "") + " " + (p.description || "")).toLowerCase();
                if (haystack.indexOf(query) === -1) return false;
            }
            return true;
        });

        // 3. Clear existing dynamic cards
        var grid = document.getElementById("galleryGrid");
        if (grid) {
            var partnerCards = grid.querySelectorAll(".product-card.is-partner");
            partnerCards.forEach(function(c) {
                c.parentNode.removeChild(c);
            });
        }
        if (sentinel && sentinel.parentNode) {
            sentinel.parentNode.removeChild(sentinel);
        }
        rendered = 0;

        var visibleInhouse = allProducts.filter(function(p) {
            return p._domNode && p._domNode.style.display !== "none";
        }).length;

        var noRes = document.getElementById("noResults");
        if (filtered.length === 0 && visibleInhouse === 0) {
            if (noRes) noRes.style.display = "block";
        } else {
            if (noRes) noRes.style.display = "none";
            renderBatch(BATCH_INIT);
        }

        updateStatusText();

        var resetBtn = document.getElementById("resetFilterBtn");
        if (resetBtn) {
            if (catSlug !== "all" || typeF !== "all" || query) {
                resetBtn.style.display = "inline-block";
            } else {
                resetBtn.style.display = "none";
            }
        }
    }

    function init() {
        var inhouse = collectInhouse();

        var partnerAll = (window.CATALOG_DATA || []).filter(function(p) {
            return p.type === "partner_product";
        }).map(function(p) {
            return Object.assign({}, p, {
                _slug: p.category_slug || p.category || "corporate-gift-sets",
                _name: (p.name || p.title || "").toLowerCase(),
                _brand: (p.brand || "").toLowerCase(),
                _type: "partner_product"
            });
        });

        allProducts = inhouse.concat(partnerAll);

        // Calculate dynamic pill counts
        var catCounts = {};
        allProducts.forEach(function(p) {
            catCounts[p._slug] = (catCounts[p._slug] || 0) + 1;
        });

        document.querySelectorAll(".cat-btn[data-cat]").forEach(function(btn) {
            var slug = btn.getAttribute("data-cat");
            var countEl = btn.querySelector(".cat-count");
            if (!countEl) return;
            if (slug === "all") {
                countEl.textContent = allProducts.length.toLocaleString();
            } else {
                var n = catCounts[slug] || 0;
                countEl.textContent = n.toLocaleString();
            }
        });

        var search = document.getElementById("productSearch");
        if (search) {
            search.placeholder = "Search " + allProducts.length.toLocaleString() + "+ items by brand, category, or keyword...";
        }

        // Category pills click
        document.querySelectorAll(".cat-btn[data-cat]").forEach(function(btn) {
            btn.addEventListener("click", function() {
                document.querySelectorAll(".cat-btn").forEach(function(b) { b.classList.remove("active"); });
                btn.classList.add("active");
                window._activeCat = btn.getAttribute("data-cat");
                applyFilters();
            });
        });

        // View mode buttons click
        document.querySelectorAll(".view-mode-btn[data-type-filter]").forEach(function(btn) {
            btn.addEventListener("click", function() {
                document.querySelectorAll(".view-mode-btn").forEach(function(b) { b.classList.remove("active"); });
                btn.classList.add("active");
                window._activeType = btn.getAttribute("data-type-filter");
                applyFilters();
            });
        });

        // Search input
        if (search) {
            search.addEventListener("input", function() {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(applyFilters, 150);
                var clearBtn = document.getElementById("clearSearch");
                if (clearBtn) {
                    clearBtn.style.display = search.value.trim().length > 0 ? "block" : "none";
                }
            });
        }

        var clearBtn = document.getElementById("clearSearch");
        if (clearBtn) {
            clearBtn.addEventListener("click", function() {
                if (search) {
                    search.value = "";
                    clearBtn.style.display = "none";
                    search.focus();
                    applyFilters();
                }
            });
        }

        window._activeCat = "all";
        window._activeType = "all";
        applyFilters();
    }

    window.resetAllFilters = function() {
        document.querySelectorAll(".cat-btn").forEach(function(b) { b.classList.remove("active"); });
        var allBtn = document.querySelector(".cat-btn[data-cat=\"all\"]");
        if (allBtn) allBtn.classList.add("active");

        document.querySelectorAll(".view-mode-btn").forEach(function(b) { b.classList.remove("active"); });
        var allType = document.querySelector(".view-mode-btn[data-type-filter=\"all\"]");
        if (allType) allType.classList.add("active");

        var s = document.getElementById("productSearch");
        if (s) s.value = "";
        var clearBtn = document.getElementById("clearSearch");
        if (clearBtn) clearBtn.style.display = "none";

        window._activeCat = "all";
        window._activeType = "all";
        applyFilters();
    };

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
