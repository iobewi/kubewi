"""
role:
    Provisioning base Ubuntu.

responsibilities:
    - appliquer le rôle ubuntu (à venir)

does_not:
    - gérer Debian ou RPi OS (kubewi debian / kubewi rpios)
"""
from __future__ import annotations

from pathlib import Path

from adp_ansible.kubewi import lib as ansible

NAME      = 'ubuntu'
_PKG_DIR  = Path(__file__).parent.parent
PLAYBOOKS = _PKG_DIR / 'playbooks'


def register(sub) -> None:
    p = sub.add_parser('ubuntu', help='Provisioning base Ubuntu (à venir)')
    s = p.add_subparsers(dest='ubuntu_cmd', metavar='CMD', required=True)

    prov = s.add_parser('provision', help='Applique le rôle base Ubuntu sur les nœuds')
    prov.add_argument('--limit', '-l', metavar='HOSTS',
                      help='Restreindre à certains nœuds')


def run_cmd(args) -> None:
    if args.ubuntu_cmd == 'provision':
        extra = ['--limit', args.limit] if args.limit else []
        ansible.run_playbook(PLAYBOOKS / 'provision.yml', *extra)
