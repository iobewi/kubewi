Implémentation
==============

``adp_kube`` importe ``eng_k0s`` à l'exécution (import tardif) pour éviter
une dépendance circulaire au chargement. Cela permet aussi de substituer
un autre engine Kubernetes sans modifier l'interface publique de l'adapter.

``kubectl`` doit être configuré sur la machine de contrôle avec le bon
contexte (``kubewi``) — obtenu via ``kubewi k0s kubeconfig``.
