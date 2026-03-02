#!/usr/bin/env python3
"""Template comparison tool for Shopify Starter Templates."""

import json
import re
from pathlib import Path
from typing import Dict, List


class TemplateComparator:
    """Compare multiple templates across various metrics."""

    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir

    def analyze_template(self, template_name: str) -> Dict:
        """Analyze a single template."""
        template_dir = self.templates_dir / template_name
        index_html = template_dir / "index.html"

        if not index_html.exists():
            return {"error": f"Template {template_name} not found"}

        content = index_html.read_text(encoding="utf-8")

        # File size
        file_size_kb = round(len(content.encode("utf-8")) / 1024, 2)

        # Count elements
        metrics = {
            "name": template_name,
            "file_size_kb": file_size_kb,
            "total_lines": len(content.splitlines()),
            "images": content.count("<img"),
            "links": content.count("<a"),
            "buttons": content.count("<button") + content.count('type="button"'),
            "forms": content.count("<form"),
            "sections": content.count("<section"),
            "scripts": content.count("<script"),
            "styles": content.count("<style") + content.count('<link rel="stylesheet"'),
        }

        # SEO metrics
        title_match = re.search(r"<title>(.+?)</title>", content)
        desc_match = re.search(r'<meta\s+name="description"\s+content="(.+?)"', content)

        metrics["seo"] = {
            "has_title": bool(title_match),
            "title_length": len(title_match.group(1)) if title_match else 0,
            "has_description": bool(desc_match),
            "description_length": len(desc_match.group(1)) if desc_match else 0,
            "og_tags": len(re.findall(r'property="og:', content)),
            "canonical": 'rel="canonical"' in content,
        }

        # Performance metrics
        metrics["performance"] = {
            "lazy_images": content.count('loading="lazy"'),
            "async_scripts": content.count("async"),
            "defer_scripts": content.count("defer"),
            "inline_styles": content.count("<style"),
            "external_styles": content.count('<link rel="stylesheet"'),
        }

        # Accessibility
        metrics["accessibility"] = {
            "aria_labels": len(re.findall(r"aria-label", content)),
            "alt_texts": len(re.findall(r'alt="[^"]+"', content)),
            "landmarks": (
                content.count("<header")
                + content.count("<nav")
                + content.count("<main")
                + content.count("<footer")
            ),
        }

        # E-commerce features
        metrics["ecommerce"] = {
            "product_cards": len(re.findall(r'class="[^"]*product[^"]*"', content)),
            "price_tags": len(re.findall(r"\$\d+|\d+\.\d{2}", content)),
            "cta_buttons": len(re.findall(r'(Buy Now|Add to Cart|Shop Now|Get Started)', content, re.IGNORECASE)),
            "testimonials": content.count("testimonial"),
            "countdown": "countdown" in content.lower(),
        }

        return metrics

    def compare_templates(self, template_names: List[str]) -> Dict:
        """Compare multiple templates."""
        results = {}
        for name in template_names:
            results[name] = self.analyze_template(name)

        return results

    def generate_comparison_table(self, results: Dict) -> str:
        """Generate a markdown comparison table."""
        if not results:
            return "No templates to compare"

        lines = ["# Template Comparison\n"]

        # Basic metrics
        lines.append("## 📊 Basic Metrics\n")
        lines.append("| Metric | " + " | ".join(results.keys()) + " |")
        lines.append("|--------|" + "|".join(["--------"] * len(results)) + "|")

        metrics_to_compare = [
            ("File Size (KB)", "file_size_kb"),
            ("Total Lines", "total_lines"),
            ("Images", "images"),
            ("Links", "links"),
            ("Buttons", "buttons"),
            ("Forms", "forms"),
            ("Sections", "sections"),
        ]

        for label, key in metrics_to_compare:
            values = [str(results[t].get(key, "N/A")) for t in results]
            lines.append(f"| {label} | " + " | ".join(values) + " |")

        # SEO comparison
        lines.append("\n## 🔍 SEO Metrics\n")
        lines.append("| Metric | " + " | ".join(results.keys()) + " |")
        lines.append("|--------|" + "|".join(["--------"] * len(results)) + "|")

        seo_metrics = [
            ("Has Title", "has_title"),
            ("Title Length", "title_length"),
            ("Has Description", "has_description"),
            ("Description Length", "description_length"),
            ("OG Tags", "og_tags"),
            ("Canonical URL", "canonical"),
        ]

        for label, key in seo_metrics:
            values = []
            for t in results:
                val = results[t].get("seo", {}).get(key, "N/A")
                if isinstance(val, bool):
                    val = "✅" if val else "❌"
                values.append(str(val))
            lines.append(f"| {label} | " + " | ".join(values) + " |")

        # Performance comparison
        lines.append("\n## ⚡ Performance\n")
        lines.append("| Metric | " + " | ".join(results.keys()) + " |")
        lines.append("|--------|" + "|".join(["--------"] * len(results)) + "|")

        perf_metrics = [
            ("Lazy Images", "lazy_images"),
            ("Async Scripts", "async_scripts"),
            ("Defer Scripts", "defer_scripts"),
            ("Inline Styles", "inline_styles"),
            ("External Styles", "external_styles"),
        ]

        for label, key in perf_metrics:
            values = [str(results[t].get("performance", {}).get(key, "N/A")) for t in results]
            lines.append(f"| {label} | " + " | ".join(values) + " |")

        # Accessibility
        lines.append("\n## ♿ Accessibility\n")
        lines.append("| Metric | " + " | ".join(results.keys()) + " |")
        lines.append("|--------|" + "|".join(["--------"] * len(results)) + "|")

        a11y_metrics = [
            ("ARIA Labels", "aria_labels"),
            ("Alt Texts", "alt_texts"),
            ("Landmarks", "landmarks"),
        ]

        for label, key in a11y_metrics:
            values = [str(results[t].get("accessibility", {}).get(key, "N/A")) for t in results]
            lines.append(f"| {label} | " + " | ".join(values) + " |")

        # E-commerce features
        lines.append("\n## 🛒 E-commerce Features\n")
        lines.append("| Feature | " + " | ".join(results.keys()) + " |")
        lines.append("|---------|" + "|".join(["--------"] * len(results)) + "|")

        ecom_metrics = [
            ("Product Cards", "product_cards"),
            ("Price Tags", "price_tags"),
            ("CTA Buttons", "cta_buttons"),
            ("Testimonials", "testimonials"),
            ("Countdown Timer", "countdown"),
        ]

        for label, key in ecom_metrics:
            values = []
            for t in results:
                val = results[t].get("ecommerce", {}).get(key, "N/A")
                if isinstance(val, bool):
                    val = "✅" if val else "❌"
                values.append(str(val))
            lines.append(f"| {label} | " + " | ".join(values) + " |")

        # Recommendations
        lines.append("\n## 💡 Recommendations\n")
        for template_name, data in results.items():
            lines.append(f"\n### {template_name}\n")
            recs = self._generate_recommendations(data)
            for rec in recs:
                lines.append(f"- {rec}")

        return "\n".join(lines)

    def _generate_recommendations(self, metrics: Dict) -> List[str]:
        """Generate recommendations for a template."""
        recs = []

        # File size
        if metrics.get("file_size_kb", 0) > 50:
            recs.append(f"⚠️  Large file size ({metrics['file_size_kb']} KB). Consider minification.")

        # SEO
        seo = metrics.get("seo", {})
        if not seo.get("has_title"):
            recs.append("❌ Missing title tag")
        elif seo.get("title_length", 0) < 30:
            recs.append(f"⚠️  Title too short ({seo['title_length']} chars)")

        if not seo.get("has_description"):
            recs.append("❌ Missing meta description")
        elif seo.get("description_length", 0) < 50:
            recs.append(f"⚠️  Description too short ({seo['description_length']} chars)")

        if seo.get("og_tags", 0) < 2:
            recs.append("⚠️  Add more Open Graph tags for social sharing")

        # Performance
        perf = metrics.get("performance", {})
        if metrics.get("images", 0) > 0 and perf.get("lazy_images", 0) == 0:
            recs.append("⚠️  No lazy loading on images. Add loading='lazy'")

        if metrics.get("scripts", 0) > 0:
            async_count = perf.get("async_scripts", 0) + perf.get("defer_scripts", 0)
            if async_count == 0:
                recs.append("⚠️  No async/defer scripts. Consider adding for better performance")

        # Accessibility
        a11y = metrics.get("accessibility", {})
        if a11y.get("aria_labels", 0) == 0:
            recs.append("⚠️  No ARIA labels found. Improve accessibility")

        if metrics.get("images", 0) > a11y.get("alt_texts", 0):
            recs.append(f"⚠️  Some images missing alt text ({a11y.get('alt_texts', 0)}/{metrics.get('images', 0)})")

        if not recs:
            recs.append("✅ No major issues detected!")

        return recs


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Compare Shopify templates")
    parser.add_argument("templates", nargs="+", help="Template names to compare")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--output", help="Save comparison to file")

    args = parser.parse_args()

    templates_dir = Path(__file__).parent.parent
    comparator = TemplateComparator(templates_dir)

    results = comparator.compare_templates(args.templates)

    if args.json:
        output = json.dumps(results, indent=2)
        print(output)
    else:
        output = comparator.generate_comparison_table(results)
        print(output)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"\n✅ Comparison saved to: {args.output}")


if __name__ == "__main__":
    main()
