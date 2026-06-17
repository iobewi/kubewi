Workloads
=========

Les workloads sont les applications déployées sur le cluster Kubernetes.
Chacun produit une image Docker et expose des commandes de build, push et
lint via la CLI ``kubewi``.

.. toctree::
   :maxdepth: 2

   packages/wrk_provisioning/index
   packages/wrk_buildkit/index
   packages/wrk_ros_core/index
   packages/wrk_ros_motion/index
   packages/wrk_ros_perception/index
