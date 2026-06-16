Rôle
====

``adp_ansible`` est l'interface stable entre le CLI kubewi et Ansible.

----

Principes Ansible
-----------------

**Sans agent** — Ansible se connecte aux nœuds via SSH et exécute les tâches
à distance avec Python. Aucun daemon ne tourne sur les nœuds cibles.

**Idempotent** — relancer un playbook sur un nœud déjà configuré ne produit
aucun changement si l'état du système correspond à la configuration déclarée.

**Déclaratif** — on décrit *ce que le système doit être*, pas *les commandes
à exécuter*. Ansible traduit cette déclaration en actions adaptées à l'état
courant du nœud.

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
     - tâche déclenchée uniquement quand une tâche notifie un changement
   * - Template
     - fichier de configuration généré dynamiquement depuis des variables

----

Hiérarchie de l'inventaire
---------------------------

Les nœuds sont organisés en groupes reflétant leurs responsabilités :

.. code-block:: yaml

   all:
     children:
       kubernetes:             # tous les nœuds k0s
         children:
           controllers:
             children:
               gateways:       # controller + exposition externe + WireGuard
           workers:

Cette hiérarchie garantit que toute modification d'un rôle commun
(version k0s, CIDRs) se propage sur controllers et workers.

----

Collections Galaxy
------------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Collection
     - Modules utilisés
   * - ``ansible.posix``
     - ``sysctl``, ``authorized_key``
   * - ``community.general``
     - ``timezone``, ``modprobe``

.. code-block:: bash

   ansible-galaxy collection install -r src/adp_ansible/requirements.yml

----

Il expose deux fonctions primitives utilisées par tous les engines et
plugins qui pilotent des playbooks : ``run_playbook()`` et ``run_make()``.

Il porte également l'inventaire (``inventory/``), les scripts d'injection
de secrets (WiFi, clés WireGuard) et les commandes de gestion du vault.
Aucun rôle Ansible ni playbook ne vit ici — c'est le domaine des engines.

----

Couches
-------

**Python** ``kubewi/lib.py``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Interface consommée par les autres paquets :

.. code-block:: python

   from adp_ansible.kubewi import lib as ansible

   ansible.run_playbook(Path('playbooks/wireguard.yml'))
   ansible.run_playbook(Path('playbooks/system.yml'), '--limit', 'workers')

L'inventaire est résolu depuis ``work/hosts.yml`` (gitignored).
Le répertoire de travail Ansible est ``src/adp_ansible/`` pour que
``ansible.cfg`` et ``roles_path`` soient correctement résolus.

**Inventaire** ``inventory/``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - Fichier
     - Contenu
   * - ``inventory/hosts.yml.example``
     - Modèle de l'inventaire — versionné, sans secrets
   * - ``inventory/group_vars/all/main.yml``
     - Variables système communes (timezone, NTP, VLANs, become)
   * - ``inventory/group_vars/kubernetes.yml``
     - Variables k0s (version, CIDRs, Cilium)
   * - ``inventory/group_vars/all/vault.yml.example``
     - Modèle du vault — versionné, valeurs vides
   * - ``inventory/group_vars/all/vault.yml``
     - Secrets réels — gitignored, créé par ``kubewi ansible init``

**Scripts** ``scripts/``
~~~~~~~~~~~~~~~~~~~~~~~~~

- ``inject_wifi.py`` — injecte SSID et PSK dans le vault
- ``inject_wg_keys.py`` — injecte les clés WireGuard dans vault et hosts
- ``kubeconfig.py`` — récupère le kubeconfig k0s depuis le controller
