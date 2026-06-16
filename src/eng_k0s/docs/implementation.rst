Implémentation
==============

L'enrollment worker se déroule en deux phases distinctes pour une raison
réseau : lors de la Phase 1, le worker n'est accessible que via l'IP
provisioning (``192.168.0.x``). Une fois le bridge et les VLANs configurés
(fin de Phase 1), ``eth0`` est absorbée dans ``br0`` — l'IP de provisioning
disparaît. La Phase 2 reprend via l'IP VLAN 220 (``192.168.22.x``).

Le token de jonction est récupéré par ``delegate_to: "{{ groups['controllers'][0] }}"``
dans le rôle ``k0s_worker/tasks/token.yml``. Ansible s'exécute côté controller
pour générer le token, puis l'écrit localement sur le worker cible. Aucun
transfert manuel n'est nécessaire.

La registry OCI interne tourne sur le controller (``registry:2``, port 5000,
VLAN 420). Chaque worker configure containerd pour accepter cette registry
sans TLS via ``/etc/k0s/containerd.d/registry.toml`` — déposé avant le
démarrage de k0s pour être pris en compte dès le premier pull.
