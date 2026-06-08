#!/usr/bin/env python3
import re, sys

ctrl_key, sdk_key, ctrl_pub, sdk_pub = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]

vault = 'inventory/group_vars/all/vault.yml'
hosts = 'inventory/hosts.yml'

v = open(vault).read()
v = re.sub(r'vault_wg_controller_private_key:.*', f'vault_wg_controller_private_key: "{ctrl_key}"', v)
v = re.sub(r'vault_wg_sdk_private_key:.*', f'vault_wg_sdk_private_key: "{sdk_key}"', v)
open(vault, 'w').write(v)

h = open(hosts).read()
h = re.sub(r'wg_controller_pubkey:.*', f'wg_controller_pubkey: "{ctrl_pub}"', h)
h = re.sub(r'wg_sdk_pubkey:.*', f'wg_sdk_pubkey: "{sdk_pub}"', h)
open(hosts, 'w').write(h)
