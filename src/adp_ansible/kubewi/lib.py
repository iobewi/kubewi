"""
Brique transversale Ansible — utilitaires pour les modules fonctionnels.
"""
from __future__ import annotations

from pathlib import Path

from kubewi._utils import run

PKG_DIR   = Path(__file__).parent.parent
WORK_DIR  = PKG_DIR.parent.parent / 'work'
INVENTORY = WORK_DIR / 'hosts.yml'


def run_make(target: str, **kwargs) -> None:
    run(['make', target], cwd=str(PKG_DIR), **kwargs)


def run_playbook(playbook: Path | str, *extra_args: str, env: dict | None = None) -> None:
    run(
        ['ansible-playbook', '-i', str(INVENTORY), str(playbook), *extra_args],
        cwd=str(PKG_DIR),
        env=env,
    )
