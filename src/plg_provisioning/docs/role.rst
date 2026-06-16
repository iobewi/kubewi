Rôle
====

``plg_provisioning`` gère le réseau DHCP temporaire utilisé pour détecter
et bootstrapper les workers lors de l'enrollment.

Il contrôle le Deployment ``dnsmasq-provisioning`` dans le namespace
``provisioning`` du cluster : déploiement initial, activation (replicas=1)
et désactivation (replicas=0).

----

Couches
-------

- ``kubewi/commands.py`` — CLI (Python, via ``adp_kube``)
- ``manifests/dnsmasq.yaml`` — Deployment + Service dnsmasq-provisioning

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
