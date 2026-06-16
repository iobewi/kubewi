"""
Détection de nœuds via les baux DHCP dnsmasq du réseau de provisioning.
"""
from __future__ import annotations

import subprocess
import sys
import threading
import time

from plg_enroll.lib.inventory import (
    HOSTS_FILE, add_worker, load_hosts, next_host_id, worker_name, workers_section,
)


def read_leases() -> dict[str, str]:
    """Retourne {mac: ip} des baux dnsmasq non expirés.

    Format dnsmasq.leases : <expiry_epoch> <mac> <ip> <hostname> <clientid>
    expiry == 0 → bail permanent (jamais expiré).
    """
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
    Détecte les nouveaux nœuds DHCP en continu.
    Chaque nœud est ajouté à hosts.yml immédiatement.
    L'utilisateur appuie sur Entrée pour terminer.
    Retourne [(name, host_id, init_host, mac), ...]
    """
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


def _banner(msg: str) -> None:
    print(f"\n  {'─' * 52}")
    print(f"  {msg}")
    print(f"  {'─' * 52}")
