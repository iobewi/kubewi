Rôle
====

``eng_wireguard`` installe et configure WireGuard sur les controllers pour
établir un tunnel VPN permanent entre le SDK de développement et le cluster.

----

Architecture VPN
-----------------

.. code-block:: text

   LAN local
   ├── SDK               (eth0 DHCP)  ──wg0──►  10.0.100.2/24
   └── controller-01     (eth0 DHCP)
           │  wg0: 10.0.100.1/24
           │  MASQUERADE → br0
           ├── VLAN 220  192.168.22.0/24   (Kubernetes)
           ├── VLAN 420  192.168.42.0/24   (Data)
           └── VLAN 620  192.168.62.0/24   (ROS 2)

.. list-table::
   :header-rows: 1
   :widths: 25 25 50

   * - Nœud
     - IP WireGuard
     - Rôle
   * - ``controller-01``
     - ``10.0.100.1``
     - Serveur WireGuard, passerelle vers les VLANs
   * - SDK
     - ``10.0.100.2``
     - Client WireGuard

Le controller est joignable sur le LAN via mDNS (``controller-01.local``)
même avec une adresse DHCP changeante sur ``eth0``. C'est ``avahi-daemon``
(installé par ``eng_debian``) qui garantit cette résolution.

Les workers ne sont pas exposés directement au SDK — ils sont atteignables
via ProxyJump SSH à travers le controller (``kubewi ssh config``).

----

Il génère la configuration cliente SDK localement dans ``work/wg0-sdk.conf``
(gitignored — contient la clé privée SDK).

C'est l'implémentation concrète de la brique VPN : ``plg_vpn`` s'appuie sur
cet engine pour le cycle de vie du tunnel côté SDK (``wg-quick up/down``).

----

Couches
-------

- ``playbooks/wireguard.yml`` — applique le rôle sur le groupe ``controllers``
- ``roles/wireguard/tasks/controller.yml`` — install paquet, IP forwarding,
  déploiement ``wg0.conf``, activation ``wg-quick@wg0``
- ``roles/wireguard/tasks/sdk_config.yml`` — génère ``work/wg0-sdk.conf``
  localement depuis le template ``wg0-sdk.conf.j2``

----

Dépendances
-----------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Paquet
     - Ce qui est utilisé
   * - ``adp_ansible``
     - exécution du playbook via ``ansible.run_playbook()``
