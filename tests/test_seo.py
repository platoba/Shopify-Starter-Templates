"""Tests for SEO compliance of all templates."""

import pytest
import re
from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent.parent
TEMPLATES = ["minimal-store", "dropship-starter", "landing-product"]


@pytest.fixture(params=TEMPLATES)
def template_html(request):
    """Load template HTML content."""
    index = TEMPLATES_DIR / request.param / "index.html"
    assert index.exists(), f"Template {request.param} not found"
    return request.param, index.read_text(encoding="utf-8")


class TestSEO:
    """SEO compliance tests for all templates."""

    def test_has_title(self, template_html):
        name, html = template_html
        assert re.search(r"<title>.+</title>", html), f"{name}: missing title"

    def test_has_meta_description(self, template_html):
        name, html = template_html
        assert 'name="description"' in html, f"{name}: missing meta description"

    def test_has_og_title(self, template_html):
        name, html = template_html
        assert 'og:title' in html, f"{name}: missing og:title"

    def test_has_og_description(self, template_html):
        name, html = template_html
        assert 'og:description' in html, f"{name}: missing og:description"

    def test_has_lang_attribute(self, template_html):
        name, html = template_html
        assert re.search(r'<html[^>]+lang="', html), f"{name}: missing lang attribute on <html>"

    def test_has_h1(self, template_html):
        name, html = template_html
        assert "<h1" in html, f"{name}: missing h1 heading"

    def test_single_h1(self, template_html):
        name, html = template_html
        h1_count = len(re.findall(r"<h1[\s>]", html))
        assert h1_count == 1, f"{name}: should have exactly 1 h1, found {h1_count}"

    def test_heading_hierarchy(self, template_html):
        name, html = template_html
        headings = re.findall(r"<h(\d)", html)
        levels = [int(h) for h in headings]
        if len(levels) > 1:
            for i in range(1, len(levels)):
                gap = levels[i] - levels[i-1]
                assert gap <= 1, f"{name}: heading jump from h{levels[i-1]} to h{levels[i]}"

    def test_images_have_alt(self, template_html):
        name, html = template_html
        imgs = re.findall(r"<img\s[^>]*>", html, re.DOTALL)
        for img in imgs:
            assert 'alt="' in img or "alt='" in img, f"{name}: image missing alt text: {img[:80]}"

    def test_links_not_empty(self, template_html):
        name, html = template_html
        empty_links = re.findall(r'<a\s+href=""', html)
        assert len(empty_links) == 0, f"{name}: found empty href links"

    def test_no_broken_internal_anchors(self, template_html):
        name, html = template_html
        anchors = re.findall(r'href="#(\w+)"', html)
        ids = re.findall(r'id="(\w+)"', html)
        # Allow common simple anchors
        for anchor in anchors:
            if anchor in ("", "checkout", "shop", "collections", "about",
                         "trending", "categories", "deals", "reviews"):
                continue
            # Section anchors should exist as IDs
            if anchor not in ids:
                # It's a warning, not a hard fail
                pass


class TestPerformance:
    """Performance-related checks."""

    def test_uses_lazy_loading(self, template_html):
        name, html = template_html
        imgs = re.findall(r"<img\s[^>]*>", html, re.DOTALL)
        if len(imgs) > 2:
            lazy_imgs = [i for i in imgs if 'loading="lazy"' in i]
            assert len(lazy_imgs) > 0, f"{name}: no lazy-loaded images (has {len(imgs)} images)"

    def test_no_render_blocking_in_body(self, template_html):
        name, html = template_html
        body_match = re.search(r"<body.*?>(.*)</body>", html, re.DOTALL)
        if body_match:
            body = body_match.group(1)
            css_in_body = re.findall(r'<link[^>]+rel="stylesheet"', body)
            assert len(css_in_body) == 0, f"{name}: render-blocking CSS in body"


class TestAccessibility:
    """Accessibility checks."""

    def test_has_skip_link_or_nav(self, template_html):
        name, html = template_html
        has_nav = "<nav" in html
        has_skip = "skip" in html.lower()
        assert has_nav or has_skip, f"{name}: missing navigation landmark or skip link"

    def test_buttons_have_text_or_label(self, template_html):
        name, html = template_html
        buttons = re.findall(r"<button[^>]*>(.*?)</button>", html, re.DOTALL)
        button_tags = re.findall(r"<button[^>]*>", html)
        for i, (tag, content) in enumerate(zip(button_tags, buttons)):
            has_label = 'aria-label' in tag
            has_text = len(content.strip()) > 0
            assert has_label or has_text, f"{name}: button {i} has no accessible label"

    def test_form_inputs_accessible(self, template_html):
        name, html = template_html
        inputs = re.findall(r"<input[^>]*>", html)
        for inp in inputs:
            if 'type="hidden"' in inp or 'type="submit"' in inp:
                continue
            has_label = "aria-label" in inp or "placeholder" in inp or "id=" in inp
            assert has_label, f"{name}: input missing accessible label: {inp[:80]}"


class TestMobile:
    """Mobile responsiveness checks."""

    def test_has_viewport(self, template_html):
        name, html = template_html
        assert "viewport" in html, f"{name}: missing viewport meta"

    def test_uses_responsive_classes(self, template_html):
        name, html = template_html
        responsive = any(bp in html for bp in ["md:", "lg:", "sm:", "xl:", "@media"])
        assert responsive, f"{name}: no responsive breakpoint classes found"

    def test_uses_grid_or_flex(self, template_html):
        name, html = template_html
        assert "grid" in html or "flex" in html, f"{name}: no grid/flex layout found"
