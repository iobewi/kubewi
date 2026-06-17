"""
Tests fonctionnels — wrk_provisioning
Vérifie que le manifest dnsmasq.yaml est présent et valide.
"""
from __future__ import annotations

from pathlib import Path

import yaml

_MANIFEST = Path(__file__).parent.parent.parent / "src" / "wrk_provisioning" / "manifests" / "dnsmasq.yaml"


def test_manifest_exists():
    assert _MANIFEST.exists(), f"manifest absent : {_MANIFEST}"


def test_manifest_valid_yaml():
    docs = list(yaml.safe_load_all(_MANIFEST.read_text()))
    assert len(docs) > 0


def test_manifest_has_namespace():
    docs = list(yaml.safe_load_all(_MANIFEST.read_text()))
    kinds = [d["kind"] for d in docs if d]
    assert "Namespace" in kinds


def test_manifest_has_deployment():
    docs = list(yaml.safe_load_all(_MANIFEST.read_text()))
    kinds = [d["kind"] for d in docs if d]
    assert "Deployment" in kinds


def test_deployment_default_replicas_zero():
    docs = list(yaml.safe_load_all(_MANIFEST.read_text()))
    deploy = next(d for d in docs if d and d.get("kind") == "Deployment")
    assert deploy["spec"]["replicas"] == 0


def test_deployment_node_selector_matches_k0s_label():
    docs = list(yaml.safe_load_all(_MANIFEST.read_text()))
    deploy = next(d for d in docs if d and d.get("kind") == "Deployment")
    selector = deploy["spec"]["template"]["spec"].get("nodeSelector", {})
    assert selector.get("node-role.kubernetes.io/control-plane") == "true"


def test_network_policy_allows_dhcp_and_ssh():
    """Port 22 intentionnel : le pod est le commutateur du réseau de provisioning.
    Pod actif = 192.168.0.x joignable (DHCP + SSH bootstrap).
    Pod inactif = réseau coupé (Cilium deny par défaut).
    """
    docs = list(yaml.safe_load_all(_MANIFEST.read_text()))
    policy = next(d for d in docs if d and d.get("kind") == "CiliumNetworkPolicy")
    ports = policy["spec"]["ingress"][0]["toPorts"][0]["ports"]
    port_numbers = {p["port"] for p in ports}
    assert "67" in port_numbers
    assert "22" in port_numbers
