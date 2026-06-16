"""
Tests de validation des manifests Kubernetes :
- syntaxe YAML valide
- champs Kubernetes obligatoires présents (apiVersion, kind, metadata, metadata.name)
"""
from __future__ import annotations

from pathlib import Path

import pytest
from ruamel.yaml import YAML

_yaml = YAML()

K8S_REQUIRED_KEYS = {"apiVersion", "kind", "metadata"}


def _all_manifests() -> list[Path]:
    src = Path(__file__).parent.parent / "src"
    return sorted(src.glob("*/manifests/*.yaml"))


def _manifest_id(p: Path) -> str:
    return f"{p.parent.parent.name}/{p.name}"


MANIFESTS = _all_manifests()


# ── Syntaxe YAML ──────────────────────────────────────────────────────────────


@pytest.mark.parametrize("manifest", MANIFESTS, ids=_manifest_id)
def test_manifest_is_valid_yaml(manifest: Path) -> None:
    try:
        with open(manifest) as f:
            docs = list(_yaml.load_all(f))
    except Exception as e:
        pytest.fail(f"{manifest} : YAML invalide — {e}")
    assert any(d is not None for d in docs), f"{manifest} : fichier YAML vide"


# ── Champs Kubernetes obligatoires ────────────────────────────────────────────


@pytest.mark.parametrize("manifest", MANIFESTS, ids=_manifest_id)
def test_manifest_k8s_required_fields(manifest: Path) -> None:
    with open(manifest) as f:
        docs = list(_yaml.load_all(f))

    for i, doc in enumerate(docs):
        if doc is None:
            continue
        doc_id = f"{_manifest_id(manifest)} [doc {i}]"

        missing = K8S_REQUIRED_KEYS - set(doc.keys())
        assert not missing, f"{doc_id} : champs Kubernetes manquants {missing}"

        assert "name" in (doc.get("metadata") or {}), \
            f"{doc_id} : metadata.name manquant"


# ── Cohérence apiVersion/kind ─────────────────────────────────────────────────


@pytest.mark.parametrize("manifest", MANIFESTS, ids=_manifest_id)
def test_manifest_api_version_non_empty(manifest: Path) -> None:
    with open(manifest) as f:
        docs = list(_yaml.load_all(f))

    for i, doc in enumerate(docs):
        if doc is None:
            continue
        assert doc.get("apiVersion"), \
            f"{_manifest_id(manifest)} [doc {i}] : apiVersion vide ou absent"
        assert doc.get("kind"), \
            f"{_manifest_id(manifest)} [doc {i}] : kind vide ou absent"
