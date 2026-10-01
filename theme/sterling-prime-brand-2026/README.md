# Sterling Prime — 2026 Brand Theme

Standalone full-stack-ready theme prototype based on the supplied Sterling Prime design guide and the real product images in this repository.

## Run locally
```
cd theme/sterling-prime-brand-2026
node server.js
```
Open http://localhost:3000

## Theme direction
- 60% clean white/Lavender Mist surfaces
- 30% Sterling Blue/Midnight Navy structure
- 10% purple/magenta/coral/orange signature accents
- Poppins headings + Inter body
- pill CTA language, 20px cards, restrained gradients
- light/dark mode
- responsive desktop/tablet/mobile layouts
- reduced-motion support and visible focus states

## Functional prototype
- Product cards and category filters
- Quick-view product modal
- Quote modal with required fields
- POST /api/quotes stores submissions in data/quotes.json
- GET /api/products returns product data
- GET /api/health returns service status
- Existing repository images are served through /raw-images/*

## Important
This is on the isolated branch `theme/sterling-prime-brand-2026`; it does not replace the live `main` homepage. The goal is to review the visual system and interaction pattern first, then integrate the approved theme into the live stack.