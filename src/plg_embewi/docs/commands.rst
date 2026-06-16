Commandes
=========

.. code-block:: text

   kubewi embewi deploy       # Installe CRDs + Deployment embewi-core
   kubewi embewi status       # État des McuNode et McuDeployment
   kubewi embewi logs [--tail N]  # Logs du controller (défaut: 100 lignes)

----

``kubewi embewi deploy``
------------------------

Applique séquentiellement :

1. ``manifests/crds.yaml`` — CRDs ``McuNode`` et ``McuDeployment``
2. ``manifests/embewi-core.yaml`` — Namespace ``embewi``, ServiceAccount,
   ClusterRole, ClusterRoleBinding, Secret ``embewi-tokens`` (vide),
   Deployment ``embewi-core``

Attend la disponibilité du Deployment avec un timeout de 120 s.

Le Secret ``embewi-tokens`` est créé vide. Le remplir avant que les ESP32
ne se connectent (cf. :doc:`role`).

----

``kubewi embewi status``
------------------------

Enchaîne :

.. code-block:: bash

   kubectl get mcu -A -o wide
   kubectl get mcudep -A -o wide

Exemple de sortie :

.. code-block:: text

   NAMESPACE   NAME        NODE ID     IP             STATE    VERSION   READY   AGE
   embewi      wheel-01    wheel-01    192.168.22.10  running  v1.2.0    true    2d
   embewi      cam-front   cam-front   192.168.22.11  booting  v1.0.0    false   5m

   NAMESPACE   NAME             NODE       IMAGE                                          PHASE     AGE
   embewi      wheel-01-v1.2    wheel-01   192.168.42.1:5000/embewi/wheel:v1.2.0          Deployed  2d

----

``kubewi embewi logs``
----------------------

.. code-block:: bash

   kubewi embewi logs          # 100 dernières lignes
   kubewi embewi logs --tail 500

Équivaut à :

.. code-block:: bash

   kubectl logs -n embewi -l app=embewi-core --tail=N --follow=false
