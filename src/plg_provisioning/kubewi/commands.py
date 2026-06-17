"""
role:
    Contrôle du réseau de provisioning DHCP pour l'enrollment des workers.

responsibilities:
    - déployer le manifest dnsmasq-provisioning (deploy)
    - activer / désactiver le Deployment dnsmasq-provisioning (on/off)

does_not:
    - détecter ni enrôler les nœuds (kubewi worker add gère le cycle complet)
"""
from __future__ import annotations

from pathlib import Path

from adp_kube.kubewi import lib as kube

NAME = 'provisioning'

_PACKAGES_DIR = Path(__file__).parent.parent.parent
_MANIFESTS    = _PACKAGES_DIR / 'wrk_provisioning' / 'manifests'


def register(sub) -> None:
    p = sub.add_parser('provisioning', help='DHCP de provisioning worker')
    s = p.add_subparsers(dest='provisioning_cmd', metavar='CMD', required=True)
    s.add_parser('deploy', help='Applique le manifest dnsmasq-provisioning sur le cluster')
    s.add_parser('on',     help='Active le DHCP de provisioning (dnsmasq replicas=1)')
    s.add_parser('off',    help='Désactive le DHCP de provisioning (dnsmasq replicas=0)')


def run_cmd(args) -> None:
    if args.provisioning_cmd == 'deploy':
        _deploy()
    elif args.provisioning_cmd == 'on':
        _scale(1)
    elif args.provisioning_cmd == 'off':
        _scale(0)


def _deploy() -> None:
    kube.apply(str(_MANIFESTS / 'dnsmasq.yaml'))
    print('  ✓ manifest dnsmasq-provisioning appliqué')


def _scale(replicas: int) -> None:
    kube.scale('provisioning', 'dnsmasq-provisioning', replicas)
    if replicas == 1:
        kube.rollout_wait('provisioning', 'dnsmasq-provisioning')
        print('  ✓ DHCP provisioning actif — brancher le worker sur le switch cluster')
    else:
        print('  ✓ DHCP provisioning désactivé')
