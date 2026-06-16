Rôle
====

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
