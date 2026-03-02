#!/usr/bin/env python3
"""Performance analyzer for Shopify templates using Lighthouse."""

import json
import subprocess
import sys
from pathlib import Path
from typing import Optional


class PerformanceAnalyzer:
    """Analyze template performance using Lighthouse."""

    def __init__(self, template_dir: Path):
        self.template_dir = template_dir
        self.index_html = template_dir / "index.html"

    def check_lighthouse_installed(self) -> bool:
        """Check if Lighthouse CLI is installed."""
        try:
            subprocess.run(
                ["lighthouse", "--version"],
                capture_output=True,
                check=True,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def analyze_file_sizes(self) -> dict:
        """Analyze file sizes in the template."""
        sizes = {
            "html": 0,
            "css": 0,
            "js": 0,
            "images": 0,
            "total": 0,
        }

        for file in self.template_dir.rglob("*"):
            if file.is_file():
                size = file.stat().st_size
                sizes["total"] += size

                if file.suffix == ".html":
                    sizes["html"] += size
                elif file.suffix == ".css":
                    sizes["css"] += size
                elif file.suffix == ".js":
                    sizes["js"] += size
                elif file.suffix in [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"]:
                    sizes["images"] += size

        # Convert to KB
        return {k: round(v / 1024, 2) for k, v in sizes.items()}

    def analyze_html_metrics(self) -> dict:
        """Analyze HTML-specific metrics."""
        if not self.index_html.exists():
            return {}

        content = self.index_html.read_text(encoding="utf-8")

        return {
            "html_size_kb": round(len(content.encode("utf-8")) / 1024, 2),
            "total_lines": len(content.splitlines()),
            "script_tags": content.count("<script"),
            "style_tags": content.count("<style"),
            "link_tags": content.count("<link"),
            "img_tags": content.count("<img"),
            "lazy_images": content.count('loading="lazy"'),
            "async_scripts": content.count("async"),
            "defer_scripts": content.count("defer"),
        }

    def run_lighthouse(self, url: str, output_path: Optional[Path] = None) -> dict:
        """Run Lighthouse analysis on a URL."""
        if not self.check_lighthouse_installed():
            return {
                "error": "Lighthouse CLI not installed. Install: npm install -g lighthouse"
            }

        output_path = output_path or Path("/tmp/lighthouse-report.json")

        try:
            subprocess.run(
                [
                    "lighthouse",
                    url,
                    "--output=json",
                    f"--output-path={output_path}",
                    "--chrome-flags=--headless",
                    "--quiet",
                ],
                check=True,
                capture_output=True,
            )

            with open(output_path) as f:
                report = json.load(f)

            categories = report.get("categories", {})
            return {
                "performance": categories.get("performance", {}).get("score", 0) * 100,
                "accessibility": categories.get("accessibility", {}).get("score", 0) * 100,
                "best_practices": categories.get("best-practices", {}).get("score", 0) * 100,
                "seo": categories.get("seo", {}).get("score", 0) * 100,
            }

        except subprocess.CalledProcessError as e:
            return {"error": f"Lighthouse failed: {e.stderr.decode()}"}

    def generate_report(self) -> dict:
        """Generate a comprehensive performance report."""
        report = {
            "template": self.template_dir.name,
            "file_sizes": self.analyze_file_sizes(),
            "html_metrics": self.analyze_html_metrics(),
        }

        # Performance recommendations
        recommendations = []
        sizes = report["file_sizes"]
        html = report["html_metrics"]

        if sizes["html"] > 50:
            recommendations.append(f"⚠️  HTML size is large ({sizes['html']} KB). Consider minification.")

        if sizes["css"] > 100:
            recommendations.append(f"⚠️  CSS size is large ({sizes['css']} KB). Consider splitting or minification.")

        if sizes["js"] > 100:
            recommendations.append(f"⚠️  JavaScript size is large ({sizes['js']} KB). Consider code splitting.")

        if sizes["images"] > 500:
            recommendations.append(f"⚠️  Images are large ({sizes['images']} KB). Consider compression or WebP format.")

        if html.get("img_tags", 0) > 0:
            lazy_ratio = html.get("lazy_images", 0) / html["img_tags"]
            if lazy_ratio < 0.5:
                recommendations.append(f"⚠️  Only {lazy_ratio:.0%} of images use lazy loading. Add loading='lazy' to below-fold images.")

        if html.get("script_tags", 0) > 0:
            async_ratio = (html.get("async_scripts", 0) + html.get("defer_scripts", 0)) / html["script_tags"]
            if async_ratio < 0.5:
                recommendations.append(f"⚠️  Only {async_ratio:.0%} of scripts are async/defer. Consider adding async or defer attributes.")

        if not recommendations:
            recommendations.append("✅ No major performance issues detected!")

        report["recommendations"] = recommendations
        return report

    def print_report(self, report: dict):
        """Print a formatted performance report."""
        print(f"\n📊 Performance Report: {report['template']}")
        print("\n📦 File Sizes:")
        for key, value in report["file_sizes"].items():
            print(f"   {key:10s}: {value:8.2f} KB")

        print("\n📄 HTML Metrics:")
        for key, value in report["html_metrics"].items():
            print(f"   {key:20s}: {value}")

        print("\n💡 Recommendations:")
        for rec in report["recommendations"]:
            print(f"   {rec}")


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Analyze template performance")
    parser.add_argument("template", help="Template directory name")
    parser.add_argument("--lighthouse", help="Run Lighthouse on URL")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    template_dir = Path(__file__).parent.parent / args.template
    if not template_dir.exists():
        print(f"❌ Template not found: {args.template}")
        sys.exit(1)

    analyzer = PerformanceAnalyzer(template_dir)
    report = analyzer.generate_report()

    if args.lighthouse:
        lighthouse_scores = analyzer.run_lighthouse(args.lighthouse)
        report["lighthouse"] = lighthouse_scores

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        analyzer.print_report(report)
        if args.lighthouse and "lighthouse" in report:
            print("\n🚦 Lighthouse Scores:")
            for metric, score in report["lighthouse"].items():
                if metric != "error":
                    emoji = "🟢" if score >= 90 else "🟡" if score >= 50 else "🔴"
                    print(f"   {emoji} {metric:20s}: {score:.0f}/100")


if __name__ == "__main__":
    main()
