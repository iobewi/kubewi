"""
Bibliothèque k0s — opérations engine exposées aux couches supérieures.
"""
from __future__ import annotations

import os
from pathlib import Path

from adp_ansible.kubewi import lib as ansible

_PLAYBOOKS = Path(__file__).parent.parent / 'playbooks'


def worker_init(limit: str, become_pass: str) -> None:
    env = os.environ.copy()
    env['ANSIBLE_BECOME_PASS'] = become_pass
    ansible.run_playbook(_PLAYBOOKS / 'workers-init.yml', '--limit', limit, '-k', env=env)


def add_worker(limit: str) -> None:
    ansible.run_playbook(_PLAYBOOKS / 'worker.yml', '--limit', limit)


def add_controller(limit: str) -> None:
    ansible.run_playbook(_PLAYBOOKS / 'controller.yml', '--limit', limit)
