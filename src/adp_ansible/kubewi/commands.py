"""
role:
    Interface vers les opérations Ansible du cluster KubeWI.

responsibilities:
    - déléguer chaque commande au Makefile ansible/ correspondant
    - exposer les opérations init, wifi, wireguard-keys, vault

does_not:
    - implémenter la logique Ansible (déléguée à Makefile + scripts)
    - gérer l'enrollment des nœuds (kubewi worker / kubewi controller)
"""
from __future__ import annotations

from adp_ansible.kubewi import lib as ansible

NAME = 'ansible'

_TARGETS = {
    'init':           'init',
    'wifi':           'wifi',
    'wireguard-keys': 'wireguard-keys',
    'vault-encrypt':  'vault-encrypt',
    'vault-edit':     'vault-edit',
}


def register(sub) -> None:
    p = sub.add_parser('ansible', help='Opérations Ansible (inventaire, vault, WireGuard)')
    s = p.add_subparsers(dest='ansible_cmd', metavar='CMD', required=True)
    s.add_parser('init',           help='Crée hosts.yml et vault.yml depuis les exemples')
    s.add_parser('wifi',           help='Renseigne les credentials WiFi dans vault.yml')
    s.add_parser('wireguard-keys', help='Génère et injecte les clés WireGuard')
    s.add_parser('vault-encrypt',  help='Chiffre vault.yml avec ansible-vault')
    s.add_parser('vault-edit',     help='Édite le vault chiffré')


def run_cmd(args) -> None:
    ansible.run_make(_TARGETS[args.ansible_cmd])
