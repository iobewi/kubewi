"""Configuration Sphinx — kubewi documentation."""

from __future__ import annotations

import pathlib
import subprocess

# -- Project information -----------------------------------------------------

project = "KubeWI"
author = "KubeWI Project"
copyright = "2025, KubeWI Project"
release = "0.1"

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "sphinx_tabs.tabs",
]

source_suffix = {
    ".rst": "restructuredtext",
}

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "_archive", "decisions.rst"]
language = "fr"

# -- HTML output -------------------------------------------------------------

html_theme = "sphinx_rtd_theme"
html_title = "kubewi"
html_logo = "_static/logo.png"
html_favicon = "_static/favicon.ico"
html_static_path = ["_static"]

html_theme_options = {
    "logo_only": False,
    "prev_next_buttons_location": "bottom",
    "collapse_navigation": False,
    "sticky_navigation": True,
    "navigation_depth": 3,
    "titles_only": True,
}

# -- D2 diagrams -------------------------------------------------------------

def generate_d2_diagrams(app):
    diagrams_dir = pathlib.Path(app.srcdir) / "_static" / "diagrams"
    for d2_file in sorted(diagrams_dir.glob("*.d2")):
        svg_file = d2_file.with_suffix(".svg")
        subprocess.run(["d2", str(d2_file), str(svg_file)], check=True)


def setup(app):
    app.connect("builder-inited", generate_d2_diagrams)


# -- Intersphinx -------------------------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}
