Implémentation
==============

Modèle projet
-------------

Un **projet kubewi** est un répertoire autonome identifié par un fichier
marqueur ``.kubewi-project``. Il contient toute la configuration locale
d'un cluster et est indépendant du code source de kubewi.

``kubewi._project.resolve()`` détermine le projet actif selon la priorité :

1. Variable d'environnement ``KUBEWI_PROJECT``
2. Répertoire courant (présence du marqueur ``.kubewi-project``)
3. Erreur explicite avec message d'aide

``kubewi cluster inventory-init <nom>`` crée le répertoire projet, pose le
marqueur, et copie les templates ``hosts.yml`` et ``vault.yml`` depuis
``adp_ansible/inventory/``. Toutes les commandes suivantes résolvent
automatiquement le projet actif sans paramètre supplémentaire.

Cycle de vie déclaratif
-----------------------

``cluster.yaml`` est un fichier déclaratif versionnable qui décrit l'état
désiré du cluster : profils matériel (``host_profiles``), groupes de rôles
(``role_groups``) et nœuds. ``kubewi cluster status`` compare cet état
désiré avec ``hosts.yml`` (nœuds enrollés) et affiche les delta.

``kubewi cluster apply`` itère les nœuds manquants dans l'ordre :
controllers d'abord (ils doivent être prêts avant les workers). Pour chaque
worker, il active le DHCP de provisioning, attend la détection, lance le
bootstrap et le provisioning k0s, puis désactive le DHCP.

L'enrollment est interruptible (``Ctrl+C``) et reprise possible : les nœuds
déjà enrollés sont détectés via ``hosts.yml`` et ignorés au prochain ``apply``.

``cluster init`` inspecte dynamiquement les paquets installés pour lister les
OS disponibles et les rôles Ansible déployables — la liste dans le fichier
généré reflète l'état réel de l'installation.
