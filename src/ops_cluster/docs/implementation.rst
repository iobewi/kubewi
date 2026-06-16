Implémentation
==============

``cluster.yaml`` est un fichier déclaratif versionnable qui décrit l'état
désiré du cluster : profils matériel (``host_profiles``), groupes de rôles
(``role_groups``) et nœuds. ``kubewi cluster status`` compare cet état
désidé avec ``hosts.yml`` (nœuds enrollés) et affiche les delta.

``kubewi cluster apply`` itère les nœuds manquants dans l'ordre :
controllers d'abord (ils doivent être prêts avant les workers). Pour chaque
worker, il active le DHCP de provisioning, attend la détection, lance le
bootstrap et le provisioning k0s, puis désactive le DHCP.

L'enrollment est interruptible (``Ctrl+C``) et reprise possible : les nœuds
déjà enrollés sont détectés via ``hosts.yml`` et ignorés au prochain ``apply``.

``cluster init`` inspecte dynamiquement les paquets installés pour lister les
OS disponibles et les rôles Ansible déployables — la liste dans le fichier
généré reflète l'état réel de l'installation.
