Rôle
====

``ops_cluster`` est le point d'entrée haut niveau pour gérer le cycle de vie
complet d'un cluster KubeWI. Il pilote le bootstrap initial, l'ajout de
nœuds, la synchronisation de la configuration et le déploiement de la stack.

L'état désiré est décrit par des fichiers ``hosts/*.yml`` (un par nœud) et
un fichier ``cluster.yml`` (métadonnées : nom + gateway). ``hosts.yml`` est
généré automatiquement — jamais édité à la main.

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
     - ``lib.add_controller()``, ``lib.add_worker()``, ``lib.worker_init()``
   * - ``adp_ansible``
     - ``lib.run_playbook()`` (init, gateway, system, network, stack)
   * - ``ops_ssh``
     - ``lib.ensure_key()``, ``SSH_KEY`` pour les accès SSH directs
   * - ``plg_vpn``
     - ``lib.up()`` pour monter le tunnel WireGuard SDK après ``cluster create``
   * - ``plg_provisioning``
     - ``lib.detect_phase()`` pour l'auto-détection MAC (``cluster add worker``)
   * - ``eng_k0s``
     - ``scripts.kubeconfig`` pour ``cluster kubeconfig``
