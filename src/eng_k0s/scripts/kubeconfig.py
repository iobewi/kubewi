#!/usr/bin/env python3
"""
Récupère le kubeconfig k0s depuis le controller et le configure sur le SDK.

- Connexion SSH via ~/.ssh/config (controller-01 doit être configuré)
- Renomme le contexte en 'kubewi' pour lisibilité
- Préserve les permissions 0600
- Idempotent : safe à relancer
"""

import subprocess
import sys
from pathlib import Path

from ruamel.yaml import YAML


KUBECONFIG = Path.home() / '.kube' / 'config'
CONTEXT    = 'kubewi'


def fetch_kubeconfig():
    r = subprocess.run(
        ['ssh', 'controller-01', 'sudo k0s kubeconfig admin'],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        print(f"  ✗ Échec SSH : {r.stderr.strip()}")
        print("  → Vérifier que le tunnel WireGuard est actif (make vpn-up)")
        print("    et que ssh controller-01 fonctionne (make ssh-config)")
        sys.exit(1)
    return r.stdout


def rename_context(data, name):
    """Renomme cluster, user et contexte avec le nom du projet."""
    for cluster in data.get('clusters', []):
        cluster['name'] = name
    for user in data.get('users', []):
        user['name'] = name
    for context in data.get('contexts', []):
        context['name'] = name
        context['context']['cluster'] = name
        context['context']['user']    = name
    data['current-context'] = name


def main():
    yaml = YAML()
    yaml.preserve_quotes = True

    print("  Récupération du kubeconfig depuis controller-01...")
    raw  = fetch_kubeconfig()
    data = yaml.load(raw)

    rename_context(data, CONTEXT)

    KUBECONFIG.parent.mkdir(mode=0o700, exist_ok=True)
    with open(KUBECONFIG, 'w') as f:
        yaml.dump(data, f)
    KUBECONFIG.chmod(0o600)

    server = data['clusters'][0]['cluster']['server']
    print(f"  ✓ kubeconfig sauvegardé dans {KUBECONFIG}")
    print(f"  ✓ Contexte : {CONTEXT}  →  {server}")
    print()
    print("  Vérifier :")
    print("    kubectl get nodes")


if __name__ == '__main__':
    main()
