#!/usr/bin/env python3
import re, sys

vault_path, hosts_path = sys.argv[1], sys.argv[2]
ctrl_key, sdk_key, ctrl_pub, sdk_pub = sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6]

v = open(vault_path).read()
v = re.sub(r'vault_wg_controller_private_key:.*', f'vault_wg_controller_private_key: "{ctrl_key}"', v)
v = re.sub(r'vault_wg_sdk_private_key:.*', f'vault_wg_sdk_private_key: "{sdk_key}"', v)
open(vault_path, 'w').write(v)

h = open(hosts_path).read()
h = re.sub(r'wg_controller_pubkey:.*', f'wg_controller_pubkey: "{ctrl_pub}"', h)
h = re.sub(r'wg_sdk_pubkey:.*', f'wg_sdk_pubkey: "{sdk_pub}"', h)
open(hosts_path, 'w').write(h)
