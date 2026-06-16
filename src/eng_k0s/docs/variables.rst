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
   * - ``k0s_pod_cidr``
     - ``10.244.0.0/16``
     - CIDR réseau pods
   * - ``k0s_service_cidr``
     - ``10.96.0.0/12``
     - CIDR services Kubernetes
   * - ``k0s_cilium_version``
     - *(dernière stable)*
     - Version Cilium déployée via l'extension helm k0s

Paramètres k0s controller (``/etc/k0s/k0s.yaml``)
---------------------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Paramètre
     - Valeur
   * - ``api.address``
     - ``192.168.22.1`` (VLAN 220)
   * - ``api.port``
     - ``6443``
   * - ``network.provider``
     - ``custom`` (Cilium gère le dataplane)
   * - ``network.podCIDR``
     - ``10.244.0.0/16``
   * - ``network.serviceCIDR``
     - ``10.96.0.0/12``
