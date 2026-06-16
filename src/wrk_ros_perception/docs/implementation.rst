Implémentation
==============

``ros-perception`` part d'une base NVIDIA L4T plutôt que ``ros-core`` car
les runtimes CUDA et TensorRT ne sont disponibles que sur la base L4T. Le
runtime ROS 2 est installé par-dessus.

Les manifests Kubernetes (``manifests/``) incluent la configuration du
``RuntimeClass`` NVIDIA et les ``limits: nvidia.com/gpu: 1`` requis pour
accéder au GPU depuis le pod.

Le build local (``build``) produit une image x86_64 sans GPU — utile
uniquement pour tester la cohérence du Dockerfile. L'image cible
opérationnelle est exclusivement ``build-arm64``.
