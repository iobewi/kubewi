"""
role:
    Provisioning base Debian — socle système pour tous les nœuds apt-based.

responsibilities:
    - appliquer le rôle debian (packages, SSH, containerd, chrony, sysctl)

does_not:
    - gérer les spécificités RPi (kubewi rpios)
    - configurer le réseau (kubewi cluster network)
"""
from __future__ import annotations

from pathlib import Path

from adp_ansible.kubewi import lib as ansible

NAME      = 'debian'
_PKG_DIR  = Path(__file__).parent.parent
PLAYBOOKS = _PKG_DIR / 'playbooks'


def register(sub) -> None:
    p = sub.add_parser('debian', help='Provisioning base Debian (packages, SSH, containerd)')
    s = p.add_subparsers(dest='debian_cmd', metavar='CMD', required=True)

    prov = s.add_parser('provision', help='Applique le rôle base Debian sur les nœuds')
    prov.add_argument('--limit', '-l', metavar='HOSTS',
                      help='Restreindre à certains nœuds (ex: controller-01)')


def run_cmd(args) -> None:
    if args.debian_cmd == 'provision':
        extra = ['--limit', args.limit] if args.limit else []
        ansible.run_playbook(PLAYBOOKS / 'provision.yml', *extra)
