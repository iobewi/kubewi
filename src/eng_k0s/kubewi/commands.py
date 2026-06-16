from __future__ import annotations

import getpass
from pathlib import Path

from kubewi._utils import run
from eng_k0s.kubewi import lib as k0s

NAME = 'k0s'

_PKG_DIR = Path(__file__).parent.parent  # k0s/


def register(sub) -> None:
    p    = sub.add_parser('k0s', help='Kubernetes k0s — distribution légère bare metal')
    cmds = p.add_subparsers(dest='k0s_cmd', metavar='CMD', required=True)

    cmds.add_parser('kubeconfig', help='Récupère le kubeconfig et configure kubectl')

    add_p = cmds.add_parser('add', help='Ajoute un nœud au cluster k0s')
    add_t = add_p.add_subparsers(dest='k0s_add_target', metavar='TARGET', required=True)

    ctrl = add_t.add_parser('controller', help='Déploie k0s sur le(s) controller(s)')
    ctrl.add_argument('--limit', default='controllers', metavar='LIMIT',
                      help='Limite Ansible (défaut: controllers)')

    wkr = add_t.add_parser('worker', help='Initialise et joint un worker au cluster k0s')
    wkr.add_argument('--name', required=True, metavar='NAME',
                     help='Nom du worker dans hosts.yml')


def run_cmd(args) -> None:
    if args.k0s_cmd == 'kubeconfig':
        run(['python3', str(_PKG_DIR / 'scripts' / 'kubeconfig.py')])

    elif args.k0s_cmd == 'add':
        if args.k0s_add_target == 'controller':
            k0s.add_controller(args.limit)
        elif args.k0s_add_target == 'worker':
            become_pass = getpass.getpass('  SSH password : ')
            k0s.worker_init(args.name, become_pass)
            k0s.add_worker(args.name)
