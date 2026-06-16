"""
role:
    Enrollment de nœuds dans le cluster via la chaîne enroll → kube → k0s.

responsibilities:
    - orchestrer le workflow complet : provisioning DHCP, détection, inventaire, enrollment
    - déléguer les opérations engine à kube (qui délègue à k0s)

does_not:
    - connaître les détails de k0s, dnsmasq ou de l'inventaire Ansible directement
"""
from __future__ import annotations

import getpass
import subprocess
import sys

from adp_kube.kubewi import lib as kube
from plg_enroll.lib.detection import detect_phase
from plg_enroll.lib.inventory import HOSTS_FILE

NAME = 'enroll'


def register(sub) -> None:
    p = sub.add_parser('enroll', help='Enrollment de nœuds dans le cluster')
    s = p.add_subparsers(dest='enroll_role', metavar='ROLE', required=True)

    w = s.add_parser('worker', help='Détecte et enrôle de nouveaux workers')
    w.add_argument('--ifaces',         type=int, choices=[1, 2], default=2)
    w.add_argument('--yes', '-y',      action='store_true')
    w.add_argument('--single', '-1',   action='store_true')
    w.add_argument('--inventory-only', action='store_true')
    w.add_argument('--dry-run', '-n',  action='store_true')

    c = s.add_parser('controller', help='Enrôle un controller dans le cluster')
    c.add_argument('--name',           required=True, metavar='NAME', help='Nom du controller dans hosts.yml')
    c.add_argument('--yes', '-y',      action='store_true')
    c.add_argument('--inventory-only', action='store_true')


def run_cmd(args) -> None:
    if args.enroll_role == 'worker':
        _enroll_worker(args)
    elif args.enroll_role == 'controller':
        _enroll_controller(args)


def _enroll_worker(args) -> None:
    if args.single:
        args.yes = True
    if args.dry_run:
        args.yes = True

    _banner("KubeWI — Enrollment worker")
    if args.dry_run:
        print("  Mode : dry-run (aucune modification)")
    elif args.single:
        print("  Mode : single (auto)")
    else:
        print(f"  Mode : {'non-interactif' if args.yes else 'interactif'}")
    print(f"  Ansible : {'désactivé (dry-run)' if args.dry_run else 'désactivé (inventory-only)' if args.inventory_only else 'activé'}")
    print(f"  Interfaces : {args.ifaces}")

    _provisioning_on()

    try:
        detected = detect_phase(args.ifaces, single=args.single, dry_run=args.dry_run)

        if not detected:
            print("\n  Aucun nœud détecté.")
            return

        _summary(detected)

        if args.dry_run:
            limit = ','.join(n for n, *_ in detected)
            print("  Aucune modification effectuée (dry-run).")
            print(f"  Aurait enrôlé : {limit}")
            return

        if args.inventory_only:
            print("  Nœuds ajoutés à hosts.yml.")
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

        _run_enrollment([name for name, *_ in detected])
        _provisioning_off()

    except KeyboardInterrupt:
        print("\n  Interruption.")
        _provisioning_off()

    except SystemExit:
        print("\n  ✗ Enrollment échoué — provisioning DHCP maintenu pour debug.")
        print("  → Désactiver manuellement : kubewi provisioning off")
        raise


def _run_enrollment(names: list[str]) -> None:
    limit = ','.join(names)

    _banner(f"Phase 1/2 — Bootstrap réseau  [{limit}]")
    become_pass = getpass.getpass("  SSH password : ")

    kube.worker_init(limit, become_pass)
    print("\n  ✓ Phase 1 terminée")

    _banner(f"Phase 2/2 — Provisioning k0s  [{limit}]")
    kube.add_worker(limit)

    _banner("Enrollment terminé")
    for name in names:
        print(f"  ✓ {name} est membre du cluster Kubernetes")
    print("\n  → kubectl get nodes")


def _enroll_controller(args) -> None:
    _banner(f"KubeWI — Enrollment controller [{args.name}]")

    if args.inventory_only:
        print("  Nœud à ajouter manuellement dans hosts.yml puis relancer sans --inventory-only.")
        return

    if not args.yes:
        try:
            confirm = input(f"  Lancer l'enrollment de {args.name} ? [O/n] ").strip().lower()
        except KeyboardInterrupt:
            print("\n  Annulé.")
            return
        if confirm in ('n', 'no', 'non'):
            print("  Annulé.")
            return

    _banner(f"Provisioning controller [{args.name}]")
    kube.add_controller(args.name)

    _banner("Enrollment terminé")
    print(f"  ✓ {args.name} est membre du cluster Kubernetes")
    print("\n  → kubectl get nodes")


def _provisioning_on() -> None:
    _banner("Activation du réseau de provisioning")
    kube.scale('provisioning', 'dnsmasq-provisioning', 1)
    kube.rollout_wait('provisioning', 'dnsmasq-provisioning')
    print("  ✓ DHCP provisioning actif\n")


def _provisioning_off() -> None:
    print()
    try:
        kube.scale('provisioning', 'dnsmasq-provisioning', 0)
        print("  ✓ DHCP provisioning désactivé")
    except SystemExit:
        print("  ✗ Échec de la désactivation du DHCP provisioning")
        print("  → Désactiver manuellement : kubewi provisioning off")


def _banner(msg: str) -> None:
    print(f"\n  {'─' * 52}")
    print(f"  {msg}")
    print(f"  {'─' * 52}")


def _summary(detected: list) -> None:
    _banner(f"Récapitulatif — {len(detected)} nœud(s) détecté(s)")
    print(f"  {'Nœud':<16} {'IP provisioning':<18} {'IP VLAN 220'}")
    print(f"  {'─'*16} {'─'*18} {'─'*16}")
    for name, host_id, init_host, _ in detected:
        print(f"  {name:<16} {init_host:<18} 192.168.22.{host_id}")
    print()
