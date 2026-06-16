Commandes CLI
=============

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
