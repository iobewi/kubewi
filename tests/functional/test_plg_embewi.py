"""
Tests fonctionnels — plg_embewi
Vérifie le dispatch et l'ordre des appels kubectl pour deploy/status/logs.
"""
from __future__ import annotations

from argparse import Namespace

import pytest


def _cmds(calls: list[list[str]]) -> list[str]:
    return [" ".join(c) for c in calls]


# ── deploy ────────────────────────────────────────────────────────────────────


def test_deploy_applies_crds(mock_subprocess):
    from plg_embewi.kubewi.commands import _deploy
    _deploy()
    assert any("crds.yaml" in c for c in _cmds(mock_subprocess))


def test_deploy_applies_embewi_core_manifest(mock_subprocess):
    from plg_embewi.kubewi.commands import _deploy
    _deploy()
    assert any("embewi-core.yaml" in c for c in _cmds(mock_subprocess))


def test_deploy_waits_for_rollout(mock_subprocess):
    from plg_embewi.kubewi.commands import _deploy
    _deploy()
    assert any("rollout" in c and "embewi-core" in c for c in _cmds(mock_subprocess))


def test_deploy_order_crds_then_manifest_then_rollout(mock_subprocess):
    """Les CRDs doivent être appliqués avant le Deployment, le rollout en dernier."""
    from plg_embewi.kubewi.commands import _deploy
    _deploy()
    cmds = _cmds(mock_subprocess)
    crds_idx     = next(i for i, c in enumerate(cmds) if "crds.yaml" in c)
    manifest_idx = next(i for i, c in enumerate(cmds) if "embewi-core.yaml" in c)
    rollout_idx  = next(i for i, c in enumerate(cmds) if "rollout" in c)
    assert crds_idx < manifest_idx < rollout_idx


def test_deploy_rollout_timeout_120s(mock_subprocess):
    from plg_embewi.kubewi.commands import _deploy
    _deploy()
    assert any("--timeout=120s" in c for c in _cmds(mock_subprocess))


# ── status ────────────────────────────────────────────────────────────────────


def test_status_queries_mcunodes(mock_subprocess):
    from plg_embewi.kubewi.commands import _status
    _status()
    assert any("mcu" in c for c in _cmds(mock_subprocess))


def test_status_queries_mcudeployments(mock_subprocess):
    from plg_embewi.kubewi.commands import _status
    _status()
    assert any("mcudep" in c for c in _cmds(mock_subprocess))


def test_status_uses_all_namespaces(mock_subprocess):
    from plg_embewi.kubewi.commands import _status
    _status()
    assert any("-A" in c for c in _cmds(mock_subprocess))


def test_status_wide_output(mock_subprocess):
    from plg_embewi.kubewi.commands import _status
    _status()
    assert any("-o wide" in c or "wide" in c for c in _cmds(mock_subprocess))


# ── logs ──────────────────────────────────────────────────────────────────────


def test_logs_default_100_lines(mock_subprocess):
    from plg_embewi.kubewi.commands import _logs
    _logs(100)
    assert any("--tail=100" in c for c in _cmds(mock_subprocess))


def test_logs_custom_tail(mock_subprocess):
    from plg_embewi.kubewi.commands import _logs
    _logs(500)
    assert any("--tail=500" in c for c in _cmds(mock_subprocess))


def test_logs_targets_embewi_namespace(mock_subprocess):
    from plg_embewi.kubewi.commands import _logs
    _logs(50)
    assert any("-n embewi" in c for c in _cmds(mock_subprocess))


def test_logs_selects_embewi_core_pod(mock_subprocess):
    from plg_embewi.kubewi.commands import _logs
    _logs(50)
    assert any("embewi-core" in c for c in _cmds(mock_subprocess))


# ── dispatch run_cmd ──────────────────────────────────────────────────────────


def test_run_cmd_deploy(mock_subprocess):
    from plg_embewi.kubewi.commands import run_cmd
    run_cmd(Namespace(embewi_cmd="deploy"))
    assert len(mock_subprocess) >= 3  # apply crds + apply manifest + rollout


def test_run_cmd_status(mock_subprocess):
    from plg_embewi.kubewi.commands import run_cmd
    run_cmd(Namespace(embewi_cmd="status"))
    assert len(mock_subprocess) == 2  # get mcu + get mcudep


def test_run_cmd_logs(mock_subprocess):
    from plg_embewi.kubewi.commands import run_cmd
    run_cmd(Namespace(embewi_cmd="logs", tail=100))
    assert len(mock_subprocess) == 1
