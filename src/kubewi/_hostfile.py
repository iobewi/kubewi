"""
Parseur et générateur de fichiers host KubeWI.

Format source  : hosts/<nom>.yml  — un fichier par machine, édité par l'utilisateur
Format généré  : hosts.yml        — inventaire Ansible, jamais édité à la main
"""
from __future__ import annotations

from io import StringIO
from pathlib import Path


# ── Utilitaires MAC ──────────────────────────────────────────────────────────

def mac_to_id(mac: str) -> str:
    """Retourne les 3 derniers octets d'une adresse MAC en minuscules sans séparateurs.
    Ex: '28:94:01:88:c2:40' → '88c240'
    """
    parts = mac.replace('-', ':').split(':')
    return ''.join(parts[-3:]).lower()


def next_host_id() -> int:
    """Retourne le prochain host_id disponible pour un worker (VLAN 220 : 192.168.22.X)."""
    from kubewi._project import resolve
    hosts = load_all_hosts(resolve())
    ids   = []
    for h in hosts:
        ah = str(h.get('ansible_host', ''))
        if ah.startswith('192.168.22.'):
            last = ah.split('.')[-1]
            if last.isdigit():
                ids.append(int(last))
    return max(ids, default=9) + 1


# ── Lecture ───────────────────────────────────────────────────────────────────

def load_host(path: Path) -> dict:
    """Parse un fichier hosts/xxx.yml, retourne la section host avec _path."""
    raw  = _yaml_load(path)
    host = dict((raw.get('kubewi') or {}).get('host') or {})
    host['_path'] = path
    return host


def load_all_hosts(project_dir: Path) -> list[dict]:
    """Charge tous les fichiers hosts/*.yml du projet, triés par nom."""
    hosts_dir = project_dir / 'hosts'
    if not hosts_dir.exists():
        return []
    return [load_host(p) for p in sorted(hosts_dir.glob('*.yml'))]


def load_cluster(project_dir: Path) -> dict:
    """Charge cluster.yml — métadonnées du cluster."""
    path = project_dir / 'cluster.yml'
    if not path.exists():
        return {}
    raw = _yaml_load(path)
    return dict((raw.get('kubewi') or {}).get('cluster') or {})


def find_gateway_host_path(project_dir: Path) -> Path | None:
    """Retourne le chemin du fichier host gateway (le premier ayant plg_gateway)."""
    hosts_dir = project_dir / 'hosts'
    if not hosts_dir.exists():
        return None
    for p in sorted(hosts_dir.glob('*.yml')):
        raw = _yaml_load(p)
        if 'plg_gateway' in ((raw.get('kubewi') or {}).get('host') or {}):
            return p
    return None


# ── Mise à jour d'un fichier host ─────────────────────────────────────────────

def update_host_section(path: Path, section: str, updates: dict) -> None:
    """Met à jour les clés d'une section paquet (préserve les commentaires)."""
    from ruamel.yaml import YAML
    y = YAML()
    y.preserve_quotes = True
    data = y.load(path.read_text())
    target = data['kubewi']['host'].setdefault(section, {})
    for key, val in updates.items():
        target[key] = val
    s = StringIO()
    y.dump(data, s)
    path.write_text(s.getvalue())


def set_enrolled(path: Path) -> None:
    """Marque un host comme enrollé dans son fichier."""
    from ruamel.yaml import YAML
    y = YAML()
    y.preserve_quotes = True
    data = y.load(path.read_text())
    data['kubewi']['host']['enrolled'] = True
    s = StringIO()
    y.dump(data, s)
    path.write_text(s.getvalue())


# ── Création d'un fichier host worker ─────────────────────────────────────────

def create_worker_host_file(
    project_dir: Path,
    name: str,
    ansible_host: str,
    ansible_user: str,
    init_host: str,
    bridge_members: list[str],
) -> Path:
    """Crée hosts/<name>.yml pour un worker détecté."""
    path = project_dir / 'hosts' / f'{name}.yml'
    _yaml_dump({
        'kubewi': {
            'host': {
                'name':                   name,
                'ansible_host':           ansible_host,
                'ansible_user':           ansible_user,
                'plg_gateway': {
                    'init_host':              init_host,
                    'network_bridge_members': bridge_members,
                },
                'eng_k0s':                {'role': 'worker'},
            }
        }
    }, path)
    return path


# ── Génération de l'inventaire Ansible ───────────────────────────────────────

def generate_ansible_inventory(project_dir: Path) -> Path:
    """Génère hosts.yml (Ansible) depuis hosts/*.yml. Appelé automatiquement."""
    hosts  = load_all_hosts(project_dir)
    inv    = to_ansible_inventory(hosts, load_cluster(project_dir))
    output = project_dir / 'hosts.yml'
    _yaml_dump(inv, output)
    return output


def to_ansible_inventory(hosts: list[dict], cluster: dict) -> dict:
    """Construit le dict d'inventaire Ansible depuis les configs host KubeWI."""
    gateways:    dict = {}
    controllers: dict = {}
    workers:     dict = {}

    for h in hosts:
        name     = h.get('name', '')
        k0s_role = ((h.get('eng_k0s') or {}).get('role') or '')
        is_gw    = 'plg_gateway' in h and k0s_role == 'controller'
        avars    = _ansible_vars(h)

        if is_gw:
            gateways[name]    = avars
        elif k0s_role == 'controller':
            controllers[name] = avars
        elif k0s_role == 'worker':
            workers[name]     = avars

    ctrl_children: dict = {}
    if gateways:
        ctrl_children['gateways'] = {'hosts': gateways}
    if controllers:
        ctrl_children['controllers'] = {'hosts': controllers}

    k8s_children: dict = {}
    if ctrl_children:
        k8s_children['controllers'] = {'children': ctrl_children}
    if workers:
        k8s_children['workers'] = {
            'vars': {
                'ansible_ssh_common_args': (
                    "-o ProxyJump={{ hostvars[groups['gateways'][0]]['ansible_user'] }}"
                    "@{{ hostvars[groups['gateways'][0]]['ansible_host'] }}"
                    " -o StrictHostKeyChecking=no"
                ),
            },
            'hosts': workers,
        }

    return {'all': {'children': {'kubernetes': {'children': k8s_children}}}}


def _ansible_vars(host: dict) -> dict:
    """Aplatit la config KubeWI d'un host en vars Ansible (clés attendues par les rôles)."""
    SKIP = {'name', 'plg_gateway', 'plg_vpn', 'eng_k0s', 'enrolled', '_path'}
    vars: dict = {}

    # Vars de connexion au niveau host (ansible_host, ansible_user, host_id, init_host, ...)
    for key, val in host.items():
        if key not in SKIP and val is not None:
            vars[key] = val

    # plg_gateway.* → aplatir (init_host, network_*, wifi_ap, ...)
    for key, val in (host.get('plg_gateway') or {}).items():
        if val is not None:
            vars[key] = val

    # plg_vpn.* → aplatir (vpn_controller_pubkey, vpn_sdk_pubkey)
    for key, val in (host.get('plg_vpn') or {}).items():
        if val is not None:
            vars[key] = val

    return vars


# ── YAML helpers ──────────────────────────────────────────────────────────────

def _yaml_load(path: Path) -> dict:
    try:
        from ruamel.yaml import YAML
        return YAML().load(path.read_text()) or {}
    except ImportError:
        import yaml
        return yaml.safe_load(path.read_text()) or {}


def _yaml_dump(data: dict, path: Path) -> None:
    try:
        from ruamel.yaml import YAML
        y = YAML()
        y.default_flow_style = False
        y.width = 120
        s = StringIO()
        y.dump(data, s)
        path.write_text(s.getvalue())
    except ImportError:
        import yaml
        path.write_text(yaml.dump(data, default_flow_style=False, allow_unicode=True))
