Worker node
============

.. contents:: Sections
   :local:
   :depth: 1

Hardware
---------

.. TODO: spécifications matérielles selon profil (Motion / Perception / Edge)

Base system
------------

OS
~~~

.. TODO: installation OS, paramètres de base selon profil nœud

systemd
~~~~~~~~

.. TODO: configuration systemd, units critiques

SSH
~~~~

.. TODO: configuration sshd, accès depuis le controller

chrony
~~~~~~~

.. TODO: synchronisation NTP depuis le controller ou source commune

Container runtime
~~~~~~~~~~~~~~~~~~

.. TODO: installation containerd, configuration registry mirror

Network stack
--------------

Interfaces physiques
~~~~~~~~~~~~~~~~~~~~~

.. TODO: identification des interfaces selon profil matériel

Bridge
~~~~~~~

.. TODO: configuration bridge si nécessaire

VLAN
~~~~~

.. TODO: configuration VLANs selon domaines réseau

Routage
~~~~~~~~

.. TODO: routage vers le controller et les autres nœuds

DNS / NTP
~~~~~~~~~~

.. TODO: résolution DNS via controller, NTP

WireGuard
~~~~~~~~~~

.. TODO: configuration WireGuard — peer controller, clés

Kubernetes enrollment
----------------------

Token
~~~~~~

.. TODO: récupération du token de jonction depuis le controller

Join
~~~~~

.. TODO: commande k0s worker join, configuration

Runtime
~~~~~~~~

.. TODO: vérification container runtime après enrollment

Registry mirror
~~~~~~~~~~~~~~~~

.. TODO: configuration du mirror vers la registry locale du controller

Validation worker
------------------

Le worker est considéré opérationnel lorsque :

- node visible dans Kubernetes (``kubectl get nodes``)
- pull registry fonctionnel
- réseau inter-nœuds opérationnel
- WireGuard actif

.. TODO: commandes de vérification pour chaque point
