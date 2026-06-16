Adaptateur Ansible
==================

.. list-table::
   :widths: 20 80
   :stub-columns: 1

   * - Paquet
     - ``adp_ansible``
   * - Type
     - ``adapter``
   * - Dépendances
     - *(aucune)*

Adaptateur Ansible — inventaire, vault, playbooks, scripts.

----

Rôle
----

``adp_ansible`` est l'interface stable entre le CLI kubewi et Ansible.
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
   ansible.run_playbook(Path('playbooks/system.yml'), '--limit', 'workers', env={'VAULT_PASS': '...'})

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
- ``inject_wg_keys.py`` — injecte les clés WireGuard générées dans vault et hosts
- ``kubeconfig.py`` — récupère le kubeconfig k0s depuis le controller

----

Commandes CLI
-------------

.. code-block:: text

   kubewi ansible init            crée hosts.yml et vault.yml depuis les exemples
   kubewi ansible wifi            renseigne les credentials WiFi dans vault.yml
   kubewi ansible wireguard-keys  génère et injecte les clés WireGuard
   kubewi ansible vault-encrypt   chiffre vault.yml avec ansible-vault
   kubewi ansible vault-edit      édite le vault chiffré

.. list-table::
   :header-rows: 1
   :widths: 42 58

   * - Commande
     - Usage
   * - ``kubewi ansible init``
     - Copie les exemples vers les fichiers réels. À lancer une seule fois.
   * - ``kubewi ansible wifi``
     - Injecte ``ssid`` et ``psk`` dans ``vault.yml`` via prompt interactif.
   * - ``kubewi ansible wireguard-keys``
     - Génère deux paires de clés (controller + SDK) et les injecte.
   * - ``kubewi ansible vault-encrypt``
     - Chiffre ``vault.yml`` — à lancer après chaque injection de secrets.
   * - ``kubewi ansible vault-edit``
     - Ouvre le vault déchiffré dans ``$EDITOR`` pour modification manuelle.

----

Implémentation
--------------

``run_playbook()`` positionne le ``cwd`` sur ``src/adp_ansible/`` pour que
``ansible.cfg`` soit trouvé automatiquement par Ansible. L'inventaire est
passé explicitement via ``-i work/hosts.yml`` — il est hors du dépôt git.

``ansible.cfg`` déclare le ``roles_path`` couvrant tous les engines et plugins
qui portent des rôles Ansible. Ajouter un nouveau paquet avec des rôles
nécessite d'y ajouter son chemin.
