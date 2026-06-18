from __future__ import annotations

from pathlib import Path


def _create_project(args) -> None:
    from kubewi._project import init as project_init
    parent      = Path(getattr(args, 'dir', '.'))
    project_dir = project_init(args.name, parent)
    print(f"\n  ✓ Projet '{args.name}' créé dans {project_dir.resolve()}")
    print(f"  → cd {project_dir.resolve()}")
    print(f"  → Éditer hosts/controller-01.yml  (init_host, réseau, clés VPN)")
    print(f"  → kubewi vpn generate-keys")
    print(f"  → kubewi cluster apply\n")
