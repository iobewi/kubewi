"""
Tests pour kubewi._project — résolution de projet et initialisation.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from kubewi._project import ENV_VAR, MARKER


# ── resolve ───────────────────────────────────────────────────────────────────


def test_resolve_via_env_var(tmp_path, monkeypatch):
    project = tmp_path / 'mon-cluster'
    project.mkdir()
    (project / MARKER).write_text('name: mon-cluster\n')
    monkeypatch.setenv(ENV_VAR, str(project))
    from kubewi._project import resolve
    assert resolve() == project.resolve()


def test_resolve_via_cwd(tmp_path, monkeypatch):
    project = tmp_path / 'mon-cluster'
    project.mkdir()
    (project / MARKER).write_text('name: mon-cluster\n')
    monkeypatch.chdir(project)
    monkeypatch.delenv(ENV_VAR, raising=False)
    from kubewi._project import resolve
    assert resolve() == project.resolve()


def test_env_var_takes_precedence_over_cwd(tmp_path, monkeypatch):
    env_project = tmp_path / 'env-cluster'
    env_project.mkdir()
    (env_project / MARKER).write_text('name: env-cluster\n')

    cwd_project = tmp_path / 'cwd-cluster'
    cwd_project.mkdir()
    (cwd_project / MARKER).write_text('name: cwd-cluster\n')

    monkeypatch.setenv(ENV_VAR, str(env_project))
    monkeypatch.chdir(cwd_project)

    from kubewi._project import resolve
    assert resolve() == env_project.resolve()


def test_resolve_no_project_exits(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv(ENV_VAR, raising=False)
    from kubewi._project import resolve
    with pytest.raises(SystemExit):
        resolve()


def test_resolve_env_var_nonexistent_dir(tmp_path, monkeypatch):
    monkeypatch.setenv(ENV_VAR, str(tmp_path / 'nonexistent'))
    from kubewi._project import resolve
    with pytest.raises(SystemExit):
        resolve()


# ── init ──────────────────────────────────────────────────────────────────────


def test_init_creates_directory(tmp_path):
    from kubewi._project import init
    project = init('test-cluster', tmp_path)
    assert project.is_dir()
    assert project.name == 'test-cluster'


def test_init_creates_marker(tmp_path):
    from kubewi._project import init
    project = init('test-cluster', tmp_path)
    assert (project / MARKER).exists()


def test_init_copies_hosts_yml(tmp_path):
    from kubewi._project import init
    project = init('test-cluster', tmp_path)
    assert (project / 'hosts.yml').exists()


def test_init_copies_vault_yml(tmp_path):
    from kubewi._project import init
    project = init('test-cluster', tmp_path)
    assert (project / 'group_vars' / 'all' / 'vault.yml').exists()


def test_init_fails_if_dir_exists(tmp_path):
    (tmp_path / 'test-cluster').mkdir()
    from kubewi._project import init
    with pytest.raises(SystemExit):
        init('test-cluster', tmp_path)
