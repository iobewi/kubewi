Commandes CLI
=============

.. code-block:: text

   kubewi ros-perception build        build l'image (x86_64)
   kubewi ros-perception push         push vers le registry interne
   kubewi ros-perception build-arm64  build + push pour linux/arm64 (VPN requis)
   kubewi ros-perception lint         lint du Dockerfile (hadolint)
   kubewi ros-perception clean        supprime l'image locale

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - Commande
     - Usage
   * - ``kubewi ros-perception build``
     - Build local pour tester le Dockerfile.
   * - ``kubewi ros-perception build-arm64``
     - Cross-compile et push en ARM64 vers ``registry.kubewi.internal``.
       Nécessite ``kubewi vpn up`` et ``kubewi buildkit setup``.
   * - ``kubewi ros-perception lint``
     - Lint hadolint du Dockerfile.
