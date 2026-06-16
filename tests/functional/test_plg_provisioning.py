"""
Tests fonctionnels — plg_provisioning
Vérifie deploy, on et off sur le Deployment dnsmasq-provisioning.
"""
from __future__ import annotations

from argparse import Namespace


def _cmds(calls: list[list[str]]) -> list[str]:
    return [" ".join(c) for c in calls]


# ── deploy ────────────────────────────────────────────────────────────────────


def test_deploy_applies_dnsmasq_manifest(mock_subprocess):
    from plg_provisioning.kubewi.commands import _deploy
    _deploy()
    assert any("dnsmasq.yaml" in c for c in _cmds(mock_subprocess))


def test_deploy_uses_kubectl_apply(mock_subprocess):
    from plg_provisioning.kubewi.commands import _deploy
    _deploy()
    assert any("kubectl apply" in c for c in _cmds(mock_subprocess))


# ── on ────────────────────────────────────────────────────────────────────────


def test_on_scales_to_1(mock_subprocess):
    from plg_provisioning.kubewi.commands import _scale
    _scale(1)
    assert any("--replicas=1" in c and "dnsmasq-provisioning" in c
               for c in _cmds(mock_subprocess))


def test_on_waits_for_rollout(mock_subprocess):
    from plg_provisioning.kubewi.commands import _scale
    _scale(1)
    assert any("rollout" in c and "dnsmasq-provisioning" in c
               for c in _cmds(mock_subprocess))


# ── off ───────────────────────────────────────────────────────────────────────


def test_off_scales_to_0(mock_subprocess):
    from plg_provisioning.kubewi.commands import _scale
    _scale(0)
    assert any("--replicas=0" in c and "dnsmasq-provisioning" in c
               for c in _cmds(mock_subprocess))


def test_off_does_not_wait_rollout(mock_subprocess):
    from plg_provisioning.kubewi.commands import _scale
    _scale(0)
    assert not any("rollout" in c for c in _cmds(mock_subprocess))


# ── dispatch run_cmd ──────────────────────────────────────────────────────────


def test_run_cmd_deploy(mock_subprocess):
    from plg_provisioning.kubewi.commands import run_cmd
    run_cmd(Namespace(provisioning_cmd="deploy"))
    assert any("dnsmasq.yaml" in c for c in _cmds(mock_subprocess))


def test_run_cmd_on(mock_subprocess):
    from plg_provisioning.kubewi.commands import run_cmd
    run_cmd(Namespace(provisioning_cmd="on"))
    assert any("--replicas=1" in c for c in _cmds(mock_subprocess))


def test_run_cmd_off(mock_subprocess):
    from plg_provisioning.kubewi.commands import run_cmd
    run_cmd(Namespace(provisioning_cmd="off"))
    assert any("--replicas=0" in c for c in _cmds(mock_subprocess))
