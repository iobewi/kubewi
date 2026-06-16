Implémentation
==============

``run_playbook()`` positionne le ``cwd`` sur ``src/adp_ansible/`` pour que
``ansible.cfg`` soit trouvé automatiquement par Ansible. L'inventaire est
passé explicitement via ``-i work/hosts.yml`` — il est hors du dépôt git.

``ansible.cfg`` déclare le ``roles_path`` couvrant tous les engines et plugins
qui portent des rôles Ansible. Ajouter un nouveau paquet avec des rôles
nécessite d'y ajouter son chemin.
