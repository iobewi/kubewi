from __future__ import annotations

from wrk_buildkit.kubewi import lib as buildkit

NAME = 'buildkit'


def register(sub) -> None:
    p = sub.add_parser('buildkit', help='Engine Docker buildx — build ARM64')
    s = p.add_subparsers(dest='buildkit_cmd', metavar='CMD', required=True)
    s.add_parser('setup', help='Crée et démarre le builder buildx ARM64')


def run_cmd(args) -> None:
    if args.buildkit_cmd == 'setup':
        buildkit.setup()
