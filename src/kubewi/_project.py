"""
Résolution du projet kubewi actif.

Priorité :
1. Variable d'environnement KUBEWI_PROJECT
2. Répertoire courant (si marqueur .kubewi-project présent)
3. Erreur explicite
"""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

MARKER  = '.kubewi-project'
ENV_VAR = 'KUBEWI_PROJECT'

_ANSIBLE_PKG = Path(__file__).parent.parent / 'adp_ansible' / 'inventory'


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
    (project_dir / 'group_vars' / 'all').mkdir(parents=True)

    shutil.copy(_ANSIBLE_PKG / 'hosts.yml.example',
                project_dir / 'hosts.yml')
    shutil.copy(_ANSIBLE_PKG / 'group_vars' / 'all' / 'vault.yml.example',
                project_dir / 'group_vars' / 'all' / 'vault.yml')

    _gitignore_if_needed(name, parent)

    return project_dir


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
