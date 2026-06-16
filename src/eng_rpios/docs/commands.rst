Commandes CLI
=============

.. code-block:: text

   kubewi rpios provision            applique les spécificités RPi OS
   kubewi rpios provision --limit    cible un sous-ensemble de nœuds

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - Commande
     - Usage
   * - ``kubewi rpios provision``
     - Applique cgroups + zram sur tous les nœuds RPi.
   * - ``kubewi rpios provision --limit worker-01``
     - Cible un nœud spécifique.
