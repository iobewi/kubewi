"""
Tests de conformité structurelle — chaque paquet doit respecter
la convention KubeWI : fichiers obligatoires, arborescence docs/.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

REQUIRED_CORE_FILES = [
    "kubewi.yaml",
    "kubewi/__init__.py",
]

REQUIRED_DOC_FILES = [
    "docs/index.rst",
    "docs/role.rst",
    "docs/implementation.rst",
]


# ── Arborescence ──────────────────────────────────────────────────────────────


def test_required_package_files(pkg_dir: Path) -> None:
    """Fichiers obligatoires de tout paquet KubeWI."""
    for rel in REQUIRED_CORE_FILES:
        assert (pkg_dir / rel).exists(), f"fichier manquant : {pkg_dir.name}/{rel}"


def test_docs_directory_exists(pkg_dir: Path) -> None:
    assert (pkg_dir / "docs").is_dir(), f"{pkg_dir.name}/docs/ absent"


def test_docs_required_files(pkg_dir: Path) -> None:
    """Fichiers de documentation obligatoires."""
    for rel in REQUIRED_DOC_FILES:
        assert (pkg_dir / rel).exists(), f"doc manquante : {pkg_dir.name}/{rel}"


# ── Contenu docs/ ─────────────────────────────────────────────────────────────


def test_docs_index_has_toctree(pkg_dir: Path) -> None:
    content = (pkg_dir / "docs" / "index.rst").read_text()
    assert ".. toctree::" in content, \
        f"{pkg_dir.name}/docs/index.rst : toctree absent"


def test_docs_index_references_role(pkg_dir: Path) -> None:
    content = (pkg_dir / "docs" / "index.rst").read_text()
    assert "role" in content, \
        f"{pkg_dir.name}/docs/index.rst : référence à 'role' absente"


def test_docs_role_has_title(pkg_dir: Path) -> None:
    lines = (pkg_dir / "docs" / "role.rst").read_text().splitlines()
    underlines = [l for l in lines if l and all(c == "=" for c in l)]
    assert underlines, f"{pkg_dir.name}/docs/role.rst : aucun titre RST (====)"


# ── Symboles commands.py (paquets CLI uniquement) ─────────────────────────────


def test_commands_py_defines_name(cli_pkg_dir: Path) -> None:
    """NAME ou NAMES doit être défini dans commands.py."""
    source = (cli_pkg_dir / "kubewi" / "commands.py").read_text()
    assert "NAME" in source, \
        f"{cli_pkg_dir.name}/kubewi/commands.py : ni NAME ni NAMES défini"


def test_commands_py_defines_register(cli_pkg_dir: Path) -> None:
    source = (cli_pkg_dir / "kubewi" / "commands.py").read_text()
    assert "def register(" in source, \
        f"{cli_pkg_dir.name}/kubewi/commands.py : fonction register() absente"


def test_commands_py_defines_run_cmd(cli_pkg_dir: Path) -> None:
    source = (cli_pkg_dir / "kubewi" / "commands.py").read_text()
    assert "def run_cmd(" in source, \
        f"{cli_pkg_dir.name}/kubewi/commands.py : fonction run_cmd() absente"


def test_commands_py_valid_syntax(cli_pkg_dir: Path) -> None:
    """Le fichier doit être du Python syntaxiquement valide."""
    source = (cli_pkg_dir / "kubewi" / "commands.py").read_text()
    try:
        ast.parse(source)
    except SyntaxError as e:
        pytest.fail(f"{cli_pkg_dir.name}/kubewi/commands.py : erreur de syntaxe — {e}")


# ── Diagrammes D2 ─────────────────────────────────────────────────────────────


def test_d2_files_have_matching_svg(pkg_dir: Path) -> None:
    """Tout fichier .d2 dans docs/ doit avoir un .svg commité à côté."""
    for d2 in (pkg_dir / "docs").glob("*.d2"):
        svg = d2.with_suffix(".svg")
        assert svg.exists(), \
            f"{pkg_dir.name}/docs/{d2.name} : .svg généré manquant ({svg.name})"
