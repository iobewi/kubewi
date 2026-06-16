from __future__ import annotations

import os
import subprocess
from pathlib import Path

from kubewi._utils import run

_PKG_DIR        = Path(__file__).parent.parent
_BUILDKITD_TOML = _PKG_DIR / 'buildkitd.toml'
_HADOLINT_CFG   = _PKG_DIR / 'hadolint.yaml'


def builder() -> str:
    return os.environ.get('BUILDX_BUILDER', 'kubewi-arm64')


def build(pkg_path: Path, image_ref: str, registry: str) -> None:
    print(f'  [build] {image_ref}')
    run(['docker', 'build',
         '--build-arg', f'REGISTRY={registry}',
         '-t', image_ref,
         str(pkg_path)])


def push(image_ref: str) -> None:
    print(f'  [push] {image_ref}')
    run(['docker', 'push', image_ref])


def clean(image_ref: str) -> None:
    run(['docker', 'rmi', image_ref], check=False)


def lint(pkg_path: Path) -> None:
    dockerfile = pkg_path / 'Dockerfile'
    if not dockerfile.exists():
        return
    cmd = ['hadolint']
    if _HADOLINT_CFG.exists():
        cmd += ['--config', str(_HADOLINT_CFG)]
    cmd.append(str(dockerfile))
    run(cmd)


def setup() -> None:
    name = builder()
    r = subprocess.run(['docker', 'buildx', 'inspect', name], capture_output=True)
    if r.returncode != 0:
        run(['docker', 'buildx', 'create',
             '--name', name,
             '--driver', 'docker-container',
             '--driver-opt', 'network=host',
             '--config', str(_BUILDKITD_TOML),
             '--use'])
        run(['docker', 'buildx', 'inspect', '--bootstrap', name])
    print(f'  [buildx] builder {name} prêt')


def build_arm64(pkg_path: Path, image_ref: str, registry: str) -> None:
    setup()
    _inject_registry(registry.split(':')[0])
    print(f'  [build-arm64] {image_ref}')
    run(['docker', 'buildx', 'build',
         '--builder', builder(),
         '--platform', 'linux/arm64',
         '--provenance=false',
         '--build-arg', f'REGISTRY={registry}',
         '--output', f'type=image,name={image_ref},push=true,compression=gzip,oci-mediatypes=false',
         str(pkg_path)])


def _inject_registry(registry_host: str) -> None:
    r = subprocess.run(['getent', 'hosts', registry_host], capture_output=True, text=True)
    if not r.stdout.strip():
        print(f'  ✗ {registry_host} non résolu — VPN actif ?')
        raise SystemExit(1)
    ip = r.stdout.split()[0]

    ctrs = subprocess.run(
        ['docker', 'ps', '--filter', f'name={builder()}', '--format', '{{.Names}}'],
        capture_output=True, text=True,
    ).stdout.strip().splitlines()
    if not ctrs:
        print(f'  ✗ container buildkitd {builder()} introuvable')
        raise SystemExit(1)

    subprocess.run(
        ['docker', 'exec', ctrs[0], 'sh', '-c',
         f"grep -v '{registry_host}' /etc/hosts > /tmp/hosts.new"
         f" && cat /tmp/hosts.new > /etc/hosts"
         f" && echo '{ip} {registry_host}' >> /etc/hosts"],
        check=True,
    )
    print(f'  [buildx] {registry_host} → {ip}')
