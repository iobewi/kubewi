Rôle
====

``wrk_ros_core`` produit l'image de base ROS 2 sur laquelle s'appuient
tous les workloads robotiques du cluster (``wrk_ros_motion``,
``wrk_ros_perception``). Elle embarque ROS 2 Jazzy avec le middleware
Zenoh (``rmw-zenoh-cpp``) en remplacement de DDS.

Le paquet gère aussi le namespace Kubernetes ``ros`` et les RBAC
nécessaires à Headlamp pour l'observer.

----

Couches
-------

**Image** ``Dockerfile``
~~~~~~~~~~~~~~~~~~~~~~~~~

- Base : ``ros:jazzy`` (image officielle ROS 2)
- Ajouts : ``ros-jazzy-ros-base``, ``ros-jazzy-rmw-zenoh-cpp``
- Image produite : ``registry.kubewi.internal:5000/kubewi/ros-core:<tag>``

**Kubernetes** ``manifests/``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Manifest
     - Contenu
   * - ``manifests/ros-headlamp-access.yaml``
     - Namespace ``ros`` + ClusterRole + ClusterRoleBinding Headlamp
   * - ``manifests/test-arm64.yaml``
     - Job de validation arm64

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
