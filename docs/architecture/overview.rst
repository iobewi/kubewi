Architecture
============

KubeWI formalise une architecture d'infrastructure destinée aux systèmes robotiques distribués.

Le projet ne cherche pas uniquement à exécuter ROS2 sur Kubernetes. L'objectif est de construire une plateforme capable d'organiser explicitement :

- les contraintes temps réel ;
- les communications distribuées ;
- les topologies réseau ;
- les capacités matérielles ;
- les stratégies de déploiement ;
- l'observabilité ;
- les modes dégradés ;
- les invariants système.

Cette architecture considère qu'un système robotique moderne est composé de plusieurs couches hétérogènes ayant des contraintes différentes et parfois incompatibles. Le rôle de la plateforme est d'organiser ces contraintes plutôt que de tenter de les masquer.

Niveaux architecturaux
-----------------------

L'architecture distingue quatre niveaux principaux :

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Niveau
     - Rôle
   * - **Core Infrastructure**
     - coordination du cluster robotique local
   * - **Worker Nodes**
     - exécution des workloads robotiques distribués
   * - **Infrastructure d'exploitation**
     - observabilité, visualisation et stockage froid
   * - **Hors cluster robotique local**
     - composants hard real-time et interfaces critiques

La **Core Infrastructure** porte les fonctions nécessaires au fonctionnement autonome immédiat du cluster robotique local.

Les **Worker Nodes** exécutent les workloads applicatifs orchestrés par k0s.

L'**infrastructure d'exploitation** regroupe les services non indispensables au fonctionnement immédiat du système robotique, mais nécessaires à l'analyse, l'historisation et l'exploitation longue durée.

Les composants **hors cluster robotique local** restent au plus près du matériel et portent les contraintes hard real-time : firmware, micro-ROS, Zenoh-Pico, interfaces bas niveau et contrôle critique.

Rôle de k0s
------------

k0s constitue la couche d'orchestration de la plateforme.

Son rôle est notamment :

- déployer les workloads ;
- maintenir l'état désiré ;
- gérer les ressources ;
- superviser les services ;
- orchestrer les communications réseau ;
- standardiser les déploiements.

La couche orchestrée Kubernetes n'est pas considérée comme adaptée aux contraintes hard real-time strictes. Elle orchestre les services distribués autour des composants critiques temps réel.

Stratégie de déploiement
-------------------------

La plateforme privilégie une approche déclarative du déploiement des workloads et de l'infrastructure orchestrée.

Les composants Kubernetes sont décrits sous forme de manifests versionnés et reproductibles :

- workloads ;
- services ;
- politiques réseau ;
- configurations ;
- stratégies de placement ;
- observabilité ;
- stockage.

L'objectif est de garantir :

- la traçabilité des changements ;
- la reproductibilité des déploiements ;
- l'inspectabilité de l'infrastructure ;
- la réduction des dérives de configuration.

Approche GitOps
~~~~~~~~~~~~~~~

La plateforme est compatible avec une approche GitOps pour la gestion des ressources orchestrées.

Dans cette approche :

- Git devient la source de vérité déclarative ;
- les manifests Kubernetes sont versionnés ;
- les changements d'infrastructure deviennent auditables ;
- les déploiements peuvent être réconciliés automatiquement.

Le GitOps concerne principalement :

- les workloads Kubernetes ;
- les manifests d'infrastructure ;
- les politiques réseau ;
- les configurations d'observabilité ;
- les stratégies de placement.

Le bootstrap initial, certaines opérations terrain ou les environnements partiellement déconnectés peuvent néanmoins nécessiter des opérations hors GitOps. La plateforme considère donc GitOps comme une stratégie d'exploitation privilégiée, mais non comme une dépendance absolue au fonctionnement du système robotique.

Workloads ROS2
---------------

Les workloads ROS2 s'exécutent principalement dans Kubernetes.

Exemples : perception, fusion de données, navigation, supervision, traitement GPU, services distribués, passerelles réseau.

L'architecture considère que ROS2 distribué doit rester observable, déployable et reproductible.

Placement des workloads
~~~~~~~~~~~~~~~~~~~~~~~~

La plateforme privilégie un placement explicite des workloads basé sur les capacités déclarées des nœuds.

Les stratégies de placement s'appuient notamment sur :

- ``nodeSelector``
- ``nodeAffinity``
- ``taints`` et ``tolerations``
- contraintes réseau et matérielles explicites

Le placement peut notamment prendre en compte :

- l'architecture CPU ;
- les accélérations GPU ;
- les contraintes temps réel ;
- les interfaces matérielles ;
- les équipements réellement intégrés ;
- les caractéristiques réseau.

Cette approche permet un placement reproductible, une meilleure lisibilité du système, une réduction des décisions implicites et une cohérence entre contraintes physiques et exécution logicielle.

Séparation hard RT / soft RT
------------------------------

La plateforme distingue explicitement les composants hard real-time des workloads distribués.

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Domaine
     - Emplacement
   * - Hard real-time
     - hors cluster robotique local
   * - MCU
     - firmware embarqué
   * - micro-ROS
     - hors couche orchestrée
   * - Zenoh-Pico
     - hors couche orchestrée
   * - Soft real-time
     - couche orchestrée Kubernetes
   * - Perception
     - Kubernetes
   * - Supervision
     - Kubernetes

Les boucles critiques restent proches du matériel : contrôle moteur, acquisition déterministe, bus terrain, interfaces critiques, firmware. Kubernetes n'est pas utilisé pour exécuter les composants nécessitant des garanties hard real-time strictes.

→ Voir :doc:`Temps réel <realtime>` pour le détail complet.

Invariants d'architecture
--------------------------

Les futures évolutions de la plateforme doivent respecter plusieurs invariants structurants :

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Invariant
     - Description
   * - autonomie locale
     - un Worker Node doit pouvoir maintenir ses fonctions essentielles
   * - hard RT séparé
     - les composants critiques restent hors cluster robotique local
   * - placement explicite
     - toute décision de placement doit être traçable
   * - flux inspectables
     - les communications doivent rester observables
   * - infrastructure explicite
     - réseau, rôles et capacités doivent être déclarés
   * - séparation exploitation / opérationnel
     - l'exploitation ne doit pas perturber les fonctions robotiques
   * - résilience multi-couche
     - la résilience concerne logiciel, réseau et matériel
   * - reproductibilité
     - les déploiements doivent être déterministes
   * - orchestration légère
     - maîtrise de la complexité infrastructure
   * - infrastructure pilotée
     - l'infrastructure doit rester déclarative, inspectable et versionnable
   * - GitOps compatible
     - les workloads orchestrés doivent pouvoir être reconstruits depuis leurs manifests déclaratifs

Conclusion
-----------

KubeWI formalise une architecture d'infrastructure robotique distribuée où :

- Kubernetes orchestre les workloads distribués ;
- les composants hard real-time restent hors cluster robotique local ;
- le réseau devient une composante explicite du système ;
- l'observabilité est intégrée dès la conception ;
- les fonctions d'exploitation peuvent être externalisées ;
- les mécanismes de résilience couvrent logiciel, réseau et matériel ;
- les modes dégradés sont pris en compte nativement ;
- les infrastructures edge conservent leur autonomie locale.

Cette architecture constitue la cible de référence que les futures évolutions techniques devront respecter.

.. toctree::
   :hidden:

   principles
   components
   networking
   realtime
   storage
   observability
   resilience
