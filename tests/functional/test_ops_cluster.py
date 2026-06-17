"""
Tests fonctionnels — ops_cluster
Vérifie inventory-init, init (cluster.yaml), et les commandes make.
"""
from __future__ import annotations

from argparse import Namespace
from pathlib import Path


def _cmds(calls: list[list[str]]) -> list[str]:
    return [" ".join(c) for c in calls]


# ── inventory-init ────────────────────────────────────────────────────────────


def test_inventory_init_creates_project_dir(tmp_path):
    from ops_cluster.kubewi.commands import _inventory_init
    _inventory_init(Namespace(name='mon-cluster', dir=str(tmp_path)))
    assert (tmp_path / 'mon-cluster').is_dir()


def test_inventory_init_creates_marker(tmp_path):
    from kubewi._project import MARKER
    from ops_cluster.kubewi.commands import _inventory_init
    _inventory_init(Namespace(name='mon-cluster', dir=str(tmp_path)))
    assert (tmp_path / 'mon-cluster' / MARKER).exists()


def test_inventory_init_creates_hosts_yml(tmp_path):
    from ops_cluster.kubewi.commands import _inventory_init
    _inventory_init(Namespace(name='mon-cluster', dir=str(tmp_path)))
    assert (tmp_path / 'mon-cluster' / 'hosts.yml').exists()


def test_inventory_init_creates_vault_yml(tmp_path):
    from ops_cluster.kubewi.commands import _inventory_init
    _inventory_init(Namespace(name='mon-cluster', dir=str(tmp_path)))
    assert (tmp_path / 'mon-cluster' / 'group_vars' / 'all' / 'vault.yml').exists()


# ── init (cluster.yaml) ───────────────────────────────────────────────────────


def test_cluster_init_creates_cluster_yaml(project_dir):
    from ops_cluster.kubewi.commands import _init
    _init(Namespace(output=None, force=False))
    assert (project_dir / 'cluster.yaml').exists()


def test_cluster_init_output_contains_nodes(project_dir):
    from kubewi._project import MARKER
    from ops_cluster.kubewi.commands import _init
    # Ajouter un controller dans hosts.yml du projet
    (project_dir / 'hosts.yml').write_text(
        'all:\n  children:\n    kubernetes:\n      children:\n'
        '        controllers:\n          children:\n'
        '            gateways:\n              hosts:\n'
        '                controller-01:\n                  host_id: 1\n'
    )
    _init(Namespace(output=None, force=False))
    content = (project_dir / 'cluster.yaml').read_text()
    assert 'nodes:' in content
    assert 'controller-01' in content
    assert 'name: test-cluster' in content  # nom depuis .kubewi-project


def test_cluster_init_force_overwrites(project_dir):
    from ops_cluster.kubewi.commands import _init
    output = project_dir / 'cluster.yaml'
    output.write_text('old content')
    _init(Namespace(output=None, force=True))
    assert 'old content' not in output.read_text()


# ── wifi / vault ──────────────────────────────────────────────────────────────


def test_wifi_ap_updates_vault(project_dir, monkeypatch):
    from ops_cluster.kubewi.commands import _wifi
    vault = project_dir / 'group_vars' / 'all' / 'vault.yml'
    vault.write_text('vault_wifi_ap_psk: ""\nvault_wifi_ssid: ""\nvault_wifi_psk: ""\n')
    inputs = iter(['1'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    monkeypatch.setattr('getpass.getpass', lambda _: 'test-passphrase')
    _wifi()
    assert 'vault_wifi_ap_psk: "test-passphrase"' in vault.read_text()


def test_wifi_client_updates_vault(project_dir, monkeypatch):
    from ops_cluster.kubewi.commands import _wifi
    vault = project_dir / 'group_vars' / 'all' / 'vault.yml'
    vault.write_text('vault_wifi_ap_psk: ""\nvault_wifi_ssid: ""\nvault_wifi_psk: ""\n')
    inputs = iter(['2', 'MySSID'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    monkeypatch.setattr('getpass.getpass', lambda _: 'test-psk')
    _wifi()
    content = vault.read_text()
    assert 'vault_wifi_ssid: "MySSID"' in content
    assert 'vault_wifi_psk: "test-psk"' in content


def test_vault_encrypt_calls_ansible_vault(mock_subprocess, project_dir):
    from ops_cluster.kubewi.commands import run_cmd
    vault = project_dir / 'group_vars' / 'all' / 'vault.yml'
    vault.write_text('test: value\n')
    run_cmd(Namespace(cluster_cmd='vault-encrypt'))
    assert any('ansible-vault' in c and 'encrypt' in c for c in _cmds(mock_subprocess))
