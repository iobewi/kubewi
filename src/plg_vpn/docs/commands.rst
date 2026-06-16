Commandes CLI
=============

.. code-block:: text

   kubewi vpn up              monte le tunnel WireGuard SDK ↔ cluster
   kubewi vpn down            coupe le tunnel
   kubewi vpn generate-keys   génère et injecte les clés dans le vault
   kubewi vpn deploy          déploie WireGuard sur le controller

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Commande
     - Usage
   * - ``kubewi vpn up``
     - Monte le tunnel via ``wg-quick up work/wg0-sdk.conf``.
   * - ``kubewi vpn down``
     - Coupe le tunnel via ``wg-quick down``.
   * - ``kubewi vpn generate-keys``
     - Génère la paire de clés WireGuard et l'injecte dans ``vault.yml``.
   * - ``kubewi vpn deploy``
     - Applique le rôle ``wireguard`` sur le controller via ``eng_wireguard``.

Ordre habituel lors de la mise en service initiale :

.. code-block:: bash

   kubewi vpn generate-keys   # 1 — génère les clés
   kubewi vpn deploy          # 2 — configure le controller
   kubewi vpn up              # 3 — monte le tunnel depuis le SDK
