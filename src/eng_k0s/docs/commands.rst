Commandes CLI
=============

.. code-block:: text

   kubewi k0s kubeconfig          récupère le kubeconfig et configure kubectl
   kubewi k0s add controller      déploie k0s sur les controllers
   kubewi k0s add worker --name   initialise et joint un worker

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - Commande
     - Usage
   * - ``kubewi k0s kubeconfig``
     - Récupère le kubeconfig depuis le controller, configure kubectl
       avec le contexte ``kubewi``.
   * - ``kubewi k0s add controller``
     - Applique ``controller.yml`` sur les controllers.
       ``--limit`` pour cibler un controller spécifique.
   * - ``kubewi k0s add worker --name <nom>``
     - Lance les deux phases d'enrollment pour un worker :
       d'abord ``workers-init.yml`` (via IP provisioning),
       puis ``worker.yml`` (via VLAN 220 + WireGuard).
