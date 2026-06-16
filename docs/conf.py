"""Configuration Sphinx — kubewi documentation."""

from __future__ import annotations

import os
import pathlib
import shutil
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
exclude_patterns = [
    "_build", "Thumbs.db", ".DS_Store",
    "_archive",
    "decisions.rst",
    "reference/package-template.rst",
]
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
    if not shutil.which("d2"):
        return
    # Diagrammes plateforme (docs/_static/diagrams/)
    diagrams_dir = pathlib.Path(app.srcdir) / "_static" / "diagrams"
    for d2_file in sorted(diagrams_dir.glob("*.d2")):
        subprocess.run(["d2", str(d2_file), str(d2_file.with_suffix(".svg"))], check=True)
    # Diagrammes paquets (src/*/docs/*.d2)
    src_dir = pathlib.Path(app.srcdir).parent / "src"
    for d2_file in sorted(src_dir.glob("*/docs/*.d2")):
        subprocess.run(["d2", str(d2_file), str(d2_file.with_suffix(".svg"))], check=True)


# -- Package docs symlinks ---------------------------------------------------
# src/<pkg>/docs/ → docs/packages/<pkg>/  (symlinks, gitignored)

def link_package_docs(app):
    src_dir = pathlib.Path(app.srcdir).parent / "src"
    pkg_dir = pathlib.Path(app.srcdir) / "packages"
    pkg_dir.mkdir(exist_ok=True)

    for pkg_path in sorted(src_dir.iterdir()):
        docs_path = pkg_path / "docs"
        if not docs_path.is_dir():
            continue
        link = pkg_dir / pkg_path.name
        if link.is_symlink():
            link.unlink()
        link.symlink_to(os.path.relpath(docs_path, pkg_dir))


def setup(app):
    app.connect("builder-inited", link_package_docs)
    app.connect("builder-inited", generate_d2_diagrams)


# -- Intersphinx -------------------------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}
