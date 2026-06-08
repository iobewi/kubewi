Worker node
============

Les workers hébergent les charges de travail Kubernetes. Chaque worker
rejoint le cluster via un token généré par le controller et communique
avec l'API server sur le VLAN 220.

.. contents:: Sections
   :local:
   :depth: 1

----

Réseau de provisioning
-----------------------

Un worker fraîchement installé n'a pas d'IP sur le réseau cluster.
Le controller expose un réseau de provisioning sur ``br0`` natif
(``192.168.0.0/24``) géré par un Deployment dnsmasq dans le namespace
``provisioning`` de Kubernetes.

Ce Deployment est **arrêté par défaut** (``replicas: 0``). Il ne s'active
que pendant l'enrollment d'un nouveau worker, soit automatiquement via
``make add-worker``, soit manuellement :

.. code-block:: bash

   make provisioning-on    # scale dnsmasq à 1

Une fois le worker branché sur le switch cluster, il obtient une IP
temporaire (``192.168.0.x``) qui permet le bootstrap Ansible via
ProxyJump à travers le controller.

Après provisioning, ``eth0`` devient membre du bridge (plus d'IP DHCP).
Le worker n'est accessible que via ses IPs VLAN (``192.168.22.x``, etc.).

----

Prérequis Raspberry Pi
-----------------------

| Rôle : `roles/system/tasks/os.yml <https://github.com/iobewi/kubewi/blob/main/ansible/roles/system/tasks/os.yml>`_

Sur Raspberry Pi, les cgroups mémoire ne sont pas activés par défaut dans
le bootloader. k0s les requiert. Le rôle système les active automatiquement
en modifiant ``/boot/firmware/cmdline.txt`` (ou ``/boot/cmdline.txt``) :

.. code-block:: text

   cgroup_memory=1 cgroup_enable=memory

Si cette ligne est modifiée, le nœud **redémarre automatiquement** avant
de poursuivre le provisioning (``ansible.builtin.reboot``).

Le rôle désactive également cloud-init sur chaque nœud :

.. code-block:: bash

   touch /etc/cloud/cloud-init.disabled

Cela empêche cloud-init de reconfigurer réseau ou utilisateurs lors des
redémarrages suivants.

----

Enrollment worker
------------------

**Prérequis :** k0s tourne sur le controller, le tunnel WireGuard et kubectl
sont configurés sur le SDK.

**1. Configurer le tunnel et kubectl sur le SDK** *(une seule fois)*

.. code-block:: bash

   make vpn-up
   make ssh-config
   make kubeconfig

``make kubeconfig`` récupère le kubeconfig k0s depuis le controller et
configure ``kubectl`` sur le SDK (contexte ``kubewi``).

.. code-block:: bash

   kubectl get nodes    # vérifier l'accès au cluster

**2. Enroller le ou les workers**

La commande ``make add-worker`` gère l'intégralité du processus :
activation du DHCP de provisioning, détection des baux dnsmasq, ajout
dans ``hosts.yml``, enrollment Ansible en deux phases, désactivation du
DHCP.

.. code-block:: bash

   make add-worker

Le script ``scripts/enroll.py`` :

1. Scale le Deployment ``dnsmasq-provisioning`` à 1 (``provisioning-on``)
2. Lit les baux dnsmasq en continu (tableau en temps réel)
3. Pour chaque nouveau bail détecté :

   - calcule le ``host_id`` = dernier octet de l'IP VLAN 220 attribuée
     (ex : ``worker-01`` → ``192.168.22.10`` → ``host_id=10``)
   - ajoute le nœud dans ``inventory/hosts.yml`` avec ``init_host``
     = IP provisioning (``192.168.0.x``)

4. ``[Entrée]`` pour terminer la détection (mode multi-nœud)
5. Demande de confirmation, puis lance les deux phases Ansible
6. Scale le Deployment à 0 en cas de succès (``provisioning-off``)

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Variable Makefile
     - Effet
   * - ``SINGLE=1``
     - Détecte un seul nœud, enrollment immédiat (``--yes`` implicite)
   * - ``YES=1``
     - Non-interactif, sans demande de confirmation (mode batch)
   * - ``IFACES=1``
     - Une seule interface réseau (``network_bridge_members: [eth0]``)
   * - ``INVENTORY_ONLY=1``
     - Ajoute uniquement dans ``hosts.yml``, sans lancer Ansible
   * - ``DRY_RUN=1``
     - Simule sans modifier ``hosts.yml`` ni lancer Ansible

Pour un seul nœud en mode entièrement automatique :

.. code-block:: bash

   make add-worker SINGLE=1

**3. Vérifier que les workers ont rejoint le cluster**

.. code-block:: bash

   kubectl get nodes

----

Phase 1 — Bootstrap réseau
---------------------------

| Playbook : `playbooks/workers-init.yml <https://github.com/iobewi/kubewi/blob/main/ansible/playbooks/workers-init.yml>`_

La Phase 1 s'exécute via l'IP de provisioning (``init_host``, ``192.168.0.x``).
Elle établit le socle système et réseau avant que le VLAN 220 soit opérationnel.

Séquence appliquée sur chaque worker :

1. **Bootstrap SSH** — déploiement de la clé Ansible, configuration sudo sans
   mot de passe (connexion initiale par mot de passe via ``-k``)
2. **Rôle** ``system`` — OS, cgroups RPi, cloud-init désactivé, modules noyau,
   sysctl, swap, SSH durci, chrony, containerd
3. **Rôle** ``network`` — désactivation dhcpcd/NetworkManager/networking,
   création bridge ``br0``, VLANs (220/420/620)
4. **Rôle** ``internal`` — route par défaut ``192.168.22.1`` sur VLAN 220,
   ``resolv.conf`` pointant vers ``192.168.22.1`` (DNS cluster)
5. Attente de disponibilité sur l'IP VLAN 220 (port 22, timeout 60 s)

À l'issue de la Phase 1, le worker est joignable via son IP VLAN 220
(``ansible_host``) et ``eth0`` est absorbée dans le bridge — le réseau de
provisioning n'est plus disponible sur ce nœud.

----

Phase 2 — Provisioning k0s
----------------------------

| Playbook : `playbooks/worker.yml <https://github.com/iobewi/kubewi/blob/main/ansible/playbooks/worker.yml>`_
| Rôle : `roles/k0s_worker <https://github.com/iobewi/kubewi/blob/main/ansible/roles/k0s_worker>`_

La Phase 2 s'exécute via le tunnel WireGuard (ProxyJump ``10.0.100.1``).

----

Hardware
--------

.. TODO: spécifications matérielles selon profil (Motion / Perception / Edge)

----

Installation k0s
----------------

| Rôle : `roles/k0s_install <https://github.com/iobewi/kubewi/blob/main/ansible/roles/k0s_install>`_

Le binaire k0s est installé via le rôle partagé ``k0s_install``, commun
au controller et aux workers — la version est ainsi garantie identique
sur l'ensemble du cluster.

La version est contrôlée par ``k0s_version`` dans
``inventory/group_vars/kubernetes.yml``. Si non définie, la dernière
release stable est installée automatiquement.

----

Registry OCI
------------

| Rôle : `roles/k0s_worker/tasks/registry_config.yml <https://github.com/iobewi/kubewi/blob/main/ansible/roles/k0s_worker/tasks/registry_config.yml>`_

La configuration containerd est déposée dans ``/etc/k0s/containerd.d/registry.toml``
avant le démarrage du service, afin que chaque worker accepte la registry
locale sans TLS (``192.168.42.1:5000``, VLAN 420).

----

Token de jonction
-----------------

| Rôle : `roles/k0s_worker/tasks/token.yml <https://github.com/iobewi/kubewi/blob/main/ansible/roles/k0s_worker/tasks/token.yml>`_

Le token de jonction est généré par le controller et sauvegardé dans
``/etc/k0s/worker-token``. Le rôle worker le récupère directement depuis
le controller via ``delegate_to`` (sans intervention manuelle) et l'écrit
localement sur chaque worker.

.. code-block:: yaml

   delegate_to: "{{ groups['controllers'][0] }}"

Le token est chiffré côté k0s et expire selon la politique du cluster.

----

Démarrage du service
--------------------

| Rôle : `roles/k0s_worker/tasks/service.yml <https://github.com/iobewi/kubewi/blob/main/ansible/roles/k0s_worker/tasks/service.yml>`_

k0s est installé comme service systemd (``k0sworker``), activé au boot.
Le rôle attend que le nœud apparaisse à l'état ``Ready`` dans le cluster
avant de passer au nœud suivant.

.. code-block:: bash

   k0s install worker --token-file /etc/k0s/worker-token

Le service démarre kubelet, containerd, et l'agent Cilium. Le nœud
rejoint le plan de contrôle via l'API server sur ``192.168.22.1:6443``
(VLAN 220).

----

Ré-application
--------------

Pour ré-appliquer la configuration k0s worker après une modification
(tunnel WireGuard actif) :

.. code-block:: bash

   make vpn-up
   ansible-playbook -i inventory/hosts.yml playbooks/worker.yml --check --diff
   ansible-playbook -i inventory/hosts.yml playbooks/worker.yml
