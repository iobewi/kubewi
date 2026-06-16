"""
Fixture mock_subprocess — intercepte tous les appels subprocess.run
via kubewi._utils pour les tests fonctionnels sans cluster réel.
"""
from __future__ import annotations

import subprocess
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
