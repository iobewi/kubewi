"""
Tests fonctionnels — adp_kube.kubewi.lib
Vérifie que chaque fonction construit et envoie la bonne commande kubectl.
"""
from __future__ import annotations

import pytest


def _cmds(calls: list[list[str]]) -> list[str]:
    return [" ".join(c) for c in calls]


# ── kubectl passthrough ───────────────────────────────────────────────────────


def test_kubectl_passes_args(mock_subprocess):
    from adp_kube.kubewi.lib import kubectl
    kubectl("get", "nodes")
    assert ["kubectl", "get", "nodes"] in mock_subprocess


def test_kubectl_multiple_args(mock_subprocess):
    from adp_kube.kubewi.lib import kubectl
    kubectl("-n", "kube-system", "get", "pods")
    assert ["kubectl", "-n", "kube-system", "get", "pods"] in mock_subprocess


# ── apply ─────────────────────────────────────────────────────────────────────


def test_apply_uses_kubectl_apply_f(mock_subprocess):
    from adp_kube.kubewi.lib import apply
    apply("/tmp/manifest.yaml")
    cmds = _cmds(mock_subprocess)
    assert any("kubectl apply -f /tmp/manifest.yaml" in c for c in cmds)


# ── scale ─────────────────────────────────────────────────────────────────────


def test_scale_targets_correct_deployment(mock_subprocess):
    from adp_kube.kubewi.lib import scale
    scale("myns", "myapp", 2)
    cmds = _cmds(mock_subprocess)
    assert any(
        "kubectl" in c and "scale" in c and "myapp" in c and "--replicas=2" in c
        for c in cmds
    )


def test_scale_uses_namespace(mock_subprocess):
    from adp_kube.kubewi.lib import scale
    scale("production", "api", 3)
    cmds = _cmds(mock_subprocess)
    assert any("-n production" in c for c in cmds)


def test_scale_zero_replicas(mock_subprocess):
    from adp_kube.kubewi.lib import scale
    scale("myns", "myapp", 0)
    cmds = _cmds(mock_subprocess)
    assert any("--replicas=0" in c for c in cmds)


# ── rollout_wait ──────────────────────────────────────────────────────────────


def test_rollout_wait_calls_rollout_status(mock_subprocess):
    from adp_kube.kubewi.lib import rollout_wait
    rollout_wait("myns", "myapp")
    cmds = _cmds(mock_subprocess)
    assert any("rollout" in c and "status" in c and "myapp" in c for c in cmds)


def test_rollout_wait_default_timeout(mock_subprocess):
    from adp_kube.kubewi.lib import rollout_wait
    rollout_wait("myns", "myapp")
    cmds = _cmds(mock_subprocess)
    assert any("--timeout=60s" in c for c in cmds)


def test_rollout_wait_custom_timeout(mock_subprocess):
    from adp_kube.kubewi.lib import rollout_wait
    rollout_wait("myns", "myapp", timeout="120s")
    cmds = _cmds(mock_subprocess)
    assert any("--timeout=120s" in c for c in cmds)
