"""
role:
    Utilitaires partagés entre les modules kubewi.

responsibilities:
    - affichage bannière et messages formatés
    - exécution de sous-processus avec affichage de la commande et gestion d'erreur

does_not:
    - implémenter de logique métier
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_WORKSPACE = Path(__file__).parent.parent


def banner(msg: str) -> None:
    print(f"\n  {'─' * 52}")
    print(f"  {msg}")
    print(f"  {'─' * 52}")


def run(
    cmd: list[str],
    cwd: str | None = None,
    check: bool = True,
    **kwargs,
) -> subprocess.CompletedProcess:
    _show(cmd, cwd)
    result = subprocess.run(cmd, cwd=cwd, **kwargs)
    if check and result.returncode != 0:
        sys.exit(result.returncode)
    return result


def _show(cmd: list[str], cwd: str | None) -> None:
    label = ' '.join(str(c) for c in cmd)
    if cwd:
        try:
            loc = Path(cwd).relative_to(_WORKSPACE)
        except ValueError:
            loc = Path(cwd)
        print(f'  \033[2m$ {label}  ({loc})\033[0m', flush=True)
    else:
        print(f'  \033[2m$ {label}\033[0m', flush=True)
