Rôle
====

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
