# Modes dégradés

## Introduction

R2BEWI considère les modes dégradés comme une propriété normale des systèmes robotiques distribués.

L’objectif n’est pas d’empêcher toute panne, mais d’éviter qu’une défaillance localisée provoque immédiatement l’arrêt complet du système robotique.

La plateforme cherche à maintenir :

* les fonctions locales essentielles ;
* les capacités hard real-time ;
* les communications critiques ;
* un niveau minimal d’autonomie opérationnelle.

---

# Principe général

La plateforme distingue explicitement :

* les fonctions critiques immédiates ;
* les fonctions distribuées ;
* les fonctions d’exploitation ;
* les fonctions d’archivage et d’observabilité.

Toutes les défaillances n’ont donc pas le même impact opérationnel.

L’architecture considère notamment que :

* la perte de l’observabilité ne doit pas arrêter les workloads ;
* la perte du stockage froid ne doit pas arrêter le robot ;
* la perte du réseau distribué ne doit pas interrompre les fonctions locales critiques ;
* la perte du cluster robotique local ne doit pas impacter directement les composants hard real-time.

---

# Dégradations infrastructure

| Défaillance | Comportement attendu | Mécanisme architectural |
|---|---|---|
| perte du Core Node | les workloads déjà actifs continuent autant que possible | kubelet local, dépendances runtime locales, services critiques découplés du control plane |
| perte partielle du cluster robotique local | maintien des fonctions locales critiques | découpage par fonctions locales, affinities, labels, fallback local |
| perte Kubernetes | les composants hard real-time restent opérationnels | hard RT hors couche orchestrée, firmware autonome, MCU indépendants |
| perte orchestration | absence de replanification mais maintien des workloads existants selon état local | distinction control plane / workloads déjà exécutés, autonomie des workers |
| perte infrastructure d’exploitation | fonctionnement robotique maintenu | observabilité et stockage froid externalisés, non bloquants pour l’opérationnel |                                            |

La plateforme considère que la couche orchestrée ne doit pas devenir un point de dépendance immédiat des fonctions critiques.

---

# Dégradations observabilité et stockage

| Défaillance | Comportement attendu | Mécanisme architectural |
|---|---|---|
| perte Loki | les workloads continuent, buffering Vector si possible | pipeline logs asynchrone, Vector local, absence de dépendance bloquante aux logs |
| perte Grafana | absence de visualisation, fonctionnement local maintenu | visualisation séparée de l’exécution opérationnelle |
| perte MinIO | archivage et exports différés | stockage froid non critique, file d’attente ou réémission différée |
| perte stockage froid | fonctionnement opérationnel maintenu | séparation stockage opérationnel / stockage d’exploitation |
| perte infrastructure observabilité | perte de supervision mais maintien des fonctions robotiques | découplage exploitation / opérationnel |

Les fonctions d’exploitation peuvent être dégradées sans interrompre immédiatement les fonctions robotiques essentielles.

---

# Dégradations réseau

| Défaillance | Comportement attendu | Mécanisme architectural |
|---|---|---|
| perte réseau inter-nœuds | maintien des fonctions locales sur chaque Worker Node | colocalisation des workloads fortement couplés via `nodeAffinity`, fallback local, limitation des dépendances inter-nœuds |
| perte partielle du réseau | fonctionnement limité selon la topologie restante | segmentation réseau, routage explicite, Zenoh, chemins alternatifs |
| saturation réseau | priorisation des flux critiques | VLAN, QoS, interfaces dédiées, séparation des flux non critiques |
| perte réseau observabilité | maintien des workloads opérationnels | observabilité découplée de l’exécution, buffering local Vector si possible |
| perte Zenoh router | fallback local selon la topologie disponible | routers multiples, communication locale ROS2/DDS, endpoints Zenoh explicites |
| perte connectivité externe | maintien du fonctionnement edge local | registry locale, manifests présents localement, dépendances cloud non critiques |

La plateforme considère que les systèmes distribués doivent pouvoir continuer à fonctionner partiellement même en cas de fragmentation réseau.

---

# Dégradations hard real-time

| Défaillance | Comportement attendu | Mécanisme architectural |
|---|---|---|
| perte couche orchestrée | hard real-time non impacté directement | MCU, firmware, micro-ROS et Zenoh-Pico hors couche orchestrée |
| perte observabilité | firmware et contrôle local maintenus | aucune dépendance directe des boucles critiques aux backends d’observabilité |
| perte communication distribuée | maintien des boucles critiques locales | contrôle local autonome, bus terrain locaux, fallback firmware |
| perte infrastructure d’exploitation | aucune dépendance immédiate des MCU et firmware | séparation stricte exploitation / contrôle critique |

Les composants hard real-time restent volontairement découplés des dépendances d’exploitation et d’orchestration distribuée.

---

# Résilience locale

Chaque Worker Node doit pouvoir maintenir un niveau minimal de fonctionnement autonome.

Cette résilience locale peut notamment s’appuyer sur :

* firmware autonome ;
* fallback local ;
* cache local ;
* buffering temporaire ;
* communications locales ;
* chemins réseau alternatifs ;
* séparation des domaines critiques.

La plateforme privilégie les architectures capables de continuer à fonctionner localement même lorsque certaines fonctions distribuées deviennent indisponibles.

---

# Limites assumées

La plateforme ne garantit pas :

* une continuité totale sans dégradation ;
* une orchestration distribuée sans interruption ;
* une observabilité permanente ;
* une synchronisation parfaite entre tous les nœuds.

L’objectif est plutôt :

* de limiter les impacts ;
* de maintenir les fonctions essentielles ;
* de préserver les contraintes critiques ;
* de rendre les dégradations prévisibles et observables.

---

# Positionnement architectural

> La plateforme ne doit pas transformer une panne d’observabilité, de stockage ou d’exploitation en panne robotique critique.

R2BEWI considère les modes dégradés comme une contrainte normale des systèmes distribués edge.

L’architecture cherche donc à maintenir :

* l’autonomie locale ;
* les fonctions hard real-time ;
* les capacités critiques ;
* les communications essentielles ;

même en présence de pertes partielles d’infrastructure ou de connectivité.
