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

    inv_p = s.add_parser('inventory-init', help='Crée un nouveau projet kubewi (hosts.yml + vault.yml)')
    inv_p.add_argument('name', metavar='NOM', help='Nom du projet/cluster')
    inv_p.add_argument('--dir', '-d', default='.', metavar='DIR', help='Répertoire parent (défaut: courant)')

    init_p = s.add_parser('init', help='Génère cluster.yaml — description déclarative de la stack')
    init_p.add_argument('--output', '-o', default=None, metavar='FILE')
    init_p.add_argument('--force',  '-f', action='store_true', help='Écraser si existe')

    status_p = s.add_parser('status', help='Affiche l\'état désiré vs enrollé')
    status_p.add_argument('--cluster', default=None, metavar='FILE')

    apply_p = s.add_parser('apply', help='Enrôle les nœuds manquants (cluster.yaml → hosts.yml)')
    apply_p.add_argument('--cluster',  default=None, metavar='FILE')
    apply_p.add_argument('--dry-run', '-n', action='store_true', help='Affiche le plan sans exécuter')
    apply_p.add_argument('--yes',     '-y', action='store_true', help='Skip la confirmation')

    s.add_parser('wifi',          help='Renseigne les credentials WiFi dans vault.yml')
    s.add_parser('vault-encrypt', help='Chiffre vault.yml avec ansible-vault')
    s.add_parser('vault-edit',    help='Édite le vault chiffré')
    s.add_parser('system',        help='Applique la configuration système sur tous les nœuds')
    s.add_parser('network',       help='Applique la configuration réseau sur tous les nœuds')
    s.add_parser('stack',         help='Déploie la stack complète (system + network + k0s)')


def run_cmd(args) -> None:
    if args.cluster_cmd == 'inventory-init': _inventory_init(args); return
    if args.cluster_cmd == 'init':           _init(args);           return
    if args.cluster_cmd == 'status':         _status(args);         return
    if args.cluster_cmd == 'apply':          _apply(args);          return

    make_targets = {'wifi', 'vault-encrypt', 'vault-edit'}
    if args.cluster_cmd in make_targets:
        ansible.run_make(args.cluster_cmd)
    else:
        ansible.run_playbook(PLAYBOOKS / f'{args.cluster_cmd}.yml')


# ── inventory-init ───────────────────────────────────────────────────────────

def _inventory_init(args) -> None:
    from kubewi._project import init as project_init
    parent      = Path(getattr(args, 'dir', '.'))
    project_dir = project_init(args.name, parent)
    print(f"\n  ✓ Projet '{args.name}' créé dans {project_dir.resolve()}")
    print(f"  → cd {project_dir.resolve()}")
    print(f"  → Éditer hosts.yml")
    print(f"  → kubewi cluster init  (génère cluster.yaml)\n")


# ── init ─────────────────────────────────────────────────────────────────────

def _init(args) -> None:
    from kubewi._project import resolve
    project_dir = resolve()
    output      = Path(args.output) if args.output else project_dir / 'cluster.yaml'
    if output.exists() and not args.force:
        print(f"  ✗ {output} existe déjà  (--force pour écraser)")
        sys.exit(1)

    os_pkgs    = _packages_by_type('os')
    node_pkgs  = _node_role_packages()
    os_opts    = ' | '.join(os_pkgs)    if os_pkgs   else 'rpios | ubuntu | debian'
    roles_opts = ' | '.join(node_pkgs)  if node_pkgs else 'k0s | gateway | vpn | ssh'

    content = f"""\
# cluster.yaml — stack déclarative KubeWI
# Généré par kubewi cluster init
# Modifiez ce fichier, puis lancez : kubewi cluster apply
#
# OS disponibles   : {os_opts}
# Rôles disponibles: {roles_opts}

name: kubewi

# Groupes de rôles — sets nommés de packages déployés sur un nœud
role_groups:
  base:
    roles: [k0s, ssh]
  gateway:
    roles: [k0s, ssh, gateway, vpn]

# Profils matériel — décrit le type de machine (arch, os, interfaces réseau)
host_profiles:
  rpi5:
    arch: aarch64
    os: rpios
    ifaces: [eth0]
  x86:
    arch: x86_64
    os: ubuntu
    ifaces: [eth0, eth1]

nodes:
  controller-01:
    ip: 192.168.22.1
    profile: x86
    role_group: gateway
    k0s: controller

  worker-01:
    ip: 192.168.22.10
    profile: rpi5
    role_group: base
    k0s: worker

  worker-02:
    ip: 192.168.22.11
    profile: rpi5
    role_group: base
    k0s: worker
"""

    output.write_text(content)
    print(f"\n  ✓ {output} généré")
    print('  → Éditez le fichier, puis lancez : kubewi cluster apply\n')


# ── apply / status ────────────────────────────────────────────────────────────

def _hosts_yml() -> Path:
    from kubewi._project import resolve
    return resolve() / 'hosts.yml'


def _status(args) -> None:
    cluster, enrolled, plan = _compute_plan(args)
    _print_status(cluster, enrolled, plan)


def _apply(args) -> None:
    cluster, enrolled, plan = _compute_plan(args)
    _print_status(cluster, enrolled, plan)

    if not plan:
        return

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


def _compute_plan(args):
    from kubewi._project import resolve
    project_dir  = resolve()
    cluster_file = Path(args.cluster) if args.cluster else project_dir / 'cluster.yaml'
    if not cluster_file.exists():
        print(f"  ✗ {cluster_file} introuvable — lancez d'abord : kubewi cluster init")
        sys.exit(1)

    cluster  = _load_cluster_yaml(cluster_file)
    enrolled = _load_enrolled_nodes()
    plan     = _build_plan(cluster, enrolled)
    return cluster, enrolled, plan


def _load_cluster_yaml(path: Path) -> dict:
    try:
        from ruamel.yaml import YAML
        _yaml = YAML()
        return dict(_yaml.load(path.read_text()) or {})
    except ImportError:
        import yaml as _y
        return _y.safe_load(path.read_text()) or {}


def _load_enrolled_nodes() -> dict:
    """Returns {hostname: 'controller'|'worker'} parsed from hosts.yml groups."""
    hosts_yml = _hosts_yml()
    if not hosts_yml.exists():
        return {}

    try:
        from ruamel.yaml import YAML
        _yaml = YAML()
        raw = dict(_yaml.load(hosts_yml.read_text()) or {})
    except ImportError:
        import yaml as _y
        raw = _y.safe_load(hosts_yml.read_text()) or {}

    result = {}

    def _collect(node, group):
        if not isinstance(node, dict):
            return
        for hostname in (node.get('hosts') or {}):
            result[hostname] = group
        for child_name, child_data in (node.get('children') or {}).items():
            g = 'controller' if child_name in ('controllers', 'gateways') \
                else 'worker'  if child_name == 'workers' \
                else group
            _collect(child_data or {}, g)

    _collect(raw.get('all', {}), None)
    return result


def _resolve_node(node: dict, cluster: dict) -> dict:
    """Merge host_profile + role_group into node — node fields take precedence."""
    resolved = {}

    profile_name = node.get('profile')
    if profile_name:
        profiles = cluster.get('host_profiles') or {}
        resolved.update(dict(profiles.get(profile_name) or {}))

    group_name = node.get('role_group')
    if group_name:
        groups = cluster.get('role_groups') or {}
        resolved.update(dict(groups.get(group_name) or {}))

    for k, v in node.items():
        resolved[k] = v

    return resolved


def _build_plan(cluster: dict, enrolled: dict) -> list:
    """Returns [(name, resolved_data, action), ...] — controllers before workers."""
    desired = cluster.get('nodes') or {}
    plan = []

    for name, node in desired.items():
        node     = dict(node) if hasattr(node, 'items') else {}
        resolved = _resolve_node(node, cluster)
        if name not in enrolled:
            plan.append((name, resolved, 'enroll'))

    plan.sort(key=lambda x: 0 if x[1].get('k0s') == 'controller' else 1)
    return plan


def _print_status(cluster: dict, enrolled: dict, plan: list) -> None:
    desired = cluster.get('nodes') or {}
    nw = max((len(n) for n in desired), default=12) + 2

    print(f"\n  Cluster : {cluster.get('name', '—')}\n")

    for name, node in desired.items():
        node     = _resolve_node(dict(node) if hasattr(node, 'items') else {}, cluster)
        k0s_role = node.get('k0s', '?')
        profile  = node.get('profile', '')
        group    = node.get('role_group', '')
        pending  = any(n == name for n, _, _ in plan)
        marker   = '→' if pending else '✓'
        state    = 'à enroller' if pending else 'enrollé   '
        tags     = '  ' + '  '.join(t for t in [profile, group] if t)
        print(f"  {marker} {name:<{nw}} {state}  [{k0s_role}]{tags}")

    for name in enrolled:
        if name not in desired:
            print(f"  ⚠ {name:<{nw}} orphan — dans hosts.yml, absent de cluster.yaml")

    if not plan:
        print('\n  Cluster à jour — rien à faire.\n')
    else:
        print(f'\n  {len(plan)} nœud(s) à enroller.\n')


def _execute(plan: list) -> None:
    import getpass
    from adp_kube.kubewi import lib as kube
    from plg_enroll.lib.detection import detect_phase

    steps = [(n, d, a) for n, d, a in plan if a == 'enroll']
    total = len(steps)

    for i, (name, data, _) in enumerate(steps, 1):
        k0s_role = data.get('k0s', 'worker')
        ifaces   = len(data.get('ifaces', ['eth0', 'eth1']))

        print(f"\n{'─' * 56}")
        print(f"  [{i}/{total}] Prochain nœud : {name}  [{k0s_role}]")

        try:
            if k0s_role == 'controller':
                print(f"  Déploiement du controller {name}...")
                kube.add_controller(name)
                print(f"  ✓ {name} est controller du cluster")

            else:
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
                print(f"  ✓ {name} est worker du cluster")

        except KeyboardInterrupt:
            print(f'\n  Interrompu pendant l\'enrollment de {name}.')
            print('  Relancez kubewi cluster apply pour reprendre.')
            return

        if i < total:
            try:
                ans = input('\n  Continuer vers le nœud suivant ? [o/N] ').strip().lower()
            except (EOFError, KeyboardInterrupt):
                print('\n  Arrêt.')
                return
            if ans not in ('o', 'oui', 'y', 'yes'):
                print(f'  Arrêt — {total - i} nœud(s) restant(s). Relancez kubewi cluster apply.')
                return

    print(f"\n{'─' * 56}")
    print(f"  ✓ Tous les nœuds enrollés ({total}/{total}).\n")


# ── helpers ───────────────────────────────────────────────────────────────────

def _packages_by_type(type_filter: str) -> list[str]:
    return [name for name, _ in _iter_manifests() if _.get('type') == type_filter]


def _node_role_packages() -> list[str]:
    """Packages with Ansible roles deployable as node roles (engine/plugin/ops)."""
    result = []
    for name, data in _iter_manifests():
        if name == NAME:
            continue
        t = data.get('type')
        if t not in ('engine', 'plugin', 'ops'):
            continue
        if (_PACKAGES_DIR / name / 'roles').is_dir():
            result.append(name)
    return result


def _iter_manifests():
    try:
        from ruamel.yaml import YAML
        _yaml = YAML()
        parse = lambda t: _yaml.load(t) or {}
    except ImportError:
        import yaml as _y
        parse = lambda t: _y.safe_load(t) or {}

    for pkg_dir in sorted(_PACKAGES_DIR.iterdir()):
        if not pkg_dir.is_dir() or pkg_dir.name.startswith('__'):
            continue
        manifest = pkg_dir / 'kubewi.yaml'
        if not manifest.exists():
            continue
        yield pkg_dir.name, parse(manifest.read_text())
