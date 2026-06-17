# Vision Architecture — R2BEWI SDK Manager

## Introduction

R2BEWI SDK Manager formalise une architecture d’infrastructure destinée aux systèmes robotiques distribués.

Le projet ne cherche pas uniquement à exécuter ROS2 sur Kubernetes.
L’objectif est de construire une plateforme capable d’organiser explicitement :

* les contraintes temps réel ;
* les communications distribuées ;
* les topologies réseau ;
* les capacités matérielles ;
* les stratégies de déploiement ;
* l’observabilité ;
* les modes dégradés ;
* les invariants système.

Cette architecture considère qu’un système robotique moderne est composé de plusieurs couches hétérogènes ayant des contraintes différentes et parfois incompatibles.

Le rôle de la plateforme est d’organiser ces contraintes plutôt que de tenter de les masquer.

---

# Principes fondateurs

L’architecture repose sur plusieurs invariants structurants.

## Infrastructure explicite

Les composants du système doivent être décrits explicitement :

* rôle des nœuds ;
* capacités matérielles ;
* placement des workloads ;
* topologies réseau ;
* stratégies de communication ;
* séparation des domaines critiques.

Le projet évite les comportements implicites ou les dépendances cachées.

---

## Séparation des responsabilités

L’architecture distingue volontairement :

* orchestration ;
* contrôle temps réel ;
* communication distribuée ;
* observabilité ;
* stockage ;
* calcul embarqué ;
* exploitation de l’infrastructure.

Toutes les couches ne possèdent pas les mêmes contraintes temporelles ni les mêmes exigences de disponibilité.

---

## Edge-first

La plateforme est conçue pour fonctionner localement, au plus près du système robotique.

Le cluster local n’est pas considéré comme un simple relais d’un cloud distant.
Il constitue lui-même la plateforme d’exécution distribuée.

L’architecture doit pouvoir continuer à fonctionner même en cas de perte de connectivité externe.

---

# Architecture générale

L’architecture distingue quatre niveaux principaux :

| Niveau                        | Rôle                                              |
| ----------------------------- | ------------------------------------------------- |
| Core Infrastructure           | coordination du cluster robotique local           |
| Worker Nodes                  | exécution des workloads robotiques distribués     |
| Infrastructure d’exploitation | observabilité, visualisation et stockage froid    |
| Hors cluster robotique local  | composants hard real-time et interfaces critiques |

La Core Infrastructure porte les fonctions nécessaires au fonctionnement autonome immédiat du cluster robotique local.

Les Worker Nodes exécutent les workloads applicatifs orchestrés par k0s.

L’infrastructure d’exploitation regroupe les services non indispensables au fonctionnement immédiat du système robotique, mais nécessaires à l’analyse, l’historisation et l’exploitation longue durée.

Les composants hors cluster robotique local restent au plus près du matériel et portent les contraintes hard real-time : firmware, micro-ROS, Zenoh-Pico, interfaces bas niveau et contrôle critique.

---

# Core Infrastructure

L’architecture distingue un ensemble minimal de services de coordination locale appelé Core Infrastructure.

Cette couche porte les fonctions nécessaires au fonctionnement autonome du cluster robotique local :

* orchestration Kubernetes ;
* services réseau locaux ;
* registry OCI locale ;
* routage distribué ;
* coordination inter-nœuds.

La Core Infrastructure peut être portée par un ou plusieurs Core Nodes selon la taille du déploiement.

Le projet cherche à éviter qu’un unique nœud devienne un point de dépendance absolu pour les fonctions robotiques essentielles.

---

# Core Node

Le Core Node héberge les composants centraux nécessaires au fonctionnement local de la plateforme.

| Service           | Rôle                     |
| ----------------- | ------------------------ |
| k0s control plane | orchestration Kubernetes |
| OCI registry      | distribution des images  |
| DHCP / DNS        | services réseau locaux   |
| Zenoh router      | communication distribuée |
| VPN               | connectivité distante    |

Selon les capacités disponibles et le mode de déploiement, certains services d’exploitation peuvent également être hébergés localement.

| Service optionnel | Usage                |
| ----------------- | -------------------- |
| Loki              | backend logs         |
| Grafana           | visualisation        |
| Hubble UI         | observabilité réseau |
| MinIO             | stockage objet       |

Ces composants restent optionnels dans les architectures edge autonomes compactes.

---

# Worker Nodes

Les Worker Nodes exécutent les workloads distribués orchestrés par k0s.

Plusieurs profils de nœuds sont envisagés :

| Type                | Usage                              |
| ------------------- | ---------------------------------- |
| Motion Worker       | contrôle robotique local           |
| Perception Worker   | vision, IA et GPU                  |
| Generic Edge Worker | services distribués et passerelles |

Chaque worker rejoint le cluster k0s comme nœud Kubernetes.

Les workloads y sont exécutés sous forme de conteneurs orchestrés.

Les agents d’infrastructure restent déployés au plus près des workloads :

| Agent  | Rôle                           |
| ------ | ------------------------------ |
| Vector | collecte et transport des logs |
| Cilium | dataplane réseau               |
| Multus | multi-network                  |
| Hubble | observabilité réseau           |

---

# Modèle déclaratif des capacités

La plateforme repose sur un modèle déclaratif décrivant explicitement les capacités matérielles et fonctionnelles des nœuds.

Les caractéristiques des nœuds sont exposées via des labels Kubernetes sous le namespace :

```text
r2bewi.io/*
```

Ces labels permettent de décrire :

* les ressources de calcul ;
* les accélérations matérielles ;
* les contraintes temps réel ;
* les équipements réellement intégrés ;
* les capacités utiles au placement des workloads.

Exemples :

```text
r2bewi.io/compute.class=embedded
r2bewi.io/compute.accelerator=nvidia
r2bewi.io/compute.realtime=true
r2bewi.io/device.camera=stereo
r2bewi.io/device.motor=bldc
```

La source de vérité reste l’opérateur et l’intégration matérielle réelle du système.

L’objectif est de rendre les capacités du système explicites, inspectables et exploitables par l’orchestrateur.

---

# Répartition des services

La plateforme distingue :

* les services nécessaires au fonctionnement autonome local ;
* les services d’exploitation ;
* les services d’archivage longue durée.

Les services d’observabilité backend et de stockage froid sont externalisés par défaut vers une infrastructure d’exploitation locale ou distante.

| Service   | Placement recommandé                     |
| --------- | ---------------------------------------- |
| Loki      | cluster d’observabilité local ou distant |
| Grafana   | cluster d’observabilité local ou distant |
| Hubble UI | cluster d’observabilité local ou distant |
| MinIO     | cluster de stockage local ou distant     |

Cette approche permet :

* de limiter la charge de la Core Infrastructure ;
* d’éviter la concentration des usages ;
* de conserver une architecture edge autonome ;
* de séparer coordination locale et exploitation longue durée.

Dans les déploiements compacts, ces services peuvent être colocalisés sur le cluster robotique local lorsque les ressources disponibles le permettent.

---

# Rôle de k0s

k0s constitue la couche d’orchestration de la plateforme.

Son rôle est notamment :

* déployer les workloads ;
* maintenir l’état désiré ;
* gérer les ressources ;
* superviser les services ;
* orchestrer les communications réseau ;
* standardiser les déploiements.

La couche orchestrée Kubernetes n’est pas considérée comme adaptée aux contraintes hard real-time strictes.

Elle orchestre les services distribués autour des composants critiques temps réel.

---

# Stratégie de déploiement

La plateforme privilégie une approche déclarative du déploiement des workloads et de l’infrastructure orchestrée.

Les composants Kubernetes sont décrits sous forme de manifests versionnés et reproductibles :

* workloads ;
* services ;
* politiques réseau ;
* configurations ;
* stratégies de placement ;
* observabilité ;
* stockage.

L’objectif est de garantir :

* la traçabilité des changements ;
* la reproductibilité des déploiements ;
* l’inspectabilité de l’infrastructure ;
* la réduction des dérives de configuration.

---

## Approche GitOps

La plateforme est compatible avec une approche GitOps pour la gestion des ressources orchestrées.

Dans cette approche :

* Git devient la source de vérité déclarative ;
* les manifests Kubernetes sont versionnés ;
* les changements d’infrastructure deviennent auditables ;
* les déploiements peuvent être réconciliés automatiquement.

Le GitOps concerne principalement :

* les workloads Kubernetes ;
* les manifests d’infrastructure ;
* les politiques réseau ;
* les configurations d’observabilité ;
* les stratégies de placement.

Le bootstrap initial, certaines opérations terrain ou les environnements partiellement déconnectés peuvent néanmoins nécessiter des opérations hors GitOps.

La plateforme considère donc GitOps comme une stratégie d’exploitation privilégiée, mais non comme une dépendance absolue au fonctionnement du système robotique.

---

# Workloads ROS2

Les workloads ROS2 s’exécutent principalement dans Kubernetes.

Exemples :

* perception ;
* fusion de données ;
* navigation ;
* supervision ;
* traitement GPU ;
* services distribués ;
* passerelles réseau.

L’architecture considère que ROS2 distribué doit rester observable, déployable et reproductible.

---

## Placement des workloads

La plateforme privilégie un placement explicite des workloads basé sur les capacités déclarées des nœuds.

Les stratégies de placement s’appuient notamment sur :

* `nodeSelector`
* `nodeAffinity`
* `taints` et `tolerations`
* contraintes réseau et matérielles explicites

Le placement peut notamment prendre en compte :

* l’architecture CPU ;
* les accélérations GPU ;
* les contraintes temps réel ;
* les interfaces matérielles ;
* les équipements réellement intégrés ;
* les caractéristiques réseau.

Cette approche permet :

* un placement reproductible ;
* une meilleure lisibilité du système ;
* une réduction des décisions implicites ;
* une cohérence entre contraintes physiques et exécution logicielle.

---

# Séparation hard RT / soft RT

La plateforme distingue explicitement les composants hard real-time des workloads distribués.

| Domaine        | Emplacement                  |
| -------------- | ---------------------------- |
| Hard real-time | hors cluster robotique local |
| MCU            | firmware embarqué            |
| micro-ROS      | hors couche orchestrée       |
| Zenoh-Pico     | hors couche orchestrée       |
| Soft real-time | couche orchestrée Kubernetes |
| perception     | Kubernetes                   |
| supervision    | Kubernetes                   |

Les boucles critiques restent proches du matériel :

* contrôle moteur ;
* acquisition déterministe ;
* bus terrain ;
* interfaces critiques ;
* firmware.

Kubernetes n’est pas utilisé pour exécuter les composants nécessitant des garanties hard real-time strictes.

---

# Architecture réseau

Le réseau constitue une composante structurelle de l’architecture.

La plateforme cherche à maîtriser :

* les flux ;
* les domaines réseau ;
* les latences ;
* le jitter ;
* les priorités ;
* les communications distribuées.

---

## Cilium

Cilium constitue le dataplane réseau Kubernetes.

Le projet utilise eBPF afin de :

* améliorer l’observabilité ;
* réduire certaines couches réseau traditionnelles ;
* faciliter l’analyse des flux ;
* appliquer des politiques réseau.

---

## Multus

Multus permet d’attacher plusieurs interfaces réseau aux workloads.

Cette approche permet notamment :

* l’isolation de certains flux ;
* l’utilisation de VLAN dédiés ;
* la séparation management / robotique ;
* le raccordement à des réseaux terrain.

---

## QoS et segmentation

La plateforme prévoit la segmentation des usages réseau via :

* VLAN ;
* interfaces dédiées ;
* politiques réseau ;
* priorisation des flux ;
* QoS réseau.

L’objectif est d’éviter qu’un trafic non critique perturbe les communications robotiques sensibles.

---

# Place de Zenoh

Zenoh constitue la couche de communication distribuée principale de la plateforme.

Le projet utilise Zenoh afin de :

* réduire les dépendances multicast DDS ;
* faciliter les topologies routées ;
* supporter les réseaux intermittents ;
* simplifier les architectures distribuées ;
* améliorer la maîtrise des flux réseau.

Zenoh est particulièrement adapté aux architectures edge et hybrides où la connectivité n’est pas garantie en permanence.

Zenoh peut être utilisé comme couche de transport distribuée complémentaire ou alternative aux mécanismes DDS classiques dans les architectures ROS2 distribuées.

Cette approche permet de découpler les communications locales ROS2 des problématiques de routage et de segmentation réseau à l’échelle distribuée.

---

# Observabilité

L’observabilité fait partie intégrante de l’architecture.

La plateforme doit permettre :

* la collecte centralisée des logs ;
* l’analyse des flux réseau ;
* la supervision des workloads ;
* le diagnostic des dégradations ;
* l’analyse distribuée du système ;
* l’investigation post-incident ;
* la corrélation entre événements applicatifs, réseau et infrastructure.

L’observabilité est conçue comme une fonction d’exploitation indépendante du fonctionnement immédiat du système robotique.

Les agents de collecte restent déployés au plus près des workloads, tandis que les backends d’observabilité peuvent être externalisés vers une infrastructure d’exploitation dédiée.

---

## Stack d’observabilité

| Composant | Rôle                                  |
| --------- | ------------------------------------- |
| Vector    | collecte et transport des logs        |
| Loki      | stockage et indexation des logs       |
| Grafana   | visualisation et supervision          |
| Hubble    | visibilité et analyse des flux réseau |
| Cilium    | instrumentation réseau via eBPF       |

Les agents Vector sont déployés sur les Worker Nodes afin de collecter les logs de la plateforme et des workloads applicatifs.

Les composants backend d’observabilité peuvent être hébergés :

* sur le cluster robotique local dans une architecture compacte ;
* sur une infrastructure d’exploitation dédiée ;
* sur un cluster externe local ou distant.

Cette séparation permet de limiter l’impact des fonctions d’observabilité sur les ressources critiques du cluster robotique.

---

# Architecture stockage

La plateforme distingue plusieurs catégories de stockage selon leur rôle, leur cycle de vie et leurs contraintes opérationnelles.

| Domaine              | Usage                              | Solution           |
| -------------------- | ---------------------------------- | ------------------ |
| observabilité        | logs et télémétrie                 | Vector + Loki      |
| données applicatives | état des services et workloads     | volumes Kubernetes |
| stockage objet       | archives et artefacts longue durée | MinIO              |

Les données applicatives, les logs et les artefacts robotiques répondent à des contraintes différentes et sont volontairement séparés.

Le stockage objet est principalement utilisé pour :

* rosbags ;
* exports ;
* captures ;
* modèles IA ;
* artefacts applicatifs ;
* archives longue durée.

Les services de stockage froid peuvent être externalisés vers une infrastructure dédiée locale ou distante afin de limiter la charge du cluster robotique opérationnel.

---

# Résilience

La plateforme considère la résilience comme une propriété multi-couche du système robotique distribué.

La résilience ne se limite pas à la reprise applicative assurée par Kubernetes. Elle concerne également :

* la continuité des fonctions locales ;
* la tolérance aux pertes réseau ;
* la séparation des contraintes hard real-time ;
* la résilience matérielle des interfaces critiques ;
* le maintien d’un fonctionnement autonome local.

L’architecture distingue plusieurs niveaux de résilience :

| Niveau         | Mécanisme                               |
| -------------- | --------------------------------------- |
| applicatif     | redéploiement Kubernetes                |
| réseau         | segmentation, routage explicite, QoS    |
| communication  | Zenoh, fallback local                   |
| edge local     | autonomie des Worker Nodes              |
| matériel       | redondance bus et interfaces            |
| hard real-time | découplage hors cluster robotique local |

Les interfaces critiques peuvent notamment s’appuyer sur :

* plusieurs interfaces CAN ;
* des bus I2C séparés ;
* des interfaces réseau multiples ;
* des chemins de communication redondants ;
* des composants locaux autonomes.

L’objectif est d’éviter qu’une défaillance isolée provoque l’arrêt complet du système robotique.

---

# Modes dégradés

La plateforme est conçue pour maintenir un fonctionnement partiel même en présence de défauts d’infrastructure ou de connectivité.

L’objectif est d’éviter qu’une panne d’observabilité, de stockage ou d’orchestration interrompe immédiatement les fonctions robotiques essentielles.

| Défaillance                 | Comportement attendu                                                   |
| --------------------------- | ---------------------------------------------------------------------- |
| perte observabilité backend | les workloads continuent de fonctionner                                |
| perte Loki / Grafana        | absence de supervision, fonctionnement local maintenu                  |
| perte MinIO                 | archivage et export différés                                           |
| perte réseau inter-nœuds    | maintien des fonctions locales sur chaque worker                       |
| perte partielle du réseau   | fonctionnement dégradé selon la topologie disponible                   |
| perte du Core Node          | les workloads déjà actifs continuent autant que possible               |
| perte Kubernetes            | les composants hard real-time restent opérationnels                    |
| perte Zenoh router          | fallback local ou communication partielle selon les routes disponibles |
| perte connectivité externe  | fonctionnement edge local maintenu                                     |
| saturation réseau           | priorisation possible des flux critiques                               |

La plateforme considère que les systèmes robotiques distribués doivent pouvoir continuer à fonctionner localement même lorsque certaines fonctions d’exploitation deviennent indisponibles.

---

# Invariants d’architecture

Les futures évolutions de la plateforme doivent respecter plusieurs invariants structurants.

| Invariant | Description |
|---|---|
| autonomie locale | un Worker Node doit pouvoir maintenir ses fonctions essentielles |
| hard RT séparé | les composants critiques restent hors cluster robotique local |
| placement explicite | toute décision de placement doit être traçable |
| flux inspectables | les communications doivent rester observables |
| infrastructure explicite | réseau, rôles et capacités doivent être déclarés |
| séparation exploitation / opérationnel | l’exploitation ne doit pas perturber les fonctions robotiques |
| résilience multi-couche | la résilience concerne logiciel, réseau et matériel |
| reproductibilité | les déploiements doivent être déterministes |
| orchestration légère | maîtrise de la complexité infrastructure |
| infrastructure pilotée | l’infrastructure doit rester déclarative, inspectable et versionnable |
| GitOps compatible | les workloads orchestrés doivent pouvoir être reconstruits depuis leurs manifests déclaratifs |

---

# Conclusion

R2BEWI SDK Manager formalise une architecture d’infrastructure robotique distribuée où :

* Kubernetes orchestre les workloads distribués ;
* les composants hard real-time restent hors cluster robotique local ;
* le réseau devient une composante explicite du système ;
* l’observabilité est intégrée dès la conception ;
* les fonctions d’exploitation peuvent être externalisées ;
* les mécanismes de résilience couvrent logiciel, réseau et matériel ;
* les modes dégradés sont pris en compte nativement ;
* les infrastructures edge conservent leur autonomie locale.

Cette architecture constitue la cible de référence que les futures évolutions techniques devront respecter.
