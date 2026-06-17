"""
Résolution du projet kubewi actif.

Priorité :
1. Variable d'environnement KUBEWI_PROJECT
2. Répertoire courant (si marqueur .kubewi-project présent)
3. Erreur explicite
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

MARKER  = '.kubewi-project'
ENV_VAR = 'KUBEWI_PROJECT'

_SRC_DIR    = Path(__file__).parent.parent
_KUBEWI_PKG = Path(__file__).parent


def resolve() -> Path:
    """Retourne le répertoire du projet actif."""
    if env := os.environ.get(ENV_VAR):
        p = Path(env)
        if not p.is_dir():
            print(f"  ✗ {ENV_VAR}={env} : répertoire introuvable")
            sys.exit(1)
        return p.resolve()

    cwd = Path.cwd()
    if (cwd / MARKER).exists():
        return cwd

    print(f"  ✗ Aucun projet kubewi actif.")
    print(f"  → Créer un projet  : kubewi cluster inventory-init <nom>")
    print(f"  → Ou définir       : export {ENV_VAR}=<chemin>")
    sys.exit(1)


def init(name: str, parent: Path) -> Path:
    """Crée un répertoire projet avec marqueur et fichiers template."""
    project_dir = parent / name
    if project_dir.exists():
        print(f"  ✗ '{name}' existe déjà : {project_dir.resolve()}")
        print(f"  → Pour utiliser ce projet : cd {project_dir.resolve()}")
        print(f"  → Ou définir              : export {ENV_VAR}={project_dir.resolve()}")
        sys.exit(1)

    project_dir.mkdir(parents=True)
    (project_dir / MARKER).write_text(f"name: {name}\n")
    (project_dir / 'hosts').mkdir()
    (project_dir / 'group_vars' / 'all').mkdir(parents=True)

    cluster_tmpl = (_SRC_DIR / 'ops_cluster' / 'conf_init' / 'cluster.yml.example').read_text()
    (project_dir / 'cluster.yml').write_text(cluster_tmpl.replace('mon-cluster', name))

    (project_dir / 'hosts' / 'controller-01.yml').write_text(
        _assemble_controller_host('controller-01')
    )

    (project_dir / 'group_vars' / 'all' / 'vault.yml').write_text(_assemble_vault())

    # hosts.yml et cache kubewi sont générés — ne pas les versionner
    (project_dir / '.gitignore').write_text('hosts.yml\n.kubewi/\n')

    _gitignore_if_needed(name, parent)

    return project_dir


# ── assemblage ────────────────────────────────────────────────────────────────

def _assemble_controller_host(hostname: str) -> str:
    """Construit hosts/<hostname>.yml depuis les pkg.yml des packages du graphe."""
    lines = [
        'kubewi:',
        '  host:',
        f'    name: {hostname}',
        '    ansible_host: 10.0.100.1     # IP WireGuard fixe (après init)',
        '    ansible_user: iobewi',
        '    host_id: 1                   # dérive les IPs VLAN : 192.168.22.1, .42.1, .62.1',
    ]

    # Packages dont on suit le graphe de deps pour assembler le controller :
    # - plg_gateway : point d'entrée gateway (amène plg_vpn via ses deps)
    # - eng_k0s     : engine Kubernetes, toujours présent
    for pkg in _pkg_conf_init_ordered(['plg_gateway', 'eng_k0s']):
        section = (_SRC_DIR / pkg / 'conf_init' / 'pkg.yml').read_text().rstrip()
        lines.append('')
        for line in section.splitlines():
            lines.append('    ' + line if line else '')

    lines.append('')
    return '\n'.join(lines) + '\n'


def _assemble_vault() -> str:
    """Concatène les sections vault.yml de chaque package qui en expose une."""
    sections: list[str] = []
    for pkg in sorted(_SRC_DIR.iterdir()):
        if not pkg.is_dir() or pkg.name.startswith('_'):
            continue
        vault_section = pkg / 'conf_init' / 'vault.yml'
        if vault_section.exists():
            sections.append(vault_section.read_text().strip())
    return '\n'.join(sections) + '\n'


def _pkg_conf_init_ordered(roots: list[str]) -> list[str]:
    """
    Parcours DFS pré-ordre du graphe de deps depuis les roots.
    Retourne la liste ordonnée des packages ayant un conf_init/pkg.yml.
    """
    from ruamel.yaml import YAML as _YAML
    _yaml = _YAML()
    seen:   set[str]  = set()
    result: list[str] = []

    def _dfs(pkg: str) -> None:
        if pkg in seen:
            return
        seen.add(pkg)
        if (_SRC_DIR / pkg / 'conf_init' / 'pkg.yml').exists():
            result.append(pkg)
        kubewi_yaml = _SRC_DIR / pkg / 'kubewi.yaml'
        if kubewi_yaml.exists():
            data = _yaml.load(kubewi_yaml.read_text()) or {}
            for dep in (data.get('deps') or []):
                _dfs(dep)

    for root in roots:
        _dfs(root)

    return result


# ── gitignore ─────────────────────────────────────────────────────────────────

def _gitignore_if_needed(name: str, parent: Path) -> None:
    """Ajoute <name>/ au .gitignore si le répertoire parent est dans un dépôt git."""
    import subprocess
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            cwd=str(parent), capture_output=True, text=True,
        )
        if result.returncode != 0:
            return
        git_root  = Path(result.stdout.strip())
        gitignore = git_root / '.gitignore'
        entry     = f'{name}/\n'
        existing  = gitignore.read_text() if gitignore.exists() else ''
        if entry.strip() in [l.strip() for l in existing.splitlines()]:
            return
        with gitignore.open('a') as f:
            f.write(entry)
        print(f"  ✓ '{name}/' ajouté à .gitignore")
    except Exception:
        pass
