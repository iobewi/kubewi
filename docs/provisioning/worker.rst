Worker node
============

.. contents:: Sections
   :local:
   :depth: 1

Hardware
--------

.. TODO: spécifications matérielles selon profil (Motion / Perception / Edge)

Kubernetes enrollment
---------------------

Token
~~~~~

.. TODO: récupération du token de jonction depuis le controller

Join
~~~~

.. TODO: commande k0s worker join, configuration

Validation worker
-----------------

Le worker est considéré opérationnel lorsque :

- le nœud est visible dans le cluster (``kubectl get nodes``) ;
- le réseau inter-nœuds est opérationnel ;
- les services sont persistants après reboot.

.. TODO: commandes de vérification pour chaque point
