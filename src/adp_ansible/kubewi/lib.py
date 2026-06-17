"""
Brique transversale Ansible — utilitaires pour les modules fonctionnels.
"""
from __future__ import annotations

from pathlib import Path

from kubewi._utils import run

PKG_DIR = Path(__file__).parent.parent


def run_playbook(playbook: Path | str, *extra_args: str, env: dict | None = None) -> None:
    from kubewi._project import resolve
    from kubewi._hostfile import generate_ansible_inventory
    project_dir = resolve()
    inventory   = generate_ansible_inventory(project_dir)
    vault_args  = _vault_args(project_dir)
    run(
        ['ansible-playbook', '-i', str(inventory), *vault_args, str(playbook), *extra_args],
        cwd=str(PKG_DIR),
        env=env,
    )


def _vault_args(project_dir: Path) -> list[str]:
    """Retourne les args vault Ansible selon le contexte (fichier pass, env, ou interactif)."""
    import os
    vault = project_dir / 'group_vars' / 'all' / 'vault.yml'
    try:
        encrypted = vault.read_text(errors='replace').startswith('$ANSIBLE_VAULT;')
    except Exception:
        return []
    if not encrypted:
        return []

    # 1. Fichier de mot de passe Ansible standard
    env_file = os.environ.get('ANSIBLE_VAULT_PASSWORD_FILE', '')
    if env_file and Path(env_file).exists():
        return ['--vault-password-file', env_file]

    # 2. Fichier kubewi par défaut (~/.kubewi/vault-pass)
    kubewi_pass = Path.home() / '.kubewi' / 'vault-pass'
    if kubewi_pass.exists():
        return ['--vault-password-file', str(kubewi_pass)]

    # 3. Fichier local au projet (.vault-pass, gitignorer)
    project_pass = project_dir / '.vault-pass'
    if project_pass.exists():
        return ['--vault-password-file', str(project_pass)]

    # 4. Fallback interactif
    return ['--ask-vault-pass']


def _vault_encrypted(project_dir: Path) -> bool:
    vault = project_dir / 'group_vars' / 'all' / 'vault.yml'
    try:
        return vault.read_text(errors='replace').startswith('$ANSIBLE_VAULT;')
    except Exception:
        return False
