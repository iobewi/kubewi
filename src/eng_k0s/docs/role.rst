Rôle
====

``eng_k0s`` installe et configure la distribution Kubernetes k0s sur les
controllers et workers du cluster. Il gère l'intégralité du cycle de vie
k0s : installation du binaire, configuration, tokens de jonction, registry
OCI interne et récupération du kubeconfig.

C'est l'implémentation concrète que ``adp_kube`` délègue pour toutes les
opérations de provisioning de nœuds Kubernetes.

----

Couches
-------

- ``playbooks/controller.yml`` — installe et configure k0s sur les controllers
- ``playbooks/workers-init.yml`` — Phase 1 worker : système + réseau via IP provisioning
- ``playbooks/worker.yml`` — Phase 2 worker : installe k0s et joint le cluster

**Rôle** ``k0s_install``
   - Télécharge et installe le binaire k0s (version contrôlée par ``k0s_version``)

**Rôle** ``k0s_controller``
   - Génère ``/etc/k0s/k0s.yaml`` depuis le template
   - Installe le service systemd ``k0scontroller``
   - Configure la registry OCI interne (``registry:2`` sur VLAN 420)
   - Génère le token de jonction pour les workers

**Rôle** ``k0s_worker``
   - Configure containerd pour la registry interne (sans TLS)
   - Récupère le token depuis le controller via ``delegate_to``
   - Installe le service systemd ``k0sworker``
   - Attend que le nœud soit ``Ready`` avant de passer au suivant

----

Dépendances
-----------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Paquet
     - Ce qui est utilisé
   * - ``adp_ansible``
     - exécution des playbooks
