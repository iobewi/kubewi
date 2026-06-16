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

Les clés WireGuard sont générées et injectées automatiquement dans
l'inventaire et le vault via :

.. code-block:: bash

   make ansible-wireguard-keys

Cette commande génère deux paires de clés (controller et SDK), injecte
les **clés publiques** dans ``inventory/hosts.yml`` et les **clés privées**
dans ``inventory/group_vars/all/vault.yml``.

Chiffrer le vault après injection :

.. code-block:: bash

   make ansible-vault-encrypt

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

Une fois le tunnel actif, configurer ``~/.ssh/config`` (une seule fois,
ou après rebuild du container SDK) :

.. code-block:: bash

   make ssh-config

Le controller est ensuite joignable par son nom :

.. code-block:: bash

   ssh controller-01

SSH vers un worker (via ProxyJump)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Les workers ne sont pas directement exposés. ``make ssh-config`` configure
automatiquement un ProxyJump via le controller pour tout le sous-réseau
``192.168.22.*`` :

.. code-block:: bash

   ssh iobewi@192.168.22.10

Pour une connexion SSH manuelle sans ``~/.ssh/config`` :

.. code-block:: bash

   ssh -J iobewi@10.0.100.1 iobewi@192.168.22.10

Ansible via le tunnel
~~~~~~~~~~~~~~~~~~~~~

Une fois le tunnel actif, tous les playbooks Ansible fonctionnent
sans configuration supplémentaire — l'inventaire utilise déjà les IPs
WireGuard et VLAN :

.. code-block:: bash

   ansible all -i inventory/hosts.yml -m ping
   ansible-playbook -i inventory/hosts.yml playbooks/stack.yml
