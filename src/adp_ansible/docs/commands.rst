Commandes CLI
=============

.. code-block:: text

   kubewi ansible init            crée hosts.yml et vault.yml depuis les exemples
   kubewi ansible wifi            renseigne les credentials WiFi dans vault.yml
   kubewi ansible wireguard-keys  génère et injecte les clés WireGuard
   kubewi ansible vault-encrypt   chiffre vault.yml avec ansible-vault
   kubewi ansible vault-edit      édite le vault chiffré

.. list-table::
   :header-rows: 1
   :widths: 42 58

   * - Commande
     - Usage
   * - ``kubewi ansible init``
     - Copie les exemples vers les fichiers réels. À lancer une seule fois.
   * - ``kubewi ansible wifi``
     - Injecte ``ssid`` et ``psk`` dans ``vault.yml`` via prompt interactif.
   * - ``kubewi ansible wireguard-keys``
     - Génère deux paires de clés (controller + SDK) et les injecte.
   * - ``kubewi ansible vault-encrypt``
     - Chiffre ``vault.yml`` — à lancer après chaque injection de secrets.
   * - ``kubewi ansible vault-edit``
     - Ouvre le vault déchiffré dans ``$EDITOR`` pour modification manuelle.
