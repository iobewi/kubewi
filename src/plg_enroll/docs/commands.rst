Commandes CLI
=============

.. code-block:: text

   kubewi enroll worker                   détecte et enrôle de nouveaux workers
   kubewi enroll worker --single          enrôle un seul nœud sans confirmation
   kubewi enroll worker --inventory-only  met à jour hosts.yml seulement
   kubewi enroll worker --dry-run         simule l'enrollment sans modifier
   kubewi enroll controller --name <n>    enrôle un controller

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - Commande
     - Usage
   * - ``kubewi enroll worker``
     - Lance le workflow complet : DHCP, détection, inventaire, enrollment.
   * - ``kubewi enroll worker --single``
     - Un seul nœud, validation automatique (mode CI/batch).
   * - ``kubewi enroll worker --inventory-only``
     - Met à jour ``hosts.yml`` sans lancer le provisioning Ansible/k0s.
   * - ``kubewi enroll worker --dry-run``
     - Simule la détection, affiche ce qui serait enrollé.
   * - ``kubewi enroll controller --name controller-01``
     - Enrôle un controller (pas de phase DHCP).
