Rôle
====

``plg_enroll`` orchestre le cycle complet d'enrollment d'un nœud :

1. Active le réseau DHCP de provisioning (``plg_provisioning``)
2. Détecte le nœud sur le réseau de provisioning (phase de détection)
3. Met à jour ``hosts.yml`` avec les informations du nœud
4. Lance le bootstrap réseau (phase 1 via ``adp_kube``)
5. Lance le provisioning k0s (phase 2 via ``eng_k0s``)
6. Désactive le DHCP de provisioning

Il ne connaît pas les détails de k0s, dnsmasq ou de l'inventaire
directement — il délègue à ``adp_kube`` (qui délègue à ``eng_k0s``).

----

Couches
-------

- ``kubewi/commands.py`` — CLI (orchestration Python pure)
- ``lib/detection.py`` — détection des nœuds sur le réseau de provisioning
- ``lib/inventory.py`` — mise à jour de ``hosts.yml``

Aucun playbook Ansible ni manifest Kubernetes dans ce paquet.

----

Dépendances
-----------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Paquet
     - Ce qui est utilisé
   * - ``adp_kube``
     - ``lib.worker_init()``, ``lib.add_worker()``, ``lib.add_controller()``,
       ``lib.scale()``, ``lib.rollout_wait()``
   * - ``adp_ansible``
     - inventaire ``hosts.yml``
   * - ``plg_provisioning``
     - cycle de vie du DHCP de provisioning
