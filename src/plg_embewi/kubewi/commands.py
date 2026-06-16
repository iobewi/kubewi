"""
role:
    Déploiement et supervision d'embewi-core sur le cluster KubeWI.

responsibilities:
    - installer les CRDs McuNode + McuDeployment
    - déployer le controller embewi-core (Deployment, RBAC, Namespace)
    - afficher l'état des nœuds MCU et des déploiements firmware

does_not:
    - gérer les firmwares ESP32 (OTA piloté par McuDeployment)
    - configurer le WiFi AP (kubewi gateway wifi-deploy)
"""
from __future__ import annotations

from pathlib import Path

from adp_kube.kubewi import lib as kube

NAME      = 'embewi'
_PKG_DIR  = Path(__file__).parent.parent
MANIFESTS = _PKG_DIR / 'manifests'


def register(sub) -> None:
    p = sub.add_parser('embewi', help='Controller ESP32 — embewi-core')
    s = p.add_subparsers(dest='embewi_cmd', metavar='CMD', required=True)
    s.add_parser('deploy', help='Installe CRDs + Deployment embewi-core')
    s.add_parser('status', help='État des McuNode et McuDeployment')
    logs_p = s.add_parser('logs', help='Logs du controller embewi-core')
    logs_p.add_argument('--tail', type=int, default=100, metavar='N',
                        help='Nombre de lignes à afficher (défaut: 100)')


def run_cmd(args) -> None:
    if args.embewi_cmd == 'deploy':
        _deploy()
    elif args.embewi_cmd == 'status':
        _status()
    elif args.embewi_cmd == 'logs':
        _logs(args.tail)


def _deploy() -> None:
    kube.apply(str(MANIFESTS / 'crds.yaml'))
    kube.apply(str(MANIFESTS / 'embewi-core.yaml'))
    kube.rollout_wait('embewi', 'embewi-core', timeout='120s')


def _status() -> None:
    kube.kubectl('get', 'mcu', '-A', '-o', 'wide')
    kube.kubectl('get', 'mcudep', '-A', '-o', 'wide')


def _logs(tail: int) -> None:
    kube.kubectl('logs', '-n', 'embewi', '-l', 'app=embewi-core',
                 f'--tail={tail}', '--follow=false')
