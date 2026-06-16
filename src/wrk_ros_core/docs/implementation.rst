Implémentation
==============

Zenoh remplace DDS comme middleware RMW car DDS impose de la découverte
multicast qui ne passe pas à travers les VLANs et les bridges du cluster.
Zenoh fonctionne en mode unicast et s'adapte à cette topologie réseau.

Le build arm64 utilise ``docker buildx`` avec un builder ``kubewi-arm64``
configuré par ``wrk_buildkit``. L'image est pushée directement depuis
le builder vers la registry (``--output type=image,push=true``) sans
passer par le daemon Docker local.

``wrk_ros_motion`` et ``wrk_ros_perception`` utilisent cette image comme
base via ``ARG REGISTRY`` + ``FROM ${REGISTRY}/kubewi/ros-core:latest``,
ce qui garantit que tous les nœuds ROS partagent exactement le même socle.
