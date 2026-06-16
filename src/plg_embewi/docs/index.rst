Plugin Embewi
=============

.. list-table::
   :widths: 20 80
   :stub-columns: 1

   * - Paquet
     - ``plg_embewi``
   * - Type
     - ``plugin``
   * - Dépendances
     - :doc:`../adp_kube/index`
   * - Prérequis réseau
     - :doc:`../plg_gateway/index` avec ``wifi_ap`` (VLAN 220)

Déploie ``embewi-core`` — le controller Kubernetes qui orchestre les
microcontrôleurs ESP32 via les CRDs ``McuNode`` et ``McuDeployment``.

.. toctree::
   :maxdepth: 1

   role
   commands
   implementation
