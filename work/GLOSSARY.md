# Glossary

Ce glossary définit le sens des principaux termes utilisés dans l’architecture R2BEWI.

Les définitions ci-dessous décrivent leur usage dans le contexte du projet et ne cherchent pas à constituer des définitions génériques ou exhaustives.

---

# Infrastructure

| Terme                         | Définition                                                                                               |
| ----------------------------- | -------------------------------------------------------------------------------------------------------- |
| Core Infrastructure           | ensemble minimal des services nécessaires au fonctionnement autonome du cluster robotique local          |
| Core Node                     | nœud portant les fonctions centrales de coordination locale                                              |
| Worker Node                   | nœud exécutant les workloads orchestrés                                                                  |
| Infrastructure d’exploitation | infrastructure dédiée à l’observabilité, la supervision et au stockage froid                             |
| Workload robotique            | application ou service robotique exécuté dans la couche orchestrée                                       |
| Cluster robotique local       | cluster k0s local exécutant les workloads opérationnels                                                  |
| Hors cluster robotique local  | composants exécutés en dehors de la couche orchestrée du cluster robotique local                         |
| Node labels                   | labels Kubernetes décrivant explicitement les capacités matérielles et fonctionnelles des nœuds          |
| Infrastructure pilotée        | infrastructure déclarative, inspectable et versionnable                                                  |
| Edge-first                    | approche privilégiant le fonctionnement autonome local avant la dépendance à une infrastructure distante |

---

# Orchestration

| Terme                        | Définition                                                                                 |
| ---------------------------- | ------------------------------------------------------------------------------------------ |
| k0s                          | distribution Kubernetes légère utilisée comme couche d’orchestration                       |
| Couche orchestrée Kubernetes | ensemble des workloads et services gérés par Kubernetes                                    |
| Placement explicite          | stratégie consistant à décrire explicitement où un workload doit être exécuté              |
| GitOps                       | stratégie d’exploitation basée sur des manifests versionnés et réconciliés automatiquement |
| Manifest Kubernetes          | description déclarative d’une ressource Kubernetes                                         |
| Node affinity                | mécanisme Kubernetes permettant de contraindre le placement d’un workload                  |
| Taints / tolerations         | mécanismes Kubernetes permettant d’isoler certains nœuds ou workloads                      |
| Reconciliation               | mécanisme consistant à ramener l’état réel vers l’état désiré                              |

---

# Temps réel

| Terme             | Définition                                                                                            |
| ----------------- | ----------------------------------------------------------------------------------------------------- |
| Hard real-time    | composants nécessitant des contraintes temporelles strictes et déterministes                          |
| Soft real-time    | composants tolérant une certaine variabilité temporelle                                               |
| Firmware          | logiciel embarqué exécuté directement sur MCU ou matériel dédié                                       |
| MCU               | microcontrôleur exécutant les fonctions embarquées critiques                                          |
| micro-ROS         | adaptation légère de ROS2 destinée aux systèmes embarqués et MCU                                      |
| Contrôle critique | fonctions dont la perte immédiate peut provoquer une défaillance physique ou fonctionnelle du système |

---

# Réseau

| Terme             | Définition                                                                                |
| ----------------- | ----------------------------------------------------------------------------------------- |
| CNI               | couche réseau utilisée par Kubernetes pour connecter les workloads                        |
| Dataplane         | couche assurant le traitement et le transport effectif des flux réseau                    |
| Cilium            | dataplane réseau Kubernetes basé sur eBPF                                                 |
| eBPF              | mécanisme du noyau Linux permettant instrumentation, filtrage et traitement réseau avancé |
| Multus            | extension Kubernetes permettant plusieurs interfaces réseau par workload                  |
| Réseau primaire   | réseau principal utilisé pour la communication inter-nœuds et Kubernetes                  |
| Réseau secondaire | réseau dédié à certains usages spécifiques : terrain, robotique, stockage ou management   |
| QoS réseau        | mécanismes de priorisation et de contrôle des flux réseau                                 |
| VLAN              | mécanisme de segmentation logique du réseau                                               |
| Zenoh router      | composant assurant le routage des communications Zenoh                                    |
| Zenoh-Pico        | implémentation légère de Zenoh destinée aux systèmes embarqués et MCU                     |
| ROS2 distribué    | architecture ROS2 répartie sur plusieurs nœuds ou machines communicant via DDS ou Zenoh   |

---

# Observabilité

| Terme         | Définition                                                                     |
| ------------- | ------------------------------------------------------------------------------ |
| Observabilité | capacité à inspecter et diagnostiquer l’état du système distribué              |
| Logs          | événements textuels produits par les applications et composants système        |
| Métriques     | données numériques représentant l’état ou les performances du système          |
| Traces        | informations permettant de suivre un flux ou une chaîne d’exécution distribuée |
| Vector        | agent de collecte et de transport des logs                                     |
| Loki          | backend de stockage et d’indexation des logs                                   |
| Grafana       | interface de visualisation et supervision                                      |
| Hubble        | outil d’observation des flux réseau Kubernetes                                 |

---

# Stockage

| Terme              | Définition                                                                          |
| ------------------ | ----------------------------------------------------------------------------------- |
| Stockage chaud     | stockage utilisé directement par les workloads et services opérationnels            |
| Stockage froid     | stockage longue durée destiné aux archives et artefacts                             |
| Stockage objet     | stockage accessible via API objet compatible S3                                     |
| MinIO              | solution de stockage objet utilisée pour les artefacts et archives robotiques       |
| Artefact robotique | donnée produite par le système robotique : rosbag, capture, modèle IA, export, etc. |

---

# Résilience et exploitation

| Terme                         | Définition                                                                                          |
| ----------------------------- | --------------------------------------------------------------------------------------------------- |
| Mode dégradé                  | fonctionnement partiel du système malgré une perte d’infrastructure ou de connectivité              |
| Résilience multi-couche       | approche couvrant logiciel, réseau, matériel et communication                                       |
| Autonomie locale              | capacité d’un système à maintenir ses fonctions essentielles sans dépendance externe immédiate      |
| Fallback local                | maintien d’un fonctionnement minimal malgré une perte partielle de connectivité ou d’infrastructure |
| Redondance matérielle         | duplication ou multiplication des interfaces critiques afin de limiter les points de défaillance    |
| Segmentation réseau           | séparation logique ou physique des flux réseau selon leurs usages ou contraintes                    |
| Infrastructure d’exploitation | ensemble des services dédiés à l’analyse, la supervision et l’archivage longue durée                |
| Stockage d’exploitation       | stockage utilisé principalement pour l’observabilité, les archives et l’historisation               |
