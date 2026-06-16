Rôle
====

``eng_rpios`` applique les ajustements spécifiques à Raspberry Pi OS
(Debian Trixie, aarch64) requis par k0s : activation des cgroups mémoire
dans le bootloader et configuration du swap zram.

Il s'applique **après** ``eng_debian`` sur les nœuds RPi, en complément
du socle système de base.

----

Couches
-------

- ``playbooks/provision.yml`` — applique le rôle ``rpios`` sur les nœuds ciblés

**Rôle** ``rpios``
   - ``tasks/cgroups.yml`` — ajoute ``cgroup_memory=1 cgroup_enable=memory``
     dans ``/boot/firmware/cmdline.txt``, redémarre si modifié
   - ``tasks/swap.yml`` — configure zram swap (module + activation)

----

Dépendances
-----------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Paquet
     - Ce qui est utilisé
   * - ``adp_ansible``
     - exécution du playbook
