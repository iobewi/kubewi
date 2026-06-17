# README — R2BEWI SDK Manager

## Introduction

R2BEWI SDK Manager est une plateforme d’infrastructure destinée aux systèmes robotiques distribués.

Le projet cherche à rendre explicites des problématiques souvent implicites dans la robotique moderne :

* placement des charges applicatives ;
* séparation des contraintes temps réel ;
* communication distribuée ;
* observabilité ;
* gestion réseau ;
* reproductibilité des environnements ;
* exploitation multi-nœuds hétérogènes.

L’objectif n’est pas uniquement de déployer des conteneurs ou d’exécuter ROS2 sur Kubernetes.
Le projet vise à formaliser une infrastructure cohérente pour des systèmes robotiques distribués mêlant plusieurs machines, plusieurs niveaux de criticité et plusieurs types de calcul.

---

# Ce qu’est la plateforme

R2BEWI SDK Manager est :

* une plateforme d’orchestration robotique distribuée ;
* un socle d’infrastructure basé sur Linux et Kubernetes ;
* un environnement de déploiement reproductible ;
* une architecture explicitant les contraintes réseau, stockage et communication ;
* une séparation assumée entre hard real-time et soft real-time ;
* une couche d’exploitation pour systèmes ROS2 distribués.

La plateforme repose sur :

* k0s pour l’orchestration Kubernetes ;
* Cilium pour le réseau ;
* Multus pour les interfaces multiples ;
* Zenoh pour la communication distribuée ;
* Vector, Loki, Grafana et Hubble pour l’observabilité ;
* MinIO pour le stockage objet ;
* Ansible pour le provisioning des nœuds.

---

# Ce que la plateforme n’est pas

R2BEWI SDK Manager n’est pas :

* un framework robotique remplaçant ROS2 ;
* une distribution Linux temps réel ;
* un système de contrôle moteur hard real-time ;
* une abstraction masquant totalement Kubernetes ;
* une plateforme cloud générique ;
* une solution cherchant à faire entrer toute la robotique dans des conteneurs.

Le projet considère que certaines contraintes doivent rester proches du matériel :

* boucles moteurs ;
* contrôle critique ;
* acquisition déterministe ;
* microcontrôleurs ;
* contraintes hard real-time.

Ces composants restent hors orchestration Kubernetes.

---

# Philosophie générale

Le projet repose sur plusieurs principes structurants.

## 1. Rendre l’infrastructure explicite

Les rôles des nœuds, les capacités matérielles, les contraintes réseau et les stratégies de communication doivent être décrits explicitement.

Exemples :

* labels Kubernetes ;
* profils matériels ;
* topologies réseau ;
* stratégies de placement ;
* interfaces dédiées ;
* routage Zenoh.

---

## 2. Assumer l’hétérogénéité

Une plateforme robotique moderne mélange :

* x86 ;
* ARM ;
* GPU ;
* MCU ;
* réseau local ;
* liaisons intermittentes ;
* calcul distribué ;
* workloads critiques et non critiques.

La plateforme cherche à organiser cette hétérogénéité plutôt qu’à la masquer.

---

## 3. Séparer hard RT et soft RT

Le projet considère que Kubernetes n’est pas destiné à porter les boucles hard real-time.

La séparation est volontaire :

| Domaine               | Emplacement           |
| --------------------- | --------------------- |
| Hard real-time        | hors cluster          |
| MCU / contrôle moteur | firmware embarqué, micro-ROS, Zenoh-Pico, hors cluster |
| Soft real-time        | cluster Kubernetes    |
| Perception            | cluster Kubernetes    |
| Supervision           | cluster Kubernetes    |
| Observabilité         | cluster Kubernetes    |

---

## 4. Observer le système distribué

L’observabilité n’est pas considérée comme optionnelle.

Le système doit permettre :

* la collecte centralisée des logs ;
* la visualisation des flux réseau ;
* la supervision des workloads ;
* l’analyse des comportements distribués ;
* le diagnostic des dégradations réseau.

---

# Cas d’usage visés

## Robotique distribuée

* robots multi-calculateur ;
* perception déportée ;
* coordination multi-agents ;
* fusion de données distribuée.

---

## Plateformes ROS2 hétérogènes

* Jetson ;
* Raspberry Pi ;
* serveurs x86 ;
* réseaux hybrides ;
* workloads CPU/GPU mixtes.

---

## Laboratoires et R&D robotique

* expérimentation reproductible ;
* déploiement rapide ;
* validation d’architectures distribuées ;
* simulation d’infrastructure robotique.

---

## Edge robotics

* systèmes embarqués connectés ou isolés ;
* traitement local ;
* orchestration locale par cluster k0s ;
* fonctionnement partiellement ou totalement déconnecté d’un cloud externe ;
* maintien des services essentiels sur site.

---

# Architecture cible

## Vue générale

```text
                         ┌──────────────────────────┐
                         │        Core Node         │
                         │──────────────────────────│
                         | k0s control plane        │
                         │ OCI registry             │
                         │ MinIO                    │
                         │ Loki / Grafana           │
                         │ Hubble                   │
                         │ Zenoh router             │
                         │ DHCP / DNS / VPN         │
                         └────────────┬─────────────┘
                                      │
                     ─────────────────┼─────────────────
                                      │
          ┌───────────────────────────┼───────────────────────────┐
          │                           │                           │
┌──────────────────────┐   ┌──────────────────────┐   ┌──────────────────────┐
│ Motion Worker Node   │   │ Perception Worker    │   │ Generic Edge Worker  │
│──────────────────────│   │──────────────────────│   │──────────────────────│
│ k0s worker           │   │ k0s worker           │   │ k0s worker           │
│ Cilium / Multus      │   │ Cilium / Multus      │   │ Cilium / Multus      │
│ Vector agent         │   │ Vector agent         │   │ Vector agent         │
│ ROS2 workloads       │   │ ROS2 workloads       │   │ edge services        │
│ ros2_control         │   │ CUDA/TensorRT        │   │ gateways / bridges   │
│ local devices        │   │ camera / GPU         │   │ local services       │
│                      │   │                      │   │                      │
└──────────────────────┘   └──────────────────────┘   └──────────────────────┘
          │                           │                           │
┌──────────────────────┐   ┌──────────────────────┐   ┌──────────────────────┐
│ Outside Kubernetes   │   │ Outside Kubernetes   │   │ Outside Kubernetes   │
│──────────────────────│   │──────────────────────│   │──────────────────────│
│ MCU                  │   │ device firmware      │   │ local control        │
│ micro-ROS            │   │ hardware drivers     │   │ fieldbus / IO        │
│ Zenoh-Pico           │   │ low-level drivers    │   │ real-time interfaces │
└──────────────────────┘   └──────────────────────┘   └──────────────────────┘
```

---

# Composants principaux

| Composant  | Rôle                            |
| ---------- | ------------------------------- |
| k0s        | orchestration Kubernetes légère |
| Cilium     | réseau Kubernetes basé eBPF     |
| Multus     | interfaces réseau multiples     |
| Zenoh      | communication distribuée        |
| Zenoh-Pico | communication embarquée MCU     |
| Vector     | collecte de logs                |
| Loki       | stockage/indexation logs        |
| Grafana    | visualisation                   |
| Hubble     | observabilité réseau            |
| MinIO      | stockage objet S3               |
| Ansible    | provisioning déclaratif         |

---

# Décisions techniques

| Sujet          | Décision                |
| -------------- | ----------------------- |
| Kubernetes     | k0s                     |
| CNI            | Cilium                  |
| multi-network  | Multus                  |
| logs           | Vector + Loki           |
| observabilité  | Grafana + Hubble        |
| stockage froid | MinIO                   |
| provisioning   | Ansible                 |
| communication  | Zenoh                   |
| temps réel     | Zenoh-Pico hors cluster |

---

# Principes réseau

La plateforme considère le réseau comme une contrainte structurelle du système robotique distribué.

Les choix techniques cherchent à :

* limiter les dépendances multicast ;
* rendre les flux observables ;
* segmenter les usages réseau ;
* supporter plusieurs interfaces par nœud ;
* isoler certains flux via VLAN ou réseaux dédiés ;
* permettre la priorisation des communications critiques ;
* maintenir des comportements réseau prévisibles.

La plateforme s’appuie notamment sur :

* Cilium comme dataplane réseau Kubernetes ;
* Multus pour le multi-network ;
* Hubble pour l’observabilité réseau ;
* Zenoh pour les communications distribuées et les topologies routées.

Zenoh est utilisé afin de réduire les contraintes liées au multicast DDS dans les architectures distribuées, intermittentes ou multi-sites.

---

# Principes stockage

La plateforme distingue plusieurs types de stockage selon leur rôle et leur cycle de vie.

| Domaine              | Usage                              | Solution           |
| -------------------- | ---------------------------------- | ------------------ |
| observabilité        | collecte et stockage des logs      | Vector + Loki      |
| données applicatives | état des workloads et services     | volumes Kubernetes |
| stockage objet       | archives, artefacts, bags, exports | MinIO / S3         |

Les logs, les données applicatives et les artefacts robotiques répondent à des contraintes différentes et sont volontairement séparés.

---

# Modes dégradés

La plateforme est conçue pour maintenir un fonctionnement partiel même en présence de défauts d’infrastructure ou de connectivité.

L’objectif est d’éviter qu’une panne d’observabilité, de stockage ou d’orchestration interrompe immédiatement les fonctions robotiques essentielles.

| Défaillance                 | Comportement attendu                                                   |
| --------------------------- | ---------------------------------------------------------------------- |
| perte observabilité         | les workloads continuent de fonctionner                                |
| perte Loki / Grafana        | absence de supervision, fonctionnement local maintenu                  |
| perte MinIO                 | archivage et export différés                                           |
| perte réseau inter-nœuds    | maintien des fonctions locales sur chaque worker                       |
| perte partielle du réseau   | fonctionnement dégradé selon la topologie disponible                   |
| perte du Core Node          | les workloads déjà actifs continuent autant que possible               |
| perte du cluster Kubernetes | les composants hard RT restent opérationnels                           |
| perte Zenoh router          | fallback local ou communication partielle selon les routes disponibles |
| perte connectivité externe  | fonctionnement edge local maintenu                                     |
| saturation réseau           | priorisation possible des flux critiques                               |

La plateforme considère que les systèmes robotiques distribués doivent pouvoir continuer à fonctionner localement même lorsque certaines fonctions d’infrastructure deviennent indisponibles.

---

# État du projet

Le projet est actuellement en phase de structuration d’architecture et de formalisation des invariants techniques.

Les travaux portent principalement sur :

* l’architecture réseau ;
* la séparation temps réel ;
* l’observabilité ;
* le provisioning ;
* les workflows de déploiement ;
* la reproductibilité des environnements robotiques distribués.
