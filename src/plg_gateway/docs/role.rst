Rôle
====

``plg_gateway`` configure la couche réseau Linux de l'ensemble du cluster
et le point d'accès WiFi optionnel.

.. image:: network-stack.svg
   :alt: Stack réseau KubeWI
   :align: center
   :target: network-stack.svg

----

Architecture réseau
--------------------

Chaque nœud porte un bridge Linux ``br0`` auquel les interfaces physiques
sont attachées. Trois VLANs 802.1Q communs à tous les nœuds :

.. list-table::
   :header-rows: 1
   :widths: 10 18 22 50

   * - VLAN
     - Interface
     - Sous-réseau
     - Domaine
   * - 220
     - ``br0.220``
     - ``192.168.22.0/24``
     - Infrastructure Kubernetes (API k0s, pod network, CoreDNS)
   * - 420
     - ``br0.420``
     - ``192.168.42.0/24``
     - Transferts (OCI registry, Vector, Loki, MinIO)
   * - 620
     - ``br0.620``
     - ``192.168.62.0/24``
     - Communications robotiques (ROS 2, Zenoh)

L'adresse IP de chaque nœud est calculée depuis ``host_id`` :

.. code-block:: yaml

   network_vlan_ips:
     "220": "192.168.22.{{ host_id }}/24"
     "420": "192.168.42.{{ host_id }}/24"
     "620": "192.168.62.{{ host_id }}/24"

----

Trois rôles, trois groupes
---------------------------

.. list-table::
   :header-rows: 1
   :widths: 18 18 64

   * - Rôle
     - Groupe
     - Périmètre
   * - ``network``
     - ``all``
     - Arrêt dhcpcd/NetworkManager, bridge ``br0``, VLANs
   * - ``gateway``
     - ``gateways``
     - Interface externe DHCP, NAT (``kubewi-nat.service``),
       DNS cluster (``systemd-resolved`` sur ``192.168.22.1``)
   * - ``internal``
     - ``all:!gateways``
     - Route par défaut ``192.168.22.1``, ``resolv.conf`` → ``192.168.22.1``

Le rôle ``internal`` nécessite que le rôle ``gateway`` soit déjà appliqué :
les workers pointent vers ``192.168.22.1`` comme gateway et DNS.

----

``plg_gateway`` configure le nœud physique qui sert de frontière entre le
LAN externe et les VLANs internes du cluster. Il met en place le NAT vers
l'extérieur, l'interface réseau externe en DHCP, les adresses IP des VLANs
sur le nœud gateway, et optionnellement un point d'accès WiFi bridgé sur le
VLAN 220 (``wifi_ap`` défini dans l'inventaire).

Un gateway est un controller k0s avec des responsabilités réseau
supplémentaires — ``plg_gateway`` ne gère que la couche réseau physique,
pas k0s lui-même.

----

Couches
-------

- ``playbooks/gateway.yml`` — applique les rôles ``network``, ``gateway``
  et ``wireguard`` sur le groupe ``gateways``
- ``playbooks/wifi.yml`` — applique le rôle ``hostapd`` (conditionné à
  ``wifi_ap`` défini dans l'inventaire)

**Rôle** ``gateway``
   - Déploie les fichiers ``systemd-networkd`` pour les VLANs du gateway
     (adresse IP seule, sans route par défaut)
   - Déploie l'interface externe (``network_external_iface``) en DHCP
   - Installe et active le service ``kubewi-nat`` (iptables MASQUERADE)
   - Configure ``systemd-resolved`` pour écouter sur le VLAN 220

**Rôle** ``hostapd``
   - Installe ``hostapd``
   - Crée le bridge ``br-wifi`` entre ``br0.220`` (VLAN 220) et ``wlan0``
   - Déploie ``/etc/hostapd/hostapd.conf``
   - Active et démarre le service

----

Dépendances
-----------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Paquet
     - Ce qui est utilisé
   * - ``adp_ansible``
     - exécution des playbooks via ``ansible.run_playbook()``
   * - ``plg_vpn``
     - le tunnel WireGuard doit être déployé pour que le gateway soit joignable
   * - ``ops_cluster``
     - le rôle ``network`` (bridge br0, VLANs) doit avoir été appliqué avant
