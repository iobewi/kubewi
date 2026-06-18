from __future__ import annotations

import sys
from pathlib import Path

from adp_ansible.kubewi import lib as ansible

NAME          = 'cluster'
_PKG_DIR      = Path(__file__).parent.parent
_PACKAGES_DIR = _PKG_DIR.parent
PLAYBOOKS     = _PKG_DIR / 'playbooks'


def register(sub) -> None:
    p = sub.add_parser('cluster', help='Gestion déclarative du cluster')
    s = p.add_subparsers(dest='cluster_cmd', metavar='CMD', required=True)

    create_p = s.add_parser('create', help='Crée un nouveau projet kubewi')
    create_p.add_argument('name', metavar='NOM', help='Nom du projet/cluster')
    create_p.add_argument('--dir', '-d', default='.', metavar='DIR', help='Répertoire parent (défaut: courant)')

    s.add_parser('status', help='Affiche l\'état désiré vs enrollé')

    apply_p = s.add_parser('apply', help='Enrôle les nœuds manquants')
    apply_p.add_argument('--dry-run', '-n', action='store_true', help='Affiche le plan sans exécuter')
    apply_p.add_argument('--yes',     '-y', action='store_true', help='Skip la confirmation')

    add_p = s.add_parser('add', help='Ajoute un nœud au cluster existant')
    add_s = add_p.add_subparsers(dest='add_role', metavar='ROLE', required=True)

    add_w = add_s.add_parser('worker', help='Ajoute un worker (auto-détection ou fichier host existant)')
    add_w.add_argument('name', nargs='?', metavar='NAME', help='Nom du worker (mode manuel, fichier hosts/<NAME>.yml requis)')
    add_w.add_argument('--ifaces', type=int, choices=[1, 2], default=2)
    add_w.add_argument('--dry-run', '-n', action='store_true')
    add_w.add_argument('--yes', '-y', action='store_true')

    add_c = add_s.add_parser('controller', help='Ajoute un controller secondaire (fichier hosts/<NAME>.yml requis)')
    add_c.add_argument('name', metavar='NAME')
    add_c.add_argument('--yes', '-y', action='store_true')

    s.add_parser('kubeconfig',     help='Récupère le kubeconfig depuis le controller et configure kubectl')
    s.add_parser('wifi',          help='Renseigne les credentials WiFi dans vault.yml')
    s.add_parser('vault-encrypt', help='Chiffre vault.yml avec ansible-vault')
    s.add_parser('vault-edit',    help='Édite le vault chiffré')
    s.add_parser('system',        help='Applique la configuration système sur tous les nœuds')
    s.add_parser('network',       help='Applique la configuration réseau sur tous les nœuds')
    s.add_parser('stack',         help='Déploie la stack complète (system + network + k0s)')


def run_cmd(args) -> None:
    if args.cluster_cmd == 'create':         _create_project(args); return
    if args.cluster_cmd == 'status':         _status(args);         return
    if args.cluster_cmd == 'apply':          _apply(args);          return
    if args.cluster_cmd == 'add':
        if args.add_role == 'worker':     _add_worker(args)
        elif args.add_role == 'controller': _add_controller(args)
        return
    if args.cluster_cmd == 'kubeconfig':     _kubeconfig();         return
    if args.cluster_cmd == 'wifi':           _wifi();               return
    if args.cluster_cmd == 'vault-encrypt':  _vault_cmd('encrypt'); return
    if args.cluster_cmd == 'vault-edit':     _vault_cmd('edit');    return

    ansible.run_playbook(PLAYBOOKS / f'{args.cluster_cmd}.yml')


# ── kubeconfig ───────────────────────────────────────────────────────────────

def _kubeconfig() -> None:
    from eng_k0s.scripts.kubeconfig import main as fetch
    fetch()



def _fetch_mac(init_host: str, user: str, iface: str) -> str:
    """Récupère la MAC d'une interface via SSH."""
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
    """Renomme le fichier host et met à jour le champ name à l'intérieur."""
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
    """Met à jour le champ gateway dans cluster.yml."""
    from ruamel.yaml import YAML
    yaml = YAML()
    yaml.preserve_quotes = True
    path = project_dir / 'cluster.yml'
    with open(path) as f:
        data = yaml.load(f)
    data['kubewi']['cluster']['gateway'] = new_name
    with open(path, 'w') as f:
        yaml.dump(data, f)


# ── add worker ───────────────────────────────────────────────────────────────

def _add_worker(args) -> None:
    import getpass
    from kubewi._project import resolve
    from kubewi._hostfile import generate_ansible_inventory, load_host
    from adp_kube.kubewi import lib as kube

    project_dir = resolve()

    if args.name:
        host_path = project_dir / 'hosts' / f'{args.name}.yml'
        if not host_path.exists():
            print(f"  ✗ Fichier host introuvable : {host_path}")
            print(f"  → Créer hosts/{args.name}.yml ou lancer sans nom pour la détection auto")
            sys.exit(1)
        data = load_host(host_path)
        name = data.get('name', args.name)
        print(f"\n  Ajout worker (manuel) : {name}\n")
    else:
        from plg_provisioning.kubewi.commands import _deploy, _scale
        from plg_provisioning.kubewi.lib import detect_phase

        print(f"\n  Ajout worker (auto-détection)\n")
        _banner("Activation du réseau de provisioning")
        _deploy()
        _scale(1)
        print("  ✓ DHCP provisioning actif\n")

        try:
            detected = detect_phase(args.ifaces, single=True, dry_run=args.dry_run)
        finally:
            try:
                _scale(0)
            except SystemExit:
                print("  ✗ Échec désactivation provisioning")
                print("  → Désactiver manuellement : kubewi provisioning off")

        if not detected:
            print("  ✗ Aucun nœud détecté.")
            sys.exit(1)

        name = detected[0][0]
        print(f"\n  ✓ Nœud détecté : {name}")

        if args.dry_run:
            print(f"  [DRY-RUN] Aurait enrôlé : {name}")
            return

    generate_ansible_inventory(project_dir)

    become_pass = getpass.getpass(f"  Mot de passe SSH {name} (premier accès) : ")
    print(f"\n  Bootstrap réseau {name}...")
    kube.worker_init(name, become_pass)
    print(f"\n  Enrôlement k0s {name}...")
    kube.add_worker(name)
    print(f"\n  ✓ {name} est membre du cluster Kubernetes\n")


# ── add controller ────────────────────────────────────────────────────────────

def _add_controller(args) -> None:
    import getpass, os, subprocess
    from kubewi._project import resolve
    from kubewi._hostfile import generate_ansible_inventory, load_host
    from adp_kube.kubewi import lib as kube
    from ops_ssh.kubewi.lib import ensure_key, SSH_KEY

    ensure_key()
    project_dir = resolve()
    host_path   = project_dir / 'hosts' / f'{args.name}.yml'
    if not host_path.exists():
        print(f"  ✗ Fichier host introuvable : {host_path}")
        print(f"  → Créer hosts/{args.name}.yml avant d'ajouter ce controller")
        sys.exit(1)

    data         = load_host(host_path)
    name         = data.get('name', args.name)
    init_host    = (data.get('plg_gateway') or {}).get('init_host') or data.get('ansible_host', '')
    ansible_user = data.get('ansible_user', 'iobewi')

    if not init_host:
        print(f"  ✗ ansible_host ou init_host absent dans {host_path.name}")
        sys.exit(1)

    if not args.yes:
        try:
            ans = input(f"  Ajouter le controller {name} ({init_host}) ? [o/N] ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n  Annulé.")
            return
        if ans not in ('o', 'oui', 'y', 'yes'):
            print("  Annulé.")
            return

    generate_ansible_inventory(project_dir)
    env    = os.environ.copy()
    key_ok = subprocess.run(
        ['ssh', '-i', str(SSH_KEY),
         '-o', 'PasswordAuthentication=no', '-o', 'BatchMode=yes',
         '-o', 'StrictHostKeyChecking=no', '-o', 'ConnectTimeout=5',
         f'{ansible_user}@{init_host}', 'true'],
        capture_output=True,
    ).returncode == 0

    if key_ok:
        print(f"  Bootstrap {name} (clé SSH)...")
        ansible.run_playbook(PLAYBOOKS / 'init.yml', '--limit', name, env=env)
    else:
        become_pass = getpass.getpass(f"  Mot de passe SSH {name} (premier accès) : ")
        env['ANSIBLE_BECOME_PASS'] = become_pass
        print(f"  Bootstrap {name} (premier accès)...")
        ansible.run_playbook(PLAYBOOKS / 'init.yml', '--limit', name, '-k', env=env)

    print(f"  Enrôlement k0s {name}...")
    kube.add_controller(name)
    print(f"\n  ✓ {name} est membre du cluster Kubernetes\n")


# ── create (nouveau projet) ───────────────────────────────────────────────────

def _create_project(args) -> None:
    from kubewi._project import init as project_init
    parent      = Path(getattr(args, 'dir', '.'))
    project_dir = project_init(args.name, parent)
    print(f"\n  ✓ Projet '{args.name}' créé dans {project_dir.resolve()}")
    print(f"  → cd {project_dir.resolve()}")
    print(f"  → Éditer hosts/controller-01.yml  (init_host, réseau, clés VPN)")
    print(f"  → kubewi vpn generate-keys")
    print(f"  → kubewi cluster apply\n")


# ── vault ────────────────────────────────────────────────────────────────────

def _vault_cmd(action: str) -> None:
    from kubewi._project import resolve
    from kubewi._utils import run
    vault = resolve() / 'group_vars' / 'all' / 'vault.yml'
    run(['ansible-vault', action, str(vault)])


# ── wifi ─────────────────────────────────────────────────────────────────────

def _wifi() -> None:
    import getpass
    import re
    from kubewi._project import resolve

    vault = resolve() / 'group_vars' / 'all' / 'vault.yml'
    if not vault.exists():
        print(f"  ✗ {vault} introuvable")
        sys.exit(1)

    print("\n  Type de WiFi à configurer :")
    print("  [1] Point d'accès AP  (vault_wifi_ap_psk)")
    print("  [2] Client WiFi       (vault_wifi_ssid + vault_wifi_psk)")
    print("  [3] Les deux\n")
    try:
        choice = input("  Choix [1/2/3] : ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\n  Annulé.")
        return

    if choice not in ('1', '2', '3'):
        print("  ✗ Choix invalide.")
        sys.exit(1)

    content = vault.read_text()

    if choice in ('1', '3'):
        psk = getpass.getpass("  Passphrase AP WiFi : ")
        content = re.sub(r'vault_wifi_ap_psk:.*', f'vault_wifi_ap_psk: "{psk}"', content)
        print("  ✓ vault_wifi_ap_psk mis à jour")

    if choice in ('2', '3'):
        ssid = input("  SSID WiFi client   : ").strip()
        psk  = getpass.getpass("  PSK WiFi client    : ")
        content = re.sub(r'vault_wifi_ssid:.*', f'vault_wifi_ssid: "{ssid}"', content)
        content = re.sub(r'vault_wifi_psk:.*',  f'vault_wifi_psk: "{psk}"',  content)
        print("  ✓ vault_wifi_ssid + vault_wifi_psk mis à jour")

    vault.write_text(content)
    print(f"\n  → Chiffrer : kubewi cluster vault-encrypt\n")


# ── apply / status ────────────────────────────────────────────────────────────

def _status(args) -> None:
    hosts, cluster, plan = _compute_plan()
    _print_status(hosts, cluster, plan)


def _apply(args) -> None:
    from kubewi._project import resolve
    project_dir = resolve()
    changed     = _sync_inventory(project_dir)
    if changed:
        print('  ↻ Inventaire mis à jour\n')

    hosts, cluster, plan = _compute_plan()
    _print_status(hosts, cluster, plan)

    if args.dry_run:
        return

    if not args.yes:
        try:
            answer = input('  Appliquer ? [o/N] ').strip().lower()
        except (EOFError, KeyboardInterrupt):
            print('\n  Annulé.')
            return
        if answer not in ('o', 'oui', 'y', 'yes'):
            print('  Annulé.')
            return

    _execute(plan)


def _sync_inventory(project_dir: Path) -> bool:
    """Régénère hosts.yml et retourne True si le contenu a changé."""
    import hashlib
    from kubewi._hostfile import generate_ansible_inventory

    inventory  = generate_ansible_inventory(project_dir)
    new_hash   = hashlib.sha256(inventory.read_bytes()).hexdigest()

    cache_file = project_dir / '.kubewi' / 'hosts.yml.hash'
    cache_file.parent.mkdir(exist_ok=True)

    old_hash   = cache_file.read_text().strip() if cache_file.exists() else ''
    changed    = new_hash != old_hash
    if changed:
        cache_file.write_text(new_hash)
    return changed


def _compute_plan():
    from kubewi._project import resolve
    from kubewi._hostfile import load_all_hosts, load_cluster
    project_dir = resolve()
    hosts_dir   = project_dir / 'hosts'
    if not hosts_dir.exists() or not any(hosts_dir.glob('*.yml')):
        print(f"  ✗ Aucun fichier host trouvé dans {hosts_dir}")
        print(f"  → Créer un projet : kubewi cluster create <nom>")
        sys.exit(1)

    hosts   = load_all_hosts(project_dir)
    cluster = load_cluster(project_dir)
    plan    = _build_plan(hosts)
    return hosts, cluster, plan


def _build_plan(hosts: list[dict]) -> list:
    """
    Retourne [(reachable: bool, name: str, data: dict), ...] — controllers avant workers.
    reachable = joignable via le réseau de gestion (ansible_host:22).
    """
    import socket
    plan = []
    for h in hosts:
        ip = h.get('ansible_host', '')
        reachable = False
        if ip:
            try:
                with socket.create_connection((ip, 22), timeout=3):
                    reachable = True
            except OSError:
                pass
        plan.append((reachable, h.get('name', ''), h))
    plan.sort(key=lambda x: 0 if (x[2].get('eng_k0s') or {}).get('role') == 'controller' else 1)
    return plan


def _print_status(hosts: list[dict], cluster: dict, plan: list) -> None:
    by_name = {name: reachable for reachable, name, _ in plan}
    nw = max((len(h.get('name', '')) for h in hosts), default=12) + 2

    print(f"\n  Cluster : {cluster.get('name', '—')}\n")

    for h in hosts:
        name      = h.get('name', '?')
        k0s_role  = (h.get('eng_k0s') or {}).get('role', '?')
        reachable = by_name.get(name, False)
        marker    = '✓' if reachable else '→'
        state     = 'en ligne  ' if reachable else 'hors ligne'
        print(f"  {marker} {name:<{nw}} {state}  [{k0s_role}]")

    offline = sum(1 for r, _, _ in plan if not r)
    if offline:
        print(f'\n  {offline} nœud(s) hors ligne — bootstrap requis.\n')
    else:
        print(f'\n  Tous les nœuds en ligne.\n')


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
                        ansible.run_playbook(PLAYBOOKS / 'init.yml', '--limit', name, env=env)
                    else:
                        become_pass = getpass.getpass(f"  Mot de passe SSH {name} (premier accès) : ")
                        env['ANSIBLE_BECOME_PASS'] = become_pass
                        print(f"  Bootstrap {name} (premier accès)...")
                        ansible.run_playbook(PLAYBOOKS / 'init.yml', '--limit', name, '-k', env=env)

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
                    ansible.run_playbook(PLAYBOOKS / 'gateway.yml', '--limit', name, env=env)

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


def _banner(msg: str) -> None:
    print(f"\n  {'─' * 52}")
    print(f"  {msg}")
    print(f"  {'─' * 52}")
