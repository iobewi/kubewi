"""
Tests de couverture fonctionnelle.

Règles vérifiées :
1. Tout paquet avec au moins un manifest Kubernetes (manifests/*.yaml)
   doit avoir un fichier tests/functional/test_<nom>.py.
2. Tout fichier tests/functional/test_<nom>.py doit correspondre à un paquet
   existant (aucun test orphelin).
"""
from __future__ import annotations

from pathlib import Path

import pytest

from conftest import PKG_DIRS

TESTS_DIR      = Path(__file__).parent
FUNCTIONAL_DIR = TESTS_DIR / "functional"


def _has_manifests(pkg_dir: Path) -> bool:
    """Le paquet contient au moins un fichier YAML dans manifests/."""
    manifests = pkg_dir / "manifests"
    return manifests.is_dir() and any(manifests.glob("*.yaml"))


def _functional_test_file(pkg_dir: Path) -> Path:
    return FUNCTIONAL_DIR / f"test_{pkg_dir.name}.py"


def _all_pkg_names() -> set[str]:
    return {p.name for p in PKG_DIRS}


# ── Règle 1 : couverture manifests ────────────────────────────────────────────


PKGS_WITH_MANIFESTS = [p for p in PKG_DIRS if _has_manifests(p)]


@pytest.mark.parametrize(
    "pkg_dir",
    PKGS_WITH_MANIFESTS,
    ids=lambda p: p.name,
)
def test_manifest_package_has_functional_test(pkg_dir: Path) -> None:
    """Tout paquet avec manifests/*.yaml doit avoir tests/functional/test_<nom>.py."""
    test_file = _functional_test_file(pkg_dir)
    assert test_file.exists(), (
        f"{pkg_dir.name} a des manifests Kubernetes mais aucun test fonctionnel.\n"
        f"  → créer {test_file.relative_to(TESTS_DIR.parent)}"
    )


# ── Règle 2 : aucun test orphelin ─────────────────────────────────────────────


def _functional_test_files() -> list[Path]:
    return sorted(FUNCTIONAL_DIR.glob("test_*.py"))


FUNCTIONAL_TEST_FILES = _functional_test_files()


@pytest.mark.parametrize(
    "test_file",
    FUNCTIONAL_TEST_FILES,
    ids=lambda f: f.stem,
)
def test_no_orphan_functional_test(test_file: Path) -> None:
    """Un fichier tests/functional/test_<nom>.py doit référencer un paquet existant."""
    # Nom du paquet déduit du nom de fichier : test_plg_embewi → plg_embewi
    pkg_name = test_file.stem[len("test_"):]
    pkg_names = _all_pkg_names()
    assert pkg_name in pkg_names, (
        f"{test_file.name} ne correspond à aucun paquet dans src/.\n"
        f"  Paquet attendu : '{pkg_name}'\n"
        f"  Paquets connus : {sorted(pkg_names)}"
    )
