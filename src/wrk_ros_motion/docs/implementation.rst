Implémentation
==============

``wrk_ros_motion`` hérite de ``wrk_ros_core`` via ``FROM ros-core`` dans le
Dockerfile. L'image de base doit donc être buildée et disponible dans le
registry avant de builder ``ros-motion``.

La variable ``IMAGE_TAG`` (défaut : ``latest``) permet de taguer les images
pour les déploiements en production. ``REGISTRY_HOST`` surcharge le registry
cible.
