Implémentation
==============

L'enrollment est divisé en deux phases distinctes pour permettre
le redémarrage en cas d'échec :

- **Phase 1** (``worker_init``) — bootstrap réseau : configure les
  interfaces réseau du worker, assigne les VLANs, configure SSH par
  mot de passe (requis pour les nœuds vierges).
- **Phase 2** (``add_worker``) — provisioning k0s : joint le nœud au
  cluster Kubernetes via le token généré par le controller.

Si la phase 1 échoue, le DHCP de provisioning reste actif pour
permettre le debug. Un message invite à ``kubewi provisioning off``
pour le désactiver manuellement.

``--single`` combine ``--yes`` et active le mode automatique : utile
pour ``kubewi cluster apply`` qui enchaine plusieurs nœuds sans
interaction.
