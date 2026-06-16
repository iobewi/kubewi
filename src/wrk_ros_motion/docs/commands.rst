Commandes CLI
=============

.. code-block:: text

   kubewi ros-motion build        build l'image (x86_64)
   kubewi ros-motion push         push vers le registry interne
   kubewi ros-motion build-arm64  build + push pour linux/arm64 (VPN requis)
   kubewi ros-motion lint         lint du Dockerfile (hadolint)
   kubewi ros-motion clean        supprime l'image locale

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - Commande
     - Usage
   * - ``kubewi ros-motion build``
     - Build local x86_64 pour tester le Dockerfile.
   * - ``kubewi ros-motion build-arm64``
     - Cross-compile et push en ARM64 vers ``registry.kubewi.internal``.
       Nécessite ``kubewi vpn up`` et ``kubewi buildkit setup``.
   * - ``kubewi ros-motion lint``
     - Lint hadolint du Dockerfile.
