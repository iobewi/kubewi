# KubeWI

**Plateforme d'infrastructure robotique distribuée — orchestration Kubernetes, séparation hard RT explicite, middleware Zenoh et observabilité native pour systèmes edge hétérogènes.**

[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://iobewi.github.io/kubewi/)

---

## Vue d'ensemble

KubeWI formalise une infrastructure cohérente pour des systèmes robotiques distribués mêlant plusieurs machines, plusieurs niveaux de criticité et plusieurs types de calcul.

| Couche | Rôle |
|---|---|
| **Core Infrastructure** | orchestration k0s, registry OCI locale, Zenoh router, VPN |
| **Worker Nodes** | exécution des workloads ROS2 orchestrés (perception, navigation, contrôle) |
| **Infrastructure d'exploitation** | observabilité, visualisation, stockage froid |
| **Hors cluster** | MCU, firmware, micro-ROS, Zenoh-Pico — hard real-time autonome |

---

## Structure du dépôt

| Répertoire | Rôle |
|---|---|
| `bootstrap/` | CLI `r2bewi` — provisioning du cluster (init, deploy, enroll, validate, status) |
| `docker/` | Images Docker des services de la plateforme |
| `containers/` | Manifests Kubernetes |
| `docs/` | Documentation Sphinx — architecture, composants, réseau, temps réel, résilience |

---

## Composants principaux

| Composant | Rôle |
|---|---|
| **k0s** | orchestration Kubernetes légère, edge-first |
| **Cilium** | dataplane réseau eBPF — policies, inspection native |
| **Multus** | interfaces réseau multiples par workload |
| **Zenoh** | communication distribuée — routage, découplage DDS multicast |
| **Vector + Loki + Grafana** | pipeline d'observabilité distribué |
| **Hubble** | visibilité native des flux réseau |
| **MinIO** | stockage objet S3 — artefacts, rosbags, archivage |
| **Ansible** | provisioning déclaratif et reproductible |

---

## Développement

### Prérequis

- Python 3.10+ et `make`
- Docker avec BuildKit

### Commandes

```bash
make bootstrap-test           # lint + tests + couverture
make -C bootstrap test-dev    # idem + pip install auto
make -C bootstrap build       # → bootstrap/dist/r2bewi

make docs                     # build documentation Sphinx locale
```

### Documentation locale

```bash
pip install -r requirements-docs.txt
sphinx-build -b html docs/ docs/_build/html
python3 -m http.server 8000 --directory docs/_build/html
```

---

## Documentation

La documentation complète est disponible sur **[iobewi.github.io/kubewi](https://iobewi.github.io/kubewi/)**.

Elle couvre :

- [Architecture](https://iobewi.github.io/kubewi/architecture/overview.html) — vue d'ensemble et invariants
- [Composants](https://iobewi.github.io/kubewi/architecture/components.html) — rôles et responsabilités
- [Réseau](https://iobewi.github.io/kubewi/architecture/networking.html) — domaines et segmentation
- [Temps réel](https://iobewi.github.io/kubewi/architecture/realtime.html) — frontière hard RT / soft RT
- [Stockage](https://iobewi.github.io/kubewi/architecture/storage.html) — catégories et résilience
- [Observabilité](https://iobewi.github.io/kubewi/architecture/observability.html) — pipeline distribué
- [Résilience](https://iobewi.github.io/kubewi/architecture/resilience.html) — modes dégradés
