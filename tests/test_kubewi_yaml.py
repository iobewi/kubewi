"""
Tests de validation du descripteur kubewi.yaml :
champs requis, cohérence name/répertoire, type valide,
existence des dépendances, respect de la hiérarchie de types.
"""
from __future__ import annotations

from pathlib import Path

import pytest
from ruamel.yaml import YAML

from conftest import PKG_DIRS, VALID_TYPES, TYPE_LEVEL

_yaml = YAML()


def _load(path: Path) -> dict:
    with open(path) as f:
        return _yaml.load(f)


# Carte globale nom → type, construite une seule fois.
ALL_PKG: dict[str, str] = {}
for _p in PKG_DIRS:
    _d = _load(_p / "kubewi.yaml")
    ALL_PKG[_d["name"]] = _d["type"]


@pytest.fixture
def pkg_data(pkg_dir: Path) -> dict:
    return _load(pkg_dir / "kubewi.yaml")


# ── Champs requis ─────────────────────────────────────────────────────────────


def test_required_fields_present(pkg_dir: Path, pkg_data: dict) -> None:
    for field in ("name", "type", "description"):
        assert field in pkg_data, \
            f"{pkg_dir.name}/kubewi.yaml : champ requis '{field}' absent"


def test_name_matches_directory(pkg_dir: Path, pkg_data: dict) -> None:
    assert pkg_data["name"] == pkg_dir.name, (
        f"kubewi.yaml name='{pkg_data['name']}' "
        f"ne correspond pas au répertoire '{pkg_dir.name}'"
    )


def test_type_is_valid(pkg_dir: Path, pkg_data: dict) -> None:
    assert pkg_data["type"] in VALID_TYPES, (
        f"{pkg_dir.name}: type='{pkg_data['type']}' invalide "
        f"(valeurs autorisées : {sorted(VALID_TYPES)})"
    )


def test_description_not_empty(pkg_dir: Path, pkg_data: dict) -> None:
    assert str(pkg_data.get("description", "")).strip(), \
        f"{pkg_dir.name}/kubewi.yaml : description vide"


# ── Dépendances ───────────────────────────────────────────────────────────────


def test_deps_is_list_or_absent(pkg_dir: Path, pkg_data: dict) -> None:
    deps = pkg_data.get("deps")
    if deps is not None:
        assert isinstance(deps, list), \
            f"{pkg_dir.name}/kubewi.yaml : 'deps' doit être une liste YAML"


def test_deps_reference_existing_packages(pkg_dir: Path, pkg_data: dict) -> None:
    for dep in pkg_data.get("deps") or []:
        assert dep in ALL_PKG, (
            f"{pkg_dir.name}: dépendance '{dep}' introuvable "
            f"(paquets connus : {sorted(ALL_PKG)})"
        )


def test_deps_respect_type_hierarchy(pkg_dir: Path, pkg_data: dict) -> None:
    """Un paquet ne peut dépendre que de paquets de niveau ≤ au sien."""
    pkg_level = TYPE_LEVEL[pkg_data["type"]]
    for dep in pkg_data.get("deps") or []:
        dep_type = ALL_PKG.get(dep)
        if dep_type is None:
            continue  # déjà signalé par test_deps_reference_existing_packages
        dep_level = TYPE_LEVEL[dep_type]
        assert dep_level <= pkg_level, (
            f"{pkg_dir.name} ({pkg_data['type']}, niveau {pkg_level}) "
            f"dépend de '{dep}' ({dep_type}, niveau {dep_level}) "
            f"— violation de hiérarchie"
        )


# ── Champs optionnels ─────────────────────────────────────────────────────────


def test_provides_is_list_if_present(pkg_dir: Path, pkg_data: dict) -> None:
    provides = pkg_data.get("provides")
    if provides is not None:
        assert isinstance(provides, list), \
            f"{pkg_dir.name}/kubewi.yaml : 'provides' doit être une liste YAML"


def test_image_present_for_workload(pkg_dir: Path, pkg_data: dict) -> None:
    """Les workloads qui buildent une image doivent déclarer 'image'."""
    if pkg_data["type"] == "workload" and (pkg_dir / "Dockerfile").exists():
        assert "image" in pkg_data, \
            f"{pkg_dir.name}: workload avec Dockerfile mais sans champ 'image'"
