Structure des paquets
=====================

Un paquet KubeWI est l'unité de base du projet. Il regroupe tout ce qui
concerne une brique fonctionnelle : descripteur, commandes CLI, ressources
Ansible, manifests Kubernetes, et toute logique métier propre.

Chaque paquet est un répertoire autonome sous ``src/``.

----

Convention de nommage
---------------------

Chaque répertoire de paquet est préfixé par un diminutif de 3 lettres
reflétant son **type sémantique**, suivi d'un underscore et du nom fonctionnel :

.. code-block:: text

    <3-lettres>_<nom>

    adp_   →   adapter  (outil technologique générique)
    eng_   →   engine   (implémentation concrète d'un adapter)
    plg_   →   plugin   (fonctionnalité métier)
    ops_   →   ops      (outillage opérationnel)
    wrk_   →   workload (application déployée sur le cluster)

Exemples : ``eng_k0s``, ``plg_enroll``, ``wrk_ros_core``.

Le **nom CLI** (dans ``commands.py``) reste court et sans préfixe :
``kubewi k0s add controller``, ``kubewi enroll worker``, etc.

----

Inventaire des paquets
-----------------------

.. list-table::
   :header-rows: 1
   :widths: 28 12 60

   * - Paquet
     - Type
     - Rôle
   * - ``adp_ansible``
     - adapter
     - Adaptateur Ansible — inventaire, vault, playbooks
   * - ``adp_kube``
     - adapter
     - Adaptateur Kubernetes — interface générique engine-agnostique
   * - ``eng_k0s``
     - engine
     - Distribution k0s — install, controller, worker, kubeconfig
   * - ``eng_wireguard``
     - engine
     - Engine WireGuard — install et configuration VPN sur les nœuds
   * - ``eng_debian``
     - engine
     - Provisioning système Debian
   * - ``eng_rpios``
     - engine
     - Provisioning système Raspberry Pi OS
   * - ``eng_ubuntu``
     - engine
     - Provisioning système Ubuntu
   * - ``plg_enroll``
     - plugin
     - Enrôlement des nœuds — détection DHCP, init SSH, join cluster
   * - ``plg_provisioning``
     - plugin
     - Service DHCP de découverte — pod dnsmasq sur le cluster
   * - ``plg_gateway``
     - plugin
     - Brique gateway — NAT, VLANs, routage du nœud d'entrée
   * - ``plg_vpn``
     - plugin
     - Tunnel VPN SDK ↔ cluster — lifecycle wg-quick, génération clés
   * - ``ops_ssh``
     - ops
     - Accès SSH — génération et distribution de la clé, ~/.ssh/config
   * - ``ops_cluster``
     - ops
     - Cycle de vie du cluster — init, enrollment déclaratif, playbooks
   * - ``wrk_buildkit``
     - workload
     - Pod Docker buildx — build et push d'images multi-arch
   * - ``wrk_ros_core``
     - workload
     - Image ROS 2 Jazzy + Zenoh (base) — namespace, RBAC, test ARM64
   * - ``wrk_ros_motion``
     - workload
     - Image ROS 2 control — nœuds de contrôle moteur (FROM ros-core)
   * - ``wrk_ros_perception``
     - workload
     - Image perception GPU — nœud ARM64/Jetson NVIDIA L4T

----

Hiérarchie sémantique
----------------------

.. code-block:: text

    ┌─────────────────────────────────────────────────────────────────┐
    │  KUBEWI  (le framework, le CLI)                                 │
    └──────────────┬──────────────────────────────────────────────────┘
                   │
           ┌───────▼────────┐
           │   adp_         │  adaptateur vers une technologie
           │  adp_ansible   │  interface stable, moteur interchangeable
           │  adp_kube      │
           └───────┬────────┘
                   │
           ┌───────▼────────┐
           │   eng_         │  implémentation concrète d'un adapter
           │  eng_k0s       │  k0s → adp_kube
           │  eng_wireguard │  wireguard → adp_ansible
           │  eng_debian    │  debian / rpios / ubuntu → adp_ansible
           │  eng_rpios     │
           │  eng_ubuntu    │
           └───────┬────────┘
                   │
           ┌───────▼────────┐
           │   plg_         │  fonctionnalité métier kubewi
           │  plg_enroll    │  dépend de adapters et d'engines
           │  plg_provisioning│
           │  plg_gateway   │
           │  plg_vpn       │
           └───────┬────────┘
                   │
           ┌───────▼────────┐
           │   ops_         │  outillage opérationnel
           │  ops_ssh       │
           │  ops_cluster   │
           └───────┬────────┘
                   │
           ┌───────▼────────┐
           │   wrk_         │  applications déployées SUR le cluster
           │  wrk_buildkit  │  pod de build multi-arch
           │  wrk_ros_core  │  image ROS de base + namespace
           │  wrk_ros_motion│
           │  wrk_ros_perception│
           └────────────────┘

**Règle de dépendance** : un paquet ne peut dépendre que de paquets de niveau
égal ou inférieur (``eng_`` → ``adp_``, ``plg_`` → ``eng_`` ou ``adp_``, etc.).

----

Arborescence standard
---------------------

.. code-block:: text

    <type>_<nom>/
    ├── kubewi.yaml               # OBLIGATOIRE — descripteur du paquet
    ├── kubewi/                   # OBLIGATOIRE — intégration CLI kubewi
    │   ├── __init__.py
    │   ├── commands.py           # register() + run_cmd()
    │   └── lib.py                # logique exposée aux autres paquets (optionnel)
    │
    ├── playbooks/                # couche ansible — playbooks/*.yml
    ├── roles/                    # couche ansible — roles/<nom>/
    │
    ├── manifests/                # couche kube   — YAML purs (jamais de Jinja2)
    │
    ├── Dockerfile                # workload uniquement — image à builder
    │
    └── scripts/                  # logique procédurale propre au paquet

----

Fichier kubewi.yaml
-------------------

.. code-block:: yaml

    name: <type>_<nom>                     # requis — = nom du répertoire
    type: adapter|engine|plugin|ops|workload  # requis
    description: <string>                  # requis
    image: <string>                        # workload uniquement — nom image Docker
    deps:                                  # optionnel
      - <type>_<paquet>
    provides:                              # optionnel
      - <capacité>

----

Types de paquets
----------------

.. list-table::
   :header-rows: 1
   :widths: 10 10 35 45

   * - Préfixe
     - Type
     - Rôle
     - Couches attendues
   * - ``adp_``
     - adapter
     - Adaptateur vers une technologie. Interface stable, moteur interchangeable.
     - ``kubewi/`` + ``lib.py``
   * - ``eng_``
     - engine
     - Implémentation concrète d'un adapter. Porte toutes les opérations
       propres à ce moteur (install, remove, upgrade…).
     - ``kubewi/`` + ``playbooks/`` + ``roles/`` + ``scripts/``
   * - ``plg_``
     - plugin
     - Fonctionnalité métier. Dépend d'adapters et/ou d'engines.
     - ``kubewi/`` + ``manifests/`` si kube
   * - ``ops_``
     - ops
     - Outillage opérationnel — scripts, helpers, configuration.
     - ``kubewi/`` + ce dont il a besoin
   * - ``wrk_``
     - workload
     - Application déployée sur le cluster. Piloté par ``wrk_buildkit``.
     - ``Dockerfile`` + ``manifests/`` + ``kubewi/``

----

Règles d'adhérence des couches
-------------------------------

KubeWI repose sur deux couches d'adhérence orthogonales :

- **Ansible** (``adp_ansible``) — adhérence au physique : configure l'OS,
  installe les binaires, monte le cluster. S'arrête là.
- **Kube** (``adp_kube``) — adhérence aux containers : gère le cycle de vie
  des workloads une fois le cluster opérationnel.

Ces couches ne se mélangent pas :

- ``playbooks/`` et ``roles/`` → couche **ansible** uniquement.
- ``manifests/`` → couche **kube** uniquement.
- Les manifests Kubernetes sont des **YAML purs** — pas de Jinja2.
  Les variables réseau passent par des ``ConfigMap``.
- Un workload Kubernetes n'est jamais déployé par Ansible.

----

Intégration CLI
---------------

Chaque paquet expose ses commandes via ``kubewi <nom> <commande>``.
Le nom CLI est défini par ``NAME`` dans ``commands.py`` (sans préfixe).

.. code-block:: python

    NAME = 'k0s'   # kubewi k0s ...  (répertoire : eng_k0s/)

    def register(sub) -> None:
        """Enregistre les sous-commandes dans le parser argparse."""

    def run_cmd(args) -> None:
        """Exécute la commande selon args."""

Les engines délèguent leurs opérations à leur ``lib.py``, exposé aux paquets
de niveau supérieur via import direct :

.. code-block:: python

    # Dans plg_enroll ou ops_cluster :
    from eng_k0s.kubewi import lib as k0s
    k0s.add_worker('worker-01')
