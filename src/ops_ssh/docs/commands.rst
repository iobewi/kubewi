Commandes CLI
=============

.. code-block:: text

   kubewi ssh init                          génère + distribue la clé sur tous les nœuds
   kubewi ssh config                        (re)génère ~/.ssh/config
   kubewi ssh setup --bastion-host <HOST>   installe la clé sur le bastion (opération initiale)

.. list-table::
   :header-rows: 1
   :widths: 55 45

   * - Commande
     - Usage
   * - ``kubewi ssh init``
     - Génère ``~/.ssh/kubewi_ansible``, configure ``~/.ssh/config``,
       distribue la clé sur controllers puis workers (mot de passe demandé).
   * - ``kubewi ssh config``
     - Configure ``~/.ssh/config`` uniquement (sans distribuer de clé).
       Idempotent.
   * - ``kubewi ssh setup --bastion-host controller-01``
     - Installe ``~/.ssh/id_ed25519.pub`` sur le bastion via son utilisateur
       bootstrap (ex. ``ubuntu``) pour permettre le premier accès SSH.

Ordre habituel lors de la mise en service initiale :

.. code-block:: bash

   kubewi ssh setup --bastion-host controller-01   # 1 — accès initial bastion
   kubewi vpn up                                   # 2 — tunnel WireGuard
   kubewi ssh init                                 # 3 — clé ansible + config
