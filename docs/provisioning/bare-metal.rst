Provisioning bare-metal
========================

Cette section décrit le provisioning des nœuds physiques permettant d'obtenir un cluster Kubernetes opérationnel.

----

Architecture cible
-------------------

.. image:: ../_static/diagrams/provisioning.svg
   :alt: Architecture cible provisioning bare-metal
   :align: center
   :target: ../_static/diagrams/provisioning.svg

----

Périmètre du provisioning
--------------------------

Le provisioning repose sur Ansible et une configuration déclarative des nœuds Linux.

- le provisioning système (OS, systemd, SSH, chrony) ;
- le réseau Linux (interfaces, bridge, VLAN, routage, DNS) ;
- le runtime conteneur (containerd) ;
- le bootstrap et l'enrôlement Kubernetes (k0s).

Chaque machine est préparée afin de fournir un nœud Kubernetes opérationnel et persistant après redémarrage.

----

Résultat attendu
-----------------

- le controller expose une API Kubernetes fonctionnelle ;
- les workers rejoignent correctement le cluster ;
- les communications réseau inter-nœuds sont opérationnelles ;
- l'infrastructure survit aux redémarrages système.

----

.. toctree::
   :hidden:

   prerequisites
   ansible
   system
   network
   controller
   worker
   validation
