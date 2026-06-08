#!/usr/bin/env python3
"""
Enrollment automatique de nœuds dans le cluster KubeWI.

Modes :
  make add-worker              — détecte plusieurs nœuds, Entrée pour stopper,
                                 enrollment collectif sur tous en une passe
  make add-worker YES=1        — même chose sans confirmation
  make add-worker INVENTORY_ONLY=1 — ajout dans hosts.yml uniquement, pas d'Ansible

Usage direct (depuis ansible/) :
  python3 scripts/enroll.py worker [--yes] [--inventory-only] [--ifaces 1|2]
"""

import argparse
import getpass
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

HOSTS_FILE      = Path('inventory/hosts.yml')
WORKER_ID_START = 10
ANSIBLE_USER    = 'iobewi'


# ── YAML ─────────────────────────────────────────────────────────────────────

def load_hosts():
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.width = 120
    with open(HOSTS_FILE) as f:
        return yaml.load(f), yaml


def save_hosts(data, yaml):
    with open(HOSTS_FILE, 'w') as f:
        yaml.dump(data, f)


def workers_section(data):
    return data['all']['children']['kubernetes']['children']['workers']['hosts']


# ── Numérotation ─────────────────────────────────────────────────────────────

def next_host_id(workers):
    if not workers:
        return WORKER_ID_START
    ids = []
    for hv in (workers or {}).values():
        last = str(hv.get('ansible_host', '')).split('.')[-1]
        if last.isdigit():
            ids.append(int(last))
    return max(ids, default=WORKER_ID_START - 1) + 1


def worker_name(host_id):
    return f'worker-{(host_id - WORKER_ID_START + 1):02d}'


# ── dnsmasq ───────────────────────────────────────────────────────────────────

def kubectl(*args, **kw):
    return subprocess.run(['kubectl'] + list(args), capture_output=True, text=True, **kw)


def provisioning_on():
    _banner("Activation du réseau de provisioning")
    subprocess.run(
        ['kubectl', '-n', 'provisioning', 'scale',
         'deployment', 'dnsmasq-provisioning', '--replicas=1'],
        check=True, capture_output=True
    )
    subprocess.run(
        ['kubectl', '-n', 'provisioning', 'rollout', 'status',
         'deployment/dnsmasq-provisioning', '--timeout=60s'],
        check=True
    )
    print("  ✓ DHCP provisioning actif\n")


def provisioning_off():
    print()
    r = kubectl('-n', 'provisioning', 'scale',
                'deployment', 'dnsmasq-provisioning', '--replicas=0')
    if r.returncode == 0:
        print("  ✓ DHCP provisioning désactivé")
    else:
        print("  ✗ Échec de la désactivation du DHCP provisioning")
        print(f"    {r.stderr.strip()}")
        print("  → Désactiver manuellement :")
        print("    kubectl -n provisioning scale deployment dnsmasq-provisioning --replicas=0")


def read_leases():
    """Retourne {mac: ip} des baux dnsmasq non expirés.

    Format dnsmasq.leases : <expiry_epoch> <mac> <ip> <hostname> <clientid>
    expiry == 0 → bail permanent (jamais expiré).
    """
    r = kubectl('-n', 'provisioning', 'exec',
                'deploy/dnsmasq-provisioning', '--',
                'cat', '/var/lib/misc/dnsmasq.leases')
    leases = {}
    now = time.time()
    for line in r.stdout.strip().splitlines():
        parts = line.split()
        if len(parts) >= 3:
            expiry, mac, ip = parts[0], parts[1], parts[2]
            if expiry == '0' or int(expiry) > now:
                leases[mac] = ip
    return leases


# ── Inventaire ────────────────────────────────────────────────────────────────

def add_worker(data, yaml, name, host_id, init_host, ifaces):
    workers = workers_section(data)
    if workers is None:
        data['all']['children']['kubernetes']['children']['workers']['hosts'] = CommentedMap()
        workers = workers_section(data)
    entry = CommentedMap()
    entry['ansible_host']         = f'192.168.22.{host_id}'
    entry['ansible_user']         = ANSIBLE_USER
    entry['init_host']            = init_host
    entry['network_bridge_members'] = ['eth0', 'eth1'] if ifaces == 2 else ['eth0']
    workers[name] = entry
    save_hosts(data, yaml)


# ── Phase détection ───────────────────────────────────────────────────────────

def detect_phase(ifaces, single=False, dry_run=False):
    """
    Détecte les nouveaux nœuds DHCP en continu.
    Chaque nœud est ajouté à hosts.yml immédiatement.
    L'utilisateur appuie sur Entrée pour terminer.
    Retourne la liste des nœuds détectés : [(name, host_id, init_host, mac), ...]
    """
    detected   = []
    stop_event = threading.Event()

    def _wait_enter():
        try:
            sys.stdin.readline()
        except (EOFError, KeyboardInterrupt):
            pass
        stop_event.set()

    t = threading.Thread(target=_wait_enter, daemon=True)
    t.start()

    _banner("Phase détection — brancher le nœud sur le switch cluster" if single
            else "Phase détection — brancher les nœuds sur le switch cluster")
    if not single:
        print("  Appuyer sur [Entrée] pour terminer la détection\n")
    print(f"  {'Nœud':<16} {'IP provisioning':<18} {'IP VLAN 220':<16} {'MAC'}")
    print(f"  {'─'*16} {'─'*18} {'─'*16} {'─'*17}")

    known = read_leases()

    while not stop_event.is_set():
        leases = read_leases()
        new    = {mac: ip for mac, ip in leases.items() if mac not in known}

        for mac, ip in new.items():
            data, yaml = load_hosts()
            host_id    = next_host_id(workers_section(data))
            name       = worker_name(host_id)
            if not dry_run:
                add_worker(data, yaml, name, host_id, ip, ifaces)
            prefix = "  [DRY-RUN]" if dry_run else "  "
            detected.append((name, host_id, ip, mac))
            known[mac] = ip
            print(f"{prefix} {name:<16} {ip:<18} 192.168.22.{host_id:<6} {mac}")
            if single:
                stop_event.set()
                break

        if not stop_event.is_set():
            time.sleep(3)

    return detected


# ── Enrollment ────────────────────────────────────────────────────────────────

def run(cmd, env=None):
    result = subprocess.run(cmd, env=env)
    if result.returncode != 0:
        print(f"\n  ✗ Échec : {' '.join(cmd)}")
        sys.exit(1)


def enroll_all(names):
    limit = ','.join(names)

    _banner(f"Phase 1/2 — Bootstrap réseau  [{limit}]")

    # Collecter le mot de passe une fois : utilisé pour ANSIBLE_BECOME_PASS (env).
    # Ansible affichera son propre "SSH password:" via -k → 2 prompts clairs au total.
    become_pass = getpass.getpass("  SSH password : ")
    env = os.environ.copy()
    env['ANSIBLE_BECOME_PASS'] = become_pass

    print("  → ansible-playbook workers-init.yml\n")
    run([
        'ansible-playbook', '-i', 'inventory/hosts.yml',
        'playbooks/workers-init.yml', '--limit', limit,
        '-k',
    ], env=env)

    print(f"\n  ✓ Phase 1 terminée")

    _banner(f"Phase 2/2 — Provisioning k0s  [{limit}]")
    print("  → ansible-playbook worker.yml\n")
    run([
        'ansible-playbook', '-i', 'inventory/hosts.yml',
        'playbooks/worker.yml', '--limit', limit,
    ])

    _banner("Enrollment terminé")
    for name in names:
        print(f"  ✓ {name} est membre du cluster Kubernetes")
    print(f"\n  → kubectl get nodes")


# ── Affichage ─────────────────────────────────────────────────────────────────

def _banner(msg):
    print(f"\n  {'─' * 52}")
    print(f"  {msg}")
    print(f"  {'─' * 52}")


def _summary(detected):
    _banner(f"Récapitulatif — {len(detected)} nœud(s) détecté(s)")
    print(f"  {'Nœud':<16} {'IP provisioning':<18} {'IP VLAN 220'}")
    print(f"  {'─'*16} {'─'*18} {'─'*16}")
    for name, host_id, init_host, _ in detected:
        print(f"  {name:<16} {init_host:<18} 192.168.22.{host_id}")
    print()


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Enrollment nœuds KubeWI')
    parser.add_argument('type', choices=['worker', 'controller'])
    parser.add_argument('--ifaces', type=int, choices=[1, 2], default=2)
    parser.add_argument('--yes', '-y', action='store_true',
                        help='Non-interactif : enrollment automatique sans confirmation')
    parser.add_argument('--single', '-1', action='store_true',
                        help='Détecte un seul nœud, enrollment immédiat (--yes implicite)')
    parser.add_argument('--inventory-only', action='store_true',
                        help='Ajouter à hosts.yml uniquement, sans Ansible')
    parser.add_argument('--dry-run', '-n', action='store_true',
                        help='Simule l\'enrollment sans modifier hosts.yml ni lancer Ansible')
    args = parser.parse_args()

    # --single implique --yes
    if args.single:
        args.yes = True
    # --dry-run implique --yes (pas de confirmation pour une simulation)
    if args.dry_run:
        args.yes = True

    if args.type == 'controller':
        print("  Enrollment controller — non implémenté")
        sys.exit(1)

    _banner("KubeWI — Enrollment worker")
    if args.dry_run:
        print(f"  Mode : dry-run (aucune modification)")
    elif args.single:
        print(f"  Mode : single (auto)")
    else:
        print(f"  Mode : {'non-interactif' if args.yes else 'interactif'}")
    print(f"  Ansible : {'désactivé (dry-run)' if args.dry_run else 'désactivé (inventory-only)' if args.inventory_only else 'activé'}")
    print(f"  Interfaces : {args.ifaces}")

    provisioning_on()

    try:
        detected = detect_phase(args.ifaces, single=args.single, dry_run=args.dry_run)

        if not detected:
            print("\n  Aucun nœud détecté.")
            return

        _summary(detected)

        if args.dry_run:
            limit = ','.join(n for n, *_ in detected)
            print("  Aucune modification effectuée (dry-run).")
            print("  Aurait ajouté à hosts.yml et exécuté :")
            print(f"    ansible-playbook -i inventory/hosts.yml playbooks/workers-init.yml --limit {limit} -k --ask-become-pass")
            print(f"    ansible-playbook -i inventory/hosts.yml playbooks/worker.yml --limit {limit}")
            return

        if args.inventory_only:
            print("  Nœuds ajoutés à hosts.yml.")
            print("  Lancer l'enrollment manuellement :")
            limit = ','.join(n for n, *_ in detected)
            print(f"    ansible-playbook -i inventory/hosts.yml playbooks/workers-init.yml --limit {limit} -k --ask-become-pass")
            print(f"    ansible-playbook -i inventory/hosts.yml playbooks/worker.yml --limit {limit}")
            return

        if not args.yes:
            try:
                confirm = input("  Lancer l'enrollment sur tous les nœuds ? [O/n] ").strip().lower()
            except KeyboardInterrupt:
                print("\n  Annulé.")
                return
            if confirm in ('n', 'no', 'non'):
                print("  Annulé — nœuds conservés dans hosts.yml.")
                return

        enroll_all([name for name, *_ in detected])
        provisioning_off()

    except KeyboardInterrupt:
        print("\n  Interruption.")
        provisioning_off()

    except SystemExit:
        print("\n  ✗ Enrollment échoué — provisioning DHCP maintenu pour debug.")
        print("  → Désactiver manuellement après investigation :")
        print("    make provisioning-off")
        raise


if __name__ == '__main__':
    main()
