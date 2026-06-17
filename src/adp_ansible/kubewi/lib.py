"""
Brique transversale Ansible — utilitaires pour les modules fonctionnels.
"""
from __future__ import annotations

import os
from pathlib import Path

from kubewi._utils import run

PKG_DIR = Path(__file__).parent.parent


def run_make(target: str) -> None:
    from kubewi._project import resolve
    env = {**os.environ, 'INVENTORY': str(resolve())}
    run(['make', target], cwd=str(PKG_DIR), env=env)


def run_playbook(playbook: Path | str, *extra_args: str, env: dict | None = None) -> None:
    from kubewi._project import resolve
    inventory = resolve() / 'hosts.yml'
    run(
        ['ansible-playbook', '-i', str(inventory), str(playbook), *extra_args],
        cwd=str(PKG_DIR),
        env=env,
    )
