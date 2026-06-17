"""
Tests d'intégration CLI :
- discover() trouve tous les paquets CLI
- chaque module expose NAME, register, run_cmd
- register(sub) ne lève pas d'exception
- <nom> --help se termine avec le code 0
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

import pytest

from conftest import CLI_PKG_DIRS, SRC_DIR


def _load_commands(pkg_dir: Path):
    """Charge kubewi/commands.py comme module isolé."""
    mod_name = f"_kubewi_cli_test_{pkg_dir.name}"
    if mod_name in sys.modules:
        return sys.modules[mod_name]
    spec = importlib.util.spec_from_file_location(
        mod_name, pkg_dir / "kubewi" / "commands.py"
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod


# ── Découverte dynamique ───────────────────────────────────────────────────────


def test_discovery_finds_all_packages() -> None:
    """discover() doit retourner un module pour chaque paquet CLI connu."""
    from kubewi._discovery import discover
    modules = discover()
    for pkg_dir in CLI_PKG_DIRS:
        mod = _load_commands(pkg_dir)
        names = getattr(mod, "NAMES", None) or [getattr(mod, "NAME")]
        for name in names:
            assert name in modules, \
                f"'{name}' ({pkg_dir.name}) non découvert par kubewi._discovery.discover()"


# ── Symboles et types ─────────────────────────────────────────────────────────


def test_name_is_non_empty_string(cli_pkg_dir: Path) -> None:
    mod = _load_commands(cli_pkg_dir)
    name = getattr(mod, "NAME", None)
    names = getattr(mod, "NAMES", None)
    assert name is not None or names is not None, \
        f"{cli_pkg_dir.name}/commands.py : ni NAME ni NAMES défini"
    if name is not None:
        assert isinstance(name, str) and name, \
            f"{cli_pkg_dir.name}: NAME doit être une chaîne non vide"
    if names is not None:
        assert isinstance(names, list) and all(isinstance(n, str) for n in names), \
            f"{cli_pkg_dir.name}: NAMES doit être une liste de chaînes"


def test_register_is_callable(cli_pkg_dir: Path) -> None:
    mod = _load_commands(cli_pkg_dir)
    assert callable(getattr(mod, "register", None)), \
        f"{cli_pkg_dir.name}/commands.py : register() non callable"


def test_run_cmd_is_callable(cli_pkg_dir: Path) -> None:
    mod = _load_commands(cli_pkg_dir)
    assert callable(getattr(mod, "run_cmd", None)), \
        f"{cli_pkg_dir.name}/commands.py : run_cmd() non callable"


# ── Intégration argparse ───────────────────────────────────────────────────────


def test_register_does_not_crash(cli_pkg_dir: Path) -> None:
    """register(sub) ne doit pas lever d'exception."""
    mod = _load_commands(cli_pkg_dir)
    parser = argparse.ArgumentParser(prog="kubewi-test")
    sub = parser.add_subparsers(dest="package")
    mod.register(sub)


def test_help_exits_zero(cli_pkg_dir: Path) -> None:
    """kubewi <nom> --help doit terminer avec le code 0."""
    mod = _load_commands(cli_pkg_dir)
    parser = argparse.ArgumentParser(prog="kubewi-test")
    sub = parser.add_subparsers(dest="package")
    mod.register(sub)

    names = getattr(mod, "NAMES", None) or [mod.NAME]
    with pytest.raises(SystemExit) as exc:
        parser.parse_args([names[0], "--help"])
    assert exc.value.code == 0, \
        f"{cli_pkg_dir.name}: --help a retourné le code {exc.value.code}"
