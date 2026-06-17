from __future__ import annotations

from pathlib import Path

SSH_KEY = Path.home() / '.ssh' / 'kubewi_ansible'


def ensure_key() -> None:
    """Génère la clé SSH kubewi_ansible si absente."""
    from kubewi._utils import run
    if SSH_KEY.exists():
        print(f"  - Clé SSH existante : {SSH_KEY}")
    else:
        run(['ssh-keygen', '-t', 'ed25519', '-N', '', '-f', str(SSH_KEY), '-C', 'kubewi-ansible-sdk'])
        print(f"  ✓ Clé SSH générée : {SSH_KEY}")
