"""Tests for performance analyzer and template comparator."""

import json
from pathlib import Path
import pytest
import sys

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.performance import PerformanceAnalyzer
from tools.compare import TemplateComparator


class TestPerformanceAnalyzer:
    """Test performance analyzer."""

    @pytest.fixture
    def templates_dir(self):
        return Path(__file__).parent.parent

    @pytest.fixture
    def analyzer(self, templates_dir):
        template_dir = templates_dir / "minimal-store"
        return PerformanceAnalyzer(template_dir)

    def test_analyze_file_sizes(self, analyzer):
        """Test file size analysis."""
        sizes = analyzer.analyze_file_sizes()
        assert "html" in sizes
        assert "css" in sizes
        assert "js" in sizes
        assert "total" in sizes
        assert sizes["total"] > 0

    def test_analyze_html_metrics(self, analyzer):
        """Test HTML metrics analysis."""
        metrics = analyzer.analyze_html_metrics()
        assert "html_size_kb" in metrics
        assert "total_lines" in metrics
        assert "script_tags" in metrics
        assert "img_tags" in metrics
        assert metrics["total_lines"] > 0

    def test_generate_report(self, analyzer):
        """Test report generation."""
        report = analyzer.generate_report()
        assert "template" in report
        assert "file_sizes" in report
        assert "html_metrics" in report
        assert "recommendations" in report
        assert len(report["recommendations"]) > 0

    def test_recommendations_logic(self, analyzer):
        """Test recommendation generation logic."""
        report = analyzer.generate_report()
        recs = report["recommendations"]

        # Should have at least one recommendation
        assert len(recs) > 0

        # Check recommendation format
        for rec in recs:
            assert isinstance(rec, str)
            assert len(rec) > 0


class TestTemplateComparator:
    """Test template comparator."""

    @pytest.fixture
    def templates_dir(self):
        return Path(__file__).parent.parent

    @pytest.fixture
    def comparator(self, templates_dir):
        return TemplateComparator(templates_dir)

    def test_analyze_single_template(self, comparator):
        """Test single template analysis."""
        result = comparator.analyze_template("minimal-store")
        assert "name" in result
        assert "file_size_kb" in result
        assert "seo" in result
        assert "performance" in result
        assert "accessibility" in result
        assert "ecommerce" in result

    def test_analyze_all_templates(self, comparator):
        """Test analyzing all templates."""
        templates = ["minimal-store", "dropship-starter", "landing-product"]
        results = comparator.compare_templates(templates)

        assert len(results) == 3
        for template in templates:
            assert template in results
            assert "file_size_kb" in results[template]

    def test_seo_metrics(self, comparator):
        """Test SEO metrics extraction."""
        result = comparator.analyze_template("minimal-store")
        seo = result["seo"]

        assert "has_title" in seo
        assert "title_length" in seo
        assert "has_description" in seo
        assert "og_tags" in seo
        assert isinstance(seo["has_title"], bool)
        assert isinstance(seo["title_length"], int)

    def test_performance_metrics(self, comparator):
        """Test performance metrics extraction."""
        result = comparator.analyze_template("minimal-store")
        perf = result["performance"]

        assert "lazy_images" in perf
        assert "async_scripts" in perf
        assert "defer_scripts" in perf
        assert isinstance(perf["lazy_images"], int)

    def test_accessibility_metrics(self, comparator):
        """Test accessibility metrics extraction."""
        result = comparator.analyze_template("minimal-store")
        a11y = result["accessibility"]

        assert "aria_labels" in a11y
        assert "alt_texts" in a11y
        assert "landmarks" in a11y
        assert isinstance(a11y["aria_labels"], int)

    def test_ecommerce_metrics(self, comparator):
        """Test e-commerce metrics extraction."""
        result = comparator.analyze_template("minimal-store")
        ecom = result["ecommerce"]

        assert "product_cards" in ecom
        assert "price_tags" in ecom
        assert "cta_buttons" in ecom
        assert isinstance(ecom["cta_buttons"], int)

    def test_generate_comparison_table(self, comparator):
        """Test comparison table generation."""
        templates = ["minimal-store", "dropship-starter"]
        results = comparator.compare_templates(templates)
        table = comparator.generate_comparison_table(results)

        assert "# Template Comparison" in table
        assert "minimal-store" in table
        assert "dropship-starter" in table
        assert "📊 Basic Metrics" in table
        assert "🔍 SEO Metrics" in table
        assert "⚡ Performance" in table

    def test_recommendations_generation(self, comparator):
        """Test recommendations generation."""
        result = comparator.analyze_template("minimal-store")
        recs = comparator._generate_recommendations(result)

        assert isinstance(recs, list)
        assert len(recs) > 0
        for rec in recs:
            assert isinstance(rec, str)

    def test_nonexistent_template(self, comparator):
        """Test handling of nonexistent template."""
        result = comparator.analyze_template("nonexistent-template")
        assert "error" in result

    def test_comparison_with_invalid_template(self, comparator):
        """Test comparison with invalid template."""
        templates = ["minimal-store", "invalid-template"]
        results = comparator.compare_templates(templates)

        assert "minimal-store" in results
        assert "invalid-template" in results
        assert "error" in results["invalid-template"]


class TestIntegration:
    """Integration tests for tools."""

    @pytest.fixture
    def templates_dir(self):
        return Path(__file__).parent.parent

    def test_performance_and_comparison_consistency(self, templates_dir):
        """Test that performance analyzer and comparator give consistent results."""
        template_name = "minimal-store"

        # Performance analyzer
        analyzer = PerformanceAnalyzer(templates_dir / template_name)
        perf_report = analyzer.generate_report()

        # Comparator
        comparator = TemplateComparator(templates_dir)
        comp_result = comparator.analyze_template(template_name)

        # File sizes should match
        assert perf_report["file_sizes"]["html"] == comp_result["file_size_kb"]

    def test_all_templates_analyzable(self, templates_dir):
        """Test that all templates can be analyzed by both tools."""
        templates = ["minimal-store", "dropship-starter", "landing-product"]

        for template in templates:
            # Performance analyzer
            analyzer = PerformanceAnalyzer(templates_dir / template)
            perf_report = analyzer.generate_report()
            assert "template" in perf_report
            assert perf_report["template"] == template

            # Comparator
            comparator = TemplateComparator(templates_dir)
            comp_result = comparator.analyze_template(template)
            assert "name" in comp_result
            assert comp_result["name"] == template


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
