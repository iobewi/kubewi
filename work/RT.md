# Périmètre hard RT / soft RT

## Introduction

R2BEWI distingue explicitement les composants hard real-time des workloads distribués orchestrés.

Cette séparation constitue un invariant architectural fondamental du projet.

L’objectif n’est pas d’utiliser Kubernetes pour exécuter toutes les fonctions robotiques, mais d’organiser explicitement les différentes contraintes temporelles du système.

---

# Principe général

La plateforme considère que :

* les fonctions hard real-time doivent rester au plus près du matériel ;
* les workloads distribués peuvent être orchestrés ;
* toutes les fonctions robotiques ne possèdent pas les mêmes contraintes temporelles ;
* l’orchestration distribuée ne doit pas perturber les fonctions critiques.

---

# Répartition des responsabilités

| Domaine                        | Emplacement recommandé       |
| ------------------------------ | ---------------------------- |
| Hard real-time                 | hors cluster robotique local |
| Boucles moteur critiques       | MCU / firmware               |
| Acquisition capteurs critiques | MCU / firmware               |
| Contrôle déterministe          | firmware / micro-ROS         |
| Communication embarquée légère | Zenoh-Pico                   |
| Soft real-time                 | couche orchestrée Kubernetes |
| Perception                     | cluster robotique local      |
| Fusion de données              | cluster robotique local      |
| Navigation                     | cluster robotique local      |
| Services distribués            | cluster robotique local      |
| Passerelles réseau             | cluster robotique local      |
| Orchestration                  | cluster robotique local      |

L’observabilité backend et le stockage froid appartiennent à l’infrastructure d’exploitation et ne constituent pas des composants temps réel du cluster robotique opérationnel.

---

# Hard real-time

Les composants hard real-time restent hors de la couche orchestrée Kubernetes.

Exemples :

* contrôle moteur ;
* PWM ;
* pilotage direct actionneurs ;
* contrôle bas niveau ;
* bus terrain critiques ;
* acquisition déterministe ;
* sécurité immédiate.

Ces fonctions restent exécutées :

* sur MCU ;
* via firmware dédié ;
* via micro-ROS ;
* via Zenoh-Pico ;
* ou directement au niveau matériel.

La plateforme considère que la couche orchestrée Kubernetes n’est pas adaptée aux contraintes hard real-time strictes.

---

# Soft real-time

Les workloads soft real-time peuvent être orchestrés dans Kubernetes lorsque leurs contraintes temporelles restent compatibles avec une architecture distribuée.

Exemples :

* perception ;
* IA ;
* SLAM ;
* navigation ;
* fusion de données ;
* passerelles réseau ;
* services distribués.

Ces workloads bénéficient alors :

* de la reproductibilité ;
* du redéploiement ;
* du placement explicite ;
* de l’orchestration distribuée.

---

# Frontière d’orchestration

La plateforme ne cherche pas à supprimer la frontière entre hard real-time et orchestration distribuée.

Elle cherche au contraire à la rendre explicite.

Cette frontière permet :

* de préserver les contraintes critiques ;
* de maintenir des comportements prévisibles ;
* de limiter les dépendances ;
* de faciliter les modes dégradés ;
* de conserver une architecture distribuée observable et reproductible.

---

# Positionnement architectural

> Kubernetes ne porte pas les boucles hard real-time. Il orchestre les composants distribués, observables et redéployables autour du système robotique.

L’observabilité backend, l’exploitation longue durée et le stockage froid peuvent être externalisés hors du cluster robotique local sans remettre en cause le fonctionnement opérationnel du système.
