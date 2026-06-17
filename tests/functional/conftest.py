"""
Fixtures partagées pour les tests fonctionnels.

- mock_subprocess : intercepte subprocess.run
- project_dir     : crée un projet kubewi temporaire et l'active via KUBEWI_PROJECT
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_subprocess(monkeypatch: pytest.MonkeyPatch) -> list[list[str]]:
    """
    Remplace subprocess.run par un stub qui :
    - capture chaque commande dans la liste retournée
    - retourne returncode=0 (pas d'erreur)

    Usage :
        def test_foo(mock_subprocess):
            _deploy()
            assert any('kubectl' in c for cmd in mock_subprocess for c in cmd)
    """
    calls: list[list[str]] = []

    def _fake_run(cmd, **kwargs):
        calls.append([str(a) for a in cmd])
        result = MagicMock()
        result.returncode = 0
        result.stdout = b""   # requis par les fonctions avec capture_output=True
        result.stderr = b""
        return result

    monkeypatch.setattr("subprocess.run", _fake_run)
    return calls


@pytest.fixture
def project_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Crée un projet kubewi temporaire et l'active via KUBEWI_PROJECT."""
    from kubewi._project import MARKER
    project = tmp_path / 'test-cluster'
    project.mkdir()
    (project / MARKER).write_text('name: test-cluster\n')
    (project / 'group_vars' / 'all').mkdir(parents=True)
    (project / 'hosts').mkdir()
    (project / 'cluster.yml').write_text('kubewi:\n  cluster:\n    name: test-cluster\n')
    (project / 'hosts' / 'controller-01.yml').write_text(
        'kubewi:\n  host:\n'
        '    name: controller-01\n'
        '    ansible_host: 10.0.100.1\n'
        '    ansible_user: iobewi\n'
        '    host_id: 1\n'
        '    plg_gateway:\n'
        '      init_host: "192.168.100.96"\n'
        '      network_external_iface: enp2s0\n'
        '      network_bridge_members: [enp1s0]\n'
        '    eng_k0s:\n'
        '      role: controller\n'
    )
    monkeypatch.setenv('KUBEWI_PROJECT', str(project))
    return project
