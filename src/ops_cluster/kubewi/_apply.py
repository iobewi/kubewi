from __future__ import annotations

import sys
from pathlib import Path


def _status(args) -> None:
    hosts, cluster, plan = _compute_plan()
    _print_status(hosts, cluster, plan)


def _apply(args) -> None:
    from kubewi._project import resolve
    from ops_cluster.kubewi._execute import _execute
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
