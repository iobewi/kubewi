Implémentation
==============

Le rôle ``gateway`` génère des fichiers ``systemd-networkd`` spécifiques
au gateway pour les VLANs qui ont un champ ``gateway:`` dans
``network_vlans``. Ces fichiers assignent l'IP sans route par défaut —
contrairement aux workers, le gateway route lui-même via ``kubewi-nat``.

Quand ``wifi_ap`` est défini, le template ``vlan.network.j2`` fait de
``br0.220`` un slave du bridge ``br-wifi`` (au lieu de lui assigner une IP).
C'est ``br-wifi`` qui porte l'IP du VLAN 220. Les deux chemins sont dans
le même template, conditionnés par la présence de ``wifi_ap``.

Le rôle ``hostapd`` utilise ``bridge=br-wifi`` dans ``hostapd.conf`` :
hostapd ajoute automatiquement ``wlan0`` au bridge à l'association d'un
client. Les clients WiFi sont sur le VLAN 220 au niveau L2, sans NAT ni
routage supplémentaire.
