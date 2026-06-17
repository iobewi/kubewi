"""
Gestion de l'inventaire Ansible pour l'enrollment de nœuds.
"""
from __future__ import annotations

from pathlib import Path

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

WORKER_ID_START = 10
ANSIBLE_USER    = 'iobewi'


def hosts_file() -> Path:
    from kubewi._project import resolve
    return resolve() / 'hosts.yml'


def load_hosts():
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.width = 120
    with open(hosts_file()) as f:
        return yaml.load(f), yaml


def save_hosts(data, yaml) -> None:
    with open(hosts_file(), 'w') as f:
        yaml.dump(data, f)


def workers_section(data):
    return data['all']['children']['kubernetes']['children']['workers']['hosts']


def next_host_id(workers) -> int:
    if not workers:
        return WORKER_ID_START
    ids = []
    for hv in (workers or {}).values():
        last = str(hv.get('ansible_host', '')).split('.')[-1]
        if last.isdigit():
            ids.append(int(last))
    return max(ids, default=WORKER_ID_START - 1) + 1


def worker_name(host_id: int) -> str:
    return f'worker-{(host_id - WORKER_ID_START + 1):02d}'


def add_worker(data, yaml, name: str, host_id: int, init_host: str, ifaces: int) -> None:
    workers = workers_section(data)
    if workers is None:
        data['all']['children']['kubernetes']['children']['workers']['hosts'] = CommentedMap()
        workers = workers_section(data)
    entry = CommentedMap()
    entry['ansible_host']           = f'192.168.22.{host_id}'
    entry['ansible_user']           = ANSIBLE_USER
    entry['init_host']              = init_host
    entry['network_bridge_members'] = ['eth0', 'eth1'] if ifaces == 2 else ['eth0']
    workers[name] = entry
    save_hosts(data, yaml)
