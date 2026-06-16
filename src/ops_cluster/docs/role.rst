Rôle
====

``ops_cluster`` est le point d'entrée haut niveau pour gérer le cluster
dans son ensemble. Il s'appuie sur un fichier déclaratif ``cluster.yaml``
qui décrit les nœuds désirés, leur profil matériel et leur rôle k0s.

Il orchestre l'enrollment guidé de plusieurs nœuds en séquence
(``apply``), gère l'inventaire initial (``inventory-init``), le vault
Ansible (``vault-encrypt``, ``vault-edit``), et déclenche les playbooks
de déploiement système et réseau.

----

Couches
-------

- ``kubewi/commands.py`` — CLI (Python, orchestration haut niveau)
- ``playbooks/`` — playbooks système, réseau, stack (via ``adp_ansible``)

----

Dépendances
-----------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Paquet
     - Ce qui est utilisé
   * - ``adp_kube``
     - ``lib.add_controller()``, ``lib.add_worker()``, scale provisioning
   * - ``adp_ansible``
     - ``lib.run_make()`` (init, wifi, vault), ``lib.run_playbook()``
   * - ``plg_enroll``
     - ``lib.detection.detect_phase()`` pour l'enrollment guidé
