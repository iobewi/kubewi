Workload ROS Core
=================

.. list-table::
   :widths: 20 80
   :stub-columns: 1

   * - Paquet
     - ``wrk_ros_core``
   * - Type
     - ``workload``
   * - Image
     - ``ros-core``
   * - Dépendances
     - :doc:`/src/wrk_buildkit/docs`

Image ROS 2 Jazzy + Zenoh — base pour tous les nœuds ROS du cluster.

----

Rôle
----

``wrk_ros_core`` produit l'image de base ROS 2 sur laquelle s'appuient
tous les workloads robotiques du cluster (``wrk_ros_motion``,
``wrk_ros_perception``). Elle embarque ROS 2 Jazzy avec le middleware
Zenoh (``rmw-zenoh-cpp``) en remplacement de DDS.

Le paquet gère aussi le namespace Kubernetes ``ros`` et les RBAC
nécessaires à Headlamp pour l'observer, via deux manifests dédiés.

----

Dépendances
-----------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Paquet
     - Ce qui est utilisé
   * - ``wrk_buildkit``
     - build multi-arch (x86_64 + arm64), push vers la registry interne

----

Couches
-------

**Image** ``Dockerfile``
~~~~~~~~~~~~~~~~~~~~~~~~~

- Base : ``ros:jazzy`` (image officielle ROS 2)
- Ajouts : ``ros-jazzy-ros-base``, ``ros-jazzy-rmw-zenoh-cpp``
- Image produite : ``registry.kubewi.internal:5000/kubewi/ros-core:<tag>``

Le build arm64 est nécessaire pour les workers Raspberry Pi et Jetson.
Il utilise ``wrk_buildkit`` avec émulation QEMU via ``docker buildx``.
Le VPN doit être actif (``kubewi vpn up``) pour pusher vers la registry.

**Kubernetes** ``manifests/``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Manifest
     - Contenu
   * - ``manifests/ros-headlamp-access.yaml``
     - Namespace ``ros`` + ClusterRole + ClusterRoleBinding pour
       permettre à Headlamp d'observer les ressources ROS
   * - ``manifests/test-arm64.yaml``
     - Job de validation arm64 — lance un pod ``ros-core`` sur un
       worker arm64 et vérifie que ROS 2 démarre correctement

----

Commandes CLI
-------------

.. code-block:: text

   kubewi ros-core build        build de l'image (x86_64)
   kubewi ros-core push         push vers la registry interne
   kubewi ros-core clean        supprime l'image locale
   kubewi ros-core lint         lint du Dockerfile (hadolint)
   kubewi ros-core build-arm64  build et push arm64 (VPN requis)
   kubewi ros-core test-deploy  déploie le Job de test arm64 sur le cluster
   kubewi ros-core ns-deploy    applique le namespace ros et les RBAC Headlamp

.. list-table::
   :header-rows: 1
   :widths: 42 58

   * - Commande
     - Usage
   * - ``kubewi ros-core build``
     - Build local x86_64. Utile pour valider le Dockerfile.
   * - ``kubewi ros-core build-arm64``
     - Build cross-compilé arm64 via buildkit + push immédiat.
       VPN actif requis (registry sur VLAN 420).
   * - ``kubewi ros-core test-deploy``
     - Applique ``test-arm64.yaml`` — à lancer après ``build-arm64``
       pour valider que l'image tourne sur un worker arm64.
   * - ``kubewi ros-core ns-deploy``
     - Crée le namespace ``ros`` et les RBAC Headlamp.
       À lancer une seule fois lors de l'initialisation du cluster.

----

Implémentation
--------------

Zenoh remplace DDS comme middleware RMW car DDS impose de la découverte
multicast qui ne passe pas facilement à travers les VLANs et les bridges
du cluster. Zenoh fonctionne en mode unicast et s'adapte mieux à cette
topologie réseau.

Le build arm64 utilise ``docker buildx`` avec un builder ``kubewi-arm64``
configuré par ``wrk_buildkit``. L'image est pushée directement depuis
le builder vers la registry (``--output type=image,push=true``) sans
passer par le daemon Docker local — ce qui contourne la limitation de
taille mémoire du builder sur le SDK.

``wrk_ros_motion`` et ``wrk_ros_perception`` utilisent cette image
comme base via ``ARG REGISTRY`` + ``FROM ${REGISTRY}/kubewi/ros-core:latest``,
ce qui garantit que tous les nœuds ROS partagent exactement le même socle.
