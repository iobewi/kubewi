"""
Découverte de nœuds via les baux DHCP du réseau de provisioning.
"""
from __future__ import annotations

import subprocess
import sys
import threading
import time


ANSIBLE_USER    = 'iobewi'
BRIDGE_MEMBERS  = ['eth0', 'eth1']


def read_leases() -> dict[str, str]:
    """Retourne {mac: ip} des baux dnsmasq actifs."""
    r = subprocess.run(
        ['kubectl', '-n', 'provisioning', 'exec',
         'deploy/dnsmasq-provisioning', '--',
         'cat', '/var/lib/misc/dnsmasq.leases'],
        capture_output=True, text=True,
    )
    leases: dict[str, str] = {}
    now = time.time()
    for line in r.stdout.strip().splitlines():
        parts = line.split()
        if len(parts) >= 3:
            expiry, mac, ip = parts[0], parts[1], parts[2]
            if expiry == '0' or int(expiry) > now:
                leases[mac] = ip
    return leases


def detect_phase(ifaces: int, single: bool = False, dry_run: bool = False) -> list:
    """
    Détecte les nœuds DHCP et crée leurs fichiers host (nommage MAC).
    Retourne [(name, host_id, init_host, mac), ...]
    """
    from kubewi._hostfile import mac_to_id, next_host_id, create_worker_host_file
    from kubewi._project import resolve

    detected:   list = []
    stop_event = threading.Event()

    def _wait_enter():
        try:
            sys.stdin.readline()
        except (EOFError, KeyboardInterrupt):
            pass
        stop_event.set()

    threading.Thread(target=_wait_enter, daemon=True).start()

    _banner("Phase détection — brancher le nœud sur le switch cluster" if single
            else "Phase détection — brancher les nœuds sur le switch cluster")
    if not single:
        print("  Appuyer sur [Entrée] pour terminer la détection\n")
    print(f"  {'Nœud':<16} {'IP provisioning':<18} {'IP VLAN 220':<16} {'MAC'}")
    print(f"  {'─'*16} {'─'*18} {'─'*16} {'─'*17}")

    known       = read_leases()
    project_dir = resolve()
    bm          = BRIDGE_MEMBERS[:ifaces]

    while not stop_event.is_set():
        leases = read_leases()
        new    = {mac: ip for mac, ip in leases.items() if mac not in known}

        for mac, ip in new.items():
            node_id     = mac_to_id(mac)
            name        = f'worker-{node_id}'
            host_id     = next_host_id()
            ansible_host = f'192.168.22.{host_id}'

            if not dry_run:
                create_worker_host_file(
                    project_dir  = project_dir,
                    name         = name,
                    ansible_host = ansible_host,
                    ansible_user = ANSIBLE_USER,
                    init_host    = ip,
                    bridge_members = bm,
                )

            prefix = "  [DRY-RUN]" if dry_run else "  "
            detected.append((name, host_id, ip, mac))
            known[mac] = ip
            print(f"{prefix} {name:<16} {ip:<18} {ansible_host:<16} {mac}")

            if single:
                stop_event.set()
                break

        if not stop_event.is_set():
            time.sleep(3)

    return detected


def _banner(msg: str) -> None:
    print(f"\n  {'─' * 52}")
    print(f"  {msg}")
    print(f"  {'─' * 52}")
