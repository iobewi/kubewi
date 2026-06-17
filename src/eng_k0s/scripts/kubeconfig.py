#!/usr/bin/env python3
"""
Récupère le kubeconfig k0s depuis le controller et configure kubectl.

- Lit l'IP et l'utilisateur depuis le projet kubewi courant
- Connexion SSH via la clé kubewi_ansible
- Remplace l'adresse serveur par l'IP WireGuard du controller
- Nomme le contexte d'après le cluster (kubewi.yaml)
- Idempotent : safe à relancer
"""

import subprocess
import sys
from pathlib import Path

from ruamel.yaml import YAML

from kubewi._project import resolve
from kubewi._hostfile import load_all_hosts, load_cluster
from ops_ssh.kubewi.lib import SSH_KEY


KUBECONFIG = Path.home() / '.kube' / 'config'


def _find_controller(project_dir: Path) -> dict:
    hosts = load_all_hosts(project_dir)
    for h in hosts:
        if (h.get('eng_k0s') or {}).get('role') == 'controller':
            return h
    print("  ✗ Aucun controller trouvé dans le projet.")
    sys.exit(1)


def _fetch_raw(host: str, user: str) -> str:
    r = subprocess.run(
        ['ssh',
         '-i', str(SSH_KEY),
         '-o', 'StrictHostKeyChecking=no',
         '-o', 'ConnectTimeout=10',
         f'{user}@{host}',
         'sudo k0s kubeconfig admin'],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        print(f"  ✗ Échec SSH vers {user}@{host} :")
        print(f"    {r.stderr.strip()}")
        print("  → Vérifier que le tunnel WireGuard est actif : kubewi vpn up")
        sys.exit(1)
    return r.stdout


def _rename_context(data: dict, name: str) -> None:
    for c in data.get('clusters', []):
        c['name'] = name
    for u in data.get('users', []):
        u['name'] = name
    for ctx in data.get('contexts', []):
        ctx['name'] = name
        ctx['context']['cluster'] = name
        ctx['context']['user']    = name
    data['current-context'] = name


def main() -> None:
    yaml = YAML()
    yaml.preserve_quotes = True

    project_dir = resolve()
    ctrl        = _find_controller(project_dir)
    host        = ctrl.get('ansible_host', '')
    user        = ctrl.get('ansible_user', 'iobewi')
    cluster     = load_cluster(project_dir)
    ctx_name    = cluster.get('name', 'kubewi')

    if not host:
        print("  ✗ ansible_host absent pour le controller.")
        sys.exit(1)

    print(f"  Récupération du kubeconfig depuis {user}@{host}...")
    raw  = _fetch_raw(host, user)
    data = yaml.load(raw)

    # Remplace l'adresse serveur par l'IP WireGuard (k0s génère parfois 127.0.0.1)
    for c in data.get('clusters', []):
        c['cluster']['server'] = f'https://{host}:6443'

    _rename_context(data, ctx_name)

    KUBECONFIG.parent.mkdir(mode=0o700, exist_ok=True)
    with open(KUBECONFIG, 'w') as f:
        yaml.dump(data, f)
    KUBECONFIG.chmod(0o600)

    print(f"  ✓ {KUBECONFIG}  [contexte : {ctx_name}]")
    print(f"  ✓ Serveur : https://{host}:6443")
    print()
    print("  Vérifier :")
    print("    kubectl get nodes")


if __name__ == '__main__':
    main()
