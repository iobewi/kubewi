Commandes CLI
=============

.. code-block:: text

   kubewi buildkit setup   crée et démarre le builder buildx ARM64

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Commande
     - Usage
   * - ``kubewi buildkit setup``
     - Configure le builder ``buildx`` avec QEMU pour cross-compiler en ARM64.
       À exécuter une fois par environnement SDK.

Les commandes de build sont exposées par les workloads qui utilisent la lib :

.. code-block:: bash

   kubewi ros-core build-arm64        # build + push image ros-core ARM64
   kubewi ros-motion build-arm64      # build + push image ros-motion ARM64
   kubewi ros-perception build-arm64  # build + push image ros-perception ARM64
