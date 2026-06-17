Ops Cluster
===========

.. list-table::
   :widths: 20 80
   :stub-columns: 1

   * - Paquet
     - ``ops_cluster``
   * - Type
     - ``ops``
   * - Dépendances
     - :doc:`../adp_kube/index`,
       :doc:`../adp_ansible/index`,
       :doc:`../ops_ssh/index`,
       :doc:`../plg_vpn/index`,
       :doc:`../plg_provisioning/index`,
       :doc:`../eng_k0s/index`

Cycle de vie déclaratif du cluster — bootstrap, ajout de nœuds, synchronisation
de la configuration et déploiement de la stack complète.

.. toctree::
   :maxdepth: 1

   role
   commands
   implementation
