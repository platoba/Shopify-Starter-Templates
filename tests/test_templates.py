"""Tests for Shopify Starter Templates — HTML validation."""

import pytest
from pathlib import Path

# Add tools to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
from cli import validate_html, validate_template, validate_all, ValidationResult, TEMPLATES_DIR


# ── Fixtures ────────────────────────────────────────────────────────────

TEMPLATES = ["minimal-store", "dropship-starter", "landing-product"]


@pytest.fixture
def sample_html(tmp_path):
    """Create a sample HTML file for testing."""
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Store — Great Products</title>
    <meta name="description" content="A test store with great products for everyone. Shop now for the best deals.">
    <meta property="og:title" content="Test Store">
    <meta property="og:description" content="Great products">
    <link rel="canonical" href="https://teststore.com">
</head>
<body>
    <img src="test.jpg" alt="Test image" loading="lazy">
    <button aria-label="Menu">Menu</button>
</body>
</html>'''
    f = tmp_path / "test.html"
    f.write_text(html)
    return f


@pytest.fixture
def bad_html(tmp_path):
    """Create a bad HTML file for testing."""
    html = '''<html>
<head><title>X</title></head>
<body><img src="test.jpg"></body>
</html>'''
    f = tmp_path / "bad.html"
    f.write_text(html)
    return f


# ── ValidationResult tests ──────────────────────────────────────────────

class TestValidationResult:
    def test_empty_result_is_ok(self):
        r = ValidationResult()
        assert r.ok is True

    def test_error_makes_not_ok(self):
        r = ValidationResult()
        r.error("something wrong")
        assert r.ok is False

    def test_warning_keeps_ok(self):
        r = ValidationResult()
        r.warn("just a warning")
        assert r.ok is True

    def test_summary_contains_counts(self):
        r = ValidationResult()
        r.pass_("good")
        r.warn("meh")
        r.error("bad")
        s = r.summary()
        assert "1 passed" in s
        assert "1 warnings" in s
        assert "1 errors" in s
        assert "FAIL" in s

    def test_pass_summary(self):
        r = ValidationResult()
        r.pass_("all good")
        s = r.summary()
        assert "PASS" in s


# ── HTML Validation tests ───────────────────────────────────────────────

class TestValidateHtml:
    def test_good_html_passes(self, sample_html):
        result = validate_html(sample_html)
        assert result.ok is True
        assert len(result.errors) == 0

    def test_good_html_has_passes(self, sample_html):
        result = validate_html(sample_html)
        assert len(result.passed) >= 5  # DOCTYPE, charset, viewport, title, etc.

    def test_bad_html_has_errors(self, bad_html):
        result = validate_html(bad_html)
        assert result.ok is False

    def test_missing_file(self, tmp_path):
        result = validate_html(tmp_path / "nonexistent.html")
        assert result.ok is False
        assert "not found" in result.errors[0].lower()

    def test_detects_missing_doctype(self, bad_html):
        result = validate_html(bad_html)
        doctype_errors = [e for e in result.errors if "DOCTYPE" in e]
        assert len(doctype_errors) > 0

    def test_detects_missing_charset(self, bad_html):
        result = validate_html(bad_html)
        charset_errors = [e for e in result.errors if "charset" in e.lower()]
        assert len(charset_errors) > 0

    def test_detects_missing_viewport(self, bad_html):
        result = validate_html(bad_html)
        viewport_errors = [e for e in result.errors if "viewport" in e.lower()]
        assert len(viewport_errors) > 0

    def test_detects_short_title(self, bad_html):
        result = validate_html(bad_html)
        title_warnings = [w for w in result.warnings if "title" in w.lower() and "short" in w.lower()]
        assert len(title_warnings) > 0

    def test_detects_missing_alt(self, bad_html):
        result = validate_html(bad_html)
        alt_warnings = [w for w in result.warnings if "alt" in w.lower()]
        assert len(alt_warnings) > 0

    def test_checks_og_tags(self, sample_html):
        result = validate_html(sample_html)
        og_passes = [p for p in result.passed if "Open Graph" in p]
        assert len(og_passes) > 0

    def test_checks_canonical(self, sample_html):
        result = validate_html(sample_html)
        canonical_passes = [p for p in result.passed if "canonical" in p.lower()]
        assert len(canonical_passes) > 0

    def test_checks_aria(self, sample_html):
        result = validate_html(sample_html)
        aria_passes = [p for p in result.passed if "ARIA" in p]
        assert len(aria_passes) > 0

    def test_checks_lazy_loading(self, sample_html):
        result = validate_html(sample_html)
        lazy_passes = [p for p in result.passed if "lazy" in p.lower()]
        assert len(lazy_passes) > 0

    def test_html_size_check(self, sample_html):
        result = validate_html(sample_html)
        size_passes = [p for p in result.passed if "size" in p.lower()]
        assert len(size_passes) > 0


# ── Template validation tests ──────────────────────────────────────────

class TestValidateTemplate:
    def test_nonexistent_template(self):
        result = validate_template("nonexistent-template-xyz")
        assert result.ok is False

    @pytest.mark.parametrize("template", TEMPLATES)
    def test_template_exists(self, template):
        """Check that each listed template directory exists."""
        template_dir = TEMPLATES_DIR / template
        assert template_dir.exists(), f"Template directory missing: {template}"

    @pytest.mark.parametrize("template", TEMPLATES)
    def test_template_has_index(self, template):
        """Check that each template has an index.html."""
        index = TEMPLATES_DIR / template / "index.html"
        assert index.exists(), f"Missing index.html in {template}/"

    @pytest.mark.parametrize("template", TEMPLATES)
    def test_template_validates(self, template):
        """Run full validation on each template."""
        result = validate_template(template)
        # Allow warnings but no errors
        assert result.ok is True, f"Template {template} failed validation:\n{result.summary()}"

    @pytest.mark.parametrize("template", TEMPLATES)
    def test_template_has_doctype(self, template):
        content = (TEMPLATES_DIR / template / "index.html").read_text()
        assert "<!DOCTYPE html>" in content or "<!doctype html>" in content

    @pytest.mark.parametrize("template", TEMPLATES)
    def test_template_has_viewport(self, template):
        content = (TEMPLATES_DIR / template / "index.html").read_text()
        assert "viewport" in content

    @pytest.mark.parametrize("template", TEMPLATES)
    def test_template_responsive(self, template):
        """Templates should use responsive CSS classes."""
        content = (TEMPLATES_DIR / template / "index.html").read_text()
        assert "md:" in content or "lg:" in content or "@media" in content

    @pytest.mark.parametrize("template", TEMPLATES)
    def test_template_has_cta(self, template):
        """Templates should have at least one call-to-action."""
        content = (TEMPLATES_DIR / template / "index.html").read_text().lower()
        ctas = ["buy now", "shop now", "add to cart", "get started", "subscribe", "quick add", "grab deal"]
        assert any(cta in content for cta in ctas), f"No CTA found in {template}"


class TestValidateAll:
    def test_validate_all_returns_dict(self):
        results = validate_all()
        assert isinstance(results, dict)
        assert len(results) > 0

    def test_validate_all_keys_are_templates(self):
        results = validate_all()
        for key in results:
            assert key in TEMPLATES


# ── Generator tests ─────────────────────────────────────────────────────

class TestGenerator:
    def test_generate_creates_directory(self, tmp_path):
        from cli import generate_template
        output = tmp_path / "my-store"
        result = generate_template("minimal-store", str(output), store_name="Cool Store")
        assert result is True
        assert output.exists()
        assert (output / "index.html").exists()
        assert (output / "config.json").exists()

    def test_generate_customizes_name(self, tmp_path):
        from cli import generate_template
        output = tmp_path / "custom"
        generate_template("minimal-store", str(output), store_name="Acme Shop")
        content = (output / "index.html").read_text()
        assert "Acme Shop" in content

    def test_generate_creates_config(self, tmp_path):
        from cli import generate_template
        import json
        output = tmp_path / "configured"
        generate_template("minimal-store", str(output), store_name="Test", currency="EUR")
        config = json.loads((output / "config.json").read_text())
        assert config["name"] == "Test"
        assert config["currency"] == "EUR"
        assert config["template"] == "minimal-store"

    def test_generate_fails_existing(self, tmp_path):
        from cli import generate_template
        output = tmp_path / "exists"
        output.mkdir()
        result = generate_template("minimal-store", str(output))
        assert result is False

    def test_generate_fails_unknown_template(self, tmp_path):
        from cli import generate_template
        result = generate_template("unknown-xyz", str(tmp_path / "out"))
        assert result is False


# ── Component tests ─────────────────────────────────────────────────────

class TestComponents:
    COMPONENTS_DIR = TEMPLATES_DIR / "components"

    @pytest.fixture(autouse=True)
    def check_components_dir(self):
        if not self.COMPONENTS_DIR.exists():
            pytest.skip("Components directory not found")

    def test_components_exist(self):
        components = list(self.COMPONENTS_DIR.glob("*.html"))
        assert len(components) >= 5, "Should have at least 5 components"

    @pytest.mark.parametrize("component", [
        "hero.html", "header.html", "footer.html", "features.html",
        "cta.html", "faq.html", "testimonials.html", "pricing.html", "newsletter.html"
    ])
    def test_component_exists(self, component):
        f = self.COMPONENTS_DIR / component
        assert f.exists(), f"Missing component: {component}"

    @pytest.mark.parametrize("component", [
        "hero.html", "header.html", "footer.html", "features.html",
        "cta.html", "faq.html", "testimonials.html", "pricing.html", "newsletter.html"
    ])
    def test_component_not_empty(self, component):
        f = self.COMPONENTS_DIR / component
        if f.exists():
            content = f.read_text()
            assert len(content) > 20, f"Component {component} is too small"

    def test_hero_has_heading(self):
        content = (self.COMPONENTS_DIR / "hero.html").read_text()
        assert "<h1" in content or "<h2" in content

    def test_cta_has_button(self):
        content = (self.COMPONENTS_DIR / "cta.html").read_text()
        assert "<a " in content or "<button" in content

    def test_faq_has_questions(self):
        content = (self.COMPONENTS_DIR / "faq.html").read_text()
        assert "?" in content  # FAQ should have questions


# ── Shared assets tests ────────────────────────────────────────────────

class TestSharedAssets:
    SHARED_DIR = TEMPLATES_DIR / "shared"

    def test_theme_css_exists(self):
        assert (self.SHARED_DIR / "styles" / "theme.css").exists()

    def test_theme_css_has_variables(self):
        content = (self.SHARED_DIR / "styles" / "theme.css").read_text()
        assert "--" in content or "var(" in content or "color" in content.lower()

    def test_ab_testing_js_exists(self):
        assert (self.SHARED_DIR / "scripts" / "ab-testing.js").exists()

    def test_theme_switcher_js_exists(self):
        assert (self.SHARED_DIR / "scripts" / "theme-switcher.js").exists()

    def test_scripts_are_valid_js(self):
        """Basic check that JS files aren't empty and have function definitions."""
        for js in (self.SHARED_DIR / "scripts").glob("*.js"):
            content = js.read_text()
            assert len(content) > 50, f"JS file too small: {js.name}"
            assert "function" in content or "=>" in content or "class" in content
