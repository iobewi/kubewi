"""
Brique transversale Kubernetes — wrapper kubectl + opérations engine pour les modules fonctionnels.
"""
from __future__ import annotations

from kubewi._utils import run


def kubectl(*args: str) -> None:
    run(['kubectl', *args])


def apply(path: str) -> None:
    kubectl('apply', '-f', path)


def scale(namespace: str, deployment: str, replicas: int) -> None:
    kubectl('-n', namespace, 'scale', 'deployment', deployment, f'--replicas={replicas}')


def rollout_wait(namespace: str, deployment: str, timeout: str = '60s') -> None:
    kubectl('-n', namespace, 'rollout', 'status', f'deployment/{deployment}', f'--timeout={timeout}')


def worker_init(limit: str, become_pass: str) -> None:
    from eng_k0s.kubewi import lib as k0s
    k0s.worker_init(limit, become_pass)


def add_worker(limit: str) -> None:
    from eng_k0s.kubewi import lib as k0s
    k0s.add_worker(limit)


def add_controller(limit: str) -> None:
    from eng_k0s.kubewi import lib as k0s
    k0s.add_controller(limit)
