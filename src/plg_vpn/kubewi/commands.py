from __future__ import annotations

import sys
from pathlib import Path

from kubewi._utils import run

NAME     = 'vpn'
_PKG_DIR = Path(__file__).parent.parent


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
        _generate_keys()
    elif args.vpn_cmd == 'deploy':
        from eng_wireguard.kubewi import lib as wireguard
        wireguard.deploy()


def _wg_conf() -> Path:
    from kubewi._project import resolve
    return resolve() / 'wg0-sdk.conf'


def _up() -> None:
    conf = _wg_conf()
    if not conf.exists():
        print(f"  ✗ {conf} absent — lancer kubewi vpn generate-keys d'abord")
        sys.exit(1)
    run(['wg-quick', 'up', str(conf)])


def _down() -> None:
    run(['wg-quick', 'down', str(_wg_conf())])


def _generate_keys() -> None:
    import re
    import subprocess
    from kubewi._project import resolve

    project = resolve()
    vault   = project / 'group_vars' / 'all' / 'vault.yml'
    hosts   = project / 'hosts.yml'

    for path in (vault, hosts):
        if not path.exists():
            print(f"  ✗ {path} introuvable")
            sys.exit(1)

    def wg_genkey() -> str:
        return subprocess.check_output(['wg', 'genkey']).decode().strip()

    def wg_pubkey(priv: str) -> str:
        return subprocess.check_output(['wg', 'pubkey'], input=priv.encode()).decode().strip()

    ctrl_key = wg_genkey()
    ctrl_pub = wg_pubkey(ctrl_key)
    sdk_key  = wg_genkey()
    sdk_pub  = wg_pubkey(sdk_key)

    v = vault.read_text()
    v = re.sub(r'vault_wg_controller_private_key:.*', f'vault_wg_controller_private_key: "{ctrl_key}"', v)
    v = re.sub(r'vault_wg_sdk_private_key:.*',        f'vault_wg_sdk_private_key: "{sdk_key}"',        v)
    vault.write_text(v)

    h = hosts.read_text()
    h = re.sub(r'wg_controller_pubkey:.*', f'wg_controller_pubkey: "{ctrl_pub}"', h)
    h = re.sub(r'wg_sdk_pubkey:.*',        f'wg_sdk_pubkey: "{sdk_pub}"',        h)
    hosts.write_text(h)

    print(f"  ✓ vault.yml mis à jour (clés privées — à chiffrer !)")
    print(f"  ✓ hosts.yml mis à jour (clés publiques)")
    print(f"  → Chiffrer : kubewi cluster vault-encrypt\n")
