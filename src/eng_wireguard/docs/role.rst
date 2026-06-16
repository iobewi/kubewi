Rôle
====

``eng_wireguard`` installe et configure WireGuard sur les controllers pour
établir un tunnel VPN permanent entre le SDK de développement et le cluster.
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
