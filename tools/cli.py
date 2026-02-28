#!/usr/bin/env python3
"""Shopify Starter Templates — Template Generator & Validator CLI."""

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Optional

TEMPLATES_DIR = Path(__file__).parent.parent
TEMPLATES = {
    "minimal-store": "Clean minimal e-commerce store with Shopify Buy Button SDK",
    "dropship-starter": "High-conversion dropshipping store with flash sales & countdown",
    "landing-product": "Single product landing page with A/B testing",
}

# ── Validation ──────────────────────────────────────────────────────────

class ValidationResult:
    """Result of a template validation check."""

    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.passed: list[str] = []

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0

    def error(self, msg: str):
        self.errors.append(msg)

    def warn(self, msg: str):
        self.warnings.append(msg)

    def pass_(self, msg: str):
        self.passed.append(msg)

    def summary(self) -> str:
        lines = []
        for p in self.passed:
            lines.append(f"  ✅ {p}")
        for w in self.warnings:
            lines.append(f"  ⚠️  {w}")
        for e in self.errors:
            lines.append(f"  ❌ {e}")
        status = "PASS" if self.ok else "FAIL"
        lines.append(f"  Result: {status} ({len(self.passed)} passed, {len(self.warnings)} warnings, {len(self.errors)} errors)")
        return "\n".join(lines)


def validate_html(filepath: Path) -> ValidationResult:
    """Validate an HTML template file."""
    result = ValidationResult()
    if not filepath.exists():
        result.error(f"File not found: {filepath}")
        return result

    content = filepath.read_text(encoding="utf-8")

    # DOCTYPE
    if "<!DOCTYPE html>" in content or "<!doctype html>" in content:
        result.pass_("Has DOCTYPE declaration")
    else:
        result.error("Missing DOCTYPE declaration")

    # charset
    if 'charset="UTF-8"' in content or "charset='UTF-8'" in content or 'charset="utf-8"' in content:
        result.pass_("Has UTF-8 charset")
    else:
        result.error("Missing UTF-8 charset meta tag")

    # viewport
    if "viewport" in content:
        result.pass_("Has viewport meta tag")
    else:
        result.error("Missing viewport meta tag (not mobile-friendly)")

    # title
    title_match = re.search(r"<title>(.+?)</title>", content)
    if title_match:
        title = title_match.group(1)
        if len(title) < 10:
            result.warn(f"Title too short: '{title}' ({len(title)} chars, recommend 30-60)")
        elif len(title) > 70:
            result.warn(f"Title too long: '{title[:50]}...' ({len(title)} chars, recommend 30-60)")
        else:
            result.pass_(f"Has title tag ({len(title)} chars)")
    else:
        result.error("Missing <title> tag")

    # meta description
    desc_match = re.search(r'<meta\s+name="description"\s+content="(.+?)"', content)
    if desc_match:
        desc = desc_match.group(1)
        if len(desc) < 50:
            result.warn(f"Meta description too short ({len(desc)} chars, recommend 120-155)")
        else:
            result.pass_(f"Has meta description ({len(desc)} chars)")
    else:
        result.warn("Missing meta description tag")

    # OG tags
    og_count = len(re.findall(r'property="og:', content))
    if og_count >= 2:
        result.pass_(f"Has {og_count} Open Graph tags")
    else:
        result.warn(f"Only {og_count} OG tags found (recommend at least og:title + og:description)")

    # Images with alt
    imgs = re.findall(r"<img\s[^>]*>", content, re.DOTALL)
    imgs_with_alt = [i for i in imgs if 'alt="' in i or "alt='" in i]
    if imgs:
        ratio = len(imgs_with_alt) / len(imgs)
        if ratio >= 0.9:
            result.pass_(f"Images have alt text ({len(imgs_with_alt)}/{len(imgs)})")
        else:
            result.warn(f"Some images missing alt text ({len(imgs_with_alt)}/{len(imgs)})")
    else:
        result.pass_("No images to check")

    # Loading lazy
    lazy_count = content.count('loading="lazy"')
    if lazy_count > 0:
        result.pass_(f"Uses lazy loading ({lazy_count} images)")
    elif len(imgs) > 2:
        result.warn("Consider adding loading='lazy' to below-fold images")

    # Canonical URL
    if 'rel="canonical"' in content:
        result.pass_("Has canonical URL")
    else:
        result.warn("Missing canonical URL")

    # Accessibility basics
    aria_count = len(re.findall(r'aria-label', content))
    if aria_count > 0:
        result.pass_(f"Has ARIA labels ({aria_count})")
    else:
        result.warn("No ARIA labels found (accessibility concern)")

    # Check for inline event handlers (bad practice)
    onclick_count = len(re.findall(r'\son\w+="', content))
    if onclick_count == 0:
        result.pass_("No inline event handlers")
    else:
        result.warn(f"Found {onclick_count} inline event handlers (prefer addEventListener)")

    # HTML size
    size_kb = len(content.encode("utf-8")) / 1024
    if size_kb > 100:
        result.warn(f"HTML file is large ({size_kb:.1f} KB)")
    else:
        result.pass_(f"HTML size OK ({size_kb:.1f} KB)")

    return result


def validate_template(template_name: str) -> ValidationResult:
    """Validate a template directory."""
    template_dir = TEMPLATES_DIR / template_name
    result = ValidationResult()

    if not template_dir.exists():
        result.error(f"Template directory not found: {template_dir}")
        return result

    index = template_dir / "index.html"
    if not index.exists():
        result.error(f"Missing index.html in {template_name}/")
        return result

    return validate_html(index)


def validate_all() -> dict[str, ValidationResult]:
    """Validate all templates."""
    results = {}
    for name in TEMPLATES:
        template_dir = TEMPLATES_DIR / name
        if template_dir.exists():
            results[name] = validate_template(name)
    return results


# ── Generator ───────────────────────────────────────────────────────────

def generate_template(
    template_name: str,
    output_dir: str,
    store_name: str = "My Store",
    primary_color: str = "#0ea5e9",
    currency: str = "USD",
) -> bool:
    """Generate a customized template from a base template."""
    src = TEMPLATES_DIR / template_name
    dst = Path(output_dir)

    if not src.exists():
        print(f"❌ Template '{template_name}' not found.")
        print(f"   Available: {', '.join(TEMPLATES.keys())}")
        return False

    if dst.exists():
        print(f"❌ Output directory already exists: {dst}")
        return False

    # Copy template
    shutil.copytree(src, dst)

    # Customize
    for html_file in dst.rglob("*.html"):
        content = html_file.read_text(encoding="utf-8")
        content = content.replace("BRAND", store_name)
        content = content.replace("Your Store", store_name)
        content = content.replace("Your Brand", store_name)
        content = content.replace("yourstore.com", f"{store_name.lower().replace(' ', '')}.com")
        html_file.write_text(content, encoding="utf-8")

    # Create config
    config = {
        "name": store_name,
        "template": template_name,
        "primaryColor": primary_color,
        "currency": currency,
        "createdAt": "2026-02-28",
    }
    (dst / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")

    print(f"✅ Template '{template_name}' generated at: {dst}")
    print(f"   Store: {store_name}")
    print(f"   Open: file://{dst.absolute()}/index.html")
    return True


# ── Preview Server ──────────────────────────────────────────────────────

def preview(template_name: str, port: int = 8080):
    """Start a local preview server."""
    import http.server
    import functools

    template_dir = TEMPLATES_DIR / template_name
    if not template_dir.exists():
        print(f"❌ Template '{template_name}' not found.")
        return

    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(template_dir))
    print(f"🌐 Preview: http://localhost:{port}")
    print(f"   Template: {template_name}")
    print("   Press Ctrl+C to stop")
    with http.server.HTTPServer(("", port), handler) as httpd:
        httpd.serve_forever()


# ── List ────────────────────────────────────────────────────────────────

def list_templates():
    """List all available templates."""
    print("📦 Available Templates:\n")
    for name, desc in TEMPLATES.items():
        template_dir = TEMPLATES_DIR / name
        exists = "✅" if template_dir.exists() else "❌"
        file_count = len(list(template_dir.rglob("*"))) if template_dir.exists() else 0
        print(f"  {exists} {name}")
        print(f"     {desc}")
        if template_dir.exists():
            print(f"     Files: {file_count}")
        print()


# ── CLI ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="shopify-templates",
        description="🛍️ Shopify Starter Templates — Generator & Validator",
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # list
    sub.add_parser("list", help="List available templates")

    # validate
    p_val = sub.add_parser("validate", help="Validate templates")
    p_val.add_argument("template", nargs="?", help="Template name (all if omitted)")

    # generate
    p_gen = sub.add_parser("generate", help="Generate a customized template")
    p_gen.add_argument("template", help="Template name")
    p_gen.add_argument("output", help="Output directory")
    p_gen.add_argument("--name", default="My Store", help="Store name")
    p_gen.add_argument("--color", default="#0ea5e9", help="Primary color hex")
    p_gen.add_argument("--currency", default="USD", help="Currency code")

    # preview
    p_prev = sub.add_parser("preview", help="Start preview server")
    p_prev.add_argument("template", help="Template name")
    p_prev.add_argument("--port", type=int, default=8080, help="Port (default 8080)")

    args = parser.parse_args()

    if args.command == "list":
        list_templates()
    elif args.command == "validate":
        if args.template:
            result = validate_template(args.template)
            print(f"\n🔍 Validating: {args.template}")
            print(result.summary())
            sys.exit(0 if result.ok else 1)
        else:
            results = validate_all()
            all_ok = True
            for name, result in results.items():
                print(f"\n🔍 {name}")
                print(result.summary())
                if not result.ok:
                    all_ok = False
            sys.exit(0 if all_ok else 1)
    elif args.command == "generate":
        ok = generate_template(args.template, args.output, args.name, args.color, args.currency)
        sys.exit(0 if ok else 1)
    elif args.command == "preview":
        preview(args.template, args.port)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
