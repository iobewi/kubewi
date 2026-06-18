from __future__ import annotations

import sys
from pathlib import Path

from adp_ansible.kubewi import lib as ansible

_PLAYBOOKS = Path(__file__).parent.parent / 'playbooks'


def _add_worker(args) -> None:
    import getpass
    from kubewi._project import resolve
    from kubewi._hostfile import generate_ansible_inventory, load_host
    from adp_kube.kubewi import lib as kube
    from ops_cluster.kubewi._execute import _banner

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
        ansible.run_playbook(_PLAYBOOKS / 'init.yml', '--limit', name, env=env)
    else:
        become_pass = getpass.getpass(f"  Mot de passe SSH {name} (premier accès) : ")
        env['ANSIBLE_BECOME_PASS'] = become_pass
        print(f"  Bootstrap {name} (premier accès)...")
        ansible.run_playbook(_PLAYBOOKS / 'init.yml', '--limit', name, '-k', env=env)

    print(f"  Enrôlement k0s {name}...")
    kube.add_controller(name)
    print(f"\n  ✓ {name} est membre du cluster Kubernetes\n")
