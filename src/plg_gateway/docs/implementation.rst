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

Forwarding inter-VLAN
---------------------

Les clients WiFi (VLAN 220) peuvent atteindre les VLANs internes (420, 620)
via le service ``kubewi-wifi-forward``, déployé par le rôle ``hostapd`` :

.. code-block:: ini

   # /etc/systemd/system/kubewi-wifi-forward.service
   ExecStart=/usr/sbin/iptables -A FORWARD -i br-wifi -j ACCEPT
   ExecStart=/usr/sbin/iptables -A FORWARD -o br-wifi -m conntrack \
       --ctstate ESTABLISHED,RELATED -j ACCEPT

La première règle autorise tout le trafic **sortant** de ``br-wifi`` vers
n'importe quel VLAN interne. La seconde autorise le trafic de **retour**
pour les connexions établies depuis le WiFi.

Le service dépend de ``kubewi-nat`` — il démarre après lui et s'arrête avant,
garantissant que les règles MASQUERADE sur ``eth0`` sont présentes avant
d'ouvrir le forwarding.

**Ce que le forwarding permet :**

.. list-table::
   :header-rows: 1
   :widths: 40 40 20

   * - Source
     - Destination
     - Résultat
   * - Client WiFi (192.168.22.x)
     - Registre OCI 192.168.42.1:5000
     - ✓ (adresse locale)
   * - Client WiFi (192.168.22.x)
     - Worker 192.168.42.x
     - ✓ (forwardé)
   * - Client WiFi (192.168.22.x)
     - Internet (via eth0)
     - ✓ (forwardé + MASQUERADE)
   * - VLAN interne → WiFi
     - Connexion établie
     - ✓ (ESTABLISHED/RELATED)
   * - VLAN interne → WiFi
     - Nouvelle connexion
     - ✗ (non autorisé)
