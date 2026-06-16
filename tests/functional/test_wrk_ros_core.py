"""
Tests fonctionnels — wrk_ros_core (commandes manifest uniquement)
Vérifie test-deploy et ns-deploy qui appliquent des manifests kubectl.
Les commandes Docker (build, push, build-arm64) requièrent un daemon Docker
et sont hors scope des tests unitaires.
"""
from __future__ import annotations

from argparse import Namespace


def _cmds(calls: list[list[str]]) -> list[str]:
    return [" ".join(c) for c in calls]


def test_test_deploy_applies_arm64_manifest(mock_subprocess):
    from wrk_ros_core.kubewi.commands import run_cmd
    run_cmd(Namespace(ros_core_cmd="test-deploy"))
    assert any("test-arm64.yaml" in c for c in _cmds(mock_subprocess))


def test_test_deploy_uses_kubectl_apply(mock_subprocess):
    from wrk_ros_core.kubewi.commands import run_cmd
    run_cmd(Namespace(ros_core_cmd="test-deploy"))
    assert any("kubectl apply" in c for c in _cmds(mock_subprocess))


def test_ns_deploy_applies_headlamp_manifest(mock_subprocess):
    from wrk_ros_core.kubewi.commands import run_cmd
    run_cmd(Namespace(ros_core_cmd="ns-deploy"))
    assert any("ros-headlamp-access.yaml" in c for c in _cmds(mock_subprocess))


def test_test_deploy_and_ns_deploy_use_different_manifests(mock_subprocess):
    from wrk_ros_core.kubewi.commands import run_cmd

    run_cmd(Namespace(ros_core_cmd="test-deploy"))
    assert not any("ros-headlamp-access.yaml" in c for c in _cmds(mock_subprocess))

    mock_subprocess.clear()

    run_cmd(Namespace(ros_core_cmd="ns-deploy"))
    assert not any("test-arm64.yaml" in c for c in _cmds(mock_subprocess))
