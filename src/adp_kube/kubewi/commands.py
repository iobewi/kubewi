from __future__ import annotations

import getpass

from adp_kube.kubewi import lib as kube

NAME = 'kube'


def register(sub) -> None:
    p    = sub.add_parser('kube', help='Kubernetes — interface générique (engine-agnostic)')
    cmds = p.add_subparsers(dest='kube_cmd', metavar='CMD', required=True)

    add_p = cmds.add_parser('add', help='Ajoute un nœud au cluster')
    add_t = add_p.add_subparsers(dest='kube_add_target', metavar='TARGET', required=True)

    ctrl = add_t.add_parser('controller', help='Déploie k0s sur le(s) controller(s)')
    ctrl.add_argument('--limit', default='controllers', metavar='LIMIT',
                      help='Limite Ansible (défaut: controllers)')

    wkr = add_t.add_parser('worker', help='Initialise et joint un worker au cluster')
    wkr.add_argument('--name', required=True, metavar='NAME',
                     help='Nom du worker dans hosts.yml')


def run_cmd(args) -> None:
    if args.kube_cmd == 'add':
        if args.kube_add_target == 'controller':
            kube.add_controller(args.limit)
        elif args.kube_add_target == 'worker':
            become_pass = getpass.getpass('  SSH password : ')
            kube.worker_init(args.name, become_pass)
            kube.add_worker(args.name)
