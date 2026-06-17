Rôle
====

``plg_provisioning`` gère le réseau DHCP temporaire utilisé pour détecter
et bootstrapper les nœuds lors de l'enrollment.

Il remplit deux responsabilités distinctes :

1. **Lifecycle du pod dnsmasq** — déploiement initial, activation
   (replicas=1) et désactivation (replicas=0) du Deployment
   ``dnsmasq-provisioning`` dans le namespace ``provisioning``.

2. **Détection des nœuds** — ``lib.detect_phase()`` surveille les baux DHCP
   dnsmasq, crée les fichiers ``hosts/<nom>.yml`` avec un nommage basé sur
   la MAC, et retourne la liste des nœuds découverts.

----

Couches
-------

- ``kubewi/commands.py`` — CLI (Python, via ``adp_kube``)
- ``kubewi/lib.py`` — logique de détection exposée à ``ops_cluster``
- ``manifests/dnsmasq.yaml`` — Deployment + Service dnsmasq-provisioning
  (dans ``wrk_provisioning``)

----

Dépendances
-----------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Paquet
     - Ce qui est utilisé
   * - ``adp_kube``
     - ``lib.apply()``, ``lib.scale()``, ``lib.rollout_wait()``
   * - ``kubewi`` (framework)
     - ``_hostfile.mac_to_id()``, ``_hostfile.next_host_id()``,
       ``_hostfile.create_worker_host_file()``, ``_project.resolve()``
