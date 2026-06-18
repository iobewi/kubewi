from __future__ import annotations

import sys


def _vault_cmd(action: str) -> None:
    from kubewi._project import resolve
    from kubewi._utils import run
    vault = resolve() / 'group_vars' / 'all' / 'vault.yml'
    run(['ansible-vault', action, str(vault)])


def _wifi() -> None:
    import getpass
    import re
    from kubewi._project import resolve

    vault = resolve() / 'group_vars' / 'all' / 'vault.yml'
    if not vault.exists():
        print(f"  ✗ {vault} introuvable")
        sys.exit(1)

    print("\n  Type de WiFi à configurer :")
    print("  [1] Point d'accès AP  (vault_wifi_ap_psk)")
    print("  [2] Client WiFi       (vault_wifi_ssid + vault_wifi_psk)")
    print("  [3] Les deux\n")
    try:
        choice = input("  Choix [1/2/3] : ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\n  Annulé.")
        return

    if choice not in ('1', '2', '3'):
        print("  ✗ Choix invalide.")
        sys.exit(1)

    content = vault.read_text()

    if choice in ('1', '3'):
        psk = getpass.getpass("  Passphrase AP WiFi : ")
        content = re.sub(r'vault_wifi_ap_psk:.*', f'vault_wifi_ap_psk: "{psk}"', content)
        print("  ✓ vault_wifi_ap_psk mis à jour")

    if choice in ('2', '3'):
        ssid = input("  SSID WiFi client   : ").strip()
        psk  = getpass.getpass("  PSK WiFi client    : ")
        content = re.sub(r'vault_wifi_ssid:.*', f'vault_wifi_ssid: "{ssid}"', content)
        content = re.sub(r'vault_wifi_psk:.*',  f'vault_wifi_psk: "{psk}"',  content)
        print("  ✓ vault_wifi_ssid + vault_wifi_psk mis à jour")

    vault.write_text(content)
    print(f"\n  → Chiffrer : kubewi cluster vault-encrypt\n")
