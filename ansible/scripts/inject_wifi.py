#!/usr/bin/env python3
import re, sys

ssid, psk = sys.argv[1], sys.argv[2]

vault = 'inventory/group_vars/all/vault.yml'

v = open(vault).read()
v = re.sub(r'vault_wifi_ssid:.*', f'vault_wifi_ssid: "{ssid}"', v)
v = re.sub(r'vault_wifi_psk:.*', f'vault_wifi_psk: "{psk}"', v)
open(vault, 'w').write(v)
