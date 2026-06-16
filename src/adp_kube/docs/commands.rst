Commandes CLI
=============

.. code-block:: text

   kubewi kube add controller   déploie k0s sur les controllers
   kubewi kube add worker       initialise et joint un worker

.. list-table::
   :header-rows: 1
   :widths: 42 58

   * - Commande
     - Usage
   * - ``kubewi kube add controller``
     - Déploie k0s sur le(s) controller(s) (délègue à ``eng_k0s``)
   * - ``kubewi kube add worker --name <nom>``
     - Initialise et joint un worker au cluster (délègue à ``eng_k0s``)
