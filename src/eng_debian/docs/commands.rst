Commandes CLI
=============

.. code-block:: text

   kubewi debian provision            applique le socle Debian sur tous les nœuds
   kubewi debian provision --limit    cible un sous-ensemble de nœuds

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - Commande
     - Usage
   * - ``kubewi debian provision``
     - Applique le rôle ``debian`` sur tous les nœuds de l'inventaire.
   * - ``kubewi debian provision --limit controller-01``
     - Cible un nœud ou un groupe spécifique.
