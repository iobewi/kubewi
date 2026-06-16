Engine WireGuard
================

.. list-table::
   :widths: 20 80
   :stub-columns: 1

   * - Paquet
     - ``eng_wireguard``
   * - Type
     - ``engine``
   * - Dépendances
     - :doc:`/src/adp_ansible/docs`

Engine WireGuard — install, configure et cycle de vie du tunnel sur les nœuds.

----

Rôle
----

``eng_wireguard`` installe et configure WireGuard sur les controllers pour
établir un tunnel VPN permanent entre le SDK de développement et le cluster.
Il génère la configuration cliente SDK localement dans ``work/wg0-sdk.conf``
(gitignored — contient la clé privée SDK).

C'est l'implémentation concrète de la brique VPN : ``plg_vpn`` s'appuie sur
cet engine pour le cycle de vie du tunnel côté SDK (``wg-quick up/down``).

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

----

Couches
-------

**Ansible** ``playbooks/`` + ``roles/``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``playbooks/wireguard.yml`` — applique le rôle sur le groupe ``controllers``
- ``roles/wireguard/tasks/main.yml`` — délègue vers ``controller.yml`` et ``sdk_config.yml``
- ``roles/wireguard/tasks/controller.yml`` — install paquet, IP forwarding,
  déploiement ``wg0.conf``, activation ``wg-quick@wg0``
- ``roles/wireguard/tasks/sdk_config.yml`` — génère ``work/wg0-sdk.conf``
  localement depuis le template ``wg0-sdk.conf.j2``

----

Commandes CLI
-------------

.. code-block:: text

   kubewi wireguard deploy   installe et configure WireGuard sur les controllers

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Commande
     - Usage
   * - ``kubewi wireguard deploy``
     - Déploie WireGuard sur tous les controllers et régénère ``work/wg0-sdk.conf``

----

Variables
---------

.. list-table::
   :header-rows: 1
   :widths: 38 28 34

   * - Variable
     - Défaut
     - Description
   * - ``controller_endpoint``
     - ``{{ inventory_hostname }}.local``
     - Endpoint mDNS du controller. Surcharger si IP fixe ou DDNS.
   * - ``wireguard_interface``
     - ``wg0``
     - Nom de l'interface WireGuard
   * - ``wireguard_port``
     - ``51820``
     - Port UDP WireGuard
   * - ``wireguard_controller_ip``
     - ``10.0.100.1``
     - IP WireGuard du controller (pair serveur)
   * - ``wireguard_sdk_ip``
     - ``10.0.100.2``
     - IP WireGuard du SDK (pair client)
   * - ``wireguard_allowed_vlans``
     - ``192.168.22/42/62.0/24``
     - Sous-réseaux VLAN routés dans le tunnel

Les clés privées (``vault_wg_controller_private_key``,
``vault_wg_sdk_private_key``) sont dans ``inventory/group_vars/all/vault.yml``
et injectées via ``kubewi ansible wireguard-keys``.

----

Implémentation
--------------

Le tunnel est asymétrique : le controller est serveur (``ListenPort``),
le SDK est client (``Endpoint`` pointant vers le controller via mDNS ou IP fixe).

``controller_endpoint`` utilise mDNS (``<hostname>.local``) par défaut pour
rester stable même avec une IP DHCP changeante — ``avahi-daemon`` doit être
actif sur le controller (garanti par ``eng_debian``).

``work/wg0-sdk.conf`` est généré par ``delegate_to: localhost`` dans
``sdk_config.yml`` : Ansible s'exécute côté controller pour lire les variables
vault, mais écrit le fichier sur la machine de contrôle. Ce fichier ne transite
jamais par le réseau chiffré, il est produit en local.

Le playbook est idempotent : relancer ``kubewi wireguard deploy`` sur un
controller déjà configuré ne produit aucun effet si les clés et la config
sont identiques. Il régénère systématiquement ``work/wg0-sdk.conf``.
