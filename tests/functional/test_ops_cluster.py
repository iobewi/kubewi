"""
Tests fonctionnels — ops_cluster
Vérifie cluster create (crée le projet) et commandes cluster.
"""
from __future__ import annotations

from argparse import Namespace
from pathlib import Path


def _cmds(calls: list[list[str]]) -> list[str]:
    return [" ".join(c) for c in calls]


# ── cluster create (nouveau projet) ──────────────────────────────────────────


def test_create_project_creates_dir(tmp_path):
    from ops_cluster.kubewi.commands import _create_project
    _create_project(Namespace(name='mon-cluster', dir=str(tmp_path)))
    assert (tmp_path / 'mon-cluster').is_dir()


def test_create_project_creates_marker(tmp_path):
    from kubewi._project import MARKER
    from ops_cluster.kubewi.commands import _create_project
    _create_project(Namespace(name='mon-cluster', dir=str(tmp_path)))
    assert (tmp_path / 'mon-cluster' / MARKER).exists()


def test_create_project_creates_controller_host(tmp_path):
    from ops_cluster.kubewi.commands import _create_project
    _create_project(Namespace(name='mon-cluster', dir=str(tmp_path)))
    assert (tmp_path / 'mon-cluster' / 'hosts' / 'controller-01.yml').exists()


def test_create_project_creates_vault_yml(tmp_path):
    from ops_cluster.kubewi.commands import _create_project
    _create_project(Namespace(name='mon-cluster', dir=str(tmp_path)))
    assert (tmp_path / 'mon-cluster' / 'group_vars' / 'all' / 'vault.yml').exists()


def test_create_project_creates_cluster_yml(tmp_path):
    from ops_cluster.kubewi.commands import _create_project
    _create_project(Namespace(name='mon-cluster', dir=str(tmp_path)))
    assert (tmp_path / 'mon-cluster' / 'cluster.yml').exists()


# ── cluster apply génère hosts.yml ────────────────────────────────────────────


def test_apply_generates_hosts_yml(project_dir):
    from kubewi._hostfile import generate_ansible_inventory
    generate_ansible_inventory(project_dir)
    assert (project_dir / 'hosts.yml').exists()


def test_apply_hosts_yml_contains_controller(project_dir):
    from kubewi._hostfile import generate_ansible_inventory
    generate_ansible_inventory(project_dir)
    content = (project_dir / 'hosts.yml').read_text()
    assert 'controller-01' in content


def test_apply_hosts_yml_contains_gateway_section(project_dir):
    from kubewi._hostfile import generate_ansible_inventory
    generate_ansible_inventory(project_dir)
    content = (project_dir / 'hosts.yml').read_text()
    assert 'gateways' in content


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


# ── cluster add worker (manuel) ───────────────────────────────────────────────


def test_add_worker_manual_missing_file_exits(project_dir):
    from ops_cluster.kubewi.commands import _add_worker
    import pytest
    with pytest.raises(SystemExit):
        _add_worker(Namespace(name='worker-aabbcc', ifaces=2, dry_run=False, yes=False))


def test_add_worker_manual_calls_worker_init_and_add(mock_subprocess, project_dir, monkeypatch):
    from ops_cluster.kubewi.commands import _add_worker

    (project_dir / 'hosts' / 'worker-aabbcc.yml').write_text(
        'kubewi:\n  host:\n'
        '    name: worker-aabbcc\n'
        '    ansible_host: 192.168.22.10\n'
        '    ansible_user: iobewi\n'
        '    plg_gateway:\n'
        '      init_host: "192.168.0.10"\n'
        '      network_bridge_members: [eth0, eth1]\n'
        '    eng_k0s:\n'
        '      role: worker\n'
    )
    monkeypatch.setattr('getpass.getpass', lambda _: 'pass')
    _add_worker(Namespace(name='worker-aabbcc', ifaces=2, dry_run=False, yes=False))

    cmds = _cmds(mock_subprocess)
    assert any('workers-init.yml' in c for c in cmds)
    assert any('worker.yml' in c for c in cmds)
    assert any('worker-aabbcc' in c for c in cmds)


# ── cluster add controller ────────────────────────────────────────────────────


def test_add_controller_missing_file_exits(project_dir):
    from ops_cluster.kubewi.commands import _add_controller
    import pytest
    with pytest.raises(SystemExit):
        _add_controller(Namespace(name='controller-x', yes=True))


def test_add_controller_calls_init_and_controller_yml(mock_subprocess, project_dir, monkeypatch):
    from ops_cluster.kubewi.commands import _add_controller

    (project_dir / 'hosts' / 'controller-aabbcc.yml').write_text(
        'kubewi:\n  host:\n'
        '    name: controller-aabbcc\n'
        '    ansible_host: 10.0.100.5\n'
        '    ansible_user: iobewi\n'
        '    eng_k0s:\n'
        '      role: controller\n'
    )
    monkeypatch.setattr('getpass.getpass', lambda _: 'pass')
    _add_controller(Namespace(name='controller-aabbcc', yes=True))

    cmds = _cmds(mock_subprocess)
    assert any('init.yml' in c for c in cmds)
    assert any('controller.yml' in c for c in cmds)
    assert any('controller-aabbcc' in c for c in cmds)
