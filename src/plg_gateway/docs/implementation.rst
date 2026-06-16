Implémentation
==============

Le rôle ``gateway`` génère des fichiers ``systemd-networkd`` spécifiques
au gateway pour les VLANs qui ont un champ ``gateway:`` dans
``network_vlans``. Ces fichiers assignent l'IP sans route par défaut —
contrairement aux workers, le gateway route lui-même via ``kubewi-nat``.

Quand ``wifi_ap`` est défini, le template ``vlan.network.j2`` bascule
``br0.220`` en slave de ``br-wifi`` au lieu de lui assigner une IP.
Les deux chemins coexistent dans le même template via un conditionnel Jinja2 :

.. code-block:: jinja

   [Network]
   LinkLocalAddressing=no
   IPv4SendRedirects=no
   {% if wifi_ap is defined and wifi_ap.vlan_id == item.id %}
   Bridge={{ wifi_ap.bridge }}
   {% elif network_vlan_ips is defined and item.id | string in network_vlan_ips %}
   Address={{ network_vlan_ips[item.id | string] }}
   {% endif %}

Ce design permet de déployer gateway avec ou sans WiFi AP avec le même
playbook — le comportement est piloté exclusivement par la présence ou
l'absence de ``wifi_ap`` dans ``hosts.yml``.

Le rôle ``hostapd`` utilise ``bridge=br-wifi`` dans ``hostapd.conf`` :
hostapd ajoute automatiquement ``wlan0`` au bridge lors de l'association
d'un client. Les clients WiFi arrivent directement sur le VLAN 220 (L2 pur),
sans NAT ni sous-réseau dédié.
