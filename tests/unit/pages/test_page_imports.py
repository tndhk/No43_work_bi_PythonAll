"""Tests that package-style pages are imported in app.py."""
from __future__ import annotations

from pathlib import Path


def test_app_imports_all_package_pages():
    pages_dir = Path("src/pages")
    package_pages = [
        p.name
        for p in pages_dir.iterdir()
        if p.is_dir() and (p / "__init__.py").exists() and not p.name.startswith("__")
    ]

    app_text = Path("app.py").read_text()

    for page_name in package_pages:
        assert f"import src.pages.{page_name}" in app_text
