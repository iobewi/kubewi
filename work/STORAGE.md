# Principes stockage

## Introduction

R2BEWI distingue explicitement plusieurs catégories de stockage selon leur rôle, leur cycle de vie et leurs contraintes opérationnelles.

Le projet considère que :

* les données opérationnelles ;
* les logs ;
* les artefacts ;
* les archives ;
* les captures robotique ;

ne répondent pas aux mêmes contraintes de performance, de persistance ou d’exploitation.

L’architecture cherche à éviter qu’un unique mécanisme de stockage devienne un point de concentration pour tous les usages.

---

# Principe général

La plateforme distingue plusieurs catégories de données :

| Domaine               | Usage                              |
| --------------------- | ---------------------------------- |
| stockage opérationnel | état des workloads et services     |
| observabilité         | logs et télémétrie                 |
| stockage objet        | artefacts et archives longue durée |
| échange fichier brut  | usage ponctuel uniquement          |

Chaque catégorie possède :

* son propre cycle de vie ;
* ses propres contraintes ;
* sa propre stratégie de stockage ;
* ses propres mécanismes d’accès.

---

# Observabilité et logs

La plateforme distingue explicitement :

* la collecte ;
* le transport ;
* le stockage ;
* la visualisation des logs.

| Fonction        | Composant |
| --------------- | --------- |
| collecte        | Vector    |
| transport       | Vector    |
| indexation logs | Loki      |
| visualisation   | Grafana   |

Les agents Vector restent déployés au plus près des workloads afin de :

* collecter les logs localement ;
* limiter les dépendances centralisées ;
* éviter les montages fichiers partagés ;
* permettre une architecture distribuée observable.

L’architecture privilégie des pipelines de logs distribués plutôt qu’un partage de fichiers centralisé.

---

# Stockage objet

MinIO constitue la solution principale de stockage objet.

Le stockage objet est utilisé pour :

* rosbags ;
* captures ;
* exports ;
* dumps ;
* modèles IA ;
* artefacts applicatifs ;
* archivage longue durée.

MinIO est principalement considéré comme un stockage froid compatible S3.

Le stockage objet peut être externalisé vers une infrastructure d’exploitation dédiée locale ou distante.

---

# Données applicatives

Les données persistantes utilisées directement par les workloads restent gérées via les mécanismes de stockage Kubernetes.

Exemples :

* volumes persistants ;
* PVC ;
* stockage local ;
* stockage distribué selon les besoins.

La plateforme ne considère pas le stockage objet comme un remplacement direct du stockage applicatif opérationnel.

---

# Partage fichier brut

Le partage de fichiers classique n’est pas considéré comme le mécanisme principal de communication ou de centralisation des données du système.

Les usages de type :

* NFS central ;
* partage brut de logs ;
* répertoires partagés globaux ;

sont volontairement limités.

Ces mécanismes peuvent exister pour certains usages ponctuels mais ne constituent pas le socle principal de l’architecture distribuée.

L’objectif est d’éviter :

* la concentration des flux ;
* les dépendances implicites ;
* les points uniques de saturation ;
* les couplages forts entre workloads.

---

# Architecture d’exploitation

Les services de stockage froid et d’observabilité peuvent être externalisés hors du cluster robotique local.

Exemples :

| Service                 | Rôle                            |
| ----------------------- | ------------------------------- |
| Loki                    | stockage et indexation des logs |
| Grafana                 | visualisation                   |
| MinIO                   | archivage objet                 |
| stockage d’exploitation | historisation longue durée      |

Cette séparation permet :

* de limiter la charge du cluster robotique ;
* de conserver l’autonomie locale ;
* de séparer exploitation et opérationnel ;
* de limiter l’impact des traitements d’analyse longue durée.

---

# Résilience stockage

L’architecture stockage cherche à éviter les dépendances critiques à un unique composant centralisé.

La plateforme privilégie :

* la séparation des usages ;
* les pipelines distribués ;
* l’externalisation du stockage froid ;
* la limitation des partages globaux ;
* le découplage entre opérationnel et exploitation.

La perte temporaire du stockage d’exploitation ne doit pas empêcher le fonctionnement immédiat du système robotique.

---

# Positionnement architectural

> Le stockage n’est pas considéré comme un espace partagé unique entre tous les composants du système.

R2BEWI distingue explicitement :

* stockage opérationnel ;
* observabilité ;
* archivage ;
* artefacts longue durée ;
* exploitation distribuée.

Cette séparation vise à conserver une architecture :

* observable ;
* découplée ;
* reproductible ;
* compatible avec les modes dégradés ;
* adaptée aux systèmes edge distribués.
