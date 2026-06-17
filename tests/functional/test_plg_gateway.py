"""
Tests fonctionnels — plg_gateway
Vérifie que deploy et wifi-deploy lancent les bons playbooks Ansible.
"""
from __future__ import annotations

from argparse import Namespace


def _cmds(calls: list[list[str]]) -> list[str]:
    return [" ".join(c) for c in calls]


def test_deploy_runs_gateway_playbook(mock_subprocess, project_dir):
    from plg_gateway.kubewi.commands import run_cmd
    run_cmd(Namespace(gateway_cmd="deploy"))
    assert any("gateway.yml" in c for c in _cmds(mock_subprocess))


def test_deploy_uses_ansible_playbook(mock_subprocess, project_dir):
    from plg_gateway.kubewi.commands import run_cmd
    run_cmd(Namespace(gateway_cmd="deploy"))
    assert any("ansible-playbook" in c for c in _cmds(mock_subprocess))


def test_wifi_deploy_runs_wifi_playbook(mock_subprocess, project_dir):
    from plg_gateway.kubewi.commands import run_cmd
    run_cmd(Namespace(gateway_cmd="wifi-deploy"))
    assert any("wifi.yml" in c for c in _cmds(mock_subprocess))


def test_wifi_deploy_uses_ansible_playbook(mock_subprocess, project_dir):
    from plg_gateway.kubewi.commands import run_cmd
    run_cmd(Namespace(gateway_cmd="wifi-deploy"))
    assert any("ansible-playbook" in c for c in _cmds(mock_subprocess))


def test_deploy_and_wifi_deploy_are_independent(mock_subprocess, project_dir):
    """deploy ne doit pas lancer wifi.yml, wifi-deploy ne doit pas lancer gateway.yml."""
    from plg_gateway.kubewi.commands import run_cmd

    run_cmd(Namespace(gateway_cmd="deploy"))
    assert not any("wifi.yml" in c for c in _cmds(mock_subprocess))

    mock_subprocess.clear()

    run_cmd(Namespace(gateway_cmd="wifi-deploy"))
    assert not any("gateway.yml" in c for c in _cmds(mock_subprocess))
