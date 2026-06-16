#!/usr/bin/env python3
import re, sys

vault_path, ssid, psk = sys.argv[1], sys.argv[2], sys.argv[3]

v = open(vault_path).read()
v = re.sub(r'vault_wifi_ssid:.*', f'vault_wifi_ssid: "{ssid}"', v)
v = re.sub(r'vault_wifi_psk:.*', f'vault_wifi_psk: "{psk}"', v)
open(vault_path, 'w').write(v)
