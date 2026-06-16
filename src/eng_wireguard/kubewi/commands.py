from __future__ import annotations

from eng_wireguard.kubewi import lib as wireguard

NAME = 'wireguard'


def register(sub) -> None:
    p = sub.add_parser('wireguard', help='WireGuard — engine VPN bare metal')
    s = p.add_subparsers(dest='wireguard_cmd', metavar='CMD', required=True)
    s.add_parser('deploy', help='Installe et configure WireGuard sur les controllers')


def run_cmd(args) -> None:
    if args.wireguard_cmd == 'deploy':
        wireguard.deploy()
