from __future__ import annotations

from pathlib import Path


def _wg_conf() -> Path:
    from kubewi._project import resolve
    return resolve() / 'wg0-sdk.conf'


def up() -> None:
    import subprocess
    from kubewi._utils import run
    conf = _wg_conf()
    if not conf.exists():
        import sys
        print(f"  ✗ {conf} absent — lancer kubewi vpn write-conf d'abord")
        sys.exit(1)
    iface = conf.stem
    if subprocess.run(['ip', 'link', 'show', iface], capture_output=True).returncode == 0:
        print(f"  - Tunnel {iface} déjà actif")
        return
    run(['wg-quick', 'up', str(conf)])


def down() -> None:
    from kubewi._utils import run
    run(['wg-quick', 'down', str(_wg_conf())])
