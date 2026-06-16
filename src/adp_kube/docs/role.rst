Rôle
====

``adp_kube`` est l'interface stable entre le CLI kubewi et Kubernetes.
Il expose les primitives kubectl (``apply``, ``scale``, ``rollout_wait``)
utilisées par les plugins et ops qui pilotent des ressources cluster.

Il délègue les opérations de provisioning de nœuds à ``eng_k0s`` — il ne
connaît pas k0s directement, mais sait qu'un engine Kubernetes implémente
``add_worker`` et ``add_controller``. C'est ce qui rend l'adapter
engine-agnostique.

----

Couches
-------

**Python** ``kubewi/lib.py``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Interface consommée par les autres paquets :

.. code-block:: python

   from adp_kube.kubewi import lib as kube

   kube.apply('manifests/dnsmasq.yaml')
   kube.scale('provisioning', 'dnsmasq-provisioning', 1)
   kube.rollout_wait('provisioning', 'dnsmasq-provisioning')
