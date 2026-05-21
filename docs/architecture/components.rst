Composants de la plateforme
============================

La plateforme distingue explicitement trois domaines aux responsabilités, contraintes et cycles de vie différents : le cluster robotique local, l'infrastructure d'exploitation, et les composants hors orchestration.

Cette séparation systémique des responsabilités est le fil conducteur de toute l'architecture.

Core Infrastructure locale
----------------------------

La **Core Infrastructure** désigne l'ensemble logique des services nécessaires au fonctionnement autonome du cluster robotique local.

Un **Core Node** représente une implémentation physique possible de cette infrastructure. La Core Infrastructure peut être portée par un ou plusieurs Core Nodes selon la taille et les contraintes du déploiement.

.. note::
   Core Infrastructure ≠ machine unique.
   La Core Infrastructure est un concept logique — un ensemble de services de coordination.
   Le Core Node est son implémentation physique, qui peut être répartie.

Cette couche porte les fonctions nécessaires au fonctionnement autonome du cluster robotique local :

- orchestration Kubernetes ;
- services réseau locaux (Cilium, Multus) ;
- registry OCI locale ;
- routage et communication distribuée (Zenoh) ;
- connectivité distante (VPN).

Core Node — services principaux
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. k0s — Motivation: distribution Kubernetes légère, edge-first, faible complexité opérationnelle.
.. Alternative écartée: k3s (légèrement plus lourd), kubeadm (trop complexe pour edge).
.. Contraintes adressées: autonomie locale, cluster embarqué, déploiement reproductible.

.. OCI registry — Motivation: indépendance cloud, fonctionnement offline, distribution locale des images.
.. Contrainte adressée: edge-first, pas de dépendance à un registry distant au runtime.

.. Zenoh router — Motivation: réduire la dépendance au multicast DDS, topologies routées, réseaux intermittents.
.. Alternative écartée: DDS multicast seul — difficile à maîtriser sur réseaux segmentés ou routés.
.. Contrainte adressée: communication distribuée explicite et maîtrisable.

.. VPN — Motivation: connectivité distante sécurisée sans exposer le cluster directement.

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Service
     - Rôle
   * - k0s control plane
     - orchestration Kubernetes du cluster robotique local
   * - OCI registry
     - distribution locale des images, indépendance cloud
   * - Zenoh router
     - communication distribuée inter-nœuds et vers les composants embarqués
   * - VPN
     - connectivité distante sécurisée
   * - Cilium
     - dataplane réseau eBPF, instrumentation native
   * - Multus
     - attachement d'interfaces réseau multiples aux workloads

Services d'exploitation externalisables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Selon les ressources disponibles et le mode de déploiement, certains services d'exploitation peuvent être colocalisés sur le Core Node ou externalisés vers une infrastructure dédiée.

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Service
     - Usage
   * - Loki
     - backend d'indexation des logs
   * - Grafana
     - visualisation et supervision
   * - Hubble UI
     - observabilité des flux réseau
   * - MinIO
     - stockage objet et archivage

.. important::
   Ces services sont externalisables — pas optionnels au sens architectural.
   L'exploitation est nécessaire à l'opération longue durée du système. Elle peut simplement résider hors du cluster robotique local sans compromettre son fonctionnement immédiat.

.. note::
   Dans les architectures edge autonomes compactes à ressources limitées, ces services sont externalisés vers une infrastructure d'exploitation dédiée.

Worker Nodes
-------------

Les Worker Nodes constituent la couche d'exécution distribuée des workloads robotiques orchestrés. Ils rejoignent le cluster k0s comme nœuds Kubernetes et exécutent les charges applicatives sous forme de conteneurs orchestrés.

Perception, IA, supervision, navigation, fusion de données et passerelles réseau sont tous pensés comme des services distribués orchestrables — déployables, reproductibles et redéployables automatiquement.

Profils de nœuds
~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Type
     - Usage principal
   * - Motion Worker
     - contrôle robotique local, ros2_control (soft RT)
   * - Perception Worker
     - vision, IA et GPU (CUDA / TensorRT)
   * - Generic Edge Worker
     - services distribués, passerelles réseau et gateways

.. Cilium — Motivation: dataplane observable via eBPF, inspection native sans sonde externe.
.. Alternative écartée: Flannel — pas d'instrumentation réseau intégrée.
.. Contraintes adressées: réseau inspectable, policies déclaratives, observabilité runtime.

.. Multus — Motivation: certains workloads nécessitent des interfaces réseau séparées (robotique, terrain, stockage).
.. Contrainte adressée: isolation des flux, pas de mélange management/robotique sur une seule interface.

.. Vector — Motivation: pipeline logs distribué sans montage partagé centralisé, bufferisation locale.
.. Alternative écartée: Fluentd (plus lourd), NFS partagé (SPOF, couplage implicite).
.. Contrainte adressée: logs distribués, résilience pipeline, pas de dépendance bloquante au backend.

Agents d'infrastructure déployés sur chaque Worker Node
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Agent
     - Rôle
   * - Vector
     - collecte et transport local des logs
   * - Cilium
     - dataplane réseau eBPF, politique et instrumentation
   * - Multus
     - attachement d'interfaces réseau secondaires
   * - Hubble
     - visibilité native des flux réseau au niveau du dataplane

Composants hors orchestration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sous chaque Worker Node, des composants s'exécutent **structurellement hors de la couche Kubernetes** — leur fonctionnement ne dépend pas du cluster :

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Composant
     - Rôle
   * - MCU
     - microcontrôleur embarqué, boucles hard real-time
   * - micro-ROS
     - adaptation ROS2 pour MCU hors cluster
   * - Zenoh-Pico
     - communication embarquée légère entre MCU et cluster
   * - firmware dédié
     - contrôle bas niveau et interfaces critiques

Ces composants constituent la couche hard real-time autonome du système. Leur fonctionnement est indépendant de l'état du cluster Kubernetes.

→ Voir :doc:`Temps réel <realtime>` pour le détail de la séparation hard RT / soft RT.

Infrastructure d'exploitation
-------------------------------

L'infrastructure d'exploitation regroupe les services dédiés à l'analyse, la supervision et l'archivage longue durée.

.. important::
   Les fonctions d'exploitation ne doivent pas devenir des dépendances immédiates du fonctionnement robotique local.
   Observabilité, archivage et dashboards sont différables — le cluster robotique ne l'est pas.

Ces services sont externalisés par défaut vers une infrastructure dédiée locale ou distante :

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Service
     - Placement recommandé
   * - Loki
     - cluster d'observabilité local ou distant
   * - Grafana
     - cluster d'observabilité local ou distant
   * - Hubble UI
     - cluster d'observabilité local ou distant
   * - MinIO
     - cluster de stockage local ou distant

Cette séparation permet de limiter la charge de la Core Infrastructure, de conserver une architecture edge autonome, et de séparer coordination locale et exploitation longue durée.

Vue d'architecture de référence
----------------------------------

La plateforme distingue trois catégories de composants selon leur rôle, leur niveau de criticité et leur cycle de vie :

**Services nécessaires au fonctionnement autonome local**

- k0s control plane
- OCI registry locale
- Zenoh router
- VPN
- Cilium / Multus

**Services d'exploitation externalisables**

- Loki, Grafana, Hubble UI
- MinIO

**Services toujours hors cluster**

- MCU / firmware
- micro-ROS
- Zenoh-Pico
- interfaces terrain (CAN, I2C, SPI, UART…)

.. list-table::
   :header-rows: 1
   :widths: 25 20 55

   * - Domaine
     - Nature
     - Dépendance immédiate au cluster
   * - Contrôle hard RT
     - MCU / firmware
     - aucune — autonome par construction
   * - Exécution distribuée
     - Worker Nodes
     - oui — orchestrée par k0s
   * - Coordination locale
     - Core Infrastructure
     - oui — porte le cluster
   * - Exploitation
     - Loki / Grafana / MinIO
     - non — externalisable et différable

Modèle déclaratif des capacités
---------------------------------

Les capacités matérielles critiques doivent être explicitement décrites — et non implicitement supposées par l'orchestrateur.

La plateforme repose sur un modèle déclaratif exposant les capacités réelles des nœuds via des labels Kubernetes sous le namespace :

.. code-block:: text

   r2bewi.io/*

Ces labels permettent de décrire :

- les ressources de calcul et accélérations matérielles ;
- les contraintes temps réel ;
- les équipements réellement intégrés ;
- les interfaces matérielles disponibles ;
- les capacités utiles au placement des workloads.

Exemples :

.. code-block:: text

   r2bewi.io/compute.class=embedded
   r2bewi.io/compute.accelerator=nvidia
   r2bewi.io/compute.realtime=true
   r2bewi.io/device.camera=stereo
   r2bewi.io/device.motor=bldc

Ce modèle va au-delà du simple labeling Kubernetes classique. Il formalise les capacités matérielles comme **primitives d'orchestration** — rendant le système physique explicite, inspectable et exploitable par le scheduler.

La source de vérité reste l'opérateur et l'intégration matérielle réelle du système.

.. Loki — Motivation: indexation logs légère, compatible Vector, externalisable.
.. Grafana — Motivation: visualisation unifiée logs + réseau + métriques.
.. Hubble — Motivation: visibilité native Cilium, pas de sonde réseau externe.
.. MinIO — Motivation: stockage objet S3-compatible, déployable localement, externalisable.
.. Contrainte adressée: stockage froid non critique, différable, indépendant du runtime.

.. Ansible — Motivation: provisioning déclaratif, reproductible, auditable.
.. Contrainte adressée: infrastructure versionnable, bootstrap offline possible.

.. micro-ROS + Zenoh-Pico — Motivation: communication légère pour MCU hors cluster.
.. Contrainte adressée: hard RT autonome, pas de dépendance réseau IP pour les boucles critiques.

.. GitOps — Motivation: traçabilité et reproductibilité des déploiements orchestrés.
.. Nuance: bootstrap offline et opérations terrain restent possibles hors GitOps.

Composants principaux — tableau de synthèse
--------------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Composant
     - Rôle architectural
   * - **k0s**
     - orchestration Kubernetes légère du cluster robotique local
   * - **Cilium**
     - dataplane réseau eBPF : politiques, instrumentation native, inspection flux
   * - **Multus**
     - attachement d'interfaces réseau multiples aux pods — ne gère pas la segmentation à lui seul
   * - **Zenoh**
     - communication distribuée inter-nœuds : routage, découplage réseau, réduction multicast DDS, topologies edge et intermittentes
   * - **Zenoh-Pico**
     - communication embarquée pour MCU hors couche orchestrée
   * - **Vector**
     - collecte locale et transport des logs, bufferisation temporaire
   * - **Loki**
     - indexation et stockage des logs — backend d'exploitation, non applicatif
   * - **Grafana**
     - visualisation, supervision et corrélation logs / réseau / métriques
   * - **Hubble**
     - visibilité et inspection native des flux réseau au niveau dataplane
   * - **MinIO**
     - stockage objet compatible S3 : artefacts, rosbags, modèles IA, archivage
   * - **Ansible**
     - provisioning déclaratif, reproductible et auditable des nœuds

