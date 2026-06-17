# Principes réseau

## Introduction

R2BEWI considère le réseau comme une composante structurelle du système robotique distribué.

Le réseau n’est pas traité comme un simple transport transparent entre workloads.
Il constitue une ressource critique influençant :

* la latence ;
* le jitter ;
* la résilience ;
* la visibilité du système ;
* les modes dégradés ;
* les capacités de communication distribuée.

L’architecture cherche à rendre les flux réseau explicites, observables et maîtrisables.

---

# Principe général

La plateforme considère que :

* tous les flux réseau ne possèdent pas les mêmes contraintes ;
* certaines communications nécessitent isolation ou priorisation ;
* les topologies distribuées doivent rester observables ;
* les communications robotiques ne doivent pas dépendre exclusivement du multicast DDS ;
* le réseau participe directement à la stabilité du système robotique.

---

# Architecture réseau

La plateforme distingue plusieurs catégories de flux réseau :

| Domaine              | Usage                                   |
| -------------------- | --------------------------------------- |
| réseau de gestion    | administration et orchestration         |
| réseau robotique     | communications ROS2 et Zenoh            |
| réseau stockage      | stockage objet et transferts volumineux |
| réseau observabilité | logs, métriques et supervision          |
| réseaux terrain      | interfaces dédiées et bus spécialisés   |

Cette séparation peut être réalisée via :

* VLAN ;
* interfaces dédiées ;
* multi-network Kubernetes ;
* segmentation logique ;
* routage explicite.

---

# Cilium

Cilium constitue le dataplane réseau principal du cluster robotique local.

Le projet utilise Cilium afin de :

* appliquer des politiques réseau ;
* améliorer l’observabilité ;
* exploiter eBPF ;
* faciliter l’analyse des flux ;
* conserver une architecture réseau inspectable.

Cilium participe également à la visibilité opérationnelle du système distribué.

---

# Multus

Multus permet d’attacher plusieurs interfaces réseau aux workloads Kubernetes.

Cette approche permet notamment :

* la séparation management / robotique ;
* l’utilisation de réseaux secondaires ;
* l’isolation de certains flux ;
* le raccordement à des réseaux terrain ;
* l’utilisation d’interfaces dédiées selon les contraintes matérielles.

Tous les workloads ne sont pas supposés partager le même domaine réseau.

---

# Segmentation et QoS

La plateforme prévoit une segmentation explicite des usages réseau.

Les mécanismes envisagés incluent notamment :

* VLAN ;
* interfaces dédiées ;
* politiques réseau ;
* priorisation des flux ;
* QoS réseau ;
* routage explicite ;
* séparation des domaines de communication.

L’objectif est d’éviter qu’un trafic non critique perturbe les communications robotiques sensibles.

---

# Observabilité réseau

Le réseau doit rester observable.

La plateforme s’appuie notamment sur :

| Composant | Rôle                                  |
| --------- | ------------------------------------- |
| Hubble    | visibilité des flux réseau            |
| Cilium    | instrumentation réseau                |
| eBPF      | inspection et instrumentation noyau   |
| Grafana   | visualisation                         |
| Loki      | corrélation logs et événements réseau |

L’observabilité réseau fait partie intégrante de la stratégie d’exploitation distribuée.

---

# Place de Zenoh

Zenoh constitue la couche de communication distribuée privilégiée pour les architectures distribuées R2BEWI.

Le projet utilise Zenoh afin de :

* réduire la dépendance au multicast DDS ;
* faciliter les topologies routées ;
* supporter les réseaux intermittents ;
* simplifier les architectures edge distribuées ;
* améliorer la maîtrise des flux réseau.

Zenoh permet de découpler les problématiques de communication distribuée des contraintes réseau purement locales.

Zenoh-Pico permet d’étendre cette approche aux composants embarqués hors couche orchestrée.

---

# Réseaux terrain et interfaces critiques

Certaines interfaces critiques peuvent rester hors de la couche orchestrée Kubernetes.

Exemples :

* CAN ;
* I2C ;
* SPI ;
* UART ;
* Ethernet temps réel ;
* interfaces industrielles spécialisées.

Ces interfaces peuvent être :

* directement pilotées par firmware ;
* exposées à certains workloads spécifiques ;
* isolées via interfaces dédiées ;
* séparées du réseau de gestion.

La plateforme considère que toutes les interfaces matérielles ne doivent pas être abstraites de manière uniforme.

---

# Résilience réseau

La résilience réseau ne repose pas uniquement sur Kubernetes.

L’architecture peut notamment s’appuyer sur :

* plusieurs interfaces réseau ;
* segmentation des usages ;
* routage explicite ;
* fallback local ;
* chemins de communication alternatifs ;
* séparation des domaines critiques.

L’objectif est de limiter les dépendances à un unique chemin réseau ou à une topologie unique.

---

# Positionnement architectural

> Le réseau n’est pas un détail d’implémentation. Il devient une partie explicite de l’architecture robotique.

L’architecture R2BEWI considère les flux réseau comme des contraintes système devant rester :

* observables ;
* segmentés ;
* maîtrisables ;
* reproductibles ;
* compatibles avec les modes dégradés et l’autonomie locale.
