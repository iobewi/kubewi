Configuration système
======================

Cette configuration s'applique à tous les nœuds du cluster,
indépendamment de leur rôle Kubernetes.

.. contents:: Sections
   :local:
   :depth: 1

Premier run
-----------

Séquence à suivre pour un premier déploiement sur nœud vierge.

**1. Installer les collections requises**

.. code-block:: bash

   cd ansible
   ansible-galaxy collection install -r requirements.yml

**2. Renseigner l'inventaire**

Éditer ``inventory/hosts.yml`` : adresses IP et users de connexion
de chaque nœud.

**3. Bootstrap : clé SSH et sudo sans mot de passe**

Le flux officiel utilise ``playbooks/bootstrap.yml``. Ce playbook prépare
l'accès SSH par clé et configure le sudo sans mot de passe. Les playbooks
suivants doivent pouvoir être exécutés sans mot de passe interactif.

Cette étape est à exécuter **une seule fois** par nœud.

.. code-block:: bash

   ansible-playbook -i inventory/hosts.yml playbooks/bootstrap.yml --ask-pass --ask-become-pass

Ansible demande deux mots de passe :

- ``SSH password`` : pour la connexion initiale
- ``BECOME password`` : pour l'escalade sudo

Après ce run, l'accès SSH par clé est actif et sudo est sans mot de passe
sur tous les nœuds.

**4. Vérifier la connectivité**

.. code-block:: bash

   ansible all -i inventory/hosts.yml -m ping

----

OS
--

| Rôle : `roles/system/tasks/os.yml <https://github.com/iobewi/kubewi/blob/main/ansible/roles/system/tasks/os.yml>`_

Le rôle configure les éléments suivants sur chaque nœud :

- **hostname** : positionné depuis le nom d'hôte déclaré dans l'inventaire
- **timezone** : configurable via la variable ``timezone`` (défaut : ``Europe/Paris``)
- **paquets de base** : ``curl``, ``vim``, ``ca-certificates``, ``apt-transport-https``, ``gnupg``
- **swap désactivé** : requis par Kubernetes (runtime et ``/etc/fstab``)
- **modules noyau** : ``overlay`` et ``br_netfilter`` chargés au démarrage
- **paramètres sysctl** : forwarding IPv4 et filtrage bridge activés

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Paramètre sysctl
     - Valeur
   * - ``net.ipv4.ip_forward``
     - ``1``
   * - ``net.bridge.bridge-nf-call-iptables``
     - ``1``
   * - ``net.bridge.bridge-nf-call-ip6tables``
     - ``1``

----

systemd
-------

| Rôle : `roles/system/tasks/systemd.yml <https://github.com/iobewi/kubewi/blob/main/ansible/roles/system/tasks/systemd.yml>`_

La taille des journaux systemd est limitée pour préserver l'espace disque
sur les nœuds embarqués :

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Paramètre
     - Valeur
   * - ``SystemMaxUse``
     - ``500M``
   * - ``RuntimeMaxUse``
     - ``100M``

----

SSH
---

| Rôle : `roles/system/tasks/ssh.yml <https://github.com/iobewi/kubewi/blob/main/ansible/roles/system/tasks/ssh.yml>`_
| Template : `roles/system/templates/sshd_config.j2 <https://github.com/iobewi/kubewi/blob/main/ansible/roles/system/templates/sshd_config.j2>`_

Une configuration sshd durcie est déployée via template sur chaque nœud.
L'authentification par mot de passe est désactivée : seule l'authentification
par clé est autorisée.

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Paramètre
     - Valeur
   * - ``PasswordAuthentication``
     - ``no``
   * - ``PermitRootLogin``
     - ``no``
   * - ``MaxAuthTries``
     - ``3``
   * - ``LoginGraceTime``
     - ``30``
   * - ``ClientAliveInterval``
     - ``300``
   * - ``ClientAliveCountMax``
     - ``2``

Ces valeurs sont surchargeables via les variables du rôle (``ssh_*``).

----

chrony
------

| Rôle : `roles/system/tasks/chrony.yml <https://github.com/iobewi/kubewi/blob/main/ansible/roles/system/tasks/chrony.yml>`_
| Template : `roles/system/templates/chrony.conf.j2 <https://github.com/iobewi/kubewi/blob/main/ansible/roles/system/templates/chrony.conf.j2>`_

chrony est installé et configuré comme client NTP. Les sources de
synchronisation sont déclarées dans ``inventory/group_vars/all.yml``
via la variable ``ntp_servers``.

Le service est activé et démarré au boot. La synchronisation est
vérifiable avec :

.. code-block:: bash

   chronyc tracking
   chronyc sources

----

Container runtime
-----------------

| Rôle : `roles/system/tasks/containerd.yml <https://github.com/iobewi/kubewi/blob/main/ansible/roles/system/tasks/containerd.yml>`_
| Template : `roles/system/templates/containerd-config.toml.j2 <https://github.com/iobewi/kubewi/blob/main/ansible/roles/system/templates/containerd-config.toml.j2>`_

containerd est installé depuis les paquets de la distribution.
La configuration déployée active le driver cgroup systemd
(``SystemdCgroup = true``), requis pour le bon fonctionnement de k0s
avec cgroup v2.

Le service est activé et démarré au boot.

----

Exécution
---------

Une fois l'inventaire renseigné et la connectivité vérifiée, simuler
le playbook pour contrôler les changements attendus :

.. code-block:: bash

   ansible-playbook -i inventory/hosts.yml playbooks/system.yml --check --diff

Puis appliquer :

.. code-block:: bash

   ansible-playbook -i inventory/hosts.yml playbooks/system.yml
