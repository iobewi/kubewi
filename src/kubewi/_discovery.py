"""
role:
    Découverte dynamique des paquets kubewi dans packages/.

responsibilities:
    - ajouter packages/ à sys.path pour rendre les briques transversales importables
    - scanner packages/ et charger les paquets fonctionnels (sans préfixe _)
    - construire le mapping group → module

does_not:
    - valider la logique des commandes (déléguée à chaque paquet)
    - charger les paquets transversaux comme commandes CLI
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

PACKAGES_DIR = Path(__file__).parent.parent          # /workspace/src
_ROOT        = str(PACKAGES_DIR)


def _setup_path() -> None:
    # src/ → kubewi.interfaces + tous les packages importables depuis le même dossier
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)


def discover() -> dict[str, ModuleType]:
    _setup_path()

    modules: dict[str, ModuleType] = {}
    for pkg_dir in sorted(PACKAGES_DIR.iterdir()):
        if not pkg_dir.is_dir() or pkg_dir.name.startswith('__'):
            continue
        commands_file = pkg_dir / 'kubewi' / 'commands.py'
        if not commands_file.exists():
            continue
        mod   = _load(commands_file, pkg_dir.name)
        names = getattr(mod, 'NAMES', None) or [getattr(mod, 'NAME', pkg_dir.name)]
        for name in names:
            modules[name] = mod
    return modules


def service_provides(interface: str) -> dict[str, object]:
    """Retourne {service_name: handler} pour les packages qui implémentent interface."""
    try:
        from ruamel.yaml import YAML as _YAML
        _yaml = _YAML()
    except ImportError:
        import yaml as _stdlib_yaml
        _yaml = None

    _setup_path()
    result: dict[str, object] = {}

    for pkg_dir in sorted(PACKAGES_DIR.iterdir()):
        if not pkg_dir.is_dir() or pkg_dir.name.startswith('__'):
            continue
        manifest = pkg_dir / 'kubewi.yaml'
        if not manifest.exists():
            continue
        handler_path = pkg_dir / interface / 'handler.py'
        if not handler_path.exists():
            continue
        mod = _load(handler_path, f'_svc_{pkg_dir.name}_{interface}')
        h   = getattr(mod, 'handler', None)
        if h is not None:
            result[pkg_dir.name] = h

    return result


def _load(path: Path, pkg_name: str) -> ModuleType:
    mod_name = f'_kubewi_pkg_{pkg_name}'
    spec = importlib.util.spec_from_file_location(mod_name, path)
    mod  = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod
