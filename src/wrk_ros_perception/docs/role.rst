Rôle
====

``wrk_ros_perception`` produit l'image Docker ``ros-perception`` pour les
nœuds de perception GPU. Elle est basée sur NVIDIA L4T PyTorch (Jetson)
et intègre les stacks de traitement visuel et d'inférence IA.

Cible : workers NVIDIA Jetson (ARM64) connectés aux capteurs (caméras,
LiDAR).

À la différence de ``wrk_ros_motion``, cette image ne dépend pas de
``wrk_ros_core`` — elle part directement d'une base NVIDIA L4T.

----

Couches
-------

- ``Dockerfile`` — ``FROM nvcr.io/nvidia/l4t-pytorch:…``, packages perception
- ``manifests/`` — manifests Kubernetes pour le déploiement sur Jetson
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
