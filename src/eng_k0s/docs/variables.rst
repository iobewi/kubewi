Variables
=========

.. list-table::
   :header-rows: 1
   :widths: 38 28 34

   * - Variable
     - Défaut
     - Description
   * - ``k0s_version``
     - *(dernière stable)*
     - Version k0s à installer. Définie dans ``group_vars/kubernetes.yml``.
   * - ``k0s_api_address``
     - ``192.168.22.{{ host_id }}``
     - IP de l'API server k0s (VLAN 220)
   * - ``registry_image``
     - ``registry:2``
     - Image Docker de la registry OCI interne
   * - ``registry_port``
     - ``5000``
     - Port de la registry (accessible sur VLAN 420)
   * - ``registry_data_dir``
     - ``/var/lib/registry``
     - Répertoire de stockage des images sur le controller
