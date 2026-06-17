Guide de démarrage
==================

Ce guide décrit la mise en service complète d'un cluster KubeWI, de
l'installation OS jusqu'aux premiers workloads.

.. image:: _static/diagrams/provisioning.svg
   :alt: Vue d'ensemble du déploiement KubeWI
   :align: center
   :target: _static/diagrams/provisioning.svg

----

Prérequis matériel
------------------

Chaque nœud doit disposer de :

- un accès ``root`` ou ``sudo``
- ``systemd`` comme système d'init
- une ou plusieurs interfaces réseau
- un accès SSH initial (par mot de passe, pour le bootstrap)

Systèmes d'exploitation supportés :

.. list-table::
   :header-rows: 1
   :widths: 22 28 30 10 10

   * - Profil
     - Matériel typique
     - OS
     - Arch
     - Paquet
   * - Controller / Edge
     - PC x86_64, mini-PC
     - Debian Stable / Ubuntu Server 24.04
     - amd64
     - ``eng_debian``
   * - Worker
     - Raspberry Pi 4/5
     - Raspberry Pi OS Lite 64-bit
     - arm64
     - ``eng_rpios``
   * - Perception GPU
     - NVIDIA Jetson Xavier / Orin
     - JetPack / Ubuntu L4T
     - arm64
     - ``eng_ubuntu``

.. note::
   Le rôle Kubernetes du nœud (controller ou worker) est défini lors de
   l'enrollment — pas par le matériel. Un RPi peut être controller et
   un x86 peut être worker.

Câblage réseau :

- Un switch pour le réseau cluster (VLANs 220/420/620)
- Le controller branché sur le switch **et** sur un port LAN externe
- Les workers branchés sur le switch cluster uniquement
- Le poste SDK sur le même LAN que le controller (pour le tunnel WireGuard)

----

Installation OS
---------------

L'installation du système d'exploitation est la seule étape manuelle.
Elle repose sur **Ventoy** (boot manager USB multi-ISO) et **cloud-init**
(configuration automatique de l'installeur).

**Préparer la clé USB**

1. Installer `Ventoy <https://www.ventoy.net>`_ sur la clé USB
2. Copier l'ISO OS à la racine de la partition Ventoy
3. Générer l'ISO ``cidata.iso`` avec les données cloud-init :

.. code-block:: bash

   # Générer le hash du mot de passe utilisateur (SHA-512)
   openssl passwd -6
   # Coller le hash dans plg_provisioning/cloud-init/user-data
   # (ne jamais commiter ce fichier avec un hash réel)

   bash src/plg_provisioning/cloud-init/build-iso.sh

4. Copier ``cidata.iso`` à la racine de la partition Ventoy

**Boot et installation**

1. Booter le nœud sur la clé Ventoy
2. Sélectionner l'ISO OS dans le menu
3. L'installation s'effectue sans interaction (cloud-init autoinstall)
4. Après reboot : utilisateur ``iobewi`` créé, SSH actif, ``python3`` installé

.. warning::
   ``cloud-init/user-data`` contenant un hash réel de mot de passe ne
   doit jamais être commité. ``cidata.iso`` est exclu via ``.gitignore``.

----

Initialisation du projet
------------------------

Un **projet kubewi** est un répertoire autonome qui contient toute la
configuration locale d'un cluster : inventaire, vault, clés WireGuard.
Il est indépendant du code source de kubewi et peut être versionné séparément.

kubewi détecte le projet actif dans cet ordre de priorité :

1. Variable d'environnement ``KUBEWI_PROJECT=/chemin/vers/projet``
2. Répertoire courant (si un fichier ``.kubewi-project`` y est présent)

**1. Créer le projet**

.. code-block:: bash

   kubewi cluster inventory-init mon-cluster
   cd mon-cluster

Crée ``mon-cluster/`` avec :

.. code-block:: text

   mon-cluster/
   ├── .kubewi-project      ← marqueur de projet
   ├── hosts.yml            ← inventaire Ansible
   └── group_vars/all/
       └── vault.yml        ← secrets (à chiffrer)

**2. Éditer** ``hosts.yml``

Renseigner a minima pour le controller :

.. code-block:: yaml

   controller-01:
     ansible_host: 10.0.100.1       # IP WireGuard (définie plus bas)
     init_host: "192.168.x.x"       # IP DHCP courante sur eth0 (visible sur le routeur)
     ansible_user: iobewi
     host_id: 1

**3. Générer la description déclarative du cluster**

.. code-block:: bash

   kubewi cluster init

Génère ``cluster.yaml`` — décrit la composition désirée du cluster
(rôles, profils matériel, nœuds). Éditer ce fichier pour ajouter les
workers avant de lancer ``kubewi cluster apply``.

**4. Générer les clés VPN**

.. code-block:: bash

   kubewi vpn generate-keys

Injecte les clés publiques dans ``hosts.yml`` et les clés privées dans
``vault.yml``. Génère ``wg0-sdk.conf`` dans le répertoire projet (gitignored).

**5. (Optionnel) Renseigner les credentials WiFi AP**

.. code-block:: bash

   kubewi cluster wifi

**6. Chiffrer le vault**

.. code-block:: bash

   kubewi cluster vault-encrypt

----

Premier déploiement controller
--------------------------------

Le premier run s'effectue via l'IP DHCP de ``eth0`` (avant que le tunnel
WireGuard ne soit disponible).

**7. Déployer le controller**

.. code-block:: bash

   kubewi cluster stack --limit controllers

Cette commande enchaîne :

- ``kubewi debian provision`` — socle système (OS, SSH, chrony, containerd, sysctl)
- ``kubewi rpios provision`` — si Raspberry Pi (cgroups, zram)
- ``kubewi gateway deploy`` — réseau Linux (bridge, VLANs, NAT, DNS)
- ``kubewi vpn deploy`` — WireGuard (interface ``wg0``, service systemd)
- ``kubewi k0s add controller`` — initialisation k0s, registry OCI, dnsmasq provisioning

----

Accès distant SDK
------------------

**8. Monter le tunnel WireGuard**

.. code-block:: bash

   kubewi vpn up

Vérifier :

.. code-block:: bash

   ping 10.0.100.1      # controller WireGuard
   ping 192.168.22.1    # controller VLAN 220 (k0s API)

**9. Initialiser l'accès SSH**

.. code-block:: bash

   kubewi ssh init

Génère ``~/.ssh/kubewi_ansible``, configure ``~/.ssh/config``
(ProxyJump workers → controller), distribue la clé sur tous les nœuds
(mot de passe demandé une fois par groupe).

**10. Récupérer le kubeconfig**

.. code-block:: bash

   kubewi k0s kubeconfig
   kubectl get nodes

----

Enrollment des workers
-----------------------

**11. Enroller les workers**

.. code-block:: bash

   kubewi cluster apply

Pour chaque worker manquant, la commande :

1. Active le DHCP de provisioning (``kubewi provisioning on``)
2. Détecte le worker branché sur le switch cluster
3. Lance le bootstrap réseau (Phase 1 via IP provisioning ``192.168.0.x``)
4. Lance le provisioning k0s (Phase 2 via VLAN 220)
5. Désactive le DHCP de provisioning

Voir :doc:`packages/plg_enroll/index` pour le détail du workflow.

----

Déploiement de la stack
------------------------

**12. Appliquer la configuration réseau et workloads**

.. code-block:: bash

   kubewi cluster stack

----

Validation
----------

.. code-block:: bash

   kubectl get nodes                     # tous les nœuds Ready
   kubectl get pods -A                   # tous les pods Running
   ping 192.168.22.10                    # VLAN 220 (worker)
   ping 192.168.42.1                     # VLAN 420 (registry)
   curl http://192.168.42.1:5000/v2/    # registry OCI

Le cluster est opérationnel lorsque :

- tous les nœuds sont à l'état ``Ready``
- les pods Cilium sont ``Running`` sur chaque nœud
- les VLANs sont accessibles depuis le SDK via le tunnel
- la registry OCI répond sur ``192.168.42.1:5000``
