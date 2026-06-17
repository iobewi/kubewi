Variables
=========

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

Les clés privées (``vault_vpn_controller_private_key``,
``vault_vpn_sdk_private_key``) sont dans ``inventory/group_vars/all/vault.yml``
et injectées via ``kubewi vpn generate-keys``.
