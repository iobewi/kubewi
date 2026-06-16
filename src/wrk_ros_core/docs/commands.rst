Commandes CLI
=============

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
     - Applique ``test-arm64.yaml`` — valide que l'image tourne sur arm64.
   * - ``kubewi ros-core ns-deploy``
     - Crée le namespace ``ros`` et les RBAC Headlamp.
       À lancer une seule fois lors de l'initialisation du cluster.
