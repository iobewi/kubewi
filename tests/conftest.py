"""
Fixtures partagées entre tous les tests kubewi.

PKG_DIRS     : tous les paquets ayant kubewi.yaml (incluant les adapters sans CLI)
CLI_PKG_DIRS : paquets qui exposent kubewi/commands.py (commandes CLI)
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

SRC_DIR = Path(__file__).parent.parent / "src"

# src/ doit être dans sys.path pour les imports inter-paquets
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

VALID_TYPES = {"adapter", "engine", "plugin", "ops", "workload"}

TYPE_LEVEL = {
    "adapter":  0,
    "engine":   1,
    "plugin":   2,
    "ops":      2,
    "workload": 3,
}


def _is_package(path: Path) -> bool:
    return (
        path.is_dir()
        and not path.name.startswith("_")
        and path.name != "kubewi"
        and (path / "kubewi.yaml").exists()
    )


PKG_DIRS: list[Path] = sorted(p for p in SRC_DIR.iterdir() if _is_package(p))

# Sous-ensemble avec commandes CLI (kubewi/commands.py présent)
CLI_PKG_DIRS: list[Path] = [p for p in PKG_DIRS if (p / "kubewi" / "commands.py").exists()]


@pytest.fixture(params=PKG_DIRS, ids=lambda p: p.name)
def pkg_dir(request: pytest.FixtureRequest) -> Path:
    return request.param


@pytest.fixture(params=CLI_PKG_DIRS, ids=lambda p: p.name)
def cli_pkg_dir(request: pytest.FixtureRequest) -> Path:
    return request.param
