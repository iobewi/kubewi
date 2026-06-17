# Décisions techniques

Ce document formalise les principales décisions techniques structurant l’architecture R2BEWI.

L’objectif n’est pas uniquement de lister des outils ou des technologies, mais d’expliciter leur rôle architectural dans la plateforme.

Chaque choix répond à des contraintes identifiées :

* orchestration distribuée ;
* edge autonome ;
* observabilité ;
* segmentation réseau ;
* reproductibilité ;
* séparation hard real-time / soft real-time ;
* résilience multi-couche ;
* exploitation distribuée.

Les composants sélectionnés doivent rester cohérents avec les invariants d’architecture du projet.

---

# Vue d’ensemble

| Sujet          |                             Décision | Rôle architectural                                     |
| -------------- | -----------------------------------: | ------------------------------------------------------ |
| Kubernetes     |                                  k0s | orchestration légère du cluster robotique local        |
| CNI            |                               Cilium | dataplane réseau, politiques réseau et visibilité eBPF |
| Multi-network  |                               Multus | interfaces secondaires robotique, terrain ou stockage  |
| Logs           |                               Vector | agent local de collecte et transport des logs          |
| Observabilité  |              Loki + Grafana + Hubble | exploitation, visualisation et analyse réseau          |
| Stockage froid |                                MinIO | stockage objet S3 pour artefacts et archives           |
| Provisioning   |                              Ansible | configuration déclarative et reproductible des nœuds   |
| Déploiement    |                    GitOps compatible | manifests versionnés, traçables et reconstruisibles    |
| Communication  |                                Zenoh | communication distribuée et routage robotique          |
| Embarqué / MCU |               micro-ROS + Zenoh-Pico | communication légère proche matériel                   |
| Temps réel     | hard RT hors cluster robotique local | boucles critiques proches du matériel                  |

---

# Kubernetes — k0s

## Décision

La plateforme utilise k0s comme distribution Kubernetes principale.

## Rôle architectural

k0s constitue la couche d’orchestration du cluster robotique local.

Son rôle est notamment :

* déployer les workloads ;
* maintenir l’état désiré ;
* orchestrer les services distribués ;
* standardiser les déploiements ;
* gérer les ressources et le placement ;
* fournir une couche d’exploitation reproductible.

## Pourquoi k0s

Le choix de k0s vise à :

* conserver une distribution légère ;
* limiter la complexité opérationnelle ;
* réduire les dépendances inutiles ;
* faciliter les déploiements edge ;
* conserver une architecture proche du Kubernetes standard.

La plateforme ne considère pas Kubernetes comme une couche hard real-time.

---

# Réseau — Cilium

## Décision

Cilium constitue le dataplane réseau principal du cluster robotique local.

## Rôle architectural

Cilium apporte :

* les politiques réseau ;
* l’observabilité réseau ;
* l’instrumentation eBPF ;
* l’analyse des flux ;
* une architecture réseau inspectable.

## Pourquoi Cilium

Le réseau est considéré comme une composante structurelle du système robotique distribué.

Le choix de Cilium permet :

* d’améliorer la visibilité des flux ;
* de réduire certaines couches réseau traditionnelles ;
* d’obtenir une meilleure observabilité ;
* de conserver des mécanismes réseau explicitement pilotés.

---

# Multi-network — Multus

## Décision

Multus est utilisé pour attacher plusieurs interfaces réseau aux workloads Kubernetes.

## Rôle architectural

Multus permet notamment :

* la séparation management / robotique ;
* les réseaux terrain dédiés ;
* l’isolation de certains flux ;
* l’utilisation de VLAN ou interfaces spécifiques ;
* le raccordement à des réseaux industriels.

## Pourquoi Multus

Tous les workloads ne possèdent pas les mêmes contraintes réseau.

La plateforme considère que certaines communications doivent pouvoir être :

* isolées ;
* priorisées ;
* segmentées ;
* physiquement séparées si nécessaire.

---

# Logs — Vector

## Décision

Vector constitue l’agent principal de collecte et de transport des logs.

## Rôle architectural

Les agents Vector sont déployés au plus près des workloads afin de :

* collecter les logs localement ;
* transporter les événements ;
* bufferiser les flux si nécessaire ;
* éviter les dépendances centralisées ;
* limiter les montages de fichiers partagés.

## Pourquoi Vector

La plateforme privilégie des pipelines de logs distribués plutôt qu’un partage de fichiers centralisé.

Le projet ne considère pas NFS comme un mécanisme principal de centralisation des logs.

---

# Observabilité — Loki, Grafana et Hubble

## Décision

La plateforme s’appuie sur Loki, Grafana et Hubble pour l’exploitation et l’observabilité.

## Rôle architectural

| Composant | Rôle                            |
| --------- | ------------------------------- |
| Loki      | stockage et indexation des logs |
| Grafana   | visualisation et supervision    |
| Hubble    | visibilité des flux réseau      |

## Pourquoi cette séparation

La plateforme distingue explicitement :

* collecte ;
* transport ;
* stockage ;
* visualisation ;
* analyse réseau.

Les composants backend d’observabilité peuvent être externalisés vers une infrastructure d’exploitation dédiée locale ou distante.

L’observabilité ne doit pas devenir une dépendance critique du fonctionnement robotique immédiat.

---

# Stockage froid — MinIO

## Décision

MinIO constitue la solution principale de stockage objet compatible S3.

## Rôle architectural

Le stockage objet est utilisé pour :

* rosbags ;
* captures ;
* exports ;
* dumps ;
* modèles IA ;
* artefacts applicatifs ;
* archivage longue durée.

## Pourquoi MinIO

La plateforme distingue explicitement :

* stockage opérationnel ;
* stockage objet ;
* observabilité ;
* archivage longue durée.

Le stockage froid peut être externalisé hors du cluster robotique local.

---

# Provisioning — Ansible

## Décision

Ansible constitue la solution principale de provisioning et de configuration des nœuds.

## Rôle architectural

Ansible permet :

* la configuration déclarative ;
* le bootstrap des nœuds ;
* la reproductibilité ;
* l’automatisation des services système ;
* la standardisation des configurations.

## Pourquoi Ansible

La plateforme privilégie une infrastructure :

* inspectable ;
* versionnable ;
* reconstruisible ;
* pilotée explicitement.

---

# Déploiement — GitOps compatible

## Décision

La plateforme privilégie une approche GitOps compatible pour la gestion des ressources orchestrées.

## Rôle architectural

Les manifests Kubernetes deviennent :

* versionnés ;
* traçables ;
* auditables ;
* reconstruisibles.

Le GitOps concerne principalement :

* workloads ;
* manifests Kubernetes ;
* politiques réseau ;
* configurations d’exploitation ;
* stratégies de placement.

## Pourquoi GitOps compatible

Le projet conserve néanmoins :

* la possibilité de bootstrap offline ;
* des opérations terrain ;
* des déploiements edge partiellement déconnectés.

GitOps est considéré comme une stratégie d’exploitation privilégiée, mais non comme une dépendance absolue.

---

# Communication distribuée — Zenoh

## Décision

Zenoh constitue la couche principale de communication distribuée de la plateforme.

## Rôle architectural

Zenoh permet :

* le routage distribué ;
* la réduction des dépendances multicast DDS ;
* les topologies distribuées ;
* les communications edge ;
* les réseaux intermittents.

## Pourquoi Zenoh

Le projet considère que DDS multicast devient difficile à maîtriser dans certaines architectures distribuées ou routées.

Zenoh permet de rendre les communications :

* plus explicites ;
* plus observables ;
* plus compatibles avec les topologies edge distribuées.

---

# Embarqué — micro-ROS et Zenoh-Pico

## Décision

Les composants embarqués peuvent s’appuyer sur micro-ROS et Zenoh-Pico.

## Rôle architectural

Ces composants permettent :

* des communications légères ;
* des échanges proches matériel ;
* l’intégration de MCU ;
* la réduction des dépendances à la couche orchestrée.

## Pourquoi cette approche

La plateforme considère que certaines fonctions doivent rester :

* proches du matériel ;
* faiblement dépendantes du réseau distribué ;
* compatibles avec des contraintes temps réel strictes.

---

# Temps réel — hard RT hors cluster robotique local

## Décision

Les composants hard real-time restent hors du cluster robotique local.

## Rôle architectural

Les fonctions critiques restent exécutées :

* sur MCU ;
* via firmware dédié ;
* via micro-ROS ;
* via Zenoh-Pico ;
* ou directement au niveau matériel.

## Exemples concernés

* contrôle moteur ;
* PWM ;
* acquisition déterministe ;
* pilotage actionneurs ;
* bus terrain critiques ;
* sécurité immédiate.

## Pourquoi cette séparation

La plateforme considère que la couche orchestrée Kubernetes n’est pas adaptée aux contraintes hard real-time strictes.

Kubernetes orchestre les composants distribués, observables et redéployables autour du système robotique, mais ne porte pas directement les boucles critiques temps réel.

---

# Positionnement architectural

Les décisions techniques R2BEWI ne sont pas choisies indépendamment les unes des autres.

Elles forment un ensemble cohérent visant à construire une infrastructure robotique :

* explicite ;
* distribuée ;
* observable ;
* reproductible ;
* segmentée ;
* résiliente ;
* compatible edge ;
* adaptée aux contraintes hard real-time et soft real-time.
