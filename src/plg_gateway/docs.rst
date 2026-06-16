Plugin Gateway
==============

.. list-table::
   :widths: 20 80
   :stub-columns: 1

   * - Paquet
     - ``plg_gateway``
   * - Type
     - ``plugin``
   * - Dépendances
     - :doc:`/src/adp_ansible/docs` · :doc:`/src/plg_vpn/docs` · :doc:`/src/ops_cluster/docs`

Brique de base du cluster — NAT, routage, VLANs et point d'accès WiFi du nœud gateway.

----

Rôle
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

----

Couches
-------

**Ansible** ``playbooks/`` + ``roles/``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``playbooks/gateway.yml`` — applique les rôles ``network``, ``gateway``
  et ``wireguard`` sur le groupe ``gateways``
- ``playbooks/wifi.yml`` — applique le rôle ``hostapd`` (conditionné à
  ``wifi_ap`` défini dans l'inventaire)

**Rôle** ``gateway``
   - Déploie les fichiers ``systemd-networkd`` pour les VLANs du gateway
     (adresse IP seule, sans route par défaut — le gateway n'est pas un
     simple worker)
   - Déploie l'interface externe (``network_external_iface``) en DHCP
   - Installe et active le service ``kubewi-nat`` (iptables MASQUERADE)
   - Configure ``systemd-resolved`` pour écouter sur le VLAN 220
     (forwardeur DNS pour les workers)

**Rôle** ``hostapd``
   - Installe ``hostapd``
   - Crée le bridge ``br-wifi`` et y attache ``br0.220`` (VLAN 220)
     et ``wlan0`` — les clients WiFi arrivent directement sur le VLAN 220
   - Déploie ``/etc/hostapd/hostapd.conf`` depuis le template
   - Active et démarre le service

----

Commandes CLI
-------------

.. code-block:: text

   kubewi gateway deploy       déploie NAT, routage et VLANs du gateway
   kubewi gateway wifi-deploy  déploie le point d'accès WiFi hostapd

.. list-table::
   :header-rows: 1
   :widths: 42 58

   * - Commande
     - Usage
   * - ``kubewi gateway deploy``
     - Applique la configuration réseau complète du gateway (NAT, VLANs,
       interface externe). Idempotent.
   * - ``kubewi gateway wifi-deploy``
     - Installe et configure hostapd. Nécessite ``wifi_ap`` dans
       ``inventory/hosts.yml``. À lancer après ``deploy``.

----

Variables
---------

.. list-table::
   :header-rows: 1
   :widths: 38 22 40

   * - Variable
     - Défaut
     - Description
   * - ``network_external_iface``
     - *(requis)*
     - Interface WAN du gateway (ex. ``eth0``)
   * - ``network_cluster_dns``
     - ``192.168.22.1``
     - IP du forwardeur DNS sur VLAN 220
   * - ``wifi_ap.iface``
     - *(optionnel)*
     - Interface WiFi (ex. ``wlan0``). Absent = pas d'AP.
   * - ``wifi_ap.bridge``
     - ``br-wifi``
     - Bridge dédié entre ``br0.220`` et ``wlan0``
   * - ``wifi_ap.vlan_id``
     - ``220``
     - VLAN sur lequel les clients WiFi arrivent
   * - ``wifi_ap.ssid``
     - *(requis si wifi_ap)*
     - SSID du réseau WiFi
   * - ``wifi_ap.passphrase``
     - *(requis si wifi_ap)*
     - Passphrase WPA2 (depuis vault)
   * - ``wifi_ap.hw_mode``
     - ``g``
     - Bande radio : ``g`` = 2.4 GHz, ``a`` = 5 GHz
   * - ``wifi_ap.channel``
     - ``6``
     - Canal WiFi

----

Implémentation
--------------

Le rôle ``gateway`` génère des fichiers ``systemd-networkd`` spécifiques
au gateway pour les VLANs qui ont un champ ``gateway:`` dans
``network_vlans``. Ces fichiers assignent l'IP sans route par défaut —
contrairement aux workers, le gateway route lui-même via ``kubewi-nat``.

Quand ``wifi_ap`` est défini, le template ``vlan.network.j2`` du rôle
``gateway`` fait de ``br0.220`` un slave du bridge ``br-wifi`` (au lieu
de lui assigner une IP directement). C'est ``br-wifi`` qui porte alors
l'IP du VLAN 220. Les deux chemins sont dans le même template,
conditionnés par la présence de ``wifi_ap``.

Le rôle ``hostapd`` utilise ``bridge=br-wifi`` dans ``hostapd.conf`` :
hostapd ajoute automatiquement ``wlan0`` au bridge au moment de
l'association d'un client. Les clients WiFi sont donc sur le VLAN 220
au niveau L2, sans NAT ni routage supplémentaire.
