from __future__ import annotations

from pathlib import Path

from adp_ansible.kubewi import lib as ansible

_PKG_DIR  = Path(__file__).parent.parent
_PLAYBOOKS = _PKG_DIR / 'playbooks'


def deploy() -> None:
    ansible.run_playbook(_PLAYBOOKS / 'wireguard.yml')
