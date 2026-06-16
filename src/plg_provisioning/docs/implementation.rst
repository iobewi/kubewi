Implémentation
==============

Le DHCP de provisioning est un pod Kubernetes temporaire, pas un service
permanent. Garder le pod éteint (replicas=0) entre les enrollments évite
les conflits DHCP avec le réseau de production.

``kubewi provisioning on`` attend que le pod soit ``Ready`` avant de rendre
la main (``rollout_wait``). Cela garantit que le DHCP est opérationnel
avant que ``plg_enroll`` ne démarre la détection réseau.
