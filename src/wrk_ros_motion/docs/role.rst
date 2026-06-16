Rôle
====

``wrk_ros_motion`` produit l'image Docker ``ros-motion`` pour les nœuds de
contrôle moteur ROS 2. Elle étend ``ros-core`` (``FROM ros-core``) avec les
packages ROS 2 spécifiques au contrôle moteur.

Cible : workers ARM64 (Raspberry Pi) connectés aux actionneurs.

----

Couches
-------

- ``Dockerfile`` — ``FROM ros-core``, packages contrôle moteur
- ``kubewi/commands.py`` — CLI build/push (délègue à ``wrk_buildkit``)

----

Dépendances
-----------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Paquet
     - Ce qui est utilisé
   * - ``wrk_buildkit``
     - ``lib.build()``, ``lib.push()``, ``lib.build_arm64()``, ``lib.lint()``
   * - ``wrk_ros_core``
     - image de base ``ros-core`` (``FROM`` dans le Dockerfile)
