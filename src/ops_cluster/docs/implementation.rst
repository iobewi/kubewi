Implémentation
==============

Modèle projet
-------------

Un **projet kubewi** est un répertoire autonome identifié par un fichier
marqueur ``.kubewi-project``. ``kubewi._project.resolve()`` le localise via :

1. Variable d'environnement ``KUBEWI_PROJECT``
2. Répertoire courant (présence du marqueur)
3. Erreur explicite avec message d'aide

Structure d'un projet :

.. code-block:: text

   mon-cluster/
   ├── .kubewi-project        # marqueur (contient le nom du cluster)
   ├── cluster.yml            # métadonnées : name + gateway
   ├── hosts/
   │   ├── controller-a3f1b2.yml   # un fichier par nœud, édité par l'utilisateur
   │   └── worker-88c240.yml
   ├── hosts.yml              # généré automatiquement — ne pas éditer
   ├── .kubewi/
   │   └── hosts.yml.hash     # cache SHA256 pour cluster apply
   └── group_vars/all/vault.yml

----

Fichiers host (``hosts/*.yml``)
--------------------------------

Chaque nœud est décrit par un fichier ``hosts/<nom>.yml`` indépendant.
Le champ ``name`` est le nom du nœud dans le cluster.

Controller gateway (nœud VPN, adresse ``.1`` sur tous les VLANs) :

.. code-block:: yaml

   kubewi:
     host:
       name: controller-a3f1b2
       ansible_host: 10.0.100.1       # IP WireGuard définitive
       ansible_user: iobewi
       plg_gateway:
         init_host: 192.168.100.96    # IP d'accès initial (DHCP LAN)
         network_bridge_members: [enp1s0, enp2s0]
       eng_k0s:
         role: controller

Worker (nommé via MAC) :

.. code-block:: yaml

   kubewi:
     host:
       name: worker-88c240
       ansible_host: 192.168.22.10    # IP VLAN 220 définitive
       ansible_user: iobewi
       plg_gateway:
         init_host: 192.168.0.10      # IP provisioning (192.168.0.x)
         network_bridge_members: [eth0, eth1]
       eng_k0s:
         role: worker

``cluster.yml`` ne contient que les métadonnées du cluster :

.. code-block:: yaml

   kubewi:
     cluster:
       name: mon-cluster
       gateway: controller-a3f1b2    # nœud VPN + adresse .1 sur tous les VLANs

----

Nommage basé sur la MAC
------------------------

Les nœuds sont nommés à partir des **3 derniers octets** de leur adresse MAC,
sans séparateur, en minuscules. Fonction ``kubewi._hostfile.mac_to_id()`` :

.. code-block:: python

   mac_to_id('28:94:01:88:c2:40')  # → '88c240'
   # → nom node  : worker-88c240
   # → fichier   : hosts/worker-88c240.yml

Ce nommage est stable : retirer un nœud du cluster ne crée pas de « trous »
dans la numérotation, et le même nœud reprend toujours le même nom.

Les adresses IP sur le VLAN 220 (``192.168.22.X``) restent séquentielles via
``next_host_id()``, indépendamment du nom du nœud.

----

``cluster create`` — bootstrap du gateway
------------------------------------------

1. Localise le fichier host du gateway (``cluster.yml → gateway`` ou premier
   fichier avec ``plg_gateway``).
2. Teste si la clé SSH est déjà acceptée (``BatchMode=yes``) ; si non, demande
   le mot de passe.
3. Exécute ``init.yml`` via Ansible.
4. Lit la MAC de l'interface principale via SSH
   (``cat /sys/class/net/<iface>/address``).
5. Renomme le fichier host et met à jour ``cluster.yml → gateway``.
6. Monte le tunnel VPN SDK (``plg_vpn``), attend que l'IP WireGuard soit
   joignable.
7. Exécute ``gateway.yml`` (configuration réseau définitive).

----

``cluster add worker`` — deux modes
-------------------------------------

**Mode auto** (aucun nom fourni) :

1. Active le réseau de provisioning (``plg_provisioning`` : deploy + scale 1).
2. Lance ``detect_phase(ifaces, single=True)`` — attend le premier bail DHCP
   dnsmasq, crée ``hosts/<nom>.yml`` avec le nommage MAC.
3. Désactive le provisioning (scale 0).
4. Régénère ``hosts.yml``.
5. Demande le mot de passe SSH (premier accès via réseau provisioning).
6. Exécute ``workers-init.yml`` (bootstrap réseau, accès via ``192.168.0.x``).
7. Exécute ``worker.yml`` (enrôlement k0s, accès via VLAN 220).

**Mode manuel** (``NAME`` fourni, ``hosts/<NAME>.yml`` existant) :

Saute les étapes 1-3, passe directement au bootstrap Ansible (étapes 4-7).

----

``cluster apply`` — hash cache
--------------------------------

À chaque appel, ``cluster apply`` régénère ``hosts.yml`` depuis ``hosts/*.yml``
et compare son SHA256 au fichier ``.kubewi/hosts.yml.hash``.

- Si le hash diffère → ``↻ Inventaire mis à jour`` est affiché et le cache est
  mis à jour. Cela indique qu'un nœud a été ajouté ou modifié.
- Si identique → aucun message, Ansible voit un inventaire stable.

Pour chaque nœud, ``_build_plan()`` teste la joignabilité sur le port 22
(``socket.create_connection``, timeout 3 s) :

- **en ligne** → controller : ``gateway.yml`` ; worker : ``worker.yml``
- **hors ligne** → bootstrap complet (même logique que ``cluster add``)

----

Sélection OS — rôles Ansible
------------------------------

``init.yml`` et ``gateway.yml`` détectent l'OS du nœud via deux conditions :

.. code-block:: yaml

   roles:
     - role: rpios
       when: eng_rpios is defined
     - role: ubuntu
       when: eng_rpios is not defined and ansible_distribution == 'Ubuntu'
     - role: debian
       when: eng_rpios is not defined and ansible_distribution == 'Debian'

``eng_rpios is defined`` est la détection la plus fiable pour Raspberry Pi OS,
car ``ansible_distribution`` retourne ``Debian`` pour RPiOS (même base).
Le rôle ``rpios`` importe ``debian`` puis ajoute les spécificités RPi
(cgroups, zram swap).

----

ProxyJump workers
------------------

Les workers ne sont pas directement joignables depuis le SDK. Ansible les
atteint via ProxyJump : SDK → WireGuard → controller → VLAN 220 → worker.

``generate_ansible_inventory()`` injecte automatiquement
``ansible_ssh_common_args`` dans le groupe ``workers`` :

.. code-block:: yaml

   workers:
     vars:
       ansible_ssh_common_args: >-
         -o ProxyJump=iobewi@10.0.100.1 -o StrictHostKeyChecking=no
