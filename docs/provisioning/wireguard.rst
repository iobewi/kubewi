Accès distant
=============

Le SDK de développement s'exécute hors des VLANs du cluster. L'interface
``eth0`` du controller porte une adresse DHCP sur le LAN local, et les workers
ne sont joignables que via les VLANs internes (``192.168.22.0/24``, etc.).

Un tunnel VPN `WireGuard <https://www.wireguard.com/>`_ est établi entre le SDK
et le controller, avec des adresses fixes indépendantes du DHCP. Le controller
fait office de passerelle : toutes les VLANs du cluster deviennent accessibles
depuis le SDK à travers le tunnel.

.. contents:: Sections
   :local:
   :depth: 1

----

Architecture
------------

.. code-block:: text

   LAN local
   ├── SDK               (eth0 DHCP)     ──wg0──► 10.0.100.2/24
   └── controller-01     (eth0 DHCP)
           │  wg0: 10.0.100.1/24
           │  MASQUERADE → br0
           ├── VLAN 220  192.168.22.0/24  (Kubernetes)
           ├── VLAN 420  192.168.42.0/24  (Data)
           └── VLAN 620  192.168.62.0/24  (ROS2)

Le controller est joignable sur le LAN via mDNS (``controller-01.local``),
ce qui le rend stable même avec une adresse DHCP changeante. ``avahi-daemon``
doit être actif sur le controller — c'est garanti par le rôle ``system``.

Les workers ne sont pas exposés directement au SDK. Ansible les atteint via
un ProxyJump SSH sur le controller (configuré dans ``inventory/hosts.yml``).

.. list-table::
   :header-rows: 1
   :widths: 25 25 50

   * - Nœud
     - IP WireGuard
     - Rôle dans le tunnel
   * - controller-01
     - ``10.0.100.1``
     - Serveur WireGuard, passerelle vers les VLANs
   * - SDK
     - ``10.0.100.2``
     - Client WireGuard

----

Rôle Ansible
------------

| Rôle : `roles/wireguard <https://github.com/iobewi/kubewi/blob/main/ansible/roles/wireguard>`_
| Playbook : `playbooks/wireguard.yml <https://github.com/iobewi/kubewi/blob/main/ansible/playbooks/wireguard.yml>`_

Le rôle s'applique uniquement aux controllers. Il effectue :

- installation du paquet ``wireguard`` ;
- activation de l'IP forwarding (``net.ipv4.ip_forward``) ;
- déploiement de ``/etc/wireguard/wg0.conf`` depuis le template ;
- activation du service ``wg-quick@wg0`` au démarrage ;
- génération de la configuration cliente SDK en local (``wireguard/wg0-sdk.conf``).

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Variable
     - Valeur par défaut
   * - ``wireguard_interface``
     - ``wg0``
   * - ``wireguard_port``
     - ``51820``
   * - ``wireguard_controller_ip``
     - ``10.0.100.1``
   * - ``wireguard_sdk_ip``
     - ``10.0.100.2``

----

Préparation des clés
--------------------

Les clés WireGuard doivent être générées avant le premier run Ansible.
Exécuter sur le controller (ou localement) :

.. code-block:: bash

   # Clés du controller
   wg genkey | tee controller.key | wg pubkey > controller.pub

   # Clés du SDK
   wg genkey | tee sdk.key | wg pubkey > sdk.pub

Renseigner ensuite les valeurs dans l'inventaire :

**``inventory/host_vars/controller-01.yml``** — clés publiques WireGuard :

.. code-block:: yaml

   wg_controller_pubkey: "<contenu de controller.pub>"
   wg_sdk_pubkey: "<contenu de sdk.pub>"

**``inventory/group_vars/vault.yml``** — clés privées et credentials (à chiffrer) :

.. code-block:: yaml

   vault_wifi_ssid: "nom-du-reseau"
   vault_wifi_psk: "mot-de-passe-wifi"
   vault_wg_controller_private_key: "<contenu de controller.key>"
   vault_wg_sdk_private_key: "<contenu de sdk.key>"

Chiffrer le vault :

.. code-block:: bash

   ansible-vault encrypt inventory/group_vars/vault.yml

Supprimer les fichiers de clés en clair après intégration :

.. code-block:: bash

   rm controller.key controller.pub sdk.key sdk.pub

----

Déploiement
-----------

WireGuard est déployé automatiquement lors de l'initialisation du controller
via ``playbooks/init.yml`` (voir :doc:`system`). Il n'est pas nécessaire de
l'exécuter manuellement lors du premier run.

Pour redéployer uniquement WireGuard sur un controller déjà accessible via
le tunnel :

.. code-block:: bash

   ansible-playbook -i inventory/hosts.yml playbooks/wireguard.yml --ask-vault-pass

Le playbook régénère ``wireguard/wg0-sdk.conf`` à chaque exécution.

----

Connexion au serveur
--------------------

Activer le tunnel depuis le SDK
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Le fichier ``wireguard/wg0-sdk.conf`` est généré localement par Ansible
lors du provisioning. Le tunnel se monte directement depuis ce fichier
sans copie dans ``/etc`` :

.. code-block:: bash

   make vpn-up

Pour couper le tunnel :

.. code-block:: bash

   make vpn-down

Vérifier que le tunnel est établi :

.. code-block:: bash

   wg show wireguard/wg0-sdk.conf

La sortie doit afficher le peer ``controller-01`` avec un ``latest handshake``
récent et des octets échangés.

Tester la connectivité :

.. code-block:: bash

   ping 10.0.100.1      # controller
   ping 192.168.22.10   # worker via VLAN 220

SSH direct vers le controller
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Une fois le tunnel actif, le controller est joignable via son IP WireGuard :

.. code-block:: bash

   ssh iobewi@10.0.100.1

SSH vers un worker (via ProxyJump)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Les workers ne sont pas directement exposés. L'inventaire Ansible configure
un ProxyJump automatique via le controller. Pour une connexion SSH manuelle :

.. code-block:: bash

   ssh -J iobewi@10.0.100.1 iobewi@192.168.22.10

Ou en ajoutant une entrée dans ``~/.ssh/config`` :

.. code-block:: text

   Host worker-*
       User iobewi
       ProxyJump iobewi@10.0.100.1

   Host worker-motion-01
       HostName 192.168.22.10

   Host worker-perception-01
       HostName 192.168.22.11

   Host worker-edge-01
       HostName 192.168.22.12

Ansible via le tunnel
~~~~~~~~~~~~~~~~~~~~~

Une fois le tunnel actif, tous les playbooks Ansible fonctionnent
sans configuration supplémentaire — l'inventaire utilise déjà les IPs
WireGuard et VLAN :

.. code-block:: bash

   ansible all -i inventory/hosts.yml -m ping
   ansible-playbook -i inventory/hosts.yml playbooks/stack.yml
