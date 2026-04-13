"""Sphinx configuration for the Nova Cart Arcade project documentation."""

import os
import sys
from pathlib import Path

from django import setup as django_setup


DOCS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = DOCS_DIR.parent

sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nova_cart_arcade.settings")
os.environ.setdefault("NOVA_CART_DB_ENGINE", "sqlite")

django_setup()

project = "Nova Cart Arcade"
author = "Jeremiah"
copyright = "2026, Jeremiah"
release = "1.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
html_theme = "alabaster"

autodoc_default_options = {
    "members": True,
    "show-inheritance": True,
    "undoc-members": False,
}
autodoc_member_order = "bysource"
