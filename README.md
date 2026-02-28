# Shopify Starter Templates

🛍️ Production-ready e-commerce starter templates with SEO validation, A/B testing, and template generator CLI.

## Templates

| Template | Style | Use Case | Preview |
|----------|-------|----------|---------|
| `minimal-store` | Clean & Modern | Brand storefront with Shopify Buy Button SDK | `make preview-minimal` |
| `dropship-starter` | Bold & Urgent | High-conversion dropshipping store with flash sales | `make preview-dropship` |
| `landing-product` | Conversion-focused | Single product landing page with A/B testing | `make preview-landing` |

## Quick Start

```bash
# Clone
git clone https://github.com/platoba/Shopify-Starter-Templates.git
cd Shopify-Starter-Templates

# Preview a template
make preview-minimal    # → http://localhost:8081
make preview-dropship   # → http://localhost:8082
make preview-landing    # → http://localhost:8083

# Or use Docker
make docker-up          # Starts all 3 preview servers
```

## Template Generator CLI

Generate customized templates from the command line:

```bash
# List templates
python tools/cli.py list

# Generate a customized store
python tools/cli.py generate minimal-store ./my-store --name "Cool Brand" --currency EUR

# Validate templates (SEO, accessibility, performance)
python tools/cli.py validate

# Preview a template
python tools/cli.py preview dropship-starter --port 8080
```

## Features

### 🎨 3 Production Templates
- **minimal-store** — Shopify Buy Button SDK integration, mobile-first, smooth animations
- **dropship-starter** — Countdown timers, flash deals, social proof, category navigation
- **landing-product** — Conversion-optimized layout, A/B test ready, trust badges

### 📦 9 Reusable Components
Drop-in HTML components for any template:
- `hero.html` — Hero banner with CTA
- `header.html` — Responsive navigation
- `footer.html` — Multi-column footer
- `features.html` — Feature grid
- `testimonials.html` — Customer reviews
- `pricing.html` — Pricing table
- `faq.html` — Accordion FAQ
- `cta.html` — Call-to-action section
- `newsletter.html` — Email signup form

### 🔧 Shared Assets
- `theme.css` — CSS custom properties for easy theming
- `ab-testing.js` — Built-in A/B testing framework
- `theme-switcher.js` — Dark/light mode toggle

### ✅ Template Validator
Built-in validation checks:
- SEO (title, meta, OG tags, canonical, heading hierarchy)
- Accessibility (ARIA labels, form labels, landmarks)
- Performance (lazy loading, render-blocking, file size)
- Mobile (viewport, responsive classes, grid/flex)
- Best practices (no inline handlers, alt text)

### 🧪 Test Suite
- **65+ tests** across 2 test files
- Template validation tests (all 3 templates)
- SEO compliance tests (title, meta, h1, OG tags)
- Accessibility tests (ARIA, form labels, landmarks)
- Performance tests (lazy loading, render-blocking)
- Component tests (existence, content, structure)
- Generator tests (create, customize, config)

## Development

```bash
# Install dev deps
pip install pytest pytest-cov ruff

# Run tests
make test

# Run with coverage
make test-cov

# Lint
make lint

# Validate HTML
make validate
```

## Project Structure

```
Shopify-Starter-Templates/
├── minimal-store/        # Clean brand storefront template
│   └── index.html
├── dropship-starter/     # Dropshipping store template
│   └── index.html
├── landing-product/      # Single product landing page
│   └── index.html
├── components/           # 9 reusable HTML components
│   ├── hero.html
│   ├── header.html
│   ├── footer.html
│   ├── features.html
│   ├── testimonials.html
│   ├── pricing.html
│   ├── faq.html
│   ├── cta.html
│   └── newsletter.html
├── shared/
│   ├── styles/theme.css
│   └── scripts/
│       ├── ab-testing.js
│       └── theme-switcher.js
├── tools/
│   └── cli.py            # Generator & validator CLI
├── tests/
│   ├── test_templates.py # Template & generator tests
│   └── test_seo.py       # SEO & accessibility tests
├── docker-compose.yml    # Multi-template preview
├── Dockerfile
├── Makefile
├── pyproject.toml
└── README.md
```

## Docker

```bash
# Start all preview servers
docker compose up -d

# Access templates:
# minimal-store   → http://localhost:8081
# dropship-starter → http://localhost:8082
# landing-product → http://localhost:8083

# Run tests in Docker
docker compose run --rm test
```

## License

MIT

## 🔗 Related Projects

- [Shopify-Scout](https://github.com/platoba/Shopify-Scout) — AI Shopify store analyzer
- [AI-Listing-Writer](https://github.com/platoba/AI-Listing-Writer) — AI product listing generator
- [MultiAffiliateTGBot](https://github.com/platoba/MultiAffiliateTGBot) — Multi-platform affiliate bot
- [SEO-Audit-CLI](https://github.com/platoba/SEO-Audit-CLI) — SEO audit command-line tool
