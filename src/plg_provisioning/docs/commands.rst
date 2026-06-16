Commandes CLI
=============

.. code-block:: text

   kubewi provisioning deploy   applique le manifest dnsmasq sur le cluster
   kubewi provisioning on       active le DHCP (replicas=1)
   kubewi provisioning off      désactive le DHCP (replicas=0)

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Commande
     - Usage
   * - ``kubewi provisioning deploy``
     - Déploie le manifest ``dnsmasq.yaml`` (opération initiale unique).
   * - ``kubewi provisioning on``
     - Active le pod DHCP — brancher ensuite le worker sur le switch cluster.
   * - ``kubewi provisioning off``
     - Désactive le pod DHCP après enrollment ou en cas d'erreur.

.. note::

   Ces commandes sont appelées automatiquement par ``kubewi enroll worker``.
   L'usage direct est réservé au debug ou à la gestion manuelle.
