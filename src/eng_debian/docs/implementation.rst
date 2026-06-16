Implémentation
==============

Le swap est désactivé de façon permanente (commentaire dans ``/etc/fstab``
et ``swapoff -a``) — k0s refuse de démarrer si le swap est actif.
``eng_rpios`` complète cette désactivation avec zram swap pour les RPi.

``avahi-daemon`` est installé sur tous les nœuds pour que les hostnames
soient résolvables sur le LAN via mDNS (``<nom>.local``). C'est ce qui
permet à ``eng_wireguard`` d'utiliser ``controller_endpoint`` sans IP fixe.

Le rôle est idempotent : relancer ``kubewi debian provision`` sur un nœud
déjà configuré ne produit aucun changement si l'état correspond.
