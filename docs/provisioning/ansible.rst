Ansible
=======

Le provisioning KubeWI repose sur Ansible pour appliquer de façon
déclarative et reproductible la configuration de chaque nœud.

`Documentation officielle Ansible <https://docs.ansible.com>`_

----

Principe de fonctionnement
---------------------------

Ansible est un outil d'**automatisation de configuration** et de
**provisioning d'infrastructure**. Il permet de décrire l'état attendu
d'un système (paquets installés, fichiers déployés, services actifs)
et de l'appliquer de façon cohérente sur un ou plusieurs nœuds distants.

Dans le contexte KubeWI, Ansible prend en charge l'intégralité de la
préparation des nœuds physiques : configuration système, réseau Linux,
runtime conteneur et bootstrap Kubernetes. L'objectif est de pouvoir
(re)provisionner un nœud de façon fiable et reproductible, sans
intervention manuelle.

**Sans agent** : Ansible se connecte aux nœuds via SSH et exécute les
tâches à distance avec Python. Aucun service ni daemon Ansible ne tourne
sur les nœuds cibles. La seule condition préalable est un accès SSH
fonctionnel.

**Idempotent** : relancer un playbook sur un nœud déjà configuré ne
produit aucun changement si l'état du système correspond à la
configuration déclarée. Cette propriété permet d'appliquer une
configuration en toute sécurité, que le nœud soit vierge ou partiellement
configuré, et de corriger une dérive de configuration sans effet de bord.

**Déclaratif** : la configuration est exprimée sous forme de YAML lisible.
On décrit *ce que le système doit être*, pas *les commandes à exécuter
dans quel ordre*. Ansible traduit cette déclaration en actions concrètes
adaptées à l'état courant du nœud.

Les concepts essentiels :

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Concept
     - Rôle
   * - Inventory
     - liste des nœuds, leurs adresses et leurs variables
   * - Playbook
     - séquence de rôles appliquée à un groupe de nœuds
   * - Role
     - unité de configuration réutilisable (tâches, templates, handlers)
   * - Handler
     - tâche déclenchée uniquement lorsqu'une tâche notifie un changement
   * - Template
     - fichier de configuration généré dynamiquement depuis des variables

----

Installation
------------

Ansible s'installe sur la **machine de contrôle** (poste opérateur ou
serveur de déploiement), pas sur les nœuds cibles.

.. code-block:: bash

   pip install ansible

Vérifier l'installation :

.. code-block:: bash

   ansible --version

----

Ansible Galaxy
--------------

`Ansible Galaxy <https://galaxy.ansible.com>`_ est le hub officiel de
partage de contenu Ansible. Il référence des **collections** et des
**roles** communautaires couvrant la plupart des usages courants
(gestion de paquets, configuration réseau, services système, etc.).

Une **collection** regroupe un ensemble de modules, plugins et roles
maintenus ensemble. KubeWI utilise deux collections qui étendent les
modules builtin d'Ansible :

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Collection
     - Modules utilisés
   * - ``ansible.posix``
     - ``sysctl`` : paramètres noyau
   * - ``community.general``
     - ``timezone``, ``modprobe``

Les dépendances sont déclarées dans ``ansible/requirements.yml``.
Installer les collections avant le premier run :

.. code-block:: bash

   ansible-galaxy collection install -r requirements.yml

Créer le squelette d'un nouveau rôle :

.. code-block:: bash

   ansible-galaxy role init roles/<nom-du-role>

----

Structure du projet
--------------------

Le projet Ansible est organisé sous ``ansible/`` :

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Répertoire
     - Contenu
   * - ``inventory/``
     - nœuds, groupes et variables par groupe
   * - ``roles/``
     - unités de configuration (une par périmètre fonctionnel)
   * - ``playbooks/``
     - points d'entrée qui associent des rôles à des groupes de nœuds
   * - ``scripts/``
     - scripts Python liés à Ansible : enrollment, kubeconfig, injection vault

Les scripts SSH (``ssh_init.py``, ``ssh_config.py``) sont dans ``scripts/``
à la racine du dépôt — ils ne sont pas spécifiques à Ansible.

Chaque section de provisioning documente le rôle qui la met en œuvre.

----

Inventory
---------

L'inventory déclare les nœuds du cluster, leurs adresses, leurs groupes
et les variables associées. Le fichier principal est ``inventory/hosts.yml``,
généré depuis ``inventory/hosts.yml.example`` (non versionné) via :

.. code-block:: bash

   make ansible-init

Les nœuds sont organisés en hiérarchie de groupes reflétant les responsabilités :

.. code-block:: yaml

   all:
     children:
       kubernetes:           # tous les nœuds k0s
         children:
           controllers:
             children:
               gateways:    # controller + exposition externe + WireGuard
           workers:

Cette hiérarchie garantit que toute modification d'un rôle commun
(installation k0s, version, CIDRs) se propage sur controllers et workers.

Les variables sont réparties selon leur périmètre :

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Fichier
     - Contenu
   * - ``group_vars/all/main.yml``
     - Variables système communes (timezone, NTP, VLANs, become)
   * - ``group_vars/kubernetes.yml``
     - Variables k0s communes (version, CIDRs, Cilium)
   * - ``group_vars/all/vault.yml``
     - Secrets chiffrés (WiFi, clés WireGuard)
   * - ``hosts.yml``
     - Variables spécifiques à chaque nœud (IPs, interfaces, clés publiques)

Le nom déclaré dans l'inventory (``controller-01``, ``worker-motion-01``)
est utilisé par Ansible comme hostname du nœud lors du provisioning.

----

Playbooks
---------

Un playbook associe un ou plusieurs rôles à un groupe de nœuds.
C'est le point d'entrée de chaque opération Ansible.

KubeWI fournit les playbooks suivants :

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Playbook
     - Usage
   * - ``playbooks/init.yml``
     - Premier run : bootstrap + system + network + WireGuard sur le gateway,
       via l'IP DHCP eth0 (avant que le tunnel VPN soit disponible).
   * - ``playbooks/gateway.yml``
     - Réseau externe et WireGuard sur les gateways uniquement.
   * - ``playbooks/system.yml``
     - Configuration système de base sur tous les nœuds
       (OS, SSH, chrony, containerd).
   * - ``playbooks/network.yml``
     - Configuration réseau (bridge, VLANs, WiFi).
   * - ``playbooks/controller.yml``
     - Bootstrap k0s controller.
   * - ``playbooks/workers-init.yml``
     - Premier run worker : bootstrap SSH + system + réseau via IP provisioning
       (``init_host``). À lancer après ``make provisioning-on``.
   * - ``playbooks/worker.yml``
     - Bootstrap k0s worker (après ``workers-init.yml``).
   * - ``playbooks/wireguard.yml``
     - Déploiement WireGuard sur les gateways.
   * - ``playbooks/stack.yml``
     - Provisioning complet enchaîné.

Un playbook est un fichier YAML minimal qui déclare les hôtes ciblés
et les rôles à appliquer :

.. code-block:: yaml

   - name: System base provisioning
     hosts: all
     roles:
       - system

----

Gestion des privilèges
-----------------------

La plupart des tâches de provisioning requièrent les droits ``root``
(installation de paquets, configuration système, modification de
fichiers système). L'user de connexion SSH n'est pas root, Ansible
utilise ``sudo`` pour escalader les privilèges via le mécanisme
``become``.

Cette escalade est activée globalement dans ``inventory/group_vars/all.yml`` :

.. code-block:: yaml

   ansible_become: true
   ansible_become_method: sudo

Selon la distribution et la configuration du nœud, deux cas se
présentent :

.. list-table::
   :header-rows: 1
   :widths: 35 30 35

   * - Situation
     - Distrib courantes
     - Commande
   * - ``sudo`` sans mot de passe
     - Ubuntu, Raspberry Pi OS, Jetson
     - ``ansible-playbook playbooks/system.yml``
   * - ``sudo`` avec mot de passe
     - Debian (selon install)
     - ``ansible-playbook playbooks/system.yml --ask-become-pass``

Sur un système fraîchement installé avec sudo protégé par mot de passe,
Ansible demandera ce mot de passe **à chaque run**. Pour éviter cela,
le playbook de bootstrap configure le sudo sans mot de passe en une
opération unique (voir :doc:`system`).

----

Préparation SSH
---------------

Ansible se connecte aux nœuds via SSH avec authentification par clé.
L'authentification par mot de passe sera **désactivée par le playbook**
une fois la clé en place.

La commande suivante gère l'intégralité de la préparation SSH en une seule
opération (tunnel WireGuard requis) :

.. code-block:: bash

   make ssh-init

Elle génère la clé ``~/.ssh/kubewi_ansible`` si absente, configure
``~/.ssh/config``, puis pousse la clé publique sur tous les nœuds via
mot de passe (un prompt par groupe — controllers, puis workers).

Pour reconfigurer uniquement ``~/.ssh/config`` (après ``make vpn-up``) :

.. code-block:: bash

   make ssh-config

La clé privée est déclarée dans ``ansible.cfg`` via ``private_key_file``,
Ansible l'utilisera automatiquement pour toutes les connexions.

----

Commandes de référence
-----------------------

.. list-table::
   :header-rows: 1
   :widths: 50 50

   * - Commande
     - Usage
   * - ``ansible all -i inventory/hosts.yml -m ping``
     - tester la connectivité SSH vers tous les nœuds
   * - ``ansible-playbook -i inventory/hosts.yml <playbook> --check --diff``
     - simuler sans appliquer
   * - ``ansible-playbook -i inventory/hosts.yml <playbook>``
     - appliquer la configuration
   * - ``ansible-playbook -i inventory/hosts.yml <playbook> --limit <cible>``
     - cibler un nœud ou un groupe
   * - ``ansible-playbook -i inventory/hosts.yml <playbook> -v``
     - verbosité niveau 1 (tâches)
   * - ``ansible-playbook -i inventory/hosts.yml <playbook> -vvv``
     - verbosité niveau 3 (connexions SSH)
   * - ``ansible-inventory -i inventory/hosts.yml --list``
     - afficher l'inventaire résolu
   * - ``ansible-galaxy collection install -r requirements.yml``
     - installer les collections requises
   * - ``ansible-galaxy role init roles/<nom>``
     - créer le squelette d'un nouveau rôle
