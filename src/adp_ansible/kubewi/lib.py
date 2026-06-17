"""
Brique transversale Ansible — utilitaires pour les modules fonctionnels.
"""
from __future__ import annotations

from pathlib import Path

from kubewi._utils import run

PKG_DIR = Path(__file__).parent.parent


def run_playbook(playbook: Path | str, *extra_args: str, env: dict | None = None) -> None:
    from kubewi._project import resolve
    inventory = resolve() / 'hosts.yml'
    run(
        ['ansible-playbook', '-i', str(inventory), str(playbook), *extra_args],
        cwd=str(PKG_DIR),
        env=env,
    )
