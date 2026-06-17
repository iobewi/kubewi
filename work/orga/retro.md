# Rétroplanning proposé — R2BEWI Reference Platform
---

Oui. Pour le **point 1**, je le reformulerais comme une phase de **cadrage architectural officiel**.

# Phase 0 — Refonte du positionnement

## Intention

Cette phase sert à figer la direction du projet avant de coder ou d’automatiser davantage.

Le but n’est pas encore d’installer le cluster, mais de répondre clairement à :

> Qu’est-ce que cette plateforme cherche à garantir, et qu’est-ce qu’elle ne cherche pas à garantir ?

Dans ton cas, c’est essentiel parce que l’architecture mélange :

* robotique distribuée,
* Kubernetes/k0s,
* réseau multi-interface,
* stockage objet,
* logs/observabilité,
* communication ROS2/Zenoh,
* contraintes hard RT / soft RT.

Sans cette phase, le risque est de construire une infra techniquement correcte, mais difficile à expliquer, documenter ou maintenir.

---

# Objectif principal

Produire une **architecture cible stable**, avec un vocabulaire commun et des décisions assumées.

La plateforme doit être décrite comme une infrastructure robotique distribuée où :

* le **hard real-time** reste proche du matériel et hors orchestration Kubernetes ;
* le **soft real-time** peut être orchestré par k0s ;
* Kubernetes sert à placer, superviser et exploiter les charges applicatives ;
* Zenoh structure la communication distribuée ;
* Cilium, Multus, Vector, Loki, Grafana, Hubble et MinIO forment les briques infra observables ;
* Ansible porte le provisioning déclaratif des nœuds.

---

# Livrables à produire

## 1. README principal

Rôle : expliquer rapidement le projet.

Il doit contenir :

* ce qu’est la plateforme ;
* ce qu’elle n’est pas ;
* les cas d’usage visés ;
* les composants principaux ;
* la philosophie générale ;
* le schéma d’architecture cible ;
* un résumé des décisions techniques.

Le README doit permettre à quelqu’un de comprendre en quelques minutes pourquoi le projet existe.

---

## 2. Vision architecture

Rôle : document plus structurant que le README.

Il doit expliquer :

* la séparation bastion / nodes / workloads ;
* le rôle de k0s ;
* le rôle du réseau ;
* la place de Zenoh ;
* la place des workloads ROS2 ;
* la séparation hard RT / soft RT ;
* la stratégie d’observabilité ;
* la stratégie de stockage ;
* les modes dégradés.

C’est le document qui dit :
**voici l’architecture cible que toutes les futures issues doivent respecter.**

---

## 3. Glossary

Rôle : éviter les ambiguïtés.

Exemples de termes à définir :

* bastion
* control plane
* edge node
* robot node
* workload robotique
* hard real-time
* soft real-time
* CNI
* Multus
* réseau primaire
* réseau secondaire
* observabilité
* logs
* traces
* métriques
* stockage chaud
* stockage froid
* mode dégradé
* Zenoh router
* Zenoh-Pico
* hors cluster

---

## 4. Périmètre hard RT / soft RT

C’est probablement l’un des documents les plus importants.

Décision à formaliser :

| Zone                               | Traitement                |
| ---------------------------------- | ------------------------- |
| Hard RT                            | hors Kubernetes           |
| Boucles critiques moteur / capteur | MCU, firmware, Zenoh-Pico |
| Soft RT                            | possible dans k0s         |
| Perception                         | dans le cluster           |
| supervision                        | dans le cluster           |
| logs                               | dans le cluster           |
| orchestration                      | dans le cluster           |

Phrase clé à poser :

> Kubernetes ne porte pas les boucles hard real-time. Il orchestre les composants distribués, observables et redéployables autour du système robotique.

---

## 5. Principes réseau

À formaliser :

* Cilium comme CNI principal ;
* Multus pour attacher des interfaces secondaires ;
* séparation réseau de gestion / réseau robotique / réseau stockage si besoin ;
* Hubble pour la visibilité réseau ;
* Zenoh pour limiter la dépendance au multicast DDS ;
* possibilité de VLAN ou interfaces dédiées selon les nœuds.

Décision importante :

> Le réseau n’est pas un détail d’implémentation. Il devient une partie explicite de l’architecture robotique.

---

## 6. Principes stockage

À formaliser :

* MinIO pour le stockage froid type S3 ;
* pas de NFS comme bus de logs principal ;
* Vector pousse les logs ;
* Loki indexe les logs ;
* Grafana visualise ;
* MinIO conserve les artefacts, dumps, bags, captures, exports longs.

Séparation utile :

| Usage                             | Brique                       |
| --------------------------------- | ---------------------------- |
| Logs temps court                  | Loki                         |
| Visualisation                     | Grafana                      |
| Collecte                          | Vector                       |
| Artefacts lourds                  | MinIO                        |
| Données applicatives persistantes | PVC selon besoin             |
| Partage brut type fichiers        | à éviter comme base centrale |

---

## 7. Modes dégradés

Document à prévoir dès maintenant.

Exemples :

| Panne                    | Comportement attendu                                          |
| ------------------------ | ------------------------------------------------------------- |
| perte du bastion         | les nœuds déjà actifs continuent autant que possible          |
| perte de MinIO           | les workloads critiques continuent, les exports sont retardés |
| perte de Loki            | les apps continuent, buffer Vector si possible                |
| perte réseau inter-nœuds | les fonctions locales restent actives                         |
| perte Zenoh router       | fallback local selon topologie                                |
| perte Kubernetes         | hard RT non impacté directement                               |

Idée centrale :

> La plateforme ne doit pas transformer une panne d’observabilité ou de stockage en panne robotique critique.

---

# Décisions techniques à officialiser

Je garderais ton tableau, mais en ajoutant une colonne “rôle architectural”.

| Sujet          |                Décision | Rôle                                     |
| -------------- | ----------------------: | ---------------------------------------- |
| Kubernetes     |                     k0s | orchestration légère                     |
| CNI            |                  Cilium | réseau principal + eBPF + visibilité     |
| Multi-network  |                  Multus | interfaces secondaires robotique/terrain |
| Logs           |                  Vector | agent de collecte par nœud               |
| Observabilité  | Loki + Grafana + Hubble | logs + visualisation + réseau            |
| Stockage froid |                   MinIO | objet S3 local                           |
| Provisioning   |                 Ansible | configuration déclarative des nœuds      |
| Communication  |                   Zenoh | routage distribué robotique              |
| Temps réel     | Zenoh-Pico hors cluster | hard RT proche matériel                  |

---

# Résultat attendu en fin de phase

À la fin de cette phase, tu dois pouvoir dire :

> L’architecture cible est figée. Les composants sont nommés. Leur rôle est clair. Les limites de Kubernetes sont assumées. Le hard RT est hors cluster. Le soft RT, l’observabilité, les logs, le stockage et la communication distribuée sont cadrés.

---

# Critère de validation

La phase 0 est terminée quand tu as :

* un README compréhensible ;
* une vision architecture validée ;
* un glossaire minimal ;
* une séparation hard RT / soft RT écrite ;
* les principes réseau écrits ;
* les principes stockage écrits ;
* les modes dégradés écrits ;
* le tableau de décisions techniques validé.

En clair : **après cette phase, chaque future issue doit pouvoir se rattacher à une décision d’architecture déjà écrite.**




# Phase 1 — Provisioning bare-metal

## Durée

1 à 2 semaines

## Objectif

Mettre en place le socle d’infrastructure permettant de reconstruire un cluster complet depuis zéro, de manière documentée, reproductible et idempotente.

## Travaux

### Provisioning Ansible

Automatiser la configuration de base des nœuds :

- utilisateurs et accès SSH
- durcissement minimal SSH
- synchronisation horaire avec chrony
- configuration réseau via systemd-networkd
- VLAN et interfaces réseau
- WireGuard
- DNS local
- NTP local
- runtime conteneur
- bootstrap k0s
- labels Kubernetes des nœuds
- registry OCI locale
- MinIO pour stockage objet

### Structure du dépôt

Mettre en place une structure claire et maintenable :

```txt
ansible/
├── inventories/
├── roles/
├── group_vars/
├── host_vars/
└── playbooks/
````

### Documentation

Rédiger la documentation minimale d’exploitation :

* prérequis matériels
* topologie réseau
* bootstrap du cluster
* ajout d’un nœud
* conventions de nommage
* conventions de labels
* procédure de reconstruction complète

## Résultat attendu

Un cluster bare-metal reproductible depuis zéro, avec un provisioning automatisé, une topologie réseau documentée, une registry locale opérationnelle et un socle de stockage objet disponible.

```

Je mettrais **MinIO dans cette phase uniquement si tu le considères comme un service socle obligatoire**. Sinon, tu peux le décaler en Phase 2 “services plateforme”.  
Dans cette phase 1, le cœur dur c’est : **réseau, accès, temps, runtime, cluster, registry, labels**.
```


---

# Phase 2 — Kubernetes networking

## Durée : 1 semaine

## Objectif

Mettre en place le réseau explicite.

## Travaux

### Cilium

* native routing
* kube-proxy replacement
* Hubble

### Multus

* VLAN robotique
* VLAN stockage

### QoS groundwork

* tc
* DSCP
* tests débit

### Documentation

* architecture réseau
* VLAN
* QoS future
* observabilité réseau

## Démo attendue

```txt
Zenoh isolé sur VLAN dédié
trafic observable via Hubble
```

---

# Phase 3 — Observabilité & logs

## Durée : 1 semaine

## Objectif

Rendre le système observable.

## Travaux

### Logs

* Vector DaemonSet
* buffering local
* Loki
* MinIO archive

### Metrics

* Prometheus
* Grafana
* node-exporter

### GPU metrics

* dcgm-exporter Jetson

### Documentation

* logs architecture
* flux observabilité
* stockage logs
* troubleshooting

## Démo attendue

```txt
logs ROS2
+
logs node
+
visualisation Grafana
+
flux réseau visibles
```

---

# Phase 4 — Modèle hardware R2BEWI

## Durée : 1 à 2 semaines

## Objectif

Formaliser la vraie différenciation du projet.

## Travaux

### Profils matériels

```yaml
r2bewi.io/gpu=true
r2bewi.io/can=true
r2bewi.io/realtime=true
```

### Validation

* schéma labels
* conventions
* catalogues capacités

### Placement

* affinity
* taints
* tolerations
* topology spread

### DaemonSets spécialisés

* zenoh-router
* vector
* hardware bridge
* monitoring

### Documentation

* taxonomy hardware
* placement policies
* examples workloads

## Démo attendue

```txt
ajout nouveau node
→ auto-placement cohérent
```

---

# Phase 5 — Stack robotique distribuée

## Durée : 2 semaines

## Objectif

Construire la démo “prod-like”.

## Travaux

### ROS2

* workloads perception
* workloads motion
* bridges

### Zenoh

* routing explicite
* topology tests
* dégradation réseau

### Zenoh-Pico

* IMU
* battery
* microcontroller loop

### Scénarios

* perte réseau
* perte node
* perte storage
* reprise cluster

### Documentation

* architecture robotique
* communication
* invariants
* modes dégradés

## Démo attendue

```txt
robot distribué fonctionnel
avec contraintes réseau visibles
```

---

# Phase 6 — Publication & industrialisation

## Durée : continue

## Objectif

Transformer le projet en référence exploitable.

## Travaux

### Documentation publique

* getting started
* architecture guides
* concepts
* tutorials
* troubleshooting
* diagrams

### Articles

Reprendre ta série :

* réseau
* déterminisme
* orchestration
* explicitation

mais maintenant avec :

* schémas réels,
* captures Hubble,
* dashboards,
* manifests.

### Démo vidéo

Très importante.

Montrer :

* placement,
* VLAN,
* logs,
* Zenoh,
* perte réseau,
* recovery.

### Packaging

```txt
kustomize/
helm/
profiles/
examples/
```

---

# Organisation dépôt recommandée

```txt
r2bewi-platform/

docs/
  architecture/
  networking/
  storage/
  observability/
  hardware/
  tutorials/

ansible/
  inventories/
  roles/

kubernetes/
  base/
  overlays/
  networking/
  observability/
  robotics/

hardware/
  rpi/
  jetson/
  stm32/
  wiring/

examples/
  perception/
  motion/
  zenoh/
```