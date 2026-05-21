Résilience et modes dégradés
=============================

Les modes dégradés sont une propriété normale des systèmes robotiques distribués. L'objectif n'est pas d'empêcher toute dégradation, mais de maintenir un comportement prévisible et localement maîtrisé.

Introduction
-------------

KubeWI ne cherche pas à construire une plateforme infiniment résiliente. Elle cherche à **dégrader le système de manière contrôlée et prévisible** — en maintenant les fonctions essentielles même en présence de défauts partiels d'infrastructure ou de connectivité.

La couche orchestrée ne doit pas devenir un point de dépendance immédiat des fonctions critiques. Aucune fonction critique immédiate ne doit dépendre exclusivement d'un composant distribué unique — cluster, réseau, stockage, observabilité ou orchestration.

.. important::
   Invariants de résilience

   - La perte de l'observabilité ne doit pas arrêter les workloads.
   - La perte du stockage froid ne doit pas arrêter le robot.
   - La perte du réseau distribué ne doit pas interrompre les fonctions locales critiques.
   - La perte du cluster robotique local ne doit pas impacter les composants hard real-time autonomes.
   - Aucune fonction critique immédiate ne doit dépendre exclusivement d'un composant distribué unique.

Principe général
-----------------

La plateforme distingue explicitement :

- les fonctions critiques immédiates (hard RT, contrôle local) ;
- les fonctions distribuées orchestrées (soft RT, workloads) ;
- les fonctions d'exploitation (observabilité, supervision) ;
- les fonctions d'archivage et de stockage froid.

Toutes les défaillances n'ont pas le même impact opérationnel. La résilience de la plateforme est organisée autour de cette hiérarchie.

Dégradations infrastructure
-----------------------------

.. list-table::
   :header-rows: 1
   :widths: 25 35 40

   * - Défaillance
     - Comportement attendu
     - Mécanisme architectural
   * - perte du Core Node
     - workloads déjà actifs continuent autant que possible
     - kubelet local, dépendances runtime locales, services critiques découplés du control plane
   * - perte partielle du cluster
     - maintien des fonctions locales critiques
     - nodeAffinity, colocalisation, fallback local, labels de capacité
   * - perte Kubernetes
     - composants hard RT autonomes non impactés
     - hard RT hors couche orchestrée, firmware autonome, MCU indépendants du cluster
   * - perte orchestration
     - absence de replanification, workloads existants maintenus
     - distinction control plane / workloads déjà déployés, autonomie des Worker Nodes
   * - perte infrastructure d'exploitation
     - fonctionnement robotique maintenu
     - observabilité et stockage froid non bloquants, externalisés

Dégradations observabilité et stockage
----------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 25 35 40

   * - Défaillance
     - Comportement attendu
     - Mécanisme architectural
   * - perte Loki
     - workloads continuent, logs bufferisés temporairement
     - pipeline asynchrone Vector, bufferisation locale, pas de dépendance bloquante
   * - perte Grafana
     - perte de visualisation uniquement
     - visualisation découplée de l'exécution opérationnelle
   * - perte MinIO
     - archivage et exports différés
     - stockage runtime séparé du stockage objet, réémission différée
   * - perte stockage froid
     - fonctionnement opérationnel maintenu
     - séparation stockage opérationnel / stockage d'exploitation
   * - perte infrastructure observabilité
     - perte de supervision, fonctions robotiques maintenues
     - agents locaux autonomes, découplage exploitation / opérationnel

.. _degradations-reseau:

Dégradations réseau
--------------------

.. list-table::
   :header-rows: 1
   :widths: 25 35 40

   * - Défaillance
     - Comportement attendu
     - Mécanisme architectural
   * - perte réseau inter-nœuds
     - maintien des fonctions locales sur chaque Worker Node
     - colocalisation via ``nodeAffinity``, fallback local, workloads autonomes
   * - perte partielle du réseau
     - fonctionnement limité selon la topologie restante
     - segmentation réseau, routage explicite, chemins alternatifs
   * - saturation réseau
     - priorisation des flux critiques
     - VLAN, QoS réseau, interfaces dédiées, séparation des flux non critiques
   * - perte réseau observabilité
     - workloads opérationnels maintenus
     - observabilité découplée de l'exécution, buffering local Vector
   * - perte Zenoh router
     - fallback selon la topologie disponible
     - Zenoh peer-to-peer sans router, DDS local, cache état local, MCU autonomes sur bus terrain
   * - perte connectivité externe
     - fonctionnement edge local maintenu
     - registry OCI locale, manifests présents localement, dépendances cloud non critiques

.. note::
   La perte du Zenoh router n'interrompt pas nécessairement les communications : Zenoh peut opérer en mode peer-to-peer entre pods sans passer par un router central. Les boucles MCU restent autonomes via leurs bus terrain locaux.

Dégradations hard real-time
-----------------------------

.. list-table::
   :header-rows: 1
   :widths: 25 35 40

   * - Défaillance
     - Comportement attendu
     - Mécanisme architectural
   * - perte couche orchestrée
     - hard RT autonome non impacté directement
     - MCU, firmware, micro-ROS et Zenoh-Pico structurellement hors couche orchestrée
   * - perte observabilité
     - firmware et contrôle local maintenus
     - aucune dépendance directe des boucles critiques aux backends d'observabilité
   * - perte communication distribuée
     - boucles critiques locales maintenues
     - contrôle local autonome, bus terrain locaux, fallback firmware
   * - perte infrastructure d'exploitation
     - aucune dépendance immédiate des MCU et firmware
     - séparation stricte exploitation / contrôle critique

Les composants hard real-time autonomes sont volontairement découplés de toute dépendance d'exploitation et d'orchestration distribuée.

Résilience locale — le Worker Node comme unité de survie
----------------------------------------------------------

Chaque Worker Node constitue l'unité minimale de survie opérationnelle de la plateforme.

En cas de perte de connectivité ou d'infrastructure partielle, un Worker Node doit pouvoir maintenir un niveau minimal de fonctionnement autonome :

- les workloads déjà déployés continuent de s'exécuter sans le control plane ;
- les agents locaux (Vector, Cilium) restent opérationnels indépendamment des backends ;
- les boucles hard RT associées (firmware, MCU) restent fonctionnelles hors cluster ;
- les communications locales (DDS, Zenoh P2P, bus terrain) sont maintenues.

Cette autonomie locale repose sur :

- firmware autonome et boucles locales indépendantes ;
- cache et état local des workloads déjà déployés ;
- bufferisation temporaire des pipelines de logs ;
- communications locales préservées indépendamment de l'état du réseau inter-nœuds ;
- chemins réseau alternatifs et segmentation des domaines critiques.

Limites assumées
-----------------

La plateforme ne garantit pas :

- une continuité totale sans dégradation de service ;
- une orchestration distribuée sans interruption en cas de panne infrastructure ;
- une observabilité permanente et complète ;
- une synchronisation parfaite entre tous les nœuds en toutes circonstances.

L'objectif est de :

- **limiter les impacts** des défaillances selon leur localisation ;
- **maintenir les fonctions essentielles** locales en mode dégradé ;
- **préserver les contraintes critiques** (hard RT, contrôle local) indépendamment du cluster ;
- **rendre les dégradations prévisibles**, observables et localement maîtrisées.

Positionnement architectural
------------------------------

KubeWI traite les modes dégradés comme une contrainte normale des systèmes distribués edge — pas comme des cas d'erreur exceptionnels.

L'architecture cherche à maintenir, même en présence de défauts partiels :

- l'autonomie locale de chaque Worker Node ;
- les fonctions hard real-time indépendantes du cluster ;
- les capacités critiques de contrôle et d'acquisition ;
- les communications essentielles locales.

La dégradation est contrôlée, hiérarchisée et prévisible. Le système ne s'arrête pas — il se replie sur ses fonctions locales essentielles.
