Variables
=========

.. list-table::
   :header-rows: 1
   :widths: 38 22 40

   * - Variable
     - Défaut
     - Description
   * - ``network_external_iface``
     - *(requis)*
     - Interface WAN du gateway (ex. ``eth0``)
   * - ``network_cluster_dns``
     - ``192.168.22.1``
     - IP du forwardeur DNS sur VLAN 220
   * - ``wifi_ap.iface``
     - *(optionnel)*
     - Interface WiFi (ex. ``wlan0``). Absent = pas d'AP.
   * - ``wifi_ap.bridge``
     - ``br-wifi``
     - Bridge dédié entre ``br0.220`` et ``wlan0``
   * - ``wifi_ap.vlan_id``
     - ``220``
     - VLAN sur lequel les clients WiFi arrivent
   * - ``wifi_ap.ssid``
     - *(requis si wifi_ap)*
     - SSID du réseau WiFi
   * - ``wifi_ap.passphrase``
     - *(requis si wifi_ap)*
     - Passphrase WPA2 (depuis vault)
   * - ``wifi_ap.hw_mode``
     - ``g``
     - Bande radio : ``g`` = 2.4 GHz, ``a`` = 5 GHz
   * - ``wifi_ap.channel``
     - ``6``
     - Canal WiFi
