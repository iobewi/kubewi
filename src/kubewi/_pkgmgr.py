from __future__ import annotations

import sys
from pathlib import Path

from ._discovery import PACKAGES_DIR


def _load_manifests() -> list[dict]:
    try:
        from ruamel.yaml import YAML as _YAML
        _yaml = _YAML()
        def _parse(text): return dict(_yaml.load(text))
    except ImportError:
        import yaml as _y
        def _parse(text): return _y.safe_load(text) or {}

    result = []
    for pkg_dir in sorted(PACKAGES_DIR.iterdir()):
        if not pkg_dir.is_dir() or pkg_dir.name.startswith('__'):
            continue
        manifest = pkg_dir / 'kubewi.yaml'
        if not manifest.exists():
            continue
        data = _parse(manifest.read_text())
        data.setdefault('name', pkg_dir.name)
        result.append(data)
    return result


def cmd_list(args) -> None:
    packages = _load_manifests()
    if getattr(args, 'type', None):
        packages = [p for p in packages if p.get('type') == args.type]
    if not packages:
        print('  Aucun package trouvé.')
        return

    nw = max(len(p['name']) for p in packages) + 2
    tw = max(len(p.get('type') or '—') for p in packages) + 2

    for p in packages:
        name  = p['name']
        typ   = p.get('type') or '—'
        desc  = p.get('description') or ''
        tags  = _tags(p)
        print(f"  {name:<{nw}} {typ:<{tw}} {desc}{tags}")


def cmd_search(args) -> None:
    query    = args.search.lower()
    packages = _load_manifests()
    matches  = [
        p for p in packages
        if query in p['name'].lower()
        or query in (p.get('description') or '').lower()
        or query in (p.get('type') or '').lower()
        or query in ' '.join(p.get('provides') or []).lower()
        or query in ' '.join(p.get('deps') or []).lower()
    ]
    if not matches:
        print(f"  Aucun résultat pour « {args.query} ».")
        return

    nw = max(len(p['name']) for p in matches) + 2
    tw = max(len(p.get('type') or '—') for p in matches) + 2
    for p in matches:
        print(f"  {p['name']:<{nw}} {(p.get('type') or '—'):<{tw}} {p.get('description') or ''}{_tags(p)}")


def cmd_info_name(name: str) -> None:
    packages = _load_manifests()
    p = next((x for x in packages if x['name'] == name), None)
    if p is None:
        print(f"  ✗ Package inconnu : {name}")
        sys.exit(1)

    fields = [
        ('name',  p.get('name')),
        ('type',  p.get('type')),
        ('desc',  p.get('description')),
        ('deps',  ', '.join(p.get('deps') or []) or None),
        ('roles', ', '.join(p.get('roles') or []) or None),
    ]
    fw = max(len(k) for k, v in fields if v) + 2
    print()
    for key, val in fields:
        if val:
            print(f"  {key:<{fw}} {val}")
    print()


def print_help() -> None:
    print('\nKubeWI — SDK Manager\n')
    print('Usage:')
    print('  kubewi [--list] [--search QUERY] [--info PACKAGE]')
    print('  kubewi <package> <commande> [options]\n')
    print('Gestion des packages:')
    print('  --list   [--type tool|os|ops|service]   Lister les packages')
    print('  --search <query>                         Rechercher un package')
    print('  --info   <package>                       Détails d\'un package')
    print('\n  kubewi <package> --help   pour les commandes d\'un package\n')


def _tags(p: dict) -> str:
    deps = p.get('deps')
    return f"  [deps: {', '.join(deps)}]" if deps else ''
