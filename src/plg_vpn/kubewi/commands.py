from __future__ import annotations

import sys
from pathlib import Path

NAME     = 'vpn'
_PKG_DIR = Path(__file__).parent.parent


def register(sub) -> None:
    p = sub.add_parser('vpn', help='Tunnel WireGuard SDK ↔ cluster')
    s = p.add_subparsers(dest='vpn_cmd', metavar='CMD', required=True)
    s.add_parser('up',            help='Monte le tunnel WireGuard')
    s.add_parser('down',          help='Coupe le tunnel WireGuard')
    s.add_parser('generate-keys', help='Génère et injecte les clés WireGuard dans le vault')
    s.add_parser('write-conf',    help='(Re)génère wg0-sdk.conf depuis les clés existantes')
    s.add_parser('deploy',        help='Déploie WireGuard sur le controller (via engine wireguard)')


def run_cmd(args) -> None:
    if args.vpn_cmd == 'up':
        _up()
    elif args.vpn_cmd == 'down':
        _down()
    elif args.vpn_cmd == 'generate-keys':
        _generate_keys()
    elif args.vpn_cmd == 'write-conf':
        _write_conf()
    elif args.vpn_cmd == 'deploy':
        from eng_wireguard.kubewi import lib as wireguard
        wireguard.deploy()


def _up() -> None:
    from plg_vpn.kubewi.lib import up
    up()


def _down() -> None:
    from plg_vpn.kubewi.lib import down
    down()


def _generate_keys() -> None:
    import re
    import subprocess
    from kubewi._project import resolve

    project = resolve()
    vault   = project / 'group_vars' / 'all' / 'vault.yml'

    if not vault.exists():
        print(f"  ✗ {vault} introuvable")
        sys.exit(1)

    def wg_genkey() -> str:
        return subprocess.check_output(['wg', 'genkey']).decode().strip()

    def wg_pubkey(priv: str) -> str:
        return subprocess.check_output(['wg', 'pubkey'], input=priv.encode()).decode().strip()

    ctrl_key = wg_genkey()
    ctrl_pub = wg_pubkey(ctrl_key)
    sdk_key  = wg_genkey()
    sdk_pub  = wg_pubkey(sdk_key)

    from kubewi._hostfile import find_gateway_host_path, load_host, update_host_section
    gw_path = find_gateway_host_path(project)
    if gw_path is None:
        print(f"  ✗ Aucun fichier host gateway trouvé dans {project / 'hosts'}")
        sys.exit(1)

    host_data = load_host(gw_path)
    init_host = (host_data.get('plg_gateway') or {}).get('init_host') or host_data.get('ansible_host', '')
    ctrl_name = host_data.get('name', 'controller-01')

    v = vault.read_text()
    v = re.sub(r'vault_vpn_controller_private_key:.*', f'vault_vpn_controller_private_key: "{ctrl_key}"', v)
    v = re.sub(r'vault_vpn_sdk_private_key:.*',        f'vault_vpn_sdk_private_key: "{sdk_key}"',        v)
    vault.write_text(v)

    update_host_section(gw_path, 'plg_vpn', {
        'vpn_controller_pubkey': ctrl_pub,
        'vpn_sdk_pubkey':        sdk_pub,
    })

    _write_sdk_conf(project, sdk_key, ctrl_pub, ctrl_name, init_host)

    print(f"  ✓ vault.yml mis à jour (clés privées — à chiffrer !)")
    print(f"  ✓ {gw_path.name} mis à jour (clés publiques dans plg_vpn)")
    print(f"  ✓ wg0-sdk.conf généré (Endpoint: {init_host}:51820)")
    print(f"  → Chiffrer : kubewi cluster vault-encrypt\n")


_WG_SDK_CONF = """\
[Interface]
Address = 10.0.100.2/24
PrivateKey = {sdk_key}

[Peer]
# {ctrl_name}
PublicKey = {ctrl_pub}
Endpoint = {init_host}:51820
AllowedIPs = 10.0.100.0/24, 192.168.22.0/24, 192.168.42.0/24, 192.168.62.0/24

PersistentKeepalive = 25
"""


def _write_conf() -> None:
    """Reconstruit wg0-sdk.conf depuis les clés existantes (vault chiffré ou non)."""
    import subprocess
    from kubewi._project import resolve
    from kubewi._hostfile import find_gateway_host_path, load_host

    project = resolve()
    vault   = project / 'group_vars' / 'all' / 'vault.yml'

    if not vault.exists():
        print(f"  ✗ {vault} introuvable")
        sys.exit(1)

    gw_path = find_gateway_host_path(project)
    if gw_path is None:
        print(f"  ✗ Aucun fichier host gateway trouvé dans {project / 'hosts'}")
        sys.exit(1)

    host_data = load_host(gw_path)
    ctrl_pub  = (host_data.get('plg_vpn') or {}).get('vpn_controller_pubkey', '')
    init_host = (host_data.get('plg_gateway') or {}).get('init_host') or host_data.get('ansible_host', '')
    ctrl_name = host_data.get('name', 'controller-01')

    if not ctrl_pub:
        print("  ✗ vpn_controller_pubkey absent du host file — lancer kubewi vpn generate-keys")
        sys.exit(1)

    vault_text = vault.read_text(errors='replace')
    if vault_text.startswith('$ANSIBLE_VAULT;'):
        result = subprocess.run(['ansible-vault', 'view', str(vault)], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  ✗ Déchiffrement du vault échoué")
            sys.exit(1)
        vault_text = result.stdout

    sdk_key = ''
    for line in vault_text.splitlines():
        if 'vault_vpn_sdk_private_key' in line:
            sdk_key = line.split(':', 1)[-1].strip().strip('"\'')
            break

    if not sdk_key:
        print("  ✗ vault_vpn_sdk_private_key introuvable dans le vault")
        sys.exit(1)

    _write_sdk_conf(project, sdk_key, ctrl_pub, ctrl_name, init_host)
    print(f"  ✓ wg0-sdk.conf généré (Endpoint: {init_host}:51820)")


def _write_sdk_conf(project: Path, sdk_key: str, ctrl_pub: str, ctrl_name: str, init_host: str) -> None:
    conf = project / 'wg0-sdk.conf'
    conf.write_text(_WG_SDK_CONF.format(
        sdk_key   = sdk_key,
        ctrl_pub  = ctrl_pub,
        ctrl_name = ctrl_name,
        init_host = init_host,
    ))
    conf.chmod(0o600)
