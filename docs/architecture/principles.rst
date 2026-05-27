Principes fondateurs
====================

L'architecture KubeWI repose sur plusieurs invariants structurants. Ces principes guident toutes les décisions techniques et architecturales du projet.

Infrastructure explicite
-------------------------

Les composants du système doivent être décrits explicitement :

- rôle des nœuds ;
- capacités matérielles ;
- placement des workloads ;
- topologies réseau ;
- stratégies de communication ;
- séparation des domaines critiques.

Le projet évite les comportements implicites ou les dépendances cachées. Ce principe se traduit concrètement par :

- des **labels Kubernetes** décrivant les capacités et le rôle de chaque nœud ;
- des **manifests versionnés** décrivant explicitement chaque workload et sa stratégie de placement ;
- des **topologies réseau documentées** pour chaque domaine de communication.

Séparation des responsabilités
--------------------------------

L'architecture distingue volontairement :

- orchestration ;
- contrôle temps réel ;
- communication distribuée ;
- observabilité ;
- stockage ;
- calcul embarqué ;
- exploitation de l'infrastructure.

Toutes les couches ne possèdent pas les mêmes contraintes temporelles ni les mêmes exigences de disponibilité.

Cette séparation permet de traiter chaque domaine selon ses propres contraintes sans imposer aux fonctions critiques les exigences des fonctions d'exploitation, et réciproquement.

Edge-first
-----------

La plateforme est conçue pour fonctionner localement, au plus près du système robotique.

Le cluster local n'est pas considéré comme un simple relais d'un cloud distant. Il constitue lui-même la plateforme d'exécution distribuée.

L'architecture doit pouvoir continuer à fonctionner même en cas de perte de connectivité externe.

Conséquences pratiques :

- la **registry OCI** est locale ;
- les **manifests** sont présents localement ;
- les **dépendances cloud** ne sont pas critiques pour le fonctionnement opérationnel ;
- le **cluster k0s** peut fonctionner de manière autonome.

Autonomie locale
-----------------

Chaque nœud doit pouvoir maintenir un niveau minimal de fonctionnement local en cas de perte de connectivité ou d'infrastructure.

Cette autonomie s'appuie sur :

- les workloads déjà déployés continuant à s'exécuter sans le control plane ;
- les composants hard real-time étant structurellement indépendants de la couche orchestrée ;
- les agents de collecte de logs bufferisant localement en cas d'indisponibilité du backend.

Reproductibilité
-----------------

Les déploiements doivent être **déterministes** et **reconstruisibles**.

La plateforme privilégie :

- le provisioning déclaratif via Ansible ;
- les manifests Kubernetes versionnés et auditables ;
- une approche GitOps compatible pour la gestion des ressources orchestrées ;
- des images OCI versionnées et distribuées via registry locale.

Résilience multi-couche
------------------------

La plateforme est conçue pour maintenir un fonctionnement partiel même en présence de défauts d'infrastructure ou de connectivité.

La résilience couvre :

- la couche logicielle (workloads, orchestration) ;
- la couche réseau (segmentation, chemins alternatifs) ;
- la couche matérielle (interfaces dédiées, redondance) ;
- la couche communication (Zenoh, fallback local).

.. important::
   Invariant clé : La perte d'une fonction d'exploitation (observabilité, stockage froid) ne doit jamais provoquer l'arrêt des fonctions robotiques essentielles.

→ Voir :doc:`Modes dégradés <resilience>` pour les scénarios détaillés.

Observabilité native
---------------------

L'observabilité est intégrée dès la conception, pas ajoutée après coup.

Chaque composant de la plateforme doit rester :

- **observable** : ses logs, métriques et flux réseau peuvent être collectés ;
- **diagnostiquable** : son état peut être inspecté en cas de dégradation ;
- **corrélable** : ses événements peuvent être mis en relation avec d'autres composants.

→ Voir :doc:`Observabilité <observability>` pour la stack complète.

Vocabulaire canonique
----------------------

Les termes suivants sont utilisés dans toute la documentation avec une signification précise :

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Terme
     - Signification
   * - Core Infrastructure
     - ensemble minimal des services nécessaires au fonctionnement autonome local
   * - Worker Node
     - nœud exécutant les workloads orchestrés
   * - Hard real-time
     - composant nécessitant des contraintes temporelles strictes et déterministes
   * - Soft real-time
     - composant tolérant une certaine variabilité temporelle
   * - Infrastructure d'exploitation
     - infrastructure dédiée à l'observabilité, la supervision et le stockage froid
   * - Placement explicite
     - stratégie consistant à décrire explicitement où un workload doit s'exécuter
   * - Edge-first
     - approche privilégiant le fonctionnement autonome local

→ Voir le :doc:`Glossaire complet </reference/glossary>`.
