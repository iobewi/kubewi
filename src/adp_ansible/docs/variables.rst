Variables
=========

Variables communes (``group_vars/all/main.yml``)
-------------------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 40 20 40

   * - Variable
     - Défaut
     - Description
   * - ``ansible_become``
     - ``true``
     - Escalade sudo activée globalement
   * - ``ansible_become_method``
     - ``sudo``
     - Méthode d'escalade
   * - ``ansible_user``
     - ``iobewi``
     - Utilisateur SSH
   * - ``timezone``
     - ``Europe/Paris``
     - Timezone système
   * - ``ntp_servers``
     - ``[0.fr.pool.ntp.org, …]``
     - Serveurs NTP (chrony)
   * - ``network_vlans``
     - ``[{id: 220}, {id: 420}, {id: 620}]``
     - VLANs déployés sur tous les nœuds

Variables Kubernetes (``group_vars/kubernetes.yml``)
-----------------------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 40 20 40

   * - Variable
     - Défaut
     - Description
   * - ``k0s_version``
     - *(latest)*
     - Version k0s — si vide, dernière release stable
   * - ``k0s_cilium_version``
     - *(latest)*
     - Version Cilium (extension helm k0s)
   * - ``k0s_pod_cidr``
     - ``10.244.0.0/16``
     - CIDR pods
   * - ``k0s_service_cidr``
     - ``10.96.0.0/12``
     - CIDR services

Variables par nœud (``hosts.yml``)
------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 38 62

   * - Variable
     - Description
   * - ``ansible_host``
     - IP WireGuard du nœud (``10.0.100.x``) pour les controllers,
       IP VLAN 220 (``192.168.22.x``) pour les workers
   * - ``init_host``
     - IP DHCP temporaire (``192.168.0.x``) — utilisée uniquement lors
       du bootstrap initial (Phase 1 workers, premier run controller)
   * - ``host_id``
     - Dernier octet de l'IP VLAN 220 — détermine les IPs sur tous les VLANs
   * - ``network_bridge_members``
     - Interfaces réseau attachées au bridge ``br0``
   * - ``network_external_iface``
     - Interface externe (gateways uniquement — ex. ``enp2s0``)
   * - ``wireguard_public_key``
     - Clé publique WireGuard du nœud (injectée par ``kubewi vpn generate-keys``)
