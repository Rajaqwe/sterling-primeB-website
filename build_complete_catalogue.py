# -*- coding: utf-8 -*-
"""
Build Complete Catalogue & Website Generator.
Incorporates:
1. All 171 physical in-house Sterling Prime products (with photos, model names, category badges, lightbox).
2. All unique brand & partner catalogue items from c:\\Users\\Krishana\\Downloads\\catalogues (boAt, Noise, JBL, Borosil, Milton, FNP, Beardo, Samsonite, Procter, Tapwell, Melamine, Bombay Store, Salido, etc.).
3. Strict deduplication: no same product or catalogue item appears twice anywhere on the site.
4. Interactive category filter pills with live counts, search bar, and filter tabs (All, In-House, Brand Catalogues).
5. Quick WhatsApp & Email quotation/catalogue enquiry buttons for every item.
"""

import os
import re
import urllib.parse
import hashlib
from collections import defaultdict

catalogues_dir = r"c:\Users\Krishana\Downloads\catalogues"
repo_dir = r"c:\Users\Krishana\Downloads\sterling-primeB-website"
raw_dir = os.path.join(repo_dir, "raw images")

# 1. In-House Sterling Prime Core Products (171 items)
inhouse_categories = [
    {
        "id": "office-desk",
        "name": "Office & Desk Essentials",
        "short": "Office & Desk",
        "icon": "fas fa-briefcase",
        "products": [
            ("BLUE DESK ORGAIZER.jpeg", "Executive Blue Desk Organizer"),
            ("BOTTLE PEN HOLDER.JPEG", "Bottle Pen & Utility Stand"),
            ("CALCULATOR.jpeg", "Executive Desktop Calculator"),
            ("COASTER SET.JPEG", "Corporate Coaster Set – Model 01"),
            ("COASTER SET (2).jpeg", "Corporate Coaster Set – Model 02"),
            ("DESK KIT.JPEG", "Professional Desk Utility Kit"),
            ("DESK MAT.jpeg", "Premium Leatherette Desk Mat"),
            ("DESK ORGANISER.JPEG", "Executive Desk Organiser – Classic"),
            ("DESK ORGANISER.PNG", "Modern Modular Desk Organiser"),
            ("DESK ORGANIZER.JPEG", "Multifunction Desk Organizer – Classic"),
            ("DESK ORGANIZER (2).jpeg", "Multifunction Desk Organizer – Model 02"),
            ("DESK ORGANIZER (3).jpeg", "Multifunction Desk Organizer – Model 03"),
            ("DESK ORGANIZER (4).jpeg", "Multifunction Desk Organizer – Model 04"),
            ("DESK WHITEBOARD.JPEG", "Desktop Memo Whiteboard & Stand"),
            ("GREEN MOBILE STAND.JPEG", "Eco Green Mobile Desktop Stand"),
            ("MOBILE STAND.JPEG", "Premium Mobile Stand – Classic"),
            ("MOBILE STAND.PNG", "Ergonomic Desktop Mobile Stand"),
            ("MOBILE STAND (2).JPEG", "Dual Angle Mobile Stand – Model 02"),
            ("PAPER WEIGHT.JPEG", "Executive Glass Paper Weight"),
            ("PHOTO FRAME.jpeg", "Corporate Photo Frame – Classic"),
            ("PHOTO FRAME (2).jpeg", "Corporate Photo Frame – Model 02"),
            ("STAND & STAPLERS.jpeg", "Desk Stapler & Utility Stand")
        ]
    },
    {
        "id": "pens-writing",
        "name": "Pens & Writing Instruments",
        "short": "Pens & Writing",
        "icon": "fas fa-pen-nib",
        "products": [
            ("BALL PENS.jpeg", "Corporate Ball Pen Set"),
            ("LEATHER PEN SET.jpeg", "Executive Leather Pen Gift Set"),
            ("PEN.jpeg", "Executive Rollerball Pen"),
            ("PEN (2).jpeg", "Executive Ballpoint Pen – Model 02"),
            ("PENS.jpeg", "Signature Executive Pens Collection"),
            ("PENS (2).jpeg", "Dual Tone Metal Pens Set"),
            ("PREMIUM PEN.jpeg", "Premium Gold Accent Executive Pen"),
            ("PROMOTIONAL PENS.jpeg", "Branded Promotional Pens Assortment"),
            ("PEN HOLDER.jpeg", "Classic Cylindrical Pen Holder"),
            ("PEN HOLDER (2).jpeg", "Modern Mesh Pen Holder – Model 02"),
            ("PEN HOLDER (3).jpeg", "Contoured Metal Pen Holder – Model 03"),
            ("PEN STAND.JPEG", "Executive Desk Pen Stand – Classic"),
            ("PEN STAND (2).JPEG", "Executive Pen Stand – Model 02"),
            ("PEN STAND (3).JPEG", "Executive Pen Stand – Model 03"),
            ("PEN STAND (4).JPEG", "Executive Pen Stand – Model 04"),
            ("PEN STAND (5).jpeg", "Executive Pen Stand – Model 05"),
            ("PEN STAND (6).jpeg", "Executive Pen Stand – Model 06"),
            ("PEN STAND (7).jpeg", "Executive Pen Stand – Model 07"),
            ("PEN STAND (8).jpeg", "Executive Pen Stand – Model 08"),
            ("PEN STAND (9).jpeg", "Executive Pen Stand – Model 09"),
            ("PEN STAND HEART.jpeg", "Heart Motif Desk Pen Stand"),
            ("ACRYLIC PEN STAND.JPEG", "Crystal Clear Acrylic Pen Stand")
        ]
    },
    {
        "id": "stationery-work",
        "name": "Stationery & Work Kits",
        "short": "Stationery & Kits",
        "icon": "fas fa-folder-open",
        "products": [
            ("CLIPBOARD.jpeg", "Executive Document Clipboard"),
            ("FILES ORGANIZER.JPEG", "Multi-Pocket Document File Organizer"),
            ("LOG DIARY.jpeg", "Corporate Daily Log Diary – Executive"),
            ("LOG DIARY (2).jpeg", "Corporate Daily Log Diary – Model 02"),
            ("LOG DIARY (3).jpeg", "Corporate Daily Log Diary – Model 03"),
            ("PLANNER.jpeg", "Executive Annual Planner & Journal"),
            ("ESSENTIAL DESK ORGANISER KIT.JPEG", "Essential Desk Organizer Stationery Kit"),
            ("EXECUTIVE STATIONARY KIT.JPEG", "Executive Corporate Stationery Kit"),
            ("OFFICE CORRECTION WRITING KIT.JPEG", "Office Writing & Correction Kit"),
            ("OFFICE KIT.JPEG", "Complete Office Workday Kit"),
            ("OFFICE PEN MARKER KIT.JPEG", "Office Highlighter & Pen Marker Kit"),
            ("OFFICE UTILITY KIT.JPEG", "Office Utility & Stationery Kit"),
            ("ORAGANIZE DESK SET.PNG", "All-in-One Desk Organization Set"),
            ("STATIONARY GIFT SET.jpeg", "Deluxe Stationery Gift Set – Model 01"),
            ("STATIONARY GIFT SET (2).jpeg", "Deluxe Stationery Gift Set – Model 02"),
            ("STATIONARY KIT.JPEG", "Corporate Stationery Kit – Classic"),
            ("STATIONARY KIT (2).JPEG", "Corporate Stationery Kit – Model 02"),
            ("STATIONARY KIT (3).JPEG", "Corporate Stationery Kit – Model 03"),
            ("STATIONARY KIT (4).JPEG", "Corporate Stationery Kit – Model 04"),
            ("STATIONARY KIT (5).JPEG", "Corporate Stationery Kit – Model 05")
        ]
    },
    {
        "id": "gift-sets",
        "name": "Corporate Gift Sets & Kits",
        "short": "Gift Sets",
        "icon": "fas fa-gift",
        "products": [
            ("CHARACTER GIFT SET.jpeg", "Character Themed Corporate Gift Set"),
            ("ESSENTIAL KIT.JPEG", "Executive Everyday Essentials Kit"),
            ("GIFT SET.JPEG", "Corporate VIP Gift Set – Classic"),
            ("GIFT SET (2).JPEG", "Corporate Gift Set – Model 02"),
            ("GIFT SET (3).jpeg", "Corporate Gift Set – Model 03"),
            ("GIFT SET (4).jpeg", "Corporate Gift Set – Model 04"),
            ("GIFT SET (5).jpeg", "Corporate Gift Set – Model 05"),
            ("GIFT SET (6).jpeg", "Corporate Gift Set – Model 06"),
            ("GIFT SET (7).jpeg", "Corporate Gift Set – Model 07"),
            ("UTILITY SET.jpeg", "Corporate Multi-Utility Gift Set"),
            ("UTILITY & CARE KIT.JPEG", "Utility & Care Executive Combo Kit")
        ]
    },
    {
        "id": "bags-travel",
        "name": "Bags, Pouches & Travel",
        "short": "Bags & Travel",
        "icon": "fas fa-suitcase-rolling",
        "products": [
            ("BACK PACK.jpeg", "Corporate Commuter Backpack"),
            ("TRAVEL BACKPACK.jpeg", "Executive Travel & Business Backpack"),
            ("FOLDER BAG.jpeg", "Professional Document Folder Bag"),
            ("LEATHER BAG.jpeg", "Premium Leather Conference Laptop Bag"),
            ("LEATHER POUCH.JPEG", "Executive Leather Utility Pouch"),
            ("LEATHER POUCH (2).jpeg", "Executive Leather Pouch – Model 02"),
            ("LEATHER POUCH (3).jpeg", "Executive Leather Pouch – Model 03"),
            ("POUCH BAG.jpeg", "Multipurpose Zipper Travel Pouch"),
            ("BRANDABLE COSMETIC POUCH.jpeg", "Brandable Cosmetic & Grooming Pouch"),
            ("CUSTOM BRANDED POUCH.JPEG", "Custom Branded Travel Utility Pouch"),
            ("PREMIUM PATTERNED CASE.JPEG", "Premium Patterned Executive Case"),
            ("DOCTOR CASE.JPEG", "Professional Medical & Doctor Case"),
            ("ZIPPER TRAVEL KIT.JPEG", "Compact Zipper Travel Organizer Kit")
        ]
    },
    {
        "id": "clocks-planners",
        "name": "Clocks, Calendars & Planners",
        "short": "Clocks & Planners",
        "icon": "fas fa-clock",
        "products": [
            ("DESK CALENDER.jpeg", "Executive Metal Desk Calendar"),
            ("DESK CLOCK.JPEG", "Executive Desk Clock – Classic"),
            ("DESK CLOCK.PNG", "Minimalist Precision Desk Clock"),
            ("DESK CLOCK (2).jpeg", "Executive Desk Clock – Model 02"),
            ("DESK CLOCK (3).jpeg", "Executive Desk Clock – Model 03"),
            ("DESK CLOCK & PEN HOLDER.jpeg", "Desk Clock & Pen Holder Duo"),
            ("DESK CLOCK MODEL.jpeg", "Architectural Desk Clock Model"),
            ("DYNAMIC DESK CLOCK.JPEG", "Dynamic Motion Dial Desk Clock"),
            ("WALL CLOCKS.jpeg", "Sterling Prime Designer Wall Clock")
        ]
    },
    {
        "id": "wooden-gifts",
        "name": "Wooden Gifts & Eco Decor",
        "short": "Wooden Gifts",
        "icon": "fas fa-tree",
        "products": [
            ("WOODEN BASE ACRYLIC STAND.JPEG", "Wooden Base Acrylic Branding Stand"),
            ("WOODEN CLOCK.JPEG", "Handcrafted Wooden Desk Clock – Model 01"),
            ("WOODEN DESK CLOCK.jpeg", "Handcrafted Wooden Desk Clock – Model 02"),
            ("WOODEN DESK ORGANIZER.JPEG", "Artisanal Wooden Desk Organizer – Classic"),
            ("WOODEN DESK ORGANIZER (2).JPEG", "Artisanal Wooden Desk Organizer – Model 02"),
            ("WOODEN DESK ORGANIZER (3).JPEG", "Artisanal Wooden Desk Organizer – Model 03"),
            ("WOODEN DESK ORGANIZER (4).jpeg", "Artisanal Wooden Desk Organizer – Model 04"),
            ("WOODEN DESK ORGANIZER (5).jpeg", "Artisanal Wooden Desk Organizer – Model 05"),
            ("WOODEN FRAME.jpeg", "Natural Wood Certificate & Photo Frame"),
            ("WOODEN MATERNITY CLOCK.JPEG", "Wooden Maternity Milestone Clock"),
            ("WOODEN PEN + MOBILE STAND.JPEG", "Wooden Dual Pen & Mobile Stand"),
            ("WOODEN PEN STAND.jpeg", "Carved Wooden Pen Stand – Classic"),
            ("WOODEN PEN STAND (2).JPEG", "Carved Wooden Pen Stand – Model 02"),
            ("WOODEN PEN STAND (6).JPEG", "Carved Wooden Pen Stand – Model 06"),
            ("WOODEN TISSUE BOX.JPEG", "Handcrafted Wooden Tissue Box Dispenser")
        ]
    },
    {
        "id": "acrylic-displays",
        "name": "Acrylic & Promotional Displays",
        "short": "Acrylic & Displays",
        "icon": "fas fa-desktop",
        "products": [
            ("ACRYLC STAND.JPEG", "Minimalist Acrylic Table Stand – Model 01"),
            ("ACRYLIC STAND.JPEG", "Premium Clear Acrylic Stand – Classic"),
            ("ACRYLIC STAND (2).JPEG", "Premium Clear Acrylic Stand – Model 02"),
            ("ACRYLIC STAND (3).JPEG", "Premium Clear Acrylic Stand – Model 03"),
            ("ACRYLIC DISPLAY STAND.JPEG", "Countertop Acrylic Display Stand"),
            ("DISPLAY MODEL.jpeg", "Custom Promotional Display Model"),
            ("DISPLAY STAND.JPEG", "Modular Showcase Display Stand"),
            ("LETTER DISPLAY.JPEG", "Corporate Letter & Branding Display"),
            ("PROMOTIONAL DISPLAY.jpeg", "Promotional Point-of-Sale Display"),
            ("PROMOTIONAL MODEL.jpeg", "Promotional Scale Product Model"),
            ("SHOWCASE MODEL.jpeg", "Exhibition Product Showcase Model"),
            ("SPINNER STAND.jpeg", "Interactive Rotating Spinner Display Stand")
        ]
    },
    {
        "id": "healthcare-medical",
        "name": "Healthcare & Medical Communication",
        "short": "Healthcare & Medical",
        "icon": "fas fa-notes-medical",
        "products": [
            ("ANATOMICAL CLOCK.JPEG", "Anatomical Medical Clock"),
            ("CARDIAC CARE DISPLAY.jpeg", "Cardiac Care Clinical Display Model"),
            ("DUMMY MARKETING BOTTLE.PNG", "Pharmaceutical Marketing Display Bottle"),
            ("EMBRYONIC DEVELOPMENT BOARD.JPEG", "Embryonic Development Board – Stage 01"),
            ("EMBRYONIC DEVELOPMENT BOARD (2).JPEG", "Embryonic Development Board – Stage 02"),
            ("HEALTHCARE DISPLAY.JPEG", "Clinical Healthcare Communication Display"),
            ("KIDS HEIGHT CHART.PNG", "Pediatric Growth & Height Chart Board"),
            ("KNEE MODEL.JPEG", "Orthopedic Knee Joint Anatomical Model"),
            ("MEDICAL CLIPBOARD.JPEG", "Clinical Medical Clipboard – Model 01"),
            ("MEDICAL CLIPBOARD (2).JPEG", "Clinical Medical Clipboard – Model 02"),
            ("MEDICAL DISPLAY.JPEG", "Medical Scientific Display Unit"),
            ("MEDICAL DISPLAY BOX.JPEG", "Healthcare Medical Display Presentation Box"),
            ("MEDICAL ICON DISPLAY.JPEG", "Medical Icon & Healthcare Communication Stand"),
            ("MEDICAL PRESENTATION BOX.JPEG", "Medical Educational Presentation Case"),
            ("MEDICINE TIMER CLOCK (2).JPEG", "Medication Dosage Reminder Timer Clock"),
            ("OSTEOPOROSIS EDUCATION MODEL.JPEG", "Osteoporosis Clinical Education Model – Model 01"),
            ("OSTEOPOROSIS EDUCATIONAL MODEL.JPEG", "Osteoporosis Demonstration Model – Model 02"),
            ("OSTEOPOROSIS EDUCATIONAL MODEL (2).JPEG", "Osteoporosis Anatomical Stage Model – Model 03"),
            ("PREGNANCY DESK CALENDER.JPEG", "Obstetric Pregnancy Desk Calendar & Tracker"),
            ("PREGNANCY TRACKER WHEEL (2).JPEG", "Gestational Age Calculator & Pregnancy Tracker Wheel"),
            ("STOMACH MODEL.JPEG", "Gastrointestinal Stomach Anatomical Model")
        ]
    },
    {
        "id": "wellness-care",
        "name": "Wellness, Care & Lifestyle",
        "short": "Wellness & Care",
        "icon": "fas fa-spa",
        "products": [
            ("BACK SUPPORT PILLOW.PNG", "Ergonomic Memory Foam Back Support Pillow"),
            ("CARE & CONFORT KIT.JPEG", "Care & Comfort Personal Wellness Kit"),
            ("HEALTH GIFT KIT.JPEG", "Corporate Health & Immunity Gift Kit"),
            ("HEALTH KIT.JPEG", "Everyday Health & First Aid Essentials Kit"),
            ("MAGNETC FIDGET DICE.PNG", "Magnetic Focus & Stress Relief Fidget Dice"),
            ("PLUSH SUITE.jpeg", "Plush Mascot Suite Corporate Gift"),
            ("PLUSH TOY.jpeg", "Custom Branded Plush Mascot – Model 01"),
            ("PLUSH TOY (2).jpeg", "Custom Branded Plush Mascot – Model 02"),
            ("WELL NESS KIT.JPEG", "Vitality Wellness & Relaxation Kit"),
            ("WELLNESS DISPLAY STAND.JPEG", "Wellness Care Countertop Display Stand"),
            ("WELLNESS JOURNEY KIT.JPEG", "Wellness Journey Holistic Care Kit"),
            ("WOMENS DAY FLOWER.JPEG", "Celebration Rose & Keepsake Flower Gift")
        ]
    },
    {
        "id": "promotional-merch",
        "name": "Promotional & Branded Merchandise",
        "short": "Promo Merchandise",
        "icon": "fas fa-bullhorn",
        "products": [
            ("ACRYLIC QR KEYCHAINS.JPEG", "Smart Acrylic QR Code Digital Keychain"),
            ("CUSTOMISED BRAND SCISSOR.PNG", "Custom Branded Precision Scissor – Model 01"),
            ("CUSTOMISED BRAND SCISSOR (2).PNG", "Custom Branded Precision Scissor – Model 02"),
            ("FABRIC KEYCHAINS.jpeg", "Embroidered Premium Fabric Keychains"),
            ("PENDRIVE.jpeg", "Corporate High-Speed Metal USB Pendrive"),
            ("SANDWITCH KEYCHAINS.jpeg", "Multi-Layer Sandwich Acrylic Keychains"),
            ("SENSOR LED WTH BRANDING.JPEG", "Motion Sensor LED Branding Light Display"),
            ("TOUCH LAMP SPEAKER.jpeg", "Touch Sensor Smart LED Speaker Lamp")
        ]
    },
    {
        "id": "packaging-storage",
        "name": "Presentation, Packaging & Storage",
        "short": "Packaging & Boxes",
        "icon": "fas fa-box-open",
        "products": [
            ("DEVICE CONTAINER.JPEG", "Protective Equipment & Device Container"),
            ("GIFTING BOX.JPEG", "Luxury Corporate Presentation Gift Box"),
            ("PRODUCT BOX.JPEG", "Custom Rigid Product Packaging Box"),
            ("TISSUE BOX.jpeg", "Premium Faux Leather Desktop Tissue Box"),
            ("TISSUE BOX & ORGANIZER.jpeg", "Dual Tissue Box & Desk Organizer"),
            ("TISSUE DISPENSER.jpeg", "Executive Countertop Tissue Dispenser")
        ]
    }
]

# 2. Extract and Deduplicate Partner Catalogues from catalogues directory
def clean_catalogue_title(fname):
    name = os.path.splitext(fname)[0]
    name = re.sub(r'^\d+[\s._]+', '', name)
    name = re.sub(r'\s*\(\d+\)\s*', ' ', name)
    name = re.sub(r'\s*-\s*Copy(?:\s*\(\d+\))?', ' ', name, flags=re.I)
    name = re.sub(r'_compressed(?:-\d+)?', '', name, flags=re.I)
    name = re.sub(r'\.pdf_compressed(?:-\d+)?', '', name, flags=re.I)
    name = re.sub(r'_tgd', '', name, flags=re.I)
    name = re.sub(r'[_.-]+', ' ', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def format_title_and_brand(fname, clean, folder):
    c = clean.lower()
    
    # Specific numbered and special files in catalogues
    if folder == "gift desk" and fname == "1.pdf":
        return "Executive Pen, Keychain & Stainless Steel Bottle Gift Sets", "The Gift Desk", "gift-sets", "Corporate Gift Sets & Kits", "fas fa-gift"
    if folder == "gift desk" and fname in ["2.pdf", "2 (1).pdf"]:
        return "Executive Corporate Gift Desk Edit – Vol 02", "The Gift Desk", "gift-sets", "Corporate Gift Sets & Kits", "fas fa-gift"
    if folder == "gift desk" and fname == "3.pdf":
        return "Festive Lanterns, Copperware & Loyka Almond Brittle Hampers", "The Gift Desk", "festive-hampers", "Festive Hampers & Gourmet", "fas fa-gifts"
    if folder == "gift desk" and fname == "4.pdf":
        return "Customized Diwali Gifting 2026 Collection", "The Gift Desk", "festive-hampers", "Festive Hampers & Gourmet", "fas fa-gifts"
    if folder == "gift desk" and fname == "5.pdf":
        return "Diwali Gifting Collection – Premium Festive Hampers", "The Gift Desk", "festive-hampers", "Festive Hampers & Gourmet", "fas fa-gifts"
    if folder == "gift desk" and fname == "6.pdf":
        return "The Gift Desk 2026 Diwali Master Corporate Gifting Catalogue", "The Gift Desk", "festive-hampers", "Festive Hampers & Gourmet", "fas fa-gifts"
    if folder == "the bombay store" and "6091705321" in fname:
        return "The Bombay Store Handcrafted Artifacts & Giftware Catalogue", "The Bombay Store", "gift-sets", "Corporate Gift Sets & Kits", "fas fa-gift"

    # Brand detections with distinct collection sub-lines
    if "boat" in c:
        brand = "boAt"
        cat_id = "electronics-tech"
        cat_name = "Electronics & Smart Gadgets"
        icon = "fas fa-headphones"
        if "b2b" in c:
            title = "boAt B2B Corporate Audio, Earbuds & Smartwatches Range"
        else:
            title = "boAt Lifestyle Audio, Bluetooth Speakers & Smart Gadgets"
    elif "noise" in c:
        brand = "Noise"
        cat_id = "electronics-tech"
        cat_name = "Electronics & Smart Gadgets"
        icon = "fas fa-headphones"
        if "institutional" in c:
            title = "Noise Institutional Smartwatches & Wireless Audio Range"
        elif "rep" in c:
            title = "Noise Corporate Accessories & Audio Edition"
        else:
            title = "Noise Smart Audio & Smartwear Master Catalogue"
    elif "jbl" in c:
        brand = "JBL"
        cat_id = "electronics-tech"
        cat_name = "Electronics & Smart Gadgets"
        icon = "fas fa-headphones"
        if "speaker" in c:
            title = "JBL 2025 Portable Bluetooth Speakers Collection"
        else:
            title = "JBL 2025 Wireless Headphones & Earphones Collection"
    elif "portronics" in c:
        brand = "Portronics"
        cat_id = "electronics-tech"
        cat_name = "Electronics & Smart Gadgets"
        icon = "fas fa-headphones"
        title = "Portronics Smart Accessories, Audio & Powerbanks"
    elif "borosil" in c:
        brand = "Borosil"
        cat_id = "drinkware-kitchen"
        cat_name = "Drinkware & Kitchenware"
        icon = "fas fa-mug-hot"
        if "bottle" in c:
            title = "Borosil Insulated Stainless Steel Bottles Range"
        else:
            title = "Borosil 2026 Complete Kitchenware & Glassware Catalogue"
    elif "milton" in c:
        brand = "Milton"
        cat_id = "drinkware-kitchen"
        cat_name = "Drinkware & Kitchenware"
        icon = "fas fa-mug-hot"
        if "bottle" in c:
            title = "Milton Insulated Water Bottles & Thermal Flasks"
        else:
            title = "Milton Complete Home & Kitchen Range Catalogue (Glamora Series)"
    elif "wonderchef" in c:
        brand = "Wonderchef"
        cat_id = "drinkware-kitchen"
        cat_name = "Drinkware & Kitchenware"
        icon = "fas fa-mug-hot"
        title = "Wonderchef Premium Cookware & Appliance Gifting"
    elif "beardo" in c:
        brand = "Beardo"
        cat_id = "apparel-lifestyle"
        cat_name = "Apparel, Grooming & Lifestyle"
        icon = "fas fa-tshirt"
        if "grooming" in c:
            title = "Beardo Electronic Grooming Devices & Trimmers"
        elif "perfume" in c:
            title = "Beardo Luxury Perfumes & Cologne Collection"
        else:
            title = "Beardo Men's Grooming & Styling Gift Kit"
    elif "samsonite" in c:
        brand = "Samsonite"
        cat_id = "bags-travel"
        cat_name = "Bags, Pouches & Travel"
        icon = "fas fa-suitcase-rolling"
        title = "Samsonite B2B Executive Luggage & Backpacks Catalogue"
    elif "delsey" in c:
        brand = "Delsey Paris"
        cat_id = "bags-travel"
        cat_name = "Bags, Pouches & Travel"
        icon = "fas fa-suitcase-rolling"
        title = "Delsey Paris Luxury Business Travel & Trolley Luggage"
    elif "fnp" in c or folder == "fnp catalogue":
        brand = "Ferns N Petals"
        cat_id = "festive-hampers"
        cat_name = "Festive Hampers & Gourmet"
        icon = "fas fa-gifts"
        if "doctor" in c:
            title = "Ferns N Petals (FNP) Doctors Day Special Gifting"
        elif "diwali" in c:
            title = "Ferns N Petals (FNP) Festive Diwali Gifting Catalogue"
        elif "employee" in c:
            title = "Ferns N Petals (FNP) Employee & Client Appreciation Gifts"
        else:
            title = f"Ferns N Petals (FNP) Corporate {clean.title()}"
    elif "ferrero" in c:
        brand = "Ferrero Rocher"
        cat_id = "festive-hampers"
        cat_name = "Festive Hampers & Gourmet"
        icon = "fas fa-gifts"
        title = "Ferrero Rocher Premium Festive Chocolate Hampers"
    elif "fabelle" in c:
        brand = "Fabelle"
        cat_id = "festive-hampers"
        cat_name = "Festive Hampers & Gourmet"
        icon = "fas fa-gifts"
        title = "Fabelle Luxury Artisan Chocolate Gift Collection"
    elif "cross" in c:
        brand = "Cross USA"
        cat_id = "pens-writing"
        cat_name = "Pens & Writing Instruments"
        icon = "fas fa-pen-nib"
        title = "Cross Luxury Executive Pens & Leather Wallets"
    elif "carlton london" in c:
        brand = "Carlton London"
        cat_id = "apparel-lifestyle"
        cat_name = "Apparel, Grooming & Lifestyle"
        icon = "fas fa-tshirt"
        if "ready stock" in c:
            title = "Carlton London Ready Stock Perfumes & Gift Sets"
        else:
            title = "Carlton London Full Range Perfumes, Watches & Accessories"
    elif "park avenue" in c:
        brand = "Park Avenue"
        cat_id = "apparel-lifestyle"
        cat_name = "Apparel, Grooming & Lifestyle"
        icon = "fas fa-tshirt"
        title = f"Park Avenue Corporate {clean.title()}"
    elif "parx" in c:
        brand = "Parx"
        cat_id = "apparel-lifestyle"
        cat_name = "Apparel, Grooming & Lifestyle"
        icon = "fas fa-tshirt"
        title = "Parx Casual & Corporate Polo Shirts"
    elif "raymond" in c:
        brand = "Raymond"
        cat_id = "apparel-lifestyle"
        cat_name = "Apparel, Grooming & Lifestyle"
        icon = "fas fa-tshirt"
        title = "Raymond Executive Apparel & Home Gifting"
    elif "lapcare" in c:
        brand = "Lapcare"
        cat_id = "electronics-tech"
        cat_name = "Electronics & Smart Gadgets"
        icon = "fas fa-headphones"
        title = f"Lapcare Corporate {clean.title()}"
    elif "lenovo" in c:
        brand = "Lenovo"
        cat_id = "electronics-tech"
        cat_name = "Electronics & Smart Gadgets"
        icon = "fas fa-headphones"
        title = "Lenovo Computing & Tech Corporate Range"
    elif "xech" in c:
        brand = "Xech"
        cat_id = "electronics-tech"
        cat_name = "Electronics & Smart Gadgets"
        icon = "fas fa-headphones"
        title = "Xech Innovative Desk Gadgets & Wellness Tech"
    elif "pebble" in c:
        brand = "Pebble"
        cat_id = "electronics-tech"
        cat_name = "Electronics & Smart Gadgets"
        icon = "fas fa-headphones"
        title = "Pebble Smart Audio & Wearables Catalogue"
    elif "qubo" in c:
        brand = "Qubo"
        cat_id = "electronics-tech"
        cat_name = "Electronics & Smart Gadgets"
        icon = "fas fa-headphones"
        title = "Qubo Smart Home Tech & Dashcam Collection"
    elif "cult fit" in c:
        brand = "Cult.fit"
        cat_id = "apparel-lifestyle"
        cat_name = "Apparel, Grooming & Lifestyle"
        icon = "fas fa-tshirt"
        title = "Cult.fit Health, Fitness & Wellness Merchandise"
    elif "melamine" in c or folder == "melamine":
        brand = "Melamine Tableware"
        cat_id = "drinkware-kitchen"
        cat_name = "Drinkware & Kitchenware"
        icon = "fas fa-utensils"
        title = f"Melamine Executive {clean.title()}"
    elif "salido" in c or folder == "salido":
        brand = "Salido Recognition"
        cat_id = "acrylic-displays"
        cat_name = "Acrylic & Promotional Displays"
        icon = "fas fa-trophy"
        title = "Salido 2025 Corporate Awards, Trophies & Gifts"
    elif "bombay store" in c or folder == "the bombay store":
        brand = "The Bombay Store"
        cat_id = "gift-sets"
        cat_name = "Corporate Gift Sets & Kits"
        icon = "fas fa-gift"
        title = f"The Bombay Store Heritage Handicrafts – {clean.title()}"
    elif "joining kit" in c or "welcome kit" in c or "onboarding" in c or "bcg" in c:
        brand = "Procter BCG"
        cat_id = "gift-sets"
        cat_name = "Corporate Gift Sets & Kits"
        icon = "fas fa-user-tie"
        title = f"Procter Employee Joining & Welcome Kit ({clean.title()})"
    elif folder == "tapwell":
        brand = "Tapwell Price Collection"
        cat_id = "gift-sets"
        cat_name = "Corporate Gift Sets & Kits"
        icon = "fas fa-wallet"
        title = f"Tapwell Corporate Gift Slabs – {clean.title()}"
    elif folder == "Chocolates & Hampers" or any(k in c for k in ["hamper", "chocolates", "dryfruit", "sweet", "diwali", "festive", "good road", "snack", "drybite"]):
        brand = "Corporate Hampers"
        cat_id = "festive-hampers"
        cat_name = "Festive Hampers & Gourmet"
        icon = "fas fa-gifts"
        title = f"Festive Gourmet Hamper – {clean.title()}"
    elif any(k in c for k in ["bottle", "flask", "mugs", "drinkware", "copper", "kitchenware", "dining"]):
        brand = "Drinkware & Dining"
        cat_id = "drinkware-kitchen"
        cat_name = "Drinkware & Kitchenware"
        icon = "fas fa-mug-hot"
        title = f"Executive Drinkware – {clean.title()}"
    elif any(k in c for k in ["bag", "backpack", "laptop bag", "leather", "duffle"]):
        brand = "Travel & Bags"
        cat_id = "bags-travel"
        cat_name = "Bags, Pouches & Travel"
        icon = "fas fa-suitcase-rolling"
        title = f"Executive Bag & Travel Kit – {clean.title()}"
    elif folder == "Notebooks & Organizers" or any(k in c for k in ["diary", "notebook", "planner", "pen", "organizer", "mdf", "desk"]):
        brand = "Desk & Stationery"
        cat_id = "office-desk"
        cat_name = "Office & Desk Essentials"
        icon = "fas fa-briefcase"
        title = f"Executive Office Stationery – {clean.title()}"
    else:
        brand = "Sterling Partner Collection"
        cat_id = "gift-sets"
        cat_name = "Corporate Gift Sets & Kits"
        icon = "fas fa-box-open"
        title = f"Corporate Gifting Edit – {clean.title()}"
        
    return title, brand, cat_id, cat_name, icon

# Scan all catalogues with MD5 deduplication first, then title normalization
hashes = {}
unique_files = []
for root, dirs, files in os.walk(catalogues_dir):
    for f in sorted(files):
        if f.lower().endswith(".pdf"):
            full = os.path.join(root, f)
            with open(full, "rb") as fp:
                h = hashlib.md5(fp.read()).hexdigest()
            if h not in hashes:
                hashes[h] = (f, root)
                unique_files.append((root, f, full))

seen_keys = set()
partner_catalogues = []

for root, f, full in unique_files:
    clean = clean_catalogue_title(f)
    folder = os.path.basename(root)
    title, brand, cat_id, cat_name, icon = format_title_and_brand(f, clean, folder)
    
    # Strict deduplication key: lowercase alphanumeric
    dedup_key = re.sub(r'[^a-z0-9]', '', title.lower())
    if dedup_key in seen_keys:
        continue
    seen_keys.add(dedup_key)
    
    partner_catalogues.append({
        "raw_file": f,
        "title": title,
        "brand": brand,
        "cat_id": cat_id,
        "cat_name": cat_name,
        "icon": icon,
        "folder": folder
    })

print(f"Loaded {len(partner_catalogues)} unique partner catalogue items!")

# Add all items into unified category list
all_categories_dict = defaultdict(lambda: {"name": "", "short": "", "icon": "", "items": []})

# Add In-House products
inhouse_total = 0
for cat in inhouse_categories:
    cid = cat["id"]
    all_categories_dict[cid]["name"] = cat["name"]
    all_categories_dict[cid]["short"] = cat["short"]
    all_categories_dict[cid]["icon"] = cat["icon"]
    for fname, title in cat["products"]:
        inhouse_total += 1
        all_categories_dict[cid]["items"].append({
            "type": "inhouse",
            "title": title,
            "filename": fname,
            "encoded_src": "raw%20images/" + urllib.parse.quote(fname),
            "brand": "Sterling Prime In-House",
            "cat_id": cid,
            "cat_name": cat["name"],
            "cat_short": cat["short"],
            "icon": cat["icon"]
        })

# Add new categories that emerged from partner catalogues
partner_cat_meta = {
    "electronics-tech": ("Electronics & Smart Gadgets", "Tech & Audio", "fas fa-headphones"),
    "drinkware-kitchen": ("Drinkware & Kitchenware", "Drinkware", "fas fa-mug-hot"),
    "festive-hampers": ("Festive Hampers & Gourmet", "Hampers", "fas fa-gifts"),
    "apparel-lifestyle": ("Apparel, Grooming & Lifestyle", "Apparel", "fas fa-tshirt")
}

for pid, (pname, pshort, picon) in partner_cat_meta.items():
    if pid not in all_categories_dict:
        all_categories_dict[pid]["name"] = pname
        all_categories_dict[pid]["short"] = pshort
        all_categories_dict[pid]["icon"] = picon

# Add Partner catalogues to their respective categories
partner_total = 0
for item in partner_catalogues:
    partner_total += 1
    cid = item["cat_id"]
    if not all_categories_dict[cid]["name"]:
        all_categories_dict[cid]["name"] = item["cat_name"]
        all_categories_dict[cid]["short"] = item["cat_name"].split()[0]
        all_categories_dict[cid]["icon"] = item["icon"]
        
    all_categories_dict[cid]["items"].append({
        "type": "partner_catalogue",
        "title": item["title"],
        "filename": item["raw_file"],
        "encoded_src": "raw%20images/sterling%20company%20LOGOS/logo.svg",  # high quality brand fallback
        "brand": item["brand"],
        "cat_id": cid,
        "cat_name": all_categories_dict[cid]["name"],
        "cat_short": all_categories_dict[cid]["short"],
        "icon": all_categories_dict[cid]["icon"]
    })

total_unified_items = inhouse_total + partner_total
print(f"Total Unified Catalog Items: {total_unified_items} ({inhouse_total} in-house + {partner_total} partner catalogues)")

# Build Category Filter Pills
pills_html = [f'''            <button class="cat-btn active" data-cat="all" data-cat-name="All Catalogue Items">
                <i class="fas fa-th-large"></i>
                <span>All Items</span>
                <span class="cat-count">{total_unified_items}</span>
            </button>''']

for cid, cdata in sorted(all_categories_dict.items(), key=lambda x: len(x[1]["items"]), reverse=True):
    cnt = len(cdata["items"])
    pills_html.append(f'''            <button class="cat-btn" data-cat="{cid}" data-cat-name="{cdata['name']}">
                <i class="{cdata['icon']}"></i>
                <span>{cdata['short']}</span>
                <span class="cat-count">{cnt}</span>
            </button>''')

cat_pills_str = "\n".join(pills_html)

# Build Cards HTML
cards_html = []
for cid, cdata in all_categories_dict.items():
    for item in cdata["items"]:
        safe_title = item["title"].replace('"', '&quot;')
        safe_cat_name = item["cat_name"].replace('"', '&quot;')
        safe_brand = item["brand"].replace('"', '&quot;')
        is_inhouse = (item["type"] == "inhouse")
        
        wa_text = urllib.parse.quote(f"Hi Sterling Prime, I am interested in '{item['title']}' (Brand: {item['brand']}, Category: {item['cat_name']}). Please share bulk B2B pricing, branding options and catalogue PDF.")
        
        if is_inhouse:
            badge_html = f'<span class="product-badge">{item["cat_short"]}</span>'
            img_html = f'''<div class="img-wrapper">
                    <img src="{item['encoded_src']}" alt="{safe_title}" loading="lazy">
                </div>'''
            actions_html = f'''<div class="card-actions">
                        <a href="https://wa.me/917041614713?text={wa_text}" target="_blank" class="btn-enquire" title="Enquire via WhatsApp" onclick="event.stopPropagation();">
                            <i class="fab fa-whatsapp"></i> Enquire
                        </a>
                        <button type="button" class="btn-zoom" title="View details" onclick="openLightbox('{item['encoded_src']}', '{safe_title}', '{safe_cat_name}', '{safe_brand}', true); event.stopPropagation();">
                            <i class="fas fa-search-plus"></i>
                        </button>
                    </div>'''
            click_action = f"openLightbox('{item['encoded_src']}', '{safe_title}', '{safe_cat_name}', '{safe_brand}', true)"
        else:
            badge_html = f'<span class="product-badge brand-badge"><i class="{item["icon"]}"></i> {item["brand"]}</span>'
            img_html = f'''<div class="img-wrapper catalogue-thumb">
                    <div class="catalogue-icon-wrap">
                        <i class="{item['icon']}"></i>
                    </div>
                    <span class="catalogue-tag-pill">B2B Catalogue PDF</span>
                </div>'''
            actions_html = f'''<div class="card-actions">
                        <a href="https://wa.me/917041614713?text={wa_text}" target="_blank" class="btn-enquire" title="Request Catalogue" onclick="event.stopPropagation();">
                            <i class="fab fa-whatsapp"></i> Request PDF
                        </a>
                        <button type="button" class="btn-zoom" title="Catalogue info" onclick="openLightbox('{item['encoded_src']}', '{safe_title}', '{safe_cat_name}', '{safe_brand}', false); event.stopPropagation();">
                            <i class="fas fa-file-pdf"></i>
                        </button>
                    </div>'''
            click_action = f"openLightbox('{item['encoded_src']}', '{safe_title}', '{safe_cat_name}', '{safe_brand}', false)"
            
        card = f'''            <div class="product-card {'is-partner-catalogue' if not is_inhouse else 'is-inhouse'}" data-category="{cid}" data-category-name="{safe_cat_name}" data-name="{safe_title}" data-brand="{safe_brand}" data-type="{item['type']}" data-aos="fade-up" onclick="{click_action}">
                {badge_html}
                {img_html}
                <div class="product-info">
                    <div class="brand-subtitle">{safe_brand}</div>
                    <div class="product-name" title="{safe_title}">{safe_title}</div>
                    {actions_html}
                </div>
            </div>'''
        cards_html.append(card)

cards_str = "\n\n".join(cards_html)

# Generate HTML
html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sterling Prime - Premium Corporate Gifts & Master B2B Catalogues</title>
    <meta name="description" content="Explore Sterling Prime's complete corporate gifting portfolio of {total_unified_items}+ products and partner catalogues across 15+ categories including desk essentials, electronics, luxury hampers, drinkware, and custom branded swag across India.">
    <link rel="icon" type="image/svg+xml" href="raw%20images/sterling%20company%20LOGOS/logo.svg">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://unpkg.com/aos@2.3.1/dist/aos.css" rel="stylesheet">
    <style>
        :root {{
            --primary: #2b2e83;
            --secondary: #e62263;
            --tertiary: #f47920;
            --gradient: linear-gradient(135deg, #2b2e83, #8e2b88, #e62263, #f47920);
            --gradient-subtle: linear-gradient(135deg, rgba(43, 46, 131, 0.08), rgba(230, 34, 99, 0.08));
            --text-main: #333;
            --text-light: #666;
            --card-bg: rgba(255, 255, 255, 0.96);
            --border-light: rgba(43, 46, 131, 0.12);
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        }}

        html {{
            scroll-behavior: smooth;
        }}

        body {{
            background: linear-gradient(135deg, #f2eff9 0%, #fdeff5 50%, #fff4ec 100%);
            background-attachment: fixed;
            color: var(--text-main);
            overflow-x: hidden;
        }}

        /* Navbar & Header */
        header {{
            background: transparent;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 1000;
            padding: 20px 50px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.3s ease;
        }}

        header.scrolled {{
            background: rgba(255, 255, 255, 0.96);
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.06);
            padding: 8px 50px;
        }}

        .logo-container {{
            display: flex;
            align-items: center;
        }}

        .logo-container img {{
            height: 70px;
            transition: all 0.3s ease;
        }}

        header.scrolled .logo-container img {{
            height: 45px;
        }}

        .logo-container img:hover {{
            transform: scale(1.05);
        }}
        
        .nav-links {{
            display: flex;
            align-items: center;
            gap: 20px;
        }}

        .nav-links a {{
            text-decoration: none; 
            color: var(--primary); 
            font-weight: 600; 
            transition: color 0.3s, text-shadow 0.3s;
            font-size: 1.05rem;
        }}
        .nav-links a:hover {{
            color: var(--secondary);
        }}

        .nav-btn-contact {{
            background: var(--gradient);
            color: white !important;
            padding: 8px 20px;
            border-radius: 25px;
            box-shadow: 0 4px 12px rgba(230, 34, 99, 0.25);
            transition: transform 0.3s ease, box-shadow 0.3s ease !important;
        }}
        .nav-btn-contact:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 18px rgba(230, 34, 99, 0.4);
        }}

        /* Hero Section */
        .hero {{
            position: relative;
            padding: 160px 20px 70px;
            text-align: center;
            min-height: 500px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 1;
        }}

        .hero::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: url('raw%20images/sterling%20company%20LOGOS/sterling%20logo.svg') center/contain no-repeat;
            background-attachment: fixed;
            opacity: 0.12;
            z-index: -1;
        }}

        .hero-badge {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(255, 255, 255, 0.92);
            border: 1px solid var(--border-light);
            padding: 6px 18px;
            border-radius: 30px;
            font-size: 0.9rem;
            font-weight: 600;
            color: var(--primary);
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.04);
            animation: fadeInDown 0.8s ease-out;
        }}
        .hero-badge i {{
            color: var(--tertiary);
        }}

        .hero h1 {{
            font-size: 3.6rem;
            margin-bottom: 18px;
            background: var(--gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: fadeInDown 1s ease-out;
            max-width: 980px;
            line-height: 1.18;
        }}

        .hero p {{
            font-size: 1.35rem;
            color: var(--text-light);
            max-width: 840px;
            margin: 0 auto 30px;
            animation: fadeInUp 1s ease-out 0.3s both;
            font-weight: 500;
            line-height: 1.5;
        }}

        .hero-highlights {{
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 15px;
            margin-top: 10px;
            animation: fadeInUp 1s ease-out 0.5s both;
        }}

        .hero-chip {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(255, 255, 255, 0.88);
            border: 1px solid rgba(43, 46, 131, 0.1);
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.88rem;
            color: var(--primary);
            font-weight: 600;
            box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        }}
        .hero-chip i {{
            color: var(--secondary);
        }}

        /* Gallery Section */
        .gallery-section {{
            padding: 50px 40px;
            max-width: 1440px;
            margin: 0 auto;
        }}

        .section-title {{
            text-align: center;
            font-size: 2.6rem;
            margin-bottom: 15px;
            color: var(--primary);
            position: relative;
        }}

        .section-title::after {{
            content: '';
            width: 90px;
            height: 4px;
            background: var(--gradient);
            display: block;
            margin: 12px auto 0;
            border-radius: 2px;
        }}

        .section-subtitle {{
            text-align: center;
            color: var(--text-light);
            font-size: 1.15rem;
            max-width: 780px;
            margin: 0 auto 35px;
        }}

        /* View Mode Filter Tabs */
        .view-mode-bar {{
            display: flex;
            justify-content: center;
            gap: 12px;
            margin: 0 auto 30px;
            max-width: 800px;
            background: rgba(255, 255, 255, 0.6);
            padding: 6px;
            border-radius: 50px;
            border: 1px solid rgba(43, 46, 131, 0.1);
        }}

        .view-mode-btn {{
            flex: 1;
            padding: 10px 18px;
            border: none;
            background: transparent;
            color: var(--primary);
            font-weight: 700;
            font-size: 0.95rem;
            border-radius: 40px;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }}

        .view-mode-btn.active {{
            background: var(--gradient);
            color: white;
            box-shadow: 0 4px 15px rgba(230, 34, 99, 0.3);
        }}

        /* Search & Filter Controls */
        .gallery-controls {{
            max-width: 1300px;
            margin: 0 auto 35px;
        }}

        .search-wrapper {{
            position: relative;
            max-width: 650px;
            margin: 0 auto 25px;
        }}

        .search-wrapper input {{
            width: 100%;
            padding: 16px 50px 16px 52px;
            font-size: 1.05rem;
            border: 2px solid rgba(43, 46, 131, 0.15);
            border-radius: 50px;
            outline: none;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.05);
            transition: all 0.3s ease;
            color: var(--text-main);
        }}

        .search-wrapper input:focus {{
            border-color: var(--secondary);
            box-shadow: 0 10px 30px rgba(230, 34, 99, 0.18);
            background: #ffffff;
        }}

        .search-wrapper .search-icon {{
            position: absolute;
            left: 20px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--primary);
            font-size: 1.15rem;
            pointer-events: none;
        }}

        .search-wrapper .clear-search-btn {{
            position: absolute;
            right: 18px;
            top: 50%;
            transform: translateY(-50%);
            background: none;
            border: none;
            font-size: 1.15rem;
            color: #999;
            cursor: pointer;
            display: none;
            padding: 5px;
            border-radius: 50%;
            transition: color 0.2s;
        }}
        .search-wrapper .clear-search-btn:hover {{
            color: var(--secondary);
        }}

        /* Category Filter Pills */
        .category-filter-bar {{
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 10px;
            margin-bottom: 25px;
        }}

        .cat-btn {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 10px 18px;
            border-radius: 50px;
            border: 1px solid rgba(43, 46, 131, 0.14);
            background: rgba(255, 255, 255, 0.88);
            backdrop-filter: blur(8px);
            color: var(--primary);
            font-weight: 600;
            font-size: 0.92rem;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.03);
            user-select: none;
        }}

        .cat-btn i {{
            font-size: 0.95rem;
            color: var(--tertiary);
            transition: color 0.3s ease;
        }}

        .cat-btn .cat-count {{
            display: inline-block;
            padding: 2px 8px;
            font-size: 0.76rem;
            border-radius: 20px;
            background: rgba(43, 46, 131, 0.08);
            color: var(--primary);
            font-weight: 700;
            transition: all 0.3s ease;
        }}

        .cat-btn:hover {{
            transform: translateY(-3px);
            border-color: var(--secondary);
            box-shadow: 0 8px 20px rgba(230, 34, 99, 0.15);
        }}

        .cat-btn.active {{
            background: var(--gradient);
            color: #ffffff;
            border-color: transparent;
            box-shadow: 0 8px 25px rgba(230, 34, 99, 0.35);
            transform: translateY(-3px);
        }}

        .cat-btn.active i {{
            color: #ffffff;
        }}

        .cat-btn.active .cat-count {{
            background: rgba(255, 255, 255, 0.28);
            color: #ffffff;
        }}

        /* Status & Count Bar */
        .gallery-status-bar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1300px;
            margin: 0 auto 30px;
            padding: 12px 20px;
            background: rgba(255, 255, 255, 0.8);
            border-radius: 12px;
            border: 1px solid rgba(43, 46, 131, 0.08);
            font-size: 0.95rem;
            color: var(--text-light);
            font-weight: 500;
            box-shadow: 0 2px 8px rgba(0,0,0,0.02);
        }}

        .gallery-status-bar strong {{
            color: var(--primary);
        }}

        .reset-filter-btn {{
            background: none;
            border: none;
            color: var(--secondary);
            font-weight: 600;
            cursor: pointer;
            font-size: 0.88rem;
            display: none;
            padding: 4px 8px;
        }}
        .reset-filter-btn:hover {{
            text-decoration: underline;
        }}

        /* Product & Catalogue Grid */
        .gallery-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(285px, 1fr));
            gap: 28px;
        }}

        .product-card {{
            background: var(--card-bg);
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 10px 25px rgba(0,0,0,0.05);
            transition: all 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            position: relative;
            cursor: pointer;
            border: 1px solid rgba(255,255,255,0.7);
            backdrop-filter: blur(5px);
            display: flex;
            flex-direction: column;
        }}

        .product-card:hover {{
            transform: translateY(-10px);
            box-shadow: 0 18px 38px rgba(0,0,0,0.12);
            border-color: rgba(230, 34, 99, 0.3);
        }}

        .product-badge {{
            position: absolute;
            top: 12px;
            left: 12px;
            background: rgba(43, 46, 131, 0.9);
            backdrop-filter: blur(6px);
            color: #ffffff;
            font-size: 0.72rem;
            font-weight: 700;
            padding: 4px 10px;
            border-radius: 20px;
            z-index: 2;
            text-transform: uppercase;
            letter-spacing: 0.4px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.12);
        }}

        .product-badge.brand-badge {{
            background: var(--gradient);
        }}

        .img-wrapper {{
            width: 100%;
            height: 250px;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #ffffff;
            position: relative;
        }}

        .product-card img {{
            width: 100%;
            height: 100%;
            object-fit: contain;
            transition: transform 0.5s ease;
            padding: 15px;
        }}

        .product-card:hover img {{
            transform: scale(1.08);
        }}

        /* Partner Catalogue Thumbnail */
        .catalogue-thumb {{
            background: linear-gradient(135deg, #f7f5fd, #fdf4f8, #fdf8f4);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}

        .catalogue-icon-wrap {{
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background: white;
            box-shadow: 0 10px 25px rgba(43, 46, 131, 0.1);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2.2rem;
            color: var(--secondary);
            margin-bottom: 12px;
            transition: transform 0.4s ease;
        }}

        .product-card:hover .catalogue-icon-wrap {{
            transform: scale(1.12) rotate(5deg);
        }}

        .catalogue-tag-pill {{
            font-size: 0.75rem;
            font-weight: 700;
            color: var(--primary);
            background: rgba(255, 255, 255, 0.9);
            padding: 4px 12px;
            border-radius: 15px;
            border: 1px solid var(--border-light);
            text-transform: uppercase;
            letter-spacing: 0.4px;
        }}

        .product-info {{
            padding: 18px;
            text-align: center;
            background: white;
            border-top: 2px solid transparent;
            border-image: var(--gradient);
            border-image-slice: 1;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            flex-grow: 1;
        }}

        .brand-subtitle {{
            font-size: 0.78rem;
            font-weight: 700;
            color: var(--secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }}

        .product-name {{
            font-size: 1.05rem;
            font-weight: 600;
            color: var(--primary);
            line-height: 1.35;
            margin-bottom: 15px;
            min-height: 2.7em;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}

        .card-actions {{
            display: flex;
            gap: 8px;
            justify-content: center;
            align-items: center;
            margin-top: auto;
        }}

        .btn-enquire {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            background: #25D366;
            color: white;
            padding: 8px 18px;
            border-radius: 25px;
            font-size: 0.85rem;
            font-weight: 600;
            text-decoration: none;
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(37, 211, 102, 0.25);
        }}

        .btn-enquire:hover {{
            background: #1eb956;
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(37, 211, 102, 0.4);
            color: white;
        }}

        .btn-zoom {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background: rgba(43, 46, 131, 0.08);
            color: var(--primary);
            width: 36px;
            height: 36px;
            border-radius: 50%;
            font-size: 0.88rem;
            transition: all 0.3s ease;
            border: none;
            cursor: pointer;
        }}

        .btn-zoom:hover {{
            background: var(--primary);
            color: white;
            transform: scale(1.1);
        }}

        /* Empty State */
        .no-results {{
            display: none;
            grid-column: 1 / -1;
            text-align: center;
            padding: 70px 20px;
            background: rgba(255, 255, 255, 0.8);
            border-radius: 16px;
            margin: 20px 0;
        }}

        .no-results i {{
            font-size: 3.5rem;
            color: var(--primary);
            opacity: 0.4;
            margin-bottom: 15px;
        }}

        .no-results h3 {{
            font-size: 1.4rem;
            color: var(--primary);
            margin-bottom: 8px;
        }}

        .no-results p {{
            color: var(--text-light);
            margin-bottom: 20px;
        }}

        .no-results button {{
            background: var(--gradient);
            color: white;
            border: none;
            padding: 10px 24px;
            border-radius: 30px;
            font-weight: 600;
            cursor: pointer;
        }}

        /* Catalogue PDF Banner */
        .catalogue-banner {{
            max-width: 1300px;
            margin: 60px auto 20px;
            background: var(--gradient);
            border-radius: 20px;
            padding: 35px 40px;
            color: white;
            box-shadow: 0 15px 35px rgba(43, 46, 131, 0.2);
        }}

        .catalogue-banner-inner {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 30px;
            flex-wrap: wrap;
        }}

        .banner-text {{
            flex: 1;
            min-width: 300px;
        }}

        .banner-text h3 {{
            font-size: 1.8rem;
            margin-bottom: 10px;
        }}

        .banner-text p {{
            font-size: 1.05rem;
            opacity: 0.95;
            line-height: 1.5;
        }}

        .banner-actions {{
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }}

        .banner-btn-wa {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: #25D366;
            color: white;
            padding: 12px 24px;
            border-radius: 30px;
            text-decoration: none;
            font-weight: 700;
            font-size: 0.95rem;
            box-shadow: 0 6px 18px rgba(0,0,0,0.15);
            transition: all 0.3s ease;
        }}
        .banner-btn-wa:hover {{
            background: #1eb956;
            transform: translateY(-3px);
            color: white;
        }}

        .banner-btn-email {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(255, 255, 255, 0.95);
            color: var(--primary);
            padding: 12px 24px;
            border-radius: 30px;
            text-decoration: none;
            font-weight: 700;
            font-size: 0.95rem;
            box-shadow: 0 6px 18px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }}
        .banner-btn-email:hover {{
            background: white;
            color: var(--secondary);
            transform: translateY(-3px);
        }}

        /* Lightbox Modal */
        .lightbox {{
            display: none;
            position: fixed;
            z-index: 9999;
            width: 100%;
            height: 100%;
            top: 0; left: 0;
            background: rgba(0,0,0,0.85);
            backdrop-filter: blur(10px);
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}

        .lightbox-modal {{
            background: white;
            border-radius: 18px;
            padding: 30px;
            max-width: 780px;
            width: 100%;
            max-height: 90vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            position: relative;
            box-shadow: 0 25px 60px rgba(0,0,0,0.4);
            animation: zoomIn 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            overflow-y: auto;
        }}

        .lightbox-close {{
            position: absolute;
            top: 15px;
            right: 20px;
            color: #555;
            font-size: 32px;
            cursor: pointer;
            transition: color 0.3s;
            line-height: 1;
        }}
        .lightbox-close:hover {{
            color: var(--secondary);
        }}

        .lightbox-img-wrapper {{
            width: 100%;
            max-height: 50vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #fafafa;
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 20px;
        }}

        .lightbox-modal img {{
            max-width: 100%;
            max-height: 48vh;
            object-fit: contain;
            border-radius: 8px;
        }}

        .lightbox-details {{
            text-align: center;
            width: 100%;
        }}

        .lightbox-cat-badge {{
            display: inline-block;
            background: var(--gradient-subtle);
            color: var(--primary);
            padding: 4px 14px;
            border-radius: 20px;
            font-size: 0.82rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
            border: 1px solid rgba(43, 46, 131, 0.1);
        }}

        .lightbox-brand {{
            font-size: 0.9rem;
            font-weight: 700;
            color: var(--secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 6px;
        }}

        .lightbox-title {{
            font-size: 1.45rem;
            font-weight: 700;
            color: var(--primary);
            margin-bottom: 20px;
            line-height: 1.3;
        }}

        .lightbox-actions {{
            display: flex;
            gap: 15px;
            justify-content: center;
            flex-wrap: wrap;
        }}

        .lightbox-wa-btn {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: #25D366;
            color: white;
            padding: 12px 26px;
            border-radius: 30px;
            text-decoration: none;
            font-weight: 700;
            font-size: 0.95rem;
            box-shadow: 0 4px 15px rgba(37, 211, 102, 0.3);
            transition: all 0.3s ease;
        }}
        .lightbox-wa-btn:hover {{
            background: #1eb956;
            transform: translateY(-2px);
            color: white;
        }}

        .lightbox-email-btn {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: var(--primary);
            color: white;
            padding: 12px 26px;
            border-radius: 30px;
            text-decoration: none;
            font-weight: 700;
            font-size: 0.95rem;
            box-shadow: 0 4px 15px rgba(43, 46, 131, 0.25);
            transition: all 0.3s ease;
        }}
        .lightbox-email-btn:hover {{
            background: var(--secondary);
            transform: translateY(-2px);
            color: white;
        }}

        /* Why Choose Us Section */
        .why-choose {{
            background: white;
            padding: 80px 40px;
            margin: 40px 0;
            text-align: center;
            border-top: 2px solid rgba(0,0,0,0.05);
            border-bottom: 2px solid rgba(0,0,0,0.05);
        }}

        .why-choose h2 {{
            font-size: 2.3rem;
            color: var(--primary);
            margin-bottom: 20px;
        }}

        .why-grid {{
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 30px;
            max-width: 1200px;
            margin: 40px auto 0;
        }}

        .why-item {{
            flex: 1;
            min-width: 200px;
            max-width: 220px;
            padding: 25px 20px;
            background: #fdfdfd;
            border-radius: 12px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.04);
            border: 1px solid rgba(0,0,0,0.03);
            transition: transform 0.3s;
        }}
        .why-item:hover {{
            transform: translateY(-5px);
        }}

        .why-item i {{
            font-size: 2.5rem;
            color: var(--secondary);
            margin-bottom: 15px;
        }}

        .why-item h4 {{
            color: var(--primary);
            font-size: 1.1rem;
            line-height: 1.3;
        }}

        /* About Us Section */
        .about-section {{
            padding: 80px 40px;
            max-width: 1300px;
            margin: 0 auto;
        }}

        .about-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 50px;
            margin-top: 40px;
        }}

        .about-box {{
            background: white;
            padding: 40px;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.05);
            border: 1px solid rgba(0,0,0,0.04);
        }}

        .about-box h3 {{
            color: var(--primary);
            font-size: 1.6rem;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .about-box p {{
            color: var(--text-light);
            line-height: 1.7;
            margin-bottom: 16px;
            font-size: 1.05rem;
        }}

        .values-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 30px;
        }}

        .value-item {{
            display: flex;
            align-items: flex-start;
            gap: 15px;
        }}

        .value-icon {{
            width: 42px;
            height: 42px;
            border-radius: 50%;
            background: var(--gradient-subtle);
            color: var(--primary);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
            flex-shrink: 0;
        }}

        .value-text h4 {{
            color: var(--primary);
            font-size: 1.05rem;
            margin-bottom: 4px;
        }}

        .value-text p {{
            color: var(--text-light);
            font-size: 0.9rem;
            line-height: 1.4;
            margin-bottom: 0;
        }}

        /* Company Details */
        .company-details {{
            background: white;
            padding: 40px;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.05);
            border: 1px solid rgba(0,0,0,0.04);
        }}

        .company-details h3 {{
            color: var(--primary);
            font-size: 1.6rem;
            margin-bottom: 25px;
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .detail-row {{
            display: flex;
            align-items: center;
            padding: 14px 0;
            border-bottom: 1px solid #f0f0f0;
        }}

        .detail-row:last-child {{
            border-bottom: none;
        }}

        .detail-icon {{
            width: 36px;
            height: 36px;
            border-radius: 50%;
            background: var(--gradient-subtle);
            color: var(--secondary);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1rem;
            margin-right: 15px;
            flex-shrink: 0;
        }}

        .detail-label {{
            font-weight: 600;
            color: var(--primary);
            width: 140px;
            flex-shrink: 0;
            font-size: 0.95rem;
        }}

        .detail-value {{
            color: var(--text-main);
            font-size: 0.95rem;
            line-height: 1.4;
        }}

        /* Footer */
        footer {{
            background: white;
            padding: 50px 20px 30px;
            text-align: center;
            border-top: 1px solid #eee;
            margin-top: 40px;
        }}

        .footer-logo {{
            height: 60px;
            margin-bottom: 15px;
        }}

        .footer-tagline {{
            font-size: 1.2rem;
            color: var(--primary);
            font-weight: 600;
            margin-bottom: 15px;
        }}

        .footer-links {{
            margin: 15px 0;
        }}

        .footer-links a {{
            text-decoration: none;
            color: var(--text-light);
            margin: 0 15px;
            font-weight: 500;
            transition: color 0.3s;
        }}

        .footer-links a:hover {{
            color: var(--secondary);
        }}

        /* Floating Actions */
        .whatsapp-float {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            background-color: #25D366;
            color: white;
            border-radius: 50%;
            text-align: center;
            font-size: 35px;
            box-shadow: 0 10px 25px rgba(37, 211, 102, 0.4);
            z-index: 999;
            width: 60px;
            height: 60px;
            display: flex;
            align-items: center;
            justify-content: center;
            text-decoration: none;
            animation: pulse 2s infinite;
            transition: transform 0.3s;
        }}

        .whatsapp-float:hover {{
            transform: scale(1.1);
        }}

        .back-to-top {{
            position: fixed;
            bottom: 105px;
            right: 35px;
            background-color: var(--primary);
            color: white;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            text-decoration: none;
            box-shadow: 0 10px 25px rgba(43, 46, 131, 0.4);
            transition: all 0.3s ease;
            opacity: 0;
            visibility: hidden;
            z-index: 998;
        }}

        .back-to-top.show {{
            opacity: 1;
            visibility: visible;
        }}

        .back-to-top:hover {{
            background-color: var(--secondary);
            transform: scale(1.1);
        }}

        @keyframes pulse {{
            0% {{ box-shadow: 0 0 0 0 rgba(37, 211, 102, 0.6); }}
            70% {{ box-shadow: 0 0 0 18px rgba(37, 211, 102, 0); }}
            100% {{ box-shadow: 0 0 0 0 rgba(37, 211, 102, 0); }}
        }}

        @keyframes zoomIn {{
            from {{ opacity: 0; transform: scale(0.9); }}
            to {{ opacity: 1; transform: scale(1); }}
        }}

        @keyframes fadeInDown {{
            from {{ opacity: 0; transform: translateY(-20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        /* Responsive */
        @media (max-width: 992px) {{
            header {{ padding: 15px 30px; }}
            header.scrolled {{ padding: 8px 30px; }}
            .about-grid {{ grid-template-columns: 1fr; }}
            .hero h1 {{ font-size: 2.8rem; }}
            .gallery-section {{ padding: 50px 25px; }}
            .about-section {{ padding: 50px 25px; }}
        }}

        @media (max-width: 768px) {{
            header {{ 
                padding: 10px 15px; 
                background: rgba(255, 255, 255, 0.96); 
                backdrop-filter: blur(10px);
                box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            }}
            .logo-container img {{ height: 42px; }}
            header.scrolled .logo-container img {{ height: 38px; }}
            .nav-links a {{ font-size: 0.95rem; margin-right: 5px; }}
            
            .hero {{ padding: 110px 15px 50px; min-height: auto; }}
            .hero h1 {{ font-size: 2.2rem; }}
            .hero p {{ font-size: 1.1rem; }}
            
            .gallery-section {{ padding: 35px 15px; }}
            .section-title {{ font-size: 2rem; }}

            .view-mode-bar {{
                flex-direction: column;
                border-radius: 16px;
                padding: 8px;
            }}
            .view-mode-btn {{
                font-size: 0.85rem;
                padding: 8px 12px;
            }}
            
            .category-filter-bar {{
                display: flex;
                flex-wrap: nowrap;
                overflow-x: auto;
                justify-content: flex-start;
                padding-bottom: 12px;
                -webkit-overflow-scrolling: touch;
                scrollbar-width: none;
            }}
            .category-filter-bar::-webkit-scrollbar {{
                display: none;
            }}
            .cat-btn {{
                flex-shrink: 0;
                padding: 8px 14px;
                font-size: 0.85rem;
            }}

            .gallery-grid {{ 
                grid-template-columns: repeat(2, 1fr); 
                gap: 12px; 
            }}
            .img-wrapper {{ height: 150px; }}
            .product-info {{ padding: 10px 8px; }}
            .product-name {{ font-size: 0.82rem; min-height: 2.4em; margin-bottom: 8px; }}
            .product-badge {{ font-size: 0.65rem; padding: 3px 7px; top: 8px; left: 8px; }}
            .btn-enquire {{ font-size: 0.75rem; padding: 6px 12px; }}
            .btn-zoom {{ width: 28px; height: 28px; font-size: 0.75rem; }}

            .catalogue-banner {{ padding: 25px 20px; }}
            .banner-text h3 {{ font-size: 1.4rem; }}
            .banner-text p {{ font-size: 0.95rem; }}

            .why-choose {{ padding: 40px 15px; }}
            .why-grid {{ gap: 15px; }}
            .why-item {{ min-width: 140px; padding: 20px 10px; }}
            .why-item i {{ font-size: 2rem; }}
            .why-item h4 {{ font-size: 0.9rem; }}

            .about-box, .company-details {{ padding: 25px 15px; }}
            .values-grid {{ grid-template-columns: 1fr; }}
            .detail-label {{ width: 110px; font-size: 0.85rem; }}
            .detail-value {{ font-size: 0.85rem; }}

            .whatsapp-float {{
                width: 50px;
                height: 50px;
                bottom: 15px;
                right: 15px;
                font-size: 28px;
            }}
            .back-to-top {{
                width: 42px;
                height: 42px;
                bottom: 75px;
                right: 19px;
                font-size: 18px;
            }}
        }}

        @media (max-width: 480px) {{
            .gallery-grid {{
                grid-template-columns: repeat(2, 1fr);
                gap: 10px;
            }}
            .img-wrapper {{ height: 135px; }}
        }}
    </style>
</head>
<body>

    <!-- Header -->
    <header>
        <div class="logo-container">
            <a href="#"><img src="raw%20images/sterling%20company%20LOGOS/logo.svg" alt="Sterling Prime Logo"></a>
        </div>
        <div class="nav-links">
            <a href="#gallery">Catalogue</a>
            <a href="#about">About Us</a>
            <a href="https://wa.me/917041614713?text=Hi%20Sterling%20Prime,%20I%20would%20like%20to%20discuss%20corporate%20gifting%20requirements." target="_blank" class="nav-btn-contact"><i class="fas fa-comment-dots"></i> Contact</a>
        </div>
    </header>

    <!-- Hero -->
    <div class="hero">
        <div class="hero-badge">
            <i class="fas fa-crown"></i> India's Premier Corporate Gifting & Merchandise Partner
        </div>
        <h1>Premium Corporate Gifts & Catalogues for Every Occasion</h1>
        <p>At Sterling Prime, we don't just deliver gifts, we deliver experiences that build stronger connections.</p>
        
        <div class="hero-highlights">
            <div class="hero-chip"><i class="fas fa-cube"></i> {total_unified_items}+ Corporate Items & Catalogues</div>
            <div class="hero-chip"><i class="fas fa-star"></i> In-House + 30+ Leading Partner Brands</div>
            <div class="hero-chip"><i class="fas fa-palette"></i> Custom Corporate Branding</div>
            <div class="hero-chip"><i class="fas fa-shipping-fast"></i> Pan-India Fulfilment</div>
        </div>
    </div>

    <!-- Gallery Section -->
    <div class="gallery-section" id="gallery">
        <h2 class="section-title" data-aos="fade-up">Corporate Gifting Range & Catalogues</h2>
        <p class="section-subtitle" data-aos="fade-up" data-aos-delay="100">Explore our unified collection of in-house corporate gifts and curated brand partner catalogues across all categories. Strictly deduplicated so you get the best options at every price slab.</p>

        <!-- View Mode Filter Bar (All / In-House / Partner Brands) -->
        <div class="view-mode-bar" data-aos="fade-up" data-aos-delay="120">
            <button type="button" class="view-mode-btn active" data-type-filter="all">
                <i class="fas fa-layer-group"></i> All Items ({total_unified_items})
            </button>
            <button type="button" class="view-mode-btn" data-type-filter="inhouse">
                <i class="fas fa-gem"></i> In-House Products ({inhouse_total})
            </button>
            <button type="button" class="view-mode-btn" data-type-filter="partner_catalogue">
                <i class="fas fa-book-open"></i> Brand Partner Catalogues ({partner_total})
            </button>
        </div>

        <!-- Controls: Search & Category Filter Pills -->
        <div class="gallery-controls" data-aos="fade-up" data-aos-delay="150">
            <!-- Search Bar -->
            <div class="search-wrapper">
                <i class="fas fa-search search-icon"></i>
                <input type="text" id="productSearch" placeholder="Search {total_unified_items}+ items by brand (boAt, Noise, Borosil...), category, or keyword..." autocomplete="off">
                <button type="button" id="clearSearch" class="clear-search-btn" title="Clear search"><i class="fas fa-times"></i></button>
            </div>

            <!-- Category Pills Bar -->
            <div class="category-filter-bar" id="categoryFilterBar">
{cat_pills_str}
            </div>

            <!-- Status & Count Bar -->
            <div class="gallery-status-bar">
                <div id="productCount">Showing <strong>{total_unified_items}</strong> items in <strong>All Catalogue Items</strong></div>
                <button type="button" id="resetFilterBtn" class="reset-filter-btn" onclick="resetAllFilters()">Clear Filters</button>
            </div>
        </div>

        <!-- Product Cards Grid -->
        <div class="gallery-grid" id="galleryGrid">

{cards_str}

            <!-- No Results Found State -->
            <div id="noResults" class="no-results">
                <i class="fas fa-search"></i>
                <h3>No Items Found</h3>
                <p>We couldn't find any products or catalogues matching your current filters.</p>
                <button type="button" onclick="resetAllFilters()"><i class="fas fa-redo"></i> Reset Filters</button>
            </div>

        </div>

        <!-- Catalogue PDF Banner -->
        <div class="catalogue-banner" data-aos="fade-up">
            <div class="catalogue-banner-inner">
                <div class="banner-text">
                    <h3><i class="fas fa-file-pdf"></i> Need Any Complete Brand Catalogue in PDF?</h3>
                    <p>Request individual PDF catalogues for boAt, Noise, Borosil, Milton, Samsonite, FNP, Procter Joining Kits, or our master Sterling Prime range with bulk pricing and logo mockup guidelines.</p>
                </div>
                <div class="banner-actions">
                    <a href="https://wa.me/917041614713?text=Hi%20Sterling%20Prime,%20please%20share%20the%20complete%20B2B%20Corporate%20Gifting%20Catalogues%20PDF%20with%20me." target="_blank" class="banner-btn-wa">
                        <i class="fab fa-whatsapp"></i> Request on WhatsApp
                    </a>
                    <a href="mailto:info@mysterling.in?subject=Request%20for%20Corporate%20Gifting%20Catalogues&body=Hi%20Sterling%20Prime%20Team,%0A%0APlease%20share%20your%20B2B%20Corporate%20Gifting%20Catalogues%20and%20bulk%20quotation%20guidelines.%0A%0AThank%20you!" class="banner-btn-email">
                        <i class="fas fa-envelope"></i> Request by Email
                    </a>
                </div>
            </div>
        </div>
    </div>

    <!-- Enhanced Lightbox Modal -->
    <div id="lightbox" class="lightbox" onclick="closeLightboxOnBackdrop(event)">
        <div class="lightbox-modal" onclick="event.stopPropagation();">
            <span class="lightbox-close" onclick="closeLightbox()">&times;</span>
            <div class="lightbox-img-wrapper" id="lightboxImgWrapper">
                <img id="lightbox-img" src="" alt="Product Image">
            </div>
            <div class="lightbox-details">
                <div id="lightbox-brand" class="lightbox-brand">Sterling Prime</div>
                <span id="lightbox-cat" class="lightbox-cat-badge">Category</span>
                <h3 id="lightbox-title" class="lightbox-title">Product Name</h3>
                <div class="lightbox-actions">
                    <a id="lightbox-wa-btn" href="#" target="_blank" class="lightbox-wa-btn">
                        <i class="fab fa-whatsapp"></i> Enquire on WhatsApp
                    </a>
                    <a id="lightbox-email-btn" href="#" class="lightbox-email-btn">
                        <i class="fas fa-envelope"></i> Email Enquiry
                    </a>
                </div>
            </div>
        </div>
    </div>

    <!-- Why Choose Us -->
    <div class="why-choose">
        <h2 data-aos="fade-up">Why Choose Sterling Prime?</h2>
        <div class="why-grid">
            <div class="why-item" data-aos="flip-left" data-aos-delay="100">
                <i class="fas fa-gift"></i>
                <h4>{total_unified_items}+ Products & Catalogues</h4>
            </div>
            <div class="why-item" data-aos="flip-left" data-aos-delay="200">
                <i class="fas fa-medal"></i>
                <h4>Custom Branding & Printing</h4>
            </div>
            <div class="why-item" data-aos="flip-left" data-aos-delay="300">
                <i class="fas fa-truck-fast"></i>
                <h4>Pan-India Delivery</h4>
            </div>
            <div class="why-item" data-aos="flip-left" data-aos-delay="400">
                <i class="fas fa-headset"></i>
                <h4>Dedicated B2B Support</h4>
            </div>
            <div class="why-item" data-aos="flip-left" data-aos-delay="500">
                <i class="fas fa-handshake-angle"></i>
                <h4>Trusted Corporate Partner</h4>
            </div>
        </div>
    </div>

    <!-- About Us Section -->
    <div class="about-section" id="about">
        <h2 class="section-title" data-aos="fade-up">About Us</h2>
        <div class="about-grid">
            
            <!-- Our Story & Values -->
            <div class="about-box" data-aos="fade-right">
                <h3><i class="fas fa-book-open"></i> Our Story</h3>
                <p>Sterling Prime is a trusted name in the world of corporate gifting and promotional solutions.</p>
                <p>Founded with a vision to deliver premium quality products and exceptional service, we partner with leading businesses across India to build long-term relationships through thoughtful gifts.</p>
                <p>From practical desk accessories, luxury drinkware, and smart electronics to executive joiner kits, festive gourmet hampers, and medical communication models, our portfolio covers every corporate occasion and budget.</p>
                
                <h3 style="margin-top: 40px;"><i class="fas fa-star"></i> Our Values</h3>
                <div class="values-grid">
                    <div class="value-item">
                        <div class="value-icon"><i class="fas fa-award"></i></div>
                        <div class="value-text">
                            <h4>Quality First</h4>
                            <p>We ensure premium quality in every product.</p>
                        </div>
                    </div>
                    <div class="value-item">
                        <div class="value-icon"><i class="fas fa-users"></i></div>
                        <div class="value-text">
                            <h4>Customer Focus</h4>
                            <p>Our customers' satisfaction is at the heart of everything we do.</p>
                        </div>
                    </div>
                    <div class="value-item">
                        <div class="value-icon"><i class="fas fa-lightbulb"></i></div>
                        <div class="value-text">
                            <h4>Innovation</h4>
                            <p>We constantly innovate to offer unique and practical gifting solutions.</p>
                        </div>
                    </div>
                    <div class="value-item">
                        <div class="value-icon"><i class="fas fa-handshake"></i></div>
                        <div class="value-text">
                            <h4>Integrity</h4>
                            <p>We believe in transparent dealings and long-term relationships.</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Company Details -->
            <div class="company-details" data-aos="fade-left">
                <h3><i class="fas fa-building"></i> Company Details</h3>
                <div style="margin-top: 25px;">
                    <div class="detail-row">
                        <div class="detail-icon"><i class="fas fa-id-badge"></i></div>
                        <div class="detail-label">Company Name</div>
                        <div class="detail-value">Sterling Prime</div>
                    </div>
                    <div class="detail-row">
                        <div class="detail-icon"><i class="fas fa-file-invoice"></i></div>
                        <div class="detail-label">GSTIN</div>
                        <div class="detail-value">27AAECN3915G1ZJ</div>
                    </div>
                    <div class="detail-row">
                        <div class="detail-icon"><i class="fas fa-calendar-alt"></i></div>
                        <div class="detail-label">Established In</div>
                        <div class="detail-value">Maharashtra, India</div>
                    </div>
                    <div class="detail-row">
                        <div class="detail-icon"><i class="fas fa-map-marker-alt"></i></div>
                        <div class="detail-label">Head Office</div>
                        <div class="detail-value">Unit No. 169, 1st Floor, A2, Shah and Nahar Industrial Estate, Sitaram Jadhav Marg, Lower Parel, Mumbai, Maharashtra - 400013.</div>
                    </div>
                    <div class="detail-row">
                        <div class="detail-icon"><i class="fas fa-phone-alt"></i></div>
                        <div class="detail-label">Contact</div>
                        <div class="detail-value">+91 70416 14713 <br> +91 87582 94908</div>
                    </div>
                    <div class="detail-row">
                        <div class="detail-icon"><i class="fas fa-envelope"></i></div>
                        <div class="detail-label">Email</div>
                        <div class="detail-value">info@mysterling.in</div>
                    </div>
                    <div class="detail-row">
                        <div class="detail-icon"><i class="fas fa-truck"></i></div>
                        <div class="detail-label">Delivery</div>
                        <div class="detail-value">Pan India Delivery</div>
                    </div>
                    <div class="detail-row">
                        <div class="detail-icon"><i class="fas fa-clock"></i></div>
                        <div class="detail-label">Delivery Time</div>
                        <div class="detail-value">5-7 Days from date of confirmation</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Footer -->
    <footer>
        <img src="raw%20images/sterling%20company%20LOGOS/logo.svg" alt="Sterling Prime Logo" class="footer-logo">
        <div class="footer-tagline">Thoughtful Gifts. Stronger Relationships.</div>
        <div class="footer-links">
            <a href="#gallery">Catalogue</a>
            <a href="#about">About Us</a>
            <a href="https://wa.me/917041614713?text=Hi%20Sterling%20Prime,%20I%20would%20like%20to%20enquire%20about%20corporate%20gifting." target="_blank">WhatsApp Us</a>
        </div>
        <p style="color: #666; margin-top: 20px;">&copy; 2026 Sterling Prime. All Rights Reserved.</p>
        <p style="color: #666; margin-top: 5px;">www.sterlingprime.com &bull; Pan-India Corporate Gifting Solutions</p>
    </footer>

    <!-- WhatsApp Floating Icon -->
    <a href="https://wa.me/917041614713?text=Hi%20Sterling%20Prime,%20I'd%20like%20to%20discuss%20corporate%20gifting%20products." class="whatsapp-float" target="_blank" aria-label="Chat on WhatsApp">
        <i class="fab fa-whatsapp"></i>
    </a>

    <!-- Back to Top Button -->
    <a href="#" class="back-to-top" aria-label="Back to top" id="backToTop">
        <i class="fas fa-arrow-up"></i>
    </a>

    <!-- Scripts -->
    <script src="https://unpkg.com/aos@2.3.1/dist/aos.js"></script>
    <script>
        // Ensure page loads at top
        if ('scrollRestoration' in history) {{
            history.scrollRestoration = 'manual';
        }}
        window.onload = function() {{
            if (window.location.hash) {{
                history.replaceState("", document.title, window.location.pathname + window.location.search);
            }}
            setTimeout(function() {{
                window.scrollTo(0, 0);
            }}, 10);
        }};

        AOS.init({{
            once: true,
            offset: 50,
            duration: 800,
            easing: 'ease-out-cubic'
        }});

        // Lightbox functionality
        const lightbox = document.getElementById('lightbox');
        const lightboxImg = document.getElementById('lightbox-img');
        const lightboxTitle = document.getElementById('lightbox-title');
        const lightboxCat = document.getElementById('lightbox-cat');
        const lightboxBrand = document.getElementById('lightbox-brand');
        const lightboxWaBtn = document.getElementById('lightbox-wa-btn');
        const lightboxEmailBtn = document.getElementById('lightbox-email-btn');

        function openLightbox(src, title, catName, brand, isPhoto) {{
            lightboxImg.src = src;
            lightboxImg.alt = title;
            lightboxTitle.textContent = title;
            lightboxCat.textContent = catName || 'Corporate Gift';
            lightboxBrand.textContent = brand || 'Sterling Prime';

            const waMsg = encodeURIComponent("Hi Sterling Prime, I am interested in '" + title + "' (Brand: " + (brand || 'Sterling Prime') + ", Category: " + (catName || 'Corporate Gift') + "). Please share pricing, customization branding and catalogue PDF.");
            lightboxWaBtn.href = "https://wa.me/917041614713?text=" + waMsg;

            const emailSub = encodeURIComponent("Enquiry for " + title + " - Sterling Prime");
            const emailBody = encodeURIComponent("Hi Sterling Prime Team,\\n\\nI am interested in '" + title + "' (Brand: " + (brand || 'Sterling Prime') + ", Category: " + (catName || 'Corporate Gift') + ").\\n\\nPlease share the pricing, MOQ, customization details and catalogue PDF.\\n\\nThank you!");
            lightboxEmailBtn.href = "mailto:info@mysterling.in?subject=" + emailSub + "&body=" + emailBody;

            lightbox.style.display = 'flex';
            document.body.style.overflow = 'hidden';
        }}

        function closeLightbox() {{
            lightbox.style.display = 'none';
            document.body.style.overflow = 'auto';
        }}

        function closeLightboxOnBackdrop(e) {{
            if (e.target === lightbox) {{
                closeLightbox();
            }}
        }}

        document.addEventListener('keydown', (e) => {{
            if (e.key === 'Escape' && lightbox.style.display === 'flex') {{
                closeLightbox();
            }}
        }});

        // Search, Category, and View Mode Filter Logic
        let currentCategory = 'all';
        let currentTypeFilter = 'all';
        let searchQuery = '';

        const searchInput = document.getElementById('productSearch');
        const clearSearchBtn = document.getElementById('clearSearch');
        const catButtons = document.querySelectorAll('.cat-btn');
        const viewModeButtons = document.querySelectorAll('.view-mode-btn');
        const productCards = document.querySelectorAll('.product-card');
        const countDisplay = document.getElementById('productCount');
        const noResults = document.getElementById('noResults');
        const resetFilterBtn = document.getElementById('resetFilterBtn');

        function applyFilters() {{
            let visibleCount = 0;
            const q = searchQuery.toLowerCase().trim();

            productCards.forEach(card => {{
                const cat = card.getAttribute('data-category');
                const type = card.getAttribute('data-type');
                const name = card.getAttribute('data-name').toLowerCase();
                const brand = (card.getAttribute('data-brand') || '').toLowerCase();
                const catName = card.getAttribute('data-category-name').toLowerCase();

                const matchesCat = (currentCategory === 'all' || cat === currentCategory);
                const matchesType = (currentTypeFilter === 'all' || type === currentTypeFilter);
                const matchesSearch = (!q || name.includes(q) || brand.includes(q) || catName.includes(q));

                if (matchesCat && matchesType && matchesSearch) {{
                    card.style.display = 'flex';
                    visibleCount++;
                }} else {{
                    card.style.display = 'none';
                }}
            }});

            // Update UI count
            let catLabel = 'All Catalogue Items';
            if (currentCategory !== 'all') {{
                const activeBtn = document.querySelector(`.cat-btn[data-cat="${{currentCategory}}"]`);
                if (activeBtn) {{
                    catLabel = activeBtn.getAttribute('data-cat-name');
                }}
            }}

            let typeLabel = '';
            if (currentTypeFilter === 'inhouse') typeLabel = ' (In-House Only)';
            else if (currentTypeFilter === 'partner_catalogue') typeLabel = ' (Brand Partner Catalogues)';

            let statusHtml = `Showing <strong>${{visibleCount}}</strong> item${{visibleCount === 1 ? '' : 's'}} in <strong>${{catLabel}}</strong>${{typeLabel}}`;
            if (q) {{
                statusHtml += ` matching "<strong>${{escapeHtml(q)}}</strong>"`;
            }}
            countDisplay.innerHTML = statusHtml;

            // Empty state
            if (visibleCount === 0) {{
                noResults.style.display = 'block';
            }} else {{
                noResults.style.display = 'none';
            }}

            // Show or hide reset button
            if (currentCategory !== 'all' || currentTypeFilter !== 'all' || q) {{
                resetFilterBtn.style.display = 'inline-block';
            }} else {{
                resetFilterBtn.style.display = 'none';
            }}
        }}

        function escapeHtml(text) {{
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }}

        // View Mode button handlers
        viewModeButtons.forEach(btn => {{
            btn.addEventListener('click', () => {{
                viewModeButtons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentTypeFilter = btn.getAttribute('data-type-filter');
                applyFilters();
            }});
        }});

        // Category button click handlers
        catButtons.forEach(btn => {{
            btn.addEventListener('click', () => {{
                catButtons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentCategory = btn.getAttribute('data-cat');
                applyFilters();
            }});
        }});

        // Search input handlers
        searchInput.addEventListener('input', (e) => {{
            searchQuery = e.target.value;
            if (searchQuery.trim().length > 0) {{
                clearSearchBtn.style.display = 'block';
            }} else {{
                clearSearchBtn.style.display = 'none';
            }}
            applyFilters();
        }});

        clearSearchBtn.addEventListener('click', () => {{
            searchInput.value = '';
            searchQuery = '';
            clearSearchBtn.style.display = 'none';
            searchInput.focus();
            applyFilters();
        }});

        function resetAllFilters() {{
            searchInput.value = '';
            searchQuery = '';
            clearSearchBtn.style.display = 'none';
            currentCategory = 'all';
            currentTypeFilter = 'all';
            catButtons.forEach(b => {{
                b.classList.remove('active');
                if (b.getAttribute('data-cat') === 'all') {{
                    b.classList.add('active');
                }}
            }});
            viewModeButtons.forEach(b => {{
                b.classList.remove('active');
                if (b.getAttribute('data-type-filter') === 'all') {{
                    b.classList.add('active');
                }}
            }});
            applyFilters();
        }}

        // Header and back to top
        const backToTopButton = document.getElementById('backToTop');
        const header = document.querySelector('header');
        
        window.addEventListener('scroll', () => {{
            if (window.scrollY > 50) {{
                header.classList.add('scrolled');
            }} else {{
                header.classList.remove('scrolled');
            }}
            
            const scrollPercent = window.scrollY / (document.documentElement.scrollHeight - window.innerHeight);
            if (scrollPercent > 0.3) {{
                backToTopButton.classList.add('show');
            }} else {{
                backToTopButton.classList.remove('show');
            }}
        }});
        
        backToTopButton.addEventListener('click', (e) => {{
            e.preventDefault();
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }});
    </script>
</body>
</html>
'''

output_path = os.path.join(repo_dir, "index.html")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"SUCCESS: Generated complete index.html with {total_unified_items} items across all catalogues!")
