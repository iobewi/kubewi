"""
Tests fonctionnels — eng_k0s
Vérifie kubeconfig, add controller et add worker.
"""
from __future__ import annotations

from argparse import Namespace
from unittest.mock import patch


def _cmds(calls: list[list[str]]) -> list[str]:
    return [" ".join(c) for c in calls]


# ── kubeconfig ────────────────────────────────────────────────────────────────


def test_kubeconfig_runs_python_script(mock_subprocess):
    from eng_k0s.kubewi.commands import run_cmd
    run_cmd(Namespace(k0s_cmd="kubeconfig"))
    assert any("kubeconfig.py" in c for c in _cmds(mock_subprocess))


def test_kubeconfig_uses_python3(mock_subprocess):
    from eng_k0s.kubewi.commands import run_cmd
    run_cmd(Namespace(k0s_cmd="kubeconfig"))
    assert any(c.startswith("python3") for c in _cmds(mock_subprocess))


# ── add controller ────────────────────────────────────────────────────────────


def test_add_controller_calls_ansible_playbook(mock_subprocess):
    from eng_k0s.kubewi.commands import run_cmd
    run_cmd(Namespace(k0s_cmd="add", k0s_add_target="controller", limit="controllers"))
    assert any("ansible-playbook" in c for c in _cmds(mock_subprocess))


def test_add_controller_default_limit(mock_subprocess):
    from eng_k0s.kubewi.commands import run_cmd
    run_cmd(Namespace(k0s_cmd="add", k0s_add_target="controller", limit="controllers"))
    cmds = _cmds(mock_subprocess)
    assert any("controllers" in c for c in cmds)


def test_add_controller_custom_limit(mock_subprocess):
    from eng_k0s.kubewi.commands import run_cmd
    run_cmd(Namespace(k0s_cmd="add", k0s_add_target="controller", limit="ctrl-02"))
    assert any("ctrl-02" in c for c in _cmds(mock_subprocess))


# ── add worker ────────────────────────────────────────────────────────────────


def test_add_worker_calls_worker_init_and_add(mock_subprocess):
    """worker_init (bootstrap réseau) puis add_worker (enrollment k0s)."""
    from eng_k0s.kubewi.commands import run_cmd
    with patch("getpass.getpass", return_value="testpass"):
        run_cmd(Namespace(k0s_cmd="add", k0s_add_target="worker", name="worker-01"))
    # worker_init + add_worker → au moins 2 playbooks ansible
    assert len(mock_subprocess) >= 2


def test_add_worker_passes_worker_name(mock_subprocess):
    from eng_k0s.kubewi.commands import run_cmd
    with patch("getpass.getpass", return_value="testpass"):
        run_cmd(Namespace(k0s_cmd="add", k0s_add_target="worker", name="worker-edge-01"))
    assert any("worker-edge-01" in c for c in _cmds(mock_subprocess))
