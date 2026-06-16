Rôle
====

``wrk_buildkit`` fournit la lib de build Docker utilisée par tous les
workloads ROS. Il crée un builder ``buildx`` ARM64 avec QEMU pour
construire des images ``linux/arm64`` depuis un poste x86_64.

Il expose sa logique via ``lib.py`` : ``build()``, ``push()``,
``build_arm64()``, ``clean()``, ``lint()``. Les workloads (``wrk_ros_core``,
``wrk_ros_motion``, ``wrk_ros_perception``) délèguent toutes leurs
opérations Docker à cette lib.

----

Couches
-------

- ``kubewi/commands.py`` + ``kubewi/lib.py`` — CLI + lib partagée
- ``buildkitd.toml`` — configuration du daemon buildkit
- ``hadolint.yaml`` — configuration hadolint (collocalisée ici car c'est
  ``wrk_buildkit`` qui l'invoque)

----

Dépendances
-----------

Aucune dépendance kubewi. Nécessite ``docker`` et ``buildx`` installés
dans le SDK.
