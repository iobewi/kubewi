Rôle
====

``wrk_provisioning`` contient le manifest Kubernetes du serveur DHCP
temporaire utilisé pour l'enrollment des workers.

Le Deployment ``dnsmasq-provisioning`` tourne en ``replicas: 0`` par
défaut (inactif). ``plg_provisioning`` le scale à 1 le temps de la
détection puis le remet à 0.

----

Couches
-------

**Kubernetes** ``manifests/``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Manifest
     - Contenu
   * - ``manifests/dnsmasq.yaml``
     - Namespace ``provisioning`` + ConfigMap dnsmasq + Deployment (replicas=0)
