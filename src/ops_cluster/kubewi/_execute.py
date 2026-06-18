from __future__ import annotations

import sys
from pathlib import Path

from adp_ansible.kubewi import lib as ansible

_PLAYBOOKS = Path(__file__).parent.parent / 'playbooks'


def _kubeconfig() -> None:
    from eng_k0s.scripts.kubeconfig import main as fetch
    fetch()


def _fetch_mac(init_host: str, user: str, iface: str) -> str:
    import subprocess
    from ops_ssh.kubewi.lib import SSH_KEY
    r = subprocess.run(
        ['ssh', '-i', str(SSH_KEY),
         '-o', 'StrictHostKeyChecking=no', '-o', 'ConnectTimeout=10',
         f'{user}@{init_host}',
         f'cat /sys/class/net/{iface}/address'],
        capture_output=True, text=True,
    )
    if r.returncode != 0 or not r.stdout.strip():
        print(f"  ✗ Impossible de lire la MAC de {iface} sur {init_host}")
        sys.exit(1)
    return r.stdout.strip()


def _rename_host(path: Path, new_name: str) -> None:
    from ruamel.yaml import YAML
    yaml = YAML()
    yaml.preserve_quotes = True
    with open(path) as f:
        data = yaml.load(f)
    data['kubewi']['host']['name'] = new_name
    with open(path, 'w') as f:
        yaml.dump(data, f)
    path.rename(path.parent / f'{new_name}.yml')


def _update_cluster_gateway(project_dir: Path, new_name: str) -> None:
    from ruamel.yaml import YAML
    yaml = YAML()
    yaml.preserve_quotes = True
    path = project_dir / 'cluster.yml'
    with open(path) as f:
        data = yaml.load(f)
    data['kubewi']['cluster']['gateway'] = new_name
    with open(path, 'w') as f:
        yaml.dump(data, f)


def _wait_vpn_ready(name: str, k0s_data: dict, timeout: int = 30) -> None:
    import socket, time
    from kubewi._hostfile import load_all_hosts
    from kubewi._project import resolve

    hosts = load_all_hosts(resolve())
    host  = next((h for h in hosts if h.get('name') == name), {})
    ip    = host.get('ansible_host', '10.0.100.1')

    print(f"  Attente de {ip}:22 via WireGuard (max {timeout}s)...", end='', flush=True)
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with socket.create_connection((ip, 22), timeout=2):
                print(' OK')
                return
        except OSError:
            print('.', end='', flush=True)
            time.sleep(3)

    print()
    print(f"\n  ✗ {ip}:22 injoignable après {timeout}s — diagnostics :")
    print(f"  → Sur le controller : sudo wg show")
    print(f"  → Sur le controller : sudo cat /etc/wireguard/wg0.conf")
    print(f"  → Sur le SDK        : sudo wg show wg0-sdk")
    print(f"  → Sur le SDK        : ping {ip}")
    print(f"  Si le peer SDK est absent de wg0.conf : kubewi cluster apply relancera init.yml\n")
    sys.exit(1)


def _banner(msg: str) -> None:
    print(f"\n  {'─' * 52}")
    print(f"  {msg}")
    print(f"  {'─' * 52}")


def _execute(plan: list) -> None:
    import getpass, os, subprocess
    from adp_kube.kubewi import lib as kube
    from ops_ssh.kubewi.lib import ensure_key, SSH_KEY
    from plg_provisioning.kubewi.lib import detect_phase

    ensure_key()
    total = len(plan)

    for i, (reachable, name, data) in enumerate(plan, 1):
        k0s_role = (data.get('eng_k0s') or {}).get('role', 'worker')
        ifaces   = len((data.get('plg_gateway') or {}).get('network_bridge_members') or ['eth0', 'eth1'])

        print(f"\n{'─' * 56}")
        print(f"  [{i}/{total}] {name}  [{k0s_role}]")

        try:
            if k0s_role == 'controller':
                from plg_vpn.kubewi.lib import up as vpn_up
                env = os.environ.copy()

                if not reachable:
                    init_host    = (data.get('plg_gateway') or {}).get('init_host') or data.get('ansible_host', '')
                    ansible_user = data.get('ansible_user', 'iobewi')
                    key_ok = subprocess.run(
                        ['ssh', '-i', str(SSH_KEY),
                         '-o', 'PasswordAuthentication=no', '-o', 'BatchMode=yes',
                         '-o', 'StrictHostKeyChecking=no', '-o', 'ConnectTimeout=5',
                         f'{ansible_user}@{init_host}', 'true'],
                        capture_output=True,
                    ).returncode == 0
                    if key_ok:
                        print(f"  Bootstrap {name} (clé SSH)...")
                        ansible.run_playbook(_PLAYBOOKS / 'init.yml', '--limit', name, env=env)
                    else:
                        become_pass = getpass.getpass(f"  Mot de passe SSH {name} (premier accès) : ")
                        env['ANSIBLE_BECOME_PASS'] = become_pass
                        print(f"  Bootstrap {name} (premier accès)...")
                        ansible.run_playbook(_PLAYBOOKS / 'init.yml', '--limit', name, '-k', env=env)

                    # Renommage MAC pour le gateway (plg_gateway présent)
                    if data.get('plg_gateway'):
                        from kubewi._hostfile import mac_to_id, generate_ansible_inventory
                        from kubewi._project import resolve as _resolve
                        iface    = ((data.get('plg_gateway') or {}).get('network_bridge_members') or [''])[0]
                        mac      = _fetch_mac(init_host, ansible_user, iface)
                        new_name = f"controller-{mac_to_id(mac)}"
                        if new_name != name:
                            print(f"  Renommage {name} → {new_name} (MAC {mac})...")
                            _proj    = _resolve()
                            _rename_host(_proj / 'hosts' / f'{name}.yml', new_name)
                            _update_cluster_gateway(_proj, new_name)
                            generate_ansible_inventory(_proj)
                            name = new_name
                            print(f"  ✓ hosts/{new_name}.yml  |  gateway: {new_name}")

                    print(f"  Montée du tunnel VPN SDK...")
                    vpn_up()
                    _wait_vpn_ready(name, data)
                else:
                    print(f"  Synchronisation gateway {name}...")
                    ansible.run_playbook(_PLAYBOOKS / 'gateway.yml', '--limit', name, env=env)

                print(f"  Synchronisation k0s sur {name}...")
                kube.add_controller(name)
                print(f"  ✓ {name} synchronisé")

            else:
                if not reachable:
                    print("  Branchez le worker sur le réseau de provisioning.")
                    input('  Prêt ? [Entrée pour démarrer la détection] ')

                    kube.scale('provisioning', 'dnsmasq-provisioning', 1)
                    kube.rollout_wait('provisioning', 'dnsmasq-provisioning')
                    try:
                        detected = detect_phase(ifaces, single=True)
                    finally:
                        try:
                            kube.scale('provisioning', 'dnsmasq-provisioning', 0)
                        except SystemExit:
                            pass

                    if not detected:
                        print(f"  ✗ Aucun nœud détecté pour {name}")
                        continue

                    name = detected[0][0]
                    from kubewi._hostfile import generate_ansible_inventory
                    from kubewi._project import resolve as _resolve
                    generate_ansible_inventory(_resolve())

                    become_pass = getpass.getpass('  SSH password : ')
                    kube.worker_init(name, become_pass)

                kube.add_worker(name)
                print(f"  ✓ {name} synchronisé")

        except KeyboardInterrupt:
            print(f'\n  Interrompu pendant la synchronisation de {name}.')
            print('  Relancez kubewi cluster apply pour reprendre.')
            return

        if i < total:
            try:
                ans = input('\n  Continuer ? [o/N] ').strip().lower()
            except (EOFError, KeyboardInterrupt):
                print('\n  Arrêt.')
                return
            if ans not in ('o', 'oui', 'y', 'yes'):
                print(f'  Arrêt — {total - i} nœud(s) restant(s).')
                return

    print(f"\n{'─' * 56}")
    print(f"  ✓ Cluster synchronisé ({total}/{total} nœuds).\n")
