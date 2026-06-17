Implémentation
==============

Le Deployment ``dnsmasq-provisioning`` utilise ``hostNetwork: true`` et
un ``nodeSelector`` sur ``control-plane`` pour s'exécuter sur le
controller, qui est le seul nœud connecté au switch de provisioning.
