Stockage
=========

Le stockage n'est pas un espace partagé unique entre tous les composants du système. Chaque usage possède ses propres contraintes temporelles, de cohérence et de cycle de vie.

Introduction
-------------

La plateforme considère que toutes les données robotiques ne possèdent ni les mêmes contraintes temporelles, ni les mêmes contraintes de cohérence, ni les mêmes cycles de vie.

.. list-table::
   :header-rows: 1
   :widths: 25 25 25 25

   * - Donnée
     - Contrainte
     - Cohérence
     - Cycle de vie
   * - logs
     - append / streaming
     - eventual
     - rétention configurable
   * - état runtime
     - immédiat
     - forte
     - durée workload
   * - captures / rosbags
     - volumineuse
     - eventual
     - longue durée
   * - modèles IA
     - lecture intensive
     - eventual
     - versionné
   * - artefacts OCI
     - distribué
     - eventual
     - versionné
   * - télémétrie
     - streaming
     - eventual
     - rétention courte

L'architecture cherche à éviter qu'un unique mécanisme de stockage devienne un point de concentration global pour tous ces usages.

Catégories de stockage
-----------------------

La plateforme distingue explicitement trois catégories selon leur rôle dans le système :

.. list-table::
   :header-rows: 1
   :widths: 25 40 35

   * - Catégorie
     - Finalité
     - Exemples
   * - **Stockage opérationnel**
     - données nécessaires au fonctionnement immédiat des workloads
     - PV/PVC Kubernetes, volumes locaux, bases embarquées
   * - **Observabilité**
     - indexation et transport des logs et métriques
     - Vector, Loki
   * - **Stockage objet**
     - artefacts, archives et données volumineuses longue durée
     - MinIO, rosbags, modèles IA, exports

Chaque catégorie possède son propre cycle de vie, ses propres contraintes d'accès et ses propres mécanismes de résilience.

Stockage opérationnel
----------------------

Le stockage opérationnel regroupe les données nécessaires au fonctionnement immédiat des workloads : état applicatif, cache, bases locales, données runtime.

Ces données sont gérées via les mécanismes de stockage Kubernetes :

- volumes persistants (PV/PVC) ;
- stockage local par nœud ;
- stockage distribué selon les besoins et les capacités disponibles.

.. warning::
   Le stockage objet (MinIO) ne remplace pas le stockage opérationnel.
   Un volume Kubernetes et un bucket S3 ne répondent pas aux mêmes contraintes de cohérence, de latence et d'accès.

Observabilité et logs
----------------------

La plateforme distingue explicitement les étapes du pipeline de logs :

.. list-table::
   :header-rows: 1
   :widths: 25 25 50

   * - Étape
     - Composant
     - Rôle
   * - collecte
     - Vector
     - agent local sur chaque Worker Node
   * - transport
     - Vector
     - bufferisation et envoi vers le backend
   * - indexation
     - Loki
     - stockage et indexation des logs
   * - visualisation
     - Grafana
     - consultation et corrélation

Les agents Vector sont déployés au plus près des workloads afin de :

- collecter les logs localement sans montage partagé ;
- bufferiser temporairement en cas d'indisponibilité du backend ;
- limiter les dépendances centralisées.

.. note::
   Loki est un backend d'indexation de logs : pas un système de stockage applicatif généraliste.
   Il n'est pas conçu pour stocker des données opérationnelles ou des artefacts volumineux.

→ Voir :doc:`Observabilité <observability>` pour le détail de la stack.

Stockage objet : MinIO
-----------------------

MinIO constitue la solution principale de stockage objet compatible S3.

Il est utilisé pour les données volumineuses, les artefacts et les données longue durée :

- rosbags et captures robotiques ;
- exports de données et dumps ;
- modèles IA versionnés ;
- artefacts applicatifs et packages ;
- archivage longue durée.

MinIO est principalement dimensionné pour les **objets volumineux et l'archivage**, mais peut également servir de backend pour des pipelines actifs (datasets ML, artefacts OCI en cache). Il peut être externalisé vers une infrastructure d'exploitation dédiée locale ou distante.

Partage de fichiers bruts
--------------------------

Le partage de fichiers classique (NFS central, répertoires partagés globaux) n'est pas le mécanisme principal de communication ou de centralisation des données dans la plateforme.

Ces approches introduisent des problèmes structurels dans une architecture distribuée :

- **couplage implicite** entre workloads partageant le même montage ;
- **perte de traçabilité** des flux de données entre composants ;
- **synchronisation implicite** non contrôlée ;
- **dépendances invisibles** difficiles à détecter et à documenter ;
- **SPOF** en cas de défaillance du point de partage central ;
- **saturation** en cas de concentration des accès.

Ces mécanismes peuvent exister pour des usages ponctuels spécifiques, mais ne constituent pas le socle de l'architecture distribuée.

Architecture d'exploitation
-----------------------------

Les services de stockage froid et d'observabilité peuvent être externalisés hors du cluster robotique local : c'est même l'approche recommandée pour les déploiements disposant de ressources dédiées.

.. list-table::
   :header-rows: 1
   :widths: 25 40 35

   * - Service
     - Rôle
     - Placement recommandé
   * - Loki
     - indexation des logs
     - infrastructure d'exploitation
   * - Grafana
     - visualisation
     - infrastructure d'exploitation
   * - MinIO
     - stockage objet et archivage
     - infrastructure d'exploitation ou cluster dédié
   * - Vector
     - collecte et transport
     - déployé sur chaque Worker Node

Cette séparation permet de :

- limiter la charge du cluster robotique opérationnel ;
- conserver l'autonomie locale du cluster même si l'exploitation devient indisponible ;
- séparer clairement les flux d'exploitation des flux robotiques ;
- limiter l'impact des traitements d'analyse longue durée sur le fonctionnement temps réel.

Résilience stockage
--------------------

L'architecture garantit un niveau minimal d'autonomie opérationnelle locale même en cas de perte des composants d'exploitation et d'archivage.

.. important::
   Invariant : La perte temporaire du stockage d'exploitation (MinIO, Loki, Grafana) ne doit pas empêcher le fonctionnement immédiat du système robotique.

.. list-table::
   :header-rows: 1
   :widths: 25 35 40

   * - Défaillance
     - Comportement attendu
     - Mécanisme architectural
   * - perte Loki
     - les workloads continuent, logs bufferisés
     - pipeline asynchrone Vector, buffering local, pas de dépendance bloquante
   * - perte MinIO
     - archivage et exports différés
     - stockage runtime découplé du stockage objet
   * - perte Grafana
     - perte de visualisation uniquement
     - visualisation séparée de l'exécution opérationnelle
   * - perte infrastructure exploitation
     - robot continue en mode autonome local
     - autonomie locale, workloads déjà déployés, hard RT indépendant

→ Voir :doc:`Modes dégradés <resilience>` pour les scénarios complets.

Positionnement architectural
------------------------------

KubeWI distingue explicitement :

- **stockage opérationnel** : volumes Kubernetes, données nécessaires au fonctionnement immédiat ;
- **observabilité** : pipeline distribué Vector → Loki → Grafana, non bloquant ;
- **stockage objet** : MinIO, artefacts et données volumineuses longue durée ;
- **exploitation distribuée** : séparable, externalisable, non critique pour le robot.

Cette architecture vise à conserver un système observable, découplé, reproductible, compatible avec les modes dégradés et adapté aux contraintes edge.

Chaque couche de stockage correspond à un usage précis. Aucune n'est censée absorber les responsabilités des autres.
