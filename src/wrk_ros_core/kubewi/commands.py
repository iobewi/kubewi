from __future__ import annotations

import os
from pathlib import Path

NAME      = 'ros-core'
_PKG_DIR  = Path(__file__).parent.parent


def _ref() -> tuple[str, str]:
    host     = os.environ.get('REGISTRY_HOST', 'registry.kubewi.internal')
    port     = os.environ.get('REGISTRY_PORT', '5000')
    tag      = os.environ.get('IMAGE_TAG', 'latest')
    registry = f'{host}:{port}'
    return f'{registry}/kubewi/ros-core:{tag}', registry


def register(sub) -> None:
    p = sub.add_parser('ros-core', help='Workload ROS 2 Jazzy + Zenoh (image de base)')
    s = p.add_subparsers(dest='ros_core_cmd', metavar='CMD', required=True)
    s.add_parser('build',       help='Build l\'image (x86_64)')
    s.add_parser('push',        help='Push vers le registry')
    s.add_parser('clean',       help='Supprime l\'image locale')
    s.add_parser('lint',        help='Lint du Dockerfile (hadolint)')
    s.add_parser('build-arm64', help='Build et push pour linux/arm64 (VPN requis)')
    s.add_parser('test-deploy', help='Déploie le Job de test ARM64 sur le cluster')
    s.add_parser('ns-deploy',   help='Applique le namespace ros et les RBAC Headlamp')


def run_cmd(args) -> None:
    from wrk_buildkit.kubewi import lib as buildkit
    ref, registry = _ref()
    cmd = args.ros_core_cmd
    if cmd == 'build':         buildkit.build(_PKG_DIR, ref, registry)
    elif cmd == 'push':        buildkit.push(ref)
    elif cmd == 'clean':       buildkit.clean(ref)
    elif cmd == 'lint':        buildkit.lint(_PKG_DIR)
    elif cmd == 'build-arm64': buildkit.build_arm64(_PKG_DIR, ref, registry)
    elif cmd in ('test-deploy', 'ns-deploy'):
        from adp_kube.kubewi import lib as kube
        manifest = 'test-arm64.yaml' if cmd == 'test-deploy' else 'ros-headlamp-access.yaml'
        kube.apply(str(_PKG_DIR / 'manifests' / manifest))
