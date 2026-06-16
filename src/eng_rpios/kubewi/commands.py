"""
role:
    Provisioning spécifique Raspberry Pi OS (Debian Trixie aarch64).

responsibilities:
    - activer cgroups memory dans le bootloader (cmdline.txt)
    - désactiver zram swap (spécifique Trixie)

does_not:
    - provisionner le socle Debian générique (kubewi debian)
    - gérer le réseau ou k0s
"""
from __future__ import annotations

from pathlib import Path

from adp_ansible.kubewi import lib as ansible

NAME      = 'rpios'
_PKG_DIR  = Path(__file__).parent.parent
PLAYBOOKS = _PKG_DIR / 'playbooks'


def register(sub) -> None:
    p = sub.add_parser('rpios', help='Provisioning RPi OS — cgroups, zram (Trixie aarch64)')
    s = p.add_subparsers(dest='rpios_cmd', metavar='CMD', required=True)

    prov = s.add_parser('provision', help='Applique les spécificités RPi OS sur les nœuds')
    prov.add_argument('--limit', '-l', metavar='HOSTS',
                      help='Restreindre à certains nœuds (ex: controller-01)')


def run_cmd(args) -> None:
    if args.rpios_cmd == 'provision':
        extra = ['--limit', args.limit] if args.limit else []
        ansible.run_playbook(PLAYBOOKS / 'provision.yml', *extra)
