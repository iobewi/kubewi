"""
role:
    Gestion du tunnel WireGuard entre le SDK et le cluster.

responsibilities:
    - monter / couper le tunnel via wg-quick
    - générer et injecter les clés WireGuard (délégué à _ansible)
    - déclencher le déploiement via l'engine wireguard

does_not:
    - configurer le peer côté controller (rôle wireguard Ansible — engine wireguard)
"""
from __future__ import annotations

import sys
from pathlib import Path

from adp_ansible.kubewi import lib as ansible
from kubewi._utils import run

NAME     = 'vpn'
_PKG_DIR = Path(__file__).parent.parent
WG_CONF  = _PKG_DIR.parent.parent / 'work' / 'wg0-sdk.conf'


def register(sub) -> None:
    p = sub.add_parser('vpn', help='Tunnel WireGuard SDK ↔ cluster')
    s = p.add_subparsers(dest='vpn_cmd', metavar='CMD', required=True)
    s.add_parser('up',            help='Monte le tunnel WireGuard')
    s.add_parser('down',          help='Coupe le tunnel WireGuard')
    s.add_parser('generate-keys', help='Génère et injecte les clés WireGuard dans le vault')
    s.add_parser('deploy',        help='Déploie WireGuard sur le controller (via engine wireguard)')


def run_cmd(args) -> None:
    if args.vpn_cmd == 'up':
        _up()
    elif args.vpn_cmd == 'down':
        _down()
    elif args.vpn_cmd == 'generate-keys':
        ansible.run_make('wireguard-keys')
    elif args.vpn_cmd == 'deploy':
        from eng_wireguard.kubewi import lib as wireguard
        wireguard.deploy()


def _up() -> None:
    if not WG_CONF.exists():
        print(f"  ✗ {WG_CONF} absent — lancer kubewi vpn generate-keys d'abord")
        sys.exit(1)
    run(['wg-quick', 'up', str(WG_CONF)])


def _down() -> None:
    run(['wg-quick', 'down', str(WG_CONF)])
