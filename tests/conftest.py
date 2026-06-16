"""
Fixtures partagées entre tous les tests kubewi.

PKG_DIRS  : liste de tous les répertoires de paquets sous src/
pkg_dir   : fixture parametrisée — un cas par paquet
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
        and (path / "kubewi" / "commands.py").exists()
    )


PKG_DIRS: list[Path] = sorted(p for p in SRC_DIR.iterdir() if _is_package(p))


@pytest.fixture(params=PKG_DIRS, ids=lambda p: p.name)
def pkg_dir(request: pytest.FixtureRequest) -> Path:
    return request.param
