Configuration système
======================

Cette configuration s'applique à tous les nœuds du cluster,
indépendamment de leur rôle Kubernetes.

.. contents:: Sections
   :local:
   :depth: 1

.. _premier-run:

Premier run
-----------

Le premier run doit initialiser le controller avant que le tunnel WireGuard
ne soit disponible. Le playbook ``init.yml`` enchaîne les quatre étapes
nécessaires en utilisant l'IP DHCP de ``eth0`` comme point d'entrée temporaire.

**1. Installer les collections requises**

.. code-block:: bash

   cd ansible
   ansible-galaxy collection install -r requirements.yml

**2. Initialiser l'inventaire local**

Les fichiers ``hosts.yml`` et ``vault.yml`` ne sont pas versionnés.
Les générer depuis les exemples (depuis le répertoire ``ansible/``) :

.. code-block:: bash

   cd ansible
   make init

**3. Renseigner l'inventaire**

Éditer ``inventory/hosts.yml`` :

.. code-block:: yaml

   init_host: "192.168.x.x"    # IP DHCP courante de eth0 (visible sur le routeur)

Les autres valeurs (``ansible_host``, ``ansible_user``, interfaces)
correspondent à l'exemple fourni dans ``hosts.yml.example``.

**4. Renseigner le vault**

Deux commandes dédiées permettent de remplir ``vault.yml`` sans l'éditer
manuellement :

.. code-block:: bash

   make wifi             # credentials WiFi (prompt interactif)
   make wireguard-keys   # génère et injecte les clés WireGuard

Le vault peut être chiffré après remplissage (optionnel, fichier gitignore) :

.. code-block:: bash

   make vault-encrypt

Pour modifier le vault ultérieurement :

.. code-block:: bash

   make vault-edit

**5. Exécuter le playbook d'initialisation**

.. code-block:: bash

   ansible-playbook -i inventory/hosts.yml playbooks/init.yml \
     -k --ask-become-pass --ask-vault-pass

Ansible demande trois mots de passe :

- ``SSH password`` (``-k``) — connexion initiale par mot de passe
- ``BECOME password`` — escalade sudo
- ``Vault password`` — déchiffrement des clés WireGuard

Ce playbook s'exécute **une seule fois**. Il bootstrap le controller,
configure l'OS, le réseau et déploie WireGuard. Il génère également
``wireguard/wg0-sdk.conf`` en local.

**6. Activer le tunnel WireGuard sur le SDK**

.. code-block:: bash

   make vpn-up

**7. Vérifier la connectivité**

.. code-block:: bash

   ansible all -i inventory/hosts.yml -m ping

----

OS
--

| Rôle : `roles/system/tasks/os.yml <https://github.com/iobewi/kubewi/blob/main/ansible/roles/system/tasks/os.yml>`_

Le rôle configure les éléments suivants sur chaque nœud :

- **hostname** : positionné depuis le nom d'hôte déclaré dans l'inventaire
- **timezone** : configurable via la variable ``timezone`` (défaut : ``Europe/Paris``)
- **paquets de base** : ``avahi-daemon``, ``curl``, ``vim``, ``ca-certificates``, ``apt-transport-https``, ``gnupg``
- **swap désactivé** : requis par Kubernetes — sur Debian 13 Trixie (RPi), la
  swap zram est gérée par ``systemd-zram-setup@zram0`` qui est masqué
  (``/dev/zram0`` désactivé, unité pointée vers ``/dev/null``) ;
  ``/etc/fstab`` est également purgé de toute entrée swap
- **modules noyau** : ``overlay`` et ``br_netfilter`` chargés au démarrage
- **paramètres sysctl** : forwarding IPv4 activé sur tous les nœuds
  (requis par Cilium pour le routage inter-pods) ; ``send_redirects``
  désactivé via ``IPv4SendRedirects=no`` dans les fichiers ``.network``
  de systemd-networkd (évite les boucles de routage sur des nœuds qui ne
  sont pas des routeurs réels)

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Paramètre sysctl
     - Valeur
   * - ``net.ipv4.ip_forward``
     - ``1`` — tous les nœuds (requis CNI)
   * - ``net.bridge.bridge-nf-call-iptables``
     - ``1``
   * - ``net.bridge.bridge-nf-call-ip6tables``
     - ``1``
   * - ``IPv4SendRedirects`` (networkd)
     - ``no`` — br0 et VLANs

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

mDNS (avahi-daemon)
-------------------

| Rôle : `roles/system/tasks/os.yml <https://github.com/iobewi/kubewi/blob/main/ansible/roles/system/tasks/os.yml>`_

``avahi-daemon`` est installé et démarré sur tous les nœuds. Il publie le
hostname de chaque machine sur le LAN local via mDNS (protocole ``_mdns._udp``).

Cela permet de joindre le controller depuis le SDK par son nom d'hôte stable,
indépendamment de son adresse DHCP sur ``eth0`` :

.. code-block:: bash

   ping controller-01.local
   ssh iobewi@controller-01.local

C'est le mécanisme utilisé par WireGuard pour résoudre l'endpoint du controller
(variable ``controller_endpoint``). Voir :doc:`wireguard`.

----

Ré-application
--------------

Pour le premier run, utiliser ``playbooks/init.yml`` (voir :ref:`premier-run`
ci-dessus).

Pour ré-appliquer la configuration système après une modification
(tunnel WireGuard actif) :

.. code-block:: bash

   make vpn-up
   ansible-playbook -i inventory/hosts.yml playbooks/system.yml --check --diff
   ansible-playbook -i inventory/hosts.yml playbooks/system.yml
