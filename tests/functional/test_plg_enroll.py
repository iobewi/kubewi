"""
Tests fonctionnels — plg_enroll
Vérifie les fonctions testables sans cluster : provisioning on/off,
et les chemins inventory-only qui n'appellent pas Ansible.
"""
from __future__ import annotations

from argparse import Namespace


def _cmds(calls: list[list[str]]) -> list[str]:
    return [" ".join(c) for c in calls]


# ── Provisioning DHCP ─────────────────────────────────────────────────────────


def test_provisioning_on_scales_dnsmasq_to_1(mock_subprocess):
    from plg_enroll.kubewi.commands import _provisioning_on
    _provisioning_on()
    cmds = _cmds(mock_subprocess)
    assert any(
        "scale" in c and "dnsmasq-provisioning" in c and "--replicas=1" in c
        for c in cmds
    )


def test_provisioning_on_waits_for_rollout(mock_subprocess):
    from plg_enroll.kubewi.commands import _provisioning_on
    _provisioning_on()
    cmds = _cmds(mock_subprocess)
    assert any("rollout" in c and "dnsmasq-provisioning" in c for c in cmds)


def test_provisioning_off_scales_dnsmasq_to_0(mock_subprocess):
    from plg_enroll.kubewi.commands import _provisioning_off
    _provisioning_off()
    cmds = _cmds(mock_subprocess)
    assert any(
        "scale" in c and "dnsmasq-provisioning" in c and "--replicas=0" in c
        for c in cmds
    )


# ── Enrollment controller — inventory-only ────────────────────────────────────


def test_enroll_controller_inventory_only_skips_ansible(mock_subprocess, capsys):
    """--inventory-only ne doit déclencher aucun ansible-playbook."""
    from plg_enroll.kubewi.commands import run_cmd
    run_cmd(Namespace(enroll_role="controller", name="ctrl-02",
                      inventory_only=True, yes=False))
    assert not any("ansible-playbook" in c for c in _cmds(mock_subprocess))


def test_enroll_controller_inventory_only_prints_message(mock_subprocess, capsys):
    from plg_enroll.kubewi.commands import run_cmd
    run_cmd(Namespace(enroll_role="controller", name="ctrl-02",
                      inventory_only=True, yes=False))
    out = capsys.readouterr().out
    assert "inventory-only" in out.lower() or "hosts.yml" in out.lower()


# ── Enrollment worker — dry-run ───────────────────────────────────────────────


def test_enroll_worker_dry_run_skips_ansible(mock_subprocess):
    """--dry-run ne doit pas appeler ansible-playbook."""
    from plg_enroll.kubewi.commands import _enroll_worker

    class _Args:
        ifaces = 2
        yes = True
        single = False
        dry_run = True
        inventory_only = False

    # Patch dans le module commands (où detect_phase est importé comme nom local)
    import unittest.mock as mock
    with mock.patch("plg_enroll.kubewi.commands.detect_phase", return_value=[]):
        _enroll_worker(_Args())

    assert not any("ansible-playbook" in c for c in _cmds(mock_subprocess))
