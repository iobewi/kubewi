"""
role:
    Gestion des accès SSH du SDK vers les nœuds du cluster.

responsibilities:
    - générer la clé kubewi_ansible si absente
    - configurer ~/.ssh/config (controller + workers via ProxyJump)
    - distribuer la clé publique sur tous les nœuds via mot de passe
    - installer la clé SDK sur le bastion (opération initiale unique)

does_not:
    - gérer le tunnel WireGuard (kubewi vpn)
    - provisionner les nœuds (kubewi worker / kubewi ansible)
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from ruamel.yaml import YAML

from kubewi._utils import banner, run

NAME     = 'ssh'
SSH_KEY  = Path.home() / '.ssh' / 'kubewi_ansible'


def _inventory() -> Path:
    from kubewi._project import resolve
    return resolve() / 'hosts.yml'
SSH_CONFIG     = Path.home() / '.ssh' / 'config'
WG_INTERFACE   = 'wg0-sdk'


# ── ssh config ────────────────────────────────────────────────────────────────

def _gateway_name() -> str:
    yaml = YAML()
    with open(_inventory()) as f:
        data = yaml.load(f)
    gateways = data['all']['children']['kubernetes']['children']['controllers']['children']['gateways']['hosts']
    return next(iter(gateways))


def config_main() -> None:
    if not _inventory().exists():
        print(f"  ✗ {_inventory()} absent — lancer kubewi ansible init d'abord")
        sys.exit(1)

    yaml = YAML()
    with open(_inventory()) as f:
        data = yaml.load(f)

    gateways     = data['all']['children']['kubernetes']['children']['controllers']['children']['gateways']['hosts']
    gateway_name = next(iter(gateways))
    gateway      = gateways[gateway_name]
    wg_ip        = gateway['ansible_host']
    ssh_user     = gateway.get('ansible_user', 'iobewi')

    config_text = SSH_CONFIG.read_text() if SSH_CONFIG.exists() else ''
    if f'Host {gateway_name}' in config_text:
        print('  - ~/.ssh/config déjà configuré, ignoré')
        return

    SSH_CONFIG.parent.mkdir(mode=0o700, exist_ok=True)
    with SSH_CONFIG.open('a') as f:
        f.write(f'\nHost {gateway_name} {wg_ip}\n')
        f.write(f'\tHostName {wg_ip}\n')
        f.write(f'\tUser {ssh_user}\n')
        f.write(f'\tIdentityFile {SSH_KEY}\n')
        f.write(f'\tStrictHostKeyChecking no\n')
        f.write(f'\nHost 192.168.22.*\n')
        f.write(f'\tUser {ssh_user}\n')
        f.write(f'\tIdentityFile {SSH_KEY}\n')
        f.write(f'\tProxyJump {gateway_name}\n')
        f.write(f'\tStrictHostKeyChecking no\n')

    SSH_CONFIG.chmod(0o600)
    print(f'  ✓ ~/.ssh/config configuré ({gateway_name} + workers via ProxyJump)')


# ── ssh init ──────────────────────────────────────────────────────────────────

def init_main() -> None:
    if not _inventory().exists():
        print(f"  ✗ {_inventory()} absent — lancer kubewi ansible init d'abord")
        sys.exit(1)

    banner('KubeWI — Initialisation SSH')

    gateway_name = _gateway_name()
    _check_vpn()
    _generate_key()
    config_main()
    _push_key('controllers', '1/2 — controllers (accès direct WireGuard)')
    _push_key('workers',     '2/2 — workers (via ProxyJump controller)')
    _test_connection(gateway_name)
    print()


def _check_vpn() -> None:
    r = subprocess.run(['ip', 'link', 'show', WG_INTERFACE], capture_output=True)
    if r.returncode != 0:
        print(f"  ✗ Tunnel WireGuard inactif — lancer kubewi vpn up d'abord")
        sys.exit(1)


def _generate_key() -> None:
    if SSH_KEY.exists():
        print(f'  - Clé {SSH_KEY} déjà présente, réutilisée')
    else:
        run(['ssh-keygen', '-t', 'ed25519', '-N', '', '-f', str(SSH_KEY), '-C', 'kubewi-ansible-sdk'])
        print(f'  ✓ Clé générée : {SSH_KEY}')


def _push_key(group: str, label: str) -> None:
    pubkey = SSH_KEY.with_suffix('.pub').read_text().strip()
    print(f'\n  Étape {label}')
    print(f'  → Entrer le mot de passe de iobewi')
    r = subprocess.run([
        'ansible', group, '-i', str(_inventory()),
        '-m', 'ansible.posix.authorized_key',
        '-a', f"user=iobewi key='{pubkey}'",
        '-k',
    ])
    if r.returncode != 0:
        print(f'\n  ✗ Échec déploiement clé sur {group}')
        sys.exit(1)
    print(f'  ✓ Clé installée sur {group}')


def _test_connection(gateway_name: str) -> None:
    r = subprocess.run(['ssh', gateway_name, 'hostname'], capture_output=True)
    if r.returncode == 0:
        print(f'\n  ✓ SSH opérationnel — lancer kubewi k0s kubeconfig')
    else:
        print(f'\n  ✗ Connexion SSH vers {gateway_name} échouée')
        sys.exit(1)


# ── ssh setup (bastion) ───────────────────────────────────────────────────────

def setup_main(bastion_host: str, bootstrap_user: str, ssh_user: str) -> None:
    key_path = Path.home() / '.ssh' / 'id_ed25519'
    if not key_path.exists():
        run(['ssh-keygen', '-t', 'ed25519', '-N', '', '-f', str(key_path)])

    b64 = subprocess.run(
        ['base64', '-w0', str(key_path.with_suffix('.pub'))],
        capture_output=True, text=True, check=True
    ).stdout.strip()

    remote_cmd = (
        f"sudo mkdir -p /home/{ssh_user}/.ssh && "
        f"sudo chmod 700 /home/{ssh_user}/.ssh && "
        f"sudo touch /home/{ssh_user}/.ssh/authorized_keys && "
        f"sudo chmod 600 /home/{ssh_user}/.ssh/authorized_keys && "
        f"sudo chown -R {ssh_user}:{ssh_user} /home/{ssh_user}/.ssh && "
        f"echo {b64} | base64 -d | sudo tee -a /home/{ssh_user}/.ssh/authorized_keys > /dev/null"
    )
    run(['ssh', '-t', f'{bootstrap_user}@{bastion_host}', remote_cmd])
    print(f'Clé installée — test : ssh {ssh_user}@{bastion_host} echo ok')


# ── register / run ────────────────────────────────────────────────────────────

def register(sub) -> None:
    p = sub.add_parser('ssh', help='Accès SSH aux nœuds du cluster')
    s = p.add_subparsers(dest='ssh_cmd', metavar='CMD', required=True)

    s.add_parser('init',   help='Génère et distribue la clé SSH sur tous les nœuds')
    s.add_parser('config', help='Configure ~/.ssh/config (controller + workers)')

    setup = s.add_parser('setup', help='Installe la clé SSH sur le bastion (opération initiale unique)')
    setup.add_argument('--bastion-host',   required=True, metavar='HOST')
    setup.add_argument('--bootstrap-user', default='ubuntu')
    setup.add_argument('--ssh-user',       default='iobewi')


def run_cmd(args) -> None:
    if args.ssh_cmd == 'init':
        init_main()
    elif args.ssh_cmd == 'config':
        config_main()
    elif args.ssh_cmd == 'setup':
        setup_main(args.bastion_host, args.bootstrap_user, args.ssh_user)
