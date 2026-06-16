"""
role:
    Configuration du nœud gateway du cluster KubeWI.

responsibilities:
    - déployer la configuration réseau NAT et routage du gateway

does_not:
    - gérer les workers ou controllers (kubewi worker / kubewi controller)
    - configurer le VPN (kubewi vpn)
"""
from __future__ import annotations

from pathlib import Path

from adp_ansible.kubewi import lib as ansible

NAME      = 'gateway'
_PKG_DIR  = Path(__file__).parent.parent
PLAYBOOKS = _PKG_DIR / 'playbooks'


def register(sub) -> None:
    p = sub.add_parser('gateway', help='Configuration du nœud gateway')
    s = p.add_subparsers(dest='gateway_cmd', metavar='CMD', required=True)
    s.add_parser('deploy',      help='Déploie NAT, routage et VLANs du gateway')
    s.add_parser('wifi-deploy', help='Déploie le point d\'accès WiFi hostapd (nécessite wifi_ap dans l\'inventaire)')


def run_cmd(args) -> None:
    if args.gateway_cmd == 'deploy':
        ansible.run_playbook(PLAYBOOKS / 'gateway.yml')
    elif args.gateway_cmd == 'wifi-deploy':
        ansible.run_playbook(PLAYBOOKS / 'wifi.yml')
