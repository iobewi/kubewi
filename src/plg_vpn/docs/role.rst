Rôle
====

``plg_vpn`` gère le tunnel WireGuard entre le poste développeur (SDK) et
le cluster. Il monte/coupe le tunnel via ``wg-quick``, génère les clés
WireGuard et délègue le déploiement de la configuration côté cluster à
``eng_wireguard``.

----

Couches
-------

- ``kubewi/commands.py`` — CLI (Python, wg-quick + délégation engines)
- ``work/wg0-sdk.conf`` — configuration WireGuard générée (gitignored)

----

Dépendances
-----------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Paquet
     - Ce qui est utilisé
   * - ``adp_ansible``
     - ``lib.run_make('wireguard-keys')`` pour la génération des clés
   * - ``eng_wireguard``
     - ``lib.deploy()`` pour le déploiement côté controller (import tardif)
